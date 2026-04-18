"""Lock platform for DroneMobile V2."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, ctrl
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    entities = [DroneMobileDoorLock(coord) for coord in coordinators.values()]
    async_add_entities(entities)


class DroneMobileDoorLock(CoordinatorEntity[DroneMobileCoordinator], LockEntity):
    """Controls the vehicle alarm arm/disarm via the lock entity."""

    _attr_has_entity_name = True
    _attr_name = "Door Lock"
    _attr_icon = "mdi:car-door-lock"

    def __init__(self, coordinator: DroneMobileCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_door_lock"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def is_locked(self) -> bool | None:
        data = self.coordinator.data or {}
        armed = ctrl(data).get("armed")
        if armed is None:
            return None
        return bool(armed)

    @property
    def is_locking(self) -> bool:
        return False

    @property
    def is_unlocking(self) -> bool:
        return False

    async def async_lock(self, **kwargs: Any) -> None:
        await self.coordinator.async_lock()
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.coordinator.async_unlock()
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        c = ctrl(data)
        return {
            "armed": c.get("armed"),
            "ignition_on": c.get("ignition_on"),
            "engine_on": c.get("engine_on"),
        }
