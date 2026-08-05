# Repository boundaries

## Durable engineering policy

- This repository defines public organization-wide defaults for `led-dynamo`.
- Never commit credentials, private keys, access tokens, customer data, or private-repository inventories.
- Resolve Git conflicts semantically: inspect both sides, the merge base, nearby tests and contracts, and normally 3–10 relevant prior commits. Never blindly select all of `ours` or all of `theirs`.
- Prefer focused pull requests, explicit validation, non-destructive Git operations, and documented tradeoffs.
- Cross-repository integration uses versioned interfaces, APIs, SDKs, events, or explicitly owned replicated read models. Services do not reach into another service's database by default.
- `*-infra` repositories and `*-monorepo` application source remain separate. A `*-infra` repository must never appear as a Git submodule under `*-monorepo/apps`.
- Git submodules are reserved for explicitly coordinated editable source composition. Zed packages or immutable artifacts are preferred for package dependencies. Production deploys immutable artifacts or OCI digests, not source clones.

## Mandatory infrastructure/application separation

Infrastructure repositories own deployment definitions, cloud resources, cluster policy, secrets integration, and environment automation. Application monorepos own application source and application-local packages.

A repository named `*-infra` must **not** be added as a Git submodule anywhere under a `*-monorepo/apps` directory. Connect the two through immutable deployment artifacts, declared interfaces, environment configuration, and release metadata instead.

## Composition

- Interfaces and schemas are versioned before dependent implementations consume them.
- Client SDKs are generated from or tested against canonical interfaces.
- End-to-end repositories test deployed boundaries without becoming a source-ownership shortcut.
- Monorepos coordinate application source; they do not absorb independently owned infrastructure history.
