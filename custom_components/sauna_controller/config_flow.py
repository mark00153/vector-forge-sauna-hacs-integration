"""Config flow for Sauna Controller integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_STATE, DEFAULT_PORT, DOMAIN, MODEL

_LOGGER = logging.getLogger(__name__)


async def _validate_host(hass, host: str, port: int) -> dict:
    """Try connecting to the device and return its state."""
    session = async_get_clientsession(hass)
    async with session.get(
        f"http://{host}:{port}{API_STATE}",
        timeout=aiohttp.ClientTimeout(total=5),
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


class SaunaControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sauna Controller."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._port: int = DEFAULT_PORT
        self._name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual user configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            try:
                await _validate_host(self.hass, host, port)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"sauna_{host.replace('.', '_')}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, MODEL),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_NAME: user_input.get(CONF_NAME, MODEL),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_NAME, default=MODEL): str,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle discovery via mDNS/Zeroconf."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        name = discovery_info.name.replace("._http._tcp.local.", "")

        # Validate it's actually a sauna controller
        try:
            await _validate_host(self.hass, host, port)
        except Exception:
            return self.async_abort(reason="cannot_connect")

        await self.async_set_unique_id(f"sauna_{host.replace('.', '_')}")
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._host = host
        self._port = port
        self._name = name

        self.context["title_placeholders"] = {"name": name, "host": host}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovered device."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._name or MODEL,
                data={
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    CONF_NAME: self._name,
                },
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "name": self._name,
                "host": self._host,
            },
        )
