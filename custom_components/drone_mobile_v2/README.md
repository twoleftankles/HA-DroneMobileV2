# DroneMobile V2 Home Assistant Integration

A full-featured custom component for controlling and monitoring your
**DroneMobile / Compustar / Firstech** remote start system from Home Assistant.

> ⚠️ **Disclaimer:** This integration uses DroneMobile's unofficial API.
> The integration authors accept no responsibility for damages
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
2. Add `https://github.com/twoleftankles/HA-DroneMobileV2` (type: Integration)
3. Search "DroneMobile V2" and install
4. Restart Home Assistant

### Manual
1. Copy the `custom_components/drone_mobile_v2/` folder into your HA config's
   `custom_components/` directory
2. Restart Home Assistant
3. Settings → Devices & Services → Add Integration → search **DroneMobile V2**

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
| Speed | Current vehicle speed |
| Heading | Direction in degrees (+ cardinal in attributes) |
| Odometer | Total mileage |
| Battery Voltage | 12V battery voltage |
| Vehicle Temperature | Ambient / interior temp |
| Cellular Signal | Cellular signal percentage |
| Ignition Status | Text state of ignition |
| API Error Count | Running count of API errors |
| Last Command | Name of last command sent |
| Last Command Result | Result/status of last command |

### Binary Sensors
| Entity | Description |
|---|---|
| Engine Running | True while engine is on |
| Ignition | Ignition state |
| Door Open | Any door open |
| Trunk Open | Trunk ajar |
| Hood Open | Hood ajar |
| Panic Status | True if panic is active |
| Towing Detected | True if towing motion detected |
| Low Battery | True if battery is low |

### Lock
| Entity | Description |
|---|---|
| Door Lock | Lock/Unlock → arms/disarms alarm |

### Buttons
| Entity | Description |
|---|---|
| Lock | Send lock/arm command (always fires) |
| Unlock | Send unlock/disarm command |
| Remote Start | Starts engine with current preset |
| Remote Stop | Stops engine |
| Trunk Release | Pops trunk |
| Panic | Activates panic/alarm |
| Aux 1 / Aux 2 | Auxiliary outputs |
| Force Refresh | Manually poll vehicle right now |

### Switches (Controller Settings)
| Entity | Description |
|---|---|
| Valet Mode | Enable/disable valet mode |
| Siren | Enable/disable siren output |
| Shock Sensor | Shock/impact detection |
| Passive Arming | Auto-arm after timeout |
| Auto Door Lock | Auto door lock feature |
| Drive Lock | Lock doors when driving |
| Timer Start | Timer start feature |
| Turbo Timer Start | Turbo timer start feature |
| **Auto Poll** | Toggle automatic polling |

> 📝 **Controller setting switches** appear as _unavailable_ if the DroneMobile
> API does not expose those fields for your plan/controller. Use the
> **dump_device_data** service to inspect your raw API payload and verify
> which keys are present.

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
| Location | GPS map tracker with speed, heading in attributes |

---

## Services

| Service | Description |
|---------|-------------|
| `drone_mobile_v2.send_lock` | Send lock/arm command unconditionally to all vehicles |
| `drone_mobile_v2.send_unlock` | Send unlock/disarm command unconditionally to all vehicles |
| `drone_mobile_v2.refresh_all` | Refresh all vehicles |
| `drone_mobile_v2.refresh_vehicle` | Refresh one vehicle (`vehicle_name` param) |
| `drone_mobile_v2.dump_device_data` | Dump raw JSON payload to HA config folder |
| `drone_mobile_v2.clear_tokens` | Clear stored auth tokens (force re-login) |

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
      - service: drone_mobile_v2.send_lock
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

## Troubleshooting

- **Entities unavailable after install:** Restart HA, then check Settings → Devices & Services → DroneMobile V2 → Logs
- **Controller setting switches unavailable:** Use `drone_mobile_v2.dump_device_data` to see which fields your API returns; not all plans/controllers expose settings
- **Auth errors:** Call `drone_mobile_v2.clear_tokens` then reload the integration
- **Vehicle not updating:** Check that **Auto Poll** switch is on, or press **Force Refresh**
