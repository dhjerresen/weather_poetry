from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import (
    GROQ_MODEL,
    LATEST_POEM_TXT,
    LATEST_WEATHER_JSON,
    RUN_SUMMARY_JSON,
)
from fetch import fetch_weather
from poem import generate_poem, summarize_weather_for_poem
from store_sql import init_db, store_weather


def main() -> None:
    print("Starting weather pipeline...")

    # 1. Fetch weather
    weather_rows = fetch_weather()
    fetched_count = len(weather_rows)
    print(f"Fetched {fetched_count} weather rows")

    if not weather_rows:
        print("No weather data fetched — exiting.")
        return

    # 2. Store in SQLite
    conn = init_db()
    sql_inserted = store_weather(conn, weather_rows)
    print(f"Inserted {sql_inserted} new rows into SQLite")

    # 3. Generate poem
    poem_text = generate_poem(conn, GROQ_MODEL)
    print("Generated poem")

    # 4. Build weather summary
    weather_summary = summarize_weather_for_poem(conn)

    # 5. Ensure output folders exist
    Path("outputs").mkdir(exist_ok=True)
    Path("docs").mkdir(exist_ok=True)

    # 6. Save JSON/text outputs
    with open(LATEST_WEATHER_JSON, "w", encoding="utf-8") as f:
        json.dump(weather_summary, f, indent=4, ensure_ascii=False)

    with open(LATEST_POEM_TXT, "w", encoding="utf-8") as f:
        f.write(poem_text)

    # 7. Save docs/data.json for GitHub Pages
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "poem": poem_text,
                "weather": weather_summary,
            },
            f,
            indent=4,
            ensure_ascii=False,
        )

    # 8. Save run summary
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "weather_rows_fetched": fetched_count,
        "sql_inserted": sql_inserted,
        "locations": [item["location_name"] for item in weather_summary],
    }

    with open(RUN_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    conn.close()

    print("Run summary written")
    print("Pipeline complete.")


if __name__ == "__main__":
    main()