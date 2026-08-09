# leddy-mcp-server.rs

Canonical read-only Rust MCP server for the Leddy API-documentation contract.

This repository is published from the reviewed seed in `led-dynamo/.github`. It uses the official Rust MCP SDK pinned exactly to `rmcp =3.1.0`; the SDK owns JSON-RPC framing, lifecycle negotiation, typed schemas, cancellation, errors, and stdio transport.

## API documentation contract

The server embeds the exact public `ore.api-docs.v1` snapshot prepared by `led-dynamo/leddy-api-server.rs` PR #4:

- immutable API source head: `aea63f652a20c087260bab3c86b31baa80eaa7ea`;
- public OpenAPI SHA-256: `cf0be66ce0ebb02c3fc077a88c3129c55b4d05f30070b3c7186d13731ae7fe88`;
- six documented HTTP/WebSocket operations;
- only `GET /health` is MCP-exposed;
- display publication, clear commands, device snapshots, telemetry-derived state, and the device WebSocket remain non-executable.

The build-pinned design performs no network requests, follows no redirects, accepts no credentials, opens no WebSockets, and invokes no HTTP operation.

## Closed read-only tool catalog

Exactly five tools are exposed:

- `api_docs_discover`
- `api_docs_get_openapi`
- `api_docs_validate`
- `api_docs_list_operations`
- `api_docs_describe_operation`

Every tool is annotated read-only, non-destructive, idempotent, and closed-world. There is deliberately no generic HTTP executor and no display/device mutation tool.

## Canonical Zed graph

Packages materialize under `.vendor/.zed` and preserve these dependency coordinates:

- `led-dynamo/leddy-clients`
- `led-dynamo/leddy-interfaces`
- `led-dynamo/leddy-lib`
- `led-dynamo/leddy-cli`
- `led-dynamo/leddy-sync`
- `shared-auth/shared-auth-clients`

Git may retain canonical repositories as exact committed source transport. Adopt existing gitlinks with `zed overtake --git-submodules`; Zed owns package identity, dependency intent, materialization, and immutable lock provenance. Do not create a second workspace path or long-name alias.

## Publication order

1. Publish and validate `led-dynamo/leddy-sync`.
2. Run this seed's `publish.sh` from an authenticated, network-enabled GitHub CLI environment.
3. Validate the initial repository CI and exact Zed resolution.
4. Run the immutable API+MCP parity gate in `led-dynamo-test`.
5. Promote API PR #4 only while both tested heads remain unchanged.

The publisher refuses to overwrite an existing repository, generates and validates a deterministic `Cargo.lock`, runs formatting, Clippy, tests, documentation, and release build, then creates the public canonical repository.

## Local validation

```bash
cargo generate-lockfile
cargo fmt --all -- --check
cargo clippy --locked --all-targets --all-features -- -D warnings
cargo test --locked --all-targets --all-features
cargo doc --locked --no-deps
cargo build --locked --release
```

Tracking: `led-dynamo/.github#18`, Linear `DEN-2885`, API work `DEN-3159`, and GitHub Project #1.
