![GitHub Release](https://img.shields.io/github/v/release/jackjpowell/hass-psn)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/jackjpowell/hass-psn/total)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://brands.home-assistant.io/playstation_network/dark_logo.png">
  <img alt="Playstation Network logo" src="https://brands.home-assistant.io/playstation_network/logo.png">
</picture>

## Playstation Network for Home Assistant

Home Assistant integration for the [Playstation Network](https://www.psn.com/).

## Installation

There are two main ways to install this custom component within your Home Assistant instance:

1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

   1. From within Home Assistant, click on the link to **HACS**
   2. Click on **Integrations**
   3. Click on the vertical ellipsis in the top right and select **Custom repositories**
   4. Enter the URL for this repository in the section that says _Add custom repository URL_ and select **Integration** in the _Category_ dropdown list
   5. Click the **ADD** button
   6. Close the _Custom repositories_ window
   7. You should now be able to see the _playstation network_ card on the HACS Integrations page. Click on **INSTALL** and proceed with the installation instructions.
   8. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

2. Manual Installation:
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
   2. Follow this link to be presented with your NPSSO code
   3. Only copy the alphanumeric string after "npsso": Do not copy the quotes

## Usage

After the device is configured, the integration will expose 3 entities:

- Sensors
  - Status: Your current status on the playstation network
  - Trophies: Your playstation trophy level
    - Additional attributes are available which breakdown your trophy stats
- Media Player
  - When playing a game the media player entity will be populated with game details such as the title and cover art

## Playstation Messages

The integration supports sending playstation network messages using the notify.playstation_network service. Below are two examples:

```
service: notify.playstation_network
data: {
  message: "Hey buddy, want to play some overwatch? ",
  target: user1
}
```

```
service: notify.playstation_network
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
