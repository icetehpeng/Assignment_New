import streamlit as st
import mysql.connector
from pyngrok import ngrok
from datetime import datetime, timedelta
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import atexit
import time

# Import custom modules
from config import NGROK_AUTH_TOKEN, NGROK_ADDR, TIMEZONE
from database import get_db_connection, create_tables
from audio_system import AudioSystem
from reminder_system import ReminderSystem
from video_processor import VideoProcessor
from chat_manager import ChatManager
from io import BytesIO

# ------------------ NGROK (FIXED) ------------------
def start_ngrok():
    try:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        ngrok.kill()
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
    st.session_state.current_page = "🎥 CCTV"
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

# Initialize systems
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

# ------------------ CUSTOM STYLES ------------------
def inject_custom_css():
    st.markdown("""
    <style>
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        max-width: 80%;
        line-height: 1.4;
        font-size: 0.95rem;
    }
    .chat-bubble-user {
        background-color: #0078FF;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 2px;
    }
    .chat-bubble-assistant {
        background-color: #E9E9EB;
        color: black;
        align-self: flex-start;
        border-bottom-left-radius: 2px;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .system-health-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ------------------ TITLE ------------------
st.markdown(
    "<h1 style='text-align:center; color:#4B0082;'>🏠 SmartHome CCTV + Intercom</h1>",
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
                            st.session_state.current_page = "🎥 CCTV"
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
                    st.session_state.current_page = "🎥 CCTV"
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
    st.sidebar.markdown(f"**👤 User: {st.session_state.current_user}**")
    st.sidebar.markdown("---")
    
    # Navigation buttons
    if st.sidebar.button("🎥 CCTV", use_container_width=True, type="primary" if st.session_state.current_page == "🎥 CCTV" else "secondary"):
        st.session_state.current_page = "🎥 CCTV"
        st.rerun()
    
    if st.sidebar.button("🎤 Live Talk", use_container_width=True, type="primary" if st.session_state.current_page == "🎤 Live Talk" else "secondary"):
        st.session_state.current_page = "🎤 Live Talk"
        st.rerun()
    
    if st.sidebar.button("🔊 Audio Tools", use_container_width=True, type="primary" if st.session_state.current_page == "🔊 Audio Tools" else "secondary"):
        st.session_state.current_page = "🔊 Audio Tools"
        st.rerun()
    
    if st.sidebar.button("📢 Announce", use_container_width=True, type="primary" if st.session_state.current_page == "📢 Announce" else "secondary"):
        st.session_state.current_page = "📢 Announce"
        st.rerun()
    
    if st.sidebar.button("⏰ Reminders", use_container_width=True, type="primary" if st.session_state.current_page == "⏰ Reminders" else "secondary"):
        st.session_state.current_page = "⏰ Reminders"
        st.rerun()
    
    if st.sidebar.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == "📊 Dashboard" else "secondary"):
        st.session_state.current_page = "📊 Dashboard"
        st.rerun()
    
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
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        if st.session_state.reminder_system:
            st.session_state.reminder_system.stop()
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.current_page = "🎥 CCTV"
        st.rerun()
    
    # ------------------ CCTV PAGE ------------------
    if st.session_state.current_page == "🎥 CCTV":
        st.markdown(f"<h2 style='color:#FF5733;'>📹 CCTV MONITORING</h2>", unsafe_allow_html=True)
        
        current_time = datetime.now(TIMEZONE).strftime("%H:%M:%S")
        st.metric("Current Time", current_time)
        
        st.markdown("---")
        st.subheader("🎥 Live Camera Feed")
        
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

        # Quick Talk Section
        st.markdown("---")
        st.subheader("🎤 Quick Talk")
        
        col1, col2 = st.columns(2)
        with col1:
            talk_duration = st.slider("Talk duration (seconds)", 3, 20, 10)
            if st.button("🎤 PRESS TO TALK", use_container_width=True, type="primary"):
                with st.spinner(f"Recording for {talk_duration} seconds..."):
                    audio = st.session_state.audio_system.record_audio(talk_duration)
                    if audio:
                        st.session_state.last_audio_message = audio
                        timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                        st.session_state.announcements.append({
                            "user": st.session_state.current_user,
                            "text": f"Quick talk ({talk_duration}s)",
                            "time": timestamp,
                            "audio": audio,
                            "type": "quick"
                        })
                        st.success(f"✅ Message recorded!")
                        st.session_state.audio_system.play_audio(audio)
        
        with col2:
            if st.session_state.last_audio_message:
                if st.button("🔊 PLAY LAST MESSAGE", use_container_width=True):
                    st.session_state.audio_system.play_audio(st.session_state.last_audio_message)
            else:
                st.info("No messages recorded yet")
    
    # ------------------ LIVE TALK PAGE ------------------
    elif st.session_state.current_page == "🎤 Live Talk":
        st.markdown(f"<h2 style='color:#FF5733;'>🎤 LIVE TALK INTERCOM</h2>", unsafe_allow_html=True)
        st.info("""
        **Live Talk Features:**
        - 🎤 **Voice Recorder** - Record and play back your voice
        - 💬 **Live Chat** - Send text and voice messages to other users
        """)
        
        st.subheader("🎤 Voice Recorder")
        col1, col2 = st.columns(2)
        with col1:
            record_duration = st.slider("Recording time (seconds)", 3, 30, 10)
            if st.button("🎤 PRESS & HOLD TO TALK", use_container_width=True, type="primary"):
                with st.spinner(f"Recording for {record_duration} seconds..."):
                    audio = st.session_state.audio_system.record_audio(record_duration)
                    if audio:
                        st.session_state.last_audio_message = audio
                        timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")
                        st.session_state.announcements.append({
                            "user": st.session_state.current_user,
                            "text": f"Live talk ({record_duration}s)",
                            "time": timestamp,
                            "audio": audio,
                            "type": "live"
                        })
                        st.success("✅ Recording complete!")
                        st.session_state.audio_system.play_audio(audio)
        
        with col2:
            st.write(" ") # Padding
            st.write(" ") # Padding
            if st.session_state.last_audio_message:
                if st.button("▶️ PLAY RECORDING", use_container_width=True):
                    st.session_state.audio_system.play_audio(st.session_state.last_audio_message)
            else:
                st.info("No recording available")
        
        st.markdown("---")
        st.subheader("💬 Chat with Users")
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
                
                # Auto-refresh toggle
                r_col1, r_col2 = st.columns([1, 1])
                with r_col1:
                    auto_refresh = st.toggle("🔄 Streaming", value=True)
                with r_col2:
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
                                    st.rerun()
                
                if auto_refresh:
                    time.sleep(5)
                    st.rerun()
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

    # ------------------ ANNOUNCE PAGE ------------------
    elif st.session_state.current_page == "📢 Announce":
        st.markdown(f"<h2 style='color:#FF5733;'>📢 ANNOUNCEMENT SYSTEM</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎤 Record Announcement")
            message_text = st.text_area("Announcement text", value="Attention everyone! Please gather in the living room.", height=100)
            record_duration = st.slider("Duration (seconds)", 5, 60, 15)
            if st.button("🎤 RECORD ANNOUNCEMENT", use_container_width=True, type="primary"):
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
        st.markdown(f"<h2 style='color:#FF5733;'>⏰ SMART REMINDERS</h2>", unsafe_allow_html=True)
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

    # ------------------ DASHBOARD PAGE ------------------
    elif st.session_state.current_page == "📊 Dashboard":
        st.markdown(f"<h2 style='color:#FF5733;'>📊 SYSTEM DASHBOARD</h2>", unsafe_allow_html=True)
        
        # System Health Section (4)
        st.subheader("🌐 System Health")
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        with h_col1:
            ngrok_status = "✅ ONLINE" if "http" in str(st.session_state.public_url) else "❌ OFFLINE"
            st.markdown(f'<div class="system-health-card"><strong>NGROK</strong><br>{ngrok_status}</div>', unsafe_allow_html=True)
        with h_col2:
            db_status = "✅ CONNECTED" if db_available else "❌ DISCONNECTED"
            st.markdown(f'<div class="system-health-card"><strong>Database</strong><br>{db_status}</div>', unsafe_allow_html=True)
        with h_col3:
            audio_status = "✅ READY" if st.session_state.audio_system else "❌ ERROR"
            st.markdown(f'<div class="system-health-card"><strong>Audio</strong><br>{audio_status}</div>', unsafe_allow_html=True)
        with h_col4:
            uptime = f"{(datetime.now(TIMEZONE) - st.session_state.start_time).seconds // 60}m" if st.session_state.start_time else "0m"
            st.markdown(f'<div class="system-health-card"><strong>Uptime</strong><br>{uptime}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📋 Status Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Reminders", len(st.session_state.reminder_system.get_pending_reminders()))
        with col2:
            st.metric("Motion Events", st.session_state.video_processor.motion_count if st.session_state.video_processor else 0)
        with col3:
            st.metric("Announcements", len(st.session_state.announcements))
        with col4:
            st.metric("Uptime", uptime)
        
        st.markdown("---")
        st.subheader("🎤 Quick Talk")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if st.button("🎤 QUICK RECORD & PLAY", use_container_width=True, type="primary"):
                audio = st.session_state.audio_system.record_audio(5)
                if audio:
                    st.session_state.announcements.append({"user": st.session_state.current_user, "text": "Quick dashboard message", "time": datetime.now(TIMEZONE).strftime("%H:%M:%S"), "audio": audio, "type": "dashboard"})
                    st.session_state.audio_system.play_audio(audio)
                    st.success("Sent!")
        with t_col2:
            if st.session_state.last_audio_message:
                if st.button("🔊 PLAY LAST MESSAGE", use_container_width=True): st.session_state.audio_system.play_audio(st.session_state.last_audio_message)

        st.markdown("---")
        st.subheader("📋 Recent Activity")
        if st.session_state.announcements:
            for ann in reversed(st.session_state.announcements[-10:]):
                st.write(f"**{ann['user']}** ({ann['time']}): {ann['text'][:100]}...")
                st.markdown("---")

# ------------------ DATABASE SETUP ------------------
with st.sidebar.expander("🔧 System Settings"):
    if st.button("🔄 Force Reconnect Database", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    if st.button("🛠️ Create Tables Automatically", use_container_width=True):
        if db_available:
            success, msg = create_tables(db_conn)
            if success: st.success(msg)
            else: st.error(msg)
        else: st.error("❌ Database not available")

    st.markdown("---")
    if st.button("🚪 LOG OUT", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Cleanup on app close
@atexit.register
def cleanup():
    if "reminder_system" in st.session_state:
        st.session_state.reminder_system.stop()
    if 'db_conn' in locals() and db_conn:
        db_conn.close()
