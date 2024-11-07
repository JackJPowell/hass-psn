![GitHub Release](https://img.shields.io/github/v/release/jackjpowell/hass-psn)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/jackjpowell/hass-psn/total)
<a href="#"><img src="https://img.shields.io/maintenance/yes/2024.svg"></a>
[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee&nbsp;☕-FFDD00?logo=buy-me-a-coffee&logoColor=white&labelColor=grey)](https://buymeacoffee.com/jackpowell)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://brands.home-assistant.io/playstation_network/dark_logo.png">
  <img alt="Playstation Network logo" src="https://brands.home-assistant.io/playstation_network/logo.png">
</picture>

## [Playstation Network](https://www.psn.com/) for Home Assistant
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/JackJPowell/hass-psn/assets/7500683/7e6d7acd-e384-49aa-9e8f-ae589eadb4d7">
  <img alt="Example Implementation" src="https://github.com/JackJPowell/hass-psn/assets/7500683/7e6d7acd-e384-49aa-9e8f-ae589eadb4d7">
</picture>

## Installation

There are two main ways to install this custom component within your Home Assistant instance:

1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

    [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JackJPowell&repository=hass-psn&category=Integration)

   Or

   1. From within Home Assistant, click on the link to **HACS**
   2. Click on **Integrations**
   3. Click on the vertical ellipsis in the top right and select **Custom repositories**
   4. Enter the URL for this repository in the section that says _Add custom repository URL_ and select **Integration** in the _Category_ dropdown list
   5. Click the **ADD** button
   6. Close the _Custom repositories_ window
   7. You should now be able to see the _playstation network_ card on the HACS Integrations page. Click on **INSTALL** and proceed with the installation instructions.
   8. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

3. Manual Installation:
   1. Download or clone this repository
   2. Copy the contents of the folder **custom_components/playstation_network** into the same file structure on your Home Assistant instance
   3. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

While the manual installation above seems like less steps, it's important to note that you will not be able to see updates to this custom component unless you are subscribed to the watch list. You will then have to repeat each step in the process. By using HACS, you'll be able to see that an update is available and easily update the custom component. Trust me, HACS is the worth the small upfront investment to get it setup.

## Configuration

There is a config flow for this integration. After installing the custom component and restarting:

1. Go to **Settings** -> **Devices & Services** -> **Integrations**
2. Click **+ ADD INTEGRATION** to setup a new integration
3. Search for **Playstation Network** and select it
4. _You will now begin the configuration flow process_
5. **NPSSO** can be found via the following steps:
   1. Login to your [Playstation](https://playstation.com) account
     1. Be sure to include your contry code like `/en-us/` or `/en-gb/` on the end of the url
   2. Follow [this link](https://ca.account.sony.com/api/v1/ssocookie) to be presented with your NPSSO code
   3. Only copy the alphanumeric string after "npsso": Do not copy the quotes
   4. If you are receiving a 429 error, logout of your playstation account and go back to step 1

## Usage

After the device is configured, the integration will expose 3 entities:

- Sensors
  - Status: Your current status on the playstation network
  - Trophies: Your playstation trophy level
    - Additional attributes are available which breakdown your trophy stats
- Media Player
  - When playing a game the media player entity will be populated with game details such as the title and cover art

## Options

There is now an option to configure the playstation network integration so it will create all additional state attributes as top level sensor entities. If you had trouble referencing the state attributes on the sensors, toggle this option on.

## Playstation Messages

The integration supports sending playstation network messages using the notify.playstation_network action. Below are two examples:

```
action: notify.playstation_network
data: {
  message: "Hey buddy, want to play some overwatch? ",
  target: user1
}
```

```
action: notify.playstation_network
data: {
  message: "Hey guys, want to play some destiny?",
  target: ["user1","user2"]
}
```

> [!TIP] When more than one user is supplied in a list, a group conversation will be created

## Future Ideas

- [ ] Extract additional game information
- [ ] Display friends who are online

## Notes

- No Notes

## About This Project

I am not associated with Sony or any of its subsidiaries, and provide this custom component purely for your own enjoyment and home automation needs.
