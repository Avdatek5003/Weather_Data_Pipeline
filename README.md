# 🌤️ Weather Data Engineering Pipeline & Dashboard

This project is an end-to-end Data Engineering and ETL (Extract, Transform, Load) pipeline. It extracts real-time weather and 5-day forecast data for selected cities in Europe and Turkey via the Open-Meteo API, stores it in a relational database, and visualizes the insights through an interactive Streamlit dashboard.

## 🚀 Project Architecture & Features

The project consists of three main layers:

1. **Extract:** Connects to the Open-Meteo API using Python. API rate limits and redundant requests are efficiently handled using `requests_cache`.
2. **Load:** The extracted data is loaded into structured relational tables (`hourly_weather_data`, `daily_forecast_data`) in PostgreSQL. To prevent data duplication and ensure data consistency, SQL **UPSERT (ON CONFLICT DO UPDATE)** logic is implemented for forecast data.
3. **Visualize & Analyze:** Real-time data is retrieved from the database using advanced SQL queries, including Window Functions, and transformed into a dynamic web dashboard using Plotly and Streamlit.

### 🌟 Dashboard Highlights
* **🌍 Live Map (Mapbox):** Displays real-time temperatures and geographical locations of the tracked cities on an interactive global map.
* **📈 5-Day Forecast Analysis:** Visualizes the maximum and minimum temperature trends for the upcoming 5 days using Plotly Line Charts.
* **🌧️ Precipitation & Wind Metrics:** Analyzes precipitation volume and wind speeds using Bar and Area charts. Custom Python functions are utilized to convert raw wind direction degrees into human-readable directional text (e.g., "From North", "From Southwest").

## 🛠️ Technologies Used

* **Programming Language:** Python (Data Processing)
* **Database:** PostgreSQL
* **Libraries & Frameworks:** 
  * `pandas` (Data manipulation)
  * `psycopg2` (PostgreSQL database adapter)
  * `streamlit` (Web application framework)
  * `plotly` (Interactive data visualization)
  * `openmeteo_requests`, `requests_cache` (API interactions and caching)

## 📂 Directory Structure

```text
WEATHER_DATA_PIPELINE/
│
├── src/                    # Core modules
│   ├── database.py         # PostgreSQL connection configurations
│   ├── extract.py          # Data extraction from API (Current & Forecast)
│   ├── load.py             # Database insertion logic (INSERT and UPSERT)
│
├── app.py                  # Streamlit Dashboard application
├── main.py                 # Orchestrator script to trigger the ETL process
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables and database credentials (Ignored in Git)
└── README.md               # Project documentation