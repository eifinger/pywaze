"""Tests for route_calculator module."""

import warnings

from curl_cffi.requests import RequestsError
from curl_cffi.requests.exceptions import Timeout as CurlTimeout
from httpx import AsyncClient
import pytest
from pywaze import route_calculator
from tests.const import (
    ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    EMPTY_ROUTE_NAME_RESPONSE,
    GET_ROUTE_RESPONSE_ADDRESSES,
    GET_ROUTE_RESPONSE_COORDS,
    GET_ALL_ROUTES_RESPONSE,
)
from tests.fake_waze import AUTOCOMPLETE_URL, ROUTING_URL, FakeWaze


@pytest.mark.parametrize(
    (
        "start",
        "end",
        "alternatives",
        "get_route_response",
        "expected_route_times",
        "expected_route_distances",
        "expected_route_names",
        "expected_street_names",
    ),
    (
        (
            "50.00332659227126,8.262322651915843",
            "50.08414976707619,8.247836017342934",
            1,
            GET_ROUTE_RESPONSE_COORDS,
            [18.4],
            [12.715],
            ["B455 - Boelckestraße Wiesbaden"],
            [
                [
                    "Kaiserstraße",
                    "B40 - Kaiserstraße",
                    "Ernst-Ludwig-Straße",
                    "Diether-von-Isenburg-Straße",
                    "Peter-Altmeier-Allee",
                    "B40 - Peter-Altmeier-Allee",
                    "Rheinstraße",
                    "B40 - Rheinstraße",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "B40",
                    "Ludwigsrampe",
                    "B455 - Ludwigsrampe",
                    "Boelckestraße",
                    "B455 - Boelckestraße",
                    "B455",
                    "Berliner Straße",
                    "B455 - Berliner Straße",
                    "B54 - Berliner Straße",
                    "Frankfurter Straße",
                    "> Stadtmitte",
                    "L3037 - Frankfurter Straße",
                    "K658 - Frankfurter Straße",
                    "Bierstadter Straße",
                    "K659 - Bierstadter Straße",
                    "Paulinenstraße",
                ]
            ],
        ),
        (
            "Kaiserstraße 30 55116 Mainz, Germany",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            1,
            GET_ROUTE_RESPONSE_ADDRESSES,
            [18.183333333333334],
            [12.644],
            ["B455 - Boelckestraße Wiesbaden"],
            [
                [
                    "Ernst-Ludwig-Straße",
                    "Diether-von-Isenburg-Straße",
                    "Peter-Altmeier-Allee",
                    "B40 - Peter-Altmeier-Allee",
                    "Rheinstraße",
                    "B40 - Rheinstraße",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "B40",
                    "Ludwigsrampe",
                    "B455 - Ludwigsrampe",
                    "Boelckestraße",
                    "B455 - Boelckestraße",
                    "B455",
                    "Berliner Straße",
                    "B455 - Berliner Straße",
                    "B54 - Berliner Straße",
                    "Frankfurter Straße",
                    "> Stadtmitte",
                    "L3037 - Frankfurter Straße",
                    "Rheinstraße",
                    "L3037 - Rheinstraße",
                    "Schwalbacher Straße",
                    "K651 - Schwalbacher Straße",
                    "Luisenstraße",
                ]
            ],
        ),
        (
            "50.00332659227126,8.262322651915843",
            "50.08414976707619,8.247836017342934",
            3,
            GET_ALL_ROUTES_RESPONSE,
            [20.5, 25.883333333333333, 28.566666666666666],
            [12.635, 13.066, 12.957],
            [
                "B455 - Boelckestraße Wiesbaden",
                "K650 - Mainzer Straße Wiesbaden",
                "A643",
            ],
            [
                [
                    "Kaiserstraße",
                    "B40 - Kaiserstraße",
                    "Kaiser-Friedrich-Straße",
                    "Große Bleiche",
                    "Peter-Altmeier-Allee",
                    "B40 - Peter-Altmeier-Allee",
                    "Rheinstraße",
                    "B40 - Rheinstraße",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "B40",
                    "Ludwigsrampe",
                    "B455 - Ludwigsrampe",
                    "Boelckestraße",
                    "B455 - Boelckestraße",
                    "B455",
                    "Berliner Straße",
                    "B455 - Berliner Straße",
                    "B54 - Berliner Straße",
                    "Frankfurter Straße",
                    "L3037 - Frankfurter Straße",
                    "K658 - Frankfurter Straße",
                    "Bierstadter Straße",
                    "K659 - Bierstadter Straße",
                    "Paulinenstraße",
                ],
                [
                    "Kaiserstraße",
                    "B40 - Kaiserstraße",
                    "Kaiser-Friedrich-Straße",
                    "Große Bleiche",
                    "Peter-Altmeier-Allee",
                    "B40 - Peter-Altmeier-Allee",
                    "Rheinstraße",
                    "B40 - Rheinstraße",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "Theodor-Heuss-Brücke",
                    "B40 - Theodor-Heuss-Brücke",
                    "B40",
                    "Rampenstraße",
                    "L3482 - Rampenstraße",
                    "Wiesbadener Straße",
                    "L3482 - Wiesbadener Straße",
                    "Biebricher Straße",
                    "K648 - Biebricher Straße",
                    "Rheingaustraße",
                    "K648 - Rheingaustraße",
                    "Glarusstraße",
                    "K649 - Glarusstraße",
                    "Breslauer Straße",
                    "K649 - Breslauer Straße",
                    "Mainzer Straße",
                    "K650 - Mainzer Straße",
                    "> A66 / Wiesbaden-Stadtmitte",
                    "Lessingstraße",
                    "Friedrich-Ebert-Allee",
                    "Wilhelmstraße",
                    "Christian-Zais-Straße",
                ],
                [
                    "Kaiserstraße",
                    "B40 - Kaiserstraße",
                    "Boppstraße",
                    "L424 - Boppstraße",
                    "Kaiser-Wilhelm-Ring",
                    "L424 - Kaiser-Wilhelm-Ring",
                    "Barbarossaring",
                    "L424 - Barbarossaring",
                    "Kaiser-Karl-Ring",
                    "Rheinallee",
                    "K6 - Rheinallee",
                    "K17 - Rheinallee",
                    "A643 > Frankfurt / Wiesbaden",
                    "A643",
                    "A643",
                    "Schiersteiner Straße",
                    "B262 - Schiersteiner Straße",
                    "K644 - Schiersteiner Straße",
                    "Adelheidstraße",
                    "K644 - Adelheidstraße",
                    "Karlstraße",
                    "K644 - Karlstraße",
                    "Rheinstraße",
                    "L3037 - Rheinstraße",
                    "Wilhelmstraße",
                    "Christian-Zais-Straße",
                ],
            ],
        ),
        (
            "31.804461,35.2115243",
            "31.80459309184719,35.21160542964936",
            1,
            EMPTY_ROUTE_NAME_RESPONSE,
            [0.03333333333333333],
            [0.007],
            [""],
            [[]],
        ),
    ),
)
@pytest.mark.usefixtures(
    "get_route_mock", "wiesbaden_to_coords_mock", "mainz_to_coords_mock"
)
async def test_calc_route_info(
    start: str,
    end: str,
    alternatives: int,
    expected_route_times: list[float],
    expected_route_distances: list[float],
    expected_route_names: list[str],
    expected_street_names: list[list[str]],
):
    """Test calc_route_info."""

    async with route_calculator.WazeRouteCalculator() as client:
        routes = await client.calc_routes(start, end, alternatives=alternatives)
        for alternative in range(alternatives):
            assert routes[alternative].duration == expected_route_times[alternative]
            assert routes[alternative].distance == expected_route_distances[alternative]
            assert routes[alternative].name == expected_route_names[alternative]
            assert (
                routes[alternative].street_names == expected_street_names[alternative]
            )


SEGMENT_ROUTE = {
    "response": {"results": [{"length": 1000, "crossTime": 60}], "streetNames": []}
}
ROUTE_RESULT = route_calculator.CalcRoutesResponse(1.0, 1.0, "", [])


async def test_calc_routes_uses_custom_base_coords_for_address_lookup(waze: FakeWaze):
    """Use explicitly provided base coordinates for address resolving."""
    waze.add(ROUTING_URL, json=SEGMENT_ROUTE)
    lookup = waze.add(
        AUTOCOMPLETE_URL,
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
        json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    )

    async with route_calculator.WazeRouteCalculator() as client:
        await client.calc_routes(
            "50.00332659227126,8.262322651915843",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            base_coords=(48.137154, 11.576124),
        )

    assert lookup.calls[-1].params["sll"] == "48.137154,11.576124"


@pytest.mark.parametrize(
    ("start", "end", "expected_lat", "expected_lon"),
    (
        (
            "50.00332659227126,8.262322651915843",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            50.00332659227126,
            8.262322651915843,
        ),
        (
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            "50.00332659227126,8.262322651915843",
            50.00332659227126,
            8.262322651915843,
        ),
    ),
)
async def test_calc_routes_uses_other_endpoint_coords_as_base_when_missing(
    start: str,
    end: str,
    expected_lat: float,
    expected_lon: float,
    waze: FakeWaze,
):
    """Use coordinate endpoint as base coords when only one side is an address."""
    waze.add(ROUTING_URL, json=SEGMENT_ROUTE)
    lookup = waze.add(
        AUTOCOMPLETE_URL,
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
        json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    )

    async with route_calculator.WazeRouteCalculator() as client:
        await client.calc_routes(start, end)

    assert lookup.calls[-1].params["sll"] == f"{expected_lat},{expected_lon}"


@pytest.mark.parametrize("lookup", (False, True), ids=("routing", "address"))
async def test_every_request_uses_a_fresh_impersonating_session(
    lookup: bool, waze: FakeWaze
):
    """Never reuse a session: Waze blocks idle curl sessions and HTTPX fingerprints."""
    url = AUTOCOMPLETE_URL if lookup else ROUTING_URL
    route = waze.add(
        url, json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN if lookup else SEGMENT_ROUTE
    )

    async with route_calculator.WazeRouteCalculator(timeout=23) as client:
        assert not waze.sessions
        for expected_sessions in (1, 2):
            if lookup:
                coords = await client.address_to_coords(
                    "Wiesbaden", base_coords={"lat": 48.1, "lon": 11.6}
                )
                assert coords == {
                    "lat": 50.07912063598633,
                    "lon": 8.240204811096191,
                    "bounds": {},
                }
                assert route.calls[-1].params["sll"] == "48.1,11.6"
            else:
                routes = await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")
                assert routes == [ROUTE_RESULT]
            assert len(waze.sessions) == expected_sessions

    assert len({id(session) for session in waze.sessions}) == 2
    for session in waze.sessions:
        assert session.kwargs == {"impersonate": "chrome"}
        assert session.exit_args == [(None, None, None)]
    assert route.call_count == 2
    for call in route.calls:
        assert call.url == url
        assert call.headers == client.HEADERS
        assert call.timeout == 23


@pytest.mark.parametrize("lookup", (False, True), ids=("routing", "address"))
@pytest.mark.parametrize(
    ("failure", "expected_error", "message"),
    (
        (
            CurlTimeout("curl timeout"),
            route_calculator.WRCTimeoutError,
            "Timeout getting",
        ),
        (RequestsError("curl error"), route_calculator.WRCError, "Error getting"),
    ),
)
async def test_request_failures_close_session_and_map_to_public_errors(
    lookup: bool, failure: Exception, expected_error, message: str, waze: FakeWaze
):
    """Map curl_cffi failures to public errors and exit the session immediately."""
    waze.add(AUTOCOMPLETE_URL if lookup else ROUTING_URL, error=failure)

    async with route_calculator.WazeRouteCalculator() as client:
        with pytest.raises(expected_error, match=message) as exc_info:
            if lookup:
                await client.address_to_coords("Wiesbaden")
            else:
                await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")

    assert exc_info.value.__cause__ is failure
    (session,) = waze.sessions
    assert session.exit_args[0][1] is failure


@pytest.mark.parametrize("lookup", (False, True), ids=("routing", "address"))
@pytest.mark.parametrize("status", (403, 500))
async def test_http_errors_are_not_retried(lookup: bool, status: int, waze: FakeWaze):
    """Surface HTTP errors, including 403, from the single request made."""
    route = waze.add(
        AUTOCOMPLETE_URL if lookup else ROUTING_URL, status=status, text="blocked"
    )

    async with route_calculator.WazeRouteCalculator() as client:
        with pytest.raises(route_calculator.WRCError, match="blocked"):
            if lookup:
                await client.address_to_coords("Wiesbaden")
            else:
                await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")

    assert route.call_count == 1
    assert len(waze.sessions) == 1


async def test_client_argument_is_deprecated_and_ignored(waze: FakeWaze):
    """Keep accepting client= for compatibility, but never use or close it."""
    waze.add(ROUTING_URL, json=SEGMENT_ROUTE)
    async with AsyncClient() as injected:
        with pytest.warns(DeprecationWarning, match="client argument is deprecated"):
            calculator = route_calculator.WazeRouteCalculator(client=injected)
        async with calculator:
            routes = await calculator.calc_routes("50.0033,8.2623", "50.0841,8.2478")
        assert routes == [ROUTE_RESULT]
        assert not injected.is_closed
    assert len(waze.sessions) == 1


async def test_no_deprecation_warning_without_client():
    """Only warn when the deprecated argument is actually used."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        route_calculator.WazeRouteCalculator()


async def test_close_is_a_noop():
    """close() remains available and can be called repeatedly."""
    calculator = route_calculator.WazeRouteCalculator()
    await calculator.close()
    await calculator.close()


@pytest.mark.usefixtures("timeout_mock")
async def test_calc_route_info_timeout():
    """Test calc_route_info with timeout."""

    async with route_calculator.WazeRouteCalculator() as client:
        with pytest.raises(route_calculator.WRCTimeoutError):
            await client.calc_routes(
                "50.00332659227126,8.262322651915843",
                "50.08414976707619,8.247836017342934",
            )


def _alternative(name: str, seconds: int, **attrs) -> dict:
    return {
        "routeName": name,
        "streetNames": [],
        "results": [{"length": 1000, "crossTime": seconds}],
        **attrs,
    }


@pytest.mark.parametrize(
    "hov_attrs",
    (
        pytest.param({"minPassengers": 1}, id="min-passengers"),
        pytest.param({"minPassengers": 3, "routeAttr": ["HOV"]}, id="hov-attr"),
        pytest.param({"routeAttr": ["Toll", "HOV"]}, id="hov-attr-with-toll"),
    ),
)
async def test_calc_routes_excludes_hov_routes(hov_attrs: dict, waze: FakeWaze):
    """Passenger-restricted alternatives are not returned when others exist."""
    waze.add(
        ROUTING_URL,
        json={
            "alternatives": [
                {"response": _alternative("hov", 60, **hov_attrs)},
                {"response": _alternative("open", 120, routeAttr=["Toll"])},
                {"response": _alternative("other", 180)},
            ]
        },
    )

    async with route_calculator.WazeRouteCalculator() as client:
        routes = await client.calc_routes(
            "50.0033,8.2623", "50.0841,8.2478", alternatives=3
        )

    assert [route.name for route in routes] == ["open", "other"]


async def test_calc_routes_keeps_hov_routes_when_nothing_else(waze: FakeWaze):
    """Return HOV routes rather than nothing when they are the only ones."""
    waze.add(
        ROUTING_URL,
        json={
            "alternatives": [
                {"response": _alternative("a", 60, minPassengers=2)},
                {"response": _alternative("b", 120, routeAttr=["HOV"])},
            ]
        },
    )

    async with route_calculator.WazeRouteCalculator() as client:
        routes = await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")

    assert [route.name for route in routes] == ["a", "b"]


async def test_get_routes_does_not_request_geometries_or_instructions(
    waze: FakeWaze,
):
    """Omit the flags: Waze treats any value, even "false", as a request for them."""
    get_route_mock = waze.add(
        ROUTING_URL, json={"response": {"results": [], "streetNames": []}}
    )
    async with route_calculator.WazeRouteCalculator() as client:
        await client.get_routes(
            {"lat": 50.0, "lon": 8.2, "bounds": {}},
            {"lat": 50.1, "lon": 8.3, "bounds": {}},
        )

    params = get_route_mock.calls[-1].params
    assert "returnGeometries" not in params
    assert "returnInstructions" not in params
    assert params["returnJSON"] == "true"


async def test_stop_at_bounds_works_without_geometries():
    """Segments keep their `path` point, which stop_at_bounds relies on."""
    segments = [
        {"length": 1000, "crossTime": 60, "path": {"x": 8.0, "y": 50.0}},
        {"length": 2000, "crossTime": 120, "path": {"x": 9.0, "y": 51.0}},
    ]
    bounds = {"left": 7.9, "right": 8.1, "bottom": 49.9, "top": 50.1}
    duration, distance = route_calculator.WazeRouteCalculator()._add_up_route(
        segments, bounds, {}, stop_at_bounds=True
    )
    assert (duration, distance) == (2.0, 2.0)


@pytest.mark.parametrize(
    ("address", "expected"),
    (
        (
            "Costco Wholesale, 1600 Montague Expy, San Jose, CA 95131",
            "1600 Montague Expy, San Jose, CA 95131",
        ),
        (
            "Milpitas Public Library, 160 N Main St, Milpitas, CA 95035, USA",
            "160 N Main St, Milpitas, CA 95035, USA",
        ),
        (
            "Tilly's, Great Mall of the Bay Area, 447 Great Mall Dr, Milpitas, CA 95035",
            "447 Great Mall Dr, Milpitas, CA 95035",
        ),
        ("Home, 123 Main St, Milpitas, CA", "123 Main St, Milpitas, CA"),
        # Nothing to strip.
        ("1600 Montague Expy, San Jose, CA 95131", None),
        ("Costco, San Jose", None),
        ("Googleplex", None),
        ("Luisenstraße 30 65185 Wiesbaden, Germany", None),
        ("Kaiserstraße 30, 55116 Mainz, Germany", None),
        ("10 Downing Street, London SW1A 2AA, UK", None),
        ("Empire State Building, New York", None),
        ("50.0033,8.2623", None),
    ),
)
def test_venue_prefix_match(address: str, expected: str | None):
    """Only a leading venue name before a US-style street address is stripped."""
    stripped = route_calculator.WazeRouteCalculator.VENUE_PREFIX_MATCH.sub(
        "", address
    ).strip()
    assert stripped == (expected or address)


@pytest.mark.parametrize(
    ("address", "expected_query"),
    (
        (
            "Costco Wholesale, 1600 Montague Expy, San Jose, CA 95131",
            "1600 Montague Expy, San Jose, CA 95131",
        ),
        ("Luisenstraße 30 65185 Wiesbaden, Germany", None),
    ),
)
async def test_address_to_coords_strips_venue_prefix(
    address: str, expected_query: str | None, respx_mock: MockRouter
):
    """Send a single autocomplete request using the stripped address."""
    lookup = respx_mock.get("https://gapi.waze.com/autocomplete/q").respond(
        200, json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN
    )

    async with route_calculator.WazeRouteCalculator() as client:
        await client.address_to_coords(address)

    assert lookup.call_count == 1
    assert lookup.calls.last.request.url.params["q"] == (expected_query or address)
