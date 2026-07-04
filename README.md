# Printables Stats for Home Assistant

Custom Home Assistant integration that exposes public statistics from a Printables.com user profile as sensors.

## Features

- Configure a Printables profile by handle, `@handle`, or profile URL.
- Uses the public Printables GraphQL API where available.
- Falls back to the public profile page if needed.
- Creates sensors for downloads, followers, published models, likes, makes, collections, club members, and profile level.
- Includes local brand images for HACS and Home Assistant.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL:

   `https://github.com/AWSW-de/Home-Assistant-HACS-Printables-Statistics`

5. Select category **Integration**.
6. Download **Printables Stats**.
7. Restart Home Assistant.
8. Go to **Settings > Devices & services > Add integration** and search for **Printables Stats**.

## Configuration

Use one of these formats:

- `AWSW`
- `@AWSW`
- `https://www.printables.com/@AWSW`

The default URLs are:

- Printables website: `https://www.printables.com`
- Printables API: `https://api.printables.com`

## Sensors

- Downloads
- Followers
- Following
- Published models
- Paid models
- Store models
- Published education projects
- Published articles
- Likes given to models
- Likes given to education projects
- Likes received by models
- Makes
- Collections
- Club members
- Profile level

## Notes

This integration only uses public Printables profile data. It does not require a Printables login or API token.

![Printables Stats](Image1.png)

HACS integration for the Prusa Printables user AWSW. =)

You can find my profile and my models here: https://www.printables.com/@AWSW/models
