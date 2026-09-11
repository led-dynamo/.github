# Pull request salvage policy

A pull request is never merely closed.

Stale, outmoded, superseded, conflict-ridden and half-finished PRs are the
*highest*-value salvage targets in this organization, not the lowest. They are
where an idea was tried once, learned from, and then lost when the branch went
cold. The reason a PR goes stale is almost never that its idea was wrong — it is
that the surrounding code moved underneath it.

## The rule

**Before any PR is closed, marked stale, superseded or abandoned, at least one
concrete thing from it must be carried forward into work that lands.**

"One concrete thing" means a real artifact, not a sentiment: a test case, a
fixture, an error message, a config default, a lockfile pin, a doc paragraph, a
edge case in a match arm, a workflow permission narrowing. If the reviewer
genuinely cannot find one, that has to be said out loud in the closing comment,
with what was examined.

Closing a PR without a recorded salvage pass is a defect. It is treated the same
as deleting work.

## What a salvage pass looks like

1. Read the whole diff, not the summary. Compare the PR's merge base against the
   current default branch and list which files moved underneath it.
2. Decide, file by file, which hunks are *superseded* (the same intent already
   landed, possibly better) and which are *unique* (nobody has since expressed
   this idea anywhere on the default branch).
3. Transplant the unique hunks onto current `main` on a new `salvage/pr-<n>-<what>`
   branch. Prefer the exact post-change blobs over a re-typed approximation;
   re-typing is how detail is lost.
4. Open the salvage PR, then close the original **with a link to it**, so the
   provenance survives in both directions.
5. If a conflict appears during the transplant, resolve it semantically — read at
   least 5 commits of surrounding history and merge the two intents. Never pick a
   side to make the conflict go away.

## When a PR may be treated as stale

Only when **all** of these hold, or a human says it is obsolete:

- it is clearly superseded — the same change is already on the default branch, or
  a newer PR covers the same intent; **and**
- it has no unique product direction left; **and**
- it is a duplicate of a fleet-wide campaign whose unique hunks have already been
  harvested elsewhere.

"It has conflicts" is not a reason. "It is old" is not a reason. "CI is red" is
not a reason — a red check is a thing to fix or to classify, and at this scale red
is nearly always a handful of root causes wearing hundreds of faces.

## Why this is written down

Automation closes PRs far faster than a person does, and an agent that is told to
"clean up stale PRs" will happily discard a year of half-finished good ideas in an
afternoon. This file is the standing instruction that makes that a policy
violation rather than a tidy-up.

The canonical statement of these rules lives in
[`ORESoftware/my-ai/AGENTS.md`](https://github.com/ORESoftware/my-ai/blob/main/AGENTS.md).
This copy exists so the rule is visible from inside the organization; when the two
disagree, `AGENTS.md` wins.
