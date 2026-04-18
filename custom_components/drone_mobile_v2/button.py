"""Button platform for DroneMobile V2."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Awaitable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DroneMobileButtonDescription(ButtonEntityDescription):
    """Extended description with press handler."""
    press_fn: Callable[[DroneMobileCoordinator], Awaitable[bool]] = None  # type: ignore[assignment]


BUTTON_DESCRIPTIONS: list[DroneMobileButtonDescription] = [
    DroneMobileButtonDescription(
        key="lock",
        name="Lock",
        icon="mdi:lock",
        press_fn=lambda c: c.async_lock(),
    ),
    DroneMobileButtonDescription(
        key="unlock",
        name="Unlock",
        icon="mdi:lock-open-variant",
        press_fn=lambda c: c.async_unlock(),
    ),
    DroneMobileButtonDescription(
        key="remote_start",
        name="Remote Start",
        icon="mdi:car-key",
        press_fn=lambda c: c.async_remote_start(),
    ),
    DroneMobileButtonDescription(
        key="remote_stop",
        name="Remote Stop",
        icon="mdi:car-off",
        press_fn=lambda c: c.async_remote_stop(),
    ),
    DroneMobileButtonDescription(
        key="trunk_release",
        name="Trunk Release",
        icon="mdi:car-back",
        press_fn=lambda c: c.async_trunk(),
    ),
    DroneMobileButtonDescription(
        key="panic",
        name="Panic",
        icon="mdi:alarm-light",
        press_fn=lambda c: c.async_panic(),
    ),
    DroneMobileButtonDescription(
        key="aux1",
        name="Aux 1",
        icon="mdi:gesture-tap-button",
        press_fn=lambda c: c.async_aux(1),
    ),
    DroneMobileButtonDescription(
        key="aux2",
        name="Aux 2",
        icon="mdi:gesture-tap-button",
        press_fn=lambda c: c.async_aux(2),
    ),
    DroneMobileButtonDescription(
        key="force_refresh",
        name="Force Refresh",
        icon="mdi:refresh",
        press_fn=lambda c: c.async_force_refresh(),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DroneMobileButton(coord, desc)
        for coord in coordinators.values()
        for desc in BUTTON_DESCRIPTIONS
    ]
    async_add_entities(entities)


class DroneMobileButton(CoordinatorEntity[DroneMobileCoordinator], ButtonEntity):
    """A button entity for a DroneMobile command."""

    entity_description: DroneMobileButtonDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DroneMobileCoordinator,
        description: DroneMobileButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator)
