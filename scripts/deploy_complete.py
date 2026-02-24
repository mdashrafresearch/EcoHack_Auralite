#!/usr/bin/env python3
"""
Complete deployment script for Auralite v2.0
"""
import os
import subprocess
import sys
import time
from pathlib import Path

def setup_environment():
    print("🚀 Setting up Auralite Environment...")
    dirs = [
        'data/raw/satellite', 'data/raw/acoustic',
        'data/processed/ndvi', 'data/processed/nightlight',
        'data/processed/audio_features',
        'models/checkpoints', 'models/ensemble',
        'logs', 'config', 'notebooks/analysis', 'scripts'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {d}")
    return True

def train_initial_model():
    print("\n🧠 Training Initial Enhanced Model...")
    from src.ml_models.fusion_model import EnhancedMiningDetector
    import numpy as np
    
    detector = EnhancedMiningDetector()
    
    # Generate synthetic training data
    n_samples = 1000
    synthetic_data = []
    for i in range(n_samples):
        is_mining = 1 if np.random.random() > 0.7 else 0
        record = {
            'ndvi_mean': np.random.normal(0.3, 0.1) if is_mining else np.random.normal(0.6, 0.1),
            'ndvi_trend': np.random.normal(-0.1, 0.05) if is_mining else np.random.normal(0, 0.02),
            'ndvi_volatility': np.random.exponential(0.1),
            'ndvi_min': 0.2, 'ndvi_max': 0.8,
            'nightlight_mean': np.random.exponential(20) if is_mining else np.random.exponential(5),
            'nightlight_trend': np.random.normal(2, 1) if is_mining else np.random.normal(0, 0.5),
            'nightlight_peak': 30, 'nightlight_volatility': 5,
            'acoustic_activity': np.random.poisson(10) if is_mining else np.random.poisson(2),
            'drilling_freq': np.random.normal(150, 50) if is_mining else 0,
            'excavator_freq': np.random.normal(100, 30) if is_mining else 0,
            'max_confidence': 0.9,
            'is_mining': is_mining,
            'severity': np.random.randint(0, 3) if is_mining else 0,
            'equipment_type': np.random.randint(1, 5) if is_mining else 0
        }
        synthetic_data.append(record)
    
    detector.train(synthetic_data, epochs=20)
    detector.save_models()
    print("  ✅ Models trained and saved to models/ensemble/")
    return True

def create_docker_prod():
    print("\n🐳 Creating Docker Configuration...")
    dockerfile_content = """
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ libsndfile1 ffmpeg libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 auralite && chown -R auralite:auralite /app
USER auralite
EXPOSE 8000 8501
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0"]
"""
    with open('Dockerfile.prod', 'w') as f:
        f.write(dockerfile_content)
    print("  ✅ Dockerfile.prod created")
    return True

if __name__ == "__main__":
    setup_environment()
    try:
        # We need to make sure src is in path for training
        sys.path.append(os.getcwd())
        train_initial_model()
    except Exception as e:
        print(f"❌ Training failed (likely missing deps): {e}")
    create_docker_prod()
    print("\n✅ Deployment Setup Complete!")
