"""Constants for the Printables Stats integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "printables_stats"

CONF_PROFILE = "profile"
CONF_BASE_URL = "base_url"
CONF_API_URL = "api_url"

DEFAULT_BASE_URL = "https://www.printables.com"
DEFAULT_API_URL = "https://api.printables.com"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

ATTR_HANDLE = "handle"
ATTR_PUBLIC_USERNAME = "public_username"
ATTR_PROFILE_URL = "profile_url"
ATTR_USER_ID = "user_id"
ATTR_VERIFIED = "verified"
ATTR_HIDDEN_STATS = "hidden_stats"
