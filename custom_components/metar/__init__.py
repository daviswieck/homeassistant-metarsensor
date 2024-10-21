import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "metar"

async def async_setup_entry(hass, entry):
    """Set up the METAR integration from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
