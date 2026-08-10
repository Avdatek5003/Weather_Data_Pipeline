import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(module_name):
    """Merkezi Loglama Sistemi"""
    
    #log klasörünün olduğundan emin olma
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG) #Tüm log seviyelerini yakalamak

    # Log formatı: Tarih - Modül - Seviye - Mesaj
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Terminal (Console) Çıktısı Handler'ı
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) #Ekranda sadece INFO ve üstünü göster
    console_handler.setFormatter(formatter)

    # 2. Dosya (File) Çıktısı Handler'ı
    #Log dosyası çok şişmesin diye 5 MB'a ulaşınca yeni dosyaya geçer
    log_file = os.path.join(log_dir, 'pipeline.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Dosyaya her detayı (DEBUG dahil) yaz
    file_handler.setFormatter(formatter)

    #Eğer logger'a daha önce handler eklenmemişse ekleyerek log tekrarı önleme
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger