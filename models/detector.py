"""
Mining detection model for Aravalli Hills
"""

import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import os

class AravalliMiningDetector:
    """Main detector for illegal mining in Aravalli Hills"""
    
    def __init__(self):
        self.rules = {
            'ndvi_threshold': 0.3,
            'nightlight_threshold': 15,
            'acoustic_confidence': 0.75,
            'camera_vehicle_threshold': 3,
            'gps_anomaly_speed': 80,
            'night_mining_hours': [22, 23, 0, 1, 2, 3, 4, 5],
            'change_detection_sensitivity': 0.2
        }
        
        self.risk_weights = {
            'sariska_zone': 1.5,
            'water_recharge_zone': 1.3,
            'low_elevation': 1.2,
            'buffer_zone': 1.1
        }
        
    def detect_from_all_sources(self, location_id, ndvi_data, nightlight_data, 
                                acoustic_data, camera_data, gps_data):
        """Multi-modal detection combining all data sources"""
        alerts = []
        confidence_scores = []
        
        if ndvi_data is not None and len(ndvi_data) > 0:
            ndvi_result = self._analyze_ndvi(ndvi_data, location_id)
            if ndvi_result['alert']:
                alerts.append(ndvi_result)
                confidence_scores.append(ndvi_result['confidence'])
        
        if nightlight_data is not None and len(nightlight_data) > 0:
            night_result = self._analyze_nightlight(nightlight_data, location_id)
            if night_result['alert']:
                alerts.append(night_result)
                confidence_scores.append(night_result['confidence'])
        
        if acoustic_data is not None and len(acoustic_data) > 0:
            acoustic_result = self._analyze_acoustic(acoustic_data, location_id)
            if acoustic_result['alert']:
                alerts.append(acoustic_result)
                confidence_scores.append(acoustic_result['confidence'])
        
        if camera_data is not None and len(camera_data) > 0:
            camera_result = self._analyze_camera(camera_data, location_id)
            if camera_result['alert']:
                alerts.append(camera_result)
                confidence_scores.append(camera_result['confidence'])
        
        if gps_data is not None and len(gps_data) > 0:
            gps_result = self._analyze_gps(gps_data, location_id)
            if gps_result['alert']:
                alerts.append(gps_result)
                confidence_scores.append(gps_result['confidence'])
        
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0
        severity = self._calculate_severity(alerts, location_id)
        recommendation = self._generate_recommendation(severity, alerts, location_id)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'location_id': location_id,
            'alerts': alerts,
            'alert_count': len(alerts),
            'overall_confidence': round(float(overall_confidence), 2),
            'severity': severity,
            'requires_action': severity in ['HIGH', 'CRITICAL'],
            'recommendation': recommendation
        }
    
    def _analyze_ndvi(self, ndvi_data, location_id):
        recent = ndvi_data.tail(5)
        historical = ndvi_data.head(10)
        current_ndvi = recent['ndvi_value'].mean()
        historical_ndvi = historical['ndvi_value'].mean()
        change_rate = (historical_ndvi - current_ndvi) / historical_ndvi if historical_ndvi > 0 else 0
        is_alert = current_ndvi < self.rules['ndvi_threshold'] or change_rate > 0.15
        confidence = min(1.0, (self.rules['ndvi_threshold'] - current_ndvi) / self.rules['ndvi_threshold'] + 0.3) if current_ndvi < self.rules['ndvi_threshold'] else 0.3
        
        return {
            'type': 'vegetation_loss',
            'alert': is_alert,
            'confidence': round(float(confidence), 2),
            'current_ndvi': round(float(current_ndvi), 2),
            'change_rate': round(float(change_rate * 100), 1),
            'message': f'Vegetation loss detected: NDVI dropped to {current_ndvi:.2f}',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_nightlight(self, nightlight_data, location_id):
        recent = nightlight_data.tail(3)
        avg_intensity = recent['intensity'].mean()
        current_hour = datetime.now().hour
        is_night = current_hour in self.rules['night_mining_hours']
        is_alert = avg_intensity > self.rules['nightlight_threshold']
        confidence = min(1.0, avg_intensity / 30) if is_alert else 0.2
        
        return {
            'type': 'night_mining',
            'alert': is_alert,
            'confidence': round(float(confidence), 2),
            'intensity': round(float(avg_intensity), 1),
            'is_night': is_night,
            'message': f'Unusual night activity detected: {avg_intensity:.1f} nW/cm²/sr',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_acoustic(self, acoustic_data, location_id):
        if len(acoustic_data) == 0:
            return {'alert': False, 'confidence': 0, 'type': 'acoustic_detection'}
        
        recent = acoustic_data.tail(5)
        high_confidence = recent[recent['confidence'] > self.rules['acoustic_confidence']]
        is_alert = len(high_confidence) > 0
        is_night_mining = False
        
        if is_alert:
            machinery_types = high_confidence['detection_type'].tolist()
            avg_confidence = high_confidence['confidence'].mean()
            if 'is_night_mining' in high_confidence.columns:
                night_detections = high_confidence[high_confidence['is_night_mining'] == True]
                is_night_mining = len(night_detections) > 0
            message = f'Machinery detected: {", ".join(machinery_types[:3])}'
            if is_night_mining:
                message += ' (NIGHT MINING ALERT)'
        else:
            avg_confidence = 0
            message = 'No significant acoustic detections'
        
        return {
            'type': 'acoustic_detection',
            'alert': is_alert,
            'confidence': round(float(avg_confidence), 2) if is_alert else 0.1,
            'detections': int(len(high_confidence)),
            'is_night_mining': is_night_mining,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_camera(self, camera_data, location_id):
        if len(camera_data) == 0:
            return {'alert': False, 'confidence': 0, 'type': 'camera_detection'}
        
        recent = camera_data.tail(3)
        total_vehicles = recent['vehicles_detected'].sum()
        is_alert = total_vehicles > self.rules['camera_vehicle_threshold']
        confidence = min(1.0, total_vehicles / 10) if is_alert else 0.1
        
        return {
            'type': 'camera_detection',
            'alert': is_alert,
            'confidence': round(float(confidence), 2),
            'vehicles_detected': int(total_vehicles),
            'has_gps': bool(recent['has_gps'].any()) if len(recent) > 0 else False,
            'message': f'{int(total_vehicles)} vehicles detected in recent footage',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_gps(self, gps_data, location_id):
        if len(gps_data) == 0:
            return {'alert': False, 'confidence': 0, 'type': 'gps_tracking'}
        
        recent = gps_data.tail(10)
        high_speed = recent[recent['speed_kmh'] > self.rules['gps_anomaly_speed']]
        near_checkpoint = recent[recent['near_checkpoint'] == True]
        is_alert = len(high_speed) > 0 or (len(near_checkpoint) == 0 and len(recent) > 5)
        confidence = 0.7 if len(high_speed) > 0 else 0.4 if len(near_checkpoint) == 0 else 0.1
        
        return {
            'type': 'gps_tracking',
            'alert': is_alert,
            'confidence': round(float(confidence), 2),
            'high_speed_count': int(len(high_speed)),
            'checkpoint_count': int(len(near_checkpoint)),
            'message': f'GPS anomaly: {len(high_speed)} vehicles exceeding speed limit',
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_severity(self, alerts, location_id):
        if len(alerts) == 0:
            return 'LOW'
        alert_types = [a['type'] for a in alerts]
        if 'night_mining' in alert_types and 'vegetation_loss' in alert_types and 'acoustic_detection' in alert_types:
            return 'CRITICAL'
        if len(alerts) >= 3 or 'night_mining' in alert_types:
            return 'HIGH'
        if len(alerts) >= 2:
            return 'MEDIUM'
        return 'LOW'
    
    def _generate_recommendation(self, severity, alerts, location_id):
        if severity == 'CRITICAL':
            return "IMMEDIATE ACTION: Deploy forest department and police. Night mining in progress with heavy machinery."
        if severity == 'HIGH':
            return "URGENT: Dispatch inspection team within 24 hours. Evidence of active mining detected."
        if severity == 'MEDIUM':
            return "SCHEDULED: Aerial survey recommended within 48 hours to verify suspicious activity."
        return "ROUTINE: Continue monitoring. No immediate action required."
