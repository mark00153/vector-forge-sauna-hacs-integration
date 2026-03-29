"""Switch entity for Sauna Controller master switch."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SaunaCoordinator
from .entity import SaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SaunaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SaunaMasterSwitch(coordinator)])


class SaunaMasterSwitch(SaunaEntity, SwitchEntity):
    """Master switch for the sauna."""

    _attr_name = "Master Switch"
    _attr_icon = "mdi:power"

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "master")

    @property
    def is_on(self) -> bool:
        return self.data.get("master", False)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_master(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_master(False)
        await self.coordinator.async_request_refresh()
