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
