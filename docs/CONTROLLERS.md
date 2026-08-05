# Controller support and extraction roadmap

Leddy supports multiple device classes behind one command, capability, and telemetry contract. The controller family must be advertised in the device `hello` event so servers can select compatible transports, display limits, and rollout policies.

## Current support matrix

| Target | Framework/runtime | Status | Transport profile | Canonical implementation |
|---|---|---|---|---|
| Arduino-compatible ESP32 | Arduino + PlatformIO | Existing baseline | Wi-Fi, WebSocket, USB serial | `leddy-arduino` environment `esp32dev` |
| ESP32-S3 | Native ESP-IDF + FreeRTOS | Implemented | USB serial, Wi-Fi, BLE | `leddy-arduino/src/ports/esp32-idf` |
| STM32F446RE | STM32Cube HAL | Implemented | USB serial, optional Ethernet | `leddy-arduino/src/ports/stm32cube` |
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

The native source directories are deliberately self-contained so they can become independent repositories without rewriting firmware:

1. Create public `led-dynamo/leddy-esp32` and move the ESP-IDF port plus common contract tests into it.
2. Create public `led-dynamo/leddy-stm32` and move the STM32Cube port plus common contract tests into it.
3. Keep `leddy-arduino` focused on Arduino-framework firmware after both extractions.
4. Add both repositories to `leddy-monorepo` as optional device-agent submodules; do not make either a dependency of `leddy-interfaces`, `leddy-lib`, or `leddy-clients`.
5. Keep protocol ownership in `leddy-interfaces` and cross-controller fixtures in `leddy-e2e`.

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
- Protocol implementation: [`leddy-interfaces` PR #1](https://github.com/led-dynamo/leddy-interfaces/pull/1)
- End-to-end fixtures: [`leddy-e2e` PR #1](https://github.com/led-dynamo/leddy-e2e/pull/1)
