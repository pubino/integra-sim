"""The original IntegrationCanvas function, midpoint rectangles, and trapezoids."""

import json
from math import exp, isfinite, pow
from typing import cast

Point = tuple[float, float]
Result = tuple[float, float, list[Point], list[Point], list[float]]
CURVE_PANELS = 1000


def integrate(parameters: str) -> Result:
    values = json.loads(parameters, parse_int=float)
    if (
        not isinstance(values, list)
        or len(values) != 6
        or not all(type(value) is float and isfinite(value) for value in values)
    ):
        raise ValueError("Enter finite numbers for all parameters.")
    start, end, panels, a, b, power = cast(list[float], values)
    if not (panels.is_integer() and 1 <= panels <= 1000):
        raise ValueError("Use 1 to 1,000 panels.")
    if not power.is_integer() or not -1000 <= power <= 1000:
        raise ValueError("Use a whole-number exponent from −1,000 to 1,000.")
    if b == 0:
        raise ValueError("Choose a nonzero value for b.")
    if power < 0 and min(start, end) <= 0 <= max(start, end):
        raise ValueError("A negative exponent requires an interval that excludes zero.")
    span = end - start
    if not isfinite(span):
        raise ValueError("The interval exceeds the numerical range.")

    exponent = int(power)

    def function(x: float) -> float:
        value = a * pow(x, exponent) * exp(-x * x / b)
        if not isfinite(value):
            raise ValueError(
                "The function exceeds the numerical range on this interval."
            )
        return value

    # The Java routine sums trapezoid interiors first, then the two half endpoints.
    count = int(panels)
    dx = span / count
    rectangles, trapezoids = 0.0, 0.0
    edges: list[Point] = []
    heights: list[float] = []
    try:
        for index in range(count):
            x = start + index * dx
            edge = function(x)
            height = function(x + dx / 2)
            edges.append((x, edge))
            heights.append(height)
            rectangles += height
            if index:
                trapezoids += edge
        edges.append((end, function(end)))
        trapezoids += edges[0][1] / 2
        trapezoids += edges[-1][1] / 2
        midpoint_area, trapezoid_area = rectangles * dx, trapezoids * dx
        if not (isfinite(midpoint_area) and isfinite(trapezoid_area)):
            raise ValueError("The integral exceeds the numerical range.")
        curve_dx = span / CURVE_PANELS
        curve = []
        for index in range(CURVE_PANELS + 1):
            x = start + index * curve_dx
            curve.append((x, function(x)))
    except OverflowError as error:
        raise ValueError(
            "The function exceeds the numerical range on this interval."
        ) from error
    return midpoint_area, trapezoid_area, curve, edges, heights
