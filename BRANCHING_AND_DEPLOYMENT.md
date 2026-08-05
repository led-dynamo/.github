# Branching, merge-confidence, and GitOps deployment policy

Policy version: `2026-08-05.1`.

<!-- BEGIN ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->
## Branch names and GitFlow

- **`dev` is the integration branch.** Feature, fix, refactor, and routine dependency branches should normally branch from `dev` and open pull requests back into `dev`.
- The repository's existing **`main` or `master` branch is the production/release branch**. Document which name the repository uses; do not rename it merely to satisfy this policy.
- Strive for GitFlow: short-lived `feature/*`, `fix/*`, `refactor/*`, and related branches flow into `dev`; releases flow from `dev` into `main`/`master`; urgent `hotfix/*` work may branch from production but must be merged back into `dev` immediately after production is repaired.
- Avoid direct feature-to-production pull requests. Preserve branch protections, required reviews, security gates, environment approvals, and semantic conflict resolution.

## AI-assisted merge thresholds

These are strict greater-than comparisons, not greater-than-or-equal comparisons.

1. **Feature/fix PR -> `dev`:** when all configured tests and required checks pass and the reviewing AI records evidence-based confidence **greater than 99.1%**, merge the pull request into `dev`.
2. **`dev` -> `main`/`master`:** when all integration, release, deployment, migration, security, and required checks pass and the reviewing AI records evidence-based confidence **greater than 99.7%**, merge `dev` into the repository's production branch.
3. Record the numerical score, supporting evidence, exact checks run, affected contracts, unresolved uncertainty, migration/deployment impact, and rollback or roll-forward plan in the pull request.
4. Confidence never overrides a failed or missing required check, unresolved review, branch protection, security/compliance gate, environment approval, or known contradictory evidence. Do not invent precision; justify the score from review depth, test coverage, affected contracts, and deployment evidence.

## `*-infra`, GitHub Actions, branch promotion, and GitOps

- Each organization designates a canonical infrastructure repository whose name ends in **`-infra`**. It owns deployable desired state: environment overlays, Kubernetes/Helm/Kustomize manifests, Terraform/Pulumi or other infrastructure code, GitOps-controller configuration, environment policy, and repository-to-environment mappings.
- Individual application, service, web, API, worker, CLI, library, interface, SDK, and client repositories own source code, tests, build definitions, artifact metadata, and repository-specific GitHub Actions workflows. They are not the source of truth for live cluster or cloud state.
- Pull requests and short-lived branches run CI and may create bounded ephemeral previews, but they must not directly mutate persistent shared environments.
- A merge into **`dev`** builds, tests, scans, attests, and publishes an immutable integration artifact identified by commit SHA and digest. GitHub Actions then opens or updates a reviewed desired-state change in the canonical `*-infra` repository for integration/development/staging. The GitOps controller reconciles it.
- A merge from **`dev` into `main`/`master`** promotes the already-tested immutable artifact whenever possible rather than rebuilding different bytes. GitHub Actions opens or updates the production desired-state change in `*-infra`; required approvals complete there; the GitOps controller performs reconciliation.
- Infrastructure-repository changes follow the same GitFlow intent: `dev` represents integration desired state and `main`/`master` represents production desired state, unless the infra repository explicitly documents an equally reviewable environment-directory model on one protected branch.
- GitHub Actions is the validation, build, test, scan, attestation, and promotion-orchestration layer. The GitOps controller is the normal deployment authority. Application workflows must not perform routine imperative production mutation such as direct `kubectl apply`, ad hoc cloud-console changes, or unreviewed Terraform applies.
- Use least-privilege OIDC or other short-lived credentials, protected GitHub environments, immutable action pins, explicit timeouts, concurrency controls, artifact provenance, and deployment-status reporting. Never expose repository or cloud credentials to untrusted pull-request contexts.
- Rollback normally means a reviewed revert or forward fix to desired state in `*-infra`, followed by GitOps reconciliation. Break-glass paths must be exceptional, auditable, time-bounded, and reconciled back into Git immediately.

Repository-local policy may strengthen these requirements but must not weaken the `dev` integration-branch declaration, strict confidence thresholds, required checks, GitFlow intent, or GitOps separation of responsibilities.
<!-- END ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->
