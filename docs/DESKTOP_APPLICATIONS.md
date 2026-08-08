# LED Dynamo desktop applications

Verified **2026-08-06**.

## Required pair

- Rust: [`led-dynamo/leddy-desktop.rs`](https://github.com/led-dynamo/leddy-desktop.rs) — **planned**, not yet verified as published.
- Flutter: [`led-dynamo/leddy-flutter`](https://github.com/led-dynamo/leddy-flutter) — **planned**, not yet verified as published.

These names supersede the earlier `led-dynamo-desktop.rs` and `led-dynamo-flutter` proposals. Do not mark either implementation live until the remote, native build, packaging, tests, and supported-board/platform matrix are verified.

## Rust desktop kit: Slint, fully native

The Rust application uses **Slint**.

- Embedded WebViews are prohibited.
- Rust owns device discovery, serial/USB and network transports, command validation, telemetry, firmware metadata, persistence, scheduling, deep-link parsing, and privileged operations.
- Slint owns compiled native presentation, matrix preview, controls, diagnostics, and user interaction.
- OS and device integration belongs behind small Rust platform/transport adapters.

This strategy provides a small native runtime, direct hardware access, deterministic rendering, and low-overhead offline control for LED matrices and embedded boards.

The future Rust repository must contain `docs/DESKTOP_TOOLKIT.md` documenting the Slint version policy, no-WebView rule, device/privilege boundaries, performance budgets, deep links, packaging, platform/board tests, and Flutter companion.

## Parallel Rust and Flutter development

The Rust and Flutter applications are first-class implementations developed side-by-side to compare native performance and device integration against Flutter portability/mobile reuse, accessibility, developer velocity, packaging, and long-term maintenance.

Every desktop-facing feature must inspect both repositories, share acceptance criteria and fixtures, and normally update both. A one-sided change requires an explicit no-change rationale and parity gap. The future `leddy-desktop.rs` README, `AGENTS.md`, pull-request template, and `docs/DESKTOP_TOOLKIT.md` must state this rule prominently.

## HTTPS-first deep links

Canonical route family:

```text
https://<verified-leddy-owned-host>/open/<route>?<bounded-query>
```

Fallback scheme:

```text
leddy://<route>?<bounded-query>
```

Rust and Flutter must share versioned route types and golden fixtures.

Initial route families may include devices, matrices, previews, playlists, schedules, fonts/assets, firmware metadata, diagnostics, and authenticated notifications.

Required behavior:

- cold-start and already-running/single-instance delivery;
- exact host, route/version, device/board/playlist/schedule identifiers, action, and bounded-query validation;
- authenticated resume and browser fallback;
- replay, expiry, device ownership, capability, and unsafe-return validation;
- explicit confirmation before firmware operations, device reconfiguration, destructive changes, or external asset import; and
- macOS, Windows, Linux, Android, and iOS tests plus simulated-device fixtures.

Passwords, bearer tokens, Wi-Fi credentials, device secrets, firmware signing keys, MQTT credentials, or raw command payloads are prohibited in URLs. Use short-lived, one-time, audience-bound codes for device enrollment and privileged handoffs.

## Product boundary

Both implementations should converge on:

- local device discovery and capability reporting;
- serial/USB, MQTT, and WebSocket configuration;
- command/telemetry diagnostics;
- matrix preview, fonts, assets, playlists, and schedules;
- firmware metadata and safe update workflows;
- offline operation, reconnect/recovery, and notifications;
- schemas, generated clients, route fixtures, simulator traces, board capability matrices, and conformance tests.

## Project routing

- GitHub Project: [`led-dynamo-project` — Project 1](https://github.com/orgs/led-dynamo/projects/1)
- Linear project: `github.com/led-dynamo`
- Central registry: `approved-private-registry` — opaque internal locator; no private repository URL is published here.
- Toolkit strategy: maintained with the same approved private registry and mirrored into public organization documentation when releasable.
- Portfolio rollout: [`DEN-2469`](https://linear.app/denman/issue/DEN-2469/roll-out-paired-rust-flutter-desktop-repositories-across-the-portfolio)

Repository creation, toolkit changes, deep-link changes, renames, transfers, archival, board/transport changes, or platform-status changes must update this document, Linear, the approved registry, and both companion repositories together.
