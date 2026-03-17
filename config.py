from __future__ import annotations

LOCATIONS = [
    {
        "name": "Gjøl",
        "latitude": 57.0684,
        "longitude": 9.7199,
    },
    {
        "name": "Hanstholm",
        "latitude": 57.1155,
        "longitude": 8.6172,
    },
    {
        "name": "Frederikshavn",
        "latitude": 57.4407,
        "longitude": 10.5366,
    },
]

HOURLY_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
    "cloud_cover",
    "relative_humidity_2m",
]

FORECAST_DAYS = 2

SQL_DB_PATH = "data/weather.db"
LATEST_WEATHER_JSON = "outputs/latest_weather.json"
LATEST_POEM_TXT = "outputs/latest_poem.txt"
RUN_SUMMARY_JSON = "outputs/run_summary.json"

GROQ_MODEL = "llama-3.3-70b-versatile"