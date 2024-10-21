from .const import BASE_URL  # Import from const.py
from metar import Metar  # Import Metar library
from urllib.request import urlopen  # For fetching data
import logging
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)




async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the METAR sensor platform."""
    airport = entry.data["airport_code"]
    name = entry.data["airport_name"]
    monitored_conditions = entry.data.get("monitored_conditions", ["temperature"])

    async_add_entities([MetarSensor(name, airport, monitored_conditions)], True)

class MetarSensor(Entity):
    """Representation of a METAR sensor."""

    def __init__(self, name, airport_code, monitored_conditions):
        self._name = name
        self._airport_code = airport_code
        self._monitored_conditions = monitored_conditions
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"METAR {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    def update(self):
        """Fetch new data from the METAR service."""
        url = f"{BASE_URL}{self._airport_code}.TXT"
        try:
            with urlopen(url) as response:
                for line in response:
                    line = line.decode().strip()
                    if line.startswith(self._airport_code):
                        report = Metar.Metar(line)
                        self._parse_report(report)
                        break
        except Exception as e:
            _LOGGER.error("Failed to fetch METAR data: %s", e)

    def _parse_report(self, report):
        """Parse the METAR report."""
        for condition in self._monitored_conditions:
            try:
                if condition == "temperature":
                    self._attributes["Temperature"] = report.temp.value("C")
                    self._state = report.temp.value("C")
                elif condition == "weather":
                    self._attributes["Weather"] = report.present_weather()
                # Add more conditions as needed
            except AttributeError:
                _LOGGER.warning("Missing data for %s", condition)
