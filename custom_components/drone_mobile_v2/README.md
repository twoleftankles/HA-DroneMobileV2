# DroneMobile Home Assistant Integration — Enhanced Rewrite v2.0

A full-featured custom component for controlling and monitoring your
**DroneMobile / Compustar / Firstech** remote start system from Home Assistant.

> ⚠️ **Disclaimer:** This integration uses DroneMobile's unofficial API.
> Anthropic / the integration authors accept no responsibility for damages
> to your vehicle. Use at your own risk.

---

## Requirements

- Home Assistant 2024.1+
- An active DroneMobile account (email + password)
- A vehicle with DroneMobile / Compustar hardware installed
- A DroneMobile subscription plan

---

## Installation (HACS or Manual)

### Via HACS (recommended)
1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/yourusername/drone_mobile_home_assistant` (type: Integration)
3. Search "DroneMobile" and install
4. Restart Home Assistant

### Manual
1. Copy the `custom_components/drone_mobile/` folder into your HA config's
   `custom_components/` directory
2. Restart Home Assistant
3. Settings → Devices & Services → Add Integration → search **DroneMobile**

---

## Configuration

Fill in your DroneMobile email, password, and preferences:

| Field | Default | Description |
|---|---|---|
| Email | — | Your DroneMobile login email |
| Password | — | Your DroneMobile password |
| Units | Imperial | Imperial (mph, mi, °F) or Metric (km/h, km, °C) |
| Poll Interval | 5 min | How often to auto-refresh vehicle data |
| Force Commands | Off | Send lock/unlock even if state already matches |

---

## Entities Created Per Vehicle

### Sensors
| Entity | Description |
|---|---|
| Fuel Level | Fuel tank % (if supported by your vehicle) |
| Speed | Current vehicle speed |
| Heading | Direction in degrees (+ cardinal in attributes) |
| Altitude | Elevation |
| Odometer | Total mileage |
| Battery Voltage | 12V battery voltage |
| Vehicle Temperature | Ambient / interior temp |
| Signal Strength | Cellular signal in dBm |
| Ignition Status | Text state of ignition |
| Door Lock Status | Text state of lock |
| Alarm Status | Text state of alarm |
| Last GPS Update | Timestamp of last GPS fix |
| Last Poll Time | Timestamp of last successful API poll |
| API Error Count | Running count of API errors |
| Last API Error | Most recent error message |
| Last Command | Name of last command sent |
| Last Command Result | Result/status of last command |
| Last Command Time | Timestamp of last command |

### Binary Sensors
| Entity | Description |
|---|---|
| Engine Running | True while engine is on |
| Ignition | Ignition state |
| Alarm Triggered | True if alarm is firing |
| Door Open | Any door open |
| Trunk Open | Trunk ajar |
| Hood Open | Hood ajar |
| Door Locked | True = locked (LOCK device class) |

### Lock
| Entity | Description |
|---|---|
| Door Lock | Lock/Unlock → arms/disarms alarm |
| Trunk | Unlock triggers trunk release |

### Buttons
| Entity | Description |
|---|---|
| Remote Start | Starts engine with current preset |
| Remote Stop | Stops engine |
| Trunk Release | Pops trunk |
| Panic | Activates panic/alarm |
| Aux 1–4 | Auxiliary outputs 1 through 4 |
| Force Refresh | Manually poll vehicle right now |

### Switches (Controller Settings)
| Entity | Description |
|---|---|
| Valet Mode | Enable/disable valet mode |
| Remote Start Enabled | Master remote start on/off |
| Siren | Enable/disable siren output |
| Passive Arming | Auto-arm after timeout |
| Two-Stage Unlock | Two-press unlock feature |
| Glass Break Sensor | Glass break detection |
| Brake Sensor | Brake-activate sensor |
| Tilt Sensor | Anti-tilt protection |
| Shock Sensor | Shock/impact detection |
| Nuisance Prevention | Reduce false alarms |
| **Auto Poll** | Toggle automatic polling (saves battery) |

> 📝 **Controller setting switches** appear as _unavailable_ if the DroneMobile
> API does not expose those fields for your plan/controller. Use the
> **dump_device_data** service to inspect your raw API payload and verify
> which keys are present. The `setting_key` attribute on each switch shows
> exactly what API field it maps to.

### Number
| Entity | Description |
|---|---|
| Remote Start Duration | Run time for next remote start (5–30 min slider) |

### Select
| Entity | Description |
|---|---|
| Climate Preset | Heat / Cool / Defrost / None (sent with next start) |

### Device Tracker
| Entity | Description |
|---|---|
| Location | GPS map tracker with speed, heading, altitude, fuel, battery in attributes |

---

## Lovelace Dashboard

A ready-made dashboard is included at `lovelace/drone_mobile_dashboard.yaml`.

1. Open **Dashboard** → ⋮ → **Edit Dashboard** → Raw configuration editor
2. Paste the YAML (or import as a new dashboard)
3. Find/replace `YOUR_VEHICLE_NAME` with your actual vehicle's entity slug
   (e.g. `my_car` for a vehicle named "My Car")

---

## Services

| Service | Description |
|---|---|
| `drone_mobile.refresh_all` | Refresh all vehicles |
| `drone_mobile.refresh_vehicle` | Refresh one vehicle (`vehicle_name` param) |
| `drone_mobile.dump_device_data` | Dump raw JSON payload to HA config folder |
| `drone_mobile.clear_tokens` | Clear stored auth tokens (force re-login) |

---

## Automations — Examples

### Auto-lock when you leave home
```yaml
automation:
  - alias: Lock car when leaving home
    trigger:
      - platform: zone
        entity_id: person.your_name
        zone: zone.home
        event: leave
    action:
      - service: lock.lock
        target:
          entity_id: lock.your_vehicle_name_door_lock
```

### Alert when alarm triggers
```yaml
automation:
  - alias: Notify on car alarm
    trigger:
      - platform: state
        entity_id: binary_sensor.your_vehicle_name_alarm_triggered
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚨 Car Alarm"
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

## Troubleshooting

- **Entities unavailable after install:** Restart HA, then check Settings → Devices & Services → DroneMobile → Logs
- **Controller setting switches unavailable:** Use `drone_mobile.dump_device_data` to see which fields your API returns; not all plans/controllers expose settings
- **Auth errors:** Call `drone_mobile.clear_tokens` then reload the integration
- **Vehicle not updating:** Check that **Auto Poll** switch is on, or press **Force Refresh**
