import voluptuous as vol

from homeassistant import config_entries
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


DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Required(CONF_APP_ID): str,
    vol.Required(CONF_APP_SECRET): str,
    vol.Required(
        CONF_BASE_URL,
        default="https://eu1-developer.deyecloud.com/v1.0",
    ): str,
    vol.Required(CONF_START_MONTH, default="2024-01"): str,
})


class DeyeCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DeyeCloud."""

    VERSION = 1

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
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
