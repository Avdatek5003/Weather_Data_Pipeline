import psycopg2
import os
from dotenv import load_dotenv

# Loglama altyapımızı dahil ediyoruz
from src.logger import get_logger

load_dotenv()

# Bu dosya için logger'ı başlatıyoruz
logger = get_logger(__name__)

def get_db_connection():
    """PostgreSQL bağlantısı"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        #Loglama
        logger.info("Veritabanı bağlantısı başarıyla kuruldu.")
        return conn
    except Exception as e:
        #Wrror loging
        logger.error(f"Veritabanı bağlantı hatası: {e}")
        return None

def get_cities_from_db():

    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT city_id, city_name, latitude, longitude, station_code, wmo_id FROM cities;")
        cities = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        
        logger.info(f"Veritabanından {len(cities)} şehir başarıyla çekildi.")
        return cities
    except Exception as e:
        
        logger.error(f"Şehirleri çekerken hata oluştu: {e}")
        return []

# Test etmek için küçük bir blok
if __name__ == "__main__":
    sehirler = get_cities_from_db()
    logger.info("Veritabanından çekilen şehirler listeleniyor:")
    for sehir in sehirler:
        logger.info(sehir)