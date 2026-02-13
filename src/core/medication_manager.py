import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE

class MedicationManager:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def add_medication(self, username, name, dosage, frequency, start_date, end_date=None, notes=""):
        """Add a medication to track"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO medications (username, name, dosage, frequency, start_date, end_date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (username, name, dosage, frequency, start_date, end_date, notes))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error adding medication: {e}")
        
        if "medications" not in st.session_state:
            st.session_state.medications = []
        
        st.session_state.medications.append({
            "username": username,
            "name": name,
            "dosage": dosage,
            "frequency": frequency,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes
        })
        return True
    
    def log_medication_taken(self, username, medication_name, timestamp=None):
        """Log that medication was taken"""
        if timestamp is None:
            timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO medication_logs (username, medication_name, taken_at)
                    VALUES (%s, %s, %s)
                """, (username, medication_name, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging medication: {e}")
        
        if "medication_logs" not in st.session_state:
            st.session_state.medication_logs = []
        
        st.session_state.medication_logs.append({
            "username": username,
            "medication_name": medication_name,
            "taken_at": timestamp
        })
        return True
    
    def get_active_medications(self, username):
        """Get currently active medications"""
        today = datetime.now(TIMEZONE).date()
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT name, dosage, frequency, start_date, end_date, notes FROM medications
                    WHERE username = %s AND start_date <= %s
                    AND (end_date IS NULL OR end_date >= %s)
                """, (username, today, today))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching medications: {e}")
        
        if "medications" not in st.session_state:
            return []
        
        return [m for m in st.session_state.medications if m["username"] == username]
    
    def get_medication_compliance(self, username, days=7):
        """Calculate medication compliance rate"""
        medications = self.get_active_medications(username)
        
        if not medications:
            return 0
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM medication_logs
                    WHERE username = %s AND taken_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """, (username, days))
                taken = cursor.fetchone()[0]
            except Exception as e:
                taken = 0
        else:
            if "medication_logs" not in st.session_state:
                taken = 0
            else:
                taken = len([m for m in st.session_state.medication_logs if m["username"] == username])
        
        expected = len(medications) * days
        return (taken / expected * 100) if expected > 0 else 0
    
    def check_refill_needed(self, username):
        """Check which medications need refilling"""
        medications = self.get_active_medications(username)
        refill_alerts = []
        
        for med in medications:
            # Simple logic: if end_date is within 7 days, flag for refill
            if med[4]:  # end_date
                days_until_end = (med[4] - datetime.now(TIMEZONE).date()).days
                if 0 <= days_until_end <= 7:
                    refill_alerts.append({
                        "medication": med[0],
                        "dosage": med[1],
                        "days_left": days_until_end
                    })
        
        return refill_alerts
    
    def check_drug_interactions(self, medications_list):
        """Check for potential drug interactions"""
        # Simplified interaction database
        interactions = {
            ("aspirin", "ibuprofen"): "High - Both are NSAIDs, risk of GI bleeding",
            ("warfarin", "aspirin"): "High - Increased bleeding risk",
            ("metformin", "alcohol"): "Moderate - Risk of lactic acidosis",
        }
        
        alerts = []
        med_names = [m.lower() for m in medications_list]
        
        for (drug1, drug2), risk in interactions.items():
            if drug1 in med_names and drug2 in med_names:
                alerts.append({
                    "drugs": f"{drug1} + {drug2}",
                    "risk": risk
                })
        
        return alerts
