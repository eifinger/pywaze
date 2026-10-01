"""Opt-in, reproducible checks against real routing and geocoding services."""

import os

import httpx
import pytest

from pywaze.route_calculator import WazeRouteCalculator

pytestmark = pytest.mark.skipif(
    os.environ.get("PYWAZE_LIVE_TESTS") != "1",
    reason="Set PYWAZE_LIVE_TESTS=1 to contact Waze",
)


@pytest.mark.parametrize(
    "region,start,end,addresses",
    (
        (
            "EU",
            "50.00332659227126,8.262322651915843",
            "50.08414976707619,8.247836017342934",
            (
                "Kaiserstraße 30 55116 Mainz, Germany",
                "Luisenstraße 30 65185 Wiesbaden, Germany",
            ),
        ),
        (
            "US",
            "40.7484,-73.9857",
            "40.7587,-73.9787",
            ("Empire State Building, New York", "Rockefeller Center, New York"),
        ),
        (
            "IL",
            "31.78923,35.20322",
            "31.7850,35.2126",
            ("Jerusalem Central Bus Station", "Mahane Yehuda Market Jerusalem"),
        ),
        (
            "AU",
            "-35.2801,149.1336",
            "-35.3082,149.1244",
            ("Canberra Centre Australia", "Parliament House Canberra Australia"),
        ),
        (
            "NA",
            "40.7484,-73.9857",
            "40.7587,-73.9787",
            ("Empire State Building, New York", "Rockefeller Center, New York"),
        ),
    ),
)
async def test_live_coordinate_address_and_mixed_routes(
    region: str, start: str, end: str, addresses: tuple[str, str]
):
    """Exercise the unchanged API, including an injected HTTPX client, in every region."""
    async with (
        httpx.AsyncClient() as injected,
        WazeRouteCalculator(region, client=injected) as client,
    ):
        bias_lat, bias_lon = map(float, start.split(","))
        for address, reference in zip(addresses, (start, end), strict=True):
            coords = await client.address_to_coords(
                address, {"lat": bias_lat, "lon": bias_lon}
            )
            reference_lat, reference_lon = map(float, reference.split(","))
            # Check the actual locations, not merely a positive route elsewhere.
            assert coords["lat"] == pytest.approx(reference_lat, abs=0.02)
            assert coords["lon"] == pytest.approx(reference_lon, abs=0.02)
        for origin, destination in ((start, end), addresses, (start, addresses[1])):
            routes = await client.calc_routes(
                origin, destination, alternatives=3, base_coords=start
            )
            # nPaths is a request hint; Waze can return additional alternatives.
            assert routes
            for route in routes:
                assert 0 < route.duration < 180
                assert 0 < route.distance < 100
                assert route.name
                assert route.street_names


async def test_live_nondefault_options():
    """Retain segment-based calculations and routing options rather than web totals."""
    async with WazeRouteCalculator() as client:
        routes = await client.calc_routes(
            "Kaiserstraße 30 55116 Mainz, Germany",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            alternatives=2,
            vehicle_type="MOTORCYCLE",
            avoid_toll_roads=True,
            avoid_subscription_roads=True,
            avoid_ferries=True,
            time_delta=15,
            real_time=False,
            stop_at_bounds=True,
            base_coords=(50.0, 8.2),
        )
        assert routes
        assert 0 < routes[0].duration < 180
        assert 0 < routes[0].distance < 100
        assert routes[0].street_names
