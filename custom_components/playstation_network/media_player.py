"""Media player entity for PSN."""

import logging
from dataclasses import dataclass

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PSN_COORDINATOR
from .entity import PSNEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class PSNdata:
    """PSN dataclass"""

    account = {"id": "", "handle": ""}
    presence = {"availability": "", "lastAvailableDate": ""}
    platform = {"status": "", "platform": ""}
    title = {"name": "", "format": "", "imageURL": None, "playing": False}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Entity Setup"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][PSN_COORDINATOR]
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([MediaPlayer(coordinator)])


class MediaPlayer(PSNEntity, MediaPlayerEntity):
    """Media player entity representing currently playing game"""

    device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_OFF | MediaPlayerEntityFeature.TURN_ON
    )

    def __init__(self, coordinator) -> None:
        """Initialize PSN MediaPlayer."""
        super().__init__(coordinator)
        self.data = self.coordinator.data

    @property
    def icon(self):
        return "mdi:sony-playstation"

    @property
    def media_image_remotely_accessible(self):
        return True

    @property
    def state(self):
        match self.data.get("platform").get("onlineStatus"):
            case "online":
                return MediaPlayerState.ON
            case "offline":
                return MediaPlayerState.STANDBY
            case _:
                return MediaPlayerState.STANDBY

    @property
    def unique_id(self):
        return f"{self.data.get('platform').get('platform')}_console"

    @property
    def name(self):
        return f"{self.data.get('platform').get('platform')} Console"

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MediaType.GAME

    @property
    def media_title(self):
        if self.data.get("title_metadata").get("npTitleId"):
            return self.data.get("title_metadata").get("titleName")
        if self.data.get("platform").get("onlineStatus") == "online":
            return "Playstation Online"
        else:
            return "Playstation Offline"

    @property
    def app_name(self):
        return ""
        # return self.data.title.get("name")

    @property
    def media_image_url(self):
        if self.data.get("title_metadata").get("npTitleId"):
            title = self.data.get("title_metadata")
            if title.get("format").casefold() == "ps5":
                return title.get("conceptIconUrl")

            if title.get("format").casefold() == "ps4":
                return title.get("npTitleIconUrl")
        return None

    @property
    def is_on(self):
        """Is user available on PSN"""
        return self.data.get("available") is True

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self.async_write_ha_state()
