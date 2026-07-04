"""Tests for Printables Stats API helpers."""

from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

aiohttp_stub = types.ModuleType("aiohttp")
aiohttp_stub.ClientError = Exception
aiohttp_stub.ClientResponseError = Exception
aiohttp_stub.ClientSession = object
sys.modules.setdefault("aiohttp", aiohttp_stub)

API_PATH = ROOT / "custom_components" / "printables_stats" / "api.py"
SPEC = importlib.util.spec_from_file_location("printables_stats_api", API_PATH)
assert SPEC is not None
api = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)

PrintablesClient = api.PrintablesClient
extract_user_from_profile_html = api.extract_user_from_profile_html
normalize_profile_handle = api.normalize_profile_handle


def test_normalize_profile_handle() -> None:
    """Normalize supported profile input formats."""
    assert normalize_profile_handle("AWSW") == "AWSW"
    assert normalize_profile_handle("@AWSW") == "AWSW"
    assert normalize_profile_handle("https://www.printables.com/@AWSW/models") == "AWSW"


def test_extract_user_from_profile_html() -> None:
    """Extract embedded SvelteKit profile data."""
    body = json.dumps({"data": {"user": {"id": "100312", "handle": "Rene"}}})
    outer = json.dumps({"body": body})
    html = (
        '<script type="application/json" data-sveltekit-fetched>'
        f"{outer}"
        "</script>"
    )

    assert extract_user_from_profile_html(html) == {"id": "100312", "handle": "Rene"}


def test_search_profile_uses_suggested_users_fallback() -> None:
    """Find exact handles returned by suggestUsers2 but not quickSearchUsers."""

    class Response:
        def raise_for_status(self) -> None:
            return None

        async def json(self) -> dict:
            return {
                "data": {
                    "quickSearchUsers": {
                        "items": [{"id": "1", "handle": "rene_144588"}]
                    },
                    "suggestUsers2": {
                        "items": [{"id": "100312", "handle": "Rene"}]
                    },
                }
            }

    class Session:
        async def post(self, *args, **kwargs) -> Response:
            return Response()

    async def run_test() -> None:
        client = PrintablesClient(
            session=Session(),
            base_url="https://www.printables.com",
            api_url="https://api.printables.com",
        )
        assert await client._async_search_profile_user("Rene") == {
            "id": "100312",
            "handle": "Rene",
        }

    asyncio.run(run_test())
