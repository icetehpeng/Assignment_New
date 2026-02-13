import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE
import json

class PrivacyManager:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def set_access_permissions(self, username, caregiver, permissions):
        """Set granular access permissions for caregiver"""
        # permissions: {"camera": True, "messages": False, "health": True, "location": False}
        
        permission_record = {
            "username": username,
            "caregiver": caregiver,
            "permissions": permissions,
            "created_at": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO access_permissions (username, caregiver, permissions)
                    VALUES (%s, %s, %s)
                """, (username, caregiver, json.dumps(permissions)))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error setting permissions: {e}")
        
        if "access_permissions" not in st.session_state:
            st.session_state.access_permissions = []
        
        st.session_state.access_permissions.append(permission_record)
        return True
    
    def get_access_permissions(self, username, caregiver):
        """Get access permissions for a caregiver"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT permissions FROM access_permissions
                    WHERE username = %s AND caregiver = %s
                """, (username, caregiver))
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
            except Exception as e:
                print(f"Error fetching permissions: {e}")
        
        return {}
    
    def set_time_based_access(self, username, caregiver, start_time, end_time):
        """Set time-based access restrictions"""
        # Example: Only allow access between 9am-5pm
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO time_based_access (username, caregiver, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                """, (username, caregiver, start_time, end_time))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error setting time-based access: {e}")
        
        return False
    
    def check_access_allowed(self, username, caregiver, resource_type):
        """Check if caregiver can access resource"""
        permissions = self.get_access_permissions(username, caregiver)
        
        if not permissions:
            return False
        
        # Check permission
        if not permissions.get(resource_type, False):
            return False
        
        # Check time-based access
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT start_time, end_time FROM time_based_access
                    WHERE username = %s AND caregiver = %s
                """, (username, caregiver))
                result = cursor.fetchone()
                
                if result:
                    current_time = datetime.now(TIMEZONE).time()
                    start = datetime.strptime(result[0], "%H:%M").time()
                    end = datetime.strptime(result[1], "%H:%M").time()
                    
                    if not (start <= current_time <= end):
                        return False
            except Exception as e:
                pass
        
        return True
    
    def log_access(self, username, caregiver, resource_type, action):
        """Log access to resources"""
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO access_logs (username, caregiver, resource_type, action, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, caregiver, resource_type, action, timestamp))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error logging access: {e}")
        
        if "access_logs" not in st.session_state:
            st.session_state.access_logs = []
        
        st.session_state.access_logs.append({
            "username": username,
            "caregiver": caregiver,
            "resource_type": resource_type,
            "action": action,
            "timestamp": timestamp
        })
    
    def get_access_audit_log(self, username, days=30):
        """Get audit log of who accessed what"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT caregiver, resource_type, action, timestamp FROM access_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY timestamp DESC
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching audit log: {e}")
        
        if "access_logs" not in st.session_state:
            return []
        
        return [l for l in st.session_state.access_logs if l["username"] == username]
    
    def export_user_data(self, username):
        """Export all user data (GDPR compliance)"""
        export_data = {
            "username": username,
            "exported_at": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
            "data": {}
        }
        
        # Collect all user data
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                
                # Messages
                cursor.execute("""
                    SELECT * FROM messages WHERE sender = %s OR receiver = %s
                """, (username, username))
                export_data["data"]["messages"] = cursor.fetchall()
                
                # Vital signs
                cursor.execute("""
                    SELECT * FROM vital_signs WHERE username = %s
                """, (username,))
                export_data["data"]["vital_signs"] = cursor.fetchall()
                
                # Activity logs
                cursor.execute("""
                    SELECT * FROM activity_logs WHERE username = %s
                """, (username,))
                export_data["data"]["activity_logs"] = cursor.fetchall()
                
                # Reminders
                cursor.execute("""
                    SELECT * FROM reminders WHERE username = %s
                """, (username,))
                export_data["data"]["reminders"] = cursor.fetchall()
                
            except Exception as e:
                print(f"Error exporting data: {e}")
        
        return export_data
    
    def delete_user_data(self, username, data_types=None):
        """Delete user data (GDPR right to be forgotten)"""
        if data_types is None:
            data_types = ["messages", "vital_signs", "activity_logs", "reminders", "mood_logs"]
        
        deleted_count = 0
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                
                for data_type in data_types:
                    if data_type == "messages":
                        cursor.execute("""
                            DELETE FROM messages WHERE sender = %s OR receiver = %s
                        """, (username, username))
                    elif data_type == "vital_signs":
                        cursor.execute("""
                            DELETE FROM vital_signs WHERE username = %s
                        """, (username,))
                    elif data_type == "activity_logs":
                        cursor.execute("""
                            DELETE FROM activity_logs WHERE username = %s
                        """, (username,))
                    elif data_type == "reminders":
                        cursor.execute("""
                            DELETE FROM reminders WHERE username = %s
                        """, (username,))
                    elif data_type == "mood_logs":
                        cursor.execute("""
                            DELETE FROM mood_logs WHERE username = %s
                        """, (username,))
                    
                    deleted_count += cursor.rowcount
                
                self.db_conn.commit()
            except Exception as e:
                print(f"Error deleting data: {e}")
        
        return deleted_count
    
    def get_privacy_settings(self, username):
        """Get user's privacy settings"""
        return {
            "data_collection": True,
            "analytics": False,
            "third_party_sharing": False,
            "location_tracking": True,
            "health_data_sharing": False,
            "emergency_override": True
        }
