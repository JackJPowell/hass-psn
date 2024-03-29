"""The IntelliFire integration."""
from __future__ import annotations

import logging
from typing import Any

from psnawp_api.core import psnawp_exceptions
from psnawp_api.psnawp import PSNAWP

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEVICE_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PsnCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data update coordinator for PSN."""

    def __init__(self, hass: HomeAssistant, api, user, client) -> None:
        """Initialize the Coordinator."""
        super().__init__(
            hass,
            name=DOMAIN,
            logger=_LOGGER,
            update_interval=DEVICE_SCAN_INTERVAL,
        )

        self.hass = hass
        self.api = api
        self.user = user
        self.client = client
        self.data = {
            "presence": {},
            "available": False,
            "platform": {},
            "title_metadata": {},
            "friends": [],
            "trophy_summary": [],
            "title_details": {},
            "title_trophies": {},
            "title_stats": {},
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Get the latest data from the PSN."""
        try:
            self.data["presence"] = await self.user.get_presence()
            self.data["available"] = (
                self.data["presence"].get("basicPresence").get("availability")
                == "availableToPlay"
            )
            self.data["platform"] = (
                self.data["presence"].get("basicPresence").get("primaryPlatformInfo")
            )
            if self.data["available"] == True:
                self.data["title_metadata"] = (
                    self.data["presence"]
                    .get("basicPresence")
                    .get("gameTitleInfoList")[0]
                )
            self.data["friends"] = await self.client.available_to_play()
            self.data["trophy_summary"] = await self.client.trophy_summary()

            if (
                self.data["available"] == True
                and self.data["title_metadata"].get("npTitleId") is not None
            ):
                title_id = self.data["title_metadata"].get("npTitleId")
                title = self.api.game_title(title_id, "me", title_id)
                self.data["title_details"] = await title.get_details()
                trophy_title = self.api.trophy_titles()
                self.data[
                    "title_trophies"
                ] = await trophy_title.get_trophy_summary_for_title([title_id])

            return self.data
        except psnawp_exceptions.PSNAWPUnauthorized:
            self.api = await PSNAWP.create(self.config_entry.data["npsso"])
        except Exception as ex:
            raise UpdateFailed(
                f"Error communicating with the Playstation Network {ex}"
            ) from ex
        _LOGGER.debug("PSN Data Update values")
