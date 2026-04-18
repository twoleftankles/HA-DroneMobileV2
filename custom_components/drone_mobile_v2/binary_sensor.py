"""Binary sensor platform for DroneMobile V2."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, ctrl
from .coordinator import DroneMobileCoordinator


@dataclass(frozen=True)
class DroneMobileBinarySensorDescription(BinarySensorEntityDescription):
    is_on_fn: Callable[[dict[str, Any]], bool | None] = lambda d: None


BINARY_SENSOR_DESCRIPTIONS: list[DroneMobileBinarySensorDescription] = [
    # --- Vehicle state ---
    DroneMobileBinarySensorDescription(
        key="ignition",
        name="Ignition",
        icon="mdi:key-variant",
        is_on_fn=lambda d: ctrl(d).get("ignition_on"),
    ),
    DroneMobileBinarySensorDescription(
        key="door_open",
        name="Door Status",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda d: ctrl(d).get("door_open"),
    ),
    DroneMobileBinarySensorDescription(
        key="trunk_open",
        name="Trunk Status",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:car-back",
        is_on_fn=lambda d: ctrl(d).get("trunk_open"),
    ),
    DroneMobileBinarySensorDescription(
        key="hood_open",
        name="Hood Status",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:car",
        is_on_fn=lambda d: ctrl(d).get("hood_open"),
    ),
    # --- Alerts ---
    DroneMobileBinarySensorDescription(
        key="panic_status",
        name="Panic Status",
        icon="mdi:alarm-light",
        is_on_fn=lambda d: d.get("panic_status"),
    ),
    DroneMobileBinarySensorDescription(
        key="towing_detected",
        name="Towing Detected",
        device_class=BinarySensorDeviceClass.MOTION,
        icon="mdi:tow-truck",
        is_on_fn=lambda d: d.get("towing_detected"),
    ),
    DroneMobileBinarySensorDescription(
        key="low_battery",
        name="Low Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        is_on_fn=lambda d: d.get("low_battery"),
    ),
    DroneMobileBinarySensorDescription(
        key="battery_off",
        name="Battery Disconnected",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:battery-off",
        is_on_fn=lambda d: d.get("battery_off"),
    ),
    DroneMobileBinarySensorDescription(
        key="backup_battery_ok",
        name="Backup Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        icon="mdi:battery-heart",
        entity_category=EntityCategory.DIAGNOSTIC,
        # BATTERY device class: on = low, off = normal — invert so True (ok) shows as "Normal"
        is_on_fn=lambda d: not (d.get("last_known_state") or {}).get("i_o_status", {}).get("backup_battery_status", True),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, DroneMobileCoordinator] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DroneMobileBinarySensor(coord, desc)
        for coord in coordinators.values()
        for desc in BINARY_SENSOR_DESCRIPTIONS
    ])


class DroneMobileBinarySensor(CoordinatorEntity[DroneMobileCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    entity_description: DroneMobileBinarySensorDescription

    def __init__(self, coordinator: DroneMobileCoordinator, description: DroneMobileBinarySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": coordinator.vehicle_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.is_on_fn(self.coordinator.data or {})
