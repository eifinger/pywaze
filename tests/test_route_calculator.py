"""Tests for route_calculator module."""
import pytest
from pywaze import route_calculator
from tests.const import (
    GET_ROUTE_RESPONSE_ADDRESSES,
    GET_ROUTE_RESPONSE_COORDS,
)


@pytest.mark.parametrize(
    (
        "start",
        "end",
        "get_route_response",
        "expected_route_time",
        "expected_route_distance",
    ),
    (
        (
            "50.00332659227126,8.262322651915843",
            "50.08414976707619,8.247836017342934",
            GET_ROUTE_RESPONSE_COORDS,
            18.4,
            12.715,
        ),
        (
            "Kaiserstraße 30 55116 Mainz, Germany",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            GET_ROUTE_RESPONSE_ADDRESSES,
            18.183333333333334,
            12.644,
        ),
    ),
)
@pytest.mark.usefixtures(
    "get_route_mock", "wiesbaden_to_coords_mock", "mainz_to_coords_mock"
)
async def test_calc_route_info(
    start: str, end: str, expected_route_time: float, expected_route_distance: float
):
    """Test calc_route_info."""

    rc = route_calculator.WazeRouteCalculator()
    route_time, route_distance = await rc.calc_route_info(start, end)
    assert route_time == expected_route_time
    assert route_distance == expected_route_distance


@pytest.mark.parametrize(
    (
        "start",
        "end",
        "get_route_response",
        "expected_route_time",
        "expected_route_distance",
    ),
    (
        (
            "50.00332659227126,8.262322651915843",
            "50.08414976707619,8.247836017342934",
            GET_ROUTE_RESPONSE_COORDS,
            18.4,
            12.715,
        ),
        (
            "Kaiserstraße 30 55116 Mainz, Germany",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            GET_ROUTE_RESPONSE_ADDRESSES,
            18.183333333333334,
            12.644,
        ),
    ),
)
@pytest.mark.usefixtures(
    "get_route_mock", "wiesbaden_to_coords_mock", "mainz_to_coords_mock"
)
async def test_calc_all_routes_info(
    start: str, end: str, expected_route_time: float, expected_route_distance: float
):
    """Test calc_all_routes_info."""

    rc = route_calculator.WazeRouteCalculator()
    results = await rc.calc_all_routes_info(start, end)
    route_time, route_distance = list(results.values())[0]
    assert route_time == expected_route_time
    assert route_distance == expected_route_distance
