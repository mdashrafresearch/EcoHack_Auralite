"""
Aravalli-specific sample data generator
Based on real reports about Aravalli Hills mining
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from .coordinates import MONITORING_LOCATIONS, GPS_CHECKPOINTS

class AravalliDataLoader:
    """Load Aravalli-specific monitoring data"""
    
    def __init__(self):
        self.locations = MONITORING_LOCATIONS
        self.ndvi_time_series = self._generate_ndvi_data()
        self.nightlight_data = self._generate_nightlight_data()
        self.acoustic_detections = self._generate_acoustic_data()
        self.camera_feeds = self._generate_camera_data()
        self.gps_tracks = self._generate_gps_tracks()
        self.mining_sites = self._generate_mining_sites()
        
    def _generate_ndvi_data(self):
        """Generate NDVI data for Aravalli locations"""
        dates = pd.date_range(start='2024-01-01', end='2026-02-24', freq='5D')
        ndvi_records = []
        
        baseline_ndvi = {
            'high': 0.25,
            'medium': 0.45,
            'low': 0.65,
            'critical': 0.20
        }
        
        for loc in self.locations:
            base = baseline_ndvi.get(loc['risk_level'], 0.4)
            
            for date in dates:
                seasonal = 0.1 * np.sin(2 * np.pi * (date.dayofyear - 120) / 365)
                
                if loc['mining_activity'] == 'active':
                    days_since_start = (date - datetime(2024, 1, 1)).days
                    mining_impact = -0.0002 * days_since_start
                    mining_impact = max(mining_impact, -0.4)
                elif loc['mining_activity'] == 'suspicious':
                    mining_impact = -0.05 * np.random.random()
                else:
                    mining_impact = 0
                
                noise = np.random.normal(0, 0.03)
                ndvi = base + seasonal + mining_impact + noise
                is_anomaly = ndvi < 0.2 and loc['risk_level'] in ['high', 'critical']
                
                ndvi_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'date': date.strftime('%Y-%m-%d'),
                    'ndvi_value': max(0.1, min(0.8, ndvi)),
                    'is_anomaly': is_anomaly,
                    'risk_level': loc['risk_level']
                })
        
        return pd.DataFrame(ndvi_records)
    
    def _generate_nightlight_data(self):
        """Generate VIIRS nightlight data for detecting night mining"""
        dates = pd.date_range(start='2024-01-01', end='2026-02-24', freq='3D')
        nightlight_records = []
        
        for loc in self.locations:
            base_light = 0.5 if loc['risk_level'] == 'low' else 2.0
            
            for date in dates:
                if loc['mining_activity'] == 'active':
                    if random.random() > 0.4:
                        mining_spike = np.random.uniform(15, 35)
                    else:
                        mining_spike = 0
                elif loc['mining_activity'] == 'suspicious':
                    mining_spike = np.random.uniform(0, 10) if random.random() > 0.7 else 0
                else:
                    mining_spike = 0
                
                if date.weekday() in [5, 6]:
                    weekly_factor = 0.8
                else:
                    weekly_factor = 1.0
                
                nightlight = (base_light + mining_spike) * weekly_factor
                is_anomaly = nightlight > 15
                
                nightlight_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'date': date.strftime('%Y-%m-%d'),
                    'intensity': nightlight,
                    'is_anomaly': is_anomaly,
                    'mining_detected': mining_spike > 15
                })
        
        return pd.DataFrame(nightlight_records)
    
    def _generate_acoustic_data(self):
        """Generate acoustic sensor data for mining machinery"""
        machinery_types = ['excavator', 'drill', 'generator', 'conveyor', 'truck', 'crusher']
        acoustic_records = []
        
        for loc in self.locations:
            if not loc.get('acoustic_sensor', False):
                continue
                
            if loc['mining_activity'] == 'active':
                num_detections = random.randint(30, 60)
                activity_hours = [22, 23, 0, 1, 2, 3, 4]
            elif loc['mining_activity'] == 'suspicious':
                num_detections = random.randint(10, 25)
                activity_hours = list(range(18, 23)) + [5, 6]
            else:
                num_detections = random.randint(0, 8)
                activity_hours = list(range(6, 18))
            
            for i in range(num_detections):
                date = datetime(2026, 1, 1) + timedelta(
                    days=random.randint(0, 55),
                    hours=random.choice(activity_hours),
                    minutes=random.randint(0, 59)
                )
                
                if loc['mining_activity'] == 'active':
                    machinery_type = random.choices(
                        machinery_types,
                        weights=[0.3, 0.25, 0.15, 0.1, 0.1, 0.1]
                    )[0]
                else:
                    machinery_type = random.choices(
                        machinery_types,
                        weights=[0.1, 0.05, 0.2, 0.05, 0.3, 0.3]
                    )[0]
                
                if date.hour in [22, 23, 0, 1, 2, 3, 4]:
                    confidence = random.uniform(0.8, 0.98)
                else:
                    confidence = random.uniform(0.6, 0.85)
                
                acoustic_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'detection_type': machinery_type,
                    'confidence': confidence,
                    'duration_seconds': random.uniform(30, 600),
                    'frequency_hz': random.uniform(50, 2000) if machinery_type in ['excavator', 'crusher'] else random.uniform(300, 3000),
                    'amplitude_db': random.uniform(65, 95),
                    'is_night_mining': date.hour in [22, 23, 0, 1, 2, 3, 4, 5]
                })
        
        return pd.DataFrame(acoustic_records)
    
    def _generate_camera_data(self):
        """Generate simulated camera feed data"""
        camera_records = []
        
        for loc in self.locations:
            if not loc.get('camera_installed', False):
                continue
                
            for i in range(random.randint(5, 15)):
                date = datetime(2026, 2, 1) + timedelta(
                    days=random.randint(0, 23),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                vehicles_detected = random.randint(0, 5) if loc['mining_activity'] == 'active' else random.randint(0, 2)
                
                camera_records.append({
                    'location_id': loc['id'],
                    'location_name': loc['name'],
                    'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'vehicles_detected': vehicles_detected,
                    'people_detected': random.randint(0, vehicles_detected * 2),
                    'has_gps': random.choice([True, False]) if vehicles_detected > 0 else False,
                    'machinery_visible': vehicles_detected > 2,
                    'image_path': f'/static/camera_feeds/{loc["id"]}_{date.strftime("%Y%m%d_%H%M%S")}.jpg'
                })
        
        return pd.DataFrame(camera_records)
    
    def _generate_gps_tracks(self):
        """Generate GPS tracking data for mineral transport vehicles"""
        gps_records = []
        vehicle_ids = [f'VH{str(i).zfill(3)}' for i in range(1, 21)]
        
        for vid in vehicle_ids:
            num_tracks = random.randint(5, 20)
            start_lat = random.uniform(27.0, 28.5)
            start_lon = random.uniform(76.0, 77.5)
            
            for i in range(num_tracks):
                timestamp = datetime(2026, 2, 1) + timedelta(
                    hours=random.randint(0, 23*24),
                    minutes=random.randint(0, 59)
                )
                
                lat = start_lat + random.uniform(-0.5, 0.5)
                lon = start_lon + random.uniform(-0.5, 0.5)
                
                near_checkpoint = False
                checkpoint_name = None
                for cp in GPS_CHECKPOINTS:
                    if abs(lat - cp['lat']) < 0.1 and abs(lon - cp['lon']) < 0.1:
                        near_checkpoint = True
                        checkpoint_name = cp['name']
                        break
                
                gps_records.append({
                    'vehicle_id': vid,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'lat': lat,
                    'lon': lon,
                    'speed_kmh': random.uniform(20, 60),
                    'near_checkpoint': near_checkpoint,
                    'checkpoint_name': checkpoint_name,
                    'has_rfid': random.choice([True, False])
                })
        
        return pd.DataFrame(gps_records)
    
    def _generate_mining_sites(self):
        """Generate known illegal mining sites from reports"""
        sites = [
            {
                'name': 'Bakrija Hill Illegal Mine',
                'lat': 28.2833, 'lon': 76.8167,
                'type': 'active_illegal', 'size': 'large',
                'discovered': '2025-06-15',
                'description': 'Deep mining scars, groundwater exposed',
                'night_activity': True, 'camera_id': 'har_001'
            },
            {
                'name': 'Ramalwas Deep Pits',
                'lat': 28.3500, 'lon': 76.8833,
                'type': 'active_illegal', 'size': 'large',
                'discovered': '2025-08-20',
                'description': '200-feet deep pits, beyond permissible depth',
                'night_activity': True, 'camera_id': 'har_002'
            },
            {
                'name': 'Rajawas Hill Stripping',
                'lat': 28.3833, 'lon': 76.9167,
                'type': 'active_illegal', 'size': 'medium',
                'discovered': '2025-09-10',
                'description': 'Hilltop completely stripped',
                'night_activity': True, 'camera_id': 'har_003'
            },
            {
                'name': 'Tehla Night Mining Site',
                'lat': 27.4217, 'lon': 76.5378,
                'type': 'active_illegal', 'size': 'medium',
                'discovered': '2025-11-05',
                'description': 'Night mining with heavy machinery',
                'night_activity': True, 'camera_id': 'raj_002'
            },
            {
                'name': 'Sariska Buffer Zone Mine',
                'lat': 27.3017, 'lon': 76.4178,
                'type': 'active_illegal', 'size': 'small',
                'discovered': '2026-01-12',
                'description': 'Illegal excavation near tiger reserve',
                'night_activity': False, 'camera_id': 'raj_001'
            },
            {
                'name': 'Chittorgarh Low Hills Mine',
                'lat': 24.8887, 'lon': 74.6269,
                'type': 'at_risk', 'size': 'expanding',
                'discovered': '2026-02-01',
                'description': 'At risk due to 100m rule exemption',
                'night_activity': True, 'camera_id': 'raj_006'
            },
            {
                'name': 'Kaman Illegal Operation',
                'lat': 27.6500, 'lon': 77.2667,
                'type': 'active_illegal', 'size': 'medium',
                'discovered': '2026-02-18',
                'description': 'Excluded from protection, active mining',
                'night_activity': True, 'camera_id': 'raj_009'
            }
        ]
        return sites
    
    def get_aravalli_stats(self):
        """Get Aravalli-specific statistics"""
        total_active_mines = sum(1 for l in self.locations if l['mining_activity'] == 'active')
        critical_zones = sum(1 for l in self.locations if l['risk_level'] == 'critical')
        
        recent_ndvi = self.ndvi_time_series[self.ndvi_time_series['date'] > '2025-12-01']
        avg_ndvi_recent = recent_ndvi['ndvi_value'].mean()
        avg_ndvi_2024 = self.ndvi_time_series[
            (self.ndvi_time_series['date'] > '2024-01-01') & 
            (self.ndvi_time_series['date'] < '2024-03-01')
        ]['ndvi_value'].mean()
        
        vegetation_loss_pct = max(0, ((avg_ndvi_2024 - avg_ndvi_recent) / avg_ndvi_2024) * 100)
        
        night_mining_count = 0
        if len(self.acoustic_detections) > 0 and 'is_night_mining' in self.acoustic_detections.columns:
            night_mining_count = int(self.acoustic_detections['is_night_mining'].sum())
        
        vehicle_count = 0
        if len(self.gps_tracks) > 0:
            vehicle_count = len(self.gps_tracks['vehicle_id'].unique())
        
        return {
            'total_locations': len(self.locations),
            'active_mining_sites': total_active_mines,
            'critical_zones': critical_zones,
            'night_mining_incidents': night_mining_count,
            'vegetation_loss_percent': round(vegetation_loss_pct, 1),
            'avg_ndvi': round(avg_ndvi_recent, 2),
            'total_vehicles_tracked': vehicle_count,
            'area_at_risk_percent': 31.8,
            'total_area_lost_km2': 5772.7,
            'projected_loss_2059_percent': 22
        }
