# Led Dynamo repository recovery — Wave 7

This directory preserves the complete Git histories recovered for two still-missing canonical repositories without rewriting the history of `led-dynamo/.github`.

| Target repository | Recovered main head | Carrier | Decoded SHA-256 |
|---|---|---|---|
| `led-dynamo/leddy-sync` | `eae9e063c693d2f5e89844acf15c4e014100d976` | `leddy-sync.bundle.b64` | `e793e52dbdf50bdbe137016ace133cdffb1239fc150b9af612c70a287a150478` |
| `led-dynamo/leddy-mcp-server.rs` | `6b8df986bcdd37a3aafdd1a97e1703c8db0379f6` | `leddy-mcp-server.rs.bundle.b64` | `a95d5338f2bd4b83b474ca8e870ca095e8e3866b357696b6b26e8520b03033d1` |

The adjacent source seeds remain directly reviewable. Their publishers now support authenticated `gh` or an environment-provided token, fail closed when the target already exists, reject dirty/non-`main` worktrees and unrelated remotes, and never embed a credential in a Git URL.

## Reconstruct and verify

```bash
mkdir -p /tmp/led-dynamo-wave7
base64 --decode leddy-sync.bundle.b64 > /tmp/led-dynamo-wave7/leddy-sync.bundle
base64 --decode leddy-mcp-server.rs.bundle.b64 > /tmp/led-dynamo-wave7/leddy-mcp-server.rs.bundle

printf '%s  %s\n' \
  e793e52dbdf50bdbe137016ace133cdffb1239fc150b9af612c70a287a150478 \
  /tmp/led-dynamo-wave7/leddy-sync.bundle \
  | sha256sum --check
printf '%s  %s\n' \
  a95d5338f2bd4b83b474ca8e870ca095e8e3866b357696b6b26e8520b03033d1 \
  /tmp/led-dynamo-wave7/leddy-mcp-server.rs.bundle \
  | sha256sum --check

git bundle verify /tmp/led-dynamo-wave7/leddy-sync.bundle
git bundle verify /tmp/led-dynamo-wave7/leddy-mcp-server.rs.bundle
```

## Publication order

1. Create `led-dynamo/leddy-sync` as an empty public repository and push the decoded bundle's `main` ref normally.
2. Verify that remote `main` is exactly `eae9e063c693d2f5e89844acf15c4e014100d976`.
3. Create `led-dynamo/leddy-mcp-server.rs` and push its decoded `main` ref normally.
4. Verify that remote `main` is exactly `6b8df986bcdd37a3aafdd1a97e1703c8db0379f6`.

No force push, rebase, history replacement, credential persistence, or claim of target-repository creation is made here. Repository creation remains gated by an organization-capable write path.

Tracking: `DEN-2884`, `DEN-2885`, `DEN-3159`, and repository-administration blocker `DEN-319`.
