import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry
from src.database import get_cities_from_db
import datetime

#Loglama altyapısı
from src.logger import get_logger

#Loglama için logger başlatma
logger = get_logger(__name__)

def fetch_current_weather():
    """Veritabanındaki şehirler için Open-Meteo'dan anlık hava durumunu çeker."""
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=1800)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"

    cities = get_cities_from_db()
    weather_data_list = []

    if not cities:
        logger.warning("⚠️ Veritabanında şehir bulunamadı.")
        return []

    for city in cities:
        city_id, city_name, lat, lon = city[0], city[1], city[2], city[3]
        
        params = {
            "latitude": float(lat),
            "longitude": float(lon),
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", 
                        "precipitation", "rain", "snowfall", "weather_code", 
                        "cloud_cover", "pressure_msl", "wind_speed_10m", "wind_direction_10m"]
        }
        
        try:
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]
            current = response.Current()
            
            city_weather = {
                "city_id": city_id,
                "city_name": city_name,
                "record_time": datetime.datetime.fromtimestamp(current.Time()),
                "temperature_c": float(current.Variables(0).Value()),
                "humidity_pct": float(current.Variables(1).Value()),
                "apparent_temp_c": float(current.Variables(2).Value()),
                "precipitation_mm": float(current.Variables(3).Value()),
                "rain_mm": float(current.Variables(4).Value()),
                "snowfall_cm": float(current.Variables(5).Value()),
                "weather_code": int(current.Variables(6).Value()),
                "cloud_cover_pct": float(current.Variables(7).Value()),
                "sea_level_pressure_hpa": float(current.Variables(8).Value()),
                "wind_speed_kmh": float(current.Variables(9).Value()),
                "wind_direction_deg": float(current.Variables(10).Value())
            }
            
            weather_data_list.append(city_weather)
            logger.info(f"✅ {city_name} merkezi için Open-Meteo verisi çekildi. Sıcaklık: {city_weather['temperature_c']:.1f}°C")
            
        except Exception as e:
            logger.error(f"❌ {city_name} merkezi için veri çekilirken hata: {e}")

    return weather_data_list


def fetch_airport_current_weather():
    """Havalimanları için NOAA'dan ICAO kodlarıyla anlık METAR verisini çeker."""
    from src.database import get_db_connection
    import requests
    import datetime
    
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT airport_id, airport_name, station_code FROM airports;")
        airports = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Havalimanları veritabanından çekilemedi: {e}")
        return []

    airport_weather_list = []

    for airport in airports:
        airport_id, airport_name, station_code = airport
        
        if not station_code:
            continue

        url = "https://aviationweather.gov/api/data/metar"
        params = {"ids": station_code, "format": "json"}
        
        try:
            headers = {"User-Agent": "WeatherPipeline/1.0"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                continue

            data = response.json()
            if not data or not isinstance(data, list):
                continue
                
            station = data[0]
            
            obs_time_raw = station.get("obsTime") 
            if obs_time_raw:
                if isinstance(obs_time_raw, (int, float)):
                    obs_time = datetime.datetime.fromtimestamp(obs_time_raw)
                else:
                    obs_time = datetime.datetime.fromisoformat(str(obs_time_raw).replace('Z', '+00:00'))
            else:
                obs_time = datetime.datetime.now()

            wind_speed_knots = station.get("wspd")
            wind_speed_kmh = float(wind_speed_knots) * 1.852 if wind_speed_knots is not None else 0.0
            
            temp = station.get("temp")
            dewp = station.get("dewp")
            humidity = None
            if temp is not None and dewp is not None:
                humidity = 100 * (1 - (temp - dewp) / 20)
                humidity = max(0, min(100, humidity))

            precip_inches = station.get("precip")
            precipitation_mm = float(precip_inches) * 25.4 if precip_inches is not None else 0.0

            #VRB (Variable) Rüzgar Yönü Çözümü 
            raw_wdir = station.get("wdir")
            if raw_wdir == "VRB" or raw_wdir == "":
                wind_dir_deg = None
            else:
                try:
                    wind_dir_deg = int(raw_wdir)
                except (ValueError, TypeError):
                    wind_dir_deg = None
            # ----------------------------------------

            airport_weather = {
                "airport_id": airport_id,
                "airport_name": airport_name,
                "record_time": obs_time,
                "temperature_c": temp,
                "dewpoint_c": dewp,
                "humidity_pct": humidity,
                "wind_speed_kmh": wind_speed_kmh,
                "wind_direction_deg": wind_dir_deg,  
                "sea_level_pressure_hpa": station.get("altim"),
                "precipitation_mm": precipitation_mm,
                "wx_string": station.get("wxString")
            }
            
            airport_weather_list.append(airport_weather)
            logger.info(f"✈️ {airport_name} ({station_code}) METAR verisi çekildi. Sıcaklık: {temp}°C")
            
        except Exception as e:
            logger.error(f"❌ {airport_name} METAR çekilirken hata: {e}")

    return airport_weather_list


def fetch_daily_forecast():
    cities = get_cities_from_db()
    if not cities:
        logger.warning("⚠️ Veritabanında şehir bulunamadı.")
        return []

    url = "https://api.open-meteo.com/v1/forecast"

    cache_session = requests_cache.CachedSession('.cache', expire_after=0)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    forecast_list = []

    for city in cities:
        city_id, city_name, lat, lon = city[0], city[1], city[2], city[3]
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_sum", "rain_sum", "snowfall_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"],
            "timezone": "auto",
            "forecast_days": 5
        }
        
        try:
            response = openmeteo.weather_api(url, params=params)[0]
            daily = response.Daily()
            
            weather_code = daily.Variables(0).ValuesAsNumpy()
            temp_max = daily.Variables(1).ValuesAsNumpy()
            temp_min = daily.Variables(2).ValuesAsNumpy()
            precip_sum = daily.Variables(3).ValuesAsNumpy()
            rain_sum = daily.Variables(4).ValuesAsNumpy()
            snow_sum = daily.Variables(5).ValuesAsNumpy()
            wind_max = daily.Variables(6).ValuesAsNumpy()
            wind_dir = daily.Variables(7).ValuesAsNumpy()

            start_date = datetime.datetime.fromtimestamp(daily.Time())
            
            for i in range(5):
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
            logger.error(f"❌ {city_name} tahmini çekilirken hata: {e}")

    return forecast_list