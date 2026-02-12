import streamlit as st
from datetime import datetime
from config import TIMEZONE
import math

class GeofencingSystem:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def create_safe_zone(self, username, zone_name, latitude, longitude, radius_meters):
        """Create a safe zone (geofence)"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO safe_zones (username, zone_name, latitude, longitude, radius_meters)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, zone_name, latitude, longitude, radius_meters))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error creating safe zone: {e}")
        
        if "safe_zones" not in st.session_state:
            st.session_state.safe_zones = []
        
        st.session_state.safe_zones.append({
            "username": username,
            "zone_name": zone_name,
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius_meters
        })
        return True
    
    def log_location(self, username, latitude, longitude):
        """Log user location"""
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO location_logs (username, latitude, longitude, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (username, latitude, longitude, timestamp))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error logging location: {e}")
        
        if "location_logs" not in st.session_state:
            st.session_state.location_logs = []
        
        st.session_state.location_logs.append({
            "username": username,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        })
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates (Haversine formula)"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def check_geofence_violation(self, username, latitude, longitude):
        """Check if user is outside safe zones"""
        safe_zones = self.get_safe_zones(username)
        
        for zone in safe_zones:
            distance = self.calculate_distance(
                latitude, longitude,
                zone[2], zone[3]  # zone latitude, longitude
            )
            
            if distance > zone[4]:  # zone radius
                return {
                    "violated": True,
                    "zone": zone[1],
                    "distance_from_zone": distance,
                    "timestamp": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                }
        
        return {"violated": False}
    
    def get_safe_zones(self, username):
        """Get all safe zones for a user"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT zone_name, latitude, longitude, radius_meters FROM safe_zones
                    WHERE username = %s
                """, (username,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching safe zones: {e}")
        
        if "safe_zones" not in st.session_state:
            return []
        
        return [z for z in st.session_state.safe_zones if z["username"] == username]
    
    def get_location_history(self, username, hours=24):
        """Get location history"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT latitude, longitude, timestamp FROM location_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                    ORDER BY timestamp DESC
                """, (username, hours))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching location history: {e}")
        
        if "location_logs" not in st.session_state:
            return []
        
        return [l for l in st.session_state.location_logs if l["username"] == username]
