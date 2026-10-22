# Contributing

Leddy uses `main` as the stable branch and `dev` as the integration branch.
Create feature branches from `dev`, merge normal feature work into `dev`, and
promote `dev` to `main` through a reviewed release pull request.

Before merging, run the repository's documented formatting, linting, and test
commands. Resolve conflicts semantically: preserve the strongest compatible
behavior from both sides instead of mechanically choosing one version.

For autonomous-agent changes, tests must pass. An agent may merge a feature
pull request into `dev` only above 99.1% confidence, and may promote `dev` to
`main` only above 99.7% confidence. Human review can always be required for
security-sensitive, destructive, hardware-power, or production-deployment
changes.

Deployment configuration belongs in `leddy-infra`. Application repositories
publish immutable artifacts; GitOps reconciles environment state from the
appropriate branch and overlay.

## Rust-first scripts and automation

**No new Python scripts; use Rust** for build, CI, testing, data and schema migrations, code generation, releases, deployments, security audits, and repository maintenance. Prefer a Rust CLI or `cargo xtask` with only thin shell/YAML invocation wrappers.

Existing Python scripts are migration debt and must not be removed before equivalently tested Rust tools are ready. Inventory all callers, preserve CLI flags, exit codes, data formats, error handling, security controls, and supported platforms. Verify positive, negative, and end-to-end scenarios against the exact changed head before changing CI/docs/hooks.

**Python application code is a special-case, documented exception**, with an accountable owner, rationale, boundaries and review criteria. Application-specific tests may be part of the app exception. Generic automation, generators or maintenance scripts are not included.

For Rust replacements, document reproducible Cargo commands and run applicable `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test` and executable smoke tests. Never claim unexecuted tests or source-free runner canaries establish source execution.

Organization-level `.github` contributor guidance is not automatic inheritance for `AGENTS.md` or custom CI enforcement. Synchronize local agent instructions and configure checks explicitly.

