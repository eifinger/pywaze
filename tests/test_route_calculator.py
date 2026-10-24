"""Tests for route_calculator module."""

from unittest.mock import AsyncMock, Mock, call

from curl_cffi.requests import RequestsError
from curl_cffi.requests import Response as CurlResponse
from curl_cffi.requests.exceptions import Timeout as CurlTimeout
from httpx import AsyncClient, Response
import pytest
from pywaze import route_calculator
from respx import MockRouter
from tests.const import (
    ADDRESS_TO_COORDS_RESPONSE_WIESBADEN,
    EMPTY_ROUTE_NAME_RESPONSE,
    GET_ROUTE_RESPONSE_ADDRESSES,
    GET_ROUTE_RESPONSE_COORDS,
    GET_ALL_ROUTES_RESPONSE,
)


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


async def test_calc_routes_uses_custom_base_coords_for_address_lookup(
    respx_mock: MockRouter,
):
    """Use explicitly provided base coordinates for address resolving."""

    route_response = {
        "response": {
            "results": [{"length": 1000, "crossTime": 60}],
            "streetNames": [],
        }
    }
    respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(200, json=route_response)

    coords_lookup_route = respx_mock.route(
        url="https://gapi.waze.com/autocomplete/q",
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
    ).mock(return_value=Response(200, json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN))

    async with route_calculator.WazeRouteCalculator() as client:
        await client.calc_routes(
            "50.00332659227126,8.262322651915843",
            "Luisenstraße 30 65185 Wiesbaden, Germany",
            base_coords=(48.137154, 11.576124),
        )

    request_params = coords_lookup_route.calls.last.request.url.params
    assert request_params["sll"] == "48.137154,11.576124"


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
    respx_mock: MockRouter,
):
    """Use coordinate endpoint as base coords when only one side is an address."""

    route_response = {
        "response": {
            "results": [{"length": 1000, "crossTime": 60}],
            "streetNames": [],
        }
    }
    respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(200, json=route_response)

    coords_lookup_route = respx_mock.route(
        url="https://gapi.waze.com/autocomplete/q",
        params={"q": "Luisenstraße 30 65185 Wiesbaden, Germany"},
    ).mock(return_value=Response(200, json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN))

    async with route_calculator.WazeRouteCalculator() as client:
        await client.calc_routes(start, end)

    request_params = coords_lookup_route.calls.last.request.url.params
    assert request_params["sll"] == f"{expected_lat},{expected_lon}"


async def test_routing_falls_back_on_403(
    respx_mock: MockRouter, fallback_session_factory: Mock
):
    """Retry an HTTPX 403 with curl_cffi and return the fallback route."""
    url = route_calculator.WazeRouteCalculator.ROUTING_SERVERS["EU"]
    blocked = respx_mock.get(url).respond(403)
    response = CurlResponse()
    response.status_code = 200
    response.content = b'{"response": {"results": [{"length": 2400, "crossTime": 90}]}}'
    session = fallback_session_factory.return_value
    session.get.return_value = response

    async with route_calculator.WazeRouteCalculator(timeout=17) as client:
        routes = await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")
        session.__aexit__.assert_awaited_once_with(None, None, None)

    assert routes == [route_calculator.CalcRoutesResponse(1.5, 2.4, "", [])]
    assert blocked.call_count == 1
    fallback_session_factory.assert_called_once_with(impersonate="chrome")
    session.get.assert_awaited_once()
    assert session.get.call_args.args == (url,)
    assert {
        key: str(value) for key, value in session.get.call_args.kwargs["params"].items()
    } == dict(blocked.calls.last.request.url.params)
    assert session.get.call_args.kwargs["headers"] == client.HEADERS
    assert session.get.call_args.kwargs["timeout"] == 17


@pytest.mark.parametrize("lookup", (False, True), ids=("routing", "address"))
async def test_fallback_uses_fresh_session_per_request(
    lookup: bool, respx_mock: MockRouter, fallback_session_factory: Mock
):
    """Use separate sessions for repeated requests on the same calculator."""
    url = (
        route_calculator.WazeRouteCalculator.AUTOCOMPLETE_URL
        if lookup
        else route_calculator.WazeRouteCalculator.ROUTING_SERVERS["EU"]
    )
    blocked = respx_mock.get(url).respond(403)
    sessions = [fallback_session_factory.return_value, AsyncMock()]
    fallback_session_factory.side_effect = sessions
    for session in sessions:
        session.__aenter__.return_value = session
        session.get.return_value = Response(
            200,
            json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN
            if lookup
            else {"response": {"results": [{"length": 2400, "crossTime": 90}]}},
        )

    async with route_calculator.WazeRouteCalculator(timeout=23) as client:
        fallback_session_factory.assert_not_called()
        for session in sessions:
            if lookup:
                coords = await client.address_to_coords(
                    "Wiesbaden", base_coords={"lat": 48.1, "lon": 11.6}
                )
                assert coords == {
                    "lat": 50.07912063598633,
                    "lon": 8.240204811096191,
                    "bounds": {},
                }
                assert session.get.call_args.kwargs["params"]["sll"] == "48.1,11.6"
            else:
                routes = await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")
                assert routes == [route_calculator.CalcRoutesResponse(1.5, 2.4, "", [])]
            session.get.assert_awaited_once()
            assert session.get.call_args.args == (url,)
            assert session.get.call_args.kwargs["headers"] == client.HEADERS
            assert session.get.call_args.kwargs["timeout"] == 23
            assert {
                key: str(value)
                for key, value in session.get.call_args.kwargs["params"].items()
            } == dict(blocked.calls.last.request.url.params)
            session.__aexit__.assert_awaited_once_with(None, None, None)

    assert blocked.call_count == 2
    assert fallback_session_factory.call_args_list == [call(impersonate="chrome")] * 2


@pytest.mark.parametrize("lookup", (False, True), ids=("routing", "address"))
@pytest.mark.parametrize("status", (200, 500))
async def test_fallback_only_on_403(
    lookup: bool, status: int, respx_mock: MockRouter, fallback_session_factory: Mock
):
    """Do not create fallback sessions for success or other HTTP errors."""
    url = (
        route_calculator.WazeRouteCalculator.AUTOCOMPLETE_URL
        if lookup
        else route_calculator.WazeRouteCalculator.ROUTING_SERVERS["EU"]
    )
    respx_mock.get(url).respond(
        status,
        json=ADDRESS_TO_COORDS_RESPONSE_WIESBADEN if lookup else {"response": {}},
    )
    async with route_calculator.WazeRouteCalculator() as client:
        request = (
            client.address_to_coords("Wiesbaden")
            if lookup
            else client.get_routes(
                {"lat": 50.0, "lon": 8.2, "bounds": {}},
                {"lat": 50.1, "lon": 8.3, "bounds": {}},
            )
        )
        if status == 200:
            await request
        else:
            with pytest.raises(route_calculator.WRCError):
                await request
    fallback_session_factory.assert_not_called()


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
        (
            Response(403, text="still blocked"),
            route_calculator.WRCError,
            "still blocked",
        ),
    ),
)
async def test_fallback_errors_close_session(
    lookup: bool,
    failure,
    expected_error,
    message: str,
    respx_mock: MockRouter,
    fallback_session_factory: Mock,
):
    """Map fallback failures to public errors and exit the session immediately."""
    url = (
        route_calculator.WazeRouteCalculator.AUTOCOMPLETE_URL
        if lookup
        else route_calculator.WazeRouteCalculator.ROUTING_SERVERS["EU"]
    )
    respx_mock.get(url).respond(403)
    session = fallback_session_factory.return_value
    if isinstance(failure, Exception):
        session.get.side_effect = failure
    else:
        session.get.return_value = failure
    async with route_calculator.WazeRouteCalculator() as client:
        with pytest.raises(expected_error, match=message) as exc_info:
            if lookup:
                await client.address_to_coords("Wiesbaden")
            else:
                await client.calc_routes("50.0033,8.2623", "50.0841,8.2478")
        session.__aexit__.assert_awaited_once()
        if isinstance(failure, Exception):
            assert exc_info.value.__cause__ is failure
            assert session.__aexit__.call_args.args[1] is failure
        else:
            session.__aexit__.assert_awaited_once_with(None, None, None)
    fallback_session_factory.assert_called_once_with(impersonate="chrome")


@pytest.mark.parametrize("injected", (False, True))
async def test_close_respects_client_ownership(
    injected: bool, fallback_session_factory: Mock
):
    """Close owned clients but leave an injected HTTPX client open."""
    async with AsyncClient() as shared_client:
        async with route_calculator.WazeRouteCalculator(
            client=shared_client if injected else None
        ) as calculator:
            if injected:
                assert calculator.client is shared_client
            assert not calculator.client.is_closed

        assert calculator.client.is_closed is (not injected)
        assert not shared_client.is_closed
        fallback_session_factory.assert_not_called()


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
async def test_calc_routes_excludes_hov_routes(hov_attrs: dict, respx_mock: MockRouter):
    """Passenger-restricted alternatives are not returned when others exist."""
    respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(
        200,
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


async def test_calc_routes_keeps_hov_routes_when_nothing_else(
    respx_mock: MockRouter,
):
    """Return HOV routes rather than nothing when they are the only ones."""
    respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(
        200,
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
    respx_mock: MockRouter,
):
    """Omit the flags: Waze treats any value, even "false", as a request for them."""
    get_route_mock = respx_mock.get(
        "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
    ).respond(200, json={"response": {"results": [], "streetNames": []}})
    async with route_calculator.WazeRouteCalculator() as client:
        await client.get_routes(
            {"lat": 50.0, "lon": 8.2, "bounds": {}},
            {"lat": 50.1, "lon": 8.3, "bounds": {}},
        )

    params = get_route_mock.calls.last.request.url.params
    assert "returnGeometries" not in params
    assert "returnInstructions" not in params
    assert params["returnJSON"] == "true"


async def test_stop_at_bounds_works_without_geometries(respx_mock: MockRouter):
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
