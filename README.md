# Agent Tool Sandbox

[![Verify](https://github.com/sivalinb/agent-tool-sandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/sivalinb/agent-tool-sandbox/actions/workflows/ci.yml)

An AI analysis tool needs a bounded place to execute Python, with explicit inputs and evidence of what happened. The application makes job policy, execution, and enforcement tests inspectable.

Python · Streamlit · Pkl · Apple Container · evaluation evidence · OpenTelemetry

## Start here

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py --server.port 8502
```

The interface opens at http://127.0.0.1:8502. Portable demos work without a model, API key, Pkl executable, or container runtime. The configuration fallback is a checked export whose source hash must match the committed Pkl source. Every report identifies its mode.

## Walkthrough

1. Choose Analyze CSV and Static preview. Inspect imports, input policy, and code hash. No submitted code runs during this step.
2. Prepare the Python container image. Choose Live Apple Container and Run job.
3. Exercise the deadline, protected-input, network, and output-budget templates. These are expected failure scenarios.
4. Run the Enforcement eval tab to execute all seven checks.
5. Fetch USGS events in Public sources, select Analyze USGS events, and enable use of the most recently fetched source.
6. Upload your own CSV or JSON only when you intend to expose it to the isolated job. Filenames inside the VM are always data.csv or data.json.

## Architecture

Pkl policy → Python policy validation → static AST preview → per-job temporary input/job directories → read-only VM mounts → nonroot Python process → bounded stdout/stderr capture → cleanup → hash-based audit record.

The Streamlit UI calls pure Python engines; each repository vendors a small `labcore` package so cloning this repository is sufficient. No sibling repository is required.

## CLI and checks

```bash
python scripts/run.py
python scripts/run.py --live
python scripts/run.py --live --security-eval
pytest -q
python scripts/evaluate.py
python scripts/export_config.py   # requires pkl on PATH or PKL_BIN
```

## Observed verification

24 automated tests passed locally. Seven live expected-outcome checks passed, including timeout, read-only input, no-network, output limits, and fresh per-job state. See [verified results and evidence](docs/VALIDATION.md) for settings, provenance, and limitations.

## Documentation

- [Setup and live runtime](docs/SETUP.md)
- [Architecture and decisions](docs/ARCHITECTURE.md)
- [Learning walkthrough](docs/WALKTHROUGH.md)
- [Evaluation methodology](docs/EVALUATION.md)
- [Public sources and licenses](docs/DATA_SOURCES.md)
- [Observability and AI](docs/OPERATIONS.md)
- [Security and limitations](docs/SECURITY.md)
- [Verified results](docs/VALIDATION.md)

MIT-licensed project code. External datasets and references retain their own terms. Public inputs are fetched explicitly and kept under ignored `artifacts/`; no private production telemetry is included.
