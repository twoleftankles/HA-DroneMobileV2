"""Switch platform for DroneMobile V2 — controller features + auto-poll."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, ctrl
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DroneMobileFeatureSwitchDescription(SwitchEntityDescription):
    """A switch backed by a feature key from PATCH /v1/device/{key}/features."""
    feature_key: str = ""


# These keys are sent as a flat dict to /api/v1/device/{device_key}/features
# and map directly to last_known_state.controller.* in the API response.
# Confirmed from DroneMobile web app network traffic.
FEATURE_SWITCH_DESCRIPTIONS: list[DroneMobileFeatureSwitchDescription] = [
    DroneMobileFeatureSwitchDescription(
        key="valet_mode",
        name="Valet Mode",
        icon="mdi:car-key",
        entity_category=EntityCategory.CONFIG,
        feature_key="valet_mode_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="siren",
        name="Siren",
        icon="mdi:bullhorn",
        entity_category=EntityCategory.CONFIG,
        feature_key="siren_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="shock_sensor",
        name="Shock Sensor",
        icon="mdi:vibrate",
        entity_category=EntityCategory.CONFIG,
        feature_key="shock_sensor_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="passive_arming",
        name="Passive Arming",
        icon="mdi:lock-clock",
        entity_category=EntityCategory.CONFIG,
        feature_key="passive_arming_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="drive_lock",
        name="Drive Lock",
        icon="mdi:lock-open-variant",
        entity_category=EntityCategory.CONFIG,
        feature_key="drive_lock_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="auto_door_lock",
        name="Auto Door Lock",
        icon="mdi:car-door-lock",
        entity_category=EntityCategory.CONFIG,
        feature_key="auto_door_lock_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="timer_start",
        name="Timer Start",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.CONFIG,
        feature_key="timer_start_enabled",
    ),
    DroneMobileFeatureSwitchDescription(
        key="turbo_timer_start",
        name="Turbo Timer Start",
        icon="mdi:timer-cog-outline",
        entity_category=EntityCategory.CONFIG,
        feature_key="turbo_timer_start_enabled",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = []
    for coord in coordinators.values():
        for desc in FEATURE_SWITCH_DESCRIPTIONS:
            entities.append(DroneMobileFeatureSwitch(coord, desc))
        entities.append(DroneMobileAutoPollSwitch(coord))
    async_add_entities(entities)


class DroneMobileFeatureSwitch(CoordinatorEntity[DroneMobileCoordinator], SwitchEntity):
    """
    Switch that reads a controller feature from last_known_state.controller
    and writes it via PATCH /api/v1/device/{device_key}/features.

    This endpoint is confirmed from DroneMobile web app network traffic.
    """

    entity_description: DroneMobileFeatureSwitchDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DroneMobileCoordinator,
        description: DroneMobileFeatureSwitchDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.entity_description.feature_key in ctrl(self.coordinator.data or {})
        )

    @property
    def is_on(self) -> bool | None:
        val = ctrl(self.coordinator.data or {}).get(self.entity_description.feature_key)
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_update_feature(
            self.entity_description.feature_key, True
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_update_feature(
            self.entity_description.feature_key, False
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"feature_key": self.entity_description.feature_key}


class DroneMobileAutoPollSwitch(CoordinatorEntity[DroneMobileCoordinator], SwitchEntity):
    """Toggle automatic polling on/off to conserve vehicle battery."""

    _attr_has_entity_name = True
    _attr_name = "Auto Poll"
    _attr_icon = "mdi:sync"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: DroneMobileCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_auto_poll"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def is_on(self) -> bool:
        return self.coordinator.auto_poll_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.coordinator.auto_poll_enabled = True
        self.async_write_ha_state()
        await self.coordinator.async_force_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.coordinator.auto_poll_enabled = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "update_interval_minutes": (
                self.coordinator.update_interval.seconds // 60
                if self.coordinator.update_interval else None
            )
        }
