# Verified results

Verified on 2026-09-30 UTC (2026-09-29 Mountain Time). This page reports observed development checks, not production reliability guarantees. The committed JSON evidence contains synthetic workloads, public-source metadata, and measured results. Secrets, local usernames, and source-cache contents are excluded.

## Portable checks

- `pytest -q`: **24 passed**, including the Streamlit primary workflow.
- `python scripts/evaluate.py`: all domain checks passed; retrieval hit@3 was 1.0 on five authored questions, and the unrelated-question abstention check passed.
- Pkl 0.32.1: valid configuration tests passed; invalid CPU allocation is rejected by the Python test suite.
- `ruff check .`: passed.

[portable-checks.json](evidence/portable-checks.json) preserves command results. The five retrieval questions are a small diagnostic suite, not a broad RAG quality benchmark. The default reviewer performs deterministic retrieval; no LLM is required for portable checks.

[Environment and OCI digests](evidence/environment.json) identify the tested dependencies and live image revisions. [GitHub Actions](https://github.com/sivalinb/agent-tool-sandbox/actions) independently reports the current portable CI status. Ordinary Linux CI does not run Apple Container workloads.

## Live enforcement results

Seven real Apple Container jobs passed the expected-outcome checks: normal CSV analysis, host deadline enforcement, rejected input writes, rejected network access, bounded output, and two consecutive jobs that both observed fresh scratch state. An intentionally rejected job has `report.passed: false` while its enclosing enforcement test has `passed: true`.

[enforcement.json](evidence/enforcement.json) retains the commands' results, reasons, durations, input/code hashes, and policy. Repeated output from the output-budget case is shortened in this public copy. The unabridged local artifact remains available to the operator.

A public USGS feed was also analyzed in a real isolated job: 229 events and mean magnitude 1.6473 for the downloaded snapshot. See [public-consumption.json](evidence/public-consumption.json). The feed changes over time; its hash and retrieval timestamp are recorded in [public-sources.json](evidence/public-sources.json).

## Reproduce and limits

Use `python scripts/run.py --live --security-eval` or the Enforcement eval tab after starting Apple Container and pre-pulling `python:3.12-slim`. This is a single-user research sandbox. The checks demonstrate specific restrictions, not resistance to every kernel, runtime, side-channel, or resource-exhaustion attack. No claim of secure public multi-tenant hosting is made. The displayed import list is informational; AST parsing is not the enforcement boundary.

## Public source verification

All ten catalogue entries downloaded successfully during verification, including USGS, NAB CPU/taxi, GSM8K, OpenMetrics, OTel semantic conventions, Pkl/Container releases, Apple runtime resource documentation, and node_exporter documentation. [public-sources.json](evidence/public-sources.json) records retrieval times, byte counts, hashes, URLs, and upstream terms. Documentation and release metadata are reference material, not empirical workload measurements. Downloaded source contents remain untracked and are not relicensed by this repository.
