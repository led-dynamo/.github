# Semantic conflict resolver

When resolving conflicts in `led-dynamo` repositories:

1. Identify the merge base and inspect both complete sides of every conflict.
2. Read surrounding implementation, tests, documentation, interfaces, and normally 3–10 relevant commits with `git log`, `git show`, and `git blame`.
3. Inspect related repositories when the conflict changes a shared contract or deployment boundary.
4. Synthesize compatible intent. Never resolve by blindly selecting all of `ours` or all of `theirs`.
5. Preserve the rule that `*-infra` repositories are separate from `*-monorepo` application source and cannot be Git submodules under `*-monorepo/apps`.
6. Remove every conflict marker, run affected validation, and document tradeoffs or intentional behavior changes.
7. Prefer a normal merge; do not rebase, force-push, reset, or discard work as a shortcut.
