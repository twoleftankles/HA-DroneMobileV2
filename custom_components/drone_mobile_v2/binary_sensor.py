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
        key="engine_running",
        name="Engine Running",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:engine",
        is_on_fn=lambda d: ctrl(d).get("engine_on"),
    ),
    DroneMobileBinarySensorDescription(
        key="ignition",
        name="Ignition",
        icon="mdi:key-variant",
        is_on_fn=lambda d: ctrl(d).get("ignition_on"),
    ),
    DroneMobileBinarySensorDescription(
        key="armed",
        name="Armed",
        device_class=BinarySensorDeviceClass.LOCK,
        icon="mdi:shield-car",
        # LOCK device class: on = unlocked, off = locked — invert armed
        is_on_fn=lambda d: not ctrl(d).get("armed", True),
    ),
    DroneMobileBinarySensorDescription(
        key="door_open",
        name="Door Open",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda d: ctrl(d).get("door_open"),
    ),
    DroneMobileBinarySensorDescription(
        key="trunk_open",
        name="Trunk Open",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:car-back",
        is_on_fn=lambda d: ctrl(d).get("trunk_open"),
    ),
    DroneMobileBinarySensorDescription(
        key="hood_open",
        name="Hood Open",
        device_class=BinarySensorDeviceClass.OPENING,
        icon="mdi:car",
        is_on_fn=lambda d: ctrl(d).get("hood_open"),
    ),
    # --- Alerts ---
    DroneMobileBinarySensorDescription(
        key="panic_status",
        name="Panic Active",
        device_class=BinarySensorDeviceClass.SAFETY,
        icon="mdi:alarm-light",
        is_on_fn=lambda d: d.get("panic_status"),
    ),
    DroneMobileBinarySensorDescription(
        key="remote_start_status",
        name="Remote Started",
        icon="mdi:car-key",
        is_on_fn=lambda d: d.get("remote_start_status"),
    ),
    DroneMobileBinarySensorDescription(
        key="towing_detected",
        name="Towing Detected",
        device_class=BinarySensorDeviceClass.MOTION,
        icon="mdi:tow-truck",
        is_on_fn=lambda d: d.get("towing_detected"),
    ),
    DroneMobileBinarySensorDescription(
        key="service_due",
        name="Service Due",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:wrench-clock",
        is_on_fn=lambda d: d.get("service_due"),
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
        name="Backup Battery OK",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        icon="mdi:battery-charging",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda d: (d.get("last_known_state") or {}).get("i_o_status", {}).get("backup_battery_status"),
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
