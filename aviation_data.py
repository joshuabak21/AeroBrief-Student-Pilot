"""API and weather calculations for AeroBrief's student-pilot data page.

All forecast processing happens in Python; no LLM is used for data analysis.
Weather data is modeled guidance, not an official aviation briefing.
"""

from datetime import datetime
from math import cos, radians, sin
from zoneinfo import ZoneInfo

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# These preset coordinates identify airfields; they are not weather-station readings.
AIRPORTS = {
    "KATL · Atlanta, GA": {"name": "Atlanta / KATL", "lat": 33.6407, "lon": -84.4277},
    "KDAB · Daytona Beach, FL": {"name": "Daytona Beach / KDAB", "lat": 29.1799, "lon": -81.0581},
    "KPHX · Phoenix, AZ": {"name": "Phoenix / KPHX", "lat": 33.4352, "lon": -112.0101},
    "KDEN · Denver, CO": {"name": "Denver / KDEN", "lat": 39.8561, "lon": -104.6737},
    "KSEA · Seattle, WA": {"name": "Seattle / KSEA", "lat": 47.4502, "lon": -122.3088},
    "KMIA · Miami, FL": {"name": "Miami / KMIA", "lat": 25.7954, "lon": -80.2906},
}

HOURLY_FIELDS = (
    "temperature_2m",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "cloud_cover",
    "precipitation_probability",
    "visibility",
)


def search_cities(query):
    """Return matching cities from Open-Meteo's geocoding JSON API."""
    query = query.strip()
    if len(query) < 2:
        return []
    response = requests.get(
        GEOCODING_URL,
        params={"name": query, "count": 8, "language": "en", "format": "json"},
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()
    return [
        {
            "id": place.get("id"),
            "name": place.get("name", "Unknown"),
            "region": place.get("admin1", ""),
            "country": place.get("country", ""),
            "lat": float(place["latitude"]),
            "lon": float(place["longitude"]),
        }
        for place in payload.get("results", [])
        if "latitude" in place and "longitude" in place
    ]


def get_forecast(latitude, longitude, temperature_unit="fahrenheit"):
    """Fetch hourly forecast data for a location, with wind in knots."""
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(HOURLY_FIELDS),
            "timezone": "auto",
            "forecast_days": 4,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": "kn",
        },
        timeout=18,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or "hourly" not in payload:
        raise ValueError("The forecast API did not provide hourly weather data.")
    return payload


def wind_components(wind_speed_knots, wind_from_degrees, runway_heading_degrees):
    """Return headwind (negative means tailwind) and absolute crosswind, in kt."""
    delta = radians(wind_from_degrees - runway_heading_degrees)
    headwind = wind_speed_knots * cos(delta)
    crosswind = abs(wind_speed_knots * sin(delta))
    return headwind, crosswind


def extract_forecast(payload, hours=24, runway_heading=90, now=None):
    """Transform parallel Open-Meteo arrays into row dictionaries.

    Hour timestamps are local to the timezone returned by the API. Only current
    and future hours are included. Values missing from the API are kept as None.
    """
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    timezone = payload.get("timezone") or "UTC"
    if now is None:
        try:
            local_now = datetime.now(ZoneInfo(timezone))
        except (KeyError, ValueError):
            local_now = datetime.now(ZoneInfo("UTC"))
    else:
        local_now = now
    current_hour = local_now.replace(minute=0, second=0, microsecond=0, tzinfo=None)

    rows = []
    for index, hour_text in enumerate(times):
        stamp = datetime.fromisoformat(hour_text)
        if stamp < current_hour:
            continue

        values = {}
        for field in HOURLY_FIELDS:
            series = hourly.get(field) or []
            values[field] = series[index] if index < len(series) else None

        speed = values["wind_speed_10m"]
        direction = values["wind_direction_10m"]
        headwind, crosswind = (None, None)
        if speed is not None and direction is not None:
            headwind, crosswind = wind_components(
                float(speed), float(direction), float(runway_heading)
            )

        visibility = values["visibility"]
        visibility_miles = float(visibility) / 1609.344 if visibility is not None else None

        rows.append({
            "Local time": stamp,
            "Wind (kt)": speed,
            "Gust (kt)": values["wind_gusts_10m"],
            "Wind direction (°)": direction,
            "Cloud cover (%)": values["cloud_cover"],
            "Rain chance (%)": values["precipitation_probability"],
            "Visibility (sm)": round(visibility_miles, 2) if visibility_miles is not None else None,
            "Temperature": values["temperature_2m"],
            "Headwind (kt)": round(headwind, 2) if headwind is not None else None,
            "Crosswind (kt)": round(crosswind, 2) if crosswind is not None else None,
        })
        if len(rows) >= hours:
            break

    if not rows:
        raise ValueError("There are no forecast hours available for this location.")
    return rows


def convert_wind_columns(rows, wind_unit):
    """Return copied rows with wind values converted for presentation."""
    if wind_unit == "knots":
        return [dict(row) for row in rows], "kt"
    if wind_unit != "mph":
        raise ValueError("Unsupported wind unit")
    converted = []
    for row in rows:
        new = dict(row)
        for name in ("Wind (kt)", "Gust (kt)", "Headwind (kt)", "Crosswind (kt)"):
            if new[name] is not None:
                new[name] = round(float(new[name]) * 1.15077945, 2)
        converted.append(new)
    return converted, "mph"
