""" Config Flow to configure AstroWeather Integration. """
import logging
import random
import string

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_ID,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_ELEVATION,
)
from homeassistant.core import callback
from pyastroweatherio import FORECAST_TYPE_HOURLY, FORECAST_TYPE_DAILY, FORECAST_TYPES

from .const import (
    CONF_FORECAST_INTERVAL,
    CONF_FORECAST_TYPE,
    DEFAULT_FORECAST_INTERVAL,
    FORECAST_INTERVAL_MIN,
    FORECAST_INTERVAL_MAX,
    DEFAULT_ELEVATION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AstroWeatherFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a AstroWeather config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is None:
            return await self._show_setup_form(user_input)

        # unique_id = "".join(
        #     random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        #     for _ in range(12)
        # )

        unique_id = (
            f"{str(user_input[CONF_LATITUDE])}_{str(user_input[CONF_LONGITUDE])}"
        )
        await self.async_set_unique_id(unique_id)

        _LOGGER.debug("Unique id: %s", str(unique_id))
        return self.async_create_entry(
            title=f"{round(user_input[CONF_LATITUDE], 3)}°, {round(user_input[CONF_LONGITUDE], 3)}°, {round(user_input[CONF_ELEVATION], 0)}m",
            data={
                CONF_ID: unique_id,
                CONF_LATITUDE: user_input[CONF_LATITUDE],
                CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                CONF_ELEVATION: user_input[CONF_ELEVATION],
                # CONF_FORECAST_TYPE: user_input[CONF_FORECAST_TYPE],
                CONF_FORECAST_INTERVAL: user_input.get(CONF_FORECAST_INTERVAL),
            },
        )

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): vol.All(vol.Coerce(float), vol.Range(min=-89, max=89)),
                    vol.Required(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
                    vol.Required(CONF_ELEVATION, default=DEFAULT_ELEVATION): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=4000)
                    ),
                    # vol.Optional(
                    #     CONF_FORECAST_TYPE, default=FORECAST_TYPE_DAILY
                    # ): vol.In(FORECAST_TYPES),
                    vol.Optional(
                        CONF_FORECAST_INTERVAL, default=DEFAULT_FORECAST_INTERVAL
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=FORECAST_INTERVAL_MIN, max=FORECAST_INTERVAL_MAX),
                    ),
                }
            ),
            errors=errors or {},
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LATITUDE,
                        default=self.config_entry.options.get(
                            CONF_LATITUDE, self.hass.config.latitude
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=-89, max=89)),
                    vol.Required(
                        CONF_LONGITUDE,
                        default=self.config_entry.options.get(
                            CONF_LONGITUDE, self.hass.config.longitude
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
                    vol.Required(
                        CONF_ELEVATION,
                        default=self.config_entry.options.get(
                            CONF_ELEVATION, DEFAULT_ELEVATION
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=4000)),
                    # vol.Optional(
                    #     CONF_FORECAST_TYPE,
                    #     default=self.config_entry.options.get(
                    #         CONF_FORECAST_TYPE, FORECAST_TYPE_DAILY
                    #     ),
                    # ): vol.In(FORECAST_TYPES),
                    vol.Optional(
                        CONF_FORECAST_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_FORECAST_INTERVAL, DEFAULT_FORECAST_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=FORECAST_INTERVAL_MIN, max=FORECAST_INTERVAL_MAX),
                    ),
                }
            ),
        )
