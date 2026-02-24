import pytest
import numpy as np
import os
from src.ml_models.fusion_model import EnhancedMiningDetector

def test_model_structure():
    """Test if model can be initialized and has expected methods"""
    detector = EnhancedMiningDetector()
    assert hasattr(detector, 'train')
    assert hasattr(detector, 'predict')
    assert hasattr(detector, 'save_models')

def test_inference_logic():
    """Test inference output structure"""
    detector = EnhancedMiningDetector()
    # Mock training status for test
    detector.is_trained = True
    detector.scaler.fit(np.random.randn(10, 13))
    # Mock models
    from unittest.mock import MagicMock
    detector.rf_classifier = MagicMock()
    detector.rf_classifier.predict_proba.return_value = np.array([[0.2, 0.8]])
    detector.fusion_model = MagicMock()
    detector.fusion_model.predict.return_value = [
        np.array([[0.7]]), # anomaly
        np.array([[0.1, 0.8, 0.1]]), # severity
        np.array([[0.1, 0.1, 0.6, 0.1, 0.1]]) # equipment
    ]
    
    sample_input = {
        'ndvi_mean': 0.3, 'ndvi_trend': -0.1, 'nightlight_mean': 20.0,
        'acoustic_activity': 8, 'drilling_freq': 150.0, 'max_confidence': 0.9
    }
    
    result = detector.predict(sample_input)
    assert result['is_mining'] is True
    assert result['severity'] == 1
    assert result['equipment'] == 2
    assert result['confidence'] >= 0.7

def test_save_load_path():
    """Test model directory creation"""
    detector = EnhancedMiningDetector()
    path = 'models/test_path/'
    detector.save_models(path)
    assert os.path.exists(path)
    # Cleanup
    import shutil
    shutil.rmtree(path)
