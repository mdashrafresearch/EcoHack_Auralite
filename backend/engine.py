import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import joblib

class MiningRiskEngine:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = MinMaxScaler()
        self.is_trained = False
        # To store min/max of raw decision scores for normalization
        self.decision_min = 0
        self.decision_max = 1

    def train_baseline_model(self):
        """
        Generates synthetic normal behavior data and trains the Isolation Forest.
        Normal Range:
        NDVI_Drop: 0.05-0.30
        Nightlight_Inc: 0.05-0.30
        Acoustic_Score: 0.05-0.20
        """
        # Generate 150 synthetic normal samples
        np.random.seed(42)
        n_samples = 150
        
        normal_data = pd.DataFrame({
            'ndvi_drop': np.random.uniform(0.05, 0.30, n_samples),
            'nightlight_inc': np.random.uniform(0.05, 0.30, n_samples),
            'acoustic_score': np.random.uniform(0.05, 0.20, n_samples)
        })
        
        features = ['ndvi_drop', 'nightlight_inc', 'acoustic_score']
        X = normal_data[features].values
        
        # Fit scaler on normal baseline
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        
        # Calibrate normalization range for decision_function
        # Higher values from decision_function imply MORE NORMAL. 
        # Lower values imply MORE ANOMALOUS.
        # Raw anomaly_score = -decision_function
        raw_scores = -self.model.decision_function(X_scaled)
        self.decision_min = raw_scores.min()
        self.decision_max = raw_scores.max()
        
        self.is_trained = True
        return True

    def compute_anomaly_score(self, record):
        """
        Computes normalized anomaly score: -model.decision_function(X)
        Returns [0, 1] where 1 is highly anomalous.
        """
        if not self.is_trained:
            self.train_baseline_model()
            
        features = np.array([[record['ndvi_drop'], record['nightlight_inc'], record['acoustic_score']]])
        scaled_features = self.scaler.transform(features)
        
        # Raw score: lower means more anomalous. 
        # decision_function returns roughly [-0.5, 0.5]
        # We use -decision_function so higher is more anomalous
        raw_anomaly = -self.model.decision_function(scaled_features)[0]
        
        # Min-Max Normalization to [0, 1] based on training range
        # We allow it to exceed 1.0 for extreme cases
        norm_score = (raw_anomaly - self.decision_min) / (self.decision_max - self.decision_min)
        
        # Map to reasonable expected range
        # Anything significantly higher than the training "anomalies" (contamination) gets pushed toward 1
        return np.clip(norm_score, 0, 1.0)

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
        return round(float(final_score), 4), round(float(ai_score), 4), round(float(rule_score), 4)

    def classify_risk(self, score, ai_score=None):
        """
        High Risk → Score > 0.75 OR AI Anomaly > 0.75
        Medium Risk → 0.45 – 0.75
        Low Risk → < 0.45
        """
        if score > 0.75 or (ai_score is not None and ai_score > 0.75):
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

    def get_feature_contributions(self, record):
        """
        Explains the risk score by showing which feature contributed most.
        Returns a dictionary of normalized contributions.
        """
        # Calculate raw contribution as deviation from 'normal' (0.15 for NDVI, 0.15 for Nightlight, 0.1 acoustic)
        # We use a simple delta-based approach for the prototype's explainability
        contributions = {
            'NDVI Decline': max(0, record['ndvi_drop'] - 0.15),
            'Nightlight Increase': max(0, record['nightlight_inc'] - 0.15),
            'Acoustic Anomaly': max(0, record['acoustic_score'] - 0.10)
        }
        
        total = sum(contributions.values())
        if total > 0:
            for k in contributions:
                contributions[k] = round(contributions[k] / total, 2)
        else:
            # Equal contribution if all are normal
            contributions = {k: 0.33 for k in contributions}
            
        return contributions

# Global engine instance
engine = MiningRiskEngine()
