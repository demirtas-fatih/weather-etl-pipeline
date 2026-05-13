"""
pipeline.py
-----------
Full ETL pipeline: Extract → Transform → Load
Optionally runs on a schedule.

Usage:
    python pipeline.py          # Run once
    python pipeline.py --schedule  # Run every hour

Author : Fatih Demirtas
"""

import sys
import time
from datetime import datetime
from scripts.extract   import fetch_current_weather, fetch_historical_weather
from scripts.transform import transform_current, transform_historical
from scripts.load      import load_current, load_historical


def run_pipeline():
    print("\n" + "=" * 50)
    print(f"  ETL Pipeline Run — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 50)

    # ── Extract ───────────────────────────────────────
    print("\n[1/3] EXTRACT")
    raw_current = fetch_current_weather()
    raw_hist    = fetch_historical_weather(days=7)

    # ── Transform ─────────────────────────────────────
    print("\n[2/3] TRANSFORM")
    df_current = transform_current(raw_current)
    df_hist    = transform_historical(raw_hist)
    print(f"   ✅ Current  : {len(df_current)} cities transformed")
    print(f"   ✅ Historical: {len(df_hist)} records transformed")

    # ── Load ──────────────────────────────────────────
    print("\n[3/3] LOAD")
    load_current(df_current)
    load_historical(df_hist)

    print(f"\n✅ Pipeline complete — {datetime.utcnow().strftime('%H:%M:%S')} UTC\n")


if __name__ == "__main__":
    run_pipeline()

    if "--schedule" in sys.argv:
        import schedule
        print("⏰ Scheduler active — running every hour. Press Ctrl+C to stop.\n")
        schedule.every(1).hours.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
