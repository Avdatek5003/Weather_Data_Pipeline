from src.extract import fetch_current_weather, fetch_daily_forecast
from src.load import insert_weather_data, insert_daily_forecast

if __name__ == "__main__":
    print("🚀 Veri boru hattı (Pipeline) başlatılıyor...")
    print("-" * 40)
    
    # --- 1. ANLIK VERİ AKIŞI ---
    print("🌤️ Anlık hava durumu çekiliyor...")
    current_data = fetch_current_weather()
    if current_data:
        insert_weather_data(current_data)
        
    print("-" * 40)
    
    # --- 2. GÜNLÜK TAHMİN AKIŞI ---
    print("📅 5 Günlük tahmin verileri çekiliyor...")
    forecast_data = fetch_daily_forecast()
    if forecast_data:
        insert_daily_forecast(forecast_data)
        
    print("-" * 40)
    print("🎉 Pipeline turu başarıyla tamamlandı!")