"""Lovelace dashboard for Sauna Controller."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel
from homeassistant.components.lovelace.dashboard import LovelaceStorage
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.start import async_at_started

from .const import DOMAIN
from .coordinator import SaunaCoordinator

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL_PATH = "sauna"
DASHBOARD_TITLE = "Sauna"
DASHBOARD_ICON = "mdi:hot-tub"
STORAGE_KEY = f"lovelace.{DASHBOARD_URL_PATH}"

_REGISTERED_KEY = f"{DOMAIN}_dashboard_registered"


def _lookup_entity_ids(hass: HomeAssistant, host: str) -> dict[str, str]:
    """Return a mapping of suffix → real entity_id from the entity registry.

    Falls back to the default slugified ID if an entry isn't found.
    """
    registry = er.async_get(hass)
    suffixes = [
        "climate",
        "temperature",
        "state",
        "door",
        "heater",
        "fault",
        "master",
        "reset_fault",
    ]
    result: dict[str, str] = {}
    for suffix in suffixes:
        unique_id = f"sauna_{host}_{suffix}"
        entry = registry.async_get_entity_id(
            _SUFFIX_PLATFORM[suffix], DOMAIN, unique_id
        )
        # Fall back to the default slug if registry lookup misses
        result[suffix] = entry or f"{_SUFFIX_PLATFORM[suffix]}.sauna_controller_{suffix}"
    return result


# Maps unique_id suffix → HA platform domain
_SUFFIX_PLATFORM: dict[str, str] = {
    "climate": "climate",
    "temperature": "sensor",
    "state": "sensor",
    "door": "binary_sensor",
    "heater": "binary_sensor",
    "fault": "binary_sensor",
    "master": "switch",
    "reset_fault": "button",
}

# Special case: climate unique_id suffix is "climate" but default entity_id
# doesn't have a suffix appended — override the fallback for climate.
_CLIMATE_FALLBACK = "climate.sauna_controller"


def _build_dashboard_config(entities: dict[str, str], device_url: str) -> dict[str, Any]:
    """Build the Lovelace dashboard config from resolved entity IDs."""
    climate_id = entities.get("climate", _CLIMATE_FALLBACK)
    # Climate entity_id has no suffix in the default slug
    if climate_id.endswith("_climate"):
        climate_id = climate_id[: -len("_climate")]

    return {
        "title": "Sauna",
        "views": [
            {
                "title": "Sauna",
                "icon": "mdi:hot-tub",
                "cards": [
                    {
                        "type": "markdown",
                        "content": f"# Sauna Controller\n[Open device web interface »]({device_url})",
                    },
                    {
                        "type": "thermostat",
                        "entity": climate_id,
                        "name": "Sauna",
                    },
                    {
                        "type": "entity",
                        "entity": entities["master"],
                        "name": "Master Switch",
                        "icon": "mdi:power",
                    },
                    {
                        "type": "horizontal-stack",
                        "cards": [
                            {
                                "type": "entity",
                                "entity": entities["state"],
                                "name": "State",
                                "icon": "mdi:state-machine",
                            },
                            {
                                "type": "entity",
                                "entity": entities["door"],
                                "name": "Door",
                            },
                            {
                                "type": "entity",
                                "entity": entities["heater"],
                                "name": "Heater",
                            },
                        ],
                    },
                    {
                        "type": "history-graph",
                        "title": "Temperature History",
                        "entities": [{"entity": entities["temperature"]}],
                        "hours_to_show": 2,
                    },
                    {
                        "type": "entities",
                        "title": "Fault Details",
                        "entities": [
                            {
                                "entity": entities["fault"],
                                "type": "attribute",
                                "attribute": "fault_list",
                                "name": "Active Faults",
                                "icon": "mdi:alert-circle-outline",
                            },
                            {
                                "entity": entities["reset_fault"],
                                "name": "Reset Fault",
                            },
                        ],
                    },
                ],
            }
        ],
    }


async def _write_storage_file(hass: HomeAssistant, coordinator: SaunaCoordinator) -> None:
    """Write the dashboard config to HA's .storage directory."""
    storage_path = hass.config.path(".storage", STORAGE_KEY)

    entities = _lookup_entity_ids(hass, coordinator.host)
    device_url = coordinator.base_url
    dashboard_config = _build_dashboard_config(entities, device_url)
    _LOGGER.debug("Sauna dashboard entity IDs resolved: %s", entities)

    storage_data = {
        "version": 1,
        "minor_version": 1,
        "key": STORAGE_KEY,
        "data": {"config": dashboard_config},
    }

    def _write() -> None:
        with open(storage_path, "w", encoding="utf-8") as f:
            json.dump(storage_data, f, indent=2)

    await hass.async_add_executor_job(_write)
    _LOGGER.debug("Sauna dashboard storage file written to %s", storage_path)


async def async_setup_dashboard(hass: HomeAssistant, coordinator: SaunaCoordinator) -> None:
    """Register the sauna Lovelace dashboard and sidebar entry."""
    if hass.data.get(_REGISTERED_KEY):
        return

    await _write_storage_file(hass, coordinator)

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

    lovelace_cfg = {
        "id": DASHBOARD_URL_PATH,
        "mode": "storage",
        "icon": DASHBOARD_ICON,
        "title": DASHBOARD_TITLE,
        "show_in_sidebar": True,
        "require_admin": False,
        "url_path": DASHBOARD_URL_PATH,
    }

    def _try_register_lovelace(hass: HomeAssistant) -> bool:
        """Register LovelaceStorage. Returns True if successful."""
        lovelace_data = hass.data.get("lovelace")
        if lovelace_data is not None and hasattr(lovelace_data, "dashboards"):
            lovelace_data.dashboards[DASHBOARD_URL_PATH] = LovelaceStorage(hass, lovelace_cfg)
            _LOGGER.debug("Sauna LovelaceStorage registered at /%s", DASHBOARD_URL_PATH)
            return True
        return False

    if not _try_register_lovelace(hass):
        # Lovelace not ready yet — defer until HA fully started.
        async def _register_lovelace_deferred(_hass: HomeAssistant) -> None:
            if not _try_register_lovelace(_hass):
                _LOGGER.warning(
                    "Lovelace dashboards registry not found; dashboard cards may not load correctly"
                )

        async_at_started(hass, _register_lovelace_deferred)


async def async_unload_dashboard(hass: HomeAssistant) -> None:
    """Remove the sauna sidebar panel when the last config entry is unloaded.

    The storage file is intentionally left in place so user edits survive
    reinstalls.
    """
    if not hass.data.get(_REGISTERED_KEY):
        return

    if hass.data.get(DOMAIN):
        return

    lovelace_data = hass.data.get("lovelace")
    if lovelace_data is not None and hasattr(lovelace_data, "dashboards"):
        lovelace_data.dashboards.pop(DASHBOARD_URL_PATH, None)

    async_remove_panel(hass, DASHBOARD_URL_PATH)
    hass.data.pop(_REGISTERED_KEY, None)
    _LOGGER.debug("Sauna dashboard panel removed")
