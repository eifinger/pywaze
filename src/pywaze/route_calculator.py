"""Waze route calculator."""

from typing import Any, Literal
import httpx
import re


class WRCError(Exception):
    """Waze Route Calculator Error."""


class WRCTimeoutError(WRCError):
    """Waze Route Calculator Timeout Error."""


class WazeRouteCalculator:
    """Calculate actual route time and distance with Waze API."""

    WAZE_URL = "https://www.waze.com/"
    HEADERS = {
        "User-Agent": "pywaze",
        "referer": WAZE_URL,
    }
    BASE_COORDS = {
        "US": {"lat": 40.713, "lon": -74.006},
        "NA": {"lat": 40.713, "lon": -74.006},
        "EU": {"lat": 47.498, "lon": 19.040},
        "IL": {"lat": 31.768, "lon": 35.214},
        "AU": {"lat": -35.281, "lon": 149.128},
    }
    COORD_SERVERS = {
        "US": "SearchServer/mozi",
        "NA": "SearchServer/mozi",
        "EU": "row-SearchServer/mozi",
        "IL": "il-SearchServer/mozi",
        "AU": "row-SearchServer/mozi",
    }
    ROUTING_SERVERS = {
        "US": "RoutingManager/routingRequest",
        "NA": "RoutingManager/routingRequest",
        "EU": "row-RoutingManager/routingRequest",
        "IL": "il-RoutingManager/routingRequest",
        "AU": "row-RoutingManager/routingRequest",
    }
    COORD_MATCH = re.compile(
        r"^([-+]?)([\d]{1,2})(((\.)(\d+)(,)))(\s*)(([-+]?)([\d]{1,3})((\.)(\d+))?)$"
    )

    def __init__(
        self,
        region="EU",
        client: httpx.AsyncClient | None = None,
        timeout: int = 10,
    ):
        self.region = region
        self.client = client
        self.timeout = timeout
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=timeout)

    def already_coords(self, address: str) -> bool:
        """Already coordinates or address."""

        m = re.search(self.COORD_MATCH, address)
        return m is not None

    async def _ensure_coords(self, address: str) -> dict[str, Any]:
        coords = {}
        if self.already_coords(address):
            coords = self.coords_string_parser(address)
        else:
            coords = await self.address_to_coords(address)
        return coords

    def coords_string_parser(self, coords: str) -> dict[str, Any]:
        """Parse the address string into coordinates to match address_to_coords return object."""

        lat, lon = coords.split(",")
        return {"lat": lat.strip(), "lon": lon.strip(), "bounds": {}}

    async def address_to_coords(self, address: str) -> dict[str, Any]:
        """Convert address to coordinates."""

        base_coords = self.BASE_COORDS[self.region]
        get_cord = self.COORD_SERVERS[self.region]
        url_options = {
            "q": address,
            "lang": "eng",
            "origin": "livemap",
            "lat": base_coords["lat"],
            "lon": base_coords["lon"],
        }

        try:
            response: httpx.Response = await self.client.get(
                self.WAZE_URL + get_cord,
                params=url_options,
                headers=self.HEADERS,
                timeout=self.timeout,
            )
        except httpx.TimeoutException as e:
            raise WRCTimeoutError("Timeout getting coords for %s" % address) from e
        for response_json in response.json():
            if response_json.get("city"):
                lat = response_json["location"]["lat"]
                lon = response_json["location"]["lon"]
                bounds = response_json["bounds"]  # sometimes the coords don't match up
                if bounds is not None:
                    bounds["top"], bounds["bottom"] = max(
                        bounds["top"], bounds["bottom"]
                    ), min(bounds["top"], bounds["bottom"])
                    bounds["left"], bounds["right"] = min(
                        bounds["left"], bounds["right"]
                    ), max(bounds["left"], bounds["right"])
                else:
                    bounds = {}
                return {"lat": lat, "lon": lon, "bounds": bounds}
        raise WRCError("Cannot get coords for %s" % address)

    async def get_route(
        self,
        start: dict[str, Any],
        end: dict[str, Any],
        vehicle_type: Literal[None, "TAXI", "MOTORCYCLE"] = None,
        avoid_toll_roads: bool = False,
        avoid_subscription_roads: bool = False,
        avoid_ferries: bool = False,
        npaths: int = 1,
        time_delta: int = 0,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get route data from waze."""

        routing_server = self.ROUTING_SERVERS[self.region]

        route_options = {
            "AVOID_TRAILS": "t",
            "AVOID_TOLL_ROADS": "t" if avoid_toll_roads else "f",
            "AVOID_FERRIES": "t" if avoid_ferries else "f",
        }

        url_options = {
            "from": f"x:{start['lon']} y:{start['lat']}",
            "to": f"x:{end['lon']} y:{end['lat']}",
            "at": time_delta,
            "returnJSON": "true",
            "returnGeometries": "true",
            "returnInstructions": "true",
            "timeout": 60000,
            "nPaths": npaths,
            "options": ",".join(
                f"{opt}:{value}" for (opt, value) in route_options.items()
            ),
        }
        if vehicle_type:
            url_options["vehicleType"] = vehicle_type.upper()
        # Handle vignette system in Europe. Defaults to false (show all routes)
        if avoid_subscription_roads is False:
            url_options["subscription"] = "*"

        try:
            response: httpx.Response = await self.client.get(
                self.WAZE_URL + routing_server,
                params=url_options,
                headers=self.HEADERS,
                timeout=self.timeout,
            )
        except httpx.TimeoutException as e:
            raise WRCTimeoutError("Timeout getting route") from e
        response_json = self._check_response(response)
        if response_json:
            if "error" in response_json:
                raise WRCError(response_json.get("error"))
            else:
                if response_json.get("alternatives"):
                    return [alt["response"] for alt in response_json["alternatives"]]
                response_obj = response_json["response"]
                if isinstance(response_obj, list):
                    response_obj = response_obj[0]
                if npaths > 1:
                    return [response_obj]
                return response_obj
        else:
            raise WRCError("empty response")

    @staticmethod
    def _check_response(response: httpx.Response) -> Any | None:
        """Check waze server response."""
        if response.is_success:
            try:
                return response.json()
            except ValueError:
                return None

    def _add_up_route(
        self, results, start_bounds, end_bounds, real_time=True, stop_at_bounds=False
    ):
        """Calculate route time and distance."""

        def between(target, min, max):
            return target > min and target < max

        time = 0
        distance = 0
        for segment in results:
            if stop_at_bounds and segment.get("path"):
                x = segment["path"]["x"]
                y = segment["path"]["y"]
                if (
                    between(
                        x, start_bounds.get("left", 0), start_bounds.get("right", 0)
                    )
                    or between(x, end_bounds.get("left", 0), end_bounds.get("right", 0))
                ) and (
                    between(
                        y, start_bounds.get("bottom", 0), start_bounds.get("top", 0)
                    )
                    or between(y, end_bounds.get("bottom", 0), end_bounds.get("top", 0))
                ):
                    continue
            if "crossTime" in segment:
                time += segment[
                    "crossTime" if real_time else "crossTimeWithoutRealTime"
                ]
            else:
                time += segment[
                    "cross_time" if real_time else "cross_time_without_real_time"
                ]
            distance += segment["length"]
        route_time = time / 60.0
        route_distance = distance / 1000.0
        return route_time, route_distance

    async def calc_route_info(
        self,
        start: dict[str, Any],
        end: dict[str, Any],
        vehicle_type: Literal[None, "TAXI", "MOTORCYCLE"] = None,
        avoid_toll_roads: bool = False,
        avoid_subscription_roads: bool = False,
        avoid_ferries: bool = False,
        npaths: int = 1,
        time_delta: int = 0,
        real_time: bool = True,
        stop_at_bounds: bool = False,
    ):
        """Calculate best route info."""

        start = await self._ensure_coords(start)
        end = await self._ensure_coords(end)

        route = await self.get_route(
            start,
            end,
            vehicle_type=vehicle_type,
            avoid_toll_roads=avoid_toll_roads,
            avoid_subscription_roads=avoid_subscription_roads,
            avoid_ferries=avoid_ferries,
            npaths=npaths,
            time_delta=time_delta,
        )
        results = route["results" if "results" in route else "result"]
        route_time, route_distance = self._add_up_route(
            results,
            start["bounds"],
            end["bounds"],
            real_time=real_time,
            stop_at_bounds=stop_at_bounds,
        )
        return route_time, route_distance

    async def calc_all_routes_info(
        self,
        start: dict[str, Any],
        end: dict[str, Any],
        vehicle_type: Literal[None, "TAXI", "MOTORCYCLE"] = None,
        avoid_toll_roads: bool = False,
        avoid_subscription_roads: bool = False,
        avoid_ferries: bool = False,
        npaths: int = 3,
        time_delta: int = 0,
        real_time=True,
        stop_at_bounds=False,
    ):
        """Calculate all route infos."""

        start = await self._ensure_coords(start)
        end = await self._ensure_coords(end)

        routes = await self.get_route(
            start,
            end,
            vehicle_type=vehicle_type,
            avoid_toll_roads=avoid_toll_roads,
            avoid_subscription_roads=avoid_subscription_roads,
            avoid_ferries=avoid_ferries,
            npaths=npaths,
            time_delta=time_delta,
        )
        try:
            results = {
                "{}-{}".format(
                    "".join(route.get("routeType", [])[:1]),
                    route.get("shortRouteName", "unknown"),
                ): self._add_up_route(
                    route["results" if "results" in route else "result"],
                    start["bounds"],
                    end["bounds"],
                    real_time=real_time,
                    stop_at_bounds=stop_at_bounds,
                )
                for route in routes
            }
        except KeyError as e:
            raise WRCError("wrong response") from e
        return results

    async def close(self):
        """Close the client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Support asynchronous context manager protocol."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Close the client."""
        await self.close()
