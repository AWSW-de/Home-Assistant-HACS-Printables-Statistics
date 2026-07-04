# Printables Stats for Home Assistant

Custom integration for Home Assistant that exposes public statistics from a Printables.com user profile as sensors.

> The requested `Prointables.com` domain does not appear to expose a public site. This integration targets `Printables.com` and keeps the website/API base URLs configurable.

## Sensors

- Downloads
- Followers and following
- Published models, paid models, store models
- Published edu projects and articles
- Likes given and likes received
- Makes
- Collections
- Club members
- Profile level

## Installation with HACS

1. Add this repository as a custom HACS repository.
2. Select category `Integration`.
3. Install `Printables Stats`.
4. Restart Home Assistant.
5. Add the integration from **Settings > Devices & services > Add integration**.

## Configuration

Enter a Printables profile handle like `Prusa3D`, `@Prusa3D`, or a profile URL like `https://www.printables.com/@Prusa3D`.

The integration resolves the public profile page to a user id, then polls `https://api.printables.com/graphql/` every 30 minutes. No login or token is required for public profile statistics.

## Notes

Printables does not publish this API as a stable third-party contract. The integration therefore includes a fallback parser for the public profile page, but future site changes can still require updates.
