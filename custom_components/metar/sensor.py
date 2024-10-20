import logging
import time
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import ATTR_ATTRIBUTION, CONF_MONITORED_CONDITIONS
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen  # Python 2 fallback
from metar import Metar

DOMAIN = 'metar'
CONF_AIRPORT_NAME = 'airport_name'
CONF_AIRPORT_CODE = 'airport_code'
SCAN_INTERVAL = timedelta(seconds=3600)
BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'time': 'Updated',
    'weather': 'Condition',
    'temperature': 'Temperature',
    'wind': 'Wind speed',
    'pressure': 'Pressure',
    'visibility': 'Visibility',
    'sky': 'Sky',
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_AIRPORT_NAME): cv.string,
    vol.Required(CONF_AIRPORT_CODE): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the METAR sensor platform."""
    airport = {
        'location': config[CONF_AIRPORT_NAME],
        'code': config[CONF_AIRPORT_CODE]
    }

    monitored_conditions = config[CONF_MONITORED_CONDITIONS]
    data = MetarData(airport)
    add_entities([MetarSensor(airport, data, monitored_conditions)], True)


class MetarSensor(Entity):
    """Representation of a single METAR sensor with multiple attributes."""

    def __init__(self, airport, weather_data, monitored_conditions):
        """Initialize the sensor."""
        self._airport_name = airport["location"]
        self._state = None
        self._attributes = {}
        self.weather_data = weather_data
        self.monitored_conditions = monitored_conditions

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"METAR {self._airport_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor."""
        try:
            self.weather_data.update()
        except Exception as e:
            _LOGGER.error("Error updating METAR data: %s", e)
            return

        sensor_data = self.weather_data.sensor_data
        if not sensor_data:
            return

        # Populate attributes based on monitored conditions
        for condition in self.monitored_conditions:
            try:
                if condition == 'time':
                    self._attributes['Updated'] = sensor_data.time.ctime()
                elif condition == 'temperature':
                    self._attributes['Temperature'] = sensor_data.temp.value('C')
                elif condition == 'weather':
                    self._attributes['Condition'] = sensor_data.present_weather()
                elif condition == 'wind':
                    self._attributes['Wind speed'] = sensor_data.wind()
                elif condition == 'pressure':
                    self._attributes['Pressure'] = sensor_data.press.string('mb')
                elif condition == 'visibility':
                    self._attributes['Visibility'] = sensor_data.visibility()
                elif condition == 'sky':
                    self._attributes['Sky'] = sensor_data.sky_conditions("\n     ")
            except KeyError:
                _LOGGER.warning("Condition not available: %s", condition)

        # Set a summary state (e.g., temperature or weather)
        self._state = self._attributes.get('Temperature', 'Unknown')


class MetarData:
    """Fetch data from the METAR source."""

    def __init__(self, airport):
        self._airport_code = airport["code"]
        self.sensor_data = None
        self.update()

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Retrieve the latest METAR data."""
        url = f"{BASE_URL}{self._airport_code}.TXT"
        try:
            with urlopen(url) as response:
                for line in response:
                    line = line.decode().strip()
                    if line.startswith(self._airport_code):
                        self.sensor_data = Metar.Metar(line)
                        _LOGGER.info("Fetched METAR: %s", self.sensor_data.string())
                        break
        except Exception as e:
            _LOGGER.error("Failed to retrieve METAR data: %s", e)