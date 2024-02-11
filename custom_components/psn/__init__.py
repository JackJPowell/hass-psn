"""The PSN integration."""
from __future__ import annotations

from psnawp_api.psnawp import PSNAWP

from config.custom_components.psn.coordinator import PsnCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery

from .const import DOMAIN, PSN_API, PSN_COORDINATOR

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PSN from a config entry."""

    npsso = entry.data.get("npsso")
    psn = await PSNAWP.create(npsso)
    user = await psn.user(online_id="me")
    client = await psn.me()
    coordinator = PsnCoordinator(hass, psn, user, client)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        PSN_COORDINATOR: coordinator,
        PSN_API: psn,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {CONF_NAME: entry.title, "entry_id": entry.entry_id},
            hass.data["psn"],
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update Listener."""
    await hass.config_entries.async_reload(entry.entry_id)
