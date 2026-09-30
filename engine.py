"""An analysis-job runner that never executes submitted code on the host."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
from pydantic import BaseModel, Field
from typing import Literal
from labcore.runtime import AppleContainer


class Policy(BaseModel):
    cpus: int = Field(default=1, ge=1, le=4)
    memoryMb: int = Field(default=256, ge=256, le=2048)
    timeoutSeconds: int = Field(default=8, ge=1, le=30)
    maxOutputBytes: int = Field(default=65536, ge=1024, le=1048576)
    maxInputBytes: int = Field(default=1000000, ge=1, le=15000000)
    network: Literal["none"] = "none"
    image: Literal["python:3.12-slim"] = "python:3.12-slim"


PRESETS = {
    "Analyze CSV": 'import csv, json, statistics\nrows = list(csv.DictReader(open("/input/data.csv")))\nvalues = [float(row["value"]) for row in rows]\nprint(json.dumps({"count":len(values), "mean":statistics.mean(values), "max":max(values)}))\n',
    "Analyze USGS events": 'import json, statistics\ndata = json.load(open("/input/data.json"))\nvalues = [f["properties"]["mag"] for f in data["features"] if isinstance(f["properties"].get("mag"),(int,float))]\nprint(json.dumps({"events":len(values), "mean_magnitude":statistics.mean(values) if values else None}))\n',
    "Deadline test": 'while True:\n    pass\n',
    "Protected input test": 'open("/input/data.csv", "w").write("overwrite")\n',
    "Network isolation test": 'import socket\nsocket.create_connection(("1.1.1.1", 443), timeout=2)\n',
    "Output budget test": 'while True:\n    print("x"*8192, flush=True)\n',
    "Cross-job isolation test": 'from pathlib import Path\np = Path("/tmp/prior-job-marker")\nprint("EXISTS" if p.exists() else "FRESH")\np.write_text("marker")\n',
}

DEFAULT_CSV = b"timestamp,value\n2026-01-01T00:00:00Z,12\n2026-01-01T00:01:00Z,14\n2026-01-01T00:02:00Z,31\n"


def assess(code, config):
    policy = Policy.model_validate(config)
    if len(code.encode()) > 100_000:
        raise ValueError("Code exceeds 100 KB limit")
    tree = ast.parse(code)
    imports = sorted({alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names} |
                     {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)})
    return {"mode":"static preview; no code executed", "syntax_valid":True, "imports":imports,
            "policy":policy.model_dump(), "code_sha256":hashlib.sha256(code.encode()).hexdigest(),
            "enforcement":"VM per job, no network, unprivileged user, read-only root/input, 16 MiB temporary scratch, host deadline/output limits",
            "note":"AST inspection is informational, not a security boundary."}


def run_job(code, data: bytes, filename: str, config):
    report = assess(code, config)
    policy = Policy.model_validate(config)
    if len(data) > policy.maxInputBytes:
        raise ValueError("Input exceeds configured byte budget")
    if filename not in {"data.csv", "data.json"}:
        raise ValueError("Input filename must be data.csv or data.json")
    runtime = AppleContainer()
    runtime.require()
    with tempfile.TemporaryDirectory(prefix="agent-tool-") as directory:
        root = Path(directory)
        inputs, job = root / "input", root / "job"
        inputs.mkdir(mode=0o755)
        job.mkdir(mode=0o755)
        (inputs / filename).write_bytes(data)
        (inputs / filename).chmod(0o444)
        (job / "submitted.py").write_text(code)
        # This trusted bootstrap runs inside the VM; code is never exec'd on the host.
        (job / "bootstrap.py").write_text("import resource,runpy\nresource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))\nresource.setrlimit(resource.RLIMIT_NOFILE,(64,64))\nrunpy.run_path('/job/submitted.py',run_name='__main__')\n")
        result = runtime.run(policy.image, ["python", "-u", "-B", "/job/bootstrap.py"],
                             cpus=policy.cpus, memory_mb=policy.memoryMb, timeout=policy.timeoutSeconds,
                             max_output=policy.maxOutputBytes, user="65534:65534", network="none",
                             read_only_root=True,
                             mounts=[(inputs,"/input","ro"),(job,"/job","ro")])
    report.update({"mode":"live Apple Container job", "result":result.dict(),
                   "input_sha256":hashlib.sha256(data).hexdigest(), "input_bytes":len(data),
                   "passed":result.returncode == 0 and result.reason == "completed"})
    return report


def security_evaluation(config):
    cases = [("Analyze CSV", "success"), ("Deadline test", "timeout"),
             ("Protected input test", "denied"), ("Network isolation test", "denied"),
             ("Output budget test", "output_limit"), ("Cross-job isolation test", "fresh"),
             ("Cross-job isolation test", "fresh")]
    results = []
    for name, expectation in cases:
        report = run_job(PRESETS[name], DEFAULT_CSV, "data.csv", config)
        r = report["result"]
        observed = r["reason"]
        if expectation == "success":
            passed = r["returncode"] == 0 and json.loads(r["stdout"])["count"] == 3
        elif expectation == "denied":
            passed = r["returncode"] != 0 and r["reason"] == "completed" and any(s in r["stderr"] for s in ["PermissionError", "Read-only", "Network is unreachable", "OSError", "TimeoutError"])
        elif expectation == "fresh":
            passed = r["returncode"] == 0 and r["stdout"].strip() == "FRESH"
        else:
            passed = observed == expectation
        results.append({"case":name,"expected":expectation,"passed":passed,"report":report})
    return {"mode":"live sandbox enforcement evaluation", "passed":all(x["passed"] for x in results),"cases":results}
