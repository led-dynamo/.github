# Desktop application allocation

Verified **2026-08-05**.

LED Dynamo is a **strong candidate** for paired native desktop device-control applications:

- Rust: [`led-dynamo/led-dynamo-desktop.rs`](https://github.com/led-dynamo/led-dynamo-desktop.rs) — **proposed**, not yet verified as a published repository.
- Flutter: [`led-dynamo/led-dynamo-flutter`](https://github.com/led-dynamo/led-dynamo-flutter) — **proposed**, not yet verified as a published repository.

These names are proposed allocation targets, not proof that either remote exists and not a claim that implementation is approved or complete. Promote the pair from proposed to planned only when scope, ownership, milestones, supported boards/transports, and repository creation are accepted in Linear.

## Product boundary

The pair should cover semantic parity for local device discovery, serial/USB configuration, MQTT and WebSocket connections, command and telemetry diagnostics, matrix preview, fonts and assets, playlists, schedules, firmware management, offline control, reconnect/recovery, and per-board capability reporting.

A shared Rust device and transport core may sit behind an explicit library, FFI, or local-service boundary, but the Flutter application remains independently buildable, testable, and releasable. Shared schemas, commands, telemetry contracts, fixtures, simulator traces, board capability matrices, firmware manifests, and conformance tests should be versioned deliberately.

## Feature-delivery rule

Once planned, every desktop-facing change must inspect both implementations, define shared acceptance and device-safety criteria, update both or record an explicit no-change rationale, and report Rust and Flutter status separately. Board, transport, firmware, and operating-system support must be verified rather than inferred.

## Project routing

- GitHub Project: [`led-dynamo-project` — Project 1](https://github.com/orgs/led-dynamo/projects/1)
- Linear project: `github.com/led-dynamo`
- Central registry: [`ORESoftware/project-registry`](https://github.com/ORESoftware/project-registry/blob/main/registry/desktop-applications.json)
- Portfolio rollout: [`DEN-2469`](https://linear.app/denman/issue/DEN-2469/roll-out-paired-rust-flutter-desktop-repositories-across-the-portfolio)

Promotion, repository creation, renames, transfers, archival, board/transport changes, or platform-status changes must update this document, Linear, the central registry, and both companion repositories together.
