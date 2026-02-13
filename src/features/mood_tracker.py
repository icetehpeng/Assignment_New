import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE

class MoodTracker:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
    
    def log_mood(self, username, mood_emoji, mood_text, notes="", timestamp=None):
        """Log daily mood check-in"""
        if timestamp is None:
            timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO mood_logs (username, mood_emoji, mood_text, notes, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, mood_emoji, mood_text, notes, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging mood: {e}")
        
        if "mood_logs" not in st.session_state:
            st.session_state.mood_logs = []
        
        st.session_state.mood_logs.append({
            "username": username,
            "mood_emoji": mood_emoji,
            "mood_text": mood_text,
            "notes": notes,
            "timestamp": timestamp
        })
        return True
    
    def get_mood_history(self, username, days=30):
        """Get mood history"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT mood_emoji, mood_text, notes, timestamp FROM mood_logs
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY timestamp DESC
                """, (username, days))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching mood history: {e}")
        
        if "mood_logs" not in st.session_state:
            return []
        
        return [m for m in st.session_state.mood_logs if m["username"] == username]
    
    def get_mood_trends(self, username, days=30):
        """Analyze mood trends"""
        mood_mapping = {
            "😄": 5,  # Very happy
            "😊": 4,  # Happy
            "😐": 3,  # Neutral
            "😔": 2,  # Sad
            "😢": 1   # Very sad
        }
        
        history = self.get_mood_history(username, days)
        
        if not history:
            return {"trend": "No data", "average_mood": 0}
        
        scores = []
        for mood in history:
            emoji = mood[0] if isinstance(mood, tuple) else mood.get("mood_emoji", "😐")
            score = mood_mapping.get(emoji, 3)
            scores.append(score)
        
        average = sum(scores) / len(scores) if scores else 0
        
        # Determine trend
        if len(scores) >= 7:
            recent_avg = sum(scores[:7]) / 7
            older_avg = sum(scores[7:]) / len(scores[7:])
            
            if recent_avg > older_avg + 0.5:
                trend = "📈 Improving"
            elif recent_avg < older_avg - 0.5:
                trend = "📉 Declining"
            else:
                trend = "➡️ Stable"
        else:
            trend = "Insufficient data"
        
        return {
            "trend": trend,
            "average_mood": round(average, 1),
            "mood_scores": scores
        }
    
    def run_depression_screening(self, username, responses):
        """Run PHQ-9 depression screening questionnaire"""
        # PHQ-9 scoring: 0-4 minimal, 5-9 mild, 10-14 moderate, 15-19 moderately severe, 20+ severe
        
        if len(responses) != 9:
            return {"error": "Need 9 responses"}
        
        total_score = sum(responses)
        
        severity_levels = {
            (0, 4): ("Minimal", "No depression symptoms"),
            (5, 9): ("Mild", "Monitor and consider lifestyle changes"),
            (10, 14): ("Moderate", "Consider professional consultation"),
            (15, 19): ("Moderately Severe", "Recommend professional help"),
            (20, 27): ("Severe", "Urgent professional consultation recommended")
        }
        
        severity = "Unknown"
        recommendation = ""
        
        for (min_score, max_score), (level, rec) in severity_levels.items():
            if min_score <= total_score <= max_score:
                severity = level
                recommendation = rec
                break
        
        # Log screening result
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO depression_screenings (username, phq9_score, severity, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (username, total_score, severity, timestamp))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error logging screening: {e}")
        
        if "depression_screenings" not in st.session_state:
            st.session_state.depression_screenings = []
        
        st.session_state.depression_screenings.append({
            "username": username,
            "phq9_score": total_score,
            "severity": severity,
            "timestamp": timestamp
        })
        
        return {
            "score": total_score,
            "severity": severity,
            "recommendation": recommendation,
            "timestamp": timestamp
        }
    
    def get_cognitive_games(self):
        """Get list of cognitive games/puzzles"""
        games = [
            {
                "name": "Memory Match",
                "description": "Match pairs of cards",
                "difficulty": "Easy",
                "duration_minutes": 5
            },
            {
                "name": "Word Search",
                "description": "Find hidden words in grid",
                "difficulty": "Medium",
                "duration_minutes": 10
            },
            {
                "name": "Sudoku",
                "description": "Number puzzle game",
                "difficulty": "Hard",
                "duration_minutes": 15
            },
            {
                "name": "Trivia Quiz",
                "description": "Answer general knowledge questions",
                "difficulty": "Medium",
                "duration_minutes": 10
            },
            {
                "name": "Pattern Recognition",
                "description": "Identify patterns in sequences",
                "difficulty": "Medium",
                "duration_minutes": 8
            }
        ]
        return games
    
    def log_cognitive_activity(self, username, game_name, score, duration_minutes):
        """Log cognitive game activity"""
        timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO cognitive_activities (username, game_name, score, duration_minutes, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, game_name, score, duration_minutes, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging cognitive activity: {e}")
        
        if "cognitive_activities" not in st.session_state:
            st.session_state.cognitive_activities = []
        
        st.session_state.cognitive_activities.append({
            "username": username,
            "game_name": game_name,
            "score": score,
            "duration_minutes": duration_minutes,
            "timestamp": timestamp
        })
        return True
