# 🌤 Weather ETL Pipeline + Streamlit Dashboard

An end-to-end ETL pipeline that **extracts** live weather data from the Open-Meteo API, **transforms** it with Python, **loads** it into SQLite, and visualizes it in a live Streamlit dashboard — fully automated with a scheduler.

---

## 📸 Dashboard Preview

![Weather Dashboard](screenshots/weather_dashboard.png)
*Live KPI cards + current temperature by city — color coded (warm vs cold)*

![Scatter Plot](screenshots/weather_scatter.png)
*Humidity vs Temperature scatter plot with wind speed as color gradient*

![7-Day Trend](screenshots/weather_trend.png)
*7-day temperature trend for selected cities*

---

## 🏗️ Architecture

```
Open-Meteo API (free, no key needed)
        ↓
   [EXTRACT] scripts/extract.py
   Fetches current + 7-day historical weather for 20 cities
        ↓
   [TRANSFORM] scripts/transform.py
   Cleans, normalizes, enriches (feels-like temp, categories)
        ↓
   [LOAD] scripts/load.py
   Stores in SQLite (weather_current + weather_historical tables)
        ↓
   [VISUALIZE] dashboard.py
   Streamlit dashboard with live charts + filters
        ↑
   [SCHEDULER] pipeline.py --schedule
   Runs automatically every hour
```

---

## 📁 Project Structure

```
weather-etl-pipeline/
│
├── scripts/
│   ├── extract.py          # API calls → raw JSON
│   ├── transform.py        # Clean & enrich data
│   └── load.py             # SQLite read/write
│
├── output/
│   └── weather.db          # SQLite database (auto-generated)
│
├── screenshots/            # Dashboard previews
├── pipeline.py             # Run ETL once or on schedule
├── dashboard.py            # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

```bash
# 1. Clone & install
git clone https://github.com/demirtas-fatih/weather-etl-pipeline.git
cd weather-etl-pipeline
pip install -r requirements.txt

# 2. Run the pipeline (fetch data)
python pipeline.py

# 3. Launch the dashboard
streamlit run dashboard.py

# 4. Run on schedule (every hour)
python pipeline.py --schedule
```

---

## 📊 Dashboard Features

- **KPI cards** — cities tracked, avg/min/max temperature
- **Temperature bar chart** — all cities ranked, color-coded (warm = red, cold = blue)
- **Humidity vs Temperature scatter** — wind speed as color gradient
- **7-day trend lines** — select any cities to compare
- **Raw data table** — filterable by country

---

## 🔍 Data Transformations

| Raw field | Transformation | Output |
|-----------|---------------|--------|
| `temperature_2m` | Round to 1dp | `temperature_c` |
| `temperature_2m` + `humidity` | Heat index formula | `feels_like_c` |
| `temperature_2m` | Binning | `temp_category` (Cold/Mild/Warm/Hot) |
| `weather_code` | Code → description map | `weather_desc` |
| `precipitation_sum` | Threshold > 1mm | `rainy_day` (bool) |

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)

---

## 🌍 Cities Tracked

20 cities across Europe, USA and Asia — Berlin, Munich, **Bamberg**, London, Paris, Amsterdam, Vienna, Istanbul, New York, Tokyo and more.

---

## 👤 Author

**Fatih Demirtas** — Data Analyst & BI Specialist
📍 Bamberg, Germany
🔗 [LinkedIn](https://www.linkedin.com/in/fatih-demirtas47/) · [Portfolio](https://demirtas-fatih.github.io/demirtas-fatih/)
