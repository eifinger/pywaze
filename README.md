# pywaze

Asynchronous Waze client for calculating routes and travel times.

Based on [WazeRouteCalculator](https://github.com/kovacsbalu/WazeRouteCalculator)

## Installation

```console
pip install pywaze
```

## Usage

```python
#!/usr/bin/env python3

import asyncio
from pywaze import route_calculator


async def get_time(start: str, end: str) -> float:
    """Return the travel time home."""

    async with route_calculator.WazeRouteCalculator() as client:
        results = await client.calc_all_routes_info(start, end)
        route_time, _ = list(results.values())[0]
        return route_time


start = "50.00332659227126,8.262322651915843"
end = "50.08414976707619,8.247836017342934"

travel_time = asyncio.run(get_time(start, end))

print(travel_time)
```

---

[<img src="https://raw.githubusercontent.com/eifinger/setup-rye/main/docs/images/bmc-button.svg" width=150 height=40 style="margin: 5px"/>](https://www.buymeacoffee.com/eifinger)
[<img src="https://raw.githubusercontent.com/eifinger/setup-rye/main/docs/images/paypal-button.svg" width=150 height=40 style="margin: 5px"/>](https://paypal.me/kevinstillhammer)
