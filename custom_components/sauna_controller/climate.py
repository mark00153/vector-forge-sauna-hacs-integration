"""Climate entity for Sauna Controller."""
from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SETPOINT_DEFAULT,
    SETPOINT_MAX,
    SETPOINT_MIN,
    SETPOINT_STEP,
    STATE_HEATING,
)
from .coordinator import SaunaCoordinator
from .entity import SaunaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SaunaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SaunaClimate(coordinator)])


class SaunaClimate(SaunaEntity, ClimateEntity):
    """Climate entity representing the sauna heater."""

    _attr_name = None  # Uses device name
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_target_temperature_step = SETPOINT_STEP
    _attr_min_temp = SETPOINT_MIN
    _attr_max_temp = SETPOINT_MAX
    _attr_icon = "mdi:sauna"

    def __init__(self, coordinator: SaunaCoordinator) -> None:
        super().__init__(coordinator, "climate")

    @property
    def current_temperature(self) -> float | None:
        if not self.data.get("sensor_ok"):
            return None
        temp = self.data.get("temp_f")
        return temp if temp is not None and temp > -100 else None

    @property
    def target_temperature(self) -> float:
        return self.data.get("setpoint_f", SETPOINT_DEFAULT)

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.HEAT if self.data.get("master") else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        state = self.data.get("state", "IDLE")
        if state == STATE_HEATING:
            return HVACAction.HEATING
        if self.data.get("master"):
            return HVACAction.IDLE
        return HVACAction.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.async_set_master(hvac_mode == HVACMode.HEAT)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get("temperature")
        if temp is not None:
            await self.coordinator.async_set_setpoint(float(temp))
            await self.coordinator.async_request_refresh()
