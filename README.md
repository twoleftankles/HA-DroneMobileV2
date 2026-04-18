# DroneMobile V2 for Home Assistant

A feature-complete Home Assistant integration for DroneMobile / Firstech / CompuStar remote start systems. Installable via [HACS](https://hacs.xyz).

## Features

- **Lock / Unlock** — arm and disarm the vehicle alarm
- **Remote Start / Stop** — start or stop the engine remotely
- **Trunk Release, Panic, Aux 1 & 2** — one-press buttons
- **GPS Tracking** — live device tracker with latitude/longitude
- **Controller Settings** — toggle valet mode, siren, shock sensor, passive arming, auto door lock, drive lock, timer start, and turbo timer start
- **Full Telemetry** — odometer, speed, GPS heading/direction, battery voltage, backup battery, temperature, cellular signal, firmware version, and more
- **Diagnostics** — API error count, last command, last command result, last update timestamp
- **Auto Poll Switch** — pause polling to conserve vehicle battery
- **Remote Start Duration** — slider to configure run time (5–30 min)
- **Climate Preset** — heat, cool, defrost, or none for the next remote start

## Installation via HACS

1. In HACS, go to **Integrations → Custom Repositories**
2. Add this repository URL and select **Integration** as the category
3. Search for **DroneMobile V2** and install
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration** and search for **DroneMobile V2**
6. Enter your DroneMobile account email and password

## Manual Installation

1. Copy the `custom_components/drone_mobile_v2` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services**

## Configuration

After adding the integration, configure via the options flow:

| Option | Default | Description |
|--------|---------|-------------|
| Update interval | 5 min | How often to poll the DroneMobile API |
| Units | Imperial | Miles/°F or Kilometers/°C |
| Force commands | Off | Send commands even if the current state already matches |

## Entities

### Controls
| Entity | Type | Description |
|--------|------|-------------|
| Door Lock | Lock | Arm / disarm the alarm |
| Remote Start | Button | Start the engine |
| Remote Stop | Button | Stop the engine |
| Trunk Release | Button | Open the trunk |
| Panic | Button | Trigger the panic alarm |
| Aux 1 / Aux 2 | Button | Auxiliary outputs |
| Force Refresh | Button | Immediate data refresh |

### Controller Settings (Switches)
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

### Sensors
Odometer, Speed, GPS Direction, GPS Heading, Battery Voltage, Backup Battery Voltage, Vehicle Temperature, Cellular Signal, Cellular Carrier, Firmware Version, Controller Model, Last Update, API Error Count, Last Command, Last Command Result

### Binary Sensors
Engine Running, Ignition, Armed, Door Open, Trunk Open, Hood Open, Panic Active, Remote Started, Towing Detected, Service Due, Low Battery, Battery Disconnected, Backup Battery OK

## Notes

- Controller settings are written via the official DroneMobile API endpoint (`/v1/device/{key}/features`) — the same endpoint used by the DroneMobile web app
- This integration uses an unofficial API. DroneMobile may change it without notice
- Tested on CompuStar CM900AS controller with HA 2026.4

## Disclaimer

This integration is not affiliated with or endorsed by DroneMobile, Firstech, or CompuStar. Use at your own risk.
