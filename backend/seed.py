from app import app, db, SensorData
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        sensors = [
            {'type': 'Temperature', 'unit': '°C', 'location': 'Server Room'},
            {'type': 'Humidity', 'unit': '%', 'location': 'Server Room'},
            {'type': 'Air Quality', 'unit': 'AQI', 'location': 'Main Hall'},
            {'type': 'Temperature', 'unit': '°C', 'location': 'Main Hall'},
            {'type': 'CO2', 'unit': 'ppm', 'location': 'Meeting Room'},
        ]

        # Generate data for the last 24 hours
        start_time = datetime.utcnow() - timedelta(days=1)
        
        data_points = []
        for sensor in sensors:
            for i in range(144): # Every 10 minutes
                timestamp = start_time + timedelta(minutes=i*10)
                
                if sensor['type'] == 'Temperature':
                    value = random.uniform(20.0, 25.0)
                elif sensor['type'] == 'Humidity':
                    value = random.uniform(40.0, 60.0)
                elif sensor['type'] == 'Air Quality':
                    value = random.uniform(30.0, 70.0)
                elif sensor['type'] == 'CO2':
                    value = random.uniform(400.0, 800.0)
                
                data_points.append(SensorData(
                    sensor_type=sensor['type'],
                    value=round(value, 2),
                    unit=sensor['unit'],
                    location=sensor['location'],
                    timestamp=timestamp
                ))

        db.session.add_all(data_points)
        db.session.commit()
        print(f"Successfully seeded {len(data_points)} data points.")

if __name__ == '__main__':
    seed_data()
