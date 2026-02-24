from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uvicorn
import os

from src.data_processing.satellite_data import EnhancedSatelliteDataCollector
from src.data_processing.acoustic_sensor import AdvancedAcousticDetector
from src.ml_models.fusion_model import EnhancedMiningDetector

app = FastAPI(title="Auralite API v2.0", description="Enhanced Illegal Mining Detection System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
satellite_collector = EnhancedSatelliteDataCollector()
detector = EnhancedMiningDetector()

# Load models if they exist
try:
    detector.load_models()
    print("Models loaded successfully.")
except:
    print("No trained models found. Please run training script.")

# Data models
class Location(BaseModel):
    lat: float
    lon: float
    radius: float = 5.0

class DetectionRequest(BaseModel):
    location: Location
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    use_acoustic: bool = True
    use_satellite: bool = True

@app.get("/")
async def root():
    return {"message": "Auralite API v2.0 Active", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_trained": detector.is_trained}

@app.post("/api/detect")
async def detect(request: DetectionRequest):
    if not detector.is_trained:
        raise HTTPException(status_code=400, detail="Model not trained.")
    
    # In a real scenario, this would trigger data collection
    # For demo/test, we'll use a placeholder logic or dummy data
    # Here we simulate the feature extraction
    dummy_features = {
        'ndvi_mean': 0.35, 'ndvi_trend': -0.05, 'ndvi_volatility': 0.1,
        'ndvi_min': 0.2, 'ndvi_max': 0.5,
        'nightlight_mean': 15.0, 'nightlight_trend': 2.0,
        'nightlight_peak': 25.0, 'nightlight_volatility': 4.0,
        'acoustic_activity': 5, 'drilling_freq': 120.0,
        'excavator_freq': 80.0, 'max_confidence': 0.85
    }
    
    result = detector.predict(dummy_features)
    result['location'] = request.location.dict()
    result['timestamp'] = datetime.now().isoformat()
    
    return result

@app.post("/api/sensor/data")
async def sensor_data(sensor_id: str, file: UploadFile = File(...)):
    # Save and process sensor data
    content = await file.read()
    # In production: detector_acoustic = AdvancedAcousticDetector(sensor_id)
    # result = detector_acoustic.process_chunk(audio_bytes)
    return {"message": "Data received", "size": len(content)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
