# poem.py
from __future__ import annotations

import os
import sqlite3
from typing import Any

from groq import Groq


def summarize_weather_for_poem(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Build a compact daily summary per location for tomorrow.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            location_name,
            forecast_date,
            ROUND(AVG(temperature_2m), 1) AS avg_temp,
            ROUND(SUM(precipitation), 1) AS total_precipitation,
            ROUND(AVG(wind_speed_10m), 1) AS avg_wind_speed,
            ROUND(AVG(cloud_cover), 1) AS avg_cloud_cover,
            ROUND(AVG(relative_humidity_2m), 1) AS avg_humidity
        FROM weather_forecasts
        GROUP BY location_name, forecast_date
        ORDER BY location_name
        """
    )

    rows = cursor.fetchall()

    summaries = []
    for row in rows:
        summaries.append(
            {
                "location_name": row[0],
                "forecast_date": row[1],
                "avg_temp": row[2],
                "total_precipitation": row[3],
                "avg_wind_speed": row[4],
                "avg_cloud_cover": row[5],
                "avg_humidity": row[6],
            }
        )

    return summaries


def generate_poem(conn: sqlite3.Connection, model: str) -> str:
    """
    Generate a bilingual poem with Groq based on tomorrow's weather.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment.")

    summaries = summarize_weather_for_poem(conn)
    if not summaries:
        raise RuntimeError("No weather summaries found for poem generation.")

    weather_lines = []
    for item in summaries:
        weather_lines.append(
            (
                f"{item['location_name']} on {item['forecast_date']}: "
                f"avg temp {item['avg_temp']}°C, "
                f"precipitation {item['total_precipitation']} mm, "
                f"wind {item['avg_wind_speed']} km/h, "
                f"cloud cover {item['avg_cloud_cover']}%, "
                f"humidity {item['avg_humidity']}%."
            )
        )

    weather_text = "\n".join(weather_lines)

    prompt = f"""
You are writing a short, slightly humorous weather poem.

Use this forecast data for tomorrow:
{weather_text}

Write a short poem that:
1. compares the weather in the three locations,
2. describes the differences clearly,
3. suggests where it would be nicest to be tomorrow,
4. evaluates which location would be best specifically for moose hunting,
5. includes a light, playful, slightly ironic tone,
6. is bilingual: first English, then Danish,
7. is concise and poetic (not too long),
8. clearly states both:
   - the best place overall,
   - and the best place for moose hunting.

Moose hunting references should be humorous and based on weather conditions 
(e.g. visibility, rain, wind, comfort), not technical hunting advice.

Return plain text only.
""".strip()

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You write concise bilingual weather poems."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()