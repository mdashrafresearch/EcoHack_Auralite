import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model, Sequential
import joblib
import warnings
warnings.filterwarnings('ignore')

class EnhancedMiningDetector:
    def __init__(self):
        """
        Initialize enhanced multi-modal detector with temporal modeling
        """
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Classical models as ensemble components
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.rf_classifier = RandomForestClassifier(n_estimators=200, random_state=42)
        
        # Neural components
        self.temporal_model = None
        self.fusion_model = None
        
    def build_lstm_model(self, input_shape=(30, 13)):
        """LSTM for temporal pattern detection (30-day window)"""
        model = Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.3),
            layers.LSTM(64),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def build_attention_fusion(self, input_dim):
        """Attention mechanism for multi-modal fusion"""
        inputs = keras.Input(shape=(input_dim,))
        
        # Feature processing
        x = layers.Dense(128, activation='relu')(inputs)
        x = layers.BatchNormalization()(x)
        
        # Self-Attention Layer
        attention_probs = layers.Dense(128, activation='softmax', name='attention_weights')(x)
        attended_x = layers.Multiply()([x, attention_probs])
        
        # Dense layers after attention
        x = layers.Dense(64, activation='relu')(attended_x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(32, activation='relu')(x)
        
        # Multi-task outputs
        anomaly_out = layers.Dense(1, activation='sigmoid', name='anomaly')(x)
        severity_out = layers.Dense(3, activation='softmax', name='severity')(x)
        equipment_out = layers.Dense(5, activation='softmax', name='equipment')(x)
        
        model = Model(inputs=inputs, outputs=[anomaly_out, severity_out, equipment_out])
        model.compile(
            optimizer='adam',
            loss={'anomaly': 'binary_crossentropy', 'severity': 'categorical_crossentropy', 'equipment': 'categorical_crossentropy'},
            metrics={'anomaly': 'accuracy', 'severity': 'accuracy', 'equipment': 'accuracy'}
        )
        return model

    def prepare_training_data(self, historical_data):
        """Extract features and labels from historical records"""
        X, y_anom, y_sev, y_equ = [], [], [], []
        
        for r in historical_data:
            features = [
                r.get('ndvi_mean', 0), r.get('ndvi_trend', 0), r.get('ndvi_volatility', 0),
                r.get('ndvi_min', 0), r.get('ndvi_max', 0),
                r.get('nightlight_mean', 0), r.get('nightlight_trend', 0),
                r.get('nightlight_peak', 0), r.get('nightlight_volatility', 0),
                r.get('acoustic_activity', 0), r.get('drilling_freq', 0),
                r.get('excavator_freq', 0), r.get('max_confidence', 0)
            ]
            X.append(features)
            y_anom.append(r.get('is_mining', 0))
            
            # Severity (0-2)
            sev = [0, 0, 0]
            sev[r.get('severity', 0)] = 1
            y_sev.append(sev)
            
            # Equipment (0-4)
            equ = [0, 0, 0, 0, 0]
            equ[r.get('equipment_type', 0)] = 1
            y_equ.append(equ)
            
        return np.array(X), np.array(y_anom), np.array(y_sev), np.array(y_equ)

    def train(self, historical_data, epochs=30):
        """Train the ensemble and neural models"""
        X, y_anom, y_sev, y_equ = selfPrepare_training_data(historical_data)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train classical models
        self.isolation_forest.fit(X_scaled)
        self.rf_classifier.fit(X_scaled, y_anom)
        
        # Train attention fusion model
        self.fusion_model = self.build_attention_fusion(X.shape[1])
        self.fusion_model.fit(
            X_scaled, 
            {'anomaly': y_anom, 'severity': y_sev, 'equipment': y_equ},
            epochs=epochs, batch_size=32, verbose=0
        )
        
        self.is_trained = True
        print("Model training complete.")

    def predict(self, features_dict):
        """Inference using ensemble logic"""
        if not self.is_trained: return None
        
        feature_order = [
            'ndvi_mean', 'ndvi_trend', 'ndvi_volatility', 'ndvi_min', 'ndvi_max',
            'nightlight_mean', 'nightlight_trend', 'nightlight_peak', 'nightlight_volatility',
            'acoustic_activity', 'drilling_freq', 'excavator_freq', 'max_confidence'
        ]
        X = np.array([[features_dict.get(f, 0) for f in feature_order]])
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        rf_prob = self.rf_classifier.predict_proba(X_scaled)[0][1]
        nn_out = self.fusion_model.predict(X_scaled, verbose=0)
        
        is_mining = (rf_prob > 0.5) or (nn_out[0][0][0] > 0.5)
        
        return {
            'is_mining': bool(is_mining),
            'severity': int(np.argmax(nn_out[1][0])),
            'equipment': int(np.argmax(nn_out[2][0])),
            'confidence': float(max(rf_prob, nn_out[0][0][0]))
        }

    def save_models(self, path='models/ensemble/'):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.rf_classifier, f'{path}rf.pkl')
        joblib.dump(self.scaler, f'{path}scaler.pkl')
        self.fusion_model.save(f'{path}fusion.h5')

    def load_models(self, path='models/ensemble/'):
        self.rf_classifier = joblib.load(f'{path}rf.pkl')
        self.scaler = joblib.load(f'{path}scaler.pkl')
        self.fusion_model = keras.models.load_model(f'{path}fusion.h5')
        self.is_trained = True
