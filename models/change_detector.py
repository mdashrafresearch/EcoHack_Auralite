"""
Change detection for Aravalli Hills using satellite imagery
"""

import numpy as np
from datetime import datetime, timedelta

class AravalliChangeDetector:
    """Detect changes in Aravalli landscape over time"""
    
    def __init__(self):
        self.change_threshold = 0.2
        self.historical_period = 365
        
    def detect_surface_changes(self, current_dem, historical_dem):
        """Detect surface elevation changes (mining scars)"""
        elevation_diff = current_dem - historical_dem
        mining_scars = elevation_diff < -5
        scar_percentage = np.sum(mining_scars) / mining_scars.size * 100
        
        return {
            'has_mining_scars': bool(scar_percentage > 1),
            'scar_percentage': round(float(scar_percentage), 2),
            'max_depth': round(float(np.min(elevation_diff)), 1),
            'severity': 'HIGH' if scar_percentage > 5 else 'MEDIUM' if scar_percentage > 2 else 'LOW'
        }
    
    def detect_vegetation_change(self, current_ndvi, historical_ndvi):
        """Detect vegetation loss over time"""
        change_rate = (historical_ndvi - current_ndvi) / historical_ndvi
        
        return {
            'change_rate': round(float(change_rate * 100), 1),
            'is_significant': bool(change_rate > self.change_threshold),
            'projected_loss': self._project_loss(change_rate)
        }
    
    def _project_loss(self, current_rate):
        annualized_rate = current_rate * 12
        projected_10yr = annualized_rate * 10
        return min(projected_10yr, 100)
    
    def identify_risk_zones(self, elevation_data):
        """Identify zones at risk based on 100m rule"""
        low_elevation = elevation_data < 100
        at_risk_percentage = np.sum(low_elevation) / low_elevation.size * 100
        
        return {
            'at_risk_percentage': round(float(at_risk_percentage), 1),
            'matches_reported': bool(abs(at_risk_percentage - 31.8) < 5)
        }
