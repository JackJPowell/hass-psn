"""Platform for sensor integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorEntityDescription)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, PSN_COORDINATOR
from .entity import PSNEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class PsnSensorEntityDescription(SensorEntityDescription):
    """Class describing PSN sensor entities."""

    value_fn: Callable = None
    attributes_fn: Callable = None
    unique_id: str = ""
    description: str = ""


def get_status(coordinator_data: any) -> str:
    """Returns online status"""
    match coordinator_data.get("platform", {}).get("onlineStatus", "offline"):
        case "online":
            if (
                coordinator_data.get("available") is True
                and coordinator_data.get("title_metadata", {}).get("npTitleId")
            ):
                return "Playing"
            else:
                return "Online"
        case "offline":
            return "Offline"
        case _:
            return "Offline"


def get_status_attr(coordinator_data: any) -> dict[str, str]:
    """Parses status attributes"""
    attrs = {
        "name": "",
        "description": "",
        "platform": "",
        "content_rating": "",
        "play_count": 0,
        "play_duration": "0h 0m",
        "star_rating": 0,
        "trophies_platinum": 0,
        "trophies_gold": 0,
        "trophies_silver": 0,
        "trophies_bronze": 0,
        "earned_trophies_platinum": 0,
        "earned_trophies_gold": 0,
        "earned_trophies_silver": 0,
        "earned_trophies_bronze": 0,
        "trophy_progress": 0,
    }

    if coordinator_data.get("title_metadata", {}).get("npTitleId"):
        title = coordinator_data.get("title_details", [{}])[0]
        title_trophies = coordinator_data.get("title_trophies", {})

        attrs["name"] = title.get("name", "")
        attrs["description"] = title.get("descriptions", [{}])[0].get("desc", "")
        attrs["platform"] = (
            coordinator_data.get("presence", {})
            .get("basicPresence", {})
            .get("gameTitleInfoList", [{}])[0]
            .get("format", "")
        )
        attrs["content_rating"] = title.get("contentRating", {}).get("description", "")
        attrs["star_rating"] = title.get("starRating", {}).get("score", 0)
        attrs["trophies_platinum"] = title_trophies.get("platinum", 0)
        attrs["trophies_gold"] = title_trophies.get("gold", 0)
        attrs["trophies_silver"] = title_trophies.get("silver", 0)
        attrs["trophies_bronze"] = title_trophies.get("bronze", 0)
        attrs["trophy_progress"] = title_trophies.get("progress", 0)

    return attrs


def convert_time(duration: datetime) -> str:
    """Convert time duration to a formatted string."""
    minutes, seconds = divmod(duration.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if duration.days > 1:
        return f"{duration.days} Days {hours}h"
    elif duration.days == 1:
        return f"{duration.days} Day {hours}h"
    else:
        return f"{hours}h {minutes}m"


# Dynamically add individual sensors for each attribute
PSN_SENSOR = [
    PsnSensorEntityDescription(
        key="status",
        device_class=SensorDeviceClass.ENUM,
        name="Status",
        icon="mdi:account-circle-outline",
        options=["Online", "Offline", "Playing"],
        entity_registry_enabled_default=True,
        has_entity_name=True,
        unique_id="psn_status",
        value_fn=get_status,
        attributes_fn=get_status_attr,
    )
]

for attr_key, attr_name in get_status_attr({}).items():
    PSN_SENSOR.append(
        PsnSensorEntityDescription(
            key=attr_key,
            name=attr_key.replace("_", " ").capitalize(),
            icon="mdi:information-outline",
            unique_id=f"psn_{attr_key}",
            value_fn=lambda data, key=attr_key: get_status_attr(data).get(key, ""),
        )
    )


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][PSN_COORDINATOR]

    async_add_entities(
        PsnSensor(coordinator, description) for description in PSN_SENSOR
    )


class PsnSensor(PSNEntity, SensorEntity):
    """PSN Sensor Class."""

    def __init__(self, coordinator, description: PsnSensorEntityDescription) -> None:
        """Initialize PSN Sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.get('username', '').lower()}_{description.unique_id}"
        self._attr_name = description.name

    @property
    def native_value(self) -> StateType:
        """Return the value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
