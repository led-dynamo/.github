# leddy-sync

Executable canonical public repository seed for `led-dynamo/leddy-sync`.

The crate owns deterministic version comparison and reconciliation decisions for state shared by Leddy UIs, API servers, WebSocket backends, and device-control surfaces. Transport remains in the clients and server repositories.

## Zed graph

- `led-dynamo/leddy-interfaces`
- `led-dynamo/leddy-lib`

Dependencies materialize under `.vendor/.zed`.

## Publish

Use either an authenticated GitHub CLI session or an environment-provided token:

```bash
# Preferred when gh is authenticated
./publish.sh

# Credential fallback; the token is read from the environment and never committed
GH_TOKEN=... ./publish.sh
```

`GITHUB_TOKEN` is accepted as a fallback variable. The publisher refuses to overwrite an existing repository, refuses dirty or non-`main` worktrees, rejects unrelated `origin` remotes, and never places a token in the remote URL.

## Validate

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets --all-features
```

## Composition

A composing workspace may retain this repository as a clean committed gitlink. Adopt it with `zed overtake --git-submodules`; Git owns the exact checkout while Zed owns package identity, dependency intent, materialization, and lock provenance.

The exact recovered Git history is retained under `.artifacts/repository-recovery-wave7/`; it records head `eae9e063c693d2f5e89844acf15c4e014100d976` without rewriting the current `.github` history.

Tracking: `led-dynamo/.github#17`, GitHub Project #1, and Linear `DEN-2884` / `DEN-3159`.
