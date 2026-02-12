# Setup Guide

## Prerequisites

- Python 3.8+
- MySQL 5.7+
- Node.js 14+
- Node-RED
- Camera/Webcam

## Quick Setup (5 minutes)

### 1. Database
```bash
mysql -u root -p < setup_database.sql
```

### 2. Environment
Create `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=elderly_care_system
TIMEZONE=Asia/Singapore
```

### 3. Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Services
```bash
./scripts/start_all_services.bat
```

### 5. Access
- Streamlit: http://localhost:8501
- Node-RED: http://localhost:1880

## Detailed Setup

### Database Setup
```bash
# Run setup script
mysql -u root -p < setup_database.sql

# Verify
mysql -u root -p elderly_care_system -e "SHOW TABLES;"
```

### Node-RED Configuration

1. Install nodes:
```bash
npm install node-red-node-mysql
npm install node-red-contrib-telegrambot
```

2. Import flow: `nodered-fall-detection-production-complete.json`

3. Configure:
   - MySQL connection to `elderly_care_system`
   - Telegram bot token
   - Chat ID for alerts

### Testing

1. Open http://localhost:8501
2. Go to CCTV page
3. Lie down in front of camera
4. Wait 2 seconds for confirmation
5. Receive Telegram alert with image

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection failed | Check MySQL running, verify credentials |
| No video stream | Check camera permissions, verify ngrok |
| Fall not detected | Lie down horizontally (width > height) |
| No alerts | Verify Node-RED running, check Telegram token |
| Services won't start | Check ports 5000, 1880, 8501 are free |

## File Structure

```
.
├── README.md
├── SETUP.md
├── DEPLOYMENT.md
├── FEATURES.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── main.py                          # Streamlit app entry
│   ├── database.py                      # Database connection
│   ├── config.py                        # Configuration
│   │
│   ├── core/                            # Core features
│   │   ├── vital_signs.py
│   │   ├── medication_manager.py
│   │   ├── activity_recognition.py
│   │   ├── fall_detector.py
│   │   ├── emergency_system.py
│   │   └── geofencing.py
│   │
│   ├── features/                        # Additional features
│   │   ├── mood_tracker.py
│   │   ├── nutrition_tracker.py
│   │   ├── voice_control.py
│   │   ├── smart_home.py
│   │   └── caregiver_dashboard.py
│   │
│   ├── ui/                              # User interface
│   │   ├── ui_pages.py
│   │   ├── ui_health.py
│   │   ├── ui_safety.py
│   │   ├── ui_lifestyle.py
│   │   ├── ui_analytics.py
│   │   ├── theme_manager.py
│   │   ├── dashboard_customizer.py
│   │   └── accessibility.py
│   │
│   ├── utils/                           # Utilities
│   │   ├── cache_manager.py
│   │   ├── error_logger.py
│   │   ├── rate_limiter.py
│   │   ├── language_manager.py
│   │   ├── report_generator.py
│   │   ├── privacy_manager.py
│   │   ├── offline_mode.py
│   │   ├── offline_sync_manager.py
│   │   ├── audio_system.py
│   │   └── chat_manager.py
│   │
│   └── video/                           # Video processing
│       ├── frame_server.py              # Flask video server
│       └── video_processor.py
│
├── nodered/                             # Node-RED flows
│   ├── nodered-fall-detection-production-complete.json
│   └── nodered-fall-detection-debug.json
│
├── database/                            # Database
│   └── setup_database.sql
│
├── scripts/                             # Utility scripts
│   ├── start_all_services.bat
│   └── stop_all_services.bat
│
├── logs/                                # Application logs
│   └── app_errors.log
│
└── .offline_cache/                      # Offline data
    ├── message_queue.json
    └── sync_queue.db
```

## Next Steps

1. Complete setup above
2. Test fall detection
3. Configure Telegram alerts
4. Deploy to production (see DEPLOYMENT.md)
