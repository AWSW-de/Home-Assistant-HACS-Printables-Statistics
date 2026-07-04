"""Sensors for Printables Stats."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_HANDLE,
    ATTR_HIDDEN_STATS,
    ATTR_PROFILE_URL,
    ATTR_PUBLIC_USERNAME,
    ATTR_USER_ID,
    ATTR_VERIFIED,
    DOMAIN,
)
from .coordinator import PrintablesStatsCoordinator


@dataclass(frozen=True, kw_only=True)
class PrintablesSensorDescription(SensorEntityDescription):
    """Description for a Printables statistics sensor."""

    value_key: str


SENSORS: tuple[PrintablesSensorDescription, ...] = (
    PrintablesSensorDescription(key="downloads", translation_key="downloads", value_key="downloads", icon="mdi:download", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="followers", translation_key="followers", value_key="followers", icon="mdi:account-heart", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="following", translation_key="following", value_key="following", icon="mdi:account-arrow-right", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="published_models", translation_key="published_models", value_key="published_models", icon="mdi:printer-3d-nozzle", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="paid_models", translation_key="paid_models", value_key="paid_models", icon="mdi:currency-usd", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="store_models", translation_key="store_models", value_key="store_models", icon="mdi:store", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="published_edu_projects", translation_key="published_edu_projects", value_key="published_edu_projects", icon="mdi:school", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="published_articles", translation_key="published_articles", value_key="published_articles", icon="mdi:newspaper-variant-outline", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="likes_given_models", translation_key="likes_given_models", value_key="likes_given_models", icon="mdi:thumb-up-outline", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="likes_given_edu_projects", translation_key="likes_given_edu_projects", value_key="likes_given_edu_projects", icon="mdi:thumb-up-outline", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="likes_received_models", translation_key="likes_received_models", value_key="likes_received_models", icon="mdi:heart", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="makes", translation_key="makes", value_key="makes", icon="mdi:hammer-wrench", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="collections", translation_key="collections", value_key="collections", icon="mdi:folder-multiple-outline", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="club_members", translation_key="club_members", value_key="club_members", icon="mdi:account-group", state_class=SensorStateClass.TOTAL),
    PrintablesSensorDescription(key="profile_level", translation_key="profile_level", value_key="profile_level", icon="mdi:badge-account", entity_category=EntityCategory.DIAGNOSTIC, state_class=SensorStateClass.TOTAL),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Printables Stats sensors."""
    coordinator: PrintablesStatsCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(PrintablesStatsSensor(coordinator, description) for description in SENSORS)


class PrintablesStatsSensor(CoordinatorEntity[PrintablesStatsCoordinator], SensorEntity):
    """A Printables statistics sensor."""

    entity_description: PrintablesSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: PrintablesStatsCoordinator, description: PrintablesSensorDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        user_id = coordinator.data.get("user_id", coordinator.config_entry.entry_id)
        self._attr_unique_id = f"{user_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(user_id))},
            "name": coordinator.data.get("public_username") or coordinator.data.get("handle") or "Printables",
            "manufacturer": "Printables",
            "configuration_url": coordinator.data.get("profile_url"),
        }

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self.entity_description.value_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return profile metadata as attributes."""
        data = self.coordinator.data
        return {
            ATTR_USER_ID: data.get("user_id"),
            ATTR_HANDLE: data.get("handle"),
            ATTR_PUBLIC_USERNAME: data.get("public_username"),
            ATTR_PROFILE_URL: data.get("profile_url"),
            ATTR_VERIFIED: data.get("verified"),
            ATTR_HIDDEN_STATS: data.get("hidden_stats"),
        }
