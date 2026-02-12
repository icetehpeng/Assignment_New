import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE

class CaregiverDashboard:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def get_daily_summary(self, username):
        """Get summary of elderly person's day"""
        summary = {
            "date": datetime.now(TIMEZONE).strftime("%Y-%m-%d"),
            "activities": self._get_activity_count(username),
            "meals": self._get_meal_count(username),
            "water_intake": self._get_water_intake(username),
            "mood": self._get_latest_mood(username),
            "medication_compliance": self._get_medication_compliance(username),
            "falls_detected": self._get_fall_count(username),
            "alerts": self._get_alerts(username)
        }
        return summary
    
    def _get_activity_count(self, username):
        """Count activities today"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM activity_logs
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                return 0
        return 0
    
    def _get_meal_count(self, username):
        """Count meals today"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM meals
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                return 0
        return 0
    
    def _get_water_intake(self, username):
        """Get water intake today"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT SUM(amount_ml) FROM water_logs
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
            except Exception as e:
                return 0
        return 0
    
    def _get_latest_mood(self, username):
        """Get latest mood check-in"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT mood_emoji, mood_text FROM mood_logs
                    WHERE username = %s ORDER BY timestamp DESC LIMIT 1
                """, (username,))
                result = cursor.fetchone()
                return {"emoji": result[0], "text": result[1]} if result else None
            except Exception as e:
                return None
        return None
    
    def _get_medication_compliance(self, username):
        """Get medication compliance percentage"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM medication_logs
                    WHERE username = %s AND DATE(taken_at) = CURDATE()
                """, (username,))
                taken = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM medications
                    WHERE username = %s AND start_date <= CURDATE()
                    AND (end_date IS NULL OR end_date >= CURDATE())
                """, (username,))
                expected = cursor.fetchone()[0]
                
                return (taken / expected * 100) if expected > 0 else 0
            except Exception as e:
                return 0
        return 0
    
    def _get_fall_count(self, username):
        """Count falls detected today"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM sos_logs
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                return 0
        return 0
    
    def _get_alerts(self, username):
        """Get active alerts"""
        alerts = []
        
        # Check for abnormal vitals
        from vital_signs import VitalSignsTracker
        vital_tracker = VitalSignsTracker(self.db_conn, self.db_available)
        abnormal = vital_tracker.check_abnormal_readings(username)
        alerts.extend([{"type": "vital", "message": f"Abnormal {a['vital']}: {a['value']}"} for a in abnormal])
        
        # Check for inactivity
        from activity_recognition import ActivityRecognition
        activity = ActivityRecognition(self.db_conn, self.db_available)
        inactivity = activity.detect_unusual_inactivity(username)
        if inactivity.get("inactive"):
            alerts.append({"type": "activity", "message": inactivity.get("alert", "Unusual inactivity")})
        
        # Check for medication refills
        from medication_manager import MedicationManager
        med_manager = MedicationManager(self.db_conn, self.db_available)
        refills = med_manager.check_refill_needed(username)
        alerts.extend([{"type": "medication", "message": f"Refill needed: {r['medication']}"} for r in refills])
        
        return alerts
    
    def get_health_trends(self, username, days=30):
        """Get health trends over time"""
        trends = {
            "vital_signs_trend": self._get_vital_trends(username, days),
            "activity_trend": self._get_activity_trend(username, days),
            "mood_trend": self._get_mood_trend(username, days),
            "medication_compliance_trend": self._get_compliance_trend(username, days)
        }
        return trends
    
    def _get_vital_trends(self, username, days):
        """Get vital signs trend"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT DATE(timestamp), AVG(value) FROM vital_signs
                    WHERE username = %s AND vital_type = 'heart_rate'
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp)
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                return []
        return []
    
    def _get_activity_trend(self, username, days):
        """Get activity trend"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT DATE(timestamp), COUNT(*) FROM activity_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp)
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                return []
        return []
    
    def _get_mood_trend(self, username, days):
        """Get mood trend"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT DATE(timestamp), mood_emoji FROM mood_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY DATE(timestamp)
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                return []
        return []
    
    def _get_compliance_trend(self, username, days):
        """Get medication compliance trend"""
        trend = []
        for i in range(days, 0, -1):
            date = (datetime.now(TIMEZONE) - timedelta(days=i)).date()
            # Calculate compliance for that day
            if self.db_available:
                try:
                    cursor = self.db_conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM medication_logs
                        WHERE username = %s AND DATE(taken_at) = %s
                    """, (username, date))
                    taken = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM medications
                        WHERE username = %s AND start_date <= %s
                        AND (end_date IS NULL OR end_date >= %s)
                    """, (username, date, date))
                    expected = cursor.fetchone()[0]
                    
                    compliance = (taken / expected * 100) if expected > 0 else 0
                    trend.append((date, compliance))
                except Exception as e:
                    pass
        
        return trend
    
    def generate_incident_report(self, username, start_date, end_date):
        """Generate incident report for date range"""
        report = {
            "username": username,
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
            "incidents": []
        }
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT timestamp, location_lat, location_lon FROM sos_logs
                    WHERE username = %s AND DATE(timestamp) BETWEEN %s AND %s
                    ORDER BY timestamp DESC
                """, (username, start_date, end_date))
                
                incidents = cursor.fetchall()
                for incident in incidents:
                    report["incidents"].append({
                        "type": "Fall/SOS",
                        "timestamp": incident[0],
                        "location": f"{incident[1]}, {incident[2]}" if incident[1] else "Unknown"
                    })
            except Exception as e:
                pass
        
        return report
