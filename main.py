from src.extract import fetch_current_weather, fetch_airport_current_weather, fetch_daily_forecast
from src.load import insert_center_weather_data, insert_airport_weather_data, insert_daily_forecast, clean_old_forecasts

if __name__ == "__main__":
    print("🚀 Veri boru hattı (Pipeline) başlatılıyor...")
    print("-" * 40)
    
    #Anlık veri akışı
    print("🌤️ Şehir merkezi anlık hava durumu çekiliyor...")
    current_center_data = fetch_current_weather()
    if current_center_data:
        insert_center_weather_data(current_center_data)
        
    print("✈️ Havalimanı (METAR) anlık verileri çekiliyor...")
    current_airport_data = fetch_airport_current_weather()
    if current_airport_data:
        insert_airport_weather_data(current_airport_data)
        
    print("-" * 40)
    
    #Günlük tahmin akışı
    print("🧹 Eski tahminler temizleniyor...")
    clean_old_forecasts()  #Eski tahmini silme
    
    print("📅 Tahmin verileri çekiliyor...")
    forecast_data = fetch_daily_forecast()
    if forecast_data:
        insert_daily_forecast(forecast_data)
        
    print("-" * 40)
    print("🎉 Pipeline turu başarıyla tamamlandı!")