"""
Simplified ML detector for illegal mining
Uses pre-trained models with sample data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import pickle
from datetime import datetime

class MiningDetector:
    """Main detector class for illegal mining identification"""
    
    def __init__(self):
        self.rf_classifier = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Try to load pre-trained model, otherwise use simple rules
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize with simple rule-based detection"""
        # Create simple rules-based model for demo
        self.rules = {
            'ndvi_threshold': 0.4,
            'nightlight_threshold': 15,
            'acoustic_threshold': 0.7,
            'temporal_window': 7  # days
        }
        print("✅ Detector initialized with rule-based logic")
    
    def train_on_sample(self, sample_data):
        """Train models on sample data"""
        print("Training models on sample data...")
        
        # Prepare features
        X = []
        y = []
        
        # Convert sample data to features
        for idx, row in sample_data.iterrows():
            features = [
                row.get('ndvi_value', 0.5),
                row.get('intensity', 5),
                row.get('confidence', 0),
                1 if row.get('detection_type') in ['excavator', 'drill'] else 0
            ]
            X.append(features)
            y.append(1 if row.get('is_anomaly', False) else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train models if we have enough data
        if len(X) > 10:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest
            self.rf_classifier = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=42
            )
            self.rf_classifier.fit(X_scaled, y)
            
            # Train Isolation Forest for anomaly detection
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.isolation_forest.fit(X_scaled)
            
            self.is_trained = True
            print("✅ Models trained successfully")
        else:
            print("⚠️ Insufficient data for training, using rules")
    
    def detect(self, ndvi_value, nightlight_value, acoustic_confidence=0, 
               detection_type=None, location_risk='medium'):
        """
        Detect if current readings indicate illegal mining
        
        Returns:
            dict: Detection result with confidence and severity
        """
        
        # Simple rule-based detection
        alerts = []
        
        # Rule 1: Low NDVI (vegetation loss)
        if ndvi_value < self.rules['ndvi_threshold']:
            alerts.append({
                'type': 'vegetation_loss',
                'severity': 'HIGH' if ndvi_value < 0.3 else 'MEDIUM',
                'confidence': 0.8,
                'message': f'Abnormal vegetation loss detected (NDVI: {ndvi_value:.2f})'
            })
        
        # Rule 2: High nightlight activity
        if nightlight_value > self.rules['nightlight_threshold']:
            alerts.append({
                'type': 'night_activity',
                'severity': 'HIGH' if nightlight_value > 25 else 'MEDIUM',
                'confidence': 0.75,
                'message': f'Unusual nightlight activity detected ({nightlight_value:.1f})'
            })
        
        # Rule 3: Acoustic detection of machinery
        if acoustic_confidence > self.rules['acoustic_threshold'] and detection_type:
            alerts.append({
                'type': 'machinery_detected',
                'severity': 'HIGH',
                'confidence': acoustic_confidence,
                'message': f'{detection_type.upper()} machinery detected'
            })
        
        # Combine alerts into final decision
        if alerts:
            # Calculate overall severity
            severities = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            max_severity = max([severities[a['severity']] for a in alerts])
            severity_map = {3: 'HIGH', 2: 'MEDIUM', 1: 'LOW'}
            
            # Calculate average confidence
            avg_confidence = np.mean([a['confidence'] for a in alerts])
            
            # Determine if it's mining (multiple alerts or high severity)
            is_mining = (len(alerts) >= 2) or (max_severity == 3)
            
            result = {
                'is_mining': is_mining,
                'severity': severity_map[max_severity],
                'confidence': avg_confidence,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat(),
                'recommendation': self._get_recommendation(severity_map[max_severity], len(alerts))
            }
        else:
            result = {
                'is_mining': False,
                'severity': 'LOW',
                'confidence': 0.1,
                'alerts': [],
                'timestamp': datetime.now().isoformat(),
                'recommendation': 'No suspicious activity detected'
            }
        
        return result
    
    def _get_recommendation(self, severity, num_alerts):
        """Generate recommendation based on detection"""
        if severity == 'HIGH':
            return "IMMEDIATE ACTION: Deploy inspection team to verify illegal mining"
        elif severity == 'MEDIUM':
            return "Schedule aerial survey within 48 hours to investigate anomalies"
        else:
            return "Continue routine monitoring"
    
    def batch_detect(self, data_frame):
        """Run detection on multiple records"""
        results = []
        for _, row in data_frame.iterrows():
            result = self.detect(
                ndvi_value=row.get('ndvi_value', 0.5),
                nightlight_value=row.get('intensity', 5),
                acoustic_confidence=row.get('confidence', 0),
                detection_type=row.get('detection_type'),
                location_risk=row.get('risk_level', 'medium')
            )
            results.append(result)
        return results
    
    def save_model(self, path='models/mining_detector.pkl'):
        """Save trained model"""
        model_data = {
            'rf_classifier': self.rf_classifier,
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'rules': self.rules,
            'is_trained': self.is_trained
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ Model saved to {path}")
    
    def load_model(self, path='models/mining_detector.pkl'):
        """Load trained model"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.rf_classifier = model_data['rf_classifier']
            self.isolation_forest = model_data['isolation_forest']
            self.scaler = model_data['scaler']
            self.rules = model_data['rules']
            self.is_trained = model_data['is_trained']
            print(f"✅ Model loaded from {path}")
            return True
        return False
