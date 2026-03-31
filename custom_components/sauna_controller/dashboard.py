"""Lovelace dashboard for Sauna Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "sauna"
DASHBOARD_TITLE = "Sauna"
DASHBOARD_ICON = "mdi:sauna"

_REGISTERED_KEY = f"{DOMAIN}_dashboard_registered"

_SLUG = "sauna_controller"

_CONFIG: dict[str, Any] = {
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


class _SaunaDashboard:
    """Duck-typed Lovelace dashboard — no internal HA base class needed."""

    is_strategy = False

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.url_path = DASHBOARD_URL_PATH

    @property
    def config(self) -> dict[str, Any]:
        return _CONFIG

    @property
    def mode(self) -> str:
        return "storage"

    async def async_get_info(self) -> dict[str, Any]:
        return {"mode": "generated", "views": len(_CONFIG.get("views", []))}

    async def async_load(self, force: bool = False) -> dict[str, Any]:
        return _CONFIG

    async def async_save(self, config: dict[str, Any]) -> None:
        raise HomeAssistantError(
            "The Sauna Controller dashboard is auto-generated and cannot be edited"
        )


async def async_setup_dashboard(hass: HomeAssistant) -> None:
    """Register the sauna Lovelace dashboard and sidebar entry."""
    if hass.data.get(_REGISTERED_KEY):
        return

    lovelace_data: dict = hass.data.get("lovelace", {})
    dashboards: dict | None = lovelace_data.get("dashboards")

    if dashboards is None:
        _LOGGER.warning(
            "Lovelace dashboards registry not found; sauna dashboard will not be added"
        )
        return

    dashboards[DASHBOARD_URL_PATH] = _SaunaDashboard(hass)

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
    """Remove the sauna dashboard when the last config entry is unloaded."""
    if not hass.data.get(_REGISTERED_KEY):
        return

    if hass.data.get(DOMAIN):
        return

    lovelace_data: dict = hass.data.get("lovelace", {})
    lovelace_data.get("dashboards", {}).pop(DASHBOARD_URL_PATH, None)

    async_remove_panel(hass, DASHBOARD_URL_PATH)
    hass.data.pop(_REGISTERED_KEY, None)
    _LOGGER.debug("Sauna dashboard removed")
