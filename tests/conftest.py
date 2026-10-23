"""Fixtures for pywaze."""

from typing import Any
from unittest.mock import patch

from curl_cffi.requests.exceptions import Timeout as CurlTimeout
import pytest

from pywaze import route_calculator
from tests.const import (
    ADDRESS_TO_COORDS_RESPONSE_MAINZ,
    ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
)
from tests.fake_waze import AUTOCOMPLETE_URL, ROUTING_URL, FakeRoute, FakeWaze


@pytest.fixture
def waze():
    """Replace the curl_cffi session used by pywaze with a fake server."""
    server = FakeWaze()
    with patch.object(route_calculator, "AsyncSession", server):
        yield server


@pytest.fixture
def get_route_mock(get_route_response: dict[str, Any], waze: FakeWaze) -> FakeRoute:
    """Return the provided json response when calculating routes."""
    return waze.add(ROUTING_URL, json=get_route_response)


@pytest.fixture
def timeout_mock(waze: FakeWaze) -> FakeRoute:
    """Raise a curl_cffi timeout when calculating routes."""
    return waze.add(ROUTING_URL, error=CurlTimeout("Timeout"))


@pytest.fixture
def wiesbaden_to_coords_mock(waze: FakeWaze) -> FakeRoute:
    """Return the provided json response when converting this address to coordinates."""
    return waze.add(
        AUTOCOMPLETE_URL,
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
        json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    )


@pytest.fixture
def mainz_to_coords_mock(waze: FakeWaze) -> FakeRoute:
    """Return the provided json response when converting this address to coordinates."""
    return waze.add(
        AUTOCOMPLETE_URL,
        params={"q": "Kaiserstraße 30 55116 Mainz, Germany"},
        json=ADDRESS_TO_COORDS_RESPONSE_MAINZ,
    )
