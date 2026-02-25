# Auralite - Illegal Mining Detection System for Aravalli Hills

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)


<p align="center">
  <b>Multi-Modal Illegal Mining Detection System for Aravalli Hills</b><br>
  Combining Satellite Imagery, Acoustic Sensors, Camera Feeds & GPS Tracking
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Production Deployment](#-production-deployment)
- [Auto Documentation](#-auto-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌄 Overview

Auralite is an advanced multi-modal illegal mining detection system designed specifically for the **Aravalli Hills** - one of India's oldest mountain ranges facing severe ecological threats from illegal mining activities.

The system combines:
- 🛰️ **Satellite Imagery** - NDVI analysis, nightlight detection
- 📹 **Camera Feeds** - Live PTZ cameras with AI object detection
- 🎤 **Acoustic Sensors** - Mining machinery sound classification
- 🚛 **GPS Tracking** - Mineral transport vehicle monitoring
- 🔔 **Real-time Alerts** - Instant notifications via WebSocket

### Why Aravalli Hills?

Based on recent reports:
- **31.8%** of Aravalli range at risk due to 100m elevation rule
- **8,000+** illegal mining sites identified
- **5,772.7 km²** lost between 1979-2019
- **22%** projected loss by 2059

---

## ✨ Features

### 🛰️ Satellite Monitoring
- Real-time NDVI analysis from Sentinel-2 & Landsat
- Nightlight anomaly detection from VIIRS
- Cloud masking & atmospheric correction
- Historical trend analysis

### 📹 Camera Integration
- RTSP stream support for IP cameras
- AI-powered object detection (YOLOv8)
- Vehicle & personnel counting
- Night vision & thermal camera support
- Motion detection & alerts

### 🎤 Acoustic Sensors
- Mining machinery classification (excavator, drill, crusher)
- Real-time audio processing
- Noise reduction & filtering
- Frequency signature analysis
- IoT sensor network support

### 🚛 GPS Tracking
- Real-time vehicle tracking
- RFID gate integration (as per NGT)
- Checkpoint monitoring
- Route anomaly detection
- Mineral transport validation

### 📊 Dashboard & Analytics
- Interactive maps with Leaflet
- Real-time charts & graphs
- Historical data visualization
- Export reports (PDF, CSV, JSON)
- Custom date range analysis

### 🔔 Alert System
- WebSocket real-time notifications
- Sound alerts for critical events
- Email/SMS notifications
- Alert acknowledgment workflow
- Severity-based escalation

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Sentinel   │     IP        │   Acoustic   │     GPS       │
│   Satellite  │   Cameras     │   Sensors    │   Trackers    │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
       ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                          │
│    Sentinel Hub API    RTSP Stream    MQTT    GPS Gateway  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                         │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐ │
│  │   NDVI     │  │   Object   │  │  Sound Classification│ │
│  │  Analysis  │  │  Detection │  │   (YAMNet/YOLOv8)    │ │
│  └────────────┘  └────────────┘  └──────────────────────┘ │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐ │
│  │   Change   │  │   Route    │  │   Multi-modal        │ │
│  │  Detection │  │  Analysis  │  │   Fusion             │ │
│  └────────────┘  └────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                            │
│    PostgreSQL    Redis    InfluxDB    MinIO (Object Store) │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│    Flask API    WebSocket    Celery    Flask-SocketIO      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                        │
│    Web Dashboard    Mobile App    Alert System    Reports  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Core programming language |
| Flask 2.3+ | Web framework |
| Flask-SocketIO | Real-time WebSocket communication |
| Flask-SQLAlchemy | Database ORM |
| Celery | Task queue for background jobs |
| Redis | Message broker & caching |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| TensorFlow 2.13+ | Deep learning models |
| scikit-learn | Classical ML algorithms |
| YAMNet | Audio classification |
| YOLOv8 | Object detection |
| Librosa | Audio processing |
| OpenCV | Image/video processing |

### Geospatial
| Technology | Purpose |
|------------|---------|
| Sentinel Hub API | Satellite data access |
| Google Earth Engine | Satellite imagery processing |
| GDAL | Geospatial data abstraction |
| GeoPandas | Geospatial data manipulation |
| Folium | Interactive maps |
| Leaflet | Map visualization |

### Database
| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary database |
| PostGIS | Geospatial extensions |
| Redis | Caching & real-time data |
| InfluxDB | Time-series data |

### Frontend
| Technology | Purpose |
|------------|---------|
| Bootstrap 5 | UI framework |
| Chart.js | Data visualization |
| Leaflet.js | Interactive maps |
| jQuery | DOM manipulation |
| Socket.IO-client | Real-time updates |

### DevOps & Deployment
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Reverse proxy & load balancing |
| Gunicorn | WSGI server |
| GitHub Actions | CI/CD |

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9 or higher
python --version

# Git
git --version

# PostgreSQL (for production)
postgres --version
```

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/auralite.git
cd auralite

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database
python scripts/init_db.py

# 6. Run the application
python run.py

# 7. Open browser
# http://localhost:5000
```

---

## 📦 Installation

### Detailed Installation Guide

#### 1. System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    ffmpeg \
    libsndfile1 \
    libgl1-mesa-glx \
    libglib2.0-0
```

**CentOS/RHEL:**
```bash
sudo yum update
sudo yum install -y \
    python3-pip \
    python3-devel \
    postgresql-server \
    postgresql-contrib \
    redis \
    nginx \
    ffmpeg \
    libsndfile \
    mesa-libGL \
    glib2
```

**macOS:**
```bash
brew install python@3.9
brew install postgresql
brew install redis
brew install nginx
brew install ffmpeg
brew install libsndfile
```

#### 2. Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Python Packages

```bash
# Install all dependencies
pip install -r requirements.txt

# For development, install additional packages
pip install -r requirements-dev.txt
```

#### 4. Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql    # macOS

# Create database
sudo -u postgres psql -c "CREATE DATABASE auralite;"
sudo -u postgres psql -c "CREATE USER auralite WITH PASSWORD 'auralite123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE auralite TO auralite;"

# Initialize tables
python scripts/init_db.py

# Load sample data
python scripts/load_sample_data.py
```

#### 5. Redis Setup

```bash
# Start Redis
sudo systemctl start redis   # Linux
brew services start redis    # macOS

# Test Redis
redis-cli ping
# Should return: PONG
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://auralite:auralite123@localhost/auralite

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET_KEY=jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=28800  # 8 hours

# Sentinel Hub API
SENTINEL_CLIENT_ID=your-client-id
SENTINEL_CLIENT_SECRET=your-client-secret

# Google Earth Engine
EARTH_ENGINE_ACCOUNT=your-account
EARTH_ENGINE_PRIVATE_KEY=path/to/key.json

# MQTT Broker
MQTT_BROKER=mqtt://localhost:1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=alerts@auralite.in

# SMS Notifications (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Mapbox/Leaflet
MAPBOX_ACCESS_TOKEN=your-mapbox-token

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/auralite.log
```

### Application Configuration

Edit `config.py` for application-specific settings:

```python
class Config:
    # Aravalli specific bounds
    ARAVALLI_BOUNDS = {
        'min_lat': 23.5,
        'max_lat': 28.5,
        'min_lon': 72.5,
        'max_lon': 77.5
    }
    
    # Detection thresholds
    NDVI_ALERT_THRESHOLD = 0.3
    NIGHTLIGHT_ALERT_THRESHOLD = 15
    ACOUSTIC_CONFIDENCE_THRESHOLD = 0.75
    
    # Monitoring intervals (seconds)
    SATELLITE_UPDATE_INTERVAL = 3600  # 1 hour
    CAMERA_CAPTURE_INTERVAL = 300     # 5 minutes
    ACOUSTIC_SAMPLE_DURATION = 60      # 1 minute
    GPS_UPDATE_INTERVAL = 10           # 10 seconds
```

---

## 🎮 Usage Guide

### Running the Application

#### Development Mode
```bash
# Terminal 1 - Flask app
python run.py

# Terminal 2 - Celery worker (for background tasks)
celery -A app.celery worker --loglevel=info

# Terminal 3 - Redis (if not running as service)
redis-server
```

#### Production Mode
```bash
# Using Gunicorn
gunicorn -w 4 -k eventlet "app:app" --bind 0.0.0.0:8000

# With systemd service (Linux)
sudo systemctl start auralite
sudo systemctl enable auralite
```

### Accessing the Application

| URL | Description |
|-----|-------------|
| `http://localhost:5000` | Home page with overview |
| `http://localhost:5000/dashboard` | Main monitoring dashboard |
| `http://localhost:5000/map` | Interactive map |
| `http://localhost:5000/camera_feed` | Live camera feeds |
| `http://localhost:5000/sensors` | Acoustic sensor data |
| `http://localhost:5000/alerts` | Active alerts |
| `http://localhost:5000/documentation` | Auto-generated documentation |

### Default Login Credentials

**Admin User:**
- Username: `admin`
- Password: `auralite2026`

**Forest Officer:**
- Username: `officer`
- Password: `forest2026`

**Viewer:**
- Username: `viewer`
- Password: `view2026`

---

## 📡 API Documentation

### Authentication

All API endpoints require JWT authentication except `/auth/login` and `/auth/register`.

```bash
# Get JWT token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "auralite2026"}'

# Response
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}

# Use token in subsequent requests
curl -X GET http://localhost:5000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Endpoints

#### Locations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations` | Get all monitoring locations |
| GET | `/api/locations/<id>` | Get specific location |
| POST | `/api/locations` | Add new location (admin only) |
| PUT | `/api/locations/<id>` | Update location |
| DELETE | `/api/locations/<id>` | Delete location |

**Example:**
```bash
curl -X GET http://localhost:5000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "locations": [
    {
      "id": "raj_001",
      "name": "Sariska Tiger Reserve",
      "lat": 27.3217,
      "lon": 76.4378,
      "state": "Rajasthan",
      "risk_level": "high",
      "mining_activity": "active"
    }
  ]
}
```

#### Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect` | Run detection on location |
| GET | `/api/detect/all` | Run detection on all locations |
| GET | `/api/detections` | Get recent detections |

**Example:**
```bash
curl -X POST http://localhost:5000/api/detect \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location_id": "raj_001"}'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "is_mining": true,
    "severity": "HIGH",
    "confidence": 0.85,
    "alerts": [
      {
        "type": "vegetation_loss",
        "confidence": 0.92,
        "message": "NDVI dropped to 0.24"
      },
      {
        "type": "night_mining",
        "confidence": 0.78,
        "message": "Unusual night activity detected"
      }
    ],
    "recommendation": "URGENT: Dispatch inspection team"
  }
}
```

#### Satellite Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ndvi/<location_id>` | Get NDVI data |
| GET | `/api/nightlight/<location_id>` | Get nightlight data |
| GET | `/api/change_detection` | Get surface change analysis |

#### Sensor Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/acoustic/<location_id>` | Get acoustic sensor data |
| GET | `/api/camera/<location_id>` | Get camera detections |
| POST | `/api/sensor/register` | Register new sensor |
| POST | `/api/sensor/data` | Submit sensor data |

#### GPS Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gps/tracks` | Get vehicle tracks |
| GET | `/api/gps/vehicles` | Get active vehicles |
| POST | `/api/gps/anomaly` | Report GPS anomaly |

#### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | Get active alerts |
| POST | `/api/alerts/<id>/acknowledge` | Acknowledge alert |
| DELETE | `/api/alerts/<id>/resolve` | Resolve alert |

#### Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get system statistics |
| GET | `/api/stats/aravalli` | Get Aravalli-specific stats |
| GET | `/api/stats/export` | Export statistics (CSV/JSON) |

---

## 🏭 Production Deployment

### Docker Deployment

#### 1. Build Docker Image
```bash
# Build the image
docker build -t auralite:latest .

# Or use Docker Compose
cd docker
docker-compose build
```

#### 2. Configure Environment
```bash
# Create docker/.env file
cp docker/.env.example docker/.env
# Edit with your credentials
```

#### 3. Run with Docker Compose
```bash
cd docker
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

#### 4. Docker Compose Configuration

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: auralite
      POSTGRES_USER: auralite
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - auralite_network
    restart: always

  redis:
    image: redis:alpine
    networks:
      - auralite_network
    restart: always

  mqtt:
    image: eclipse-mosquitto
    ports:
      - "1883:1883"
    networks:
      - auralite_network
    restart: always

  api:
    build: ..
    environment:
      DATABASE_URL: postgresql://auralite:${DB_PASSWORD}@postgres/auralite
      REDIS_URL: redis://redis:6379
      MQTT_BROKER: mqtt://mqtt:1883
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      SENTINEL_CLIENT_ID: ${SENTINEL_CLIENT_ID}
      SENTINEL_CLIENT_SECRET: ${SENTINEL_CLIENT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - mqtt
    networks:
      - auralite_network
    restart: always
    volumes:
      - ../logs:/app/logs
      - ../static/captures:/app/static/captures

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ../static:/usr/share/nginx/html/static
    depends_on:
      - api
    networks:
      - auralite_network
    restart: always

networks:
  auralite_network:
    driver: bridge

volumes:
  postgres_data:
```

### Cloud Deployment

#### AWS EC2
```bash
# Launch EC2 instance (Ubuntu 20.04)
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Clone repository
git clone https://github.com/yourusername/auralite.git
cd auralite/docker

# Configure environment
cp .env.example .env
nano .env  # Add your credentials

# Run with Docker Compose
sudo docker-compose up -d
```

#### Google Cloud Platform
```bash
# Create Compute Engine instance
gcloud compute instances create auralite \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud \
  --machine-type n1-standard-4

# SSH into instance
gcloud compute ssh auralite

# Follow same steps as AWS
```

#### Azure
```bash
# Create VM
az vm create \
  --resource-group auralite-rg \
  --name auralite-vm \
  --image UbuntuLTS \
  --size Standard_D4s_v3

# SSH and deploy
ssh azureuser@your-vm-ip
```

### Production Checklist

- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure firewall (ufw)
- [ ] Set up automated backups
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up log rotation
- [ ] Create systemd service
- [ ] Configure email/SMS alerts
- [ ] Set up database replication (for HA)
- [ ] Configure CDN for static files
- [ ] Implement rate limiting
- [ ] Set up CI/CD pipeline

---

## 🤖 Auto Documentation

Auralite includes an AI-powered auto-documentation system that automatically:

1. **Opens your Flask application**
2. **Navigates through all pages**
3. **Records video of each feature**
4. **Generates AI voice narration**
5. **Creates subtitles**
6. **Compiles professional documentation**

### Run Auto-Documentation

```bash
# Make sure your Flask app is running
python run.py

# In another terminal, run auto-documentation
python run_auto_doc.py
```

### Output Files

```
recordings/
├── scenes/          # Individual scene recordings
├── narration/       # AI voice narration files
├── subtitles/       # SRT subtitle files
├── final/           # Compiled final video
└── documentation/   # HTML/Markdown documentation
```

### Customize Narration

Edit `auto_documentation/scene_planner.py` to customize narration scripts:

```python
def generate_narration_script(self, route):
    scripts = {
        "/": "Your custom intro text...",
        "/dashboard": "Your custom dashboard explanation..."
    }
    return scripts.get(route["url"], f"Exploring {route['name']}")
```

---


### Development Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/yourusername/auralite.git
cd auralite

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Keep functions focused and small

### Pull Request Process

1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Auralite Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact

### Team
- **Saravanakumar M B** - ML & Data Modeling - [@mbsaravanakumar2006-dotcom](https://github.com/mbsaravanakumar2006-dotcom)
- **Sanjay Yuvanraj B** - GIS & Remote Sensing - [@sanjayyuvanraj2006-cloud](https://github.com/sanjayyuvanraj2006-cloud)
- **Mohammed Ashraf A** - IoT & Backend - [@mdashrafresearch](https://github.com/mdashrafresearch)

### Project Links
- **GitHub Repository**: [https://github.com/mdashrafresearch/EcoHack_Auralite]([https://github.com/yourusername/auralite](https://github.com/mdashrafresearch/EcoHack_Auralite))
- **Documentation** : Inside Application Website

---

## 🙏 Acknowledgments

- **Indian Forest Department** - For domain expertise and field support
- **National Green Tribunal (NGT)** - For regulatory guidance
- **ISRO** - For satellite data access
- **Google Earth Engine** - For geospatial processing
- **Sentinel Hub** - For satellite imagery API
- **OpenStreetMap** - For map data
- **All Contributors** - Who helped make this project possible

---

## 📊 Project Status

| Metric | Status |
|--------|--------|
| Build | ![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/auralite/ci.yml) |
| Coverage | ![Coverage](https://img.shields.io/codecov/c/github/yourusername/auralite) |
| Version | ![Version](https://img.shields.io/github/v/release/yourusername/auralite) |
| Downloads | ![Downloads](https://img.shields.io/pypi/dm/auralite) |
| Stars | ![Stars](https://img.shields.io/github/stars/yourusername/auralite) |

---

<p align="center">
  Made with ❤️ for the Aravalli Hills
</p>
