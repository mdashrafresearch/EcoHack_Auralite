from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)

# Database configuration
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'auralite.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    area_sqkm = db.Column(db.Float, nullable=False)
    current_risk_level = db.Column(db.String(20), default='Low')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    indicators = db.relationship('EnvironmentalIndicators', backref='region', lazy=True)
    risk_history = db.relationship('RiskScoreHistory', backref='region', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'area_sqkm': self.area_sqkm,
            'current_risk_level': self.current_risk_level,
            'last_updated': self.last_updated.isoformat()
        }

class EnvironmentalIndicators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ndvi_drop = db.Column(db.Float, nullable=False)
    nightlight_inc = db.Column(db.Float, nullable=False)
    acoustic_score = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'region_id': self.region_id,
            'timestamp': self.timestamp.isoformat(),
            'ndvi_drop': round(self.ndvi_drop, 3),
            'nightlight_inc': round(self.nightlight_inc, 3),
            'acoustic_score': round(self.acoustic_score, 3)
        }

class RiskScoreHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    final_score = db.Column(db.Float, nullable=False)
    ai_score = db.Column(db.Float, nullable=False)
    rule_score = db.Column(db.Float, nullable=False)
    classification = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'region_id': self.region_id,
            'timestamp': self.timestamp.isoformat(),
            'final_score': round(self.final_score, 3),
            'ai_score': round(self.ai_score, 3),
            'rule_score': round(self.rule_score, 3),
            'classification': self.classification
        }

# Engine Logic
from engine import engine

def refresh_global_model():
    """Trains the model with all current indicator data in DB."""
    indicators = EnvironmentalIndicators.query.all()
    if indicators:
        data = [{'ndvi_drop': i.ndvi_drop, 'nightlight_inc': i.nightlight_inc, 'acoustic_score': i.acoustic_score} for i in indicators]
        engine.train_global_model(data)

@app.route('/api/regions', methods=['GET'])
def get_regions():
    regions = Region.query.all()
    return jsonify([r.to_dict() for r in regions])

@app.route('/api/analyze/<int:region_id>', methods=['GET'])
def analyze_region(region_id):
    region = Region.query.get_or_404(region_id)
    latest_indicator = EnvironmentalIndicators.query.filter_by(region_id=region_id).order_by(EnvironmentalIndicators.timestamp.desc()).first()
    
    if not latest_indicator:
        return jsonify({'error': 'No data available for this region'}), 404

    # Ensure model is trained
    if not engine.is_trained:
        refresh_global_model()

    # Compute Risk
    indicator_data = {
        'ndvi_drop': latest_indicator.ndvi_drop,
        'nightlight_inc': latest_indicator.nightlight_inc,
        'acoustic_score': latest_indicator.acoustic_score
    }
    final_score, ai_score, rule_score = engine.compute_final_score(indicator_data)
    classification = engine.classify_risk(final_score)
    confidence = engine.get_confidence(ai_score, rule_score)

    # Update Region status
    region.current_risk_level = classification
    region.last_updated = datetime.utcnow()

    # Save to history if significant change or periodic
    new_history = RiskScoreHistory(
        region_id=region_id,
        final_score=final_score,
        ai_score=ai_score,
        rule_score=rule_score,
        classification=classification,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_history)
    db.session.commit()
    
    history = RiskScoreHistory.query.filter_by(region_id=region_id).order_by(RiskScoreHistory.timestamp.desc()).limit(15).all()
    
    return jsonify({
        'region': region.to_dict(),
        'latest_indicators': latest_indicator.to_dict(),
        'risk_analysis': {
            'final_score': final_score,
            'ai_score': ai_score,
            'rule_score': rule_score,
            'classification': classification,
            'confidence': confidence
        },
        'history': [h.to_dict() for h in history]
    })

@app.route('/api/risk-summary', methods=['GET'])
def risk_summary():
    total_regions = Region.query.count()
    high_risk = Region.query.filter_by(current_risk_level='High').count()
    med_risk = Region.query.filter_by(current_risk_level='Medium').count()
    
    avg_score = 0
    # Average of last scores for each region
    regions = Region.query.all()
    scores = []
    for r in regions:
        latest_history = RiskScoreHistory.query.filter_by(region_id=r.id).order_by(RiskScoreHistory.timestamp.desc()).first()
        if latest_history:
            scores.append(latest_history.final_score)
    
    if scores:
        avg_score = sum(scores) / len(scores)

    return jsonify({
        'total_regions': total_regions,
        'high_risk_count': high_risk,
        'medium_risk_count': med_risk,
        'average_risk_score': round(avg_score, 2),
        'health_index': round(100 - (avg_score * 100), 1) # Rule of thumb: Higher risk = lower health
    })

import math

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance in km between two points."""
    R = 6371 # Earth radius
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route('/api/analyze-location', methods=['POST'])
def analyze_location():
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')

    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    # Find nearest region within 20km
    regions = Region.query.all()
    nearest_region = None
    min_dist = float('inf')

    for r in regions:
        dist = haversine(lat, lng, r.latitude, r.longitude)
        if dist < min_dist:
            min_dist = dist
            nearest_region = r

    if nearest_region is None or min_dist > 20:
        return jsonify({'message': 'No monitoring data available for this location.'}), 404

    # Use the nearest region's latest data to compute risk for this coordinate
    latest_indicator = EnvironmentalIndicators.query.filter_by(region_id=nearest_region.id).order_by(EnvironmentalIndicators.timestamp.desc()).first()
    
    if not latest_indicator:
        return jsonify({'error': 'No data available for the nearest region'}), 404

    # Ensure model is trained
    if not engine.is_trained:
        refresh_global_model()

    indicator_data = {
        'ndvi_drop': latest_indicator.ndvi_drop,
        'nightlight_inc': latest_indicator.nightlight_inc,
        'acoustic_score': latest_indicator.acoustic_score
    }
    final_score, ai_score, rule_score = engine.compute_final_score(indicator_data)
    classification = engine.classify_risk(final_score)

    return jsonify({
        'region_name': nearest_region.name,
        'latitude': lat,
        'longitude': lng,
        'ndvi_drop': round(latest_indicator.ndvi_drop, 3),
        'nightlight_inc': round(latest_indicator.nightlight_inc, 3),
        'acoustic_score': round(latest_indicator.acoustic_score, 3),
        'anomaly_score': round(ai_score, 3),
        'composite_score': round(rule_score, 3),
        'final_score': round(final_score, 3),
        'classification': classification,
        'distance_km': round(min_dist, 2)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initial training if data exists
        refresh_global_model()
    app.run(debug=True, port=5000)
