"""Device tracker platform for DroneMobile V2."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, UNITS_IMPERIAL, lks, ctrl
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    # Always register the tracker — lat/lon may not be available on first setup
    # but the coordinator will provide them once data arrives.
    async_add_entities([DroneMobileTracker(coord) for coord in coordinators.values()])


class DroneMobileTracker(CoordinatorEntity[DroneMobileCoordinator], TrackerEntity):
    """GPS device tracker for a DroneMobile vehicle."""

    _attr_has_entity_name = True
    _attr_name = "Location"
    _attr_icon = "mdi:car-connected"
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator: DroneMobileCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_tracker"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def latitude(self) -> float | None:
        try:
            return float(lks(self.coordinator.data or {})["latitude"])
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def longitude(self) -> float | None:
        try:
            return float(lks(self.coordinator.data or {})["longitude"])
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def location_accuracy(self) -> int:
        return 20

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        state = lks(data)
        c = ctrl(data)
        is_imperial = self.coordinator.units == UNITS_IMPERIAL
        attrs: dict[str, Any] = {
            "vehicle_name": self.coordinator.vehicle_name,
            "device_id": self.coordinator.device_id,
            "gps_direction": state.get("gps_direction"),
            "odometer": state.get("mileage"),
            "odometer_unit": "mi" if is_imperial else "km",
            "ignition_on": c.get("ignition_on"),
            "engine_on": c.get("engine_on"),
            "armed": c.get("armed"),
            "door_open": c.get("door_open"),
            "trunk_open": c.get("trunk_open"),
            "hood_open": c.get("hood_open"),
            "battery_voltage": c.get("main_battery_voltage"),
            "temperature": c.get("current_temperature"),
            "last_known_state_timestamp": state.get("timestamp"),
        }
        return {k: v for k, v in attrs.items() if v is not None}
