"""
transform.py
------------
Cleans and enriches raw weather data.

Author : Fatih Demirtas
"""

import pandas as pd

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Heavy showers", 82: "Violent showers", 95: "Thunderstorm",
}

def transform_current(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return df

    # Clean
    df = df.dropna(subset=["temperature_c"])
    df["temperature_c"]    = df["temperature_c"].round(1)
    df["wind_speed_kmh"]   = df["wind_speed_kmh"].round(1)
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0).round(2)
    df["humidity_pct"]     = df["humidity_pct"].fillna(df["humidity_pct"].median())

    # Enrich
    df["weather_desc"] = df["weather_code"].map(WEATHER_CODES).fillna("Unknown")
    df["feels_like_c"] = (
        df["temperature_c"] - 0.4 * (df["temperature_c"] - 10) *
        (1 - df["humidity_pct"] / 100)
    ).round(1)
    df["temp_category"] = pd.cut(
        df["temperature_c"],
        bins=[-50, 0, 10, 20, 30, 60],
        labels=["Freezing", "Cold", "Mild", "Warm", "Hot"]
    ).astype(str)

    return df


def transform_historical(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["date"]             = pd.to_datetime(df["date"])
    df["temp_avg_c"]       = ((df["temp_max_c"] + df["temp_min_c"]) / 2).round(1)
    df["temp_range_c"]     = (df["temp_max_c"] - df["temp_min_c"]).round(1)
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0).round(2)
    df["rainy_day"]        = df["precipitation_mm"] > 1.0
    df["day_of_week"]      = df["date"].dt.day_name()

    return df


if __name__ == "__main__":
    from scripts.extract import fetch_current_weather, fetch_historical_weather
    cur  = transform_current(fetch_current_weather())
    hist = transform_historical(fetch_historical_weather(7))
    print("Current:\n", cur[["city","temperature_c","feels_like_c","weather_desc","temp_category"]].to_string(index=False))
    print("\nHistorical:\n", hist[["city","date","temp_avg_c","precipitation_mm"]].head(10).to_string(index=False))
