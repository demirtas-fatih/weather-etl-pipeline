"""
dashboard.py
------------
Streamlit dashboard for weather ETL pipeline.

Run with: streamlit run dashboard.py

Author : Fatih Demirtas
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sqlite3
from pathlib import Path
from scripts.load import get_latest_current, get_historical

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather ETL Dashboard",
    page_icon="🌤",
    layout="wide",
)

st.title("🌤 Weather ETL Pipeline — Live Dashboard")
st.caption("Data fetched from Open-Meteo API · Stored in SQLite · Refreshed hourly")

# ── Load data ─────────────────────────────────────────────────────────────────
df_cur  = get_latest_current()
df_hist = get_historical()

if df_cur.empty:
    st.warning("No data yet. Run `python pipeline.py` first.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Cities tracked",    len(df_cur))
col2.metric("Avg temperature",   f"{df_cur['temperature_c'].mean():.1f} °C")
col3.metric("Hottest city",      df_cur.loc[df_cur['temperature_c'].idxmax(), 'city'])
col4.metric("Coldest city",      df_cur.loc[df_cur['temperature_c'].idxmin(), 'city'])
col5.metric("Avg humidity",      f"{df_cur['humidity_pct'].mean():.0f}%")

st.divider()

# ── Filters ───────────────────────────────────────────────────────────────────
countries = ["All"] + sorted(df_cur["country"].unique().tolist())
sel_country = st.selectbox("Filter by country", countries)
if sel_country != "All":
    df_cur = df_cur[df_cur["country"] == sel_country]

# ── Chart 1: Temperature bar chart ────────────────────────────────────────────
st.subheader("Current Temperature by City (°C)")
df_sorted = df_cur.sort_values("temperature_c", ascending=False)

fig, ax = plt.subplots(figsize=(12, 4))
colors = ["#E85D24" if t > 20 else "#2563EB" if t < 10 else "#0891B2"
          for t in df_sorted["temperature_c"]]
bars = ax.bar(df_sorted["city"], df_sorted["temperature_c"], color=colors, alpha=0.85)
ax.bar_label(bars, labels=[f"{v:.1f}°" for v in df_sorted["temperature_c"]],
             padding=3, fontsize=8)
ax.axhline(0, color="black", linewidth=0.8, alpha=0.3)
ax.set_ylabel("Temperature (°C)")
ax.tick_params(axis="x", rotation=45)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# ── Chart 2: Humidity vs Temperature scatter ───────────────────────────────────
st.subheader("Humidity vs Temperature")
fig2, ax2 = plt.subplots(figsize=(8, 4))
scatter = ax2.scatter(
    df_cur["temperature_c"], df_cur["humidity_pct"],
    c=df_cur["wind_speed_kmh"], cmap="YlOrRd",
    s=80, alpha=0.8, edgecolors="white", linewidth=0.5
)
plt.colorbar(scatter, ax=ax2, label="Wind speed (km/h)")
for _, row in df_cur.iterrows():
    ax2.annotate(row["city"], (row["temperature_c"], row["humidity_pct"]),
                 fontsize=7, alpha=0.7, xytext=(4, 4), textcoords="offset points")
ax2.set_xlabel("Temperature (°C)")
ax2.set_ylabel("Humidity (%)")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig2)
plt.close()

# ── Chart 3: Historical temp trend ────────────────────────────────────────────
if not df_hist.empty:
    st.subheader("7-Day Temperature Trend (selected cities)")
    top_cities = df_cur.nlargest(5, "temperature_c")["city"].tolist()
    sel_cities = st.multiselect("Select cities", df_hist["city"].unique().tolist(),
                                default=top_cities[:5])
    if sel_cities:
        fig3, ax3 = plt.subplots(figsize=(12, 4))
        palette = ["#2563EB","#E85D24","#0891B2","#7C3AED","#16A34A"]
        for i, city in enumerate(sel_cities):
            city_df = df_hist[df_hist["city"] == city].sort_values("date")
            ax3.plot(city_df["date"], city_df["temp_avg_c"],
                     marker="o", markersize=4, linewidth=2,
                     color=palette[i % len(palette)], label=city)
        ax3.set_ylabel("Avg Temperature (°C)")
        ax3.legend(framealpha=0, ncol=3)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        ax3.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

# ── Data table ────────────────────────────────────────────────────────────────
st.subheader("Raw Data Snapshot")
st.dataframe(
    df_cur[["city","country","temperature_c","feels_like_c","humidity_pct",
            "wind_speed_kmh","precipitation_mm","weather_desc","temp_category"]]
    .sort_values("temperature_c", ascending=False)
    .reset_index(drop=True),
    use_container_width=True
)

st.caption(f"Last fetch: {df_cur['fetched_at'].iloc[0]} UTC")
