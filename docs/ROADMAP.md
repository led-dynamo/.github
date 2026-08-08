# Leddy delivery roadmap

This document is the GitHub-facing execution map for the `led-dynamo` organization. Linear owns priority, milestones, dependencies, and status; GitHub owns code, reviews, checks, releases, and runtime evidence.

## Planning surfaces

- [GitHub Project: led-dynamo-project](https://github.com/orgs/led-dynamo/projects/1)
- [Linear project: github.com/led-dynamo](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- [Linear architecture and delivery map](https://linear.app/denman/document/leddy-architecture-and-delivery-map-910ae52f998f)
- [Organization delivery tracker](https://github.com/led-dynamo/.github/issues/9)
- [Project-routing contract](./PROJECTS.md)

## Current repository fleet

| Layer | Repositories |
| --- | --- |
| Organization governance | `.github` |
| Contracts and packages | `leddy-interfaces`, `leddy-lib`, `leddy-clients` |
| Control plane | `leddy-api-server.rs`, `leddy-web-server.rs`, `leddy-cli` |
| Devices | `leddy-arduino`, `leddy-rasp-pi` |
| Validation and delivery | `leddy-e2e`, `leddy-infra`, `leddy-monorepo` |

## Package and runtime boundaries

```text
leddy-interfaces
      |
      +--> leddy-lib
      +--> leddy-clients

web/API servers and device agents consume canonical interfaces;
rendering targets also consume leddy-lib;
leddy-cli consumes interfaces + lib + clients.
```

Zed packages materialize under `.vendor/.zed`. Generated `.zpkg.lock` files are committed only after a real resolver run against published packages.

## Milestone 1 — Software-only vertical slice — complete

Linear: [DEN-2343](https://linear.app/denman/issue/DEN-2343/deliver-the-leddy-software-only-vertical-slice)

The complete API/CLI → WebSocket device → canonical renderer → telemetry/E2E path is merged.

Evidence:

- [`leddy-lib#2`](https://github.com/led-dynamo/leddy-lib/pull/2) / [`2a9a0cd`](https://github.com/led-dynamo/leddy-lib/commit/2a9a0cd43180d4be1f09b1fd98ec00ead9203795): deterministic playback lifecycle and physical LED-chain ordering;
- [`leddy-cli#4`](https://github.com/led-dynamo/leddy-cli/pull/4) / [`5adb8c6`](https://github.com/led-dynamo/leddy-cli/commit/5adb8c6f09530c838cc8daf30ed606c286ca1edd): modular CLI and canonical offline preview;
- [`leddy-api-server.rs#3`](https://github.com/led-dynamo/leddy-api-server.rs/pull/3) / [`3171b44`](https://github.com/led-dynamo/leddy-api-server.rs/commit/3171b4412db972e773ac1ca44e4812b1f522b285): desired-state revisions, reconnect replay, and duplicate suppression;
- [`leddy-e2e#3`](https://github.com/led-dynamo/leddy-e2e/pull/3) / [`907939c`](https://github.com/led-dynamo/leddy-e2e/commit/907939c48f8656da3c935161897e34e92c9d2347): live API + Rust virtual-device E2E covering 300×20 and 100×5 boards, arbitrary-length messages, both directions, all repeat modes, telemetry, clear, reconnect, and replay de-duplication.

## Milestone 2 — First physical LED sign — software ready, hardware gated

### Raspberry Pi

Linear: [DEN-2346](https://linear.app/denman/issue/DEN-2346/connect-the-raspberry-pi-agent-to-a-real-configurable-led-matrix)

[`leddy-rasp-pi#2`](https://github.com/led-dynamo/leddy-rasp-pi/pull/2) merged as [`7ce0089`](https://github.com/led-dynamo/leddy-rasp-pi/commit/7ce00891b3e6760736df40d29a20ba23cd820778). The runtime now has current protocol capabilities, canonical frame playback/order, brightness, acknowledgements, telemetry, atomic persisted configuration, bounded reconnect, and a no-GPIO frame-snapshot mode.

The remaining direct panel driver is intentionally blocked on [DEN-2893](https://linear.app/denman/issue/DEN-2893/select-leddy-physical-panel-topology-and-power-architecture). Choose the panel family, signal interface, voltage/current budget, level shifting, fusing, wire gauge, and power-injection topology before committing to Raspberry Pi GPIO code.

### Arduino / ESP32

Linear: [DEN-2349](https://linear.app/denman/issue/DEN-2349/implement-arduinoesp32-firmware-against-the-shared-device-protocol) — complete

[`leddy-arduino#2`](https://github.com/led-dynamo/leddy-arduino/pull/2) merged as [`4aa3154`](https://github.com/led-dynamo/leddy-arduino/commit/4aa315414c6893c5a2c9425533d3631f4e01238c). The firmware now supports configure/show/clear/ping, hello/ack/telemetry/pong/errors, left/right scrolling, once/forever/count playback, bounded frame planning, runtime matrix configuration, recovery documentation, and a hardware-in-loop smoke plan.

The merge gate passed four independent lanes: host-native contract tests, Arduino ESP32, native ESP-IDF ESP32-S3, and STM32Cube HAL. ESP-IDF source selection now uses its supported CMake component mechanism instead of PlatformIO source filtering.

## Milestone 3 — WhatsApp message ingestion — capability gated

Linear: [DEN-2352](https://linear.app/denman/issue/DEN-2352/add-authenticated-whatsapp-group-and-channel-ingestion)

The intended connector still normalizes approved inbound messages into canonical `MessageEnvelope` commands, deduplicates retries, records an audit trail, and exposes preview/pause/approval/emergency-clear controls. Connector credentials never reach display devices.

Before deploying public webhook infrastructure, complete [DEN-2898](https://linear.app/denman/issue/DEN-2898/verify-official-whatsapp-groupchannel-ingestion-eligibility): verify the exact official Meta capability available to the actual account for group/channel ingestion. Standard Cloud API inbound webhooks are a valid supported integration surface, but group/channel support must not be assumed or replaced with unofficial browser/session scraping.

Cloudflare webhook/DNS/R2 provisioning is intentionally deferred until that eligibility and ingress shape are known.

## Current execution status

- Software-only vertical slice: complete and green end to end.
- Arduino/ESP32 protocol parity: complete with four-target CI.
- Raspberry Pi software runtime: merged; physical panel driver remains gated by DEN-2893.
- WhatsApp connector: planning exists; deployment remains gated by DEN-2898.
- Organization delivery tracker: [.github issue #9](https://github.com/led-dynamo/.github/issues/9).

## Merge policy

PRs are merged only when their semantics improve the current default branch. When branches diverge, preserve the strongest behavior from both sides rather than choosing an entire side mechanically. Superseded PRs should be closed with a clear pointer to the replacement implementation.
