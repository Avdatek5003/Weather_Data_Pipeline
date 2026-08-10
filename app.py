import streamlit as st
import pandas as pd
from src.database import get_db_connection
import plotly.express as px
import plotly.graph_objects as go
import pycountry
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime


from src.logger import get_logger

# Bu dosya için logger'ı başlatıyoruz
logger = get_logger(__name__)


#1. SAYFA AYARLARI
st.set_page_config(page_title="Weather Engineering Dashboard", page_icon="🌤️", layout="wide")

st.title("🌤️ Hava Durumu Canlı Dashboard")
st.markdown("Bu panel; kişisel veri boru hattımızdan geçip PostgreSQL'e yazılan **şehir merkezi modellerini, havalimanı saf METAR istasyon verilerini ve 1940'tan günümüze tarihsel kayıtları** göstermektedir.")

# 2. VERİ ÇEKME FONKSİYONLARI
@st.cache_data(ttl=300) #Veritabanını yormamak için 5 dk cache
def load_locations():
    conn = get_db_connection()
    if not conn: 
        logger.error("load_locations: Veritabanı bağlantısı kurulamadı.")
        return [], []
    cursor = conn.cursor()
    
    #Şehir merkezleri
    cursor.execute("SELECT DISTINCT city_name FROM cities ORDER BY city_name;")
    cities = [row[0] for row in cursor.fetchall()]
    
    #Havalimanları
    cursor.execute("SELECT DISTINCT airport_name FROM airports ORDER BY airport_name;")
    airports = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    logger.info(f"Arayüz için {len(cities)} şehir ve {len(airports)} havalimanı veritabanından yüklendi.")
    return cities, airports

@st.cache_data(ttl=300)
def load_latest_center_data(city_name):
    conn = get_db_connection()
    if not conn: 
        return pd.DataFrame()
    cursor = conn.cursor()
    query = """
    WITH RankedWeather AS (
        SELECT 
            c.city_name as location_name, c.country, c.latitude, c.longitude,
            h.record_time, h.temperature_c, h.apparent_temp_c as dewpoint_c, 
            h.humidity_pct, h.wind_speed_kmh, h.wind_direction_deg, 
            h.sea_level_pressure_hpa, h.precipitation_mm, NULL as wx_string,
            h.weather_code
        FROM center_hourly_weather_data h
        JOIN cities c ON h.city_id = c.city_id
        WHERE c.city_name = %s
    )
    SELECT * FROM RankedWeather ORDER BY record_time DESC LIMIT 1;
    """
    cursor.execute(query, (city_name,))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    if not df.empty:
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    cursor.close()
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_latest_airport_data(airport_name):
    conn = get_db_connection()
    if not conn: 
        return pd.DataFrame()
    cursor = conn.cursor()
    query = """
    WITH RankedWeather AS (
        SELECT 
            a.airport_name as location_name, a.country, a.latitude, a.longitude,
            h.record_time, h.temperature_c, h.dewpoint_c, 
            h.humidity_pct, h.wind_speed_kmh, h.wind_direction_deg, 
            h.sea_level_pressure_hpa, h.precipitation_mm, h.wx_string,
            NULL as weather_code
        FROM airport_hourly_weather_data h
        JOIN airports a ON h.airport_id = a.airport_id
        WHERE a.airport_name = %s
    )
    SELECT * FROM RankedWeather ORDER BY record_time DESC LIMIT 1;
    """
    cursor.execute(query, (airport_name,))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    if not df.empty:
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    cursor.close()
    conn.close()
    return df

@st.cache_data(ttl=3600)
def load_forecast_data(city_name):
    conn = get_db_connection()
    if not conn: 
        return pd.DataFrame()
    cursor = conn.cursor()
    query = """
    SELECT 
        f.forecast_date, f.max_temp_c, f.min_temp_c, 
        f.precipitation_sum_mm, f.max_wind_speed_kmh, f.wind_direction_deg, f.weather_code
    FROM daily_forecast_data f
    JOIN cities c ON f.city_id = c.city_id
    WHERE c.city_name = %s
    ORDER BY f.forecast_date;
    """
    cursor.execute(query, (city_name,))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    conn.close()
    return df

@st.cache_data(ttl=86400)
def load_historical_records(city_name):
    conn = get_db_connection()
    if not conn: 
        return {}
    cursor = conn.cursor()
    records = {}
    
    cursor.execute("SELECT date, tmax FROM historical_weather WHERE city_name = %s ORDER BY tmax DESC NULLS LAST LIMIT 1;", (city_name,))
    res = cursor.fetchone()
    records['max_temp'] = {"val": res[1], "date": res[0]} if res else {"val": "N/A", "date": "N/A"}
    
    cursor.execute("SELECT date, tmin FROM historical_weather WHERE city_name = %s ORDER BY tmin ASC NULLS LAST LIMIT 1;", (city_name,))
    res = cursor.fetchone()
    records['min_temp'] = {"val": res[1], "date": res[0]} if res else {"val": "N/A", "date": "N/A"}
    
    cursor.execute("SELECT date, prcp FROM historical_weather WHERE city_name = %s ORDER BY prcp DESC NULLS LAST LIMIT 1;", (city_name,))
    res = cursor.fetchone()
    records['max_prcp'] = {"val": res[1], "date": res[0]} if res else {"val": "N/A", "date": "N/A"}
    
    try:
        cursor.execute("SELECT date, snow FROM historical_weather WHERE city_name = %s ORDER BY snow DESC NULLS LAST LIMIT 1;", (city_name,))
        res = cursor.fetchone()
        records['max_snow'] = {"val": res[1], "date": res[0]} if res else {"val": "N/A", "date": "N/A"}
    except Exception as e:
        conn.rollback()
        records['max_snow'] = {"val": "-", "date": "-"}
        
    cursor.close()
    conn.close()
    return records

@st.cache_data(ttl=86400)
def load_yearly_precipitation(city_name):
    conn = get_db_connection()
    if not conn: 
        return pd.DataFrame()
    cursor = conn.cursor()
    query = """
    SELECT 
        EXTRACT(YEAR FROM date) as year,
        SUM(prcp) as yearly_prcp
    FROM historical_weather 
    WHERE city_name = %s
    GROUP BY EXTRACT(YEAR FROM date)
    ORDER BY year;
    """
    cursor.execute(query, (city_name,))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    if not df.empty:
        df['year'] = df['year'].astype(int)
    cursor.close()
    conn.close()
    return df

@st.cache_data(ttl=86400)
def load_monthly_averages(city_name):
    conn = get_db_connection()
    if not conn: 
        return pd.DataFrame()
    cursor = conn.cursor()
    query = """
    WITH MonthlyTotals AS (
        SELECT 
            EXTRACT(YEAR FROM date) as year,
            EXTRACT(MONTH FROM date) as month,
            AVG(tmax) as avg_tmax,
            AVG(tmin) as avg_tmin, 
            SUM(prcp) as total_prcp
        FROM historical_weather 
        WHERE city_name = %s
        GROUP BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date)
    )
    SELECT 
        month,
        AVG(avg_tmax) as avg_tmax,
        AVG(avg_tmin) as avg_tmin,
        AVG(total_prcp) as avg_prcp
    FROM MonthlyTotals
    GROUP BY month
    ORDER BY month;
    """
    cursor.execute(query, (city_name,))
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    conn.close()
    return df

#3. YARDIMCI FONKSİYONLAR

def get_local_time(lat, lon):
    try:
        if pd.isna(lat) or pd.isna(lon):
            return "Bilinmiyor"
            
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=float(lon), lat=float(lat))
        
        if tz_name:
            tz = pytz.timezone(tz_name)
            local_time = datetime.now(tz)
            return local_time.strftime("%d %m %Y - %H:%M") 
    except Exception as e:
        logger.warning(f"Yerel saat hesaplanamadı: {e}")
        return "Bilinmiyor"

def format_city_time(dt_val, lat, lon):
    """Veritabanından gelen sistem saatini (Türkiye), hedeflenen şehrin yerel saatine çevirir."""
    try:
        if pd.isna(lat) or pd.isna(lon) or pd.isnull(dt_val):
            return str(dt_val)
            
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=float(lon), lat=float(lat))
        
        if tz_name:
            target_tz = pytz.timezone(tz_name)
            system_tz = pytz.timezone('Europe/Istanbul') 
            
            dt = pd.to_datetime(dt_val)
            
            #Eğer veritabanından gelen saatin bir dilimi yoksa onu sistem saati olarak etiketle
            if dt.tzinfo is None:
                dt = system_tz.localize(dt)
                
            #Sistemi saatini hedeflenen şehrin saat dilimine dönüştür
            city_time = dt.astimezone(target_tz)
            return city_time.strftime("%d %b %Y - %H:%M")
            
    except Exception as e:
        logger.warning(f"Ölçüm saati dönüştürülemedi: {e}")
        return str(dt_val)
        
    return str(dt_val)

def deg_to_compass(d):
    if pd.isna(d): return ""
    try:
        d_val = float(d)
    except:
        return ""
    dirs = ["⬇️ K", "↙️ KD", "⬅️ D", "↖️ GD", "⬆️ G", "↗️ GB", "➡️ B", "↘️ KB"]
    ix = int((d_val + 22.5) / 45) % 8
    return dirs[ix]

def get_weather_desc(code):
    if pd.isna(code): return "❓ Bilinmiyor"
    mapping = {
        0: "☀️ Açık",
        1: "🌤️ Az Bulutlu", 2: "⛅ Parçalı Bulutlu", 3: "☁️ Çok Bulutlu",
        45: "🌫️ Sisli", 48: "🌫️ Kırağılı Sis",
        51: "🌦️ Hafif Çisenti", 53: "🌦️ Çisenti", 55: "🌦️ Yoğun Çisenti",
        56: "🌧️ Dondurucu Çisenti", 57: "🌧️ Yoğun Dondurucu Çisenti",
        61: "🌧️ Hafif Yağmur", 63: "🌧️ Yağmur", 65: "🌧️ Şiddetli Yağmur",
        66: "🌨️ Dondurucu Yağmur", 67: "🌨️ Şiddetli Don. Yağmur",
        71: "🌨️ Hafif Kar", 73: "🌨️ Kar", 75: "❄️ Yoğun Kar",
        77: "❄️ Kar Taneleri",
        80: "🌦️ Hafif Sağanak", 81: "🌦️ Sağanak", 82: "⛈️ Şiddetli Sağanak",
        85: "🌨️ Kar Sağanağı", 86: "❄️ Şiddetli Kar Sağanağı",
        95: "⛈️ Gök Gürültülü", 96: "⛈️ Dolulu Fırtına", 99: "⛈️ Şiddetli Fırtına"
    }
    return mapping.get(int(code), "☁️ Bilinmiyor")


# 4. ARAYÜZ (UI) İNŞASI

cities, airports = load_locations()
if not cities and not airports:
    logger.error("Arayüz başlatılamadı: Veritabanı tabloları boş!")
    st.error("Veritabanına bağlanılamadı veya tablolar boş!")
    st.stop()
    
#Yenileme ekranı
with st.sidebar:
    st.markdown("### ⚙️ Panel Kontrolleri")
    if st.button("🔄 Verileri Yenile"):
        logger.info("Kullanıcı arayüz üzerinden verileri yenileme talebinde bulundu. Önbellek temizleniyor...")
        st.cache_data.clear()
        st.success("Hafıza temizlendi! En taze veriler getiriliyor...")
        st.rerun()

#Şehir veya havalimanı seç alanı
source_type = st.radio("🔍 Veri Kaynağı Türü:", ["🏙️ Şehir Merkezleri (Open-Meteo)", "✈️ Havalimanları (METAR İstasyonları)"], horizontal=True)

if "Şehir" in source_type:
    selected_location = st.selectbox("🌍 İncelemek İstediğiniz Şehri Seçin:", cities)
    is_airport = False
else:
    selected_location = st.selectbox("✈️ İncelemek İstediğiniz Havalimanını Seçin:", airports)
    is_airport = True

st.divider()

#BÖLÜM 1: ÜST PANEL (ANLIK DURUM VE HARİTA)
if not is_airport:
    df_latest = load_latest_center_data(selected_location)
else:
    df_latest = load_latest_airport_data(selected_location)

if not df_latest.empty:
    col_info, col_map = st.columns([1, 1])
    
    with col_info:
        raw_country = df_latest['country'].iloc[0] if 'country' in df_latest.columns else "Bilinmiyor"
        raw_wx = df_latest['wx_string'].iloc[0] if 'wx_string' in df_latest.columns else None
        
        if is_airport:
            current_weather = f"📡 METAR Kod: {raw_wx}" if raw_wx else "📡 Saf Havalimanı İstasyon Verisi"
            title_prefix = "✈️ Havalimanı Canlı Durum"
        else:
            w_code = df_latest['weather_code'].iloc[0] if 'weather_code' in df_latest.columns else None
            weather_text = get_weather_desc(w_code)
            current_weather = f"{weather_text} <span style='font-size:14px; color:gray;'>(Open-Meteo)</span>"
            title_prefix = "📍 Şehir Merkezi Canlı Durum"
            
        st.subheader(f"{title_prefix}: {selected_location}, {raw_country}")
        
        #Yerel saati hesaplama
        lat = df_latest['latitude'].iloc[0]
        lon = df_latest['longitude'].iloc[0]
        
        #Şehrin o anki saati
        local_time_str = get_local_time(lat, lon)
        
        #O şehrin ölçüm saati
        record_time_raw = df_latest['record_time'].iloc[0]
        record_time_local = format_city_time(record_time_raw, lat, lon)
        
        st.write(f"**Güncel Durum:** <span style='color:#48cae4; font-size:22px; font-weight:bold;'>{current_weather}</span>", unsafe_allow_html=True)
        st.markdown(f"🕒 **Şehrin Yerel Saati:** <span style='font-size:18px; color:#fca311; font-weight:bold;'>{local_time_str}</span>", unsafe_allow_html=True)
        st.caption(f"📡 Ölçüm / Okuma Saati (Şehrin Yerel Saatiyle): `{record_time_local}`")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ Sıcaklık", f"{df_latest['temperature_c'].iloc[0]:.1f} °C")
        c2.metric("💧 Çiğ Noktası", f"{df_latest['dewpoint_c'].iloc[0]:.1f} °C" if pd.notna(df_latest['dewpoint_c'].iloc[0]) else "N/A")
        c3.metric("💦 Nem", f"% {df_latest['humidity_pct'].iloc[0]:.1f}" if pd.notna(df_latest['humidity_pct'].iloc[0]) else "N/A")
        
        c4, c5, c6 = st.columns(3)
        wind_dir = deg_to_compass(df_latest['wind_direction_deg'].iloc[0])
        c4.metric("💨 Rüzgar", f"{df_latest['wind_speed_kmh'].iloc[0]:.1f} km/h", f"Yön: {wind_dir}", delta_color="off")
        c5.metric("🌧️ Yağış", f"{df_latest['precipitation_mm'].iloc[0]:.1f} mm")
        c6.metric("⏱️ Basınç", f"{df_latest['sea_level_pressure_hpa'].iloc[0]:.1f} hPa" if pd.notna(df_latest['sea_level_pressure_hpa'].iloc[0]) else "N/A")
        
    with col_map:
        fig_map = px.scatter_mapbox(
            df_latest, lat="latitude", lon="longitude", hover_name="location_name",
            hover_data={"latitude": False, "longitude": False, "temperature_c": True},
            color_discrete_sequence=["#ef233c"], zoom=8, height=300  
        )
        
        fig_map.update_layout(
            mapbox_style="open-street-map", 
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ Bu lokasyon için anlık saatlik veri bulunamadı.")


#BÖLÜM 2: 5 GÜNLÜK TAHMİN (Sadece şehirler)
if not is_airport:
    st.subheader("📅 5 Günlük Tahmin")
    df_forecast = load_forecast_data(selected_location)

    if not df_forecast.empty:
        cols = st.columns(len(df_forecast.head(5)))
        for idx, row in df_forecast.head(5).iterrows():
            with cols[idx]:
                date_str = pd.to_datetime(row['forecast_date']).strftime("%d %b")
                daily_weather = get_weather_desc(row['weather_code'])
                
                st.markdown(f"**{date_str}**")
                st.markdown(f"*{daily_weather}*")
                st.write(f"🌡️ {row['max_temp_c']:.1f}° / {row['min_temp_c']:.1f}°")
                st.write(f"🌧️ {row['precipitation_sum_mm']:.1f} mm")
                st.write(f"💨 {deg_to_compass(row['wind_direction_deg'])}")
    else:
        st.info("Bu lokasyon için tahmin verisi bulunamadı.")

    st.divider()

    #BÖLÜM 3: TARİHSEL VERİLER (1940 - 2026)
    st.markdown("<h2 style='text-align: center; color: #1f2aa0;'>🏛️ Veriseti Ekstremleri (Model Kayıtları)</h2>", unsafe_allow_html=True)

    #Kaynak bilgilendirme
    st.info("💡 **Veri Altyapısı ve Kaynakçası:** Bu paneldeki tarihsel rekorlar ve iklim analizleri **Meteostat (Reanalysis)** veri setinden ve **Openmeteo Weather APİ** verisetinden beslenmektedir.")

    records = load_historical_records(selected_location)

    def format_val(val):
        try:
            return f"{float(val):.1f}"
        except:
            return val

    c_max_t, c_min_t, c_max_p, c_max_s = st.columns(4)

    with c_max_t:
        st.info("🔥 **Maksimum Sıcaklık**")
        st.markdown(f"### {format_val(records.get('max_temp', {}).get('val'))} °C")
        st.caption(f"📅 {records.get('max_temp', {}).get('date')}")

    with c_min_t:
        st.info("🧊 **Minimum Sıcaklık**")
        st.markdown(f"### {format_val(records.get('min_temp', {}).get('val'))} °C")
        st.caption(f"📅 {records.get('min_temp', {}).get('date')}")

    with c_max_p:
        st.info("🌧️ **Maksimum Yağış**")
        st.markdown(f"### {format_val(records.get('max_prcp', {}).get('val'))} mm")
        st.caption(f"📅 {records.get('max_prcp', {}).get('date')}")

    with c_max_s:
        st.info("❄️ **Maksimum Kar**")
        st.markdown(f"### {format_val(records.get('max_snow', {}).get('val'))} mm")
        st.caption(f"📅 {records.get('max_snow', {}).get('date')}")

    st.write("")

    #BÖLÜM 4: AYLIK ORTALAMALAR GRAFİĞİ
    df_monthly = load_monthly_averages(selected_location)

    if not df_monthly.empty:
        st.subheader("📊 Aylık İklim Ortalamaları Analizi")
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        df_monthly['ay_ismi'] = df_monthly['month'].apply(lambda x: aylar[int(x)-1])
        
        col_temp, col_prcp = st.columns(2)
        
        with col_temp:
            fig_temp = px.line(
                df_monthly, x="ay_ismi", y=["avg_tmax", "avg_tmin"],
                labels={"value": "Sıcaklık (°C)", "ay_ismi": "Ay", "variable": "Sıcaklık Türü"},
                title="🌡️ Ort. Maksimum ve Minimum Sıcaklıklar",
                markers=True
            )
            fig_temp.data[0].name = "Max Sıcaklık"
            fig_temp.data[0].line.color = "#ef233c" 
            fig_temp.data[1].name = "Min Sıcaklık"
            fig_temp.data[1].line.color = "#1f2aa0"
            
            fig_temp.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_temp, use_container_width=True)
            
        with col_prcp:
            fig_prcp = px.bar(
                df_monthly, x="ay_ismi", y="avg_prcp",
                labels={"avg_prcp": "Toplam Yağış (mm)", "ay_ismi": "Ay"},
                title="🌧️ Ort. Aylık Toplam Yağış Miktarı",
                text_auto=".1f",
                color_discrete_sequence=["#48cae4"]
            )
            fig_prcp.update_traces(textposition="outside")
            st.plotly_chart(fig_prcp, use_container_width=True)

        st.subheader("📑 Ay-Ay İklim Verileri Tablosu")
        df_display = df_monthly[['ay_ismi', 'avg_tmax', 'avg_tmin', 'avg_prcp']].copy()
        df_display.columns = ["Ay", "Ort. Max Sıcaklık (°C)", "Ort. Min Sıcaklık (°C)", "Ort. Toplam Yağış (mm)"]
        
        for col in df_display.columns[1:]:
             df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}")
             
        st.dataframe(df_display, use_container_width=True, hide_index=True)

 
    
#BÖLÜM 5: YILLIK TOPLAM YAĞIŞ TRENDİ
df_yearly = load_yearly_precipitation(selected_location)

if not df_yearly.empty:
    st.subheader("📅 Yıllara Göre Toplam Yağış Eğilimi (1940 - 2026)")
    
    
    #2026 yılını hesap etmiyoruz
    df_calc = df_yearly[(df_yearly['year'] != 2026) & (df_yearly['yearly_prcp'] > 0)]
    
    # 2. Kalan yıllar üzerinden geçici bir ortalama hesaplıyoruz
    initial_mean = df_calc['yearly_prcp'].mean()
    
    #Ortalamanın %20 sinden daha eksik olan  yılları dışlıyoruz eksik veri ihtimali
    df_robust = df_calc[df_calc['yearly_prcp'] >= (initial_mean * 0.20)]
    
    #Temizlenmiş datasetten yeni ortalama hesabı
    robust_mean_prcp = df_robust['yearly_prcp'].mean()
    
    # --- GRAFİK ÇİZİMİ ---
    #Grafiği df_yearly ile çiziyoruz ki barda eksik/düşük yılları görsel olarak tespit edebilelim
    fig_yearly = px.bar(
        df_yearly, x="year", y="yearly_prcp",
        labels={"yearly_prcp": "Yıllık Toplam Yağış (mm)", "year": "Yıl"},
        color_discrete_sequence=["#0077b6"]
    )
    
    #Ortalama çizgisi
    fig_yearly.add_hline(
        y=robust_mean_prcp, 
        line_dash="dash", 
        line_color="#ef233c",
        line_width=2
    )
    
    fig_yearly.update_layout(
        hovermode="x unified",
        title=dict(
            text=f"Ortalama Yıllık Yağış(1940-2025): {robust_mean_prcp:.1f} mm", 
            font=dict(size=12, color="gray")
        )
    )
    st.plotly_chart(fig_yearly, use_container_width=True)

st.divider()