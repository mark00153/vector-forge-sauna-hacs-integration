"""Button entity for Sauna Controller fault reset."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    async_add_entities([SaunaResetFaultButton(coordinator)])


class SaunaResetFaultButton(SaunaEntity, ButtonEntity):
    """Button to reset active faults."""

    _attr_name = "Reset Fault"
    _attr_icon = "mdi:alert-circle-check"

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "reset_fault")

    async def async_press(self) -> None:
        await self.coordinator.async_reset_fault()
