"""Fixtures for pywaze."""

from typing import Any
from unittest.mock import AsyncMock, patch

from curl_cffi.requests import AsyncSession
from httpx import Response
import httpx
import pytest
from respx import MockRouter

from pywaze import route_calculator
from tests.const import (
    ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    ADDRESS_TO_COORDS_RESPONSE_MAINZ,
)


@pytest.fixture
def routing_session_mock():
    """Mock the routing transport without affecting HTTPX address requests."""
    with patch.object(route_calculator, "AsyncSession") as factory:
        factory.return_value = AsyncMock(spec=AsyncSession)
        yield factory.return_value


@pytest.fixture
def get_route_mock(get_route_response: dict[str, Any], respx_mock: MockRouter):
    """Return the provided json response when calculating routes."""
    yield respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(200, json=get_route_response)


@pytest.fixture
def timeout_mock(respx_mock: MockRouter):
    """Throw a httpx.TimeoutException when calculating routes."""
    yield respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).mock(side_effect=httpx.TimeoutException("Timeout"))


@pytest.fixture()
def wiesbaden_to_coords_mock(respx_mock: MockRouter):
    """Return the provided json response when converting this address to coordinates."""
    yield respx_mock.route(
        url="https://gapi.waze.com/autocomplete/q",
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
    ).mock(
        return_value=Response(
            200,
            json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
        )
    )


@pytest.fixture()
def mainz_to_coords_mock(respx_mock: MockRouter):
    """Return the provided json response when converting this address to coordinates."""
    yield respx_mock.route(
        url="https://gapi.waze.com/autocomplete/q",
        params={"q": "Kaiserstraße 30 55116 Mainz, Germany"},
    ).mock(
        return_value=Response(
            200,
            json=ADDRESS_TO_COORDS_RESPONSE_MAINZ,
        )
    )
