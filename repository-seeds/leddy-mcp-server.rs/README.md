# leddy-mcp-server.rs

Executable repository seed for `led-dynamo/leddy-mcp-server.rs`.

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

```bash
./publish.sh
```

The publisher requires an authenticated GitHub CLI session, refuses to overwrite an existing repository, and embeds no credential.

## Validate

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets --all-features
```

Tracking: `led-dynamo/.github#18`, GitHub Project #1, and the `github.com/led-dynamo` Linear project.
