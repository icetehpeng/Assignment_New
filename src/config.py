import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ngrok Configuration
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
NGROK_ADDR = int(os.getenv("NGROK_ADDR", 8501))
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "elderly_care_system")
}

# System Configuration
TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "Asia/Kuala_Lumpur"))
NODERED_ENDPOINT = os.getenv("NODERED_ENDPOINT", "http://localhost:1880/fall-alert")
