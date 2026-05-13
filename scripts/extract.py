"""
extract.py
----------
Fetches current & historical weather data from Open-Meteo API (free, no key needed).
Returns raw JSON as a list of records.

Author : Fatih Demirtas
"""

import requests
import pandas as pd
from datetime import datetime, timedelta

CITIES = [
    {"city": "Berlin",        "country": "DE", "lat": 52.52,  "lon": 13.41},
    {"city": "Munich",        "country": "DE", "lat": 48.14,  "lon": 11.58},
    {"city": "Hamburg",       "country": "DE", "lat": 53.55,  "lon": 10.00},
    {"city": "Frankfurt",     "country": "DE", "lat": 50.11,  "lon": 8.68},
    {"city": "Cologne",       "country": "DE", "lat": 50.94,  "lon": 6.96},
    {"city": "Stuttgart",     "country": "DE", "lat": 48.78,  "lon": 9.18},
    {"city": "Bamberg",       "country": "DE", "lat": 49.90,  "lon": 10.90},
    {"city": "London",        "country": "GB", "lat": 51.51,  "lon": -0.13},
    {"city": "Paris",         "country": "FR", "lat": 48.85,  "lon": 2.35},
    {"city": "Amsterdam",     "country": "NL", "lat": 52.37,  "lon": 4.90},
    {"city": "Vienna",        "country": "AT", "lat": 48.21,  "lon": 16.37},
    {"city": "Zurich",        "country": "CH", "lat": 47.38,  "lon": 8.54},
    {"city": "Madrid",        "country": "ES", "lat": 40.42,  "lon": -3.70},
    {"city": "Rome",          "country": "IT", "lat": 41.90,  "lon": 12.50},
    {"city": "Stockholm",     "country": "SE", "lat": 59.33,  "lon": 18.07},
    {"city": "Warsaw",        "country": "PL", "lat": 52.23,  "lon": 21.01},
    {"city": "Prague",        "country": "CZ", "lat": 50.08,  "lon": 14.44},
    {"city": "Istanbul",      "country": "TR", "lat": 41.01,  "lon": 28.95},
    {"city": "New York",      "country": "US", "lat": 40.71,  "lon": -74.01},
    {"city": "Tokyo",         "country": "JP", "lat": 35.68,  "lon": 139.69},
]

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_current_weather():
    """Fetch current weather for all cities."""
    records = []
    fetched_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"   Fetching weather for {len(CITIES)} cities...")
    for city in CITIES:
        params = {
            "latitude":            city["lat"],
            "longitude":           city["lon"],
            "current":             "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
            "wind_speed_unit":     "kmh",
            "timezone":            "UTC",
        }
        try:
            r = requests.get(BASE_URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            cur  = data["current"]
            records.append({
                "city":              city["city"],
                "country":           city["country"],
                "latitude":          city["lat"],
                "longitude":         city["lon"],
                "temperature_c":     cur.get("temperature_2m"),
                "humidity_pct":      cur.get("relative_humidity_2m"),
                "wind_speed_kmh":    cur.get("wind_speed_10m"),
                "precipitation_mm":  cur.get("precipitation"),
                "weather_code":      cur.get("weather_code"),
                "fetched_at":        fetched_at,
            })
        except Exception as e:
            print(f"   ⚠ {city['city']}: {e}")

    print(f"   ✅ Fetched {len(records)} cities")
    return records


def fetch_historical_weather(days: int = 7):
    """Fetch last N days of daily weather for all cities."""
    records = []
    end   = datetime.utcnow().date()
    start = end - timedelta(days=days)

    print(f"   Fetching {days}-day history ({start} → {end})...")
    for city in CITIES:
        params = {
            "latitude":   city["lat"],
            "longitude":  city["lon"],
            "daily":      "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "start_date": str(start),
            "end_date":   str(end),
            "timezone":   "UTC",
        }
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast",
                             params=params, timeout=10)
            r.raise_for_status()
            data   = r.json()
            daily  = data["daily"]
            for i, date in enumerate(daily["time"]):
                records.append({
                    "city":            city["city"],
                    "country":         city["country"],
                    "date":            date,
                    "temp_max_c":      daily["temperature_2m_max"][i],
                    "temp_min_c":      daily["temperature_2m_min"][i],
                    "precipitation_mm": daily["precipitation_sum"][i],
                    "wind_max_kmh":    daily["wind_speed_10m_max"][i],
                })
        except Exception as e:
            print(f"   ⚠ {city['city']}: {e}")

    print(f"   ✅ Fetched {len(records)} historical records")
    return records


if __name__ == "__main__":
    current = fetch_current_weather()
    print(pd.DataFrame(current)[["city","temperature_c","humidity_pct","wind_speed_kmh"]].to_string(index=False))
