"""
Theme management system with dark/light mode toggle and customization
"""
import streamlit as st
from typing import Dict, Optional
import json
from pathlib import Path

class ThemeManager:
    def __init__(self):
        """Initialize theme manager"""
        self.themes = {
            "dark": {
                "bg_primary": "#0B0E14",
                "bg_secondary": "#0F131A",
                "text_primary": "#E0E6ED",
                "text_secondary": "#A0A6AD",
                "accent_blue": "#0078FF",
                "accent_glow": "#00D1FF",
                "alert_orange": "#FF5E00",
                "glass_bg": "rgba(255, 255, 255, 0.05)",
                "glass_border": "rgba(255, 255, 255, 0.1)",
            },
            "light": {
                "bg_primary": "#FFFFFF",
                "bg_secondary": "#F5F5F5",
                "text_primary": "#1A1A1A",
                "text_secondary": "#666666",
                "accent_blue": "#0056B3",
                "accent_glow": "#0078FF",
                "alert_orange": "#FF5E00",
                "glass_bg": "rgba(0, 0, 0, 0.05)",
                "glass_border": "rgba(0, 0, 0, 0.1)",
            },
            "high_contrast": {
                "bg_primary": "#000000",
                "bg_secondary": "#1A1A1A",
                "text_primary": "#FFFFFF",
                "text_secondary": "#CCCCCC",
                "accent_blue": "#00FFFF",
                "accent_glow": "#00FF00",
                "alert_orange": "#FFFF00",
                "glass_bg": "rgba(255, 255, 255, 0.1)",
                "glass_border": "rgba(255, 255, 255, 0.3)",
            },
            "warm": {
                "bg_primary": "#FFF8F0",
                "bg_secondary": "#FFE8D6",
                "text_primary": "#3D2817",
                "text_secondary": "#6B4423",
                "accent_blue": "#D97706",
                "accent_glow": "#F59E0B",
                "alert_orange": "#DC2626",
                "glass_bg": "rgba(217, 119, 6, 0.05)",
                "glass_border": "rgba(217, 119, 6, 0.1)",
            }
        }
    
    def get_theme(self, theme_name: str) -> Dict[str, str]:
        """Get theme colors"""
        return self.themes.get(theme_name, self.themes["dark"])
    
    def apply_theme(self, theme_name: str) -> str:
        """Apply theme and return CSS"""
        theme = self.get_theme(theme_name)
        
        css = f"""
        <style>
        :root {{
            --bg-primary: {theme['bg_primary']};
            --bg-secondary: {theme['bg_secondary']};
            --text-primary: {theme['text_primary']};
            --text-secondary: {theme['text_secondary']};
            --accent-blue: {theme['accent_blue']};
            --accent-glow: {theme['accent_glow']};
            --alert-orange: {theme['alert_orange']};
            --glass-bg: {theme['glass_bg']};
            --glass-border: {theme['glass_border']};
        }}
        
        .stApp {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }}
        
        [data-testid="stMetric"] {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            padding: 15px !important;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: var(--bg-secondary) !important;
            border-right: 1px solid var(--glass-border);
        }}
        
        .stButton > button {{
            background-color: var(--accent-blue) !important;
            color: white !important;
        }}
        
        .stTextInput > div > div > input {{
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--glass-border) !important;
        }}
        
        .stSelectbox > div > div > select {{
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--glass-border) !important;
        }}
        </style>
        """
        return css
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return list(self.themes.keys())
    
    def save_user_theme(self, username: str, theme_name: str, db_conn=None):
        """Save user's theme preference"""
        if db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (username, theme, updated_at)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE theme=%s, updated_at=NOW()
                """, (username, theme_name, theme_name))
                db_conn.commit()
            except Exception as e:
                print(f"Error saving theme preference: {e}")
    
    def load_user_theme(self, username: str, db_conn=None) -> str:
        """Load user's saved theme preference"""
        if db_conn:
            try:
                cursor = db_conn.cursor()
                cursor.execute("SELECT theme FROM user_preferences WHERE username=%s", (username,))
                result = cursor.fetchone()
                if result:
                    return result[0]
            except Exception as e:
                print(f"Error loading theme preference: {e}")
        return "dark"  # Default theme
