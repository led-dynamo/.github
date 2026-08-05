# Leddy delivery roadmap

This document is the GitHub-facing execution map for the `led-dynamo` organization. Linear owns priority, milestones, dependencies, and status; GitHub owns code, reviews, checks, releases, and runtime evidence.

## Planning surfaces

- [GitHub Project: led-dynamo-project](https://github.com/orgs/led-dynamo/projects/1)
- [Linear project: github.com/led-dynamo](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- [Linear architecture and delivery map](https://linear.app/denman/document/leddy-architecture-and-delivery-map-910ae52f998f)
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

## Milestone 1 — Software-only vertical slice

Linear: [DEN-2343](https://linear.app/denman/issue/DEN-2343/deliver-the-leddy-software-only-vertical-slice)

Deliver an arbitrary-length message through the API/CLI to a virtual WebSocket device, render deterministic scrolling frames, return acknowledgements and telemetry, and verify the flow in `leddy-e2e`.

Required evidence:

- message validation and command fan-out;
- configurable 100–300 by 5–20 display fixtures;
- left/right scrolling and once/forever/count playback;
- reconnect, replay, clear, and duplicate-suppression tests;
- CI links from every affected repository.

## Milestone 2 — First physical LED sign

- Raspberry Pi: [DEN-2346](https://linear.app/denman/issue/DEN-2346/connect-the-raspberry-pi-agent-to-a-real-configurable-led-matrix)
- Arduino/ESP32: [DEN-2349](https://linear.app/denman/issue/DEN-2349/implement-arduinoesp32-firmware-against-the-shared-device-protocol)

Validate the same contracts and renderer on physical hardware. Document power injection, level shifting, supported panel/strip types, current limits, safe shutdown, Wi-Fi provisioning, OTA updates, and recovery after power loss.

## Milestone 3 — WhatsApp message ingestion

Linear: [DEN-2352](https://linear.app/denman/issue/DEN-2352/add-authenticated-whatsapp-group-and-channel-ingestion)

Add WhatsApp as an optional authenticated connector. Allowlist sources, normalize messages into `MessageEnvelope`, deduplicate retries, keep an audit trail, and expose preview/pause/approval/emergency-clear controls. Connector credentials never reach display devices.

## Current execution status — 2026-08-05

- All 12 requested repositories are public and writable.
- Shared package manifests and dependency validation are present.
- The client SDK matrix is validated across native, BEAM, JVM/mobile, scripting, and TypeScript runtimes.
- [leddy-lib PR #2](https://github.com/led-dynamo/leddy-lib/pull/2) adds finite/infinite playback and physical LED-chain ordering.
- Four older draft PRs were closed as superseded rather than merged over stronger implementations.

## Merge policy

PRs are merged only when their semantics improve the current default branch. When branches diverge, preserve the strongest behavior from both sides rather than choosing an entire side mechanically. Superseded PRs should be closed with a clear pointer to the replacement implementation.
