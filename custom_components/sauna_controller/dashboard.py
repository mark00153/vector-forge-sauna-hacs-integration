"""Lovelace dashboard for Sauna Controller."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "sauna"
DASHBOARD_TITLE = "Sauna"
DASHBOARD_ICON = "mdi:sauna"
STORAGE_KEY = f"lovelace.{DASHBOARD_URL_PATH}"

_REGISTERED_KEY = f"{DOMAIN}_dashboard_registered"

_SLUG = "sauna_controller"

_DASHBOARD_CONFIG: dict[str, Any] = {
    "title": "Sauna",
    "views": [
        {
            "title": "Sauna",
            "icon": "mdi:sauna",
            "cards": [
                {
                    "type": "thermostat",
                    "entity": f"climate.{_SLUG}",
                    "name": "Sauna",
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {
                            "type": "entity",
                            "entity": f"sensor.{_SLUG}_state",
                            "name": "State",
                            "icon": "mdi:state-machine",
                        },
                        {
                            "type": "entity",
                            "entity": f"binary_sensor.{_SLUG}_door",
                            "name": "Door",
                        },
                        {
                            "type": "entity",
                            "entity": f"binary_sensor.{_SLUG}_heater",
                            "name": "Heater",
                        },
                    ],
                },
                {
                    "type": "history-graph",
                    "title": "Temperature History",
                    "entities": [{"entity": f"sensor.{_SLUG}_temperature"}],
                    "hours_to_show": 2,
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {
                            "type": "entity",
                            "entity": f"binary_sensor.{_SLUG}_fault",
                            "name": "Fault",
                            "state_color": True,
                        },
                        {
                            "type": "button",
                            "entity": f"button.{_SLUG}_reset_fault",
                            "name": "Reset Fault",
                            "icon": "mdi:alert-circle-check",
                            "show_state": False,
                        },
                    ],
                },
            ],
        }
    ],
}


async def _write_storage_file(hass: HomeAssistant) -> None:
    """Write the dashboard config to HA's .storage directory.

    Skips if the file already exists so user edits are preserved.
    """
    storage_path = hass.config.path(".storage", STORAGE_KEY)

    if os.path.exists(storage_path):
        _LOGGER.debug("Sauna dashboard storage file already exists, skipping write")
        return

    storage_data = {
        "version": 1,
        "minor_version": 1,
        "key": STORAGE_KEY,
        "data": {"config": _DASHBOARD_CONFIG},
    }

    def _write() -> None:
        with open(storage_path, "w", encoding="utf-8") as f:
            json.dump(storage_data, f, indent=2)

    await hass.async_add_executor_job(_write)
    _LOGGER.debug("Sauna dashboard storage file written to %s", storage_path)


async def async_setup_dashboard(hass: HomeAssistant) -> None:
    """Register the sauna Lovelace dashboard and sidebar entry."""
    if hass.data.get(_REGISTERED_KEY):
        return

    await _write_storage_file(hass)

    async_register_built_in_panel(
        hass,
        component_name="lovelace",
        sidebar_title=DASHBOARD_TITLE,
        sidebar_icon=DASHBOARD_ICON,
        frontend_url_path=DASHBOARD_URL_PATH,
        config={"mode": "storage"},
        require_admin=False,
        update=False,
    )

    hass.data[_REGISTERED_KEY] = True
    _LOGGER.debug("Sauna dashboard registered at /%s", DASHBOARD_URL_PATH)


async def async_unload_dashboard(hass: HomeAssistant) -> None:
    """Remove the sauna sidebar panel when the last config entry is unloaded.

    The storage file is intentionally left in place so user edits survive
    reinstalls.
    """
    if not hass.data.get(_REGISTERED_KEY):
        return

    if hass.data.get(DOMAIN):
        return

    async_remove_panel(hass, DASHBOARD_URL_PATH)
    hass.data.pop(_REGISTERED_KEY, None)
    _LOGGER.debug("Sauna dashboard panel removed")
