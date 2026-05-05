from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_BASE_URL,
    CONF_START_MONTH,
)
from .api import async_get_token


DEFAULT_BASE_URL = "https://eu1-developer.deyecloud.com/v1.0"
DEFAULT_START_MONTH = "2024-01"


def _data_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return config/options schema with defaults."""
    defaults = defaults or {}

    return vol.Schema({
        vol.Required(
            CONF_USERNAME,
            default=defaults.get(CONF_USERNAME, ""),
        ): str,
        vol.Required(
            CONF_PASSWORD,
            default=defaults.get(CONF_PASSWORD, ""),
        ): str,
        vol.Required(
            CONF_APP_ID,
            default=defaults.get(CONF_APP_ID, ""),
        ): str,
        vol.Required(
            CONF_APP_SECRET,
            default=defaults.get(CONF_APP_SECRET, ""),
        ): str,
        vol.Required(
            CONF_BASE_URL,
            default=defaults.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        ): str,
        vol.Required(
            CONF_START_MONTH,
            default=defaults.get(CONF_START_MONTH, DEFAULT_START_MONTH),
        ): str,
    })


class DeyeCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DeyeCloud."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Create the options flow."""
        return DeyeCloudOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)

                await async_get_token(
                    session,
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_APP_ID],
                    user_input[CONF_APP_SECRET],
                    user_input[CONF_BASE_URL],
                )

                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"DeyeCloud - {user_input[CONF_USERNAME]}",
                    data=user_input,
                )

            except Exception:
                errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=_data_schema(),
            errors=errors,
        )


class DeyeCloudOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle DeyeCloud options flow.

    This flow updates entry.data because the integration currently reads
    credentials and API settings from entry.data in sensor.py and button.py.
    """

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage DeyeCloud configuration."""
        errors = {}

        current_data = dict(self._config_entry.data)

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)

                await async_get_token(
                    session,
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_APP_ID],
                    user_input[CONF_APP_SECRET],
                    user_input[CONF_BASE_URL],
                )

                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    title=f"DeyeCloud - {user_input[CONF_USERNAME]}",
                    data=user_input,
                )

                return self.async_create_entry(title="", data={})

            except Exception:
                errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="init",
            data_schema=_data_schema(current_data),
            errors=errors,
        )