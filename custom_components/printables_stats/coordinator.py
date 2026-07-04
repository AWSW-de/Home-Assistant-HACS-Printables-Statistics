"""Data update coordinator for Printables Stats."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PrintablesClient, PrintablesError
from .const import CONF_PROFILE, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PrintablesStatsCoordinator(DataUpdateCoordinator[dict]):
    """Fetch and store Printables profile statistics."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: PrintablesClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        self.config_entry = entry

    async def _async_update_data(self) -> dict:
        """Fetch data from Printables."""
        try:
            return await self.client.async_get_stats(self.config_entry.data[CONF_PROFILE])
        except PrintablesError as err:
            raise UpdateFailed(str(err)) from err
