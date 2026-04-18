"""Number platform for DroneMobile — remote start run-time duration."""
from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MIN_RUN_TIME, MAX_RUN_TIME, DEFAULT_RUN_TIME
from .coordinator import DroneMobileCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [DroneMobileRunTimeNumber(coord) for coord in coordinators.values()]
    )


class DroneMobileRunTimeNumber(
    CoordinatorEntity[DroneMobileCoordinator], NumberEntity
):
    """Slider to configure the remote-start run-time in minutes."""

    _attr_has_entity_name = True
    _attr_name = "Remote Start Duration"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = float(MIN_RUN_TIME)
    _attr_native_max_value = float(MAX_RUN_TIME)
    _attr_native_step = 5.0
    _attr_mode = NumberMode.SLIDER
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: DroneMobileCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_run_time"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def native_value(self) -> float:
        return float(self.coordinator.run_time)

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.run_time = int(value)
        self.async_write_ha_state()
