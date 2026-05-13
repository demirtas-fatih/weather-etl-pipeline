"""
load.py
-------
Loads transformed DataFrames into SQLite.

Author : Fatih Demirtas
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path("output/weather.db")
DB_PATH.parent.mkdir(exist_ok=True)


def load_current(df: pd.DataFrame):
    if df.empty:
        print("   ℹ No current data to load")
        return
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("weather_current", conn, if_exists="append", index=False)
    conn.close()
    print(f"   ✅ Loaded {len(df)} rows → weather_current")


def load_historical(df: pd.DataFrame):
    conn = sqlite3.connect(DB_PATH)
    df["date"] = df["date"].astype(str)
    # Avoid duplicates
    try:
        existing = pd.read_sql("SELECT city, date FROM weather_historical", conn)
        key = df["city"] + "_" + df["date"]
        ex_key = existing["city"] + "_" + existing["date"]
        df = df[~key.isin(ex_key)]
    except Exception:
        pass
    if not df.empty:
        df.to_sql("weather_historical", conn, if_exists="append", index=False)
        print(f"   ✅ Loaded {len(df)} new rows → weather_historical")
    else:
        print("   ℹ No new historical rows to load")
    conn.close()


def get_latest_current() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("""
            SELECT * FROM weather_current
            WHERE fetched_at = (SELECT MAX(fetched_at) FROM weather_current)
        """, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def get_historical() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM weather_historical ORDER BY date", conn)
        df["date"] = pd.to_datetime(df["date"])
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


if __name__ == "__main__":
    print(f"DB: {DB_PATH.resolve()}")
    df = get_latest_current()
    print(f"Latest snapshot: {len(df)} cities")
