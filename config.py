import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aravalli-hills-secret-2026'
    
    # Aravalli specific configuration
    ARAVALLI_BOUNDS = {
        'min_lat': 23.5,
        'max_lat': 28.5,
        'min_lon': 72.5,
        'max_lon': 77.5,
    }
    
    # Critical monitoring zones based on NGT directives
    CRITICAL_ZONES = [
        {'name': 'Sariska Tiger Reserve', 'lat': 27.0, 'lon': 76.5, 'radius': 15},
        {'name': 'Alwar District', 'lat': 27.5, 'lon': 76.5, 'radius': 20},
        {'name': 'Gurugram', 'lat': 28.4, 'lon': 77.0, 'radius': 10},
        {'name': 'Nuh', 'lat': 28.1, 'lon': 77.0, 'radius': 15},
        {'name': 'Faridabad', 'lat': 28.4, 'lon': 77.3, 'radius': 10},
        {'name': 'Mount Abu', 'lat': 24.6, 'lon': 72.7, 'radius': 15},
    ]
    
    # Detection thresholds
    NDVI_ALERT_THRESHOLD = 0.3
    NIGHTLIGHT_ALERT_THRESHOLD = 15
    ACOUSTIC_CONFIDENCE_THRESHOLD = 0.75
    CHANGE_DETECTION_SENSITIVITY = 0.2
    
    # Notification settings
    NOTIFICATION_REFRESH_INTERVAL = 5
    ENABLE_SOUND_ALERTS = True
