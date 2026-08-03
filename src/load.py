from src.database import get_db_connection

def insert_weather_data(weather_data_list):

    if not weather_data_list:
        print("⚠️ Kaydedilecek veri bulunamadı.")
        return

    conn = get_db_connection()
    if not conn:
        print("❌ Veritabanına bağlanılamadığı için veriler kaydedilemedi.")
        return

    try:
        cursor = conn.cursor()
        
        #SQL Insert Sorgusu
        insert_query = """
        INSERT INTO hourly_weather_data (
            city_id, record_time, temperature_c, apparent_temp_c, 
            humidity_pct, wind_speed_kmh, wind_direction_deg, 
            precipitation_mm, rain_mm, snowfall_cm, 
            cloud_cover_pct, sea_level_pressure_hpa, weather_code
        ) VALUES (
            %(city_id)s, %(record_time)s, %(temperature_c)s, %(apparent_temp_c)s,
            %(humidity_pct)s, %(wind_speed_kmh)s, %(wind_direction_deg)s,
            %(precipitation_mm)s, %(rain_mm)s, %(snowfall_cm)s,
            %(cloud_cover_pct)s, %(sea_level_pressure_hpa)s, %(weather_code)s
        );
        """
        
        #Verileri tek tek (veya topluca) tabloya ekleme
        for data in weather_data_list:
            cursor.execute(insert_query, data)
            
        #Değişiklikleri veritabanına kesin olarak kaydet
        conn.commit()
        print(f"💾 Başarılı! {len(weather_data_list)} şehrin verisi veritabanına kaydedildi.")
        
    except Exception as e:
        conn.rollback() #Hata olursa işlemi geri alma
        print(f"❌ Veriler kaydedilirken bir hata oluştu: {e}")
        
    finally:
        cursor.close()
        conn.close()


def insert_daily_forecast(forecast_data_list):
    """5 günlük tahminleri PostgreSQL'e UPSERT mantığıyla yükler."""
    if not forecast_data_list:
        print("⚠️ Kaydedilecek tahmin verisi bulunamadı.")
        return

    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        #Ekleme
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
        print(f"💾 UPSERT Başarılı! Toplam {len(forecast_data_list)} günlük tahmin verisi işlendi.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Tahminler kaydedilirken bir hata oluştu: {e}")
        
    finally:
        cursor.close()
        conn.close()