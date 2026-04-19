# DroneMobile V2 — Custom Component

A full-featured Home Assistant integration for **DroneMobile / Compustar / Firstech** remote start and security systems.

For full documentation, installation instructions, and entity reference, see the [main README](https://github.com/twoleftankles/HA-DroneMobileV2).

---

## Quick Start

1. Install via HACS (add `https://github.com/twoleftankles/HA-DroneMobileV2` as a custom repository)
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration** and search for **DroneMobile V2**
4. Enter your DroneMobile email and password

---

## Services

| Service | Description |
|---------|-------------|
| `drone_mobile_v2.send_lock` | Send lock/arm command unconditionally to all vehicles |
| `drone_mobile_v2.send_unlock` | Send unlock/disarm command unconditionally to all vehicles |
| `drone_mobile_v2.refresh_all` | Force an immediate poll of all vehicles |
| `drone_mobile_v2.refresh_vehicle` | Force a poll for a specific vehicle (`vehicle_name` param) |
| `drone_mobile_v2.dump_device_data` | Write raw API response to a JSON file in your config folder |
| `drone_mobile_v2.clear_tokens` | Clear cached auth tokens and force re-authentication |

---

## Disclaimer

This integration uses the unofficial DroneMobile cloud API and is not affiliated with or endorsed by DroneMobile, Firstech, or CompuStar. Use at your own risk.
