# Evaluation methodology

The real enforcement suite checks useful analysis (three CSV rows), timeout of a busy loop, denied input mutation, failed external network connection, bounded excessive stdout, and two successive clean-state runs. Check the failure class as well as a nonzero exit code: an image-pull or runtime-startup failure is not evidence of successful isolation. The reports include stdout/stderr because they are the requested job output; audit logs contain hashes and metadata only.

## Portable automated checks

Run `pytest -q` and `python scripts/evaluate.py`. Pytest covers independent expected outcomes and boundary conditions, while Streamlit AppTest drives a visible workflow and checks for uncaught exceptions. Pkl tests exercise valid configuration and the Python suite rejects invalid configuration/inputs. The retrieval evaluation uses hand-authored held-out questions, expected evidence IDs, top-three hit rate, and an unrelated question requiring abstention.

## Live verification

Run `python scripts/run.py --live` where supported on an Apple silicon Mac. Live work is intentionally excluded from ordinary Linux CI. A manual macOS workflow is supplied for an explicitly provisioned self-hosted runner. Review the checkout before running it; no pull-request trigger dispatches arbitrary code onto a personal Mac.

## Reporting

Keep the actual pass/fail result, sample count, environment, and raw evidence. A failed negative-control workload may be the expected test outcome; a failed runtime setup is not. Synthetic fixtures test logic, not real-world performance. Simulation invariants do not establish production guarantees. Local model quality scores are bounded by the prompt sample and scoring rule. Retrieval hit rate does not measure generated-answer factuality.
