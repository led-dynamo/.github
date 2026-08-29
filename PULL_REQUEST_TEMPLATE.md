## Purpose

Describe the problem, intended behavior, and why this repository owns the change.

## Review path

- [ ] All commits are on a non-default branch and this pull request is the only proposed path into the default branch.
- [ ] No generated tool, bot, migration runner, or deployment process writes directly to `main`, `master`, or another protected default branch.
- [ ] The change is small enough to review, or its staged rollout and follow-up pull requests are identified.

## Scope and boundaries

- [ ] The change is focused and does not silently cross repository ownership boundaries.
- [ ] No `*-infra` repository is introduced as a Git submodule under `*-monorepo/apps`.
- [ ] Public contracts, compatibility, rollback, telemetry, and failure behavior are documented.
- [ ] Shared functionality is imported from its owning repository rather than copied into a new local implementation.

## Contracts, SQL, and migrations

- [ ] If SQL changes, declarations use the registered logical namespace `<organization>.<domain>` and stable `<domain>_` object prefixes where a shared PostgreSQL schema such as `public` is required.
- [ ] Domain SQL may remain in the owning organization, but identity, ordering, checksums, drift detection, and promotion are registered through `declarative-migrations`.
- [ ] JSON Schema, generated language interfaces, ORM models, fixtures, and migration declarations were updated and checked deterministically together.
- [ ] Destructive changes include compatibility, backfill, rollback, tenant isolation, and row-level-security evidence.

## Infrastructure and end-to-end coverage

- [ ] Kubernetes application manifests compose through `oresoftware/k8s-cluster` and reuse `oresoftware/k8s-libs-and-shared-defs`; application repositories do not become a second cluster control plane.
- [ ] Workload identity, restricted Pod Security, default-deny networking, explicit egress, probes, resources, secret handling, and immutable image/dependency references were considered.
- [ ] Destructive and cross-runtime tests run in the corresponding `*-test` organization or an isolated e2e environment, with teardown evidence.
- [ ] Zed lifecycle hooks cover the relevant pre-build, pre-test, and pre-publish checks without bypassing local language-native validation.

## Validation

List formatters, linters, tests, builds, schema/codegen checks, migration validation, security checks, and manual verification performed. Include exact commands and explain any check that could not run.

## Safety

- [ ] No credentials, customer data, private-repository inventory, or sensitive telemetry is included.
- [ ] Conflicts were resolved semantically using both sides and relevant history.
- [ ] Destructive Git recovery, force pushes to protected branches, and history rewrites were not used.
- [ ] Logs and traces exclude secrets and user content by default and preserve tenant boundaries.
