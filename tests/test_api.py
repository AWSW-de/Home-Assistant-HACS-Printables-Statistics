"""Tests for Printables Stats API helpers."""

from __future__ import annotations

import html
import importlib.util
import json
import sys
import types
from pathlib import Path

aiohttp_stub = types.ModuleType("aiohttp")
aiohttp_stub.ClientError = Exception
aiohttp_stub.ClientResponseError = Exception
aiohttp_stub.ClientSession = object
sys.modules.setdefault("aiohttp", aiohttp_stub)

API_PATH = Path(__file__).parents[1] / "custom_components" / "printables_stats" / "api.py"
SPEC = importlib.util.spec_from_file_location("printables_stats_api", API_PATH)
assert SPEC is not None
api = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)


def test_normalize_profile_handle() -> None:
    """Normalize handles and URLs."""
    assert api.normalize_profile_handle("Prusa3D") == "Prusa3D"
    assert api.normalize_profile_handle("@Prusa3D") == "Prusa3D"
    assert (
        api.normalize_profile_handle("https://www.printables.com/@Prusa3D/models")
        == "Prusa3D"
    )


def test_extract_user_from_profile_html() -> None:
    """Extract user data from SvelteKit fetched JSON."""
    body = {"data": {"user": {"id": "16", "handle": "Prusa3D"}}}
    outer = {"status": 200, "body": json.dumps(body)}
    encoded = html.escape(json.dumps(outer))
    page = (
        '<script type="application/json" data-sveltekit-fetched '
        f'data-url="https://api.printables.com/graphql/">{encoded}</script>'
    )

    assert api.extract_user_from_profile_html(page) == {"id": "16", "handle": "Prusa3D"}


if __name__ == "__main__":
    test_normalize_profile_handle()
    test_extract_user_from_profile_html()
