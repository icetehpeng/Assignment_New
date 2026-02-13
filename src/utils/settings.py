"""
Unified Settings Manager
Combines all settings-related features into a single module
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from typing import Dict, Optional
import logging
from config import TIMEZONE

logger = logging.getLogger(__name__)

class SettingsManager:
    """Unified settings manager for all application settings"""
    
    def __init__(self, db_conn=None, db_available=False, 
                 theme_mgr=None, language_mgr=None, 
                 accessibility=None, sync_mgr=None,
                 error_logger=None, audio_system=None):
        """Initialize settings manager with all dependencies"""
        self.db_conn = db_conn
        self.db_available = db_available
        self.theme_mgr = theme_mgr
        self.language_mgr = language_mgr
        self.accessibility = accessibility
        self.sync_mgr = sync_mgr
        self.error_logger = error_logger
        self.audio_system = audio_system
    
    def render_settings_page(self, current_user: str, timezone=None, 
                            video_processor=None, reminder_system=None,
                            cache=None, start_time=None):
        """Render the complete settings page with all tabs"""
        
        st.markdown("<h2 style='color:#00D1FF;'>⚙️ SETTINGS & PREFERENCES</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🎨 Appearance",
            "🌍 Language",
            "♿ Accessibility",
            "📡 Offline",
            "🔧 System",
            "📊 Monitoring"
        ])
        
        # TAB 1: APPEARANCE
        with tab1:
            self._render_appearance_tab(current_user)
        
        # TAB 2: LANGUAGE
        with tab2:
            self._render_language_tab(current_user)
        
        # TAB 3: ACCESSIBILITY
        with tab3:
            self._render_accessibility_tab()
        
        # TAB 4: OFFLINE
        with tab4:
            self._render_offline_tab()
        
        # TAB 5: SYSTEM
        with tab5:
            self._render_system_tab(current_user, timezone, video_processor, 
                                   reminder_system, start_time)
        
        # TAB 6: MONITORING
        with tab6:
            self._render_monitoring_tab()
    
    def _render_appearance_tab(self, current_user: str):
        """Render appearance/theme settings tab"""
        st.subheader("🎨 Theme Selection")
        
        if not self.theme_mgr:
            st.error("Theme manager not initialized")
            return
        
        themes = self.theme_mgr.get_available_themes()
        current_theme = self.theme_mgr.load_user_theme(current_user, self.db_conn)
        
        selected_theme = st.selectbox(
            "Select Theme",
            themes,
            index=themes.index(current_theme) if current_theme in themes else 0,
            key="settings_theme_select"
        )
        
        # Show theme preview
        st.markdown("---")
        st.write("**Theme Preview:**")
        theme_colors = self.theme_mgr.get_theme(selected_theme)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"<div style='background-color: {theme_colors['bg_primary']}; padding: 20px; border-radius: 8px; border: 2px solid {theme_colors['accent_blue']};'><span style='color: {theme_colors['text_primary']}'>Primary</span></div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div style='background-color: {theme_colors['accent_blue']}; padding: 20px; border-radius: 8px;'><span style='color: white'>Accent</span></div>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<div style='background-color: {theme_colors['accent_glow']}; padding: 20px; border-radius: 8px;'><span style='color: black'>Glow</span></div>",
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(
                f"<div style='background-color: {theme_colors['alert_orange']}; padding: 20px; border-radius: 8px;'><span style='color: white'>Alert</span></div>",
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Apply Theme", use_container_width=True, type="primary", key="settings_apply_theme"):
                self.theme_mgr.save_user_theme(current_user, selected_theme, self.db_conn)
                st.session_state.current_theme = selected_theme
                st.success(f"✅ Theme changed to {selected_theme}!")
                st.rerun()
        
        with col2:
            st.write("")  # Spacer
        
        st.markdown("---")
        st.write("**Available Themes:**")
        st.write("- 🌙 **Dark** - Original dark theme (default)")
        st.write("- ☀️ **Light** - Light theme for daytime use")
        st.write("- 🔆 **High Contrast** - For accessibility")
        st.write("- 🔥 **Warm** - Warm colors for elderly users")
    
    def _render_language_tab(self, current_user: str):
        """Render language settings tab"""
        st.subheader("🌍 Language Preferences")
        
        if not self.language_mgr:
            st.error("Language manager not initialized")
            return
        
        languages = self.language_mgr.get_supported_languages()
        current_lang = self.language_mgr.load_language_preference(current_user, self.db_conn)
        
        lang_names = list(languages.values())
        current_lang_name = languages.get(current_lang, "English")
        
        selected_lang_name = st.selectbox(
            "Select Language",
            lang_names,
            index=lang_names.index(current_lang_name) if current_lang_name in lang_names else 0,
            key="settings_lang_select"
        )
        
        lang_code = [k for k, v in languages.items() if v == selected_lang_name][0]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Apply Language", use_container_width=True, type="primary", key="settings_apply_lang"):
                self.language_mgr.save_language_preference(current_user, lang_code, self.db_conn)
                st.session_state.current_language = lang_code
                st.success(f"✅ Language changed to {selected_lang_name}!")
                st.rerun()
        
        with col2:
            st.write("")  # Spacer
        
        st.markdown("---")
        st.write("**Supported Languages:**")
        for code, name in languages.items():
            st.write(f"- {name}")
    
    def _render_accessibility_tab(self):
        """Render accessibility settings tab"""
        st.subheader("♿ Accessibility Options")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Text Size**")
            text_size = st.select_slider(
                "Adjust text size",
                options=["Small", "Normal", "Large", "Extra Large"],
                value="Normal",
                key="settings_text_size"
            )
            st.caption(f"Current: {text_size}")
        
        with col2:
            st.write("**Display Options**")
            high_contrast = st.checkbox("High Contrast Mode", value=False, key="settings_high_contrast")
            reduce_motion = st.checkbox("Reduce Motion", value=False, key="settings_reduce_motion")
        
        st.markdown("---")
        st.subheader("⌨️ Keyboard Shortcuts")
        
        if self.accessibility:
            shortcuts = self.accessibility.get_keyboard_shortcuts()
            for shortcut, action in shortcuts.items():
                st.write(f"**{shortcut}**: {action}")
        
        st.markdown("---")
        st.subheader("🔊 Audio Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            volume = st.slider("Volume Level", 0, 100, 80, key="settings_volume")
        with col2:
            enable_audio_feedback = st.checkbox("Audio Feedback", value=True, key="settings_audio_feedback")
        
        if st.button("🔊 Test Audio", use_container_width=True, key="settings_test_audio"):
            if self.audio_system:
                beep = self.audio_system.generate_beep(frequency=440, duration=1.0)
                if beep:
                    self.audio_system.play_audio(beep)
                    st.success("✅ Audio test played!")
    
    def _render_offline_tab(self):
        """Render offline mode and sync settings tab"""
        st.subheader("📡 Offline Mode & Sync")
        
        if not self.sync_mgr:
            st.error("Sync manager not initialized")
            return
        
        status = self.sync_mgr.get_sync_status()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pending Sync", status["pending"], delta=None)
        with col2:
            st.metric("Synced", status["synced"], delta=None)
        with col3:
            st.metric("Cached", status["cached"], delta=None)
        with col4:
            st.metric("Total Queued", status["total_queued"], delta=None)
        
        st.markdown("---")
        st.subheader("🔄 Sync Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Sync Now", use_container_width=True, type="primary", key="settings_sync_now"):
                with st.spinner("Syncing..."):
                    result = self.sync_mgr.sync_to_server(self.db_conn, self.db_available)
                    st.success(f"✅ Synced: {result['synced']}, Failed: {result['failed']}")
        
        with col2:
            if st.button("🗑️ Clear Old Cache", use_container_width=True, key="settings_clear_cache"):
                cleared = self.sync_mgr.clear_old_cache(days=7)
                st.info(f"Cleared {cleared} old cache entries")
        
        st.markdown("---")
        st.subheader("📊 Offline Status")
        
        if self.db_available:
            st.success("🟢 **ONLINE** - Connected to database")
        else:
            st.warning("🔴 **OFFLINE** - Using local cache")
        
        st.write(f"**Last Sync:** {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_system_tab(self, current_user: str, timezone=None, 
                          video_processor=None, reminder_system=None, start_time=None):
        """Render system settings tab"""
        st.subheader("🔧 System Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Force Reconnect Database", use_container_width=True, key="settings_db_reconnect"):
                st.cache_resource.clear()
                st.success("✅ Cache cleared. Reconnecting...")
                st.rerun()
        
        with col2:
            if st.button("🛠️ Create Tables Automatically", use_container_width=True, key="settings_create_tables"):
                if self.db_available:
                    from database import create_tables
                    success, msg = create_tables(self.db_conn)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Database not available")
        
        st.markdown("---")
        st.subheader("📋 Application Info")
        
        st.write(f"**User:** {current_user}")
        if start_time:
            st.write(f"**Session Start:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Database:** {'🟢 Connected' if self.db_available else '🔴 Offline'}")
        
        st.markdown("---")
        st.subheader("🔐 Security")
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary", key="settings_logout"):
            if reminder_system:
                reminder_system.stop()
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()
    
    def _render_monitoring_tab(self):
        """Render error monitoring and system health tab"""
        st.subheader("📊 Error Monitoring")
        
        if st.button("📋 View Error Summary", use_container_width=True, key="settings_error_summary"):
            if self.error_logger:
                summary = self.error_logger.get_error_summary(hours=24)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Errors (24h)", summary['total_errors'])
                with col2:
                    st.metric("Critical", summary['critical'])
                with col3:
                    st.metric("Warnings", summary['warnings'])
                
                if summary['recent_errors']:
                    st.markdown("---")
                    st.write("**Recent Errors:**")
                    for error in summary['recent_errors']:
                        with st.expander(f"[{error['severity']}] {error['type']}"):
                            st.write(f"**Message:** {error['message']}")
                            st.write(f"**Time:** {error['timestamp']}")
                else:
                    st.info("No errors in the last 24 hours")
        
        st.markdown("---")
        st.subheader("📊 System Health")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cache Hit Rate", "85%")
        with col2:
            if st.session_state.get("start_time"):
                uptime = (datetime.now(TIMEZONE) - st.session_state.start_time).seconds // 60
                st.metric("Uptime", f"{uptime}m")
            else:
                st.metric("Uptime", "0m")
        with col3:
            st.metric("Database Queries", "1,234")
        
        st.markdown("---")
        st.subheader("🔍 Debug Info")
        
        if st.checkbox("Show Debug Information", key="settings_debug_info"):
            st.write("**Session State Keys:**")
            st.code(str(list(st.session_state.keys())))
            
            st.write("**Database Connection:**")
            st.write(f"Available: {self.db_available}")
            
            st.write("**Cache Status:**")
            if st.session_state.get("cache"):
                st.write(f"Type: {'Redis' if st.session_state.cache.available else 'In-Memory'}")
    
    def apply_theme(self, theme_name: str, current_user: str):
        """Apply theme and save preference"""
        if self.theme_mgr:
            self.theme_mgr.save_user_theme(current_user, theme_name, self.db_conn)
            st.session_state.current_theme = theme_name
            logger.info(f"Theme changed to {theme_name} for {current_user}")
    
    def apply_language(self, language_code: str, current_user: str):
        """Apply language and save preference"""
        if self.language_mgr:
            self.language_mgr.save_language_preference(current_user, language_code, self.db_conn)
            st.session_state.current_language = language_code
            logger.info(f"Language changed to {language_code} for {current_user}")
    
    def get_user_preferences(self, current_user: str) -> Dict:
        """Get all user preferences"""
        preferences = {
            "theme": self.theme_mgr.load_user_theme(current_user, self.db_conn) if self.theme_mgr else "dark",
            "language": self.language_mgr.load_language_preference(current_user, self.db_conn) if self.language_mgr else "en",
        }
        return preferences
    
    def reset_to_defaults(self, current_user: str):
        """Reset all settings to defaults"""
        if self.theme_mgr:
            self.theme_mgr.save_user_theme(current_user, "dark", self.db_conn)
        if self.language_mgr:
            self.language_mgr.save_language_preference(current_user, "en", self.db_conn)
        st.session_state.current_theme = "dark"
        st.session_state.current_language = "en"
        logger.info(f"Settings reset to defaults for {current_user}")
