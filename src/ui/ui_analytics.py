import streamlit as st
from datetime import datetime, timedelta
from config import TIMEZONE

def show_caregiver_dashboard():
    """Caregiver Dashboard UI"""
    st.markdown("<h2 style='color:#00D1FF;'>👨‍⚕️ CAREGIVER DASHBOARD</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Daily Summary", "📈 Trends", "📋 Reports"])
    
    with tab1:
        st.subheader("Daily Summary")
        summary = st.session_state.dashboard.get_daily_summary(st.session_state.current_user)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Activities", summary["activities"])
        with col2:
            st.metric("Meals", summary["meals"])
        with col3:
            st.metric("Water (ml)", summary["water_intake"])
        with col4:
            st.metric("Mood", summary["mood"]["emoji"] if summary["mood"] else "N/A")
        
        st.markdown("---")
        st.metric("Medication Compliance", f"{summary['medication_compliance']:.1f}%")
        
        if summary["alerts"]:
            st.warning("⚠️ Active Alerts:")
            for alert in summary["alerts"]:
                st.write(f"- {alert['message']}")
    
    with tab2:
        st.subheader("Health Trends (30 Days)")
        trends = st.session_state.dashboard.get_health_trends(st.session_state.current_user, days=30)
        
        if trends["vital_signs_trend"]:
            st.write("**Heart Rate Trend**")
            st.line_chart([v[1] for v in trends["vital_signs_trend"]])
        
        if trends["activity_trend"]:
            st.write("**Activity Trend**")
            st.bar_chart([a[1] for a in trends["activity_trend"]])
        
        if trends["mood_trend"]:
            st.write("**Mood Trend**")
            mood_values = [1 if m[1] == "😢" else 2 if m[1] == "😔" else 3 if m[1] == "😐" else 4 if m[1] == "😊" else 5 for m in trends["mood_trend"]]
            st.line_chart(mood_values)
    
    with tab3:
        st.subheader("Generate Incident Report")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if st.button("📋 Generate Report", use_container_width=True, type="primary"):
            report = st.session_state.dashboard.generate_incident_report(st.session_state.current_user, start_date, end_date)
            st.success("Report generated!")
            st.json(report)

def show_voice_control_page():
    """Voice Control UI"""
    st.markdown("<h2 style='color:#00D1FF;'>🎤 VOICE CONTROL</h2>", unsafe_allow_html=True)
    
    st.info("Available voice commands:")
    commands = st.session_state.voice.get_available_commands()
    for cmd in commands:
        st.write(f"- {cmd}")
    
    st.markdown("---")
    st.subheader("Test Voice Command")
    
    voice_input = st.text_input("Enter command (or say it):")
    
    if voice_input:
        result = st.session_state.voice.process_voice_command(voice_input)
        st.write(f"**Status**: {result['status']}")
        st.write(f"**Response**: {result['message']}")

def show_privacy_page():
    """Privacy & Data Management UI"""
    st.markdown("<h2 style='color:#00D1FF;'>🔒 PRIVACY & DATA</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Permissions", "📋 Audit Log", "📥 Export Data", "🗑️ Delete Data"])
    
    with tab1:
        st.subheader("Access Permissions")
        caregiver = st.text_input("Caregiver Username")
        
        permissions = {
            "camera": st.checkbox("Camera Access"),
            "messages": st.checkbox("Messages Access"),
            "health": st.checkbox("Health Data Access"),
            "location": st.checkbox("Location Access"),
            "activity": st.checkbox("Activity Access")
        }
        
        if st.button("✅ Set Permissions", use_container_width=True, type="primary"):
            st.session_state.privacy.set_access_permissions(st.session_state.current_user, caregiver, permissions)
            st.success("Permissions updated!")
        
        time_based = st.checkbox("Enable time-based access?")
        if time_based:
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("Start Time")
            with col2:
                end_time = st.time_input("End Time")
            
            if st.button("✅ Set Time Restriction", use_container_width=True):
                st.session_state.privacy.set_time_based_access(st.session_state.current_user, caregiver, str(start_time), str(end_time))
                st.success("Time restriction set!")
    
    with tab2:
        st.subheader("Access Audit Log")
        audit_log = st.session_state.privacy.get_access_audit_log(st.session_state.current_user, days=30)
        
        if audit_log:
            for log in audit_log:
                st.write(f"**{log[1]}** accessed {log[2]}: {log[3]} @ {log[4]}")
        else:
            st.info("No access logs")
    
    with tab3:
        st.subheader("Export Your Data (GDPR)")
        st.info("Download all your personal data in JSON format")
        
        if st.button("📥 Export Data", use_container_width=True, type="primary"):
            export = st.session_state.privacy.export_user_data(st.session_state.current_user)
            st.json(export)
            st.download_button("Download JSON", str(export), "user_data.json")
    
    with tab4:
        st.subheader("Delete Your Data")
        st.warning("⚠️ This action cannot be undone!")
        
        data_types = st.multiselect("Select data to delete", ["messages", "vital_signs", "activity_logs", "reminders", "mood_logs"])
        
        if st.button("🗑️ Delete Selected Data", use_container_width=True, type="secondary"):
            if st.checkbox("I understand this cannot be undone"):
                deleted = st.session_state.privacy.delete_user_data(st.session_state.current_user, data_types)
                st.success(f"✅ {deleted} records deleted")

def show_accessibility_page():
    """Accessibility Settings UI"""
    st.markdown("<h2 style='color:#00D1FF;'>♿ ACCESSIBILITY</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 Themes", "⌨️ Shortcuts", "🔊 Text-to-Speech"])
    
    with tab1:
        st.subheader("Theme Selection")
        theme = st.selectbox("Select Theme", ["default", "large_text", "high_contrast", "high_contrast_large", "dark_mode"])
        
        if st.button("✅ Apply Theme", use_container_width=True, type="primary"):
            st.session_state.accessibility.apply_theme(theme)
            st.success(f"Theme changed to {theme}!")
            st.rerun()
    
    with tab2:
        st.subheader("Keyboard Shortcuts")
        shortcuts = st.session_state.accessibility.get_keyboard_shortcuts()
        
        for shortcut, action in shortcuts.items():
            st.write(f"**{shortcut}**: {action}")
    
    with tab3:
        st.subheader("Text-to-Speech")
        text = st.text_area("Enter text to read aloud:")
        language = st.selectbox("Language", ["en", "es", "fr", "de"])
        
        if st.button("🔊 Read Aloud", use_container_width=True, type="primary"):
            st.session_state.accessibility.enable_text_to_speech(text, language)
            st.success("Reading text...")

def show_offline_page():
    """Offline Mode UI"""
    st.markdown("<h2 style='color:#00D1FF;'>📡 OFFLINE MODE</h2>", unsafe_allow_html=True)
    
    status = st.session_state.offline.get_sync_status()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Queued Messages", status["total_queued"])
    with col2:
        st.metric("Synced", status["synced"])
    with col3:
        st.metric("Pending", status["unsynced"])
    
    st.markdown("---")
    
    if st.button("🔄 Sync Now", use_container_width=True, type="primary"):
        synced = st.session_state.offline.sync_messages(st.session_state.chat_manager)
        st.success(f"✅ {synced} messages synced!")
    
    if st.button("🗑️ Clear Old Cache", use_container_width=True):
        st.session_state.offline.clear_old_cache(days=30)
        st.success("Cache cleared!")
