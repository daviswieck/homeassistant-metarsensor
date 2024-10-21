import logging
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import timedelta
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=60)
BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up METAR sensor based on a config entry."""
    data = entry.data
    airport = {"name": data["airport_name"], "code": data["airport_code"]}
    monitored_conditions = data["monitored_conditions"]

    async_add_entities([MetarSensor(airport, monitored_conditions)], True)

class MetarSensor(Entity):
    """Representation of a METAR sensor with multiple attributes."""

    def __init__(self, airport, monitored_conditions):
        """Initialize the sensor."""
        self._airport = airport
        self._monitored_conditions = monitored_conditions
        self._attributes = {}
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"METAR {self._airport['name']}"

    @property
    def state(self):
        """Return the main state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new data from METAR."""
        url = f"{BASE_URL}{self._airport['code']}.TXT"
        try:
            with urlopen(url) as response:
                for line in response:
                    line = line.decode().strip()
                    if line.startswith(self._airport['code']):
                        report = Metar.Metar(line)
                        self._parse_report(report)
                        break
        except Exception as e:
            _LOGGER.error("Failed to fetch METAR data: %s", e)

    def _parse_report(self, report):
        """Parse the METAR report and update attributes."""
        for condition in self._monitored_conditions:
            try:
                if condition == "temperature":
                    self._attributes["Temperature"] = report.temp.value("C")
                    self._state = report.temp.value("C")
                elif condition == "weather":
                    self._attributes["Weather"] = report.present_weather()
                elif condition == "wind":
                    self._attributes["Wind"] = report.wind()
                elif condition == "pressure":
                    self._attributes["Pressure"] = report.press.string("mb")
                elif condition == "visibility":
                    self._attributes["Visibility"] = report.visibility()
                elif condition == "sky":
                    self._attributes["Sky"] = report.sky_conditions()
            except AttributeError:
                _LOGGER.warning("Missing data for %s", condition)
