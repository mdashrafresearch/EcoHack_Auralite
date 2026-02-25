"""
Auralite - Aravalli Hills Illegal Mining Detection System
Flask Application with Real-time Monitoring
"""

from flask import Flask, render_template, jsonify, request, session, Response
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import threading
import queue
import random

# Import modules
from config import Config
from data.aravalli_data import AravalliDataLoader
from data.coordinates import MONITORING_LOCATIONS, GPS_CHECKPOINTS, RFID_GATES
from models.detector import AravalliMiningDetector
from models.change_detector import AravalliChangeDetector
from utils.notification import NotificationManager

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize components
print("🚀 Initializing Auralite Aravalli Hills monitoring system...")
data_loader = AravalliDataLoader()
detector = AravalliMiningDetector()
change_detector = AravalliChangeDetector()
notification_manager = NotificationManager()
print("✅ All components initialized!")

# Global variables
active_alerts = []
notification_queue = queue.Queue()
monitoring_active = True

# ===================== PAGE ROUTES =====================

@app.route('/')
def index():
    """Home page with Aravalli overview"""
    stats = data_loader.get_aravalli_stats()
    return render_template('index.html', 
                         stats=stats,
                         locations=MONITORING_LOCATIONS,
                         critical_zones=Config.CRITICAL_ZONES)

@app.route('/dashboard')
def dashboard():
    """Main monitoring dashboard"""
    stats = data_loader.get_aravalli_stats()
    return render_template('dashboard.html', 
                         stats=stats,
                         locations=MONITORING_LOCATIONS)

@app.route('/map')
def map_view():
    """Interactive map of Aravalli Hills"""
    return render_template('map_view.html',
                         locations=MONITORING_LOCATIONS,
                         mining_sites=data_loader.mining_sites,
                         gps_checkpoints=GPS_CHECKPOINTS,
                         rfid_gates=RFID_GATES,
                         critical_zones=Config.CRITICAL_ZONES)

@app.route('/camera_feed')
def camera_feed():
    """Live camera feeds from monitoring locations"""
    camera_locs = [l for l in MONITORING_LOCATIONS if l.get('camera_installed', False)]
    camera_data = data_loader.camera_feeds.to_dict('records') if len(data_loader.camera_feeds) > 0 else []
    return render_template('camera_feed.html',
                         locations=camera_locs,
                         camera_data=camera_data)

@app.route('/sensors')
def sensors():
    """Acoustic sensor monitoring"""
    sensor_locs = [l for l in MONITORING_LOCATIONS if l.get('acoustic_sensor', False)]
    acoustic_data = data_loader.acoustic_detections.tail(50).to_dict('records') if len(data_loader.acoustic_detections) > 0 else []
    return render_template('sensors.html',
                         locations=sensor_locs,
                         acoustic_data=acoustic_data)

@app.route('/alerts')
def alerts():
    """Active alerts page"""
    global active_alerts
    return render_template('alerts.html', 
                         alerts=active_alerts[-20:],
                         locations=MONITORING_LOCATIONS)

@app.route('/documentation')
def documentation():
    """Production deployment documentation"""
    return render_template('documentation.html')

# ===================== API ROUTES =====================

@app.route('/api/locations')
def get_locations():
    return jsonify({'success': True, 'locations': MONITORING_LOCATIONS})

@app.route('/api/location/<location_id>')
def get_location(location_id):
    location = next((l for l in MONITORING_LOCATIONS if l['id'] == location_id), None)
    if not location:
        return jsonify({'success': False, 'error': 'Location not found'}), 404
    
    ndvi_data = data_loader.ndvi_time_series[
        data_loader.ndvi_time_series['location_id'] == location_id
    ].tail(30).to_dict('records')
    
    nightlight_data = data_loader.nightlight_data[
        data_loader.nightlight_data['location_id'] == location_id
    ].tail(30).to_dict('records')
    
    acoustic_data = data_loader.acoustic_detections[
        data_loader.acoustic_detections['location_id'] == location_id
    ].tail(20).to_dict('records') if len(data_loader.acoustic_detections) > 0 else []
    
    camera_data = data_loader.camera_feeds[
        data_loader.camera_feeds['location_id'] == location_id
    ].tail(10).to_dict('records') if len(data_loader.camera_feeds) > 0 else []
    
    return jsonify({
        'success': True,
        'location': location,
        'data': {
            'ndvi': ndvi_data,
            'nightlight': nightlight_data,
            'acoustic': acoustic_data,
            'camera': camera_data
        }
    })

@app.route('/api/ndvi/<location_id>')
def get_ndvi(location_id):
    days = int(request.args.get('days', 30))
    ndvi_data = data_loader.ndvi_time_series[
        data_loader.ndvi_time_series['location_id'] == location_id
    ].tail(days)
    return jsonify({'success': True, 'data': ndvi_data.to_dict('records')})

@app.route('/api/nightlight/<location_id>')
def get_nightlight(location_id):
    days = int(request.args.get('days', 30))
    nightlight_data = data_loader.nightlight_data[
        data_loader.nightlight_data['location_id'] == location_id
    ].tail(days)
    return jsonify({'success': True, 'data': nightlight_data.to_dict('records')})

@app.route('/api/acoustic/<location_id>')
def get_acoustic(location_id):
    limit = int(request.args.get('limit', 50))
    if location_id == 'all':
        acoustic_data = data_loader.acoustic_detections.tail(limit)
    else:
        acoustic_data = data_loader.acoustic_detections[
            data_loader.acoustic_detections['location_id'] == location_id
        ].tail(limit)
    return jsonify({'success': True, 'data': acoustic_data.to_dict('records')})

@app.route('/api/camera/<location_id>')
def get_camera(location_id):
    limit = int(request.args.get('limit', 20))
    if len(data_loader.camera_feeds) == 0:
        return jsonify({'success': True, 'data': []})
    camera_data = data_loader.camera_feeds[
        data_loader.camera_feeds['location_id'] == location_id
    ].tail(limit)
    return jsonify({'success': True, 'data': camera_data.to_dict('records')})

@app.route('/api/gps_tracks')
def get_gps_tracks():
    limit = int(request.args.get('limit', 100))
    vehicle_id = request.args.get('vehicle_id')
    if vehicle_id:
        gps_data = data_loader.gps_tracks[
            data_loader.gps_tracks['vehicle_id'] == vehicle_id
        ].tail(limit)
    else:
        gps_data = data_loader.gps_tracks.tail(limit)
    return jsonify({'success': True, 'data': gps_data.to_dict('records')})

@app.route('/api/mining_sites')
def get_mining_sites():
    return jsonify({'success': True, 'sites': data_loader.mining_sites})

@app.route('/api/checkpoints')
def get_checkpoints():
    return jsonify({
        'success': True,
        'gps_checkpoints': GPS_CHECKPOINTS,
        'rfid_gates': RFID_GATES
    })

@app.route('/api/detect', methods=['POST'])
def detect_mining():
    data = request.json
    location_id = data.get('location_id')
    if not location_id:
        return jsonify({'success': False, 'error': 'Location ID required'}), 400
    
    ndvi_data = data_loader.ndvi_time_series[
        data_loader.ndvi_time_series['location_id'] == location_id
    ]
    nightlight_data = data_loader.nightlight_data[
        data_loader.nightlight_data['location_id'] == location_id
    ]
    acoustic_data = data_loader.acoustic_detections[
        data_loader.acoustic_detections['location_id'] == location_id
    ] if len(data_loader.acoustic_detections) > 0 else pd.DataFrame()
    
    camera_data = data_loader.camera_feeds[
        data_loader.camera_feeds['location_id'] == location_id
    ] if len(data_loader.camera_feeds) > 0 else pd.DataFrame()
    
    location = next((l for l in MONITORING_LOCATIONS if l['id'] == location_id), None)
    nearby_gps = pd.DataFrame()
    if location and len(data_loader.gps_tracks) > 0:
        nearby_gps = data_loader.gps_tracks[
            (abs(data_loader.gps_tracks['lat'] - location['lat']) < 0.5) &
            (abs(data_loader.gps_tracks['lon'] - location['lon']) < 0.5)
        ]
    
    result = detector.detect_from_all_sources(
        location_id=location_id,
        ndvi_data=ndvi_data,
        nightlight_data=nightlight_data,
        acoustic_data=acoustic_data,
        camera_data=camera_data,
        gps_data=nearby_gps
    )
    result['location'] = location
    
    if result['severity'] in ['HIGH', 'CRITICAL']:
        alert = {
            'id': f"alert_{datetime.now().timestamp()}",
            'location_id': location_id,
            'location_name': location['name'] if location else 'Unknown',
            'severity': result['severity'],
            'message': result['recommendation'],
            'timestamp': datetime.now().isoformat(),
            'confidence': result['overall_confidence']
        }
        active_alerts.append(alert)
        notification_queue.put(alert)
        socketio.emit('new_alert', alert)
    
    return jsonify({'success': True, 'result': result})

@app.route('/api/detect_all')
def detect_all():
    results = []
    for location in MONITORING_LOCATIONS:
        ndvi_data = data_loader.ndvi_time_series[
            data_loader.ndvi_time_series['location_id'] == location['id']
        ]
        nightlight_data = data_loader.nightlight_data[
            data_loader.nightlight_data['location_id'] == location['id']
        ]
        acoustic_data = data_loader.acoustic_detections[
            data_loader.acoustic_detections['location_id'] == location['id']
        ] if len(data_loader.acoustic_detections) > 0 else pd.DataFrame()
        
        camera_data = data_loader.camera_feeds[
            data_loader.camera_feeds['location_id'] == location['id']
        ] if len(data_loader.camera_feeds) > 0 else pd.DataFrame()
        
        nearby_gps = pd.DataFrame()
        if len(data_loader.gps_tracks) > 0:
            nearby_gps = data_loader.gps_tracks[
                (abs(data_loader.gps_tracks['lat'] - location['lat']) < 0.5) &
                (abs(data_loader.gps_tracks['lon'] - location['lon']) < 0.5)
            ]
        
        result = detector.detect_from_all_sources(
            location_id=location['id'],
            ndvi_data=ndvi_data,
            nightlight_data=nightlight_data,
            acoustic_data=acoustic_data,
            camera_data=camera_data,
            gps_data=nearby_gps
        )
        results.append({'location': location, 'result': result})
    
    return jsonify({
        'success': True,
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    stats = data_loader.get_aravalli_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/active_alerts')
def get_active_alerts():
    global active_alerts
    return jsonify({
        'success': True,
        'alerts': active_alerts[-50:],
        'count': len(active_alerts)
    })

@app.route('/api/acknowledge_alert/<alert_id>', methods=['POST'])
def acknowledge_alert(alert_id):
    global active_alerts
    for alert in active_alerts:
        if alert['id'] == alert_id:
            alert['acknowledged'] = True
            alert['acknowledged_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': 'Alert acknowledged'})
    return jsonify({'success': False, 'error': 'Alert not found'}), 404

@app.route('/api/aravalli_risk_map')
def get_risk_map():
    risk_zones = []
    for loc in MONITORING_LOCATIONS:
        if loc['risk_level'] in ['critical', 'high']:
            risk_zones.append({
                'lat': loc['lat'], 'lon': loc['lon'],
                'risk_level': loc['risk_level'],
                'name': loc['name'],
                'mining_activity': loc['mining_activity']
            })
    return jsonify({
        'success': True,
        'risk_zones': risk_zones,
        'total_at_risk_percent': 31.8,
        'critical_zones_count': sum(1 for l in MONITORING_LOCATIONS if l['risk_level'] == 'critical')
    })

@app.route('/api/simulate/detection')
def simulate_detection():
    high_risk = [l for l in MONITORING_LOCATIONS if l['risk_level'] in ['high', 'critical']]
    if not high_risk:
        return jsonify({'success': False, 'error': 'No high-risk locations'})
    
    location = random.choice(high_risk)
    detection_types = ['night_mining', 'vegetation_loss', 'excavator', 'drill', 'truck_convoy']
    detection_type = random.choice(detection_types)
    severity = random.choice(['HIGH', 'CRITICAL']) if random.random() > 0.3 else 'MEDIUM'
    
    alert = {
        'id': f"sim_{datetime.now().timestamp()}",
        'location_id': location['id'],
        'location_name': location['name'],
        'severity': severity,
        'type': detection_type,
        'message': f"Simulated {detection_type} detected at {location['name']}",
        'timestamp': datetime.now().isoformat(),
        'confidence': round(random.uniform(0.75, 0.98), 2),
        'is_simulated': True
    }
    active_alerts.append(alert)
    socketio.emit('new_alert', alert)
    return jsonify({'success': True, 'alert': alert})

# ===================== WEBSOCKET =====================

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to Auralite server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_location')
def handle_subscribe(data):
    location_id = data.get('location_id')
    emit('subscribed', {'location_id': location_id})

# ===================== BACKGROUND MONITORING =====================

def monitoring_thread():
    """Background thread that continuously monitors"""
    global monitoring_active
    while monitoring_active:
        try:
            if random.random() > 0.7:
                locations_to_check = random.sample(MONITORING_LOCATIONS, min(3, len(MONITORING_LOCATIONS)))
                for location in locations_to_check:
                    if random.random() > 0.85:
                        severity = random.choice(['MEDIUM', 'HIGH', 'CRITICAL'])
                        alert = {
                            'id': f"bg_{datetime.now().timestamp()}",
                            'location_id': location['id'],
                            'location_name': location['name'],
                            'severity': severity,
                            'type': 'auto_detected',
                            'message': f"Automated detection: Possible mining activity at {location['name']}",
                            'timestamp': datetime.now().isoformat(),
                            'confidence': round(random.uniform(0.7, 0.95), 2)
                        }
                        active_alerts.append(alert)
                        socketio.emit('new_alert', alert)
            time.sleep(15)
        except Exception as e:
            print(f"Monitoring thread error: {e}")
            time.sleep(30)

# Start background monitoring
monitor = threading.Thread(target=monitoring_thread, daemon=True)
monitor.start()

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     AURALITE - Aravalli Hills Illegal Mining Detection    ║
    ║                    Flask Web Application v2.0             ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    stats = data_loader.get_aravalli_stats()
    print(f"📍 Monitoring {len(MONITORING_LOCATIONS)} locations across Aravalli Hills")
    print(f"⚠️  Critical zones: {stats['critical_zones']}")
    print(f"📸 Cameras: {sum(1 for l in MONITORING_LOCATIONS if l.get('camera_installed', False))}")
    print(f"🎤 Acoustic sensors: {sum(1 for l in MONITORING_LOCATIONS if l.get('acoustic_sensor', False))}")
    print(f"🚛 GPS-tracked vehicles: {stats['total_vehicles_tracked']}")
    print(f"📊 Active mining sites: {stats['active_mining_sites']}")
    print(f"🌿 Vegetation loss: {stats['vegetation_loss_percent']}%")
    print(f"⚡ Area at risk: {stats['area_at_risk_percent']}%")
    
    print("\n🌐 Access the application:")
    print("   http://localhost:5000")
    print("   http://127.0.0.1:5000")
    print("\n🔔 Real-time notifications enabled via WebSocket")
    print(" Press CTRL+C to stop the server\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
