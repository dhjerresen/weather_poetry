from __future__ import annotations

from typing import Any

import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests

from config import LATITUDES, LONGITUDES, FORECAST_DAYS

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def build_weather_params() -> dict[str, Any]:
    """
    Build the Open-Meteo API parameters for multiple locations.
    """
    return {
        "latitude": LATITUDES,
        "longitude": LONGITUDES,
        "hourly": [
            "wind_speed_10m",
            "cloud_cover",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
        ],
        "forecast_days": FORECAST_DAYS,
    }


def fetch_weather() -> list[dict[str, Any]]:
    """
    Fetch hourly weather data from Open-Meteo for multiple locations
    and return them as cleaned dictionaries.
    """
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    client = openmeteo_requests.Client(session=retry_session)

    params = build_weather_params()
    responses = client.weather_api(BASE_URL, params=params)

    if not responses:
        raise RuntimeError("No response returned from Open-Meteo API.")

    weather_data: list[dict[str, Any]] = []

    for response in responses:
        hourly = response.Hourly()
        if hourly is None:
            continue

        # The order must match params["hourly"]
        hourly_wind_speed_10m = hourly.Variables(0).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
        hourly_temperature_2m = hourly.Variables(2).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(3).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            ),
            "wind_speed_10m": hourly_wind_speed_10m,
            "cloud_cover": hourly_cloud_cover,
            "temperature_2m": hourly_temperature_2m,
            "relative_humidity_2m": hourly_relative_humidity_2m,
            "precipitation": hourly_precipitation,
        }

        df = pd.DataFrame(data=hourly_data)

        for _, row in df.iterrows():
            weather_data.append(
                {
                    "latitude": float(response.Latitude()),
                    "longitude": float(response.Longitude()),
                    "elevation": float(response.Elevation()),
                    "utc_offset_seconds": int(response.UtcOffsetSeconds()),
                    "time": row["time"].isoformat(),
                    "wind_speed_10m": float(row["wind_speed_10m"]),
                    "cloud_cover": float(row["cloud_cover"]),
                    "temperature_2m": float(row["temperature_2m"]),
                    "relative_humidity_2m": float(row["relative_humidity_2m"]),
                    "precipitation": float(row["precipitation"]),
                }
            )

    return weather_data


if __name__ == "__main__":
    weather = fetch_weather()
    print(f"Fetched {len(weather)} hourly weather rows")

    if weather:
        print("\nFirst row:")
        for key, value in weather[0].items():
            print(f"  {key}: {value}")