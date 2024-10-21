import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN

class MetarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the METAR integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate if the airport code works (optional check)
                await self._validate_airport_code(user_input["airport_code"])
                return self.async_create_entry(
                    title=user_input["airport_name"], data=user_input
                )
            except ConfigEntryNotReady:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("airport_name"): str,
                vol.Required("airport_code"): str,
                vol.Optional("monitored_conditions", default=["temperature"]): vol.MultipleSelect(
                    {
                        "temperature": "Temperature",
                        "weather": "Weather",
                        "wind": "Wind",
                        "pressure": "Pressure",
                        "visibility": "Visibility",
                        "sky": "Sky",
                    }
                ),
            }),
            errors=errors,
        )

    async def _validate_airport_code(self, code):
        """Optional: Validate the airport code by attempting a request."""
        import aiohttp
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{code}.TXT"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ConfigEntryNotReady("Cannot connect to METAR source.")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return MetarOptionsFlowHandler(config_entry)


class MetarOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for METAR."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("monitored_conditions", default=self.config_entry.options.get("monitored_conditions", ["temperature"])): vol.MultipleSelect(
                    {
                        "temperature": "Temperature",
                        "weather": "Weather",
                        "wind": "Wind",
                        "pressure": "Pressure",
                        "visibility": "Visibility",
                        "sky": "Sky",
                    }
                ),
            }),
        )
