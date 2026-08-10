from src.database import get_db_connection

#Loglama altyapısı
from src.logger import get_logger

#Logger başlatma
logger = get_logger(__name__)

def insert_center_weather_data(weather_data_list):
    """Open-Meteo'dan çekilen şehir merkezi anlık verilerini center_hourly_weather_data tablosuna kaydeder."""
    if not weather_data_list:
        logger.warning("⚠️ Kaydedilecek şehir merkezi verisi bulunamadı.")
        return

    conn = get_db_connection()
    if not conn:
        logger.error("❌ Veritabanına bağlanılamadığı için veriler kaydedilemedi.")
        return

    try:
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO center_hourly_weather_data (
            city_id, record_time, temperature_c, humidity_pct, 
            apparent_temp_c, precipitation_mm, rain_mm, snowfall_cm, 
            weather_code, cloud_cover_pct, sea_level_pressure_hpa, 
            wind_speed_kmh, wind_direction_deg
        ) VALUES (
            %(city_id)s, %(record_time)s, %(temperature_c)s, %(humidity_pct)s,
            %(apparent_temp_c)s, %(precipitation_mm)s, %(rain_mm)s, %(snowfall_cm)s,
            %(weather_code)s, %(cloud_cover_pct)s, %(sea_level_pressure_hpa)s,
            %(wind_speed_kmh)s, %(wind_direction_deg)s
        );
        """
        
        for data in weather_data_list:
            cursor.execute(insert_query, data)
            
        conn.commit()
        logger.info(f"💾 Başarılı! {len(weather_data_list)} şehrin merkezi Open-Meteo verisi kaydedildi.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Merkez verileri kaydedilirken bir hata oluştu: {e}")
        
    finally:
        cursor.close()
        conn.close()


def insert_airport_weather_data(airport_weather_list):
    """NOAA'dan (METAR) çekilen havalimanı anlık verilerini airport_hourly_weather_data tablosuna kaydeder."""
    if not airport_weather_list:
        logger.warning("⚠️ Kaydedilecek havalimanı verisi bulunamadı.")
        return

    conn = get_db_connection()
    if not conn:
        logger.error("❌ Veritabanına bağlanılamadığı için havalimanı verileri kaydedilemedi.")
        return

    try:
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO airport_hourly_weather_data (
            airport_id, record_time, temperature_c, dewpoint_c, 
            humidity_pct, wind_speed_kmh, wind_direction_deg, 
            sea_level_pressure_hpa, precipitation_mm, wx_string
        ) VALUES (
            %(airport_id)s, %(record_time)s, %(temperature_c)s, %(dewpoint_c)s,
            %(humidity_pct)s, %(wind_speed_kmh)s, %(wind_direction_deg)s,
            %(sea_level_pressure_hpa)s, %(precipitation_mm)s, %(wx_string)s
        );
        """
        
        for data in airport_weather_list:
            cursor.execute(insert_query, data)
            
        conn.commit()
        logger.info(f"✈️ Başarılı! {len(airport_weather_list)} havalimanının METAR verisi kaydedildi.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Havalimanı verileri kaydedilirken bir hata oluştu: {e}")
        
    finally:
        cursor.close()
        conn.close()


def insert_daily_forecast(forecast_data_list):
    """5 günlük tahminleri PostgreSQL'e UPSERT mantığıyla yükler."""
    if not forecast_data_list:
        logger.warning("⚠️ Kaydedilecek tahmin verisi bulunamadı.")
        return

    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO daily_forecast_data (
            city_id, forecast_date, weather_code, max_temp_c, min_temp_c, 
            max_wind_speed_kmh, wind_direction_deg, precipitation_sum_mm, 
            rain_sum_mm, snowfall_sum_cm
        ) VALUES (
            %(city_id)s, %(forecast_date)s, %(weather_code)s, %(max_temp_c)s, %(min_temp_c)s,
            %(max_wind_speed_kmh)s, %(wind_direction_deg)s, %(precipitation_sum_mm)s,
            %(rain_sum_mm)s, %(snowfall_sum_cm)s
        )
        ON CONFLICT (city_id, forecast_date) 
        DO UPDATE SET 
            weather_code = EXCLUDED.weather_code,
            max_temp_c = EXCLUDED.max_temp_c,
            min_temp_c = EXCLUDED.min_temp_c,
            max_wind_speed_kmh = EXCLUDED.max_wind_speed_kmh,
            wind_direction_deg = EXCLUDED.wind_direction_deg,
            precipitation_sum_mm = EXCLUDED.precipitation_sum_mm,
            rain_sum_mm = EXCLUDED.rain_sum_mm,
            snowfall_sum_cm = EXCLUDED.snowfall_sum_cm,
            created_at = CURRENT_TIMESTAMP;
        """
        
        for data in forecast_data_list:
            cursor.execute(insert_query, data)
            
        conn.commit()
        logger.info(f"💾 UPSERT Başarılı! Toplam {len(forecast_data_list)} günlük tahmin verisi işlendi.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Tahminler kaydedilirken bir hata oluştu: {e}")
        
    finally:
        cursor.close()
        conn.close()


def clean_old_forecasts():
    """Bugünden eski olan tahmin verilerini veritabanından siler."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            delete_query = "DELETE FROM daily_forecast_data WHERE forecast_date < CURRENT_DATE;"
            cur.execute(delete_query)
            conn.commit()
            logger.info("🧹 Eski tahmin verileri veritabanından başarıyla temizlendi.")
        except Exception as e:
            logger.error(f"Silme işlemi sırasında hata oluştu: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()