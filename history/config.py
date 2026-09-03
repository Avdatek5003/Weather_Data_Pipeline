# src/config.py

# Şehirlerin Tarihi Ekstrem Değerleri Kılavuzu (Sanity Check Thresholds)
CITY_THRESHOLDS = {
    
    
    "Seul": {"max_temp": 39.6,"min_temp": -23.1, "max_prcp": 354.7,"max_snow": 31.0 },

    "Rio de Janeiro": {"max_temp": 43.2, "min_temp": 4.8, "max_prcp": 360.2,"max_snow": 0.0 },

    "Ottawa": { "max_temp": 37.8, "min_temp": -38.9,"max_prcp": 109.0,"max_snow": 97.0},

    "Atina": {"max_temp": 44.8,"min_temp": -6.5, "max_prcp": 150.2,"max_snow": 25.0 }

}

    
    


# Hibrit Lokasyon ve İstasyon Kaynakları Sözlüğü
LOCATION_SOURCES = {
    
    "Seul": {"type": "point","lat": 37.57, "lon": 126.97 },

    "Rio de Janeiro": {"type": "point", "lat": -22.82,"lon": -43.25 },

    "Ottawa": {"type": "point", "lat": 45.32, "lon": -75.67 },

    "Atina": {"type": "point","lat": 37.97,"lon": 23.72 }
    
}


