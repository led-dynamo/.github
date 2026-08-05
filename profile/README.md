# LED Dynamo · Leddy

Leddy is a configurable, internet-connected LED message-board platform for
matrices ranging from narrow ticker displays to boards hundreds of pixels
wide. Messages can be submitted through the web/API layer, streamed to an
Arduino-compatible controller, native ESP32-S3, STM32F4, or Raspberry Pi, and
rendered as continuously scrolling text so message length is not constrained
by display width.

## Data path

```text
WhatsApp connector / web UI / CLI
                │
                ▼
      Rust web + API servers
                │  WebSocket commands and telemetry
                ▼
 Arduino / ESP32-S3 / STM32F4 / Raspberry Pi
                │
                ▼
 configurable LED matrix + scrolling renderer
```

WhatsApp is treated as a connector rather than a hard dependency, allowing the
same system to accept messages from a browser, CLI, automation, MQTT bridge, or
other messaging platform.

## Controller matrix

| Controller | Runtime | Status |
|---|---|---|
| Arduino-compatible ESP32 | Arduino + PlatformIO | Existing baseline |
| ESP32-S3 | Native ESP-IDF + FreeRTOS | Implemented and CI-targeted |
| STM32F446RE | STM32Cube HAL | Implemented and CI-targeted |
| Raspberry Pi | Linux device agent | Existing baseline |

See [controller support and extraction roadmap](../docs/CONTROLLERS.md) for
transport capabilities, hardware validation gates, and the planned standalone
`leddy-esp32` and `leddy-stm32` repository split.

## Repository map

| Repository | Responsibility |
|---|---|
| `leddy-interfaces` | Canonical Rust types, OpenAPI, AsyncAPI, and JSON Schema contracts |
| `leddy-lib` | Shared matrix framebuffer, font, and scrolling renderer |
| `leddy-clients` | Polyglot SDK family generated around the contracts |
| `leddy-web-server.rs` | Browser UI and operator WebSocket surface |
| `leddy-api-server.rs` | Device/message API, command fan-out, and telemetry intake |
| `leddy-cli` | Operator and automation command-line client |
| `leddy-arduino` | Arduino firmware plus native ESP-IDF and STM32Cube MCU ports |
| `leddy-rasp-pi` | Raspberry Pi display-agent daemon |
| `leddy-e2e` | Browser, protocol, controller-capability, device-simulator, and system tests |
| `leddy-infra` | Kubernetes, GitOps, and deployment configuration |
| `leddy-monorepo` | Fleet manifest and coordinated development workspace |

The canonical dependency direction is interfaces → library/clients → servers
and device agents → CLI and end-to-end tests. Zed packages materialize under
`.vendor/.zed`; resolver-generated lockfiles are committed only after packages
are published and resolvable.

<!-- org-project-routing:start -->
## Planning and delivery

- [GitHub Project: led-dynamo-project](https://github.com/orgs/led-dynamo/projects/1)
- [Linear planning project](https://linear.app/denman/project/githubcomled-dynamo-bd51986e8494)
- [Detailed project-routing contract](../docs/PROJECTS.md)
- [Controller support roadmap](../docs/CONTROLLERS.md)

GitHub owns code and delivery evidence; Linear owns planning and dependencies. The linked organization Project provides the cross-repository execution view.
<!-- org-project-routing:end -->
