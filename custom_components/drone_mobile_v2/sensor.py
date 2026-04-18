"""Sensor platform for DroneMobile V2."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.util import dt as dt_util
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, UNITS_IMPERIAL, lks, ctrl
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DroneMobileSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any], DroneMobileCoordinator], Any] = lambda d, c: None
    imperial_unit: str | None = None
    metric_unit: str | None = None


SENSOR_DESCRIPTIONS: list[DroneMobileSensorDescription] = [
    # --- Vehicle telemetry ---
    DroneMobileSensorDescription(
        key="odometer",
        name="Odometer",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        imperial_unit=UnitOfLength.MILES,
        metric_unit=UnitOfLength.KILOMETERS,
        value_fn=lambda d, c: lks(d).get("mileage"),
    ),
    DroneMobileSensorDescription(
        key="speed",
        name="Speed",
        icon="mdi:speedometer",
        imperial_unit=UnitOfSpeed.MILES_PER_HOUR,
        metric_unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d, c: lks(d).get("speed"),
    ),
    DroneMobileSensorDescription(
        key="gps_direction",
        name="GPS Direction",
        icon="mdi:compass",
        value_fn=lambda d, c: lks(d).get("gps_direction"),
    ),
    DroneMobileSensorDescription(
        key="gps_degree",
        name="GPS Heading",
        icon="mdi:compass-rose",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d, c: lks(d).get("gps_degree"),
    ),
    DroneMobileSensorDescription(
        key="battery_voltage",
        name="Battery Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: ctrl(d).get("main_battery_voltage"),
    ),
    DroneMobileSensorDescription(
        key="backup_battery_voltage",
        name="Backup Battery Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: lks(d).get("backup_battery_voltage"),
    ),
    DroneMobileSensorDescription(
        key="temperature",
        name="Vehicle Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        imperial_unit=UnitOfTemperature.FAHRENHEIT,
        metric_unit=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d, c: _convert_temp(
            ctrl(d).get("current_temperature"), c.units == UNITS_IMPERIAL
        ),
    ),
    DroneMobileSensorDescription(
        key="cellular_signal",
        name="Cellular Signal",
        icon="mdi:signal",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: lks(d).get("cellular_signal_strength"),
    ),
    # --- Controller info ---
    DroneMobileSensorDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: lks(d).get("firmware_version"),
    ),
    DroneMobileSensorDescription(
        key="controller_model",
        name="Controller Model",
        icon="mdi:car-cog",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: lks(d).get("controller_model"),
    ),
    DroneMobileSensorDescription(
        key="carrier",
        name="Cellular Carrier",
        icon="mdi:sim",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: lks(d).get("carrier"),
    ),
    DroneMobileSensorDescription(
        key="last_known_state_timestamp",
        name="Last Update",
        icon="mdi:clock-check",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: dt_util.parse_datetime(lks(d).get("timestamp", "")),
    ),
    # --- Integration diagnostics ---
    DroneMobileSensorDescription(
        key="api_error_count",
        name="API Error Count",
        icon="mdi:alert-circle-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: c._api_error_count,
    ),
    DroneMobileSensorDescription(
        key="last_command",
        name="Last Command",
        icon="mdi:remote",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: c._last_command or "None",
    ),
    DroneMobileSensorDescription(
        key="last_command_result",
        name="Last Command Result",
        icon="mdi:check-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d, c: c._last_command_result or "None",
    ),
]


def _convert_temp(value: Any, to_fahrenheit: bool) -> float | None:
    if value is None or value == "null":
        return None
    try:
        c = float(value)
        return round(c * 9 / 5 + 32, 1) if to_fahrenheit else round(c, 1)
    except (TypeError, ValueError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DroneMobileSensor(coord, desc)
        for coord in coordinators.values()
        for desc in SENSOR_DESCRIPTIONS
    ])


class DroneMobileSensor(CoordinatorEntity[DroneMobileCoordinator], SensorEntity):
    _attr_has_entity_name = True
    entity_description: DroneMobileSensorDescription

    def __init__(self, coordinator: DroneMobileCoordinator, description: DroneMobileSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }
        if description.imperial_unit or description.metric_unit:
            if coordinator.units == UNITS_IMPERIAL and description.imperial_unit:
                self._attr_native_unit_of_measurement = description.imperial_unit
            elif description.metric_unit:
                self._attr_native_unit_of_measurement = description.metric_unit
            else:
                self._attr_native_unit_of_measurement = description.imperial_unit

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data or {}, self.coordinator)
