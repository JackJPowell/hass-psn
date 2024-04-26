"""Platform for sensor integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
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


def get_status(coordinator_data: any) -> dict[str, str]:
    """Returns online status"""
    match coordinator_data.get("platform").get("onlineStatus"):
        case "online":
            if (
                coordinator_data.get("available") is True
                and coordinator_data.get("title_metadata").get("npTitleId") is not None
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
    if coordinator_data.get("title_metadata").get("npTitleId") is not None:
        attrs: dict[str, str] = {
            "name": "",
            "description": "",
            "platform": "",
            "contentRating": "",
            "starRating": "",
            "trophies": {
                "platinum": 0,
                "gold": 0,
                "silver": 0,
                "bronze": 0,
            },
            "earned_trophies": {
                "platinum": 0,
                "gold": 0,
                "silver": 0,
                "bronze": 0,
            },
        }

        title = coordinator_data.get("title_details")[0]
        title_trophies = coordinator_data.get("title_trophies")[0]

        attrs["name"] = title.get("name")
        attrs["description"] = title.get("descriptions")[0].get("desc")
        attrs["platform"] = (
            coordinator_data.get("presence")
            .get("basicPresence")
            .get("gameTitleInfoList")[0]
            .get("format")
        )
        attrs["contentRating"] = title.get("contentRating").get("description")
        attrs["starRating"] = title.get("starRating").get("score")
        attrs["trophies"] = title_trophies.defined_trophies
        attrs["earned_trophies"] = title_trophies.earned_trophies
    else:
        attrs = {}
    return attrs


def get_trophy_attr(coordinator_data: any) -> dict[str, str]:
    """Create the attributes for earned trophies."""
    attrs: dict[str, str] = {
        "platinum": 0,
        "gold": 0,
        "silver": 0,
        "bronze": 0,
        "next_level_progress": 0,
    }
    earned_trophies = coordinator_data.get("trophy_summary").earned_trophies

    attrs["platinum"] = earned_trophies.platinum
    attrs["gold"] = earned_trophies.gold
    attrs["silver"] = earned_trophies.silver
    attrs["bronze"] = earned_trophies.bronze
    attrs["next_level_progress"] = coordinator_data.get("trophy_summary").progress
    return attrs


PSN_SENSOR: tuple[PsnSensorEntityDescription, ...] = (
    PsnSensorEntityDescription(
        key="friends",
        native_unit_of_measurement="friends",
        suggested_unit_of_measurement="friends",
        description="Your Online PSN Friends",
        name="Friends Online",
        icon="mdi:account-group",
        entity_registry_enabled_default=True,
        has_entity_name=False,
        unique_id="friends_online",
        value_fn=lambda data: len(data.get("friends")),
        attributes_fn=lambda data: {},
    ),
    PsnSensorEntityDescription(
        key="trophy_summary",
        native_unit_of_measurement="Trophy Level",
        suggested_unit_of_measurement="",
        description="Your PSN Trophies",
        name="Playstation Trophy Level",
        icon="mdi:trophy",
        entity_registry_enabled_default=True,
        has_entity_name=False,
        unique_id="psn_trophies",
        value_fn=lambda data: data.get("trophy_summary").trophy_level,
        attributes_fn=get_trophy_attr,
    ),
    PsnSensorEntityDescription(
        key="status",
        device_class=SensorDeviceClass.ENUM,
        description="Your PSN Status",
        name="PSN Status",
        icon="mdi:account-circle-outline",
        options=["Online", "Offline", "Playing"],
        entity_registry_enabled_default=True,
        has_entity_name=False,
        unique_id="psn_status",
        value_fn=get_status,
        attributes_fn=get_status_attr,
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][PSN_COORDINATOR]
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        PsnSensor(coordinator, description) for description in PSN_SENSOR
    )


class PsnSensor(PSNEntity, SensorEntity):
    """PSN Sensor Class."""

    entity_description = PSN_SENSOR

    def __init__(self, coordinator, description: PsnSensorEntityDescription) -> None:
        """Initialize PSN Sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"psn_{description.unique_id}"
        self.entity_description = description
        self._state = 0

    @property
    def available(self) -> bool:
        """Return if available."""
        return True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._attr_native_value = self.entity_description.value_fn(
            self.coordinator.data
        )
        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        """Return native value for entity."""
        self._state = self.entity_description.value_fn(self.coordinator.data)
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes of the entity."""
        return self.entity_description.attributes_fn(self.coordinator.data)
