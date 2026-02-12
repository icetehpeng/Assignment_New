import streamlit as st

class AccessibilityManager:
    def __init__(self):
        self.themes = {
            "default": {
                "font_size": 16,
                "contrast": "normal",
                "colors": {"bg": "#ffffff", "text": "#000000"}
            },
            "large_text": {
                "font_size": 24,
                "contrast": "normal",
                "colors": {"bg": "#ffffff", "text": "#000000"}
            },
            "high_contrast": {
                "font_size": 16,
                "contrast": "high",
                "colors": {"bg": "#000000", "text": "#ffff00"}
            },
            "high_contrast_large": {
                "font_size": 24,
                "contrast": "high",
                "colors": {"bg": "#000000", "text": "#ffff00"}
            },
            "dark_mode": {
                "font_size": 16,
                "contrast": "normal",
                "colors": {"bg": "#1a1a1a", "text": "#ffffff"}
            }
        }
    
    def get_theme(self, theme_name):
        """Get theme configuration"""
        return self.themes.get(theme_name, self.themes["default"])
    
    def apply_theme(self, theme_name):
        """Apply theme to session state"""
        theme = self.get_theme(theme_name)
        st.session_state.accessibility_theme = theme
        st.session_state.font_size = theme["font_size"]
        st.session_state.contrast = theme["contrast"]
        return theme
    
    def get_css_for_theme(self, theme):
        """Generate CSS for theme"""
        css = f"""
        <style>
            body {{
                font-size: {theme['font_size']}px;
                background-color: {theme['colors']['bg']};
                color: {theme['colors']['text']};
            }}
            
            .stButton > button {{
                font-size: {theme['font_size']}px;
                padding: 15px 30px;
            }}
            
            .stTextInput > div > div > input {{
                font-size: {theme['font_size']}px;
            }}
            
            .stSelectbox > div > div > select {{
                font-size: {theme['font_size']}px;
            }}
            
            h1, h2, h3 {{
                font-size: {int(theme['font_size'] * 1.5)}px;
            }}
        </style>
        """
        return css
    
    def get_simplified_ui_config(self):
        """Get configuration for simplified UI"""
        return {
            "show_advanced_options": False,
            "show_only_essential_buttons": True,
            "large_buttons": True,
            "simple_navigation": True,
            "reduced_animations": True
        }
    
    def enable_text_to_speech(self, text, language="en"):
        """Enable text-to-speech for accessibility"""
        # Placeholder for TTS implementation
        return {
            "status": "enabled",
            "text": text,
            "language": language
        }
    
    def get_keyboard_shortcuts(self):
        """Get keyboard shortcuts for accessibility"""
        shortcuts = {
            "Alt+H": "Go to Home",
            "Alt+C": "Open Camera",
            "Alt+M": "Open Messages",
            "Alt+R": "Open Reminders",
            "Alt+S": "Trigger SOS",
            "Alt+?": "Show Help",
            "Tab": "Navigate between elements",
            "Enter": "Activate button/link",
            "Space": "Toggle checkbox"
        }
        return shortcuts
    
    def enable_screen_reader_support(self):
        """Enable screen reader support"""
        return {
            "aria_labels": True,
            "semantic_html": True,
            "focus_indicators": True,
            "skip_links": True
        }
    
    def get_color_blind_friendly_palette(self):
        """Get color-blind friendly color palette"""
        return {
            "primary": "#0173B2",      # Blue
            "secondary": "#DE8F05",    # Orange
            "success": "#029E73",      # Green
            "danger": "#CC78BC",       # Purple
            "warning": "#CA9161",      # Brown
            "info": "#56B4E9"          # Light Blue
        }
    
    def enable_dyslexia_friendly_font(self):
        """Enable dyslexia-friendly font"""
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=OpenDyslexic:wght@400;700&display=swap');
            
            body, .stApp {{
                font-family: 'OpenDyslexic', sans-serif;
                letter-spacing: 0.05em;
                line-height: 1.8;
            }}
        </style>
        """
        return css
