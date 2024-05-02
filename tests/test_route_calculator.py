"""Tests for route_calculator module."""
import pytest
from pywaze import route_calculator
from tests.const import (
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


@pytest.mark.usefixtures("timeout_mock")
async def test_calc_route_info_timeout():
    """Test calc_route_info with timeout."""

    async with route_calculator.WazeRouteCalculator() as client:
        with pytest.raises(route_calculator.WRCTimeoutError):
            await client.calc_routes(
                "50.00332659227126,8.262322651915843",
                "50.08414976707619,8.247836017342934",
            )
