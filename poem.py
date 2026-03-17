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
You are writing a short bilingual weather poem with humor.

Use this forecast data for tomorrow:
{weather_text}

Write one short poem in TWO parts:
- first in English
- then in Danish

Requirements:
1. Compare the weather in the three locations.
2. Mention the differences in temperature, rain, wind, clouds, or humidity.
3. Clearly say which location would be nicest to be in tomorrow for moose hunting
5. The moose hunting part must be humorous, playful, and based only on weather conditions
   such as visibility, mud, wind, comfort, and whether an elk would also prefer the place.
6. Keep the tone warm, witty, and slightly absurd.
7. Do not give real hunting advice.
8. Be concise: around 8–12 lines total.
9. Make the ending memorable and funny.
10. Return plain text only.

Important:
- The poem must explicitly “best for moose hunting”.
- Do not be generic.
- Do not only describe the weather; make it sound like an actual poem.
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