<!-- ore-org-baseline:begin -->
# Repository relationships for `led-dynamo`

This file is rendered from `repository-relationships.json`. The JSON registry is authoritative.

- Audience: `public`
- Repositories represented: **12**
- Relationships represented: **16**
- Inventory digest: `sha256:40d741713ce986ee8c44fc6c6d3a8fffff9ffcdcb84443e32c19bb8ec8c05fe9`

## Immutable routing identity

| Field | Value |
|---|---|
| Mapping ID | `context:led-dynamo` |
| GitHub owner ID | `313447864` |
| Linear project ID | `82f88159-8d79-4daa-9d3e-3781acf48e7e` |
| Linear team ID | `eb8ab169-5afe-4b6f-9cab-3f2aa3e887dc` |

## Repositories

| Repository | Visibility | Roles | Archived |
|---|---|---|---|
| `led-dynamo/.github` | `public` | `community-health`, `governance`, `relationship-registry` | no |
| `led-dynamo/leddy-api-server.rs` | `public` | `api-server` | no |
| `led-dynamo/leddy-arduino` | `public` | `repository` | no |
| `led-dynamo/leddy-cli` | `public` | `repository` | no |
| `led-dynamo/leddy-clients` | `public` | `clients` | no |
| `led-dynamo/leddy-e2e` | `public` | `end-to-end-tests` | no |
| `led-dynamo/leddy-infra` | `public` | `infrastructure` | no |
| `led-dynamo/leddy-interfaces` | `public` | `interfaces` | no |
| `led-dynamo/leddy-lib` | `public` | `repository` | no |
| `led-dynamo/leddy-monorepo` | `public` | `monorepo` | no |
| `led-dynamo/leddy-rasp-pi` | `public` | `repository` | no |
| `led-dynamo/leddy-web-server.rs` | `public` | `web-server` | no |

## Relationships

| From | Type | To | Status | Required |
|---|---|---|---|---|
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-api-server.rs` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-arduino` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-cli` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-clients` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-e2e` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-infra` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-interfaces` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-lib` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-monorepo` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-rasp-pi` | `declared` | yes |
| `led-dynamo/.github` | `governs` | `led-dynamo/leddy-web-server.rs` | `declared` | yes |
| `led-dynamo/leddy-api-server.rs` | `depends_on` | `led-dynamo/leddy-interfaces` | `inferred` | no |
| `led-dynamo/leddy-clients` | `depends_on` | `led-dynamo/leddy-interfaces` | `inferred` | no |
| `led-dynamo/leddy-e2e` | `tests` | `led-dynamo/leddy-monorepo` | `inferred` | no |
| `led-dynamo/leddy-infra` | `deploys` | `led-dynamo/leddy-monorepo` | `inferred` | no |
| `led-dynamo/leddy-web-server.rs` | `depends_on` | `led-dynamo/leddy-interfaces` | `inferred` | no |

## Editing relationships

Put reviewed public declarations in `repository-relationships.manual.json`; do not edit the generated registry directly.
Private repository names and private-only relationships belong in the private `approved-private-registry` mirror.
Inferred edges are advisory and must remain visibly labeled until reviewed.
<!-- ore-org-baseline:end -->
