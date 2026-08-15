import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine

#Config'den şehir verilerini çekme
from src.config import CITY_THRESHOLDS, LOCATION_SOURCES

#Loglama altyapısı
from src.logger import get_logger

#Logger başlatma
logger = get_logger(__name__)

# .env dosyasındaki gizli bilgileri yüklüyoruz
load_dotenv()


RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") 
RAPIDAPI_HOST = "meteostat.p.rapidapi.com"  

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")  
DB_PORT = os.getenv("DB_PORT", "5432")       
DB_NAME = os.getenv("DB_NAME")

#Güvenlik kontrolü
if not RAPIDAPI_KEY or not DB_PASSWORD:
    logger.error("API Key veya Veritabanı şifresi .env dosyasından okunamadı!")
    raise ValueError(".env dosyanızı kontrol edin. Hassas veriler eksik.")

# Her şey yolundaysa veritabanı linkini oluştur
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def clean_historical_data(df, city_name):
    numeric_cols = ['tmax', 'tmin', 'prcp', 'snow']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    thresholds = CITY_THRESHOLDS.get(city_name)
    if not thresholds:
        return df

    BUFFER = 1.08 

    df.loc[df['tmax'] > (thresholds['max_temp'] * BUFFER), 'tmax'] = None
    df.loc[df['tmin'] < (thresholds['min_temp'] * BUFFER), 'tmin'] = None
    df.loc[df['prcp'] > (thresholds['max_prcp'] * BUFFER), 'prcp'] = None
    if 'snow' in df.columns:
         df.loc[df['snow'] > (thresholds['max_snow'] * BUFFER), 'snow'] = None

    df['tmax'] = df['tmax'].interpolate(method='linear', limit=7)
    df['tmin'] = df['tmin'].interpolate(method='linear', limit=7)
    
    df['prcp'] = df['prcp'].fillna(0.0)
    if 'snow' in df.columns:
        df['snow'] = df['snow'].fillna(0.0)

    df = df.dropna(subset=['tmax', 'tmin'])
    return df


def fetch_and_save_pipeline():
    logger.info("🚀 Profesyonel Hibrit ETL Pipeline Başlatılıyor...")
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    start_year_global = 1940
    current_year = datetime.now().year

    try:
        engine = create_engine(DATABASE_URL)
    except Exception as e:
        logger.critical(f"❌ Veritabanı bağlantı hatası: {e}")
        sys.exit(1)


    for city, info in LOCATION_SOURCES.items():
        logger.info(f"\n📡 {city} verileri 8'er yıllık periyotlarla çekiliyor...")
        city_chunks = []
        
        for year in range(start_year_global, current_year + 1, 8):
            chunk_start = f"{year}-01-01"
            chunk_end_year = min(year + 7, current_year)
            chunk_end = f"{chunk_end_year}-12-31"
            
            if chunk_end_year == current_year:
                chunk_end = datetime.now().strftime('%Y-%m-%d')
                
            #İstasyon bazlı mı yoksa koordinat bazlı mı istek atılacağını seçiyoruz
            if info["type"] == "station":
                url = f"https://{RAPIDAPI_HOST}/station/daily"
                querystring = {
                    "station": info["station_id"],
                    "start": chunk_start,
                    "end": chunk_end
                }
            else:
                url = f"https://{RAPIDAPI_HOST}/point/daily"
                querystring = {
                    "lat": info["lat"],
                    "lon": info["lon"],
                    "alt": 50,  
                    "start": chunk_start,
                    "end": chunk_end
                }
            
            try:
                response = requests.get(url, headers=headers, params=querystring)
                remaining = response.headers.get('X-RateLimit-Requests-Remaining', 'Bilinmiyor')
                logger.info(f"   [i] Kalan API İstek Hakkı: {remaining}")
                
                response.raise_for_status() 
                
                json_data = response.json()
                daily_records = json_data.get('data', [])
                
                if daily_records:
                    city_chunks.append(pd.DataFrame(daily_records))
                    logger.info(f"   [+] {chunk_start} - {chunk_end} başarıyla indirildi.")
                
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"   [X] {chunk_start} periyodu hata verdi: {e}")
                continue
            
        if city_chunks:
            df_city_full = pd.concat(city_chunks, ignore_index=True)
            
            if 'date' in df_city_full.columns:
                df_city_full['date'] = pd.to_datetime(df_city_full['date'])
                df_city_full = df_city_full.drop_duplicates(subset=['date']).sort_values('date')
                
            logger.info(f"🧹 {city} verileri temizleniyor...")
            df_cleaned = clean_historical_data(df_city_full, city)
            df_cleaned['city_name'] = city
            
            #Veritabanına kayıt ve hata kontrol
            try:
                df_cleaned.to_sql('historical_weather', engine, if_exists='append', index=False)
                logger.info(f"DB ye {city} başarıyla kaydedildi")
                
            except Exception as db_err:
                logger.critical(f"\n❌ KRİTİK VERİTABANI HATASI: {city} verisi DB'ye yazılamadı!")
                logger.critical(f"Hata Detayı: {db_err}")
                logger.critical("🛑 Sistem güvenli bir şekilde sonlandırılıyor.")
                sys.exit(1)
        else:
            logger.warning(f"⚠️ {city} için hiçbir periyotta veri bulunamadı.")

    logger.info("\n🎉 Tüm süreç kusursuz tamamlandı! Veriler veritabanında güvenle yerini aldı.")


if __name__ == "__main__":
    fetch_and_save_pipeline()