"""
Auralite - Illegal Mining Detection System
Flask Web Application with Preloaded Dataset
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import random

# Import our modules
from data.sample_data import SampleDataLoader
from models.detector import MiningDetector

app = Flask(__name__)
app.secret_key = 'auralite-secret-key-2024'

# Initialize data loader and detector
data_loader = SampleDataLoader()
detector = MiningDetector()

# Initialize on startup
def initialize():
    """Initialize application with sample data"""
    print("🚀 Initializing Auralite with preloaded dataset...")
    
    # Train detector on sample data
    sample_df = pd.concat([
        data_loader.ndvi_time_series.head(100),
        data_loader.nightlight_data.head(100)
    ])
    detector.train_on_sample(sample_df)
    
    print("✅ Auralite ready!")

# Run initialization
with app.app_context():
    initialize()

@app.route('/')
def index():
    """Home page"""
    stats = data_loader.get_aggregated_stats()
    return render_template('index.html', 
                         stats=stats,
                         locations=data_loader.locations)

@app.route('/dashboard')
def dashboard():
    """Main dashboard view"""
    stats = data_loader.get_aggregated_stats()
    recent_detections = data_loader.acoustic_detections.tail(20).to_dict('records')
    return render_template('dashboard.html', 
                         stats=stats,
                         alerts=recent_detections)

@app.route('/map')
def map_view():
    """Map view for monitoring"""
    return render_template('map_view.html',
                         locations=data_loader.locations,
                         mining_sites=data_loader.mining_sites)

@app.route('/alerts')
def alerts():
    """Alerts and detections page"""
    # Get recent alerts
    recent_detections = data_loader.acoustic_detections.tail(20).to_dict('records')
    return render_template('alerts.html',
                         alerts=recent_detections)

# API Routes

@app.route('/api/locations')
def get_locations():
    """Get all monitoring locations"""
    return jsonify({
        'success': True,
        'locations': data_loader.locations
    })

@app.route('/api/location/<location_id>')
def get_location(location_id):
    """Get specific location details"""
    location = next((l for l in data_loader.locations if l['id'] == location_id), None)
    if location:
        # Get location data
        ndvi_data = data_loader.ndvi_time_series[
            data_loader.ndvi_time_series['location_id'] == location_id
        ].to_dict('records')
        
        nightlight_data = data_loader.nightlight_data[
            data_loader.nightlight_data['location_id'] == location_id
        ].to_dict('records')
        
        acoustic_data = data_loader.acoustic_detections[
            data_loader.acoustic_detections['location_id'] == location_id
        ].to_dict('records')
        
        return jsonify({
            'success': True,
            'location': location,
            'data': {
                'ndvi': ndvi_data[-30:],  # Last 30 records
                'nightlight': nightlight_data[-30:],
                'acoustic': acoustic_data[-20:]
            }
        })
    
    return jsonify({'success': False, 'error': 'Location not found'}), 404

@app.route('/api/ndvi/<location_id>')
def get_ndvi(location_id):
    """Get NDVI data for location"""
    days = int(request.args.get('days', 30))
    
    ndvi_data = data_loader.ndvi_time_series[
        data_loader.ndvi_time_series['location_id'] == location_id
    ].tail(days)
    
    return jsonify({
        'success': True,
        'data': ndvi_data.to_dict('records')
    })

@app.route('/api/nightlight/<location_id>')
def get_nightlight(location_id):
    """Get nightlight data for location"""
    days = int(request.args.get('days', 30))
    
    nightlight_data = data_loader.nightlight_data[
        data_loader.nightlight_data['location_id'] == location_id
    ].tail(days)
    
    return jsonify({
        'success': True,
        'data': nightlight_data.to_dict('records')
    })

@app.route('/api/detections')
def get_detections():
    """Get recent detections"""
    limit = int(request.args.get('limit', 50))
    location_id = request.args.get('location_id')
    
    if location_id:
        detections = data_loader.acoustic_detections[
            data_loader.acoustic_detections['location_id'] == location_id
        ].tail(limit)
    else:
        detections = data_loader.acoustic_detections.tail(limit)
    
    return jsonify({
        'success': True,
        'detections': detections.to_dict('records')
    })

@app.route('/api/detect', methods=['POST'])
def detect_mining():
    """Run detection on current data"""
    data = request.json
    location_id = data.get('location_id')
    
    if not location_id:
        return jsonify({'success': False, 'error': 'Location ID required'}), 400
    
    # Get latest data for location
    loc_ndvi = data_loader.ndvi_time_series[
        data_loader.ndvi_time_series['location_id'] == location_id
    ]
    loc_nightlight = data_loader.nightlight_data[
        data_loader.nightlight_data['location_id'] == location_id
    ]
    loc_acoustic = data_loader.acoustic_detections[
        data_loader.acoustic_detections['location_id'] == location_id
    ]
    
    latest_ndvi = loc_ndvi.iloc[-1] if len(loc_ndvi) > 0 else None
    latest_nightlight = loc_nightlight.iloc[-1] if len(loc_nightlight) > 0 else None
    latest_acoustic = loc_acoustic.iloc[-1] if len(loc_acoustic) > 0 else None
    
    # Get location info
    location = next((l for l in data_loader.locations if l['id'] == location_id), None)
    
    if latest_ndvi is not None and latest_nightlight is not None:
        # Run detection
        result = detector.detect(
            ndvi_value=latest_ndvi['ndvi_value'],
            nightlight_value=latest_nightlight['intensity'],
            acoustic_confidence=latest_acoustic['confidence'] if latest_acoustic is not None else 0,
            detection_type=latest_acoustic['detection_type'] if latest_acoustic is not None else None,
            location_risk=location['risk_level'] if location else 'medium'
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'location': location
        })
    
    return jsonify({'success': False, 'error': 'Insufficient data'}), 400

@app.route('/api/stats')
def get_stats():
    """Get aggregated statistics"""
    return jsonify({
        'success': True,
        'stats': data_loader.get_aggregated_stats()
    })

@app.route('/api/heatmap')
def get_heatmap_data():
    """Get data for risk heatmap"""
    heatmap_data = []
    
    for loc in data_loader.locations:
        # Calculate risk score based on recent detections
        recent_detections = data_loader.acoustic_detections[
            data_loader.acoustic_detections['location_id'] == loc['id']
        ].tail(10)
        
        risk_score = len(recent_detections) * 10
        if loc['risk_level'] == 'high':
            risk_score += 30
        elif loc['risk_level'] == 'medium':
            risk_score += 15
        
        heatmap_data.append({
            'lat': loc['lat'],
            'lon': loc['lon'],
            'intensity': min(risk_score, 100),
            'location': loc['name']
        })
    
    return jsonify({
        'success': True,
        'data': heatmap_data
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_area():
    """Analyze a specific area for mining activity"""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 5)  # km
    
    # Find nearest location
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c
    
    nearest_loc = None
    min_dist = float('inf')
    
    for loc in data_loader.locations:
        dist = haversine(lat, lon, loc['lat'], loc['lon'])
        if dist < min_dist:
            min_dist = dist
            nearest_loc = loc
    
    if nearest_loc and min_dist <= radius:
        # Get data for this location
        ndvi_data = data_loader.ndvi_time_series[
            data_loader.ndvi_time_series['location_id'] == nearest_loc['id']
        ].tail(30)
        
        nightlight_data = data_loader.nightlight_data[
            data_loader.nightlight_data['location_id'] == nearest_loc['id']
        ].tail(30)
        
        # Calculate trends
        ndvi_trend = np.polyfit(range(len(ndvi_data)), ndvi_data['ndvi_value'].values, 1)[0] if len(ndvi_data) > 1 else 0
        nightlight_trend = np.polyfit(range(len(nightlight_data)), nightlight_data['intensity'].values, 1)[0] if len(nightlight_data) > 1 else 0
        
        # Run detection
        detection_result = detector.detect(
            ndvi_value=ndvi_data['ndvi_value'].iloc[-1] if len(ndvi_data) > 0 else 0.5,
            nightlight_value=nightlight_data['intensity'].iloc[-1] if len(nightlight_data) > 0 else 5,
            location_risk=nearest_loc['risk_level']
        )
        
        return jsonify({
            'success': True,
            'location': nearest_loc,
            'distance_km': min_dist,
            'analysis': {
                'risk_level': nearest_loc['risk_level'],
                'ndvi_trend': float(ndvi_trend),
                'nightlight_trend': float(nightlight_trend),
                'detection': detection_result,
                'recommendation': 'High probability of illegal mining' if detection_result['is_mining'] else 'Area appears normal'
            }
        })
    else:
        return jsonify({
            'success': True,
            'analysis': {
                'risk_level': 'UNKNOWN',
                'recommendation': 'No monitoring data available for this area'
            }
        })

@app.route('/api/simulate/detection')
def simulate_detection():
    """Simulate a new detection (for demo purposes)"""
    location_id = request.args.get('location_id')
    
    if not location_id:
        location_id = random.choice([l['id'] for l in data_loader.locations])
    
    # Create a simulated detection
    detection_types = ['excavator', 'drill', 'generator', 'conveyor', 'truck']
    new_detection = {
        'location_id': location_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'detection_type': random.choice(detection_types),
        'confidence': random.uniform(0.75, 0.99),
        'duration_seconds': random.uniform(60, 600),
        'frequency_hz': random.uniform(50, 2000),
        'amplitude_db': random.uniform(70, 95)
    }
    
    return jsonify({
        'success': True,
        'detection': new_detection,
        'message': f"New {new_detection['detection_type']} detected with {new_detection['confidence']:.1%} confidence"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
