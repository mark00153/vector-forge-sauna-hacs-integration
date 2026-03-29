"""Data coordinator for Sauna Controller."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_RESET_FAULT,
    API_SETPOINT,
    API_STATE,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    WS_PATH,
)

_LOGGER = logging.getLogger(__name__)


class SaunaCoordinator(DataUpdateCoordinator):
    """Coordinator for polling and pushing state to/from the sauna controller."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host: str = entry.data[CONF_HOST]
        self.port: int = entry.data.get(CONF_PORT, 80)
        self._session = async_get_clientsession(hass)
        self._base_url = f"http://{self.host}:{self.port}"
        self._ws_task: asyncio.Task | None = None

    @property
    def base_url(self) -> str:
        return self._base_url

    async def _async_update_data(self) -> dict:
        """Fetch state from the device."""
        try:
            async with self._session.get(
                f"{self._base_url}{API_STATE}", timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with sauna controller: {err}") from err

    async def async_set_setpoint(self, value: float) -> None:
        """Send setpoint command."""
        try:
            async with self._session.post(
                f"{self._base_url}{API_SETPOINT}",
                json={"value": value},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to set setpoint: %s", err)

    async def async_set_master(self, on: bool) -> None:
        """Send master switch command via WebSocket."""
        cmd = "master_on" if on else "master_off"
        await self._send_ws_command({"cmd": cmd})

    async def async_reset_fault(self) -> None:
        """Send reset fault command."""
        try:
            async with self._session.post(
                f"{self._base_url}{API_RESET_FAULT}",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
                await self.async_request_refresh()
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to reset fault: %s", err)

    async def _send_ws_command(self, payload: dict) -> None:
        """Send a command via WebSocket."""
        import json
        ws_url = f"ws://{self.host}:{self.port}{WS_PATH}"
        try:
            async with self._session.ws_connect(
                ws_url, timeout=aiohttp.ClientTimeout(total=5)
            ) as ws:
                await ws.send_str(json.dumps(payload))
                await asyncio.sleep(0.1)
        except aiohttp.ClientError as err:
            _LOGGER.error("WebSocket command failed: %s", err)
        finally:
            await self.async_request_refresh()
