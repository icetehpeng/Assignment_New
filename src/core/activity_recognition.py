import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE

class ActivityRecognition:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def log_activity(self, username, activity_type, duration_minutes, timestamp=None):
        """Log an activity"""
        if timestamp is None:
            timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO activity_logs (username, activity_type, duration_minutes, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (username, activity_type, duration_minutes, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging activity: {e}")
        
        if "activity_logs" not in st.session_state:
            st.session_state.activity_logs = []
        
        st.session_state.activity_logs.append({
            "username": username,
            "activity_type": activity_type,
            "duration_minutes": duration_minutes,
            "timestamp": timestamp
        })
        return True
    
    def detect_unusual_inactivity(self, username, hours=4):
        """Detect if person has been inactive for too long"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT MAX(timestamp) FROM activity_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                """, (username, hours))
                result = cursor.fetchone()
                last_activity = result[0] if result and result[0] else None
            except Exception as e:
                last_activity = None
        else:
            if "activity_logs" not in st.session_state:
                return {"inactive": True, "hours": hours}
            
            activities = [a for a in st.session_state.activity_logs if a["username"] == username]
            if not activities:
                return {"inactive": True, "hours": hours}
            
            last_activity = activities[-1]["timestamp"]
        
        if last_activity is None:
            return {"inactive": True, "hours": hours, "alert": "No recent activity detected"}
        
        # Calculate time difference
        now = datetime.now(TIMEZONE)
        last_time = datetime.fromisoformat(str(last_activity).replace('Z', '+00:00'))
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=TIMEZONE)
        
        time_diff = (now - last_time).total_seconds() / 3600
        
        if time_diff > hours:
            return {
                "inactive": True,
                "hours_inactive": round(time_diff, 1),
                "alert": f"Person has been inactive for {round(time_diff, 1)} hours"
            }
        
        return {"inactive": False, "hours_inactive": round(time_diff, 1)}
    
    def detect_excessive_sleep(self, username, hours=12):
        """Detect if person is sleeping too much"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT SUM(duration_minutes) FROM activity_logs
                    WHERE username = %s AND activity_type = 'sleep'
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY)
                """, (username,))
                result = cursor.fetchone()
                total_sleep = result[0] if result and result[0] else 0
            except Exception as e:
                total_sleep = 0
        else:
            if "activity_logs" not in st.session_state:
                total_sleep = 0
            else:
                activities = [a for a in st.session_state.activity_logs 
                            if a["username"] == username and a["activity_type"] == "sleep"]
                total_sleep = sum(a["duration_minutes"] for a in activities)
        
        sleep_hours = total_sleep / 60
        
        if sleep_hours > hours:
            return {
                "excessive": True,
                "sleep_hours": round(sleep_hours, 1),
                "alert": f"Excessive sleep detected: {round(sleep_hours, 1)} hours"
            }
        
        return {"excessive": False, "sleep_hours": round(sleep_hours, 1)}
    
    def get_activity_summary(self, username, days=7):
        """Get activity summary for a period"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT activity_type, COUNT(*), SUM(duration_minutes) FROM activity_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY activity_type
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching activity summary: {e}")
        
        if "activity_logs" not in st.session_state:
            return []
        
        activities = [a for a in st.session_state.activity_logs if a["username"] == username]
        
        summary = {}
        for activity in activities:
            activity_type = activity["activity_type"]
            if activity_type not in summary:
                summary[activity_type] = {"count": 0, "total_minutes": 0}
            summary[activity_type]["count"] += 1
            summary[activity_type]["total_minutes"] += activity["duration_minutes"]
        
        return [(k, v["count"], v["total_minutes"]) for k, v in summary.items()]
    
    def detect_movement_pattern_anomaly(self, username):
        """Detect unusual movement patterns"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                # Get hourly movement counts for today
                cursor.execute("""
                    SELECT HOUR(timestamp), COUNT(*) FROM activity_logs
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                    GROUP BY HOUR(timestamp)
                """, (username,))
                today_pattern = cursor.fetchall()
                
                # Get average hourly pattern for past 7 days
                cursor.execute("""
                    SELECT HOUR(timestamp), AVG(COUNT(*)) FROM activity_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    GROUP BY HOUR(timestamp)
                """, (username,))
                avg_pattern = cursor.fetchall()
            except Exception as e:
                return {"anomaly": False}
        else:
            return {"anomaly": False}
        
        # Simple anomaly detection: if today's pattern differs significantly from average
        anomalies = []
        for hour, count in today_pattern:
            avg = next((p[1] for p in avg_pattern if p[0] == hour), 0)
            if avg > 0 and count < avg * 0.5:  # Less than 50% of average
                anomalies.append({
                    "hour": hour,
                    "expected": avg,
                    "actual": count
                })
        
        return {
            "anomaly": len(anomalies) > 0,
            "anomalies": anomalies
        }
