"""Client for public Printables profile statistics."""

from __future__ import annotations

import html
import json
import logging
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from aiohttp import ClientError, ClientResponseError, ClientSession

_LOGGER = logging.getLogger(__name__)

PROFILE_JSON_RE = re.compile(
    r'<script type="application/json" data-sveltekit-fetched[^>]*>(.*?)</script>',
    re.DOTALL,
)

USER_STATS_QUERY = """
query PrintablesUserStats($id: ID!) {
  user(id: $id) {
    id
    handle
    publicUsername
    verified
    hiddenStats
    dateCreated
    downloadCount
    followersCount
    followingCount
    publishedPrintsCount
    paidModelsCount
    storeModelsCount
    publishedEduProjectsCount
    publishedArticlesCount
    likesCountPrints
    likesCountEduProjects
    likesReceivedCountPrints
    makesCount
    collectionsCount
    clubMembersCount
    badgesProfileLevel {
      profileLevel
    }
  }
}
"""

USER_SEARCH_QUERY = """
query PrintablesUserSearch($query: String!) {
  quickSearchUsers(query: $query) {
    items {
      id
      handle
      publicUsername
      verified
    }
  }
}
"""

REQUEST_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": (
        "Mozilla/5.0 (compatible; HomeAssistant-PrintablesStats/0.1; "
        "+https://www.home-assistant.io/)"
    ),
}


class PrintablesError(Exception):
    """Base exception for Printables client errors."""


class CannotConnect(PrintablesError):
    """Raised when Printables cannot be reached."""


class ProfileNotFound(PrintablesError):
    """Raised when a profile cannot be found."""


class InvalidResponse(PrintablesError):
    """Raised when Printables returns an unexpected response."""


@dataclass
class PrintablesProfile:
    """Resolved Printables profile."""

    user_id: str
    handle: str
    public_username: str | None
    profile_url: str


class PrintablesClient:
    """Small async client for public Printables profile data."""

    def __init__(self, session: ClientSession, base_url: str, api_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._api_url = api_url.rstrip("/")

    async def async_resolve_profile(self, profile: str) -> PrintablesProfile:
        """Resolve a profile handle or URL to the Printables user id."""
        handle = normalize_profile_handle(profile)
        try:
            user = await self._async_search_profile_user(handle)
        except PrintablesError as err:
            _LOGGER.debug("GraphQL profile search failed, falling back to page: %s", err)
            profile_url = f"{self._base_url}/@{handle}"
            user = await self._async_fetch_profile_user(profile_url)

        return PrintablesProfile(
            user_id=str(user["id"]),
            handle=str(user.get("handle") or handle),
            public_username=user.get("publicUsername"),
            profile_url=f"{self._base_url}/@{user.get('handle') or handle}",
        )

    async def async_get_stats(self, profile: str) -> dict[str, Any]:
        """Fetch current public statistics for a profile."""
        resolved = await self.async_resolve_profile(profile)

        try:
            user = await self._async_graphql_user(resolved.user_id)
        except InvalidResponse as err:
            _LOGGER.debug("GraphQL stats lookup failed, falling back to profile page: %s", err)
            user = await self._async_fetch_profile_user(resolved.profile_url)

        return _normalize_user_stats(user, resolved)

    async def _async_graphql_user(self, user_id: str) -> dict[str, Any]:
        """Fetch user statistics through Printables GraphQL."""
        try:
            response = await self._session.post(
                f"{self._api_url}/graphql/",
                json={"query": USER_STATS_QUERY, "variables": {"id": user_id}},
                headers={**REQUEST_HEADERS, "content-type": "application/json"},
                timeout=20,
            )
            response.raise_for_status()
            payload = await response.json()
        except (ClientError, TimeoutError) as err:
            raise CannotConnect("Could not connect to Printables GraphQL") from err
        except (ClientResponseError, json.JSONDecodeError) as err:
            raise InvalidResponse("Printables GraphQL returned an invalid response") from err

        if payload.get("errors"):
            raise InvalidResponse(str(payload["errors"]))

        user = payload.get("data", {}).get("user")
        if not isinstance(user, dict):
            raise ProfileNotFound("Printables user was not found")
        return user

    async def _async_search_profile_user(self, handle: str) -> dict[str, Any]:
        """Resolve a profile by handle through Printables quick search."""
        try:
            response = await self._session.post(
                f"{self._api_url}/graphql/",
                json={"query": USER_SEARCH_QUERY, "variables": {"query": handle}},
                headers={**REQUEST_HEADERS, "content-type": "application/json"},
                timeout=20,
            )
            response.raise_for_status()
            payload = await response.json()
        except (ClientError, TimeoutError) as err:
            raise CannotConnect("Could not connect to Printables GraphQL") from err
        except (ClientResponseError, json.JSONDecodeError) as err:
            raise InvalidResponse("Printables GraphQL returned an invalid response") from err

        if payload.get("errors"):
            raise InvalidResponse(str(payload["errors"]))

        items = payload.get("data", {}).get("quickSearchUsers", {}).get("items", [])
        if not isinstance(items, list):
            raise InvalidResponse("Printables user search returned an invalid response")

        for user in items:
            if not isinstance(user, dict):
                continue
            if str(user.get("handle", "")).casefold() == handle.casefold():
                return user

        raise ProfileNotFound("Printables profile was not found")

    async def _async_fetch_profile_user(self, profile_url: str) -> dict[str, Any]:
        """Fetch the public profile page and extract its embedded user payload."""
        try:
            response = await self._session.get(
                profile_url,
                headers=REQUEST_HEADERS,
                timeout=20,
            )
            if response.status == 404:
                raise ProfileNotFound("Printables profile was not found")
            response.raise_for_status()
            text = await response.text()
        except ProfileNotFound:
            raise
        except (ClientError, TimeoutError) as err:
            raise CannotConnect("Could not connect to Printables profile page") from err
        except ClientResponseError as err:
            raise InvalidResponse("Printables profile page returned an error") from err

        user = extract_user_from_profile_html(text)
        if user is None:
            raise InvalidResponse("Could not find profile data in Printables page")
        return user


def normalize_profile_handle(value: str) -> str:
    """Normalize a Printables handle, profile URL, or @handle."""
    cleaned = value.strip()
    parsed = urlparse(cleaned)
    if parsed.netloc:
        path = parsed.path.strip("/")
        cleaned = path.split("/", 1)[0] if path else cleaned
    if cleaned.startswith("@"):
        cleaned = cleaned[1:]
    if not cleaned:
        raise ProfileNotFound("Profile handle is empty")
    return cleaned


def extract_user_from_profile_html(text: str) -> dict[str, Any] | None:
    """Extract the user object from SvelteKit fetched JSON blocks."""
    for match in PROFILE_JSON_RE.finditer(text):
        try:
            outer = json.loads(html.unescape(match.group(1)))
            body = json.loads(outer.get("body", "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        user = body.get("data", {}).get("user")
        if isinstance(user, dict) and user.get("id"):
            return user
    return None


def _normalize_user_stats(user: dict[str, Any], resolved: PrintablesProfile) -> dict[str, Any]:
    """Map Printables field names to stable Home Assistant data keys."""
    profile_level = None
    badges = user.get("badgesProfileLevel")
    if isinstance(badges, dict):
        profile_level = badges.get("profileLevel")

    return {
        "user_id": str(user.get("id") or resolved.user_id),
        "handle": str(user.get("handle") or resolved.handle),
        "public_username": user.get("publicUsername") or resolved.public_username,
        "profile_url": resolved.profile_url,
        "verified": bool(user.get("verified", False)),
        "hidden_stats": bool(user.get("hiddenStats", False)),
        "date_created": user.get("dateCreated"),
        "downloads": _as_int(user.get("downloadCount")),
        "followers": _as_int(user.get("followersCount")),
        "following": _as_int(user.get("followingCount")),
        "published_models": _as_int(
            user.get("publishedPrintsCount", user.get("publishedModelsCount"))
        ),
        "paid_models": _as_int(user.get("paidModelsCount")),
        "store_models": _as_int(user.get("storeModelsCount")),
        "published_edu_projects": _as_int(user.get("publishedEduProjectsCount")),
        "published_articles": _as_int(user.get("publishedArticlesCount")),
        "likes_given_models": _as_int(
            user.get("likesCountPrints", user.get("likesCountModels"))
        ),
        "likes_given_edu_projects": _as_int(user.get("likesCountEduProjects")),
        "likes_received_models": _as_int(
            user.get("likesReceivedCountPrints", user.get("likesReceivedCountModels"))
        ),
        "makes": _as_int(user.get("makesCount")),
        "collections": _as_int(user.get("collectionsCount")),
        "club_members": _as_int(user.get("clubMembersCount")),
        "profile_level": _as_int(profile_level),
    }


def _as_int(value: Any) -> int | None:
    """Convert numeric values to int without turning missing values into zero."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
