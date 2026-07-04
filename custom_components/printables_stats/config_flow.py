"""Config flow for Printables Stats."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, InvalidResponse, PrintablesClient, ProfileNotFound
from .const import (
    CONF_API_URL,
    CONF_BASE_URL,
    CONF_PROFILE,
    DEFAULT_API_URL,
    DEFAULT_BASE_URL,
    DOMAIN,
)


class PrintablesStatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Printables Stats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = PrintablesClient(
                session=session,
                base_url=user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                api_url=user_input.get(CONF_API_URL, DEFAULT_API_URL),
            )
            try:
                profile = await client.async_resolve_profile(user_input[CONF_PROFILE])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except ProfileNotFound:
                errors[CONF_PROFILE] = "profile_not_found"
            except InvalidResponse:
                errors["base"] = "invalid_response"
            else:
                await self.async_set_unique_id(profile.user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=profile.public_username or profile.handle,
                    data={
                        CONF_PROFILE: profile.handle,
                        CONF_BASE_URL: user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                        CONF_API_URL: user_input.get(CONF_API_URL, DEFAULT_API_URL),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROFILE): str,
                    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                    vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str,
                }
            ),
            errors=errors,
        )
