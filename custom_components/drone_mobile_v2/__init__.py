"""DroneMobile V2 Home Assistant Integration."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DroneMobileAPI, DroneMobileAuthError, DroneMobileConnectionError
from .const import (
    DOMAIN,
    MANUFACTURER,
    PLATFORMS,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from .coordinator import DroneMobileCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DroneMobile V2 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = DroneMobileAPI(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )

    try:
        await api.authenticate()
        devices = await api.get_devices()
    except DroneMobileAuthError as err:
        _LOGGER.error("DroneMobile authentication failed: %s", err)
        return False
    except DroneMobileConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to DroneMobile: {err}") from err

    if not devices:
        _LOGGER.error("No DroneMobile vehicles found on this account")
        return False

    coordinators: dict[str, DroneMobileCoordinator] = {}

    for device in devices:
        device_id = str(device.get("id", ""))
        device_key = str(device.get("device_key", ""))
        vehicle_name = device.get("vehicle_name") or f"Vehicle {device_id}"

        coordinator = DroneMobileCoordinator(
            hass=hass,
            api=api,
            entry=entry,
            device_id=device_id,
            device_key=device_key,
            vehicle_name=vehicle_name,
        )

        try:
            await coordinator.async_config_entry_first_refresh()
        except ConfigEntryNotReady:
            _LOGGER.warning(
                "Could not fetch initial data for %s; will retry", vehicle_name
            )

        coordinators[device_id] = coordinator

        last_known = (coordinator.data or {}).get("last_known_state") or {}
        model = last_known.get("controller", {}).get("controller_model", "DroneMobile")
        dev_reg = dr.async_get(hass)
        dev_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            name=vehicle_name,
            model=model,
        )

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # ---- Services ----
    async def handle_refresh(call: ServiceCall) -> None:
        for coord in coordinators.values():
            await coord.async_force_refresh()

    async def handle_refresh_vehicle(call: ServiceCall) -> None:
        vehicle = call.data.get("vehicle_name", "").lower()
        for coord in coordinators.values():
            if coord.vehicle_name.lower().replace(" ", "_") == vehicle.replace(" ", "_"):
                await coord.async_force_refresh()
                return
        _LOGGER.warning("Vehicle '%s' not found for refresh", vehicle)

    async def handle_dump_data(call: ServiceCall) -> None:
        for coord in coordinators.values():
            name = coord.vehicle_name.replace(" ", "_")
            path = hass.config.path(f"drone_mobile_v2_{name}_dump.json")
            with open(path, "w") as f:
                json.dump(coord.data, f, indent=2, default=str)
            _LOGGER.info("Dumped data for %s → %s", coord.vehicle_name, path)

    async def handle_clear_tokens(call: ServiceCall) -> None:
        api.clear_tokens()
        _LOGGER.info("DroneMobile tokens cleared")

    hass.services.async_register(DOMAIN, "refresh_all", handle_refresh)
    hass.services.async_register(DOMAIN, "refresh_vehicle", handle_refresh_vehicle)
    hass.services.async_register(DOMAIN, "dump_device_data", handle_dump_data)
    hass.services.async_register(DOMAIN, "clear_tokens", handle_clear_tokens)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
