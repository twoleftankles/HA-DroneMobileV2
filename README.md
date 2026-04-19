# DroneMobile V2

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue)](https://www.home-assistant.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured Home Assistant integration for **DroneMobile / Firstech / CompuStar** remote start and security systems. Control your vehicle, monitor telemetry, and automate your garage security — all from Home Assistant.

---

## Features

- **Lock / Unlock** — arm and disarm the vehicle alarm, always sends even if already locked (great for horn-beep automations)
- **Remote Start / Stop** — start or stop the engine remotely with configurable run time and climate preset
- **Trunk, Panic, Aux 1 & 2** — dedicated button entities for every command
- **GPS Tracking** — live device tracker with latitude, longitude, speed, and heading
- **Battery Monitoring** — main battery voltage with charging/good/low/critical thresholds, plus backup battery
- **Full Telemetry** — odometer, temperature, cellular signal, carrier, firmware version, controller model
- **Controller Settings** — toggle valet mode, siren, shock sensor, passive arming, auto door lock, drive lock, timer start, and turbo timer start via switches
- **Diagnostics** — API error count, last command sent, last result, last update timestamp
- **Custom Lovelace Card** — a built-in visual card with mini map, status chips, battery bars, and a visual editor

---

## Installation

### HACS (Recommended)

1. In Home Assistant, open **HACS → Integrations**
2. Click the **⋮** menu → **Custom repositories**
3. Add `https://github.com/twoleftankles/HA-DroneMobileV2` as an **Integration**
4. Search for **DroneMobile V2** and click **Download**
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration** and search for **DroneMobile V2**
7. Enter your DroneMobile account email and password

### Manual

1. Copy the `custom_components/drone_mobile_v2` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services → Add Integration**

---

## Lovelace Card

The integration ships with a custom Lovelace card (`www/drone-mobile-v2-card.js`) that provides a visual overview of your vehicle including a mini map, status chips, battery bars, and lock/unlock/remote-start buttons.

### Registering the Card

The card is registered **automatically** when the integration loads — no YAML changes needed. After installing via HACS and restarting Home Assistant, the card appears as **DroneMobile V2** in the Lovelace card picker with a full visual editor.

If for any reason auto-registration fails, you can register it manually by adding this to `configuration.yaml` and restarting:

```yaml
lovelace:
  resources:
    - url: /drone_mobile_v2/drone-mobile-v2-card.js
      type: module
```

### Card Features

- Vehicle status chips (engine, alarm, ignition, remote start, panic, towing)
- Telemetry row (speed, odometer, temperature, heading)
- Battery bars with voltage, status label, and color thresholds
- Door / trunk / hood status with open/closed color indicators
- Lock and Unlock buttons (always send the command regardless of current state)
- Remote start, stop, trunk, panic, Aux 1 & 2 control buttons
- Controller setting switches (valet mode, siren, shock sensor, etc.)
- Diagnostics panel
- Mini map with configurable zoom and custom vehicle icon
- All sections individually toggleable in the visual editor
- Fully theme-aware — inherits your HA theme colors

---

## Configuration

After adding the integration, configure it via **Settings → Devices & Services → DroneMobile V2 → Configure**:

| Option | Default | Description |
|--------|---------|-------------|
| Update interval | 5 min | How often to poll the DroneMobile API |
| Units | Imperial | Miles / °F or Kilometers / °C |
| Force commands | Off | Send commands even when current state already matches (not needed for lock — lock always sends by default) |

---

## Entities

### Lock

| Entity | Description |
|--------|-------------|
| Door Lock | Arm / disarm the alarm. Reports `locked` / `unlocked`. |

### Buttons

| Entity | Description |
|--------|-------------|
| Lock | Send lock/arm command — always fires regardless of current state |
| Unlock | Send unlock/disarm command |
| Remote Start | Start the engine |
| Remote Stop | Stop the engine |
| Trunk Release | Open the trunk |
| Panic | Trigger the panic alarm |
| Aux 1 / Aux 2 | Auxiliary outputs |
| Force Refresh | Immediately poll the API |

### Sensors

| Entity | Description |
|--------|-------------|
| Engine Status | `Running` / `Off` |
| Alarm | `Armed` / `Disarmed` |
| Remote Start Status | `Active` / `Off` |
| Maintenance Due | `True` / `False` |
| Battery Voltage | Main battery in V (1 decimal) |
| Backup Battery Voltage | Backup battery in V (2 decimal) |
| Vehicle Temperature | Cabin temperature in °F / °C |
| Odometer | Miles or kilometers |
| Speed | MPH or KPH |
| GPS Direction | Cardinal direction (e.g. `North`) |
| GPS Heading | Degrees (0–360) |
| Cellular Signal | Percentage |
| Cellular Carrier | Carrier name |
| Firmware Version | Controller firmware string |
| Controller Model | Controller model string |
| Last Update | Timestamp of last vehicle report |
| Last Command | Most recently sent command name |
| Last Command Result | API result for the last command |
| API Error Count | Cumulative count of API errors |

### Binary Sensors

| Entity | Device Class | On State | Off State |
|--------|-------------|----------|-----------|
| Ignition | — | On | Off |
| Door Status | Door | Open | Closed |
| Trunk Status | Opening | Open | Closed |
| Hood Status | Opening | Open | Closed |
| Panic Status | — | Active | Off |
| Towing Detected | Motion | Detected | Clear |
| Low Battery | Battery | Low | Normal |
| Battery Disconnected | Problem | Disconnected | OK |
| Backup Battery | Battery | Low | Normal |

### Switches

| Entity | Description |
|--------|-------------|
| Valet Mode | Enable / disable valet mode |
| Siren | Enable / disable the siren |
| Shock Sensor | Enable / disable shock sensor |
| Passive Arming | Enable / disable passive arming |
| Auto Door Lock | Enable / disable auto door lock |
| Drive Lock | Enable / disable drive lock |
| Timer Start | Enable / disable timer start |
| Turbo Timer Start | Enable / disable turbo timer start |
| Auto Poll | Pause automatic API polling |

### Number / Select

| Entity | Description |
|--------|-------------|
| Remote Start Duration | Run time for the next remote start (5–30 min) |
| Climate Preset | Heat, Cool, Defrost, or None for the next remote start |

### Device Tracker

| Entity | Description |
|--------|-------------|
| Location | Live GPS position — latitude, longitude, speed, and heading |

---

## Services

| Service | Description |
|---------|-------------|
| `drone_mobile_v2.send_lock` | Send lock/arm to all vehicles unconditionally |
| `drone_mobile_v2.send_unlock` | Send unlock/disarm to all vehicles unconditionally |
| `drone_mobile_v2.refresh_all` | Force an immediate poll of all vehicles |
| `drone_mobile_v2.refresh_vehicle` | Force a poll for a specific vehicle (pass `vehicle_name`) |
| `drone_mobile_v2.dump_device_data` | Write raw API response to a JSON file in your config folder |
| `drone_mobile_v2.clear_tokens` | Clear cached auth tokens and force re-authentication |

> **Tip — Frigate horn-beep automation:** Because `send_lock` always transmits the arm signal regardless of current state, you can use it to beep your vehicle's horn when motion is detected. The vehicle will emit a confirmation beep even if it's already armed.

---

## Automation Examples

### Lock at 11pm

```yaml
alias: Lock Vehicle at 11pm
triggers:
  - trigger: time
    at: "23:00:00"
conditions:
  - condition: state
    entity_id: person.your_name
    state: home
actions:
  - action: drone_mobile_v2.send_lock
mode: single
```

### Horn beep on person detection (Frigate)

```yaml
alias: Front Yard Person - Lock Vehicle
triggers:
  - trigger: state
    entity_id: binary_sensor.front_person_occupancy
    to: "on"
conditions:
  - condition: time
    after: "23:00:00"
    before: "06:00:00"
  - condition: state
    entity_id: person.your_name
    state: home
actions:
  - action: drone_mobile_v2.send_lock
  - delay: "00:05:00"   # rate limit — blocks re-trigger for 5 minutes
mode: single
max_exceeded: silent
```

### Alert when alarm triggers
```yaml
automation:
  - alias: Notify on car alarm
    trigger:
      - platform: state
        entity_id: binary_sensor.your_vehicle_name_panic_status
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Car Alarm"
          message: "Vehicle alarm has been triggered!"
```

### Remote start on cold mornings
```yaml
automation:
  - alias: Start car on cold mornings
    trigger:
      - platform: time
        at: "07:30:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.your_vehicle_name_vehicle_temperature
        below: 35
    action:
      - service: button.press
        target:
          entity_id: button.your_vehicle_name_remote_start
```

---

## Notes

- This integration uses the unofficial DroneMobile cloud API — the same endpoints used by the DroneMobile mobile app and web portal. DroneMobile may change the API without notice.
- Tested on a CompuStar CM900AS controller with Home Assistant 2026.4.
- Controller settings (switches) are written via the `/v1/device/{key}/features` endpoint used by the official DroneMobile web app.
- The Lock button entity and `send_lock` service both always transmit the command to the vehicle regardless of the current `armed` state. This is intentional and enables horn-beep use cases.

## Disclaimer

This integration is not affiliated with or endorsed by DroneMobile, Firstech, or CompuStar. Use at your own risk.
