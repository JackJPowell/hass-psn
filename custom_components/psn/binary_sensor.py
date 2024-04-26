"""Binary sensor platform for Unfolded Circle."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PSN_API

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup routine"""
    api = hass.data[DOMAIN][config_entry.entry_id][PSN_API]

    npsso = config_entry.data.get("npsso")
    psn = await api.create(npsso)
    # api = PSNAWP(npsso)
    # client = await hass.async_add_executor_job(api.me)
    user = await api.user(online_id="JackPowell")
    presence = await user.get_presence()
    api = {"api": psn, "user": user, "presence": presence}

    new_devices = []
    new_devices.append(BinarySensor(api))
    if new_devices:
        async_add_entities(new_devices)


class BinarySensor(BinarySensorEntity):
    """Binary Sensor representing online status"""

    device_class = BinarySensorDeviceClass.PRESENCE

    def __init__(self, api) -> None:
        """Initialize the sensor."""
        self._api = api

        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._api.get('user').online_id}_presence"

        # The name of the entity
        self._attr_name = f"{self._api.get('user').online_id} Presence"
        self._attr_icon = "mdi:sony-playstation"

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return (
            self._api.get("presence").get("basicPresence").get("availability")
            == "availableToPlay"
        )

    async def async_update(self) -> None:
        """Async update"""
        ...

    # await self._api.update()
