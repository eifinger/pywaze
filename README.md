# pywaze

Asynchronous Waze client for calculating routes and travel times.

Based on [WazeRouteCalculator](https://github.com/kovacsbalu/WazeRouteCalculator)

## Installation

```console
uv add pywaze
```

## Usage

```python
#!/usr/bin/env python3

import asyncio
from pywaze import route_calculator


async def get_time(start: str, end: str) -> float:
    """Return the travel time home."""

    async with route_calculator.WazeRouteCalculator() as client:
        results = await client.calc_routes(start, end)
        first_route = results[0]
        return first_route.duration


start = "50.00332659227126,8.262322651915843"
end = "50.08414976707619,8.247836017342934"

travel_time = asyncio.run(get_time(start, end))

print(travel_time)
```

Use the asynchronous context manager, or call `await client.close()` when finished.
The calculator closes its own HTTPX client and its impersonating session, but
leaves an injected `httpx.AsyncClient` open for its owner to close.
Consumers must close calculators after validation and on unload; closing a shared
HTTPX client does not clean up a calculator's impersonating session.
curl-cffi allocates native resources lazily on the first fallback request, but
once used, its session requires explicit asynchronous cleanup, not garbage collection.

### Address resolving base coordinates

When one or both endpoints are addresses, `calc_routes()` resolves them directly
via Waze's mobile autocomplete API.
You can provide custom base coordinates to bias address results near those coordinates:

```python
await client.calc_routes(start, end, base_coords=(48.137154, 11.576124))
```

If `base_coords` is omitted and exactly one endpoint is already coordinates,
that coordinate endpoint is used automatically as base coordinates for
resolving the address.

---

[<img src="https://raw.githubusercontent.com/eifinger/pywaze/main/docs/images/bmc-button.svg" width=150 height=40 style="margin: 5px"/>](https://www.buymeacoffee.com/eifinger)
[<img src="https://raw.githubusercontent.com/eifinger/pywaze/main/docs/images/paypal-button.svg" width=150 height=40 style="margin: 5px"/>](https://paypal.me/kevinstillhammer)
