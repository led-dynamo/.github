# Repository hardening baseline

<!-- ore-org-baseline:begin -->
The public `.github` repository supplies only GitHub-supported fallback files. It does not inject arbitrary agent instructions or workflow files into sibling repositories.

Each active repository should therefore maintain:

- a local lowercase `agents.md` derived from this policy plus repository-specific constraints;
- provider mirrors or pointers as required by the tools used in that repository;
- explicit least-privilege workflow permissions and job timeouts;
- full commit-SHA pins for external Actions;
- checkout with `persist-credentials: false` unless a reviewed write step proves it is necessary;
- tests appropriate to the repository's language and risk;
- branch/ruleset controls that prevent force pushes and branch deletion;
- vulnerability alerts and automated security fixes where supported;
- a linked GitHub issue or pull request for material Linear architecture or policy changes.

The selectable workflow template is standalone and uses immutable external Action pins. A repository that calls `.github/workflows/reusable-policy.yml` directly must pin the call to a reviewed full commit SHA of `led-dynamo/.github`; do not use a mutable branch or tag for enforcement.

Account administrators should separately review organization-wide Actions policy, default `GITHUB_TOKEN` permissions, approval of forked workflows, repository creation permissions, rulesets, GitHub App scopes, secret scanning and push protection, private vulnerability reporting, audit-log access, and emergency break-glass procedures. Those settings cannot be enforced merely by committing files to this repository.
<!-- ore-org-baseline:end -->
