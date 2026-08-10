import os
import sys
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import time

from src.config import CITY_THRESHOLDS

#Loglama altyapısı
from src.logger import get_logger

#Logger
logger = get_logger(__name__)

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Avdatek5003")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "Weather_Data_Pipeline")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

RESCUE_CITIES = {
    "İzmir": {"lat": 38.42, "lon": 27.14}
}

def clean_openmeteo_data(df, city_name):
    df = df.rename(columns={
        "time": "date",
        "temperature_2m_max": "tmax",
        "temperature_2m_min": "tmin",
        "precipitation_sum": "prcp",
        "snowfall_sum": "snow",  
        "wind_speed_10m_max": "wspd"
    })

    numeric_cols = ['tmax', 'tmin', 'prcp', 'snow', 'wspd']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    thresholds = CITY_THRESHOLDS.get(city_name)
    if not thresholds:
        return df

    BUFFER = 1.08 

    if 'tmax' in df.columns and 'max_temp' in thresholds:
        df.loc[df['tmax'] > (thresholds['max_temp'] * BUFFER), 'tmax'] = None
    if 'tmin' in df.columns and 'min_temp' in thresholds:
        df.loc[df['tmin'] < (thresholds['min_temp'] * BUFFER), 'tmin'] = None
    if 'prcp' in df.columns and 'max_prcp' in thresholds:
        df.loc[df['prcp'] > (thresholds['max_prcp'] * BUFFER), 'prcp'] = None
    if 'snow' in df.columns and 'max_snow' in thresholds:
         df.loc[df['snow'] > (thresholds['max_snow'] * BUFFER), 'snow'] = None
    if 'wspd' in df.columns and 'max_wind_ms' in thresholds:
         df.loc[df['wspd'] > (thresholds['max_wind_ms'] * BUFFER), 'wspd'] = None

    if 'tmax' in df.columns:
        df['tmax'] = df['tmax'].interpolate(method='linear', limit=3)
    if 'tmin' in df.columns:
        df['tmin'] = df['tmin'].interpolate(method='linear', limit=3)
    
    if 'prcp' in df.columns:
        df['prcp'] = df['prcp'].fillna(0.0)
    if 'snow' in df.columns:
        df['snow'] = df['snow'].fillna(0.0)

    df = df.dropna(subset=['tmax', 'tmin'])
    df['date'] = pd.to_datetime(df['date'])
    return df

def fetch_from_openmeteo():
    logger.info("🚀 Open-Meteo Kurtarma Operasyonu (Snowfall Sum Odaklı) Başlatılıyor...")
    
    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        logger.critical(f"❌ Veritabanı bağlantı hatası: {e}")
        sys.exit(1)

    url = "https://archive-api.open-meteo.com/v1/archive"
    start_date = "1940-01-01"
    end_date = "2026-08-04"

    for city, coords in RESCUE_CITIES.items():
        logger.info(f"\n📡 {city} için Open-Meteo'dan taze kar verisi çekiliyor ({start_date} - {end_date})...")
        
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"],
            "timezone": "auto",
            "wind_speed_unit": "ms" 
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily_data = data.get("daily", {})
            if daily_data:
                df = pd.DataFrame(daily_data)
                logger.info(f"   [+] Veri başarıyla indirildi. Temizleniyor...")
                
                df_cleaned = clean_openmeteo_data(df, city)
                df_cleaned['city_name'] = city
                
                df_cleaned.to_sql('historical_weather', engine, if_exists='append', index=False)
                logger.info(f"🐘 {city} başarıyla PostgreSQL'e eklendi! (Temiz Satır: {len(df_cleaned)})")
            else:
                logger.warning(f"⚠️ {city} için veri dönmedi.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"   [X] {city} verisi çekilirken hata oluştu: {e}")

        time.sleep(2)
            
    logger.info("\n🎉 Operasyon başarıyla tamamlandı!")

if __name__ == "__main__":
    fetch_from_openmeteo()