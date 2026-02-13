import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE
import pandas as pd

class VitalSignsTracker:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def add_vital_sign(self, username, vital_type, value, unit):
        """Record a vital sign reading"""
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO vital_signs (username, vital_type, value, unit, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, vital_type, value, unit, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error recording vital sign: {e}")
        
        # Fallback to session state
        if "vital_signs_log" not in st.session_state:
            st.session_state.vital_signs_log = []
        
        st.session_state.vital_signs_log.append({
            "username": username,
            "vital_type": vital_type,
            "value": value,
            "unit": unit,
            "timestamp": timestamp
        })
        return True
    
    def get_vital_signs(self, username, vital_type=None, days=7):
        """Fetch vital signs for a user"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                if vital_type:
                    cursor.execute("""
                        SELECT vital_type, value, unit, timestamp FROM vital_signs
                        WHERE username = %s AND vital_type = %s
                        AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                        ORDER BY timestamp DESC
                    """, (username, vital_type, days))
                else:
                    cursor.execute("""
                        SELECT vital_type, value, unit, timestamp FROM vital_signs
                        WHERE username = %s
                        AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                        ORDER BY timestamp DESC
                    """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching vital signs: {e}")
        
        # Fallback to session state
        if "vital_signs_log" not in st.session_state:
            return []
        
        filtered = [v for v in st.session_state.vital_signs_log if v["username"] == username]
        if vital_type:
            filtered = [v for v in filtered if v["vital_type"] == vital_type]
        return filtered
    
    def check_abnormal_readings(self, username):
        """Check for abnormal vital signs"""
        alerts = []
        
        # Normal ranges
        ranges = {
            "heart_rate": (60, 100),
            "blood_pressure_systolic": (90, 120),
            "blood_pressure_diastolic": (60, 80),
            "temperature": (36.5, 37.5),
            "blood_oxygen": (95, 100)
        }
        
        vitals = self.get_vital_signs(username, days=1)
        
        for vital_type, value, unit, timestamp in vitals:
            if vital_type in ranges:
                min_val, max_val = ranges[vital_type]
                if value < min_val or value > max_val:
                    alerts.append({
                        "vital": vital_type,
                        "value": value,
                        "unit": unit,
                        "timestamp": timestamp,
                        "status": "abnormal"
                    })
        
        return alerts
