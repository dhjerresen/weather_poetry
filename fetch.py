from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from config import FORECAST_DAYS, HOURLY_VARIABLES, LOCATIONS

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def build_weather_params() -> dict[str, Any]:
    """
    Build Open-Meteo parameters for all configured locations.
    """
    return {
        "latitude": [location["latitude"] for location in LOCATIONS],
        "longitude": [location["longitude"] for location in LOCATIONS],
        "hourly": HOURLY_VARIABLES,
        "forecast_days": FORECAST_DAYS,
        "timezone": "auto",
    }


def tomorrow_date_str() -> str:
    """
    Return tomorrow's date in YYYY-MM-DD format (UTC-based).
    """
    tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
    return tomorrow.isoformat()


def fetch_weather() -> list[dict[str, Any]]:
    """
    Fetch hourly weather data for all configured locations and return
    cleaned rows for tomorrow only.
    """
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    client = openmeteo_requests.Client(session=retry_session)

    params = build_weather_params()
    responses = client.weather_api(BASE_URL, params=params)

    if not responses:
        raise RuntimeError("No response returned from Open-Meteo API.")

    target_date = tomorrow_date_str()
    all_rows: list[dict[str, Any]] = []

    for location, response in zip(LOCATIONS, responses):
        hourly = response.Hourly()
        if hourly is None:
            continue

        hourly_data = {
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "precipitation": hourly.Variables(1).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(2).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(3).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(4).ValuesAsNumpy(),
        }

        df = pd.DataFrame(hourly_data)
        df["forecast_date"] = df["time"].dt.strftime("%Y-%m-%d")
        df = df[df["forecast_date"] == target_date]

        for _, row in df.iterrows():
            all_rows.append(
                {
                    "location_name": location["name"],
                    "latitude": float(location["latitude"]),
                    "longitude": float(location["longitude"]),
                    "forecast_date": row["forecast_date"],
                    "forecast_time": row["time"].isoformat(),
                    "temperature_2m": float(row["temperature_2m"]),
                    "precipitation": float(row["precipitation"]),
                    "wind_speed_10m": float(row["wind_speed_10m"]),
                    "cloud_cover": float(row["cloud_cover"]),
                    "relative_humidity_2m": float(row["relative_humidity_2m"]),
                }
            )

    return all_rows


if __name__ == "__main__":
    rows = fetch_weather()
    print(f"Fetched {len(rows)} weather rows")

    if rows:
        print("\nFirst row:")
        for key, value in rows[0].items():
            print(f"  {key}: {value}")