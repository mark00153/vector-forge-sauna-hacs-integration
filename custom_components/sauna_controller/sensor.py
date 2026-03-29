"""Sensors for Sauna Controller."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATE_DOOR_OPEN, STATE_FAULT, STATE_HEATING, STATE_IDLE
from .coordinator import SaunaCoordinator
from .entity import SaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SaunaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SaunaTemperatureSensor(coordinator),
        SaunaStateSensor(coordinator),
    ])


class SaunaTemperatureSensor(SaunaEntity, SensorEntity):
    """Current sauna temperature."""

    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "temperature")

    @property
    def native_value(self) -> float | None:
        if not self.data.get("sensor_ok"):
            return None
        temp = self.data.get("temp_f")
        return temp if temp is not None and temp > -100 else None


class SaunaStateSensor(SaunaEntity, SensorEntity):
    """Sauna state machine state."""

    _attr_name = "State"
    _attr_icon = "mdi:state-machine"

    _STATE_LABELS = {
        STATE_IDLE: "Idle",
        STATE_HEATING: "Heating",
        STATE_DOOR_OPEN: "Door open",
        STATE_FAULT: "Fault",
        "PROVISIONING": "Provisioning",
    }

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "state")

    @property
    def native_value(self) -> str:
        state = self.data.get("state", STATE_IDLE)
        return self._STATE_LABELS.get(state, state)
