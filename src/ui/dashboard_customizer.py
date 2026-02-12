"""
Customizable dashboard system - allows users to choose widgets and layout
"""
from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

class DashboardCustomizer:
    def __init__(self, db_conn=None, db_available=False):
        """Initialize dashboard customizer"""
        self.db_conn = db_conn
        self.db_available = db_available
        
        self.available_widgets = {
            "vital_signs": {
                "name": "❤️ Vital Signs",
                "description": "Display latest vital signs",
                "category": "health",
                "default": True
            },
            "medications": {
                "name": "💊 Medications",
                "description": "Show active medications and compliance",
                "category": "health",
                "default": True
            },
            "activity": {
                "name": "🚶 Activity",
                "description": "Display activity summary",
                "category": "lifestyle",
                "default": True
            },
            "nutrition": {
                "name": "🍽️ Nutrition",
                "description": "Show nutrition and water intake",
                "category": "lifestyle",
                "default": True
            },
            "mood": {
                "name": "😊 Mood",
                "description": "Display mood trends",
                "category": "mental",
                "default": True
            },
            "reminders": {
                "name": "⏰ Reminders",
                "description": "Show active reminders",
                "category": "alerts",
                "default": True
            },
            "emergency_contacts": {
                "name": "🚨 Emergency",
                "description": "Quick access to emergency contacts",
                "category": "safety",
                "default": False
            },
            "geofencing": {
                "name": "📍 Location",
                "description": "Show safe zones and location status",
                "category": "safety",
                "default": False
            },
            "smart_home": {
                "name": "🏠 Smart Home",
                "description": "Display smart home device status",
                "category": "home",
                "default": False
            },
            "motion_analytics": {
                "name": "📈 Motion",
                "description": "Show motion activity chart",
                "category": "analytics",
                "default": True
            },
            "health_trends": {
                "name": "📊 Trends",
                "description": "Display health trends over time",
                "category": "analytics",
                "default": False
            },
            "incidents": {
                "name": "🚨 Incidents",
                "description": "Show incident snapshot gallery",
                "category": "safety",
                "default": True
            }
        }
    
    def get_default_layout(self) -> List[str]:
        """Get default widget layout"""
        return [
            widget_id for widget_id, config in self.available_widgets.items()
            if config["default"]
        ]
    
    def get_user_layout(self, username: str) -> List[str]:
        """Get user's custom dashboard layout"""
        if self.db_available and self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT dashboard_layout FROM user_preferences WHERE username=%s
                """, (username,))
                result = cursor.fetchone()
                if result and result[0]:
                    return json.loads(result[0])
            except Exception as e:
                logger.error(f"Error loading dashboard layout: {e}")
        
        return self.get_default_layout()
    
    def save_user_layout(self, username: str, widget_ids: List[str]) -> bool:
        """Save user's custom dashboard layout"""
        if self.db_available and self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                layout_json = json.dumps(widget_ids)
                cursor.execute("""
                    INSERT INTO user_preferences (username, dashboard_layout, updated_at)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE dashboard_layout=%s, updated_at=NOW()
                """, (username, layout_json, layout_json))
                self.db_conn.commit()
                logger.info(f"Dashboard layout saved for {username}")
                return True
            except Exception as e:
                logger.error(f"Error saving dashboard layout: {e}")
        return False
    
    def get_available_widgets(self) -> Dict:
        """Get all available widgets"""
        return self.available_widgets
    
    def get_widgets_by_category(self, category: str) -> Dict:
        """Get widgets filtered by category"""
        return {
            widget_id: config for widget_id, config in self.available_widgets.items()
            if config["category"] == category
        }
    
    def reorder_widgets(self, username: str, widget_ids: List[str]) -> bool:
        """Reorder widgets in dashboard"""
        # Validate all widget IDs exist
        if not all(wid in self.available_widgets for wid in widget_ids):
            logger.error("Invalid widget IDs provided")
            return False
        
        return self.save_user_layout(username, widget_ids)
    
    def toggle_widget(self, username: str, widget_id: str, enabled: bool) -> bool:
        """Enable/disable a widget"""
        current_layout = self.get_user_layout(username)
        
        if enabled and widget_id not in current_layout:
            current_layout.append(widget_id)
        elif not enabled and widget_id in current_layout:
            current_layout.remove(widget_id)
        
        return self.save_user_layout(username, current_layout)
    
    def reset_to_default(self, username: str) -> bool:
        """Reset dashboard to default layout"""
        return self.save_user_layout(username, self.get_default_layout())
