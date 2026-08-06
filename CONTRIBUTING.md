# Contributing

Leddy uses `main` as the stable branch and `dev` as the integration branch.
Create feature branches from `dev`, merge normal feature work into `dev`, and
promote `dev` to `main` through a reviewed release pull request.

Before merging, run the repository's documented formatting, linting, and test
commands. Resolve conflicts semantically: preserve the strongest compatible
behavior from both sides instead of mechanically choosing one version.

For autonomous-agent changes, tests must pass. An agent may merge a feature
pull request into `dev` only above 99.1% confidence, and may promote `dev` to
`main` only above 99.7% confidence. Human review can always be required for
security-sensitive, destructive, hardware-power, or production-deployment
changes.

Deployment configuration belongs in `leddy-infra`. Application repositories
publish immutable artifacts; GitOps reconciles environment state from the
appropriate branch and overlay.

<!-- ore-org-baseline:begin -->
Thank you for contributing to repositories owned by [`led-dynamo`](https://github.com/led-dynamo). Repository-local instructions take precedence when they are stricter.

## Before proposing a change

1. Read the repository README, contribution notes, lowercase `agents.md`, architecture documentation, linked issues, and relevant [Linear project](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494).
2. Confirm the authoritative source repository and whether files are generated, vendored, mirrored, or owned by another repository.
3. Fetch current remote state and preserve concurrent work. Avoid git rebase in favor of git merge.
4. Do not use `git stash`, `git reset`, `git clean`, `git filter-repo`, force-push, destructive worktree/submodule operations, or broad deletion/rewrite commands without exact authorization.
5. Never include secrets, credentials, customer data, legal records, or other private information in issues, commits, test fixtures, screenshots, or logs.

## Pull requests

Use a focused feature branch and a draft pull request. Link the relevant issue or Linear work; explain behavior, risk, security impact, migration and rollback considerations, tests, and cross-repository dependencies. Resolve conflicts semantically with full context—normally including the merge base and 3–10 relevant commits—rather than selecting one side wholesale. Run all affected checks and scan the complete worktree for conflict markers.

External GitHub Actions must be pinned to full commit SHAs. Workflows must use explicit least-privilege permissions, explicit timeouts, and non-persisted checkout credentials.
<!-- ore-org-baseline:end -->
