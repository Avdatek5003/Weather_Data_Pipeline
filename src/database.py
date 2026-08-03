import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

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
        return conn
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

def get_cities_from_db():

    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT city_id, city_name, latitude, longitude FROM cities;")
        cities = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return cities
    except Exception as e:
        print(f"Şehirleri çekerken hata oluştu: {e}")
        return []

# Test etmek için küçük bir blok
if __name__ == "__main__":
    sehirler = get_cities_from_db()
    print("Veritabanından çekilen şehirler:")
    for sehir in sehirler:
        print(sehir)