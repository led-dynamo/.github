# Organization-wide agent instructions

<!-- BEGIN ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->
## Required `dev`/GitFlow/GitOps policy

Read and follow [`BRANCHING_AND_DEPLOYMENT.md`](BRANCHING_AND_DEPLOYMENT.md) before reviewing, merging, releasing, or deploying changes.

- `dev` is the integration branch; strive for GitFlow.
- With all tests and required checks passing, merge feature/fix PRs into `dev` only when AI confidence is strictly greater than 99.1%.
- Merge `dev` into `main`/`master` only when release/deployment checks pass and AI confidence is strictly greater than 99.7%.
- Use the organization's canonical `*-infra` repository, GitHub Actions, immutable artifacts, and GitOps reconciliation for branch-based deployment promotion.
- Required reviews, branch protection, security gates, and environment approvals always take precedence.
<!-- END ORESOFTWARE MANAGED BRANCHING AND GITOPS POLICY -->

<!-- ore-org-baseline:begin -->
These instructions apply to this repository. Repository-local instructions may add stricter requirements, but they must not weaken this baseline.

## Canonical organization links

- GitHub organization: https://github.com/led-dynamo
- Public organization defaults: https://github.com/led-dynamo/.github
- Canonical Linear project: https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494
- Fleet tracking issue: https://github.com/ORESoftware/k8s-cluster/issues/1222

## Instruction discovery

Lowercase `agents.md` is canonical. Read every applicable lowercase `agents.md` from the repository root toward the current working directory before editing. Uppercase `AGENTS.md` and provider-specific instruction files are compatibility mirrors and must remain aligned with the applicable lowercase policy.

## Inspect before editing

Inspect the current branch, complete working tree, remotes, default branch, open pull requests, linked GitHub issues, linked Linear work, repository documentation, tests, schemas, generated artifacts, deployment definitions, and relevant related repositories. Preserve every unfamiliar or uncommitted change.

Use read-only inspection and non-pruning synchronization such as `git status --short --branch`, `git remote -v`, `git fetch --all`, `git diff`, `git log`, `git show`, and `git blame`. Before integrating remote work, avoid git rebase in favor of git merge. Never treat a dirty worktree or inconvenient branch as permission to discard state.

## Mandatory semantic conflict resolution

> resolve any and all git conflicts semantically, will full context, even looking back 3-10 commits in git log history for more context - never hastily pick sides in a conflict but merge things conceptually, using max context and complete conceptual awareness for a given github organization's repos and external org repos too

For every conflict:

1. Read the merge base, both complete sides, surrounding implementation, tests, schemas, generated artifacts, documentation, deployment configuration, and public contracts—not only conflict markers.
2. Inspect the affected path history and normally review 3–10 relevant commits on each side with `git log`, `git show`, and `git blame` where useful.
3. Review linked pull requests, issues, Linear work, related repositories in `led-dynamo`, and relevant external-organization repositories whenever behavior or contracts cross boundaries.
4. Preserve compatible intent and invariants from both sides. Synthesize a conceptual merge; never resolve by selecting `ours`, `theirs`, `current`, or `incoming` wholesale.
5. Scan the complete tree for unresolved markers and run the applicable formatter, linter, unit, integration, contract, build, security, and end-to-end checks.
6. Document incompatible requirements, intentional choices, and any discarded intent in the commit and pull-request description.

## Hard denylist for automated agents

Automated agents must **never execute or recommend** destructive, state-concealing, history-rewriting, purge, revocation, or policy-bypass operations. This is a hard denylist: authorization may support a reviewed human-run procedure, but it does not authorize an automated agent to perform the destructive step.

The blacklist includes, without limitation:

- every form of `git stash`, every mode of `git reset`, every mode of `git clean`, `git filter-repo`, `git filter-branch`, BFG, `git rebase`, interactive history rewriting, `git commit --amend`, commit replacement, destructive `git checkout -- <path>`, destructive `git restore`, `git branch -D`, ref or tag deletion, `git reflog expire`, `git gc --prune`, `git push --force`, and `git push --force-with-lease`;
- recursive or bulk deletion and destructive filesystem mutation, including `rm -rf`, `find -delete`, truncation, shredding, destructive overwrite, formatting, and access-removing ownership or permission changes;
- destructive data operations, including `DROP`, `TRUNCATE`, unbounded `DELETE`, destructive rollback, irreversible migration, bucket/object purge, queue/topic deletion, and bulk mutation without a bounded reversible plan;
- destructive infrastructure or identity operations, including `kubectl delete`, `helm uninstall`, `terraform destroy`, `pulumi destroy`, cloud delete/purge calls, cluster or namespace teardown, and autonomous secret, key, certificate, credential, factor, or session revocation or rotation;
- deleting repositories, worktrees, submodules, branches, tags, releases, packages, artifacts, registries, environments, evidence, audit logs, customer data, or production state;
- bypassing hooks, reviews, branch protection, rulesets, required checks, security/compliance gates, approvals, or audit logging, including `--no-verify` and equivalent bypasses.

Do not use destructive commands merely to make tests pass, clear a conflict, simplify a migration, or hide an inconvenient state.

### Required safe alternatives

To preserve shared history, avoid git rebase in favor of git merge. Use additive branches, separate clean worktrees or clones, explicit path staging, ordinary commits, non-force pushes, patch-based edits, read-only queries, dry runs, backups, additive migrations, and reversible roll-forward changes. Leave unrelated work untouched. When safe progress is impossible, preserve all state and report the exact blocker.

## Source ownership and cross-repository context

Edit authoritative sources rather than generated mirrors, vendored copies, caches, or downstream consumers. Identify generators and regenerate derived artifacts from reviewed sources. Never detach, absorb, relocate, remove, or rewrite a submodule or worktree. Cross-repository behavior must be understood across the owning organization and relevant external organizations before contracts are changed.

## Secrets and sensitive data

Never print, log, commit, paste into issues, include in fixtures, or expose tokens, passwords, private keys, session material, database URLs, customer data, legal records, private health data, production data, or unpublished security details. Use approved secret stores, placeholders, and redacted diagnostics.

## Pull requests, validation, and evidence

Use focused branches and pull requests. Link the relevant Linear issue or project. Explain behavior, risks, migration and roll-forward considerations, security impact, tests run, conflicts and their semantic resolution, and cross-repository dependencies. Never report a branch, commit, pull request, merge, deployment, test run, or external update as complete without authoritative remote evidence.
<!-- ore-org-baseline:end -->

<!-- ore-primary-branch-policy:begin -->
## Primary branch and concurrent-agent policy

This organization policy overrides generic feature-branch and worktree defaults for agent tooling.

- Highly prefer an existing primary branch, in this order: `main`, `dev`, then `master`.
- Work directly on the selected primary branch even when other agents are active. Use another branch only when a human or a repository-specific release process explicitly requires it.
- Never create or use a Git worktree unless a human explicitly instructs you to do so for the current task. Concurrency alone is not permission to use a worktree.
- Concurrent agents must coordinate repository and file ownership through the available agent communication channel, keep edits scoped, inspect live state before each write, and hand off cleanly. Coordinate instead of isolating routine work in worktrees.
- Preserve unrelated in-progress changes and never overwrite another agent's work. If safe ownership of overlapping files cannot be established, pause that overlapping edit and coordinate before continuing.
<!-- ore-primary-branch-policy:end -->

## Repository-local Git worktrees

- Create or use a Git worktree only when the human operator explicitly authorizes it for the current task. Concurrency or a dirty checkout is not permission by itself.
- Put every authorized worktree at `<repository-root>/tmp/worktrees/<name>`; from the repository root, use `./tmp/worktrees/<name>`. Never place worktrees beside repositories or organization directories.
- Keep `tmp`, `temp`, `tmp/worktrees`, and `temp/worktrees` ignored in the repository-root `.gitignore`. Do not commit files from those directories.
- Relocate or remove a worktree only when the operator explicitly requests it. Before removal, preserve and publish intended changes, verify its commit is represented on the target branch, and confirm there are no tracked, untracked, ignored-sensitive, or in-use files that must survive. Remove it with `git worktree remove <path>` without `--force`; never delete a worktree directory with `rm`.
