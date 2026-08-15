# 1. Temel imaj olarak hafif bir Python sürümü seçiyoruz
FROM python:3.12-slim

# 2. İşletim sistemi seviyesindeki gerekli güncellemeleri ve derleme araçlarını kuruyoruz
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Konteyner içindeki çalışma dizinini belirliyoruz
WORKDIR /app

# 4. Önce sadece kütüphane listesini kopyalayıp kuruyoruz (Docker Cache'i verimli kullanmak için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Projemizdeki tüm kodları konteynerin içine kopyalıyoruz
COPY . .

# 6. Streamlit'in varsayılan portunu (8501) dışarıya açıyoruz
EXPOSE 8501

# 7. Konteyner ayağa kalktığında çalışacak olan ana komut
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]