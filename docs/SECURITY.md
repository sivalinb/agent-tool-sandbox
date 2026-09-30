# Security and limitations

This is a single-user research sandbox, not a hardened public multi-tenant code-execution service. It does not provide a formally verified boundary, an aggregate guest-disk quota, an egress proxy, malware analysis, or a guarantee against hypervisor vulnerabilities. Code can write only to guest locations permitted by the read-only root and temporary-memory mounts. Per-file size and execution limits reduce resource abuse but are not a total disk accounting system. Do not expose the Streamlit app publicly without authentication and a separate execution service. VM startup is included in the deadline, so pre-pull images first.

## Shared boundaries

The app is intended for a trusted local user. It has no multi-user authentication or tenant isolation at the Streamlit layer. Public deployment requires a separate access-control and execution-service design. The Pkl evaluator only loads the repository's trusted module. Public sources are allowlisted and not executed. Input sizes, resource settings, subprocess output, and execution durations are bounded where implemented. The detailed report distinguishes active enforcement from documentation and experimental assumptions.

Source and model content may include misleading instructions; retrieval and model outputs have no authority to change application policy. Citation membership alone does not prove correctness. Never publish private production logs or credentials as example data. Report suspected security defects privately through the repository owner's GitHub contact channels; do not include working credentials in an issue.
