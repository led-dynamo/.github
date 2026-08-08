<!-- org-project-routing:start -->
# Project routing

- **GitHub organization:** [led-dynamo](https://github.com/led-dynamo)
- **Canonical GitHub Project:** [led-dynamo-project](https://github.com/orgs/led-dynamo/projects/1) (project 1)
- **Canonical Linear project:** [planning workspace](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- **Organization documentation repository:** [led-dynamo/.github](https://github.com/led-dynamo/.github)

## Source-of-truth boundaries

GitHub is authoritative for repositories, commits, pull requests, reviews, CI checks, releases, deployable artifacts, and runtime evidence. Linear is authoritative for product planning, priorities, ownership, dependencies, milestones, and status reporting. The GitHub Project is the organization-level execution board and should contain the governance issue maintained by this repository.

## Change and merge policy

Documentation branches must be reviewed through pull requests and merged after checks pass. Concurrent edits are reconciled semantically against the latest default branch: this managed routing block is regenerated while all unrelated prose outside the block is preserved. Do not resolve conflicts by blindly choosing one side.
<!-- org-project-routing:end -->

## Zed dependency rollout

| Consumer | Canonical dependencies | Delivery |
| --- | --- | --- |
| `leddy-clients` | interfaces (plus shared lib) | already present |
| `leddy-lib` | interfaces | already present |
| `leddy-cli` | clients, interfaces, lib | already present |
| `leddy-api-server.rs` | interfaces, lib, shared-auth; sync after publication | PR #2 |
| `leddy-web-server.rs` | interfaces, lib, shared-auth; sync after publication | PR #3 |
| `leddy-e2e` | clients, interfaces, lib, CLI | PR #2 |
| `leddy-monorepo` | clients, interfaces, lib, CLI, shared-auth; sync after publication | PR #2 |
| `leddy-mcp-server.rs` | clients, interfaces, lib, CLI, sync, shared-auth | issue #18 / seed below |

All packages materialize under `.vendor/.zed`. A canonical package may remain a committed gitlink as exact source transport, but it must be adopted with `zed overtake --git-submodules`; duplicate package identities, long-name aliases, and second workspace paths are prohibited.

## Repository publication seeds

- [`repository-seeds/leddy-sync/`](../repository-seeds/leddy-sync/) — canonical sync library; tracked by [issue #17](https://github.com/led-dynamo/.github/issues/17).
- [`repository-seeds/leddy-mcp-server.rs/`](../repository-seeds/leddy-mcp-server.rs/) — read-only MCP server; tracked by [issue #18](https://github.com/led-dynamo/.github/issues/18) and published only after `leddy-sync`.

Each seed has an idempotent authenticated-`gh` publisher that refuses to overwrite an existing repository and embeds no credentials. GitHub Project #1 owns execution visibility; the Linear project owns priority, dependencies, milestones, and delivery status.
