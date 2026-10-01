"""Waze route calculator."""

import logging
import re
from dataclasses import dataclass
from typing import Any, Literal, TypedDict

import httpx
from curl_cffi.requests import AsyncSession, RequestsError
from curl_cffi.requests import Response as CurlResponse
from curl_cffi.requests.exceptions import Timeout as CurlTimeout

logger = logging.getLogger(__name__)


class BaseCoords(TypedDict):
    """Base coordinates."""

    lat: float
    lon: float


class Coords(BaseCoords):
    """Coordinates and bounds."""

    bounds: dict[str, float]


BaseCoordsInput = BaseCoords | str | tuple[float, float]


@dataclass(frozen=True)
class CalcRoutesResponse:
    """The Response from this lib."""

    duration: float
    distance: float
    name: str
    street_names: list[str]


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
    BASE_COORDS: dict[str, BaseCoords] = {
        "US": {"lat": 40.713, "lon": -74.006},
        "NA": {"lat": 40.713, "lon": -74.006},
        "EU": {"lat": 47.498, "lon": 19.040},
        "IL": {"lat": 31.768, "lon": 35.214},
        "AU": {"lat": -35.281, "lon": 149.128},
    }
    AUTOCOMPLETE_URL = "https://gapi.waze.com/autocomplete/q"
    AUTOCOMPLETE_ENVIRONMENTS = {
        "US": "NA",
        "NA": "NA",
        "EU": "ROW",
        "IL": "IL",
        "AU": "ROW",
    }
    ROUTING_SERVERS = {
        "US": "https://routing-livemap-am.waze.com/RoutingManager/routingRequest",
        "NA": "https://routing-livemap-am.waze.com/RoutingManager/routingRequest",
        "EU": "https://routing-livemap-row.waze.com/RoutingManager/routingRequest",
        "IL": "https://routing-livemap-il.waze.com/RoutingManager/routingRequest",
        "AU": "https://routing-livemap-row.waze.com/RoutingManager/routingRequest",
    }
    COORD_MATCH = re.compile(
        r"^([-+]?)([\d]{1,2})(((\.)(\d+)(,)))(\s*)(([-+]?)([\d]{1,3})((\.)(\d+))?)$"
    )

    def __init__(
        self,
        region="EU",
        client: httpx.AsyncClient | None = None,
        timeout: int = 60,
    ):
        self.region = region
        self._owns_client = client is None
        self.client = httpx.AsyncClient(timeout=timeout) if client is None else client
        self.timeout = timeout
        # Waze rejects HTTPX's TLS fingerprint even with browser headers.
        self._impersonating_client: AsyncSession = AsyncSession(impersonate="chrome136")

    def already_coords(self, address: str) -> bool:
        """Already coordinates or address."""

        m = re.search(self.COORD_MATCH, address)
        return m is not None

    async def _ensure_coords(
        self,
        address: str,
        base_coords: BaseCoords | None = None,
    ) -> Coords:
        if self.already_coords(address):
            return self.coords_string_parser(address)
        return await self.address_to_coords(address, base_coords=base_coords)

    def coords_string_parser(self, coords: str) -> Coords:
        """Parse the address string into coordinates to match address_to_coords return object."""

        lat, lon = coords.split(",")
        return {"lat": float(lat.strip()), "lon": float(lon.strip()), "bounds": {}}

    def _normalize_base_coords(self, base_coords: BaseCoordsInput) -> BaseCoords:
        """Normalize supported base coordinate input formats."""

        if isinstance(base_coords, str):
            parsed_coords = self.coords_string_parser(base_coords)
            return {"lat": parsed_coords["lat"], "lon": parsed_coords["lon"]}

        if isinstance(base_coords, tuple):
            return {"lat": float(base_coords[0]), "lon": float(base_coords[1])}

        if isinstance(base_coords, dict):
            return {"lat": float(base_coords["lat"]), "lon": float(base_coords["lon"])}

        raise TypeError("base_coords must be a coords string, tuple, or dict")

    async def address_to_coords(
        self,
        address: str,
        base_coords: BaseCoords | None = None,
    ) -> Coords:
        """Convert address to coordinates using Waze's mobile autocomplete API."""

        base_coords = base_coords or self.BASE_COORDS[self.region]
        try:
            response = await self.client.get(
                self.AUTOCOMPLETE_URL,
                params={
                    "q": address,
                    "e": self.AUTOCOMPLETE_ENVIRONMENTS[self.region],
                    # The mobile client ID works without the website's reCAPTCHA.
                    "c": "wd",
                    "exp": "8",
                    "gxy": "1",
                    "sll": f"{base_coords['lat']},{base_coords['lon']}",
                    "lang": "en",
                },
                headers=self.HEADERS,
                timeout=self.timeout,
            )
        except httpx.TimeoutException as e:
            raise WRCTimeoutError(f"Timeout getting coords for {address}") from e
        payload = self._check_response(response)
        if (
            not isinstance(payload, list)
            or len(payload) < 2
            or not isinstance(payload[1], list)
        ):
            raise WRCError("Invalid autocomplete response")
        try:
            for suggestion in payload[1]:
                if len(suggestion) < 4 or suggestion[3] is None:
                    continue
                place = suggestion[3]
                if place.get("v", "").startswith("advertisement.poi-"):
                    continue
                lat, lon = place.get("y"), place.get("x")
                if lat is not None and lon is not None:
                    # Autocomplete supplies coordinates but no endpoint bounds.
                    return {"lat": float(lat), "lon": float(lon), "bounds": {}}
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            raise WRCError("Invalid autocomplete response") from e
        raise WRCError(f"Cannot get coords for {address}")

    async def get_routes(
        self,
        start: Coords,
        end: Coords,
        vehicle_type: Literal[None, "TAXI", "MOTORCYCLE"] = None,
        avoid_toll_roads: bool = False,
        avoid_subscription_roads: bool = False,
        avoid_ferries: bool = False,
        alternatives: int = 1,
        time_delta: int = 0,
    ) -> list[dict[str, Any]]:
        """Get route data from waze."""

        routing_server = self.ROUTING_SERVERS[self.region]

        route_options = {
            "AVOID_TRAILS": "t",
            "AVOID_TOLL_ROADS": "t" if avoid_toll_roads else "f",
            "AVOID_FERRIES": "t" if avoid_ferries else "f",
        }

        url_options: dict[str, str | int] = {
            "from": f"x:{start['lon']} y:{start['lat']}",
            "to": f"x:{end['lon']} y:{end['lat']}",
            "at": time_delta,
            "returnJSON": "true",
            "returnGeometries": "true",
            "returnInstructions": "true",
            "timeout": 60000,
            "nPaths": alternatives,
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
            response: httpx.Response | CurlResponse = await self.client.get(
                routing_server,
                params=url_options,
                headers=self.HEADERS,
                timeout=self.timeout,
            )
            if response.status_code == 403:
                response = await self._impersonating_client.get(
                    routing_server,
                    params=url_options,
                    headers=self.HEADERS,
                    timeout=self.timeout,
                )
        except (httpx.TimeoutException, CurlTimeout) as e:
            raise WRCTimeoutError("Timeout getting route") from e
        except RequestsError as e:
            raise WRCError("Error getting route") from e
        response_json = self._check_response(response)
        if response_json.get("alternatives"):
            return [alt["response"] for alt in response_json["alternatives"]]
        response_obj = response_json["response"]
        if isinstance(response_obj, list):
            response_obj = response_obj[0]
        return [response_obj]

    @staticmethod
    def _check_response(response: httpx.Response | CurlResponse) -> Any:
        """Check waze server response."""
        if 200 <= response.status_code < 300:
            try:
                response_json = response.json()
                logger.debug("Response is: %s", response_json)
                if "error" in response_json:
                    raise WRCError(response_json.get("error"))
                return response_json
            except ValueError:
                raise WRCError("empty response")
        raise WRCError(response.text)

    def _add_up_route(
        self,
        results: list[dict],
        start_bounds: dict[str, float],
        end_bounds: dict[str, float],
        real_time: bool = True,
        stop_at_bounds: bool = False,
    ) -> tuple[float, float]:
        """Calculate route time and distance."""

        def between(target: float, min: float, max: float) -> bool:
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

    async def calc_routes(
        self,
        start: str,
        end: str,
        vehicle_type: Literal[None, "TAXI", "MOTORCYCLE"] = None,
        avoid_toll_roads: bool = False,
        avoid_subscription_roads: bool = False,
        avoid_ferries: bool = False,
        alternatives: int = 1,
        time_delta: int = 0,
        real_time: bool = True,
        stop_at_bounds: bool = False,
        base_coords: BaseCoordsInput | None = None,
    ) -> list[CalcRoutesResponse]:
        """Get route info with enhanced calculations like total distance."""

        resolved_base_coords = (
            self._normalize_base_coords(base_coords)
            if base_coords is not None
            else None
        )

        start_is_coords = self.already_coords(start)
        end_is_coords = self.already_coords(end)

        if resolved_base_coords is None:
            if start_is_coords and not end_is_coords:
                resolved_base_coords = self._normalize_base_coords(start)
            elif end_is_coords and not start_is_coords:
                resolved_base_coords = self._normalize_base_coords(end)

        start_coords = await self._ensure_coords(
            start, base_coords=resolved_base_coords
        )
        end_coords = await self._ensure_coords(end, base_coords=resolved_base_coords)

        routes = await self.get_routes(
            start_coords,
            end_coords,
            vehicle_type=vehicle_type,
            avoid_toll_roads=avoid_toll_roads,
            avoid_subscription_roads=avoid_subscription_roads,
            avoid_ferries=avoid_ferries,
            alternatives=alternatives,
            time_delta=time_delta,
        )
        result = []
        for route in routes:
            results = route["results" if "results" in route else "result"]
            duration, distance = self._add_up_route(
                results,
                start_coords["bounds"],
                end_coords["bounds"],
                real_time=real_time,
                stop_at_bounds=stop_at_bounds,
            )
            result.append(
                CalcRoutesResponse(
                    distance=distance,
                    duration=duration,
                    name=route.get("routeName", ""),
                    street_names=[
                        name
                        for name in route.get("streetNames", {})
                        if name is not None
                    ],
                )
            )
        return result

    async def close(self) -> None:
        """Close owned clients, leaving an injected HTTPX client open."""
        try:
            if self._owns_client:
                await self.client.aclose()
        finally:
            await self._impersonating_client.close()

    async def __aenter__(self) -> "WazeRouteCalculator":
        """Support asynchronous context manager protocol."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Close owned clients."""
        await self.close()
