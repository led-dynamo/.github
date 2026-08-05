# Organization-wide agent instructions

<!-- BEGIN ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->
## Required `dev`/GitFlow/GitOps policy

Read and follow [`BRANCHING_AND_DEPLOYMENT.md`](BRANCHING_AND_DEPLOYMENT.md) before reviewing, merging, releasing, or deploying changes.

- `dev` is the integration branch; strive for GitFlow.
- With all tests and required checks passing, merge feature/fix PRs into `dev` only when AI confidence is strictly greater than 99.1%.
- Merge `dev` into `main`/`master` only when release/deployment checks pass and AI confidence is strictly greater than 99.7%.
- Use the organization's canonical `*-infra` repository, GitHub Actions, immutable artifacts, and GitOps reconciliation for branch-based deployment promotion.
- Required reviews, branch protection, security gates, and environment approvals always take precedence.
<!-- END ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->
