"""DroneMobile API client — AWS Cognito auth + DroneMobile REST API."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from .const import (
    AWS_COGNITO_URL,
    AWS_CLIENT_ID,
    API_BASE_URL,
    API_VEHICLES_PATH,
    API_COMMAND_PATH,
    API_TIMEOUT,
    DEVICE_TYPE_VEHICLE,
)

_LOGGER = logging.getLogger(__name__)


class DroneMobileAuthError(Exception):
    """Raised when authentication fails."""


class DroneMobileConnectionError(Exception):
    """Raised when connection to the API fails."""


class DroneMobileCommandError(Exception):
    """Raised when a command fails."""


class DroneMobileAPI:
    """Async client for the DroneMobile API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._username = username
        self._password = password
        self._session = session
        self._id_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expiry: datetime | None = None

    # ------------------------------------------------------------------
    # Authentication (AWS Cognito)
    # ------------------------------------------------------------------

    async def authenticate(self) -> None:
        """Obtain tokens via AWS Cognito USER_PASSWORD_AUTH flow."""
        payload = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": AWS_CLIENT_ID,
            "AuthParameters": {
                "USERNAME": self._username,
                "PASSWORD": self._password,
            },
            "ClientMetadata": {},
        }
        await self._cognito_auth(payload)

    async def _do_token_refresh(self) -> None:
        """Refresh tokens via AWS Cognito REFRESH_TOKEN_AUTH flow."""
        payload = {
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "ClientId": AWS_CLIENT_ID,
            "AuthParameters": {
                "REFRESH_TOKEN": self._refresh_token,
            },
        }
        await self._cognito_auth(payload)

    async def _cognito_auth(self, payload: dict[str, Any]) -> None:
        """POST to the Cognito endpoint and store resulting tokens."""
        headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
            "X-Amz-User-Agent": "aws-amplify/5.0.4 js",
            "Referer": "https://accounts.dronemobile.com/",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
        }
        try:
            async with self._session.post(
                AWS_COGNITO_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                body = await resp.text()
                _LOGGER.debug(
                    "Cognito auth response: HTTP %s — %s", resp.status, body[:500]
                )
                if resp.status in (400, 401, 403):
                    raise DroneMobileAuthError(
                        f"Authentication failed (HTTP {resp.status}): {body}"
                    )
                if not resp.ok:
                    raise DroneMobileConnectionError(
                        f"Unexpected Cognito response (HTTP {resp.status}): {body}"
                    )
                import json as _json
                data = _json.loads(body)
        except (DroneMobileAuthError, DroneMobileConnectionError):
            raise
        except aiohttp.ClientError as err:
            raise DroneMobileConnectionError(
                f"Connection error during authentication: {err}"
            ) from err

        result = data.get("AuthenticationResult", {})
        self._id_token = result.get("IdToken")
        self._refresh_token = result.get("RefreshToken", self._refresh_token)
        expires_in = result.get("ExpiresIn", 3600)
        self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)
        _LOGGER.debug(
            "DroneMobile authenticated via Cognito, token expires in %ds", expires_in
        )

    async def _maybe_refresh(self) -> None:
        """Re-authenticate if the token is expired or missing."""
        if self._id_token is None:
            await self.authenticate()
            return
        if self._token_expiry and datetime.utcnow() >= self._token_expiry:
            _LOGGER.debug("DroneMobile token expired, refreshing…")
            if self._refresh_token:
                try:
                    await self._do_token_refresh()
                    return
                except Exception:  # noqa: BLE001
                    _LOGGER.warning(
                        "Token refresh failed, falling back to full re-auth"
                    )
            await self.authenticate()

    def _api_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._id_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Vehicles
    # ------------------------------------------------------------------

    async def get_devices(self) -> list[dict[str, Any]]:
        """Return all vehicles registered to the account."""
        await self._maybe_refresh()
        url = API_BASE_URL + API_VEHICLES_PATH + "?limit=100"
        try:
            async with self._session.get(
                url,
                headers=self._api_headers(),
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == 401:
                    await self.authenticate()
                    return await self.get_devices()
                resp.raise_for_status()
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise DroneMobileConnectionError(f"Error fetching vehicles: {err}") from err

        if isinstance(data, list):
            return data
        return data.get("results", [])

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Fetch the latest status for a vehicle by re-querying the vehicle list."""
        vehicles = await self.get_devices()
        for vehicle in vehicles:
            if str(vehicle.get("id", "")) == str(device_id):
                return vehicle
        raise DroneMobileConnectionError(
            f"Vehicle {device_id} not found in API response"
        )

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def send_command(
        self,
        device_key: str,
        command: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a remote command to the vehicle using its device_key."""
        await self._maybe_refresh()
        url = API_BASE_URL + API_COMMAND_PATH
        payload: dict[str, Any] = {
            "device_key": device_key,
            "command": command,
            "device_type": DEVICE_TYPE_VEHICLE,
        }
        if params:
            payload.update(params)

        _LOGGER.debug("Sending command '%s' to device_key %s", command, device_key)
        try:
            async with self._session.post(
                url,
                json=payload,
                headers=self._api_headers(),
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == 401:
                    await self.authenticate()
                    return await self.send_command(device_key, command, params)
                if resp.status not in (200, 201, 202):
                    body = await resp.text()
                    raise DroneMobileCommandError(
                        f"Command '{command}' failed (HTTP {resp.status}): {body}"
                    )
                return await resp.json()
        except aiohttp.ClientError as err:
            raise DroneMobileConnectionError(
                f"Connection error during command '{command}': {err}"
            ) from err

    async def update_device_features(
        self, device_key: str, features: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update controller features via PATCH /api/v1/device/{device_key}/features.

        This is the correct endpoint used by the DroneMobile web/app UI.
        The payload is a flat dict of setting keys and their new bool values.
        The API accepts partial updates (only the keys you want to change).
        """
        await self._maybe_refresh()
        url = f"{API_BASE_URL}/v1/device/{device_key}/features"
        _LOGGER.debug("Updating features for device %s: %s", device_key, features)
        try:
            async with self._session.patch(
                url,
                json=features,
                headers=self._api_headers(),
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == 401:
                    await self.authenticate()
                    return await self.update_device_features(device_key, features)
                body = await resp.text()
                _LOGGER.debug(
                    "Feature update response: HTTP %s — %s", resp.status, body[:300]
                )
                if not resp.ok:
                    raise DroneMobileConnectionError(
                        f"Failed to update features (HTTP {resp.status}): {body}"
                    )
                import json as _json
                return _json.loads(body) if body else {}
        except (DroneMobileConnectionError, DroneMobileAuthError):
            raise
        except aiohttp.ClientError as err:
            raise DroneMobileConnectionError(
                f"Connection error updating features: {err}"
            ) from err

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clear_tokens(self) -> None:
        """Clear stored tokens, forcing re-auth on next call."""
        self._id_token = None
        self._refresh_token = None
        self._token_expiry = None
