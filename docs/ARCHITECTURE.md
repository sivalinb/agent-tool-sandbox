# Architecture

## Data flow

Pkl policy → Python policy validation → static AST preview → per-job temporary input/job directories → read-only VM mounts → nonroot Python process → bounded stdout/stderr capture → cleanup → hash-based audit record.

## Implementation decisions

Submitted code is never evaluated by the Streamlit host. Static parsing only checks syntax and lists imports. Actual execution requires Apple Container; there is no fallback to host subprocess execution. Each job gets its own VM, no network, an unprivileged UID/GID, dropped Linux capabilities, and read-only input/code mounts, a read-only root filesystem, and a 16 MiB temporary scratch mount. The host reads process output incrementally, caps retained bytes, kills the client process group on timeout or output overflow, and deletes the named VM. The bootstrap adds per-file and open-file limits inside the guest. Unique mount directories and VM names prevent reuse of a prior job's writable state.

## Modules

`app.py` renders Streamlit controls and stores the current report in session state. `engine.py` contains domain logic and typed runtime models. `config/` stores Pkl source and its verified export. `labcore/runtime.py` issues argument-array subprocess calls, captures bounded output, and scopes cleanup to generated job names. `labcore/observability.py` writes event metadata and experiment reports. `labcore/ai.py` retrieves reference evidence and optionally synthesizes a cited answer. `data/sources.json` declares the public inputs and their terms. `workloads/` contains trusted workload entrypoints, where needed. `tests/` covers failure cases and Streamlit workflows.

## Trust boundaries

UI uploads and downloaded source content are data. They do not become system commands or Pkl modules. The sandbox project explicitly permits user Python inside a VM. Other tools execute only checked-in workload entrypoints. Subprocess calls use argument lists without a shell. Source URLs come from a fixed HTTPS catalogue with redirects disabled. Model responses are advisory and cannot trigger container actions.

## Persistence and reproducibility

Run artifacts are local and ignored by Git. Reports retain the mode, input/contract settings, source/config hashes where applicable, raw observations, and calculated decisions. Reproduce a finding by saving the report, pinning runtime/image/model versions, rerunning with the same workload, and comparing independent trials. Generated configuration and dependency versions are committed. For formal benchmarks replace mutable image tags with verified OCI digests.
