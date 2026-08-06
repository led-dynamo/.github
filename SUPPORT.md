# Support

Use the relevant repository issue tracker for reproducible bugs and feature requests. Include expected behavior, actual behavior, environment, minimal reproduction, redacted logs, and the exact revision tested. Security reports belong in the private process described by `SECURITY.md`.

## Durable engineering policy

- This repository defines public organization-wide defaults for `led-dynamo`.
- Never commit credentials, private keys, access tokens, customer data, or private-repository inventories.
- Resolve Git conflicts semantically: inspect both sides, the merge base, nearby tests and contracts, and normally 3–10 relevant prior commits. Never blindly select all of `ours` or all of `theirs`.
- Prefer focused pull requests, explicit validation, non-destructive Git operations, and documented tradeoffs.
- Cross-repository integration uses versioned interfaces, APIs, SDKs, events, or explicitly owned replicated read models. Services do not reach into another service's database by default.
- `*-infra` repositories and `*-monorepo` application source remain separate. A `*-infra` repository must never appear as a Git submodule under `*-monorepo/apps`.
- Git submodules are reserved for explicitly coordinated editable source composition. Zed packages or immutable artifacts are preferred for package dependencies. Production deploys immutable artifacts or OCI digests, not source clones.

<!-- ore-org-baseline:begin -->
For reproducible product or development problems, use the affected repository's issue tracker and include environment, version or commit, expected behavior, actual behavior, and a minimal reproduction. Use discussions where a repository enables them for open-ended questions.

Do not post credentials, private logs, customer data, legal records, or vulnerability details. Security reports must follow [`SECURITY.md`](SECURITY.md).

Planning context for the GitHub owner is tracked in [github.com/led-dynamo](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494), although external contributors may not have access. Repository-local support documentation may define a narrower channel or support policy.
<!-- ore-org-baseline:end -->
