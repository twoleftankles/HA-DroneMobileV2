"""Constants for the DroneMobile V2 integration."""
from __future__ import annotations

DOMAIN = "drone_mobile_v2"
MANUFACTURER = "Firstech / DroneMobile"

# Config keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UNITS = "units"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_FORCE_COMMAND = "force_command"

# Units
UNITS_IMPERIAL = "imperial"
UNITS_METRIC = "metric"

# Defaults
DEFAULT_UPDATE_INTERVAL = 5  # minutes
DEFAULT_UNITS = UNITS_IMPERIAL
DEFAULT_FORCE_COMMAND = False

# AWS Cognito — DroneMobile uses Cognito for authentication
AWS_COGNITO_URL = "https://cognito-idp.us-east-1.amazonaws.com/"
AWS_CLIENT_ID = "3l3gtebtua7qft45b4splbeuiu"

# DroneMobile REST API
API_BASE_URL = "https://api.dronemobile.com/api"
API_VEHICLES_PATH = "/v1/vehicle"
API_COMMAND_PATH = "/v1/iot/command"
API_TIMEOUT = 30

# Device type sent with commands
DEVICE_TYPE_VEHICLE = "1"

# Commands — must be uppercase per API
CMD_LOCK = "ARM"
CMD_UNLOCK = "DISARM"
CMD_REMOTE_START = "REMOTE_START"
CMD_REMOTE_STOP = "REMOTE_STOP"
CMD_TRUNK = "TRUNK"
CMD_PANIC_ON = "PANIC_ON"
CMD_PANIC_OFF = "PANIC_OFF"
CMD_AUX1 = "REMOTE_AUX1"
CMD_AUX2 = "REMOTE_AUX2"

# IoT commands for controller settings (sent via /v1/iot/command).
# These are educated guesses at the command strings; if the command is rejected
# by the API the switch will revert and log an error.
SETTING_COMMANDS: dict[str, tuple[str, str]] = {
    # setting_key           -> (command_when_true, command_when_false)
    "valet_mode_enabled":       ("VALET_ON",           "VALET_OFF"),
    "siren_enabled":            ("SIREN_ON",            "SIREN_OFF"),
    "shock_sensor_enabled":     ("SHOCK_SENSOR_ON",     "SHOCK_SENSOR_OFF"),
    "passive_arming_enabled":   ("PASSIVE_ARM_ON",      "PASSIVE_ARM_OFF"),
    "auto_door_lock_enabled":   ("AUTO_DOOR_LOCK_ON",   "AUTO_DOOR_LOCK_OFF"),
    "drive_lock_enabled":       ("DRIVE_LOCK_ON",       "DRIVE_LOCK_OFF"),
    "timer_start_enabled":      ("TIMER_START_ON",      "TIMER_START_OFF"),
    "turbo_timer_start_enabled": ("TURBO_TIMER_ON",     "TURBO_TIMER_OFF"),
}

# Platforms
PLATFORMS = [
    "sensor",
    "binary_sensor",
    "lock",
    "button",
    "switch",
    "number",
    "select",
    "device_tracker",
]

# Runtime/duration
MIN_RUN_TIME = 5    # minutes
MAX_RUN_TIME = 30   # minutes
DEFAULT_RUN_TIME = 15

# Climate presets
CLIMATE_PRESET_NONE    = "none"
CLIMATE_PRESET_HEAT    = "heat"
CLIMATE_PRESET_COOL    = "cool"
CLIMATE_PRESET_DEFROST = "defrost"
CLIMATE_PRESETS = [
    CLIMATE_PRESET_NONE,
    CLIMATE_PRESET_HEAT,
    CLIMATE_PRESET_COOL,
    CLIMATE_PRESET_DEFROST,
]

# Diagnostic keys
DIAG_LAST_POLL_TIME    = "last_poll_time"
DIAG_LAST_POLL_SUCCESS = "last_poll_success"
DIAG_API_ERROR_COUNT   = "api_error_count"
DIAG_LAST_ERROR        = "last_error_message"
DIAG_LAST_COMMAND      = "last_command"
DIAG_LAST_CMD_RESULT   = "last_command_result"
DIAG_LAST_CMD_TIME     = "last_command_time"

# Helpers to extract nested API response fields
# API response structure:
# {
#   "id": 12345,
#   "device_key": "abc123",
#   "vehicle_name": "My Car",
#   "last_known_state": {
#     "timestamp": "2024-01-01T12:00:00+00:00",
#     "mileage": 12345,
#     "latitude": 40.123,
#     "longitude": -75.456,
#     "gps_direction": "NE",
#     "controller": {
#       "main_battery_voltage": 12.6,
#       "current_temperature": 22,
#       "armed": true,
#       "ignition_on": true,
#       "engine_on": true,
#       "door_open": false,
#       "trunk_open": false,
#       "hood_open": false,
#     }
#   }
# }

def lks(data: dict) -> dict:
    """Return the last_known_state dict from a vehicle payload."""
    return data.get("last_known_state") or {}

def ctrl(data: dict) -> dict:
    """Return the controller dict from a vehicle payload."""
    return lks(data).get("controller") or {}
