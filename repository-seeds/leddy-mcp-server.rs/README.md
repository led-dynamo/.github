# leddy-mcp-server.rs

Executable canonical public repository seed for `led-dynamo/leddy-mcp-server.rs`.

The initial server implements newline-delimited JSON-RPC over stdio, negotiates MCP protocol revision `2025-06-18`, and exposes a read-only `zed_dependency_graph` tool. Write-capable device commands are intentionally excluded from the first release.

## Canonical Zed graph

- `led-dynamo/leddy-clients`
- `led-dynamo/leddy-interfaces`
- `led-dynamo/leddy-lib`
- `led-dynamo/leddy-cli`
- `led-dynamo/leddy-sync`
- `shared-auth/shared-auth-clients`

Publish `leddy-sync` first. Packages materialize under `.vendor/.zed`.

## Publish

Use either an authenticated GitHub CLI session or an environment-provided token:

```bash
# Preferred when gh is authenticated
./publish.sh

# Credential fallback; the token is read from the environment and never committed
GH_TOKEN=... ./publish.sh
```

`GITHUB_TOKEN` is accepted as a fallback variable. The publisher verifies that `leddy-sync` exists first, refuses to overwrite an existing repository, refuses dirty or non-`main` worktrees, rejects unrelated `origin` remotes, and never places a token in the remote URL.

## Validate

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets --all-features
```

The five read-only `api_docs_*` tools required by `DEN-3159` remain a follow-up gate; the current seed intentionally contains only `zed_dependency_graph`.

The exact recovered Git history is retained under `.artifacts/repository-recovery-wave7/`; it records head `6b8df986bcdd37a3aafdd1a97e1703c8db0379f6` without rewriting the current `.github` history.

Tracking: `led-dynamo/.github#18`, GitHub Project #1, and Linear `DEN-2885` / `DEN-3159`.
