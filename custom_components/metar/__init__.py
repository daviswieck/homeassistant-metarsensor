from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up METAR from a config entry."""
    try:
        # Use async_create_task to avoid blocking during setup
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        )
    except Exception as err:
        raise ConfigEntryNotReady(f"Error setting up METAR: {err}") from err

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
