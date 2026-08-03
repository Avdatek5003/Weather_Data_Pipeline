import openmeteo_requests
import requests_cache
from retry_requests import retry
from src.database import get_cities_from_db
import datetime

def fetch_current_weather():
    """Veritabanındaki şehirler için anlık hava durumunu çeker."""
    
    #Openmeto ayarları
    cache_session = requests_cache.CachedSession('.cache', expire_after=1800)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"

    #Veritabanından şehirleri al
    cities = get_cities_from_db()
    weather_data_list = []

    for city in cities:
        city_id, city_name, lat, lon = city
        
        
        params = {
            "latitude": float(lat),
            "longitude": float(lon),
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", 
                        "precipitation", "rain", "snowfall", "weather_code", 
                        "cloud_cover", "pressure_msl", "wind_speed_10m", "wind_direction_10m"]
        }
        
        try:
            # API isteği
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0] # Tek bir lokasyon attığımız için ilk elemanı alıyoruz
            current = response.Current()
            
            #Verileri dictionary atama
            city_weather = {
                "city_id": city_id,
                "city_name": city_name,
                "record_time": datetime.datetime.fromtimestamp(current.Time()),
                "temperature_c": current.Variables(0).Value(),
                "humidity_pct": current.Variables(1).Value(),
                "apparent_temp_c": current.Variables(2).Value(),
                "precipitation_mm": current.Variables(3).Value(),
                "rain_mm": current.Variables(4).Value(),
                "snowfall_cm": current.Variables(5).Value(),
                "weather_code": current.Variables(6).Value(),
                "cloud_cover_pct": current.Variables(7).Value(),
                "sea_level_pressure_hpa": current.Variables(8).Value(),
                "wind_speed_kmh": current.Variables(9).Value(),
                "wind_direction_deg": current.Variables(10).Value()
            }
            
            weather_data_list.append(city_weather)
            print(f"✅ {city_name} için veri başarıyla çekildi. (Sıcaklık: {city_weather['temperature_c']:.1f}°C)")
            
        except Exception as e:
            print(f"❌ {city_name} için veri çekilirken hata: {e}")

    return weather_data_list

def fetch_daily_forecast():
    
    from src.database import get_cities_from_db
    import datetime
    
    cities = get_cities_from_db()
    if not cities:
        print("⚠️ Veritabanında şehir bulunamadı.")
        return []

    url = "https://api.open-meteo.com/v1/forecast"

    import openmeteo_requests
    import requests_cache
    from retry_requests import retry

    cache_session = requests_cache.CachedSession('.cache', expire_after=0)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    forecast_list = []

    for city in cities:
        city_id, city_name, lat, lon = city
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum", "rain_sum", "snowfall_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"],
            "timezone": "auto",
            "forecast_days": 5
        }
        
        try:
            # API isteği
            response = openmeteo.weather_api(url, params=params)[0]
            daily = response.Daily()
            
            #Değişkenleri Open-Meteo'nun verdiği sıraya göre alıyoruz
            weather_code = daily.Variables(0).ValuesAsNumpy()
            temp_max = daily.Variables(1).ValuesAsNumpy()
            temp_min = daily.Variables(2).ValuesAsNumpy()
            precip_sum = daily.Variables(3).ValuesAsNumpy()
            rain_sum = daily.Variables(4).ValuesAsNumpy()
            snow_sum = daily.Variables(5).ValuesAsNumpy()
            wind_max = daily.Variables(6).ValuesAsNumpy()
            wind_dir = daily.Variables(7).ValuesAsNumpy()

            #API'den gelen Unix zamanını çeviri
            start_date = datetime.datetime.fromtimestamp(daily.Time())
            
            #5 günlük veriyi tek tek işleyip listemize ekliyoruz
            for i in range(5):
                # Her döngüde günü 1 artırıyoruz (Bugün, Yarın, Sonraki Gün...)
                current_date = (start_date + datetime.timedelta(days=i)).date()
                
                forecast_list.append({
                    "city_id": city_id,
                    "forecast_date": current_date,
                    "weather_code": int(weather_code[i]),
                    "max_temp_c": float(temp_max[i]),
                    "min_temp_c": float(temp_min[i]),
                    "max_wind_speed_kmh": float(wind_max[i]),
                    "wind_direction_deg": float(wind_dir[i]),
                    "precipitation_sum_mm": float(precip_sum[i]),
                    "rain_sum_mm": float(rain_sum[i]),
                    "snowfall_sum_cm": float(snow_sum[i])
                })
                
        except Exception as e:
            print(f"❌ {city_name} tahmini çekilirken hata: {e}")

    return forecast_list
