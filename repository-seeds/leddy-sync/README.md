# leddy-sync

Executable repository seed for the canonical public repository `led-dynamo/leddy-sync`.

The crate owns deterministic version comparison and reconciliation decisions for state shared by Leddy UIs, API servers, WebSocket backends, and device-control surfaces. Transport remains in the clients and server repositories.

## Zed graph

- `led-dynamo/leddy-interfaces`
- `led-dynamo/leddy-lib`

Dependencies materialize under `.vendor/.zed`.

## Publish

From this seed directory, using an authenticated GitHub CLI session:

```bash
./publish.sh
```

The publisher refuses to overwrite an existing repository and does not embed a token.

## Validate

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets --all-features
```

## Composition

A composing workspace may retain this repository as a clean committed gitlink. Adopt it with `zed overtake --git-submodules`; Git owns the exact checkout while Zed owns package identity, dependency intent, materialization, and lock provenance.

Tracking: `led-dynamo/.github#17`, GitHub Project #1, and the `github.com/led-dynamo` Linear project.
