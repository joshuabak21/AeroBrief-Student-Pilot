"""Offline tests: use mocked API responses, not live weather/network."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from aviation_data import convert_wind_columns, extract_forecast, search_cities, wind_components


def test_wind_components_aligned_runway():
    headwind, crosswind = wind_components(10, 90, 90)
    assert headwind == pytest.approx(10)
    assert crosswind == pytest.approx(0)


def test_wind_components_crosswind():
    headwind, crosswind = wind_components(12, 180, 90)
    assert headwind == pytest.approx(0, abs=1e-8)
    assert crosswind == pytest.approx(12)


def test_extract_forecast_arrays():
    future = datetime(2090, 1, 1, 0, 0)
    payload = {
        "timezone": "UTC",
        "hourly": {
            "time": [(future + timedelta(hours=i)).isoformat(timespec="minutes") for i in range(3)],
            "temperature_2m": [70, 72, 74],
            "wind_speed_10m": [10, 12, 15],
            "wind_gusts_10m": [14, 17, 19],
            "wind_direction_10m": [90, 180, 270],
            "cloud_cover": [20, 50, 90],
            "precipitation_probability": [0, 10, 45],
            "visibility": [16093.44, 8046.72, 1609.344],
        },
    }
    rows = extract_forecast(payload, hours=2, runway_heading=90, now=datetime(2026, 1, 1))
    assert len(rows) == 2
    assert rows[0]["Visibility (sm)"] == pytest.approx(10)
    assert rows[0]["Headwind (kt)"] == pytest.approx(10)
    assert rows[1]["Crosswind (kt)"] == pytest.approx(12)

    mph_rows, unit = convert_wind_columns(rows, "mph")
    assert unit == "mph"
    assert mph_rows[0]["Wind (kt)"] == pytest.approx(11.51, abs=.01)
    assert rows[0]["Wind (kt)"] == 10  # Does not mutate original


def test_geocoding_json_lookup():
    fake = Mock()
    fake.raise_for_status.return_value = None
    fake.json.return_value = {"results": [{
        "id": 1, "name": "Atlanta", "admin1": "Georgia", "country": "United States",
        "latitude": 33.7, "longitude": -84.4,
    }]}
    with patch("aviation_data.requests.get", return_value=fake) as get:
        found = search_cities("Atlanta")
    assert found[0]["name"] == "Atlanta"
    assert found[0]["lat"] == 33.7
    assert get.call_args.kwargs["timeout"] == 12
