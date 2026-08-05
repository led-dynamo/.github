

<!-- org-project-routing:start -->
# Project routing

- **GitHub organization:** [led-dynamo](https://github.com/led-dynamo)
- **Canonical GitHub Project:** [led-dynamo-project](https://github.com/orgs/led-dynamo/projects/1) (project 1)
- **Canonical Linear project:** [planning workspace](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- **Organization documentation repository:** [led-dynamo/.github](https://github.com/led-dynamo/.github)

## Source-of-truth boundaries

GitHub is authoritative for repositories, commits, pull requests, reviews, CI checks, releases, deployable artifacts, and runtime evidence. Linear is authoritative for product planning, priorities, ownership, dependencies, milestones, and status reporting. The GitHub Project is the organization-level execution board and should contain the governance issue maintained by this repository.

## Current controller expansion

- [Controller support and extraction roadmap](CONTROLLERS.md)
- [Create standalone `leddy-esp32`](https://github.com/led-dynamo/.github/issues/5)
- [Create standalone `leddy-stm32` and complete hardware validation](https://github.com/led-dynamo/.github/issues/6)
- [Merged firmware implementation](https://github.com/led-dynamo/leddy-arduino/pull/1)
- [Merged protocol implementation](https://github.com/led-dynamo/leddy-interfaces/pull/1)
- [Merged end-to-end fixtures](https://github.com/led-dynamo/leddy-e2e/pull/1)

Both open extraction issues belong in the canonical organization Project. Their matching Linear issues carry planning state and dependencies; GitHub remains authoritative for repository creation and code delivery.

## Change and merge policy

Documentation branches must be reviewed through pull requests and merged after checks pass. Concurrent edits are reconciled semantically against the latest default branch: this managed routing block is regenerated while all unrelated prose outside the block is preserved. Do not resolve conflicts by blindly choosing one side.
<!-- org-project-routing:end -->
