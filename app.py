import streamlit as st
import pandas as pd
from src.database import get_db_connection
import plotly.express as px

# 1.Sayfa Ayarları (Tam ekran ve ikon)
st.set_page_config(page_title="Weather Engineering Dashboard", page_icon="🌤️", layout="wide")

st.title("🌤️ Hava Durumu Canlı Dashboard")
st.markdown("Bu panel, veri boru hattımızdan geçip PostgreSQL'e yazılan **en güncel** verileri göstermektedir.")

# 2.Veritabanından Sadece En Son Çekilen Veriyi Alma Fonksiyonu
def load_latest_data():
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
        
    cursor = conn.cursor()
    
    #Haritada göstermek için enlem/boylam (latitude/longitude) da çekiyoruz
    query = """
    WITH RankedWeather AS (
        SELECT 
            c.city_name,
            c.country,
            c.latitude,
            c.longitude,
            h.record_time,
            h.temperature_c,
            h.apparent_temp_c,
            h.humidity_pct,
            h.wind_speed_kmh,
            -- Her şehri kendi içinde grupla (PARTITION BY) ve zamana göre en yeniden eskiye sırala
            ROW_NUMBER() OVER(PARTITION BY c.city_id ORDER BY h.record_time DESC, h.log_id DESC) as rn
        FROM hourly_weather_data h
        JOIN cities c ON h.city_id = c.city_id
    )
    -- rn = 1 demek, her şehrin kendi içindeki EN YENİ (1. sıradaki) verisini getir demektir.
    SELECT * FROM RankedWeather WHERE rn = 1;
    """
    
    cursor.execute(query)
    #Sütun isimlerini dinamik olarak al
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    # Veriyi Pandas DataFrame'e çevir
    df = pd.DataFrame(data, columns=columns)
    
    #Decimal to float
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    
    cursor.close()
    conn.close()
    return df
    
    cursor.close()
    conn.close()
    return df


#5 Günlük Tahmin Verisini Çekme Fonksiyonu
def load_forecast_data():
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
        
    cursor = conn.cursor()
    query = """
    SELECT 
        c.city_name,
        f.forecast_date,
        f.max_temp_c,
        f.min_temp_c,
        f.precipitation_sum_mm,
        f.max_wind_speed_kmh,
        f.wind_direction_deg
    FROM daily_forecast_data f
    JOIN cities c ON f.city_id = c.city_id
    ORDER BY c.city_name, f.forecast_date;
    """
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df_forecast = pd.DataFrame(data, columns=columns)
    
    cursor.close()
    conn.close()
    return df_forecast


df = load_latest_data()

df_forecast = load_forecast_data()

#Tabs oluşturma
tab1, tab2 = st.tabs(["🌍 Anlık Durum & Harita", "📅 5 Günlük Tahmin Analizi"])

#Anlık durum sekmesi
with tab1:
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 En Güncel Metrikler")
            display_df = df[['city_name', 'country', 'record_time', 'temperature_c', 'apparent_temp_c', 'humidity_pct', 'wind_speed_kmh']]
            st.dataframe(display_df, use_container_width=True)
            
        with col2:
            st.subheader("📍 Şehirlerin Konumu ve Sıcaklıkları")
            # Plotly Haritası
            fig = px.scatter_mapbox(
                df, lat="latitude", lon="longitude", hover_name="city_name",
                hover_data={"latitude": False, "longitude": False, "temperature_c": True, "country": True},
                color="temperature_c", color_continuous_scale=px.colors.sequential.Turbo, 
                zoom=3, height=500
            )
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Anlık veri bulunamadı. Lütfen main.py'yi çalıştırın.")

#5 günlük tahmin ekranı
with tab2:
    st.subheader("📈 Şehirlere Göre 5 Günlük Hava Durumu Analizi")
    
    if not df_forecast.empty:
        selected_city = st.selectbox("Tahminini görmek istediğiniz şehri seçin:", df_forecast['city_name'].unique())
        
        # Filtreleme yaparken kopyasını alıyoruz ki Pandas uyarı vermesin
        city_data = df_forecast[df_forecast['city_name'] == selected_city].copy()
        
        # DERECEYİ YÖNLERE VE EMOJİLERE ÇEVİREN FONKSİYON
        def deg_to_compass(d):
            if pd.isna(d): return "Bilinmiyor"
            dirs = ["⬇️ Kuzey'den", "↙️ Kuzeydoğu'dan", "⬅️ Doğu'dan", "↖️ Güneydoğu'dan", 
                    "⬆️ Güney'den", "↗️ Güneybatı'dan", "➡️ Batı'dan", "↘️ Kuzeybatı'dan"]
            ix = int((d + 22.5) / 45) % 8
            return dirs[ix]
            
        #Rüzgar yönü sütunu
        city_data['Rüzgar Yönü'] = city_data['wind_direction_deg'].apply(deg_to_compass)
        
        # 1. ANA GRAFİK: Sıcaklık
        fig_temp = px.line(
            city_data, x="forecast_date", y=["max_temp_c", "min_temp_c"],
            labels={"value": "Sıcaklık (°C)", "forecast_date": "Tarih", "variable": "Sıcaklık Değeri"},
            title=f"🌡️ {selected_city} Beklenen Sıcaklık Değişimi", markers=True
        )
        fig_temp.data[0].name = "Maksimum Sıcaklık"
        fig_temp.data[1].name = "Minimum Sıcaklık"
        fig_temp.data[0].line.color = "#ef233c" 
        fig_temp.data[1].line.color = "#1f2aa0" 
        st.plotly_chart(fig_temp, use_container_width=True)
        
        col_precip, col_wind = st.columns(2)
        
        with col_precip:
            # 2. ALT GRAFİK: Yağış
            fig_precip = px.bar(
                city_data, x="forecast_date", y="precipitation_sum_mm",
                labels={"precipitation_sum_mm": "Toplam Yağış (mm)", "forecast_date": "Tarih"},
                title="🌧️ Beklenen Yağış Miktarı", text_auto=True, color_discrete_sequence=["#48cae4"]
            )
            fig_precip.update_traces(textposition="outside")
            st.plotly_chart(fig_precip, use_container_width=True)
            
        with col_wind:
            # 3. ALT GRAFİK: Rüzgar (Hover Data ile Yön Ekleme)
            fig_wind = px.line(
                city_data, x="forecast_date", y="max_wind_speed_kmh",
                hover_data={"Rüzgar Yönü": True, "forecast_date": False}, # Üzerine gelince rüzgar yönü çıkacak
                labels={"max_wind_speed_kmh": "Rüzgar Hızı (km/h)", "forecast_date": "Tarih"},
                title="💨 Maksimum Rüzgar Şiddeti ve Yönü", markers=True, color_discrete_sequence=["#ffb703"]
            )
            fig_wind.update_traces(fill='tozeroy') 
            st.plotly_chart(fig_wind, use_container_width=True)
        
        #Yön sütununu da detaylı tabloya dahil ettik
        st.divider() 
        st.write(f"**📑 {selected_city} İçin Detaylı Tahmin Verileri:**")
        display_forecast_df = city_data[['forecast_date', 'max_temp_c', 'min_temp_c', 'precipitation_sum_mm', 'max_wind_speed_kmh', 'Rüzgar Yönü']]
        st.dataframe(display_forecast_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ Tahmin verisi bulunamadı. Lütfen önce main.py'yi çalıştırıp veri çekin.")