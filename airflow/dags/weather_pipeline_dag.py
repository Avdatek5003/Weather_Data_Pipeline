from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum


from src.extract import fetch_current_weather, fetch_airport_current_weather, fetch_daily_forecast
from src.load import insert_center_weather_data, insert_airport_weather_data, insert_daily_forecast, clean_old_forecasts

#1. Adım: Airflow Görev (Task) Fonksiyonlarını Tanımlama
#Airflow'un PythonOperator'ü bu fonksiyonları tetikleyecek. 


def process_center_weather():
    current_center_data = fetch_current_weather()
    if current_center_data:
        insert_center_weather_data(current_center_data)

def process_airport_weather():
    current_airport_data = fetch_airport_current_weather()
    if current_airport_data:
        insert_airport_weather_data(current_airport_data)

def process_daily_forecast():
    clean_old_forecasts() 
    forecast_data = fetch_daily_forecast()
    if forecast_data:
        insert_daily_forecast(forecast_data)

# . Adım: DAGın Genel Ayarları
default_args = {
    'owner': 'ahmet',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2026, 8, 14, tz="Europe/Istanbul"), 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

#3. Adım: DAG'ı Tanımlama
with DAG(
    'weather_etl_pipeline',
    default_args=default_args,
    description='Merkez, Havalimanı ve Tahmin verilerini çeken tam otomatik boru hattı',
    schedule='*/30 * * * *', #Her 30 dakikada bir çalıştır
    catchup=False, #Geçmiş günlerdeki kaçırılan görevleri çalıştırma
    tags=['weather', 'etl', 'production']
) as dag:

    #Görev 1:Şehir Merkezi Verileri
    task_center = PythonOperator(
        task_id='extract_and_load_center',
        python_callable=process_center_weather
    )

    #Görev 2:Havalimanı METAR Verileri
    task_airport = PythonOperator(
        task_id='extract_and_load_airport',
        python_callable=process_airport_weather
    )

    #Görev 3:5 Günlük Tahmin Verileri
    task_forecast = PythonOperator(
        task_id='extract_and_load_forecast',
        python_callable=process_daily_forecast
    )

    #4. Adım:Görevlerin Sıralaması (Dependencies)
    
    [task_center, task_airport] >> task_forecast