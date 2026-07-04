"""Printables Stats integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PrintablesClient
from .const import CONF_API_URL, CONF_BASE_URL, DEFAULT_API_URL, DEFAULT_BASE_URL, DOMAIN
from .coordinator import PrintablesStatsCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Printables Stats from a config entry."""
    client = PrintablesClient(
        session=async_get_clientsession(hass),
        base_url=entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        api_url=entry.data.get(CONF_API_URL, DEFAULT_API_URL),
    )
    coordinator = PrintablesStatsCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
