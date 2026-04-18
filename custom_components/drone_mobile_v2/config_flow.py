"""Config flow for DroneMobile."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DroneMobileAPI, DroneMobileAuthError, DroneMobileConnectionError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_UNITS,
    CONF_UPDATE_INTERVAL,
    CONF_FORCE_COMMAND,
    DEFAULT_UNITS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_FORCE_COMMAND,
    UNITS_IMPERIAL,
    UNITS_METRIC,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_UNITS, default=DEFAULT_UNITS): vol.In(
            [UNITS_IMPERIAL, UNITS_METRIC]
        ),
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=60)
        ),
        vol.Optional(CONF_FORCE_COMMAND, default=DEFAULT_FORCE_COMMAND): bool,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_UNITS, default=DEFAULT_UNITS): vol.In(
            [UNITS_IMPERIAL, UNITS_METRIC]
        ),
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=60)
        ),
        vol.Optional(CONF_FORCE_COMMAND, default=DEFAULT_FORCE_COMMAND): bool,
    }
)


class DroneMobileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = DroneMobileAPI(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                session=session,
            )
            try:
                await api.authenticate()
                devices = await api.get_devices()
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"DroneMobileV2 ({user_input[CONF_USERNAME]})",
                        data=user_input,
                    )
            except DroneMobileAuthError:
                errors["base"] = "invalid_auth"
            except DroneMobileConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during DroneMobile setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DroneMobileOptionsFlow:
        return DroneMobileOptionsFlow(config_entry)


class DroneMobileOptionsFlow(config_entries.OptionsFlow):
    """Handle options (reconfigure units, interval, etc.)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options or self.config_entry.data
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UNITS, default=current.get(CONF_UNITS, DEFAULT_UNITS)
                ): vol.In([UNITS_IMPERIAL, UNITS_METRIC]),
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=current.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Optional(
                    CONF_FORCE_COMMAND,
                    default=current.get(CONF_FORCE_COMMAND, DEFAULT_FORCE_COMMAND),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
