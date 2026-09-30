# Learning walkthrough

## Guided experiment

1. Choose Analyze CSV and Static preview. Inspect imports, input policy, and code hash. No submitted code runs during this step.
2. Prepare the Python container image. Choose Live Apple Container and Run job.
3. Exercise the deadline, protected-input, network, and output-budget templates. These are expected failure scenarios.
4. Run the Enforcement eval tab to execute all seven checks.
5. Fetch USGS events in Public sources, select Analyze USGS events, and enable use of the most recently fetched source.
6. Upload your own CSV or JSON only when you intend to expose it to the isolated job. Filenames inside the VM are always data.csv or data.json.

## Questions to answer in your portfolio write-up

1. What concrete failure does this experiment expose?
2. Which checks happen before execution, and which need runtime observations?
3. Which input, configuration, image, and model versions were used?
4. What did the positive and negative controls demonstrate?
5. Where could the measurements be misleading?
6. Which follow-up experiment would challenge your conclusion?

## Suggested demonstration

Record a three-minute walkthrough: explain the failure in one sentence, run a baseline, introduce one deliberate change, inspect the evidence, and explain the tradeoff. Include the downloadable report and the command needed to reproduce it. Prefer measured operational behavior over an unsupported claim of production readiness.

## Next extensions

Add one extension only after retaining a passing baseline: more realistic public workloads, an additional failure mode, stricter provenance, a larger evaluation set, or a runtime-version comparison. Preserve fixture/live distinctions and document negative results. The other four repositories in this portfolio can reuse the report schema without creating a runtime dependency on each other.
