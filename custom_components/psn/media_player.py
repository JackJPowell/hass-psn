"""Binary sensor platform for Unfolded Circle."""
from dataclasses import dataclass
import logging

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PSN_COORDINATOR
from .coordinator import PsnCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class PSNdata:
    account = {"id": "", "handle": ""}
    presence = {"availability": "", "lastAvailableDate": ""}
    platform = {"status": "", "platform": ""}
    title = {"name": "", "format": "", "imageURL": None, "playing": False}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id][PSN_COORDINATOR]
    await coordinator.async_config_entry_first_refresh()
    # api = hass.data[DOMAIN][config_entry.entry_id][PSN_API]

    # npsso = config_entry.data.get("npsso")
    # psn = await api.create(npsso)
    # user = await psn.user(online_id="me")
    # presence = await user.get_presence()
    # psn = {"psn": psn, "user": user, "presence": presence}

    async_add_entities([MediaPlayer(coordinator)])


class MediaPlayer(CoordinatorEntity[PsnCoordinator], MediaPlayerEntity):
    device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_OFF | MediaPlayerEntityFeature.TURN_ON
    )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "PSN")
            },
            name="PSN",
            manufacturer="Sony",
            model="Playstation Network",
            configuration_url="https://ca.account.sony.com/api/v1/ssocookie",
        )

    def __init__(self, coordinator) -> None:
        """Initialize PSN MediaPlayer."""
        super().__init__(self, coordinator)
        self.coordinator = coordinator
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

            if title == "ps4":
                return title.get("npTitleIconUrl")
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/PlayStation_logo2.svg/512px-PlayStation_logo2.svg.png?20210920040209"

    @property
    def is_on(self):
        return self.data.get("available") == True

    # async def async_update(self) -> None:
    #     # user = await self._psn.user(online_id="JackPowell")
    #     presence = await self._psn.get("user").get_presence()
    #     real_presence = {"presence": presence}
    #     self._psn.update(real_presence)

    #     self._parse_response()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # self._attr_native_value = self.entity_description.value_fn(
        #     self.coordinator.data
        # )
        self.async_write_ha_state()

    # def _parse_response(self) -> PSNdata:
    #     data = PSNdata()

    #     data.platform["status"] = (
    #         self._psn.get("presence")
    #         .get("basicPresence")
    #         .get("primaryPlatformInfo")
    #         .get("onlineStatus")
    #     )

    #     data.platform["platform"] = (
    #         self._psn.get("presence")
    #         .get("basicPresence")
    #         .get("primaryPlatformInfo")
    #         .get("platform")
    #     )

    #     data.account["id"] = self._psn.get("user").account_id
    #     data.account["handle"] = self._psn.get("user").online_id
    #     data.presence["availability"] = (
    #         self._psn.get("presence").get("basicPresence").get("availability")
    #     )
    #     data.presence["lastAvailableDate"] = (
    #         self._psn.get("presence").get("basicPresence").get("lastAvailableDate")
    #     )

    #     if data.platform.get("status") == "online":
    #         gameTitle = (
    #             self._psn.get("presence").get("basicPresence").get("gameTitleInfoList")
    #         )
    #         if gameTitle:
    #             data.title["name"] = gameTitle[0].get("titleName")
    #             data.title["playing"] = True

    #         data.title["format"] = (
    #             self._psn.get("presence")
    #             .get("basicPresence")
    #             .get("gameTitleInfoList")[0]
    #             .get("format")
    #         )

    #         if data.title["format"].casefold() == "ps5":
    #             data.title["imageURL"] = (
    #                 self._psn.get("presence")
    #                 .get("basicPresence")
    #                 .get("gameTitleInfoList")[0]
    #                 .get("conceptIconUrl")
    #             )
    #         if data.title["format"].casefold() == "ps4":
    #             data.title["imageURL"] = (
    #                 self._psn.get("presence")
    #                 .get("basicPresence")
    #                 .get("gameTitleInfoList")[0]
    #                 .get("npTitleIconUrl")
    #             )
    #     else:
    #         data.title["name"] = ""
    #         data.title["format"] = ""
    #         data.title["imageURL"] = None
    #         data.title["playing"] = False

    #     return data
