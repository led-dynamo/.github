# Controller support and extraction roadmap

Leddy supports multiple device classes behind one command, capability, and telemetry contract. The controller family must be advertised in the device `hello` event so servers can select compatible transports, display limits, and rollout policies.

## Current support matrix

| Target | Framework/runtime | Status | Transport profile | Canonical implementation |
|---|---|---|---|---|
| Arduino-compatible ESP32 | Arduino + PlatformIO | Existing baseline | Wi-Fi, WebSocket, USB serial | `leddy-arduino` environment `esp32dev` |
| ESP32-S3 | Native ESP-IDF + FreeRTOS | Implemented and extraction-ready | USB serial, Wi-Fi, BLE | `leddy-arduino/src/ports/esp32-idf` |
| STM32F446RE | STM32Cube HAL | Implemented and extraction-ready | USB serial, optional Ethernet | `leddy-arduino/src/ports/stm32cube` |
| Raspberry Pi | Linux device agent | Existing baseline | Wi-Fi, Ethernet, USB serial | `leddy-rasp-pi` |

The native MCU ports share `leddy-arduino/src/ports/common`, which validates display dimensions and framebuffer memory before platform-specific rendering starts. CI builds the Arduino, ESP-IDF, and STM32Cube targets and runs host-native capability tests.

## Protocol contract

`leddy-interfaces` defines these controller families:

- `arduino`
- `raspberry_pi`
- `esp32`
- `stm32`

It also defines `usb_serial`, `wifi`, `ble`, and `ethernet` transports. Platform and transport fields are optional when decoding older device payloads. Missing data means “not advertised,” not automatically “unsupported.”

## Standalone repository extraction

The native controller source is now mechanically packageable. `leddy-arduino` contains `scripts/extract-controller-repo.sh`, which materializes either target into a complete standalone repository tree without network access:

```sh
bash scripts/extract-controller-repo.sh esp32 /tmp/leddy-esp32
bash scripts/extract-controller-repo.sh stm32 /tmp/leddy-stm32
```

Each generated tree contains the controller entrypoint, shared C portability layer, host-native tests, PlatformIO configuration, GitHub Actions CI, governance files, and an origin/migration record. `scripts/test-controller-extraction.sh` generates both trees in CI and strict-compiles the copied shared C layer to prevent source/extraction drift.

Publishing sequence:

1. Create public `led-dynamo/leddy-esp32` and `led-dynamo/leddy-stm32` repositories.
2. Generate and push each tree from the current `leddy-arduino` default branch.
3. Run native and firmware CI in each standalone repository.
4. Add both repositories to `leddy-monorepo` as optional device-agent submodules and fleet entries; do not make either a dependency of `leddy-interfaces`, `leddy-lib`, or `leddy-clients`.
5. Update organization routing and Linear links.
6. Remove duplicated native port sources from `leddy-arduino` only after downstream references have moved.

Repository creation remains the only automation gap in the current connected GitHub environment; the application can write branches/files/issues/PRs in existing repositories but does not expose an organization repository-creation mutation.

## Hardware validation gates

A controller target is release-ready only after:

- clean CI build using its native toolchain;
- device `hello`, command acknowledgement, telemetry, clear, and reconnect tests;
- framebuffer allocation and oversized-display rejection tests;
- at least one real HUB75 or addressable-LED fixture run;
- documented pin map, power budget, brownout behavior, watchdog behavior, and recovery path;
- signed firmware artifact and reproducible version metadata.

## Planning and delivery

- GitHub Project: [`led-dynamo-project`](https://github.com/orgs/led-dynamo/projects/1)
- Linear project: [`github.com/led-dynamo`](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- Firmware implementation: [`leddy-arduino` PR #1](https://github.com/led-dynamo/leddy-arduino/pull/1)
- Standalone packaging: [`leddy-arduino` PR #3](https://github.com/led-dynamo/leddy-arduino/pull/3)
- Protocol implementation: [`leddy-interfaces` PR #1](https://github.com/led-dynamo/leddy-interfaces/pull/1)
- End-to-end fixtures: [`leddy-e2e` PR #1](https://github.com/led-dynamo/leddy-e2e/pull/1)
- ESP32 extraction tracker: [`.github` issue #5](https://github.com/led-dynamo/.github/issues/5)
- STM32 extraction/hardware tracker: [`.github` issue #6](https://github.com/led-dynamo/.github/issues/6)
