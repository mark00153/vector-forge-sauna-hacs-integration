"""Binary sensors for Sauna Controller."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAULT_DESCRIPTIONS
from .coordinator import SaunaCoordinator
from .entity import SaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SaunaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SaunaDoorSensor(coordinator),
        SaunaHeatSensor(coordinator),
        SaunaFaultSensor(coordinator),
    ])


class SaunaDoorSensor(SaunaEntity, BinarySensorEntity):
    """Door open/closed sensor."""

    _attr_name = "Door"
    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "door")

    @property
    def is_on(self) -> bool:
        """True = door open."""
        return not self.data.get("door_closed", True)


class SaunaHeatSensor(SaunaEntity, BinarySensorEntity):
    """Heater relay active sensor."""

    _attr_name = "Heater"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "heater")

    @property
    def is_on(self) -> bool:
        return self.data.get("relay", False)


class SaunaFaultSensor(SaunaEntity, BinarySensorEntity):
    """Fault condition sensor."""

    _attr_name = "Fault"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "fault")

    @property
    def is_on(self) -> bool:
        return bool(self.data.get("fault_flags", 0))

    @property
    def extra_state_attributes(self) -> dict:
        flags = self.data.get("fault_flags", 0)
        if not flags:
            return {}
        active = [desc for bit, desc in FAULT_DESCRIPTIONS.items() if flags & bit]
        return {"fault_list": active}
