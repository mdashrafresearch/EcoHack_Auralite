"""
Preloaded sample dataset for Auralite
Contains synthetic but realistic data for demonstration
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class SampleDataLoader:
    """Load pre-generated sample data for the application"""
    
    def __init__(self):
        self.locations = self._generate_locations()
        self.ndvi_time_series = self._generate_ndvi_data()
        self.nightlight_data = self._generate_nightlight_data()
        self.acoustic_detections = self._generate_acoustic_data()
        self.mining_sites = self._generate_mining_sites()
        
    def _generate_locations(self):
        """Generate sample monitoring locations"""
        return [
            {
                'id': 'loc_001',
                'name': 'Amazon Basin North',
                'lat': -3.4653,
                'lon': -62.2159,
                'risk_level': 'high',
                'area_km2': 1250
            },
            {
                'id': 'loc_002',
                'name': 'Amazon Basin South',
                'lat': -5.1348,
                'lon': -63.0432,
                'risk_level': 'medium',
                'area_km2': 980
            },
            {
                'id': 'loc_003',
                'name': 'Madre de Dios',
                'lat': -12.5937,
                'lon': -69.1831,
                'risk_level': 'high',
                'area_km2': 2100
            },
            {
                'id': 'loc_004',
                'name': 'Guyana Shield',
                'lat': 3.8667,
                'lon': -59.2833,
                'risk_level': 'low',
                'area_km2': 750
            },
            {
                'id': 'loc_005',
                'name': 'Suriname Rainforest',
                'lat': 4.0,
                'lon': -56.0,
                'risk_level': 'medium',
                'area_km2': 1100
            }
        ]
    
    def _generate_ndvi_data(self):
        """Generate NDVI time series data"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='5D')
        ndvi_records = []
        
        for loc in self.locations:
            base_ndvi = 0.7 if loc['risk_level'] == 'low' else 0.5 if loc['risk_level'] == 'medium' else 0.3
            
            for date in dates:
                # Add seasonal variation
                seasonal = 0.1 * np.sin(2 * np.pi * date.dayofyear / 365)
                
                # Add random noise
                noise = np.random.normal(0, 0.05)
                
                # Add mining impact for high-risk areas
                if loc['risk_level'] == 'high' and date > datetime(2024, 6, 1):
                    mining_impact = -0.02 * (date.dayofyear - 152) / 30
                    mining_impact = max(mining_impact, -0.3)
                else:
                    mining_impact = 0
                
                ndvi = base_ndvi + seasonal + noise + mining_impact
                
                ndvi_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'date': date.strftime('%Y-%m-%d'),
                    'ndvi_value': max(0.1, min(0.9, ndvi)),
                    'is_anomaly': ndvi < 0.25 and loc['risk_level'] == 'high'
                })
        
        return pd.DataFrame(ndvi_records)
    
    def _generate_nightlight_data(self):
        """Generate nightlight intensity data"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='7D')
        nightlight_records = []
        
        for loc in self.locations:
            base_light = 2 if loc['risk_level'] == 'low' else 8 if loc['risk_level'] == 'medium' else 15
            
            for date in dates:
                # Add weekly pattern
                if date.weekday() in [5, 6]:  # Weekend
                    weekly = base_light * 0.8
                else:
                    weekly = base_light
                
                # Add random variation
                variation = np.random.normal(0, 2)
                
                # Add mining activity spikes
                if loc['risk_level'] == 'high' and np.random.random() > 0.7:
                    mining_spike = np.random.uniform(10, 25)
                else:
                    mining_spike = 0
                
                nightlight = weekly + variation + mining_spike
                
                nightlight_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'date': date.strftime('%Y-%m-%d'),
                    'intensity': max(0, nightlight),
                    'is_anomaly': nightlight > 20
                })
        
        return pd.DataFrame(nightlight_records)
    
    def _generate_acoustic_data(self):
        """Generate acoustic detection data"""
        detection_types = ['excavator', 'drill', 'generator', 'conveyor', 'truck']
        acoustic_records = []
        
        for loc in self.locations:
            # Generate more detections for high-risk areas
            num_detections = 50 if loc['risk_level'] == 'high' else 20 if loc['risk_level'] == 'medium' else 5
            
            for i in range(num_detections):
                date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365), 
                                                        hours=random.randint(0, 23))
                
                detection = {
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'detection_type': random.choice(detection_types),
                    'confidence': random.uniform(0.65, 0.98),
                    'duration_seconds': random.uniform(30, 300),
                    'frequency_hz': random.uniform(50, 2000),
                    'amplitude_db': random.uniform(60, 95)
                }
                acoustic_records.append(detection)
        
        return pd.DataFrame(acoustic_records)
    
    def _generate_mining_sites(self):
        """Generate known/illegal mining sites"""
        sites = []
        
        # Active illegal mining sites
        illegal_sites = [
            {'name': 'Illegal Site Alpha', 'lat': -3.51, 'lon': -62.25, 'type': 'illegal', 'size': 'large'},
            {'name': 'Illegal Site Beta', 'lat': -5.18, 'lon': -63.09, 'type': 'illegal', 'size': 'medium'},
            {'name': 'Illegal Site Gamma', 'lat': -12.63, 'lon': -69.21, 'type': 'illegal', 'size': 'large'},
            {'name': 'Suspicious Activity Delta', 'lat': -3.42, 'lon': -62.18, 'type': 'suspicious', 'size': 'small'}
        ]
        
        for site in illegal_sites:
            site['location_id'] = self._get_location_id(site['lat'], site['lon'])
            sites.append(site)
        
        return sites
    
    def _get_location_id(self, lat, lon):
        """Find closest location ID"""
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c
        
        min_dist = float('inf')
        closest = None
        
        for loc in self.locations:
            dist = haversine(lat, lon, loc['lat'], loc['lon'])
            if dist < min_dist:
                min_dist = dist
                closest = loc['id']
        
        return closest
    
    def get_aggregated_stats(self):
        """Get aggregated statistics for dashboard"""
        stats = {
            'total_locations': len(self.locations),
            'high_risk_areas': sum(1 for l in self.locations if l['risk_level'] == 'high'),
            'total_alerts': len(self.acoustic_detections[self.acoustic_detections['confidence'] > 0.85]),
            'avg_ndvi': self.ndvi_time_series['ndvi_value'].mean(),
            'total_detections': len(self.acoustic_detections),
            'active_mining_sites': len([s for s in self.mining_sites if s['type'] == 'illegal'])
        }
        return stats
