"""DataUpdateCoordinator for the DroneMobile V2 integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DroneMobileAPI, DroneMobileConnectionError, DroneMobileCommandError
from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    CONF_UPDATE_INTERVAL,
    CONF_UNITS,
    CONF_FORCE_COMMAND,
    DEFAULT_UNITS,
    DIAG_LAST_POLL_TIME,
    DIAG_LAST_POLL_SUCCESS,
    DIAG_API_ERROR_COUNT,
    DIAG_LAST_ERROR,
    DIAG_LAST_COMMAND,
    DIAG_LAST_CMD_RESULT,
    DIAG_LAST_CMD_TIME,
    CMD_REMOTE_START,
    CMD_REMOTE_STOP,
    CMD_LOCK,
    CMD_UNLOCK,
    CMD_TRUNK,
    CMD_PANIC_ON,
    CMD_AUX1,
    CMD_AUX2,
    DEFAULT_RUN_TIME,
    CLIMATE_PRESET_NONE,
    ctrl,
)

_LOGGER = logging.getLogger(__name__)

COMMAND_NAMES: dict[str, str] = {
    CMD_LOCK: "Lock / Arm",
    CMD_UNLOCK: "Unlock / Disarm",
    CMD_REMOTE_START: "Remote Start",
    CMD_REMOTE_STOP: "Remote Stop",
    CMD_TRUNK: "Trunk Release",
    CMD_PANIC_ON: "Panic",
    CMD_AUX1: "Aux 1",
    CMD_AUX2: "Aux 2",
}


class DroneMobileCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manage fetching DroneMobile data for one vehicle."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: DroneMobileAPI,
        entry: ConfigEntry,
        device_id: str,
        device_key: str,
        vehicle_name: str,
    ) -> None:
        self.api = api
        self.device_id = device_id
        self.device_key = device_key  # used for sending commands
        self.vehicle_name = vehicle_name
        self.entry = entry

        self.units: str = entry.options.get(
            CONF_UNITS, entry.data.get(CONF_UNITS, DEFAULT_UNITS)
        )
        self.force_command: bool = entry.options.get(
            CONF_FORCE_COMMAND, entry.data.get(CONF_FORCE_COMMAND, False)
        )
        update_minutes: int = entry.options.get(
            CONF_UPDATE_INTERVAL,
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )

        self.auto_poll_enabled: bool = True
        self._run_time: int = DEFAULT_RUN_TIME
        self._climate_preset: str = CLIMATE_PRESET_NONE

        # Diagnostics
        self._api_error_count: int = 0
        self._last_error: str = ""
        self._last_command: str = ""
        self._last_command_result: str = ""
        self._last_command_time: str = ""

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=timedelta(minutes=update_minutes),
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def run_time(self) -> int:
        return self._run_time

    @run_time.setter
    def run_time(self, value: int) -> None:
        self._run_time = value

    @property
    def climate_preset(self) -> str:
        return self._climate_preset

    @climate_preset.setter
    def climate_preset(self, value: str) -> None:
        self._climate_preset = value

    # ------------------------------------------------------------------
    # Fetch / update
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch fresh data from the DroneMobile API."""
        if not self.auto_poll_enabled:
            return self.data or {}

        now_str = datetime.now().isoformat()
        try:
            vehicle = await self.api.get_device_status(self.device_id)
            vehicle[DIAG_LAST_POLL_TIME] = now_str
            vehicle[DIAG_LAST_POLL_SUCCESS] = True
            self._last_error = ""
            return vehicle

        except DroneMobileConnectionError as err:
            self._api_error_count += 1
            self._last_error = str(err)
            _LOGGER.warning("DroneMobile update failed: %s", err)
            raise UpdateFailed(str(err)) from err
        except Exception as err:  # noqa: BLE001
            self._api_error_count += 1
            self._last_error = str(err)
            raise UpdateFailed(str(err)) from err

    async def async_force_refresh(self) -> None:
        """Force a data refresh regardless of auto-poll state."""
        prev = self.auto_poll_enabled
        self.auto_poll_enabled = True
        await self.async_refresh()
        self.auto_poll_enabled = prev

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def async_send_command(
        self, command: str, params: dict[str, Any] | None = None
    ) -> bool:
        """Send a command via device_key and schedule a refresh."""
        self._last_command = COMMAND_NAMES.get(command, command)
        self._last_command_time = datetime.now().isoformat()
        try:
            result = await self.api.send_command(self.device_key, command, params)
            status = result.get("status", result.get("result", "ok"))
            self._last_command_result = str(status)
            _LOGGER.info(
                "Command '%s' sent to %s: %s", command, self.vehicle_name, status
            )

            async def _delayed_refresh() -> None:
                await asyncio.sleep(3)
                await self.async_force_refresh()

            self.hass.async_create_task(_delayed_refresh())
            return True
        except (DroneMobileCommandError, DroneMobileConnectionError) as err:
            self._last_command_result = f"Error: {err}"
            self._api_error_count += 1
            self._last_error = str(err)
            _LOGGER.error("Command '%s' failed: %s", command, err)
            return False

    async def async_lock(self) -> bool:
        if not self.force_command:
            if ctrl(self.data or {}).get("armed") is True:
                _LOGGER.debug("Vehicle already armed; skipping")
                return True
        return await self.async_send_command(CMD_LOCK)

    async def async_unlock(self) -> bool:
        if not self.force_command:
            if ctrl(self.data or {}).get("armed") is False:
                _LOGGER.debug("Vehicle already disarmed; skipping")
                return True
        return await self.async_send_command(CMD_UNLOCK)

    async def async_remote_start(self) -> bool:
        params: dict[str, Any] = {"run_time": self._run_time}
        if self._climate_preset != CLIMATE_PRESET_NONE:
            params["climate_preset"] = self._climate_preset
        return await self.async_send_command(CMD_REMOTE_START, params)

    async def async_remote_stop(self) -> bool:
        return await self.async_send_command(CMD_REMOTE_STOP)

    async def async_trunk(self) -> bool:
        return await self.async_send_command(CMD_TRUNK)

    async def async_panic(self) -> bool:
        return await self.async_send_command(CMD_PANIC_ON)


    async def async_update_feature(self, key: str, value: bool) -> bool:
        """
        Toggle a controller feature via PATCH /api/v1/device/{device_key}/features.
        This is the endpoint used by the DroneMobile web/app UI.
        """
        try:
            await self.api.update_device_features(self.device_key, {key: value})
            _LOGGER.info(
                "Feature '%s' set to %s on %s", key, value, self.vehicle_name
            )
            await self.async_force_refresh()
            return True
        except DroneMobileConnectionError as err:
            self._api_error_count += 1
            self._last_error = str(err)
            _LOGGER.error("Failed to update feature '%s': %s", key, err)
            return False

    async def async_aux(self, aux_number: int) -> bool:
        cmds = {1: CMD_AUX1, 2: CMD_AUX2}
        cmd = cmds.get(aux_number)
        if cmd is None:
            _LOGGER.warning("Aux %d is not supported by DroneMobile API", aux_number)
            return False
        return await self.async_send_command(cmd)
