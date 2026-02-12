import mysql.connector
import streamlit as st
from config import DB_CONFIG

def get_db_connection():
    """Try to connect to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn, True
    except mysql.connector.Error as e:
        st.sidebar.warning(f"⚠️ MySQL not available: {e}")
        return None, False

def create_tables(db_conn):
    """Create database tables automatically"""
    try:
        cursor = db_conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create activity_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                activity VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                title VARCHAR(100),
                message TEXT,
                trigger_time DATETIME,
                repeat_type VARCHAR(20),
                audio_data LONGBLOB,
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create messages table for chat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender VARCHAR(50),
                receiver VARCHAR(50),
                content TEXT,
                audio_data LONGBLOB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vital signs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vital_signs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                vital_type VARCHAR(50),
                value FLOAT,
                unit VARCHAR(20),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Medications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                name VARCHAR(100),
                dosage VARCHAR(50),
                frequency VARCHAR(50),
                start_date DATE,
                end_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Medication logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medication_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                medication_name VARCHAR(100),
                taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Safe zones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS safe_zones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                zone_name VARCHAR(100),
                latitude FLOAT,
                longitude FLOAT,
                radius_meters INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Location logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS location_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                latitude FLOAT,
                longitude FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Emergency contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                contact_name VARCHAR(100),
                phone_number VARCHAR(20),
                priority INT,
                relation VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # SOS logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sos_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location_lat FLOAT,
                location_lon FLOAT
            )
        """)
        
        # Activity logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                activity_type VARCHAR(50),
                duration_minutes INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Meals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                meal_name VARCHAR(100),
                food_items TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Water logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                amount_ml INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Mood logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                mood_emoji VARCHAR(10),
                mood_text VARCHAR(50),
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Depression screenings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS depression_screenings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                phq9_score INT,
                severity VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cognitive activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cognitive_activities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                game_name VARCHAR(100),
                score INT,
                duration_minutes INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Smart devices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(50),
                device_name VARCHAR(100),
                device_type VARCHAR(50),
                ip_address VARCHAR(50),
                port INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Device logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(50),
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Routines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                routine_name VARCHAR(100),
                trigger TEXT,
                actions TEXT,
                enabled BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Access permissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                caregiver VARCHAR(50),
                permissions JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Time-based access table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_based_access (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                caregiver VARCHAR(50),
                start_time TIME,
                end_time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Access logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                caregiver VARCHAR(50),
                resource_type VARCHAR(50),
                action VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Error logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                error_id VARCHAR(50) UNIQUE,
                error_type VARCHAR(100),
                message TEXT,
                severity VARCHAR(20),
                username VARCHAR(50),
                context JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_error_type (error_type),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        # Recovery logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                error_id VARCHAR(50),
                recovery_action TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_error_id (error_id)
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                theme VARCHAR(50) DEFAULT 'dark',
                language VARCHAR(10) DEFAULT 'en',
                dashboard_layout JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            )
        """)
        
        # Activities table (for activity tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                activity_type VARCHAR(50),
                duration_minutes INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        db_conn.commit()
        return True, "✅ Tables created successfully!"
        
    except Exception as e:
        return False, f"❌ Error creating tables: {e}"
