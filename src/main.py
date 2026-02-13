import sys
from pathlib import Path

# Add src directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import mysql.connector
from pyngrok import ngrok
from datetime import datetime, timedelta
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import atexit
import time

# Import custom modules
from config import NGROK_AUTH_TOKEN, NGROK_ADDR, NGROK_DOMAIN, TIMEZONE
from database import get_db_connection, create_tables
from utils.audio_system import AudioSystem
from utils.chat_manager import ChatManager
from core.vital_signs import VitalSignsTracker
from core.medication_manager import MedicationManager
from core.geofencing import GeofencingSystem
from core.emergency_system import EmergencySystem
from core.activity_recognition import ActivityRecognition
from features.nutrition_tracker import NutritionTracker
from features.mood_tracker import MoodTracker
from features.smart_home import SmartHomeController
from features.caregiver_dashboard import CaregiverDashboard
from features.voice_control import VoiceControl
from ui.accessibility import AccessibilityManager
from utils.offline_mode import OfflineMode
from utils.privacy_manager import PrivacyManager
from utils.cache_manager import CacheManager
from utils.error_logger import ErrorLogger
from utils.rate_limiter import RateLimiter
from ui.theme_manager import ThemeManager
from ui.dashboard_customizer import DashboardCustomizer
from ui.ui_video_monitor import show_video_monitor
from utils.report_generator import ReportGenerator
from utils.language_manager import LanguageManager
from utils.offline_sync_manager import OfflineSyncManager
from utils.reminder_system import ReminderSystem
from utils.settings import SettingsManager
from video.video_processor import VideoProcessor
from ui.dashboard_customizer import DashboardCustomizer
from utils.report_generator import ReportGenerator
from utils.language_manager import LanguageManager
from utils.offline_sync_manager import OfflineSyncManager
from video.video_processor import VideoProcessor
from io import BytesIO

# ------------------ NGROK (FIXED) ------------------
def start_ngrok():
    try:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        
        # Check for existing tunnels to avoid redundant creation
        tunnels = ngrok.get_tunnels()
        for t in tunnels:
            if t.config.get('addr') == f'http://localhost:{NGROK_ADDR}' or t.config.get('addr') == str(NGROK_ADDR):
                return t.public_url
        
        # Kill all existing ngrok processes to start fresh if no matching tunnel found
        ngrok.kill()
        
        # Connect with static domain if configured
        if NGROK_DOMAIN:
            tunnel = ngrok.connect(addr=NGROK_ADDR, domain=NGROK_DOMAIN, bind_tls=True)
        else:
            tunnel = ngrok.connect(addr=NGROK_ADDR, bind_tls=True)
            
        return tunnel.public_url
    except Exception as e:
        return f"NGROK ERROR: {e}"

if "public_url" not in st.session_state:
    st.session_state.public_url = start_ngrok()

st.sidebar.success("🌐 Public Link")
st.sidebar.write(st.session_state.public_url)

# ------------------ DATABASE CONNECTION ------------------
db_conn, db_available = get_db_connection()

# ------------------ SESSION STATE ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_page = "🏠 Home" # Renamed and set as default
    st.session_state.video_processor = None
    st.session_state.audio_system = None
    st.session_state.reminder_system = None
    st.session_state.motion_alerts = []
    st.session_state.announcements = []
    st.session_state.reminders = []
    st.session_state.triggered_reminders = []
    st.session_state.start_time = None
    st.session_state.last_audio_message = None
    st.session_state.chat_target = None
    st.session_state.chat_history = []
    st.session_state.voice_message = None
    st.session_state.incidents = []      # Store snapshots of falls
    st.session_state.alert_active = False # Global alert status
    st.session_state.motion_history = [0] * 60 # Last 60 minutes of motion counts

# Initialize systems
if st.session_state.get("video_processor") is None:
    st.session_state.video_processor = VideoProcessor()

# --- Sync Incidents from VideoProcessor ---
if st.session_state.video_processor and hasattr(st.session_state.video_processor, 'pending_incidents'):
    while st.session_state.video_processor.pending_incidents:
        new_incid = st.session_state.video_processor.pending_incidents.pop(0)
        st.session_state.incidents.append({
            "time": new_incid["timestamp"],
            "image": new_incid["image"],
            "event": "Fall Detected"
        })
        st.session_state.alert_active = True # Trigger the Global Banner

if st.session_state.get("audio_system") is None:
    st.session_state.audio_system = AudioSystem()

if st.session_state.get("reminder_system") is None:
    st.session_state.reminder_system = ReminderSystem()
    st.session_state.reminder_system.start_background_check()

if st.session_state.get("chat_manager") is None:
    st.session_state.chat_manager = ChatManager(db_conn, db_available)
else:
    # Always update the connection to avoid stale objects
    st.session_state.chat_manager.db_conn = db_conn
    st.session_state.chat_manager.db_available = db_available

# Initialize enhancement systems
if st.session_state.get("cache") is None:
    st.session_state.cache = CacheManager()

if st.session_state.get("error_logger") is None:
    st.session_state.error_logger = ErrorLogger(db_conn, db_available)

if st.session_state.get("rate_limiter") is None:
    st.session_state.rate_limiter = RateLimiter()

if st.session_state.get("theme_mgr") is None:
    st.session_state.theme_mgr = ThemeManager()

if st.session_state.get("dashboard_customizer") is None:
    st.session_state.dashboard_customizer = DashboardCustomizer(db_conn, db_available)

if st.session_state.get("report_generator") is None:
    st.session_state.report_generator = ReportGenerator(db_conn, db_available)

if st.session_state.get("language_mgr") is None:
    st.session_state.language_mgr = LanguageManager()

if st.session_state.get("sync_mgr") is None:
    st.session_state.sync_mgr = OfflineSyncManager()

if "current_theme" not in st.session_state:
    st.session_state.current_theme = "dark"

if "current_language" not in st.session_state:
    st.session_state.current_language = "en"

# Initialize settings manager
# Initialize settings manager (moved to after all systems are initialized)
# See line ~1100 for actual initialization

# Apply theme immediately after initialization
if st.session_state.logged_in:
    saved_theme = st.session_state.theme_mgr.load_user_theme(st.session_state.current_user, db_conn)
    st.session_state.current_theme = saved_theme
    theme_css = st.session_state.theme_mgr.apply_theme(saved_theme)
    st.markdown(theme_css, unsafe_allow_html=True)

# ------------------ CUSTOM STYLES ------------------
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Ubuntu+Mono&display=swap');
    
    :root {
        --bg-midnight: #0B0E14;
        --accent-blue: #0078FF;
        --accent-glow: #00D1FF;
        --alert-orange: #FF5E00;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    .stApp {
        background-color: var(--bg-midnight);
        color: #E0E6ED;
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism Cards */
    [data-testid="stMetric"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        padding: 15px !important;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: var(--accent-glow);
    }
    
    /* Emergency Alert Banner */
    .emergency-banner {
        background: linear-gradient(90deg, #FF5E00, #FF2D00);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        animation: pulse-alert 2s infinite;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(255, 94, 0, 0.3);
    }
    
    @keyframes pulse-alert {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(0.99); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Circular Glowing Talk Buttons */
    .talk-btn-container {
        display: flex;
        justify-content: center;
        padding: 20px;
    }
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F131A !important;
        border-right: 1px solid var(--glass-border);
    }
    
    /* Chat Bubbles */
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 18px;
        margin-bottom: 12px;
        max-width: 85%;
        backdrop-filter: blur(5px);
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #0078FF, #0056B3);
        color: white;
        border-bottom-right-radius: 4px;
    }
    .chat-bubble-assistant {
        background: var(--glass-bg);
        color: #E0E6ED;
        border: 1px solid var(--glass-border);
        border-bottom-left-radius: 4px;
    }
    
    /* Hardware monitoring cards for Dashboard */
    .health-card {
        padding: 20px;
        border-radius: 12px;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--glass-border);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .health-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: var(--accent-glow);
        box-shadow: 0 0 10px var(--accent-glow);
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ------------------ TITLE ------------------
# Global Alert Banner (New)
if st.session_state.alert_active:
    st.markdown("""
    <div class="emergency-banner">
        🚨 EMERGENCY ALERT: Fall Detected! Please check CCTV immediately.
        <br><small>A snapshot has been saved to your dashboard gallery.</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✅ Clear Alert", use_container_width=True):
        st.session_state.alert_active = False
        st.rerun()

st.markdown(
    "<h1 style='text-align:center; color:#00D1FF; text-shadow: 0 0 10px rgba(0,209,255,0.4);'>🏠 SmartHome Command Center</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# ------------------ LOGIN / REGISTER PAGE ------------------
if not st.session_state.logged_in:
    st.subheader("🔐 System Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # Login
    with col1:
        if st.button("🔓 Login", use_container_width=True, type="primary"):
            if username and password:
                if db_available:
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute(
                            "SELECT * FROM users WHERE username=%s AND password_hash=%s",
                            (username, password)
                        )
                        user = cursor.fetchone()
                        
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.current_user = username
                            st.session_state.current_page = "🏠 Home"
                            st.session_state.video_processor = VideoProcessor()
                            st.session_state.motion_alerts = []
                            st.session_state.announcements = []
                            st.session_state.reminders = []
                            st.session_state.start_time = datetime.now(TIMEZONE)
                            
                            # Create tables if they don't exist
                            create_tables(db_conn)
                            
                            st.success(f"✅ Welcome {username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    except Exception as e:
                        st.error(f"Login error: {e}")
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.current_page = "🏠 Home"
                    st.session_state.video_processor = VideoProcessor()
                    st.session_state.motion_alerts = []
                    st.session_state.announcements = []
                    st.session_state.reminders = []
                    st.session_state.start_time = datetime.now(TIMEZONE)
                    st.success(f"✅ Welcome {username}!")
                    st.rerun()
            else:
                st.warning("Please enter username and password")

    # Register
    with col2:
        if st.button("📝 Register", use_container_width=True):
            if username and password:
                if db_available:
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                            (username, password)
                        )
                        db_conn.commit()
                        st.success("✅ Account created! You can now login.")
                    except mysql.connector.Error as e:
                        if e.errno == 1062:
                            st.error("⚠️ Username already exists")
                        else:
                            st.error(f"Registration error: {e}")
                else:
                    if "local_users" not in st.session_state:
                        st.session_state.local_users = {}
                    
                    if username in st.session_state.local_users:
                        st.error("⚠️ Username already exists")
                    else:
                        st.session_state.local_users[username] = password
                        st.success("✅ Account created! You can now login.")
            else:
                st.warning("Please enter username and password")

# ------------------ MAIN SYSTEM ------------------
else:
    # Check for triggered reminders
    if hasattr(st.session_state, 'triggered_reminders') and st.session_state.triggered_reminders:
        for reminder in st.session_state.triggered_reminders[:]:
            if reminder.get("audio_message"):
                st.session_state.audio_system.play_audio(reminder["audio_message"])
            
            st.toast(f"🔔 REMINDER: {reminder['title']}\n{reminder['message']}", icon="⏰")
            
            st.session_state.announcements.append({
                "user": "REMINDER SYSTEM",
                "text": f"Reminder: {reminder['title']} - {reminder['message']}",
                "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"),
                "type": "reminder"
            })
        st.session_state.triggered_reminders = []
    
    # Sidebar Navigation

    
    # ------------------ CCTV PAGE ------------------
    if st.session_state.current_page == "🎥 CCTV":
        st.markdown(f"<h2 style='color:#FF5733;'>📹 CCTV MONITORING</h2>", unsafe_allow_html=True)
        
        current_time = datetime.now(TIMEZONE).strftime("%H:%M:%S")
        st.metric("Current Time", current_time)
        
        st.markdown("---")
        st.subheader("🎥 Live Camera Feed")
        st.info("💡 **Note**: Fall detection runs via Node-RED. Video stream optimized for smooth playback.")
        
        RTC_CONFIGURATION = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        webrtc_ctx = webrtc_streamer(
            key="cctv-monitoring",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={
                "video": {"width": {"ideal": 1280}, "height": {"ideal": 720}, "frameRate": {"ideal": 30}},
                "audio": False
            },
            video_processor_factory=VideoProcessor,
            async_processing=True,
        )
        
        if not webrtc_ctx.state.playing:
            st.warning("⚠️ Camera feed not active")
            st.image("https://via.placeholder.com/640x360/333333/FFFFFF?text=Live+Camera+Feed")
        
        # Display monitoring metrics
        st.markdown("---")
        st.subheader("📊 Performance Metrics")
        
        if webrtc_ctx.state.playing and st.session_state.video_processor:
            processor = st.session_state.video_processor
            
            # Create three columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                fps = processor.get_fps()
                st.metric("FPS", f"{fps:.1f}", delta="Target: 30", delta_color="off")
            
            with col2:
                latency = processor.get_latency()
                st.metric("Latency", f"{latency:.0f}ms", delta="Target: <100ms", delta_color="off")
            
            with col3:
                cpu = processor.get_cpu_usage()
                st.metric("CPU Usage", f"{cpu:.1f}%", delta="Target: <10%", delta_color="off")
            
            with col4:
                memory = processor.get_memory_usage()
                st.metric("Memory", f"{memory:.1f}MB", delta="Stable", delta_color="off")
            
            # Connection status
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.success("✅ **Connection Status**: Connected")
            with col2:
                st.info(f"📹 **Frames Processed**: {processor.frame_count}")
        else:
            st.warning("⚠️ Waiting for camera connection...")

        # Quick Talk Control Hub (Optimized Layout)
        st.markdown("---")
        st.subheader("🎤 Community Intercom Hub")
        
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                talk_duration = st.slider("Record Duration", 3, 20, 10, help="Drag to set how long you want to record your voice.")
                if st.button("🎤 HOLD TO TALK", use_container_width=True, type="primary"):
                    with st.spinner(f"Recording..."):
                        audio = st.session_state.audio_system.record_audio(talk_duration)
                        if audio:
                            st.session_state.last_audio_message = audio
                            timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                            st.session_state.announcements.append({
                                "user": st.session_state.current_user,
                                "text": f"CCTV Intercom ({talk_duration}s)",
                                "time": timestamp, "audio": audio, "type": "quick"
                            })
                            st.success(f"✅ Success!")
                            st.session_state.audio_system.play_audio(audio)
            
            with col2:
                st.write("") # Spacer
                if st.session_state.last_audio_message:
                    if st.button("🔊 Replay My Last", use_container_width=True):
                        st.session_state.audio_system.play_audio(st.session_state.last_audio_message)
                else:
                    st.info("No recordings")
    
    # ------------------ FLASK VIDEO MONITOR PAGE ------------------
    elif st.session_state.current_page == "📹 Flask Video":
        show_video_monitor()
    
    # ------------------ CHAT PAGE ------------------
    elif st.session_state.current_page == "💬 Chat":
        st.markdown(f"<h2 style='color:#00D1FF;'>💬 CHAT WITH USERS</h2>", unsafe_allow_html=True)
        # ... (rest of search result was truncated but I will provide the full block)
        # Get list of users for chat
        chat_users = []
        if db_available:
            try:
                cursor = db_conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username != %s", (st.session_state.current_user,))
                chat_users = [u[0] for u in cursor.fetchall()]
            except Exception as e:
                st.error(f"Error fetching users: {e}")
        else:
            # Fallback for local testing
            if "local_users" in st.session_state:
                chat_users = [u for u in st.session_state.local_users.keys() if u != st.session_state.current_user]

        if chat_users:
            selected_chat = st.selectbox("Select user to chat with:", ["None"] + chat_users)
            if selected_chat != "None":
                st.session_state.chat_target = selected_chat
                st.write(f"Chatting with **{selected_chat}**")
                
                # DB & Sync Status
                if not db_available:
                    st.error("🔴 **OFFLINE MODE**: Messages are saved locally and NOT shared with others. Start MySQL to sync.")
                else:
                    st.success("🟢 **SYNCED**: Connected to database. Messages are shared in real-time.")
                    # Table Verification
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute("SHOW TABLES LIKE 'messages'")
                        if not cursor.fetchone():
                            st.warning("⚠️ **Sync Table Missing**: Click 'Create Tables Automatically' in the sidebar to enable chat sync.")
                    except: pass
                
                # Refresh button
                if st.button("🔃 REFRESH CHAT", use_container_width=True):
                    st.rerun()
                
                # Fetch messages
                messages = st.session_state.chat_manager.get_messages(st.session_state.current_user, selected_chat)
                
                # Chat and Sidebar Debug
                with st.expander("🛠️ Connection Details"):
                    st.write(f"Logged in as: `{st.session_state.current_user}`")
                    st.write(f"Chatting with: `{selected_chat}`")
                    st.write(f"DB Mode: `{'🟢 SYNCED' if db_available else '🔴 OFFLINE'}`")
                    st.write(f"Found in this chat: `{len(messages)}` messages")
                    
                    if db_available:
                        st.markdown("---")
                        st.subheader("🕵️ Global Database Inspector")
                        st.caption("This shows the last 5 messages in the WHOLE database (any user)")
                        try:
                            cursor = db_conn.cursor()
                            cursor.execute("SELECT id, sender, receiver, timestamp FROM messages ORDER BY id DESC LIMIT 5")
                            rows = cursor.fetchall()
                            if rows:
                                for r in rows: st.code(f"ID:{r[0]} | {r[1]} -> {r[2]} ({r[3]})")
                            else:
                                st.warning("Database table 'messages' is EMPTY.")
                        except:
                            st.error("Could not read Global Log.")
                
                # Chat container
                chat_container = st.container(height=500, border=True)
                
                # Check for new messages for notification
                if messages:
                    latest_msg = messages[-1]
                    msg_sender = latest_msg[0]
                    # We only care about the ID for tracking "newness"
                    # But we only toast if the SENDER is the other person
                    current_max_id = st.session_state.chat_manager.get_latest_message_id(st.session_state.current_user, selected_chat)
                    
                    if "last_max_id" not in st.session_state:
                        st.session_state.last_max_id = current_max_id
                    
                    if current_max_id > st.session_state.last_max_id:
                        if msg_sender != st.session_state.current_user:
                            st.toast(f"💬 New message from {msg_sender}!", icon="👋")
                        st.session_state.last_max_id = current_max_id

                with chat_container:
                    if not messages:
                        st.info("No messages between you yet. Start the conversation below!")
                    else:
                        for i, (msg_sender, msg_content, msg_audio, msg_time) in enumerate(messages):
                            # FIXED: Case-insensitive 'is_me' check (prevents your messages showing on the left)
                            is_me = str(msg_sender).strip().lower() == str(st.session_state.current_user).strip().lower()
                            align = "flex-end" if is_me else "flex-start"
                            bubble_class = "chat-bubble-user" if is_me else "chat-bubble-assistant"
                            
                            # Row wrapper
                            st.markdown(f'<div style="display: flex; justify-content: {align}; padding: 2px;">', unsafe_allow_html=True)
                            
                            if msg_content:
                                st.markdown(f"""
                                <div class="chat-bubble {bubble_class}" style="box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                                    <small style="font-weight: bold; opacity: 0.9; color: {'#FFF' if is_me else '#0078FF'};">{msg_sender}</small>
                                    <div style="margin-top: 2px;">{msg_content}</div>
                                    <div style="font-size: 0.65rem; text-align: right; opacity: 0.6; margin-top: 5px;">{msg_time}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if msg_audio:
                                with st.container():
                                    st.markdown(f"""
                                    <div class="chat-bubble {bubble_class}" style="border: 1px solid rgba(255,255,255,0.2);">
                                        <small style="opacity: 0.8;">{msg_sender} sent a audio clip</small><br>
                                        🎤 Voice Note ({msg_time})
                                    </div>
                                    """, unsafe_allow_html=True)
                                    if st.button(f"▶️ Play", key=f"v_play_{i}_{msg_time}"):
                                        st.session_state.audio_system.play_audio(BytesIO(msg_audio))
                            
                            st.markdown('</div>', unsafe_allow_html=True)

                # Chat inputs
                chat_input = st.chat_input("Type your message...")
                if chat_input:
                    if st.session_state.chat_manager.send_message(st.session_state.current_user, selected_chat, content=chat_input):
                        st.rerun()
                
                # Voice recorder in chat (Audio Improvements - 6)
                st.markdown("---")
                v_col1, v_col2 = st.columns([1, 1])
                with v_col1:
                    voice_duration = st.slider("Voice message duration", 3, 10, 5, key="chat_voice_dur")
                    if st.button("🎤 RECORD VOICE MSG", use_container_width=True):
                        with st.spinner("Recording (Optimized)..."):
                            # Use record_optimized (6)
                            audio_data = st.session_state.audio_system.record_optimized(voice_duration)
                            if audio_data:
                                if st.session_state.chat_manager.send_message(st.session_state.current_user, selected_chat, audio_data=audio_data.getvalue()):
                                    st.success("✅ Voice message sent!")
                
                # Auto-refresh disabled to prevent sidebar darkening
                # Users can click "REFRESH CHAT" button manually instead
        else:
            st.warning("No other users available to chat.")
            
        st.markdown("---")
        st.subheader("📋 Recent Announcements")
        if st.session_state.announcements:
            live_messages = [msg for msg in st.session_state.announcements if msg['type'] in ['live', 'quick']]
            if live_messages:
                for msg in reversed(live_messages[-5:]):
                    col_l, col_r = st.columns([3, 1])
                    with col_l:
                        st.write(f"**{msg['user']}** ({msg['time']}): {msg['text']}")
                    with col_r:
                        if st.button("▶️ Play", key=f"play_{msg['time']}"):
                            st.session_state.audio_system.play_audio(msg['audio'])
                    st.markdown("---")
            else:
                st.info("No live talk messages yet")

    # ------------------ AUDIO TOOLS PAGE ------------------
    elif st.session_state.current_page == "🔊 Audio Tools":
        st.markdown(f"<h2 style='color:#FF5733;'>🔊 AUDIO UTILITY TOOLS</h2>", unsafe_allow_html=True)
        st.info("""
        **Audio Tools:**
        - ⚡ **Quick Sounds** - Play attention and doorbell alerts
        - 🎚️ **Audio Test** - Verify your microphone and speaker settings
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("⚡ Quick Sounds")
            col_sound1, col_sound2 = st.columns(2)
            with col_sound1:
                if st.button("📣 ATTENTION", use_container_width=True):
                    beep = st.session_state.audio_system.generate_beep(frequency=880, duration=2.0)
                    if beep:
                        st.session_state.audio_system.play_audio(beep)
                        st.success("Attention sound played!")
            
            with col_sound2:
                if st.button("🔔 DOORBELL", use_container_width=True):
                    beep1 = st.session_state.audio_system.generate_beep(frequency=800, duration=0.5)
                    beep2 = st.session_state.audio_system.generate_beep(frequency=600, duration=0.5)
                    if beep1 and beep2:
                        st.session_state.audio_system.play_audio(beep1)
                        time.sleep(0.5)
                        st.session_state.audio_system.play_audio(beep2)
                        st.success("Doorbell sound played!")
        
        with col2:
            st.subheader("🎚️ Audio Test")
            if st.button("🔊 TEST MICROPHONE", use_container_width=True):
                with st.spinner("Testing microphone for 3 seconds..."):
                    test_audio = st.session_state.audio_system.record_audio(3)
                    if test_audio:
                        st.success("✅ Microphone test successful!")
                        st.session_state.audio_system.play_audio(test_audio)
        
        st.markdown("---")
        st.subheader("🔊 Playback")
        if st.session_state.last_audio_message:
            if st.button("▶️ PLAY LAST GLOBAL RECORDING", use_container_width=True):
                st.session_state.audio_system.play_audio(st.session_state.last_audio_message)
        else:
            st.info("No global recording available")

    # ------------------ INTERCOM PAGE ------------------
    elif st.session_state.current_page == "🎤 Intercom":
        st.markdown(f"<h2 style='color:#00D1FF;'>🎤 SMART INTERCOM</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="talk-btn-container">', unsafe_allow_html=True)
            if st.button("🎤 PUSH TO TALK", use_container_width=True, type="primary"):
                # Style can be applied via the talk-btn-container class in CSS
                audio = st.session_state.audio_system.record_audio(5)
                if audio:
                    st.session_state.announcements.append({"user": st.session_state.current_user, "text": "Voice Message", "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"), "audio": audio, "type": "intercom"})
                    st.session_state.audio_system.play_audio(audio)
                    st.success("Message Sent through Intercom!")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="talk-btn-container">', unsafe_allow_html=True)
            if st.button("🔊 LISTEN TO ROOM", use_container_width=True):
                st.info("Listening to live room audio...")
            st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ ANNOUNCE PAGE ------------------
    elif st.session_state.current_page == "📢 Announce":
        st.markdown(f"<h2 style='color:#00D1FF;'>📢 ANNOUNCEMENT SYSTEM</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎤 Record Announcement")
            message_text = st.text_area("Announcement text", value="Attention everyone! Please gather in the living room.", height=100, help="Type the message you want to save or announce.")
            record_duration = st.slider("Duration (seconds)", 5, 60, 15, help="How long the microphone will stay active.")
            if st.button("🎤 RECORD ANNOUNCEMENT", use_container_width=True, type="primary", help="Immediately starts recording your voice message."):
                with st.spinner(f"Recording for {record_duration} seconds..."):
                    audio = st.session_state.audio_system.record_audio(record_duration)
                    if audio:
                        timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                        st.session_state.announcements.append({
                            "user": st.session_state.current_user,
                            "text": message_text,
                            "time": timestamp,
                            "audio": audio,
                            "type": "announcement"
                        })
                        st.session_state.last_audio_message = audio
                        st.success(f"✅ Announcement recorded! ({record_duration}s)")
                        st.session_state.audio_system.play_audio(audio)
        
        with col2:
            st.subheader("📢 Quick Announcements")
            qa_col1, qa_col2 = st.columns(2)
            with qa_col1:
                if st.button("💊 MEDICINE TIME", use_container_width=True):
                    msg = "Time to take your medicine!"
                    beep = st.session_state.audio_system.generate_beep(frequency=440, duration=3.0)
                    if beep:
                        st.session_state.announcements.append({
                            "user": "SYSTEM", "text": msg, "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"),
                            "audio": beep, "type": "quick"
                        })
                        st.session_state.audio_system.play_audio(beep)
                        st.success("Medicine reminder announced!")
            
            with qa_col2:
                if st.button("🍽️ MEAL TIME", use_container_width=True):
                    msg = "Meal time! Please come to the dining area."
                    beep = st.session_state.audio_system.generate_beep(frequency=523, duration=3.0)
                    if beep:
                        st.session_state.announcements.append({
                            "user": "SYSTEM", "text": msg, "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"),
                            "audio": beep, "type": "quick"
                        })
                        st.session_state.audio_system.play_audio(beep)
                        st.success("Meal reminder announced!")

            st.markdown("---")
            st.subheader("💾 Saved Announcements")
            saved_ann = [a for a in st.session_state.announcements if a['type'] == 'announcement']
            if saved_ann:
                for ann in reversed(saved_ann[-3:]):
                    st.write(f"**{ann['user']}** ({ann['time']}): {ann['text'][:100]}...")
                    if st.button("▶️ Play", key=f"play_ann_{ann['time']}"):
                        st.session_state.audio_system.play_audio(ann['audio'])
                    st.markdown("---")
            else:
                st.info("No saved announcements")

    # ------------------ REMINDERS PAGE ------------------
    elif st.session_state.current_page == "⏰ Reminders":
        st.markdown(f"<h2 style='color:#00D1FF;'>⏰ SMART REMINDERS</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["➕ Set New Reminder", "📋 Active Reminders", "🎯 Quick Presets"])
        
        with tab1:
            st.subheader("➕ Set New Reminder")
            reminder_title = st.text_input("Reminder Title", "Medicine Reminder")
            reminder_message = st.text_area("Reminder Message", "Time to take your medicine! 💊")
            
            col1, col2 = st.columns(2)
            with col1:
                schedule_type = st.radio("Schedule Type", ["In X minutes", "Specific Time", "Daily", "Hourly"])
                if schedule_type == "In X minutes":
                    minutes = st.number_input("Minutes from now", min_value=1, max_value=1440, value=5)
                    trigger_time = datetime.now(TIMEZONE) + timedelta(minutes=minutes)
                elif schedule_type == "Specific Time":
                    date = st.date_input("Date", datetime.now(TIMEZONE).date())
                    time_input = st.time_input("Time", datetime.now(TIMEZONE).time())
                    trigger_time = datetime.combine(date, time_input).replace(tzinfo=TIMEZONE)
                elif schedule_type == "Daily":
                    time_input = st.time_input("Daily at", datetime.now(TIMEZONE).time())
                    trigger_time = datetime.combine(datetime.now(TIMEZONE).date(), time_input).replace(tzinfo=TIMEZONE)
                    if trigger_time < datetime.now(TIMEZONE): trigger_time += timedelta(days=1)
                elif schedule_type == "Hourly":
                    minute = st.number_input("Minute past each hour", min_value=0, max_value=59, value=0)
                    trigger_time = datetime.now(TIMEZONE).replace(minute=minute, second=0, microsecond=0)
                    if trigger_time < datetime.now(TIMEZONE): trigger_time += timedelta(hours=1)
            
            with col2:
                st.subheader("🔊 Audio Settings")
                audio_option = st.radio("Audio Announcement", ["Record Voice Message", "Beep Sound", "No Audio"])
                audio_data = None
                if audio_option == "Record Voice Message":
                    if st.button("🎤 Record Voice"):
                        with st.spinner("Recording for 5 seconds..."):
                            audio_data = st.session_state.audio_system.record_audio(5)
                            if audio_data: st.success("✅ Voice recorded!")
                elif audio_option == "Beep Sound":
                    audio_data = st.session_state.audio_system.generate_beep(duration=3.0)
            
            repeat_option = "once"
            if schedule_type in ["Daily", "Hourly"]: repeat_option = schedule_type.lower()
            else: repeat_option = st.selectbox("Repeat", ["once", "daily", "hourly"])
            
            if st.button("✅ SET REMINDER", use_container_width=True, type="primary"):
                reminder = st.session_state.reminder_system.add_reminder(
                    title=reminder_title, message=reminder_message, trigger_time=trigger_time,
                    repeat=repeat_option, audio_message=audio_data
                )
                st.session_state.reminders.append(reminder)
                if db_available and audio_data:
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute(
                            "INSERT INTO reminders (username, title, message, trigger_time, repeat_type, audio_data, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (st.session_state.current_user, reminder_title, reminder_message, trigger_time, repeat_option, audio_data.getvalue(), "pending")
                        )
                        db_conn.commit()
                    except Exception as e:
                        st.warning(f"⚠️ Service error: {e}")
                st.success(f"✅ Reminder set for {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")

        with tab2:
            st.subheader("📋 Active Reminders")
            pending = st.session_state.reminder_system.get_pending_reminders()
            if pending:
                for reminder in pending:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{reminder['title']}**")
                        st.write(reminder['message'])
                        time_left = reminder['trigger_time'] - datetime.now(TIMEZONE)
                        if time_left.total_seconds() > 0:
                            st.caption(f"⏰ In {int(time_left.total_seconds() // 60)}m {int(time_left.total_seconds() % 60)}s")
                    with col2:
                        if st.button("▶️ Test", key=f"test_{reminder['id']}"):
                            if reminder.get("audio_message"): st.session_state.audio_system.play_audio(reminder["audio_message"])
                    with col3:
                        if st.button("❌ Cancel", key=f"cancel_{reminder['id']}"):
                            if st.session_state.reminder_system.cancel_reminder(reminder['id']):
                                st.success("Cancelled!")
                                st.rerun()
                    st.markdown("---")
            else:
                st.info("No active reminders")

        with tab3:
            st.subheader("🎯 Quick Presets")
            presets = st.columns(2)
            with presets[0]:
                if st.button("💊 Medicine\n(5 minutes)", use_container_width=True):
                    trigger = datetime.now(TIMEZONE) + timedelta(minutes=5)
                    beep = st.session_state.audio_system.generate_beep(duration=3.0)
                    st.session_state.reminder_system.add_reminder("Medicine Time", "Take your prescribed medicine", trigger, audio_message=beep)
                    st.success("Set!")
            with presets[1]:
                if st.button("🍽️ Lunch\n(1 hour)", use_container_width=True):
                    trigger = datetime.now(TIMEZONE) + timedelta(hours=1)
                    beep = st.session_state.audio_system.generate_beep(frequency=523, duration=3.0)
                    st.session_state.reminder_system.add_reminder("Lunch Time", "Time to have your lunch", trigger, audio_message=beep)
                    st.success("Set!")

    # ------------------ HOME PAGE (Renamed from Dashboard) ------------------
    elif st.session_state.current_page == "🏠 Home":
        st.markdown(f"<h2 style='color:#00D1FF;'>🏠 SMART HOME OVERVIEW</h2>", unsafe_allow_html=True)
        # Removed redundant Dashboard title
        
        # Hardware Health Section (Re-styled)
        st.subheader("🖥️ Hardware Status")
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        with h_col1:
            ngrok_status = "ONLINE" if "http" in str(st.session_state.public_url) else "OFFLINE"
            glow = "#00FF41" if ngrok_status == "ONLINE" else "#FF3131"
            st.markdown(f'<div class="health-card" style="border-top: 2px solid {glow};"><strong>TUNNEL</strong><br><span style="color:{glow}">{ngrok_status}</span></div>', unsafe_allow_html=True)
            st.caption("Active Public URL tunnel status.", help="Ngrok provides the link for remote access.")
        with h_col2:
            db_status = "SYNCED" if db_available else "LOCAL"
            glow = "#00FF41" if db_available else "#FFD700"
            st.markdown(f'<div class="health-card" style="border-top: 2px solid {glow};"><strong>DB CORE</strong><br><span style="color:{glow}">{db_status}</span></div>', unsafe_allow_html=True)
            st.caption("Central database connection.", help="Synced means messages are shared across all users.")
        with h_col3:
            audio_status = "READY" if st.session_state.audio_system else "ERROR"
            glow = "#00FF41" if st.session_state.audio_system else "#FF3131"
            st.markdown(f'<div class="health-card" style="border-top: 2px solid {glow};"><strong>AUDIO</strong><br><span style="color:{glow}">{audio_status}</span></div>', unsafe_allow_html=True)
            st.caption("Microphone & speaker status.", help="Check local audio hardware.")
        with h_col4:
            uptime = f"{(datetime.now(TIMEZONE) - st.session_state.start_time).seconds // 60}m" if st.session_state.start_time else "0m"
            st.markdown(f'<div class="health-card"><strong>UPTIME</strong><br><span style="color:#00D1FF">{uptime}</span></div>', unsafe_allow_html=True)
            st.caption("System runtime.", help="How long the app has been running in this session.")
        
        st.markdown("---")
        
        # Motion Analytics (New Chart)
        st.subheader("📈 Motion Activity (Last 60 Minutes)")
        # Update motion history
        if st.session_state.video_processor:
            current_count = st.session_state.video_processor.motion_count
            if "last_total_motion" not in st.session_state:
                st.session_state.last_total_motion = current_count
            
            diff = current_count - st.session_state.last_total_motion
            st.session_state.motion_history.append(diff)
            st.session_state.motion_history = st.session_state.motion_history[-60:]
            st.session_state.last_total_motion = current_count
            
        st.area_chart(st.session_state.motion_history, color="#00D1FF")
        
        st.markdown("---")
        
        # Incident Gallery (New)
        st.subheader("🚨 Incident Snapshot Gallery")
        if st.session_state.incidents:
            cols = st.columns(3)
            for i, incident in enumerate(reversed(st.session_state.incidents[-6:])):
                with cols[i % 3]:
                    st.image(incident["image"], caption=f"Fall @ {incident['time']}", use_container_width=True)
                    st.caption(f"Status: {incident['event']}")
        else:
            st.info("No safety incidents recorded. System is operating normally.")
            
        st.markdown("---")
        st.subheader("📋 Recent Activity Logs")
        if st.session_state.announcements:
            for ann in reversed(st.session_state.announcements[-5:]):
                st.markdown(f"""
                <div style="background:{var('--glass-bg')}; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid #00D1FF;">
                    <strong>{ann['user']}</strong> <small>({ann['time']})</small><br>
                    {ann['text']}
                </div>
                """, unsafe_allow_html=True)
# Cleanup on app close
@atexit.register
def cleanup():
    if "reminder_system" in st.session_state:
        st.session_state.reminder_system.stop()
    if 'db_conn' in locals() and db_conn:
        db_conn.close()

# Initialize all new feature systems
if st.session_state.get("vital_tracker") is None:
    st.session_state.vital_tracker = VitalSignsTracker(db_conn, db_available)

if st.session_state.get("med_manager") is None:
    st.session_state.med_manager = MedicationManager(db_conn, db_available)

if st.session_state.get("geo_system") is None:
    st.session_state.geo_system = GeofencingSystem(db_conn, db_available)

if st.session_state.get("emergency") is None:
    st.session_state.emergency = EmergencySystem(db_conn, db_available)

if st.session_state.get("activity") is None:
    st.session_state.activity = ActivityRecognition(db_conn, db_available)

if st.session_state.get("nutrition") is None:
    st.session_state.nutrition = NutritionTracker(db_conn, db_available)

if st.session_state.get("mood") is None:
    st.session_state.mood = MoodTracker(db_conn, db_available)

if st.session_state.get("smart_home") is None:
    st.session_state.smart_home = SmartHomeController(db_conn, db_available)

if st.session_state.get("dashboard") is None:
    st.session_state.dashboard = CaregiverDashboard(db_conn, db_available)

if st.session_state.get("voice") is None:
    st.session_state.voice = VoiceControl()

if st.session_state.get("accessibility") is None:
    st.session_state.accessibility = AccessibilityManager()

if st.session_state.get("offline") is None:
    st.session_state.offline = OfflineMode()

if st.session_state.get("privacy") is None:
    st.session_state.privacy = PrivacyManager(db_conn, db_available)

# Initialize settings manager (after all systems are initialized)
if st.session_state.get("settings_manager") is None:
    st.session_state.settings_manager = SettingsManager(
        db_conn=db_conn,
        db_available=db_available,
        theme_mgr=st.session_state.theme_mgr,
        language_mgr=st.session_state.language_mgr,
        accessibility=st.session_state.accessibility,
        sync_mgr=st.session_state.sync_mgr,
        error_logger=st.session_state.error_logger,
        audio_system=st.session_state.audio_system
    )

# ==================== PAGE ROUTING ====================
else:
    # Sync Incidents from VideoProcessor
    if st.session_state.video_processor and hasattr(st.session_state.video_processor, 'pending_incidents'):
        while st.session_state.video_processor.pending_incidents:
            new_incid = st.session_state.video_processor.pending_incidents.pop(0)
            st.session_state.incidents.append({
                "time": new_incid["timestamp"],
                "image": new_incid["image"],
                "event": "Fall Detected"
            })
            st.session_state.alert_active = True

    # Check for triggered reminders
    if hasattr(st.session_state, 'triggered_reminders') and st.session_state.triggered_reminders:
        for reminder in st.session_state.triggered_reminders[:]:
            if reminder.get("audio_message"):
                st.session_state.audio_system.play_audio(reminder["audio_message"])
            st.toast(f"🔔 REMINDER: {reminder['title']}\n{reminder['message']}", icon="⏰")
            st.session_state.announcements.append({
                "user": "REMINDER SYSTEM",
                "text": f"Reminder: {reminder['title']} - {reminder['message']}",
                "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"),
                "type": "reminder"
            })
        st.session_state.triggered_reminders = []
    
    # Sidebar Navigation - Fixed to prevent darkening
    st.sidebar.markdown(f"**👤 {st.session_state.current_user}**")
    st.sidebar.markdown("---")
    
    # Collect all pages
    all_pages = {
        "🔍 MONITOR": ["🏠 Home", "🎥 CCTV", "📹 Flask Video"],
        "💬 COMMUNICATE": ["🎤 Intercom", "💬 Chat", "📢 Announce"],
        "❤️ HEALTH": ["❤️ Vital Signs", "💊 Medications", "😊 Mood & Mental"],
        "🍽️ LIFESTYLE": ["🍽️ Nutrition", "🚶 Activity"],
        "🛡️ EMERGENCY": ["🚨 Emergency", "📍 Geofencing", "🏠 Smart Home"],
        "📊 ANALYTICS": ["👨‍⚕️ Caregiver", "🎤 Voice Control", "🔒 Privacy"],
    }
    
    # Render sidebar with selectbox instead of buttons
    for category, pages in all_pages.items():
        st.sidebar.caption(category)
        for page in pages:
            col1, col2 = st.sidebar.columns([0.9, 0.1])
            with col1:
                if st.sidebar.button(page, use_container_width=True, 
                                    type="primary" if st.session_state.current_page == page else "secondary", 
                                    key=f"nav_{page}"):
                    st.session_state.current_page = page
    
    # Settings button
    st.sidebar.caption("⚙️ SETTINGS")
    if st.sidebar.button("⚙️ Settings", use_container_width=True, 
                        type="primary" if st.session_state.current_page == "⚙️ Settings" else "secondary", 
                        key="nav_settings"):
        st.session_state.current_page = "⚙️ Settings"
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Status")
    
    if st.session_state.video_processor:
        st.sidebar.metric("Motion Events", st.session_state.video_processor.motion_count)
    
    if st.session_state.reminder_system:
        pending_reminders = len(st.session_state.reminder_system.get_pending_reminders())
        st.sidebar.metric("Active Reminders", pending_reminders)
    else:
        st.sidebar.metric("Active Reminders", 0)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="nav_logout"):
        if st.session_state.reminder_system:
            st.session_state.reminder_system.stop()
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.current_page = "🎥 CCTV"
        st.rerun()
    
    # ==================== PAGE HANDLERS ====================
    
    # VITAL SIGNS PAGE
    if st.session_state.current_page == "❤️ Vital Signs":
        st.markdown("<h2 style='color:#FF5733;'>❤️ VITAL SIGNS MONITORING</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📊 Log Vitals", "📈 History", "⚠️ Alerts"])
        
        with tab1:
            st.subheader("Log Vital Signs")
            col1, col2 = st.columns(2)
            with col1:
                vital_type = st.selectbox("Vital Type", ["heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic", "temperature", "blood_oxygen"], key="vital_type_select")
                value = st.number_input("Value", min_value=0.0, max_value=300.0, key="vital_value_input")
            with col2:
                units = {"heart_rate": "bpm", "blood_pressure_systolic": "mmHg", "blood_pressure_diastolic": "mmHg", "temperature": "°C", "blood_oxygen": "%"}
                unit = units.get(vital_type, "")
                st.metric("Unit", unit)
            
            if st.button("✅ Record Vital Sign", use_container_width=True, type="primary", key="vital_record"):
                st.session_state.vital_tracker.add_vital_sign(st.session_state.current_user, vital_type, value, unit)
                st.success(f"✅ {vital_type}: {value} {unit} recorded!")
        
        with tab2:
            st.subheader("Vital Signs History")
            vitals = st.session_state.vital_tracker.get_vital_signs(st.session_state.current_user, days=7)
            if vitals:
                for vital_type, value, unit, timestamp in vitals:
                    st.write(f"**{vital_type}**: {value} {unit} @ {timestamp}")
            else:
                st.info("No vital signs recorded yet")
        
        with tab3:
            st.subheader("Abnormal Readings Alert")
            alerts = st.session_state.vital_tracker.check_abnormal_readings(st.session_state.current_user)
            if alerts:
                for alert in alerts:
                    st.warning(f"⚠️ {alert['vital']}: {alert['value']} {alert['unit']} (Abnormal)")
            else:
                st.success("✅ All vital signs are normal!")
    
    # MEDICATIONS PAGE
    elif st.session_state.current_page == "💊 Medications":
        st.markdown("<h2 style='color:#FF5733;'>💊 MEDICATION MANAGEMENT</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Medication", "📋 Active Meds", "✅ Log Taken", "📊 Compliance"])
        
        with tab1:
            st.subheader("Add New Medication")
            name = st.text_input("Medication Name", key="med_name_input")
            dosage = st.text_input("Dosage (e.g., 100mg)", key="med_dosage_input")
            frequency = st.selectbox("Frequency", ["once", "daily", "twice daily", "three times daily"], key="med_freq_select")
            start_date = st.date_input("Start Date", key="med_start_date")
            end_date = st.date_input("End Date (optional)", key="med_end_date")
            notes = st.text_area("Notes", key="med_notes_area")
            
            if st.button("✅ Add Medication", use_container_width=True, type="primary", key="med_add"):
                st.session_state.med_manager.add_medication(st.session_state.current_user, name, dosage, frequency, start_date, end_date, notes)
                st.success(f"✅ {name} added!")
        
        with tab2:
            st.subheader("Active Medications")
            meds = st.session_state.med_manager.get_active_medications(st.session_state.current_user)
            if meds:
                for med in meds:
                    st.write(f"**{med[0]}** - {med[1]} {med[2]}")
                    st.caption(f"Notes: {med[4] if med[4] else 'None'}")
            else:
                st.info("No active medications")
        
        with tab3:
            st.subheader("Log Medication Taken")
            meds = st.session_state.med_manager.get_active_medications(st.session_state.current_user)
            if meds:
                med_names = [m[0] for m in meds]
                selected_med = st.selectbox("Select Medication", med_names, key="med_select_taken")
                if st.button("✅ Mark as Taken", use_container_width=True, type="primary", key="med_taken"):
                    st.session_state.med_manager.log_medication_taken(st.session_state.current_user, selected_med)
                    st.success(f"✅ {selected_med} marked as taken!")
            else:
                st.info("No medications to log")
        
        with tab4:
            st.subheader("Medication Compliance")
            compliance = st.session_state.med_manager.get_medication_compliance(st.session_state.current_user)
            st.metric("Compliance Rate (7 days)", f"{compliance:.1f}%")
            refills = st.session_state.med_manager.check_refill_needed(st.session_state.current_user)
            if refills:
                st.warning("⚠️ Medications needing refill:")
                for refill in refills:
                    st.write(f"- {refill['medication']} ({refill['days_left']} days left)")
    
    # MOOD PAGE
    elif st.session_state.current_page == "😊 Mood & Mental":
        st.markdown("<h2 style='color:#FF5733;'>😊 MOOD & MENTAL HEALTH</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["😊 Daily Check-in", "📈 Trends", "🧠 Cognitive Games"])
        
        with tab1:
            st.subheader("Daily Mood Check-in")
            mood_emoji = st.selectbox("How are you feeling?", ["😄", "😊", "😐", "😔", "😢"], key="mood_emoji_select")
            mood_text = st.selectbox("Mood", ["Very Happy", "Happy", "Neutral", "Sad", "Very Sad"], key="mood_text_select")
            notes = st.text_area("Any notes?", key="mood_notes_area")
            
            if st.button("✅ Log Mood", use_container_width=True, type="primary", key="mood_log"):
                st.session_state.mood.log_mood(st.session_state.current_user, mood_emoji, mood_text, notes)
                st.success("✅ Mood logged!")
        
        with tab2:
            st.subheader("Mood Trends")
            trends = st.session_state.mood.get_mood_trends(st.session_state.current_user)
            if trends:
                st.metric("Trend", trends.get("trend", "N/A"))
                st.metric("Average Mood", f"{trends.get('average_mood', 0)}/5")
                if trends.get("mood_scores"):
                    st.line_chart(trends["mood_scores"])
                else:
                    st.info("No mood data available yet")
            else:
                st.info("No mood trends available")
        
        with tab3:
            st.subheader("Cognitive Games")
            games = st.session_state.mood.get_cognitive_games()
            for game in games:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{game['name']}** - {game['description']}")
                    st.caption(f"Difficulty: {game['difficulty']} | Duration: {game['duration_minutes']}min")
                with col2:
                    if st.button("Play", key=f"game_{game['name']}"):
                        st.info(f"Starting {game['name']}...")
    
    # NUTRITION PAGE
    elif st.session_state.current_page == "🍽️ Nutrition":
        st.markdown("<h2 style='color:#FF5733;'>🍽️ NUTRITION TRACKING</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🍽️ Log Meal", "💧 Water Intake", "📊 Daily Analysis"])
        
        with tab1:
            st.subheader("Log Meal")
            meal_name = st.text_input("Meal Name (e.g., Breakfast)", key="nutrition_meal_name")
            food_items = st.multiselect("Food Items", ["apple", "banana", "chicken", "rice", "broccoli", "milk", "egg", "bread"], key="nutrition_food_items")
            if st.button("✅ Log Meal", use_container_width=True, type="primary", key="nutrition_meal"):
                st.session_state.nutrition.log_meal(st.session_state.current_user, meal_name, food_items)
                st.success(f"✅ {meal_name} logged!")
        
        with tab2:
            st.subheader("Water Intake")
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount (ml)", min_value=100, max_value=1000, value=250, step=50, key="nutrition_water_amount")
            with col2:
                if st.button("✅ Log Water", use_container_width=True, type="primary", key="nutrition_water"):
                    st.session_state.nutrition.log_water_intake(st.session_state.current_user, amount)
                    st.success(f"✅ {amount}ml logged!")
            daily_water = st.session_state.nutrition.get_daily_water_intake(st.session_state.current_user)
            st.metric("Today's Water Intake", f"{daily_water}ml / 2000ml")
            st.progress(min(daily_water / 2000, 1.0))
        
        with tab3:
            st.subheader("Daily Nutritional Analysis")
            nutrition = st.session_state.nutrition.get_daily_nutrition(st.session_state.current_user)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Calories", f"{nutrition['calories']:.0f}")
            with col2:
                st.metric("Protein", f"{nutrition['protein']:.1f}g")
            with col3:
                st.metric("Carbs", f"{nutrition['carbs']:.1f}g")
            with col4:
                st.metric("Fat", f"{nutrition['fat']:.1f}g")
    
    # ACTIVITY PAGE
    elif st.session_state.current_page == "🚶 Activity":
        st.markdown("<h2 style='color:#FF5733;'>🚶 ACTIVITY TRACKING</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📝 Log Activity", "📊 Summary", "⚠️ Alerts"])
        
        with tab1:
            st.subheader("Log Activity")
            activity_type = st.selectbox("Activity Type", ["walking", "running", "sitting", "sleeping", "exercise"], key="activity_type_select")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30, key="activity_duration_input")
            if st.button("✅ Log Activity", use_container_width=True, type="primary", key="activity_log"):
                st.session_state.activity.log_activity(st.session_state.current_user, activity_type, duration)
                st.success(f"✅ {activity_type} for {duration}min logged!")
        
        with tab2:
            st.subheader("Activity Summary (Last 7 Days)")
            summary = st.session_state.activity.get_activity_summary(st.session_state.current_user, days=7)
            if summary:
                for activity_type, count, total_minutes in summary:
                    st.write(f"**{activity_type}**: {count} times, {total_minutes}min total")
            else:
                st.info("No activities logged")
        
        with tab3:
            st.subheader("Activity Alerts")
            inactivity = st.session_state.activity.detect_unusual_inactivity(st.session_state.current_user)
            if inactivity.get("inactive"):
                st.warning(f"⚠️ {inactivity.get('alert', 'Unusual inactivity detected')}")
            else:
                st.success(f"✅ Active - {inactivity.get('hours_inactive', 0):.1f}h since last activity")
    
    # EMERGENCY PAGE
    elif st.session_state.current_page == "🚨 Emergency":
        st.markdown("<h2 style='color:#FF5733;'>🚨 EMERGENCY SYSTEM</h2>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["➕ Add Contact", "📞 Contacts", "🆘 SOS"])
        
        with tab1:
            st.subheader("Add Emergency Contact")
            name = st.text_input("Contact Name", key="emergency_name_input")
            phone = st.text_input("Phone Number", key="emergency_phone_input")
            priority = st.number_input("Priority (1=highest)", min_value=1, max_value=10, value=1, key="emergency_priority_input")
            relation = st.text_input("Relation (e.g., Daughter)", key="emergency_relation_input")
            if st.button("✅ Add Contact", use_container_width=True, type="primary", key="emergency_add"):
                st.session_state.emergency.add_emergency_contact(st.session_state.current_user, name, phone, priority, relation)
                st.success(f"✅ {name} added!")
        
        with tab2:
            st.subheader("Emergency Contacts")
            contacts = st.session_state.emergency.get_emergency_contacts(st.session_state.current_user)
            if contacts:
                for contact in contacts:
                    st.write(f"**{contact[0]}** ({contact[3]})")
                    st.caption(f"📞 {contact[1]} | Priority: {contact[2]}")
            else:
                st.info("No emergency contacts added")
        
        with tab3:
            st.subheader("🆘 SOS Emergency Alert")
            st.warning("⚠️ This will immediately alert all emergency contacts!")
            if st.button("🚨 TRIGGER SOS", use_container_width=True, type="primary", key="emergency_sos"):
                results = st.session_state.emergency.trigger_sos(st.session_state.current_user, 3.1357, 101.6880)
                st.success("✅ SOS triggered!")
    
    # GEOFENCING PAGE
    elif st.session_state.current_page == "📍 Geofencing":
        st.markdown("<h2 style='color:#FF5733;'>📍 GEOFENCING & LOCATION</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["➕ Create Safe Zone", "📍 Location History"])
        
        with tab1:
            st.subheader("Create Safe Zone")
            zone_name = st.text_input("Zone Name (e.g., Home)", key="geo_zone_name_input")
            lat = st.number_input("Latitude", value=3.1357, key="geo_lat_input")
            lon = st.number_input("Longitude", value=101.6880, key="geo_lon_input")
            radius = st.number_input("Radius (meters)", min_value=50, max_value=5000, value=500, key="geo_radius_input")
            if st.button("✅ Create Zone", use_container_width=True, type="primary", key="geo_zone"):
                st.session_state.geo_system.create_safe_zone(st.session_state.current_user, zone_name, lat, lon, radius)
                st.success(f"✅ {zone_name} created!")
        
        with tab2:
            st.subheader("Safe Zones")
            zones = st.session_state.geo_system.get_safe_zones(st.session_state.current_user)
            if zones:
                for zone in zones:
                    st.write(f"**{zone[0]}** - {zone[3]}m radius")
            else:
                st.info("No safe zones created")
    
    # SMART HOME PAGE
    elif st.session_state.current_page == "🏠 Smart Home":
        st.markdown("<h2 style='color:#FF5733;'>🏠 SMART HOME CONTROL</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["➕ Add Device", "⚠️ Safety Alerts"])
        
        with tab1:
            st.subheader("Add Smart Device")
            device_id = st.text_input("Device ID", key="smart_device_id_input")
            device_name = st.text_input("Device Name", key="smart_device_name_input")
            device_type = st.selectbox("Device Type", ["light", "thermostat", "lock", "stove", "door", "water_sensor"], key="smart_device_type_select")
            ip_address = st.text_input("IP Address", key="smart_device_ip_input")
            if st.button("✅ Add Device", use_container_width=True, type="primary", key="smart_device"):
                st.session_state.smart_home.add_device(device_id, device_name, device_type, ip_address, 80)
                st.success(f"✅ {device_name} added!")
        
        with tab2:
            st.subheader("Safety Alerts")
            stove_alerts = st.session_state.smart_home.detect_stove_left_on()
            if stove_alerts:
                for alert in stove_alerts:
                    st.warning(f"🚨 {alert['alert']}")
            door_alerts = st.session_state.smart_home.detect_door_window_open()
            if door_alerts:
                for alert in door_alerts:
                    st.warning(f"⚠️ {alert['alert']}")
            water_alerts = st.session_state.smart_home.detect_water_leak()
            if water_alerts:
                for alert in water_alerts:
                    st.error(f"🚨 {alert['alert']}")
            if not stove_alerts and not door_alerts and not water_alerts:
                st.success("✅ All systems normal")
    
    # CAREGIVER DASHBOARD PAGE
    elif st.session_state.current_page == "👨‍⚕️ Caregiver":
        st.markdown("<h2 style='color:#00D1FF;'>👨‍⚕️ CAREGIVER DASHBOARD</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📊 Daily Summary", "📈 Trends"])
        
        with tab1:
            st.subheader("Daily Summary")
            summary = st.session_state.dashboard.get_daily_summary(st.session_state.current_user)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Activities", summary.get("activities", 0))
            with col2:
                st.metric("Meals", summary.get("meals", 0))
            with col3:
                st.metric("Water (ml)", summary.get("water_intake", 0))
            with col4:
                mood_data = summary.get("mood")
                mood_emoji = mood_data.get("emoji") if mood_data else "N/A"
                st.metric("Mood", mood_emoji)
            
            st.metric("Medication Compliance", f"{summary.get('medication_compliance', 0):.1f}%")
        
        with tab2:
            st.subheader("Health Trends (30 Days)")
            trends = st.session_state.dashboard.get_health_trends(st.session_state.current_user, days=30)
            if trends and trends.get("activity_trend"):
                st.write("**Activity Trend**")
                st.bar_chart([a[1] for a in trends["activity_trend"]])
            else:
                st.info("No health trends available yet")
    
    # VOICE CONTROL PAGE
    elif st.session_state.current_page == "🎤 Voice Control":
        st.markdown("<h2 style='color:#00D1FF;'>🎤 VOICE CONTROL</h2>", unsafe_allow_html=True)
        st.info("Available voice commands:")
        commands = st.session_state.voice.get_available_commands()
        for cmd in commands:
            st.write(f"- {cmd}")
        st.markdown("---")
        voice_input = st.text_input("Enter command:")
        if voice_input:
            result = st.session_state.voice.process_voice_command(voice_input)
            st.write(f"**Response**: {result['message']}")
    
    # PRIVACY PAGE
    elif st.session_state.current_page == "🔒 Privacy":
        st.markdown("<h2 style='color:#00D1FF;'>🔒 PRIVACY & DATA</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Permissions", "📥 Export Data"])
        
        with tab1:
            st.subheader("Access Permissions")
            caregiver = st.text_input("Caregiver Username", key="privacy_caregiver_input")
            permissions = {
                "camera": st.checkbox("Camera Access", key="privacy_camera_check"),
                "messages": st.checkbox("Messages Access", key="privacy_messages_check"),
                "health": st.checkbox("Health Data Access", key="privacy_health_check"),
            }
            if st.button("✅ Set Permissions", use_container_width=True, type="primary", key="privacy_perms"):
                st.session_state.privacy.set_access_permissions(st.session_state.current_user, caregiver, permissions)
                st.success("Permissions updated!")
        
        with tab2:
            st.subheader("Export Your Data (GDPR)")
            if st.button("📥 Export Data", use_container_width=True, type="primary", key="privacy_export"):
                export = st.session_state.privacy.export_user_data(st.session_state.current_user)
                st.json(export)
    
    # SETTINGS PAGE - Consolidated
    elif st.session_state.current_page == "⚙️ Settings":
        # Use the unified SettingsManager to render all settings
        st.session_state.settings_manager.render_settings_page(
            current_user=st.session_state.current_user,
            timezone=TIMEZONE,
            video_processor=st.session_state.video_processor,
            reminder_system=st.session_state.reminder_system,
            cache=st.session_state.cache,
            start_time=st.session_state.start_time
        )


# ==================== APPLY NAVIGATION ====================
# Single rerun to apply page changes without darkening sidebar
if "page_changed" not in st.session_state:
    st.session_state.page_changed = False

# Check if page changed and rerun once
if st.session_state.current_page != st.session_state.get("last_page"):
    st.session_state.last_page = st.session_state.current_page
    st.rerun()


# ==================== DATABASE SETUP ====================
# Moved to Settings page - no longer needed in sidebar

# Cleanup on app close
@atexit.register
def cleanup():
    if "reminder_system" in st.session_state:
        st.session_state.reminder_system.stop()
    if db_conn:
        db_conn.close()
