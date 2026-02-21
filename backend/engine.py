import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import joblib

class MiningRiskEngine:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = MinMaxScaler()
        self.is_trained = False

    def train_global_model(self, data_points):
        """
        Trains the Isolation Forest model on all available indicator data.
        data_points: List of dictionaries with ndvi_drop, nightlight_inc, acoustic_score
        """
        if not data_points:
            return False
            
        df = pd.DataFrame(data_points)
        features = ['ndvi_drop', 'nightlight_inc', 'acoustic_score']
        
        # Fit scaler and model
        X = df[features].values
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model.fit(X_scaled)
        self.is_trained = True
        return True

    def compute_anomaly_score(self, record):
        """
        Computes the anomaly score using Isolation Forest.
        Returns a value mapped from [0, 1] where 1 is highly anomalous.
        """
        if not self.is_trained:
            return 0.5
            
        features = np.array([[record['ndvi_drop'], record['nightlight_inc'], record['acoustic_score']]])
        scaled_features = self.scaler.transform(features)
        
        # decision_function returns roughly [-0.5, 0.5] where lower is more anomalous
        raw_score = self.model.decision_function(scaled_features)[0]
        
        # Map to [0, 1] range. Since lower is more anomalous:
        # We want 1 - (mapped_score)
        # Empirical mapping: -0.5 is high anomaly, 0.5 is normal.
        norm_score = (raw_score + 0.5) / 1.0 
        norm_score = np.clip(norm_score, 0, 1)
        return 1.0 - norm_score

    def compute_composite_score(self, record):
        """
        Rule-based score: (0.4 × NDVI_Drop) + (0.3 × Nightlight_Inc) + (0.3 × Acoustic_Score)
        """
        return (0.4 * record['ndvi_drop']) + \
               (0.3 * record['nightlight_inc']) + \
               (0.3 * record['acoustic_score'])

    def compute_final_score(self, record):
        """
        Final Score = (0.6 × AnomalyScore) + (0.4 × CompositeScore)
        """
        ai_score = self.compute_anomaly_score(record)
        rule_score = self.compute_composite_score(record)
        
        final_score = (0.6 * ai_score) + (0.4 * rule_score)
        return round(final_score, 4), round(ai_score, 4), round(rule_score, 4)

    def classify_risk(self, score):
        """
        High Risk → Score > 0.75
        Medium Risk → 0.45 – 0.75
        Low Risk → < 0.45
        """
        if score > 0.75:
            return 'High'
        elif score >= 0.45:
            return 'Medium'
        else:
            return 'Low'

    def get_confidence(self, ai_score, rule_score):
        """
        High confidence if both AI and Rule scores are high (>0.6) or both are low (<0.4).
        """
        if (ai_score > 0.6 and rule_score > 0.6) or (ai_score < 0.4 and rule_score < 0.4):
            return 'High'
        return 'Standard'

# Global engine instance
engine = MiningRiskEngine()
