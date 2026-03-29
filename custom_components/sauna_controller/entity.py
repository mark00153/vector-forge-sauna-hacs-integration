"""Base entity for Sauna Controller."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN, MANUFACTURER, MODEL
from .coordinator import SaunaCoordinator


class SaunaEntity(CoordinatorEntity[SaunaCoordinator]):
    """Base class for all sauna controller entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SaunaCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"sauna_{coordinator.host}_{unique_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="Sauna Controller",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{coordinator.host}",
        )

    @property
    def data(self) -> dict:
        """Shortcut to coordinator data."""
        return self.coordinator.data or {}
