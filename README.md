# Automated Weather Pipeline with GitHub Pages

This project implements a small automated data pipeline that collects weather forecasts, stores them in a database, generates a bilingual poem using an LLM, and publishes the result as a website using GitHub Pages.

The pipeline runs automatically using GitHub Actions.

---

## Project Overview

The pipeline performs the following steps:

1. Fetch weather forecast data from the Open-Meteo API
2. Store the data in a SQLite database
3. Generate a bilingual poem using the Groq API
4. Publish the results on a GitHub Pages website

The system runs automatically every day.

---

## Technologies Used

* Python
* Open-Meteo API
* SQLite
* Groq API (LLM)
* GitHub Actions
* GitHub Pages

---

## Locations

The pipeline fetches weather data for three locations:

* Birthplace
* Last residence before Aalborg
* Aalborg

(These are defined in `config.py`.)

---

## Weather Variables

The following weather variables are used:

* Temperature (°C)
* Precipitation (mm)
* Wind speed (km/h)
* Cloud cover (%)
* Relative humidity (%)

---

## Project Structure

```
.
├── config.py
├── fetch.py
├── store_sql.py
├── poem.py
├── run_pipeline.py
├── requirements.txt
│
├── data/
│   └── weather.db
│
├── outputs/
│   ├── latest_weather.json
│   ├── latest_poem.txt
│   └── run_summary.json
│
├── docs/
│   ├── index.html
│   └── data.json
│
└── .github/
    └── workflows/
        └── weather.yml
```

---

## How It Works

### 1. Fetch Data

The script `fetch.py` retrieves hourly weather forecasts from Open-Meteo for all locations and filters data for **tomorrow**.

### 2. Store Data

The data is stored in a local SQLite database (`data/weather.db`) using `store_sql.py`.

### 3. Generate Poem

`poem.py` summarizes the weather and uses the Groq API to generate a short poem:

* compares the locations
* describes differences
* suggests the best place to be
* written in English and Danish

### 4. Build Output

The pipeline writes:

* `docs/data.json` → used by the website
* `outputs/latest_poem.txt` → latest generated poem

### 5. Publish

GitHub Pages serves the website from the `/docs` folder.

---

## Running the Pipeline Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

### 3. Run the pipeline

```bash
python run_pipeline.py
```

---

## Automation (GitHub Actions)

The pipeline runs automatically every day using GitHub Actions.

Schedule:

* Every day at **20:00 Danish time**

The workflow:

1. Installs dependencies
2. Runs the pipeline
3. Updates database and website files
4. Commits changes to the repository

---

## GitHub Pages

The website is automatically updated and published via GitHub Pages.

To enable:

1. Go to **Settings → Pages**
2. Select:

   * Source: `Deploy from a branch`
   * Branch: `main`
   * Folder: `/docs`

---

## Example Output

The website displays:

* A bilingual weather poem
* A summary of weather data for each location

---

## Notes

* The database uses `INSERT OR IGNORE` to avoid duplicates
* The pipeline only processes **tomorrow's forecast**
* No API key is required for Open-Meteo
* Groq API key must be added as a GitHub Secret

---

## Author

This project was created as part of a course assignment on data pipelines and MLOps.

---
