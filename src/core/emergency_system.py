import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from config import TIMEZONE
import requests

class EmergencySystem:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def add_emergency_contact(self, username, contact_name, phone_number, priority=1, relation=""):
        """Add emergency contact with priority"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO emergency_contacts (username, contact_name, phone_number, priority, relation)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, contact_name, phone_number, priority, relation))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error adding emergency contact: {e}")
        
        if "emergency_contacts" not in st.session_state:
            st.session_state.emergency_contacts = []
        
        st.session_state.emergency_contacts.append({
            "username": username,
            "contact_name": contact_name,
            "phone_number": phone_number,
            "priority": priority,
            "relation": relation
        })
        return True
    
    def get_emergency_contacts(self, username):
        """Get emergency contacts sorted by priority"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT contact_name, phone_number, priority, relation FROM emergency_contacts
                    WHERE username = %s ORDER BY priority ASC
                """, (username,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching emergency contacts: {e}")
        
        if "emergency_contacts" not in st.session_state:
            return []
        
        contacts = [c for c in st.session_state.emergency_contacts if c["username"] == username]
        return sorted(contacts, key=lambda x: x["priority"])
    
    def trigger_sos(self, username, location_lat=None, location_lon=None, last_frame=None):
        """Trigger SOS alert to all emergency contacts"""
        contacts = self.get_emergency_contacts(username)
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        alert_data = {
            "username": username,
            "timestamp": timestamp,
            "location": f"{location_lat}, {location_lon}" if location_lat and location_lon else "Unknown",
            "status": "SOS_TRIGGERED"
        }
        
        # Log the SOS event
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO sos_logs (username, timestamp, location_lat, location_lon)
                    VALUES (%s, %s, %s, %s)
                """, (username, timestamp, location_lat, location_lon))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error logging SOS: {e}")
        
        if "sos_logs" not in st.session_state:
            st.session_state.sos_logs = []
        
        st.session_state.sos_logs.append(alert_data)
        
        # Send alerts to contacts (in priority order)
        results = []
        for contact in contacts:
            result = self._send_alert_to_contact(
                contact[0],  # contact_name
                contact[1],  # phone_number
                username,
                alert_data
            )
            results.append(result)
        
        return results
    
    def _send_alert_to_contact(self, contact_name, phone_number, username, alert_data):
        """Send alert to a single contact"""
        message = f"🚨 EMERGENCY SOS from {username}!\nTime: {alert_data['timestamp']}\nLocation: {alert_data['location']}"
        
        # Placeholder for SMS/call integration (Twilio, etc.)
        # For now, just log it
        return {
            "contact": contact_name,
            "phone": phone_number,
            "status": "alert_sent",
            "message": message,
            "timestamp": alert_data['timestamp']
        }
    
    def get_sos_history(self, username, days=30):
        """Get SOS history"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT timestamp, location_lat, location_lon FROM sos_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY timestamp DESC
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching SOS history: {e}")
        
        if "sos_logs" not in st.session_state:
            return []
        
        return [s for s in st.session_state.sos_logs if s["username"] == username]
