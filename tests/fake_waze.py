"""A fake curl_cffi AsyncSession serving canned Waze responses."""

import json
from dataclasses import dataclass, field
from typing import Any

from curl_cffi.requests import Response as CurlResponse

ROUTING_URL = "https://routing-livemap-row.waze.com/RoutingManager/routingRequest"
AUTOCOMPLETE_URL = "https://gapi.waze.com/autocomplete/q"


def make_response(
    status: int = 200, *, json_body: Any = None, text: str = ""
) -> CurlResponse:
    """Build a curl_cffi response."""
    response = CurlResponse()
    response.status_code = status
    response.content = (
        json.dumps(json_body).encode() if json_body is not None else text.encode()
    )
    return response


@dataclass
class Call:
    """A request made through a fake session."""

    url: str
    params: dict[str, str]
    headers: dict[str, str]
    timeout: float


@dataclass
class FakeRoute:
    """A canned answer for requests to a URL (optionally filtered by params)."""

    url: str
    params: dict[str, str]
    response: CurlResponse | None = None
    error: BaseException | None = None
    calls: list[Call] = field(default_factory=list)

    @property
    def call_count(self) -> int:
        """Return how many requests were answered."""
        return len(self.calls)

    def matches(self, url: str, params: dict[str, str]) -> bool:
        """Return whether a request should be answered by this route."""
        return url == self.url and all(
            params.get(key) == value for key, value in self.params.items()
        )


class FakeSession:
    """Stand-in for curl_cffi.requests.AsyncSession."""

    def __init__(self, server: "FakeWaze", kwargs: dict[str, Any]) -> None:
        self.server = server
        self.kwargs = kwargs
        self.exit_args: list[tuple[Any, Any, Any]] = []

    async def __aenter__(self) -> "FakeSession":
        """Enter the session context."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Record how the session context was exited."""
        self.exit_args.append(args)

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> CurlResponse:
        """Answer a GET request from the registered routes."""
        str_params = {key: str(value) for key, value in (params or {}).items()}
        for route in reversed(self.server.routes):
            if route.matches(url, str_params):
                route.calls.append(Call(url, str_params, headers or {}, timeout or 0))
                if route.error is not None:
                    raise route.error
                assert route.response is not None
                return route.response
        raise AssertionError(f"Unexpected request to {url} with {str_params}")


class FakeWaze:
    """Session factory (patched in for AsyncSession) plus route registry."""

    def __init__(self) -> None:
        self.routes: list[FakeRoute] = []
        self.sessions: list[FakeSession] = []

    def add(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        status: int = 200,
        json: Any = None,
        text: str = "",
        error: BaseException | None = None,
    ) -> FakeRoute:
        """Register an answer for a URL, most recent registration wins."""
        route = FakeRoute(
            url,
            params or {},
            response=None
            if error
            else make_response(status, json_body=json, text=text),
            error=error,
        )
        self.routes.append(route)
        return route

    def __call__(self, **kwargs: Any) -> FakeSession:
        """Create a session, like AsyncSession(...)."""
        session = FakeSession(self, kwargs)
        self.sessions.append(session)
        return session
