from app import app, db, Region, EnvironmentalIndicators, RiskScoreHistory
from datetime import datetime, timedelta
import random

def seed_mining_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        regions_data = [
            {'name': 'Amazon Basin Sector A', 'lat': -3.4653, 'lng': -62.2159, 'area': 1200},
            {'name': 'Gongo Soco Reserve', 'lat': -19.9822, 'lng': -43.6125, 'area': 850},
            {'name': 'Kyushu Forest Zone', 'lat': 32.5933, 'lng': 130.7333, 'area': 500},
            {'name': 'Congo Basin North', 'lat': 0.5273, 'lng': 25.2822, 'area': 2100},
            {'name': 'Kalimantan West', 'lat': -0.0006, 'lng': 109.3332, 'area': 1400},
            {'name': 'Appalachian Highlands', 'lat': 37.5, 'lng': -82.5, 'area': 900},
        ]

        regions = []
        for rd in regions_data:
            r = Region(
                name=rd['name'],
                latitude=rd['lat'],
                longitude=rd['lng'],
                area_sqkm=rd['area']
            )
            db.session.add(r)
            regions.append(r)
        
        db.session.commit()

        # Generate data for the last 30 days
        start_time = datetime.utcnow() - timedelta(days=30)
        
        for r in regions:
            # Assign a "personality" to each region
            if r.name == 'Amazon Basin Sector A':
                profile = 'HighRisk' # Clear mining activity
            elif r.name == 'Kalimantan West':
                profile = 'MedRisk'  # Early stages/Expanding
            elif r.name == 'Kyushu Forest Zone':
                profile = 'LowRisk'  # Pristine
            else:
                profile = random.choice(['LowRisk', 'MedRisk'])

            for day in range(30):
                timestamp = start_time + timedelta(days=day)
                
                if profile == 'HighRisk':
                    # High NDVI drop, High Nightlight, High Acoustic
                    ndvi_drop = random.uniform(0.6, 0.9)
                    nightlight = random.uniform(0.7, 1.0)
                    acoustic = random.uniform(0.65, 0.95)
                elif profile == 'MedRisk':
                    # Modest NDVI drop, Sporadic Nightlight, Moderate Acoustic
                    ndvi_drop = random.uniform(0.2, 0.5)
                    nightlight = random.uniform(0.3, 0.6)
                    acoustic = random.uniform(0.3, 0.5)
                else: # LowRisk
                    # Minimal changes
                    ndvi_drop = random.uniform(0.01, 0.1)
                    nightlight = random.uniform(0.01, 0.1)
                    acoustic = random.uniform(0.01, 0.15)

                indicator = EnvironmentalIndicators(
                    region_id=r.id,
                    timestamp=timestamp,
                    ndvi_drop=ndvi_drop,
                    nightlight_inc=nightlight,
                    acoustic_score=acoustic
                )
                db.session.add(indicator)

        db.session.commit()
        print(f"Successfully seeded {len(regions)} regions and 180 indicator records.")

if __name__ == '__main__':
    seed_mining_data()
