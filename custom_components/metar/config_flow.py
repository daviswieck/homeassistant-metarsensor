import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class MetarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Include monitored conditions if the input is valid
            user_input.setdefault("monitored_conditions", ["temperature"])
            return self.async_create_entry(
                title=user_input["airport_name"], data=user_input
            )

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
