"""Fixtures for pywaze."""

from typing import Any
from httpx import Response
import httpx
import pytest
from respx import MockRouter

from tests.const import (
    ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    ADDRESS_TO_COORDS_RESPONSE_MAINZ,
)


@pytest.fixture
def get_route_mock(get_route_response: dict[str, Any], respx_mock: MockRouter):
    """Return the provided json response when calculating routes."""
    yield respx_mock.get("https://www.waze.com/row-RoutingManager/routingRequest").mock(
        return_value=Response(
            200,
            json=get_route_response,
        )
    )


@pytest.fixture
def timeout_mock(respx_mock: MockRouter):
    """Throw a httpx.TimeoutException when calculating routes."""
    yield respx_mock.get("https://www.waze.com/row-RoutingManager/routingRequest").mock(
        side_effect=httpx.TimeoutException("Timeout")
    )


@pytest.fixture()
def wiesbaden_to_coords_mock(respx_mock: MockRouter):
    """Return the provided json response when converting this address to coordinates."""
    yield respx_mock.route(
        path="/row-SearchServer/mozi",
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
        path="/row-SearchServer/mozi",
        params={"q": "Kaiserstraße 30 55116 Mainz, Germany"},
    ).mock(
        return_value=Response(
            200,
            json=ADDRESS_TO_COORDS_RESPONSE_MAINZ,
        )
    )
