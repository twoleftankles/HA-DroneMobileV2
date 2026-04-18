"""Select platform for DroneMobile — climate preset mode."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    CLIMATE_PRESETS,
    CLIMATE_PRESET_NONE,
)
from .coordinator import DroneMobileCoordinator

# Human-friendly labels
PRESET_LABELS: dict[str, str] = {
    "none": "No Preset",
    "heat": "Heat",
    "cool": "Cool",
    "defrost": "Defrost",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [DroneMobileClimatePresetSelect(coord) for coord in coordinators.values()]
    )


class DroneMobileClimatePresetSelect(
    CoordinatorEntity[DroneMobileCoordinator], SelectEntity
):
    """
    Select entity to choose a climate preset for the next remote start.
    The selected preset is sent as a parameter with the next remote_start command.
    """

    _attr_has_entity_name = True
    _attr_name = "Climate Preset"
    _attr_icon = "mdi:thermometer-auto"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(PRESET_LABELS.values())

    def __init__(self, coordinator: DroneMobileCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_climate_preset"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def current_option(self) -> str:
        return PRESET_LABELS.get(self.coordinator.climate_preset, "No Preset")

    async def async_select_option(self, option: str) -> None:
        # Reverse-map label → key
        key = next(
            (k for k, v in PRESET_LABELS.items() if v == option),
            CLIMATE_PRESET_NONE,
        )
        self.coordinator.climate_preset = key
        self.async_write_ha_state()
