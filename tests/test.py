import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "d83487a418msh9c3190e57937301p1fa1d1jsn58a5f8ea9cbe") 
RAPIDAPI_HOST = "meteostat.p.rapidapi.com"

CITIES = {
    "Roma": {"lat":41.80, "lon":12.25},
    "Los Angales": {"lat":40.78, "lon":-73.97}
}

def check_station_inventory():
    print(" RapidAPI Gerçek İstasyon Künyesi Testi Başlıyor...\n" + "-"*60)
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    for city, coords in CITIES.items():
        nearby_url = f"https://{RAPIDAPI_HOST}/stations/nearby"
        nearby_query = {"lat": coords["lat"], "lon": coords["lon"], "limit": 2}
        
        try:
            res_nearby = requests.get(nearby_url, headers=headers, params=nearby_query)
            res_nearby.raise_for_status()
            nearby_data = res_nearby.json().get('data', [])
            
            if nearby_data:
                for i in range(2):
                    station = nearby_data[i]
                    station_id = station.get('id')
                    station_name = station.get('name', {}).get('en', 'Bilinmiyor')
                    distance = station.get('distance', 0)
                
                    meta_url = f"https://{RAPIDAPI_HOST}/stations/meta"
                    meta_query = {"id": station_id}
                
                    res_meta = requests.get(meta_url, headers=headers, params=meta_query)
                    res_meta.raise_for_status()
                    meta_data = res_meta.json().get('data', {})
                
                    inventory = meta_data.get('inventory', {}).get('daily', {})
                
                        #None veri gelirse veri yok işaretle
                    daily_start = inventory.get('start') or 'Veri Yok'
                    daily_end = inventory.get('end') or 'Veri Yok'
                
                    print(f"📍 Şehir: {city}")
                    print(f"   🏢 İstasyon Adı      : {station_name} (ID: {station_id})")
                    print(f"   📏 Merkeze Mesafe    : {distance / 1000:.1f} km")
                    print(f"   📅 Veri Başlangıcı   : {daily_start}")
                    print(f"   📅 Veri Bitişi       : {daily_end}")
                
                    if daily_start != 'Veri Yok' and daily_start < '1950-01-01':
                        print("   ✅ Durum: Tarihi veri var, Ana ETL'de sorunsuz akar.")
                    elif daily_start != 'Veri Yok':
                        print("   ⚠️ Durum: Sadece yakın dönem verisi var. ETL (Point) diğer istasyonlardan destek alacak.")
                    else:
                        print("   ❌ Durum: İstasyon günlük veri tutmuyor.")
                        print("-" * 60)
                
            else:
                print(f"📍 Şehir: {city}")
                print("   ❌ Yakında istasyon bulunamadı!")
                print("-" * 60)
                
        except requests.exceptions.RequestException as e:
            print(f"📍 Şehir: {city} -> İstek hatası: {e}")
            print("-" * 60)

        time.sleep(2)    

if __name__ == "__main__":
    check_station_inventory()