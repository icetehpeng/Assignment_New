import streamlit as st
import mysql.connector
from pyngrok import ngrok
import cv2
import numpy as np
import time
from datetime import datetime, timedelta
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import pyaudio
import wave
import queue
import threading
from io import BytesIO
import schedule
import json
import pytz
from zoneinfo import ZoneInfo
from collections import deque
import io
import sys

# ------------------ NGROK ------------------
@st.cache_resource
def start_ngrok():
    ngrok.set_auth_token("38eCDcvqCWaYKg6rTJXMbvl0nPw_4xHQedFTBMF9iunkVjxHd")
    return ngrok.connect(8501)

public_url = start_ngrok()
st.sidebar.success("🌐 Public Link")
st.sidebar.write(public_url)

# ------------------ DATABASE CONNECTION ------------------
def get_db_connection():
    """Try to connect to MySQL database"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1234",
            database="login_system"
        )
        return conn, True
    except mysql.connector.Error as e:
        st.sidebar.warning(f"⚠️ MySQL not available: {e}")
        return None, False

# Initialize database
db_conn, db_available = get_db_connection()

# ------------------ SIMPLE AUDIO SYSTEM ------------------
class SimpleAudioSystem:
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.audio_buffer = deque(maxlen=10)
        
    def record(self, duration=5):
        """Record audio for specified duration"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            for _ in range(0, int(self.sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to WAV buffer
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            wav_buffer.seek(0)
            return wav_buffer
            
        except Exception as e:
            st.error(f"❌ Recording failed: {e}")
            return None
    
    def play(self, audio_bytes):
        """Play audio from bytes"""
        try:
            # Import pyaudio for playback
            import pyaudio
            
            if isinstance(audio_bytes, BytesIO):
                audio_bytes.seek(0)
                audio_data = audio_bytes.read()
            else:
                audio_data = audio_bytes
            
            p = pyaudio.PyAudio()
            
            # Open stream for playback
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Playback failed: {e}")
            return False
    
    def generate_beep(self, frequency=440, duration=1.0):
        """Generate a beep sound"""
        try:
            samples = int(self.sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(frequency * t * 2 * np.pi)
            
            # Convert to 16-bit PCM
            audio = (tone * 32767).astype(np.int16)
            
            # Create WAV file in memory
            wav_buffer = BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio.tobytes())
            
            wav_buffer.seek(0)
            return wav_buffer
            
        except Exception as e:
            st.error(f"❌ Beep generation failed: {e}")
            return None

# ------------------ REMINDER SYSTEM ------------------
class ReminderSystem:
    def __init__(self):
        self.reminders = []
        self.active_reminders = []
        self.reminder_thread = None
        self.running = False
        self.timezone = ZoneInfo("Asia/Kuala_Lumpur")
        
    def add_reminder(self, title, message, trigger_time, repeat="once", audio_message=None):
        """Add a new reminder"""
        reminder = {
            "id": len(self.reminders) + 1,
            "title": title,
            "message": message,
            "trigger_time": trigger_time,
            "repeat": repeat,
            "audio_message": audio_message,
            "created_at": datetime.now(self.timezone),
            "status": "pending",
            "triggered": False
        }
        
        self.reminders.append(reminder)
        
        # Add to active reminders if not triggered
        if trigger_time > datetime.now(self.timezone):
            self.active_reminders.append(reminder)
        
        return reminder
    
    def check_reminders(self):
        """Check and trigger reminders"""
        current_time = datetime.now(self.timezone)
        triggered = []
        
        for reminder in self.active_reminders[:]:
            if reminder["trigger_time"] <= current_time and not reminder["triggered"]:
                # Trigger this reminder
                reminder["triggered"] = True
                reminder["triggered_at"] = current_time
                reminder["status"] = "triggered"
                triggered.append(reminder)
                
                # Handle repeat
                if reminder["repeat"] == "daily":
                    # Schedule for next day
                    new_time = reminder["trigger_time"] + timedelta(days=1)
                    new_reminder = reminder.copy()
                    new_reminder["trigger_time"] = new_time
                    new_reminder["triggered"] = False
                    new_reminder["status"] = "pending"
                    self.active_reminders.append(new_reminder)
                elif reminder["repeat"] == "hourly":
                    # Schedule for next hour
                    new_time = reminder["trigger_time"] + timedelta(hours=1)
                    new_reminder = reminder.copy()
                    new_reminder["trigger_time"] = new_time
                    new_reminder["triggered"] = False
                    new_reminder["status"] = "pending"
                    self.active_reminders.append(new_reminder)
        
        # Remove triggered reminders from active list
        self.active_reminders = [r for r in self.active_reminders if not r.get("triggered", False)]
        
        return triggered
    
    def get_pending_reminders(self):
        """Get reminders that are still pending"""
        return [r for r in self.reminders if r["status"] == "pending"]
    
    def get_upcoming_reminders(self, count=5):
        """Get upcoming reminders"""
        pending = self.get_pending_reminders()
        pending.sort(key=lambda x: x["trigger_time"])
        return pending[:count]
    
    def cancel_reminder(self, reminder_id):
        """Cancel a reminder"""
        for reminder in self.reminders:
            if reminder["id"] == reminder_id:
                reminder["status"] = "cancelled"
                self.active_reminders = [r for r in self.active_reminders if r["id"] != reminder_id]
                return True
        return False
    
    def start_background_check(self):
        """Start background thread to check reminders"""
        if not self.running:
            self.running = True
            self.reminder_thread = threading.Thread(target=self._background_check, daemon=True)
            self.reminder_thread.start()
    
    def _background_check(self):
        """Background thread to check reminders"""
        while self.running:
            triggered = self.check_reminders()
            if triggered:
                # Store triggered reminders for UI
                if "triggered_reminders" not in st.session_state:
                    st.session_state.triggered_reminders = []
                st.session_state.triggered_reminders.extend(triggered)
            
            time.sleep(1)  # Check every second
    
    def stop(self):
        """Stop the reminder system"""
        self.running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=1)

# ------------------ VIDEO PROCESSOR ------------------
class VideoProcessor:
    def __init__(self):
        self.previous_frame = None
        self.motion_detected = False
        self.motion_count = 0
        self.last_motion_time = None
        
    def recv(self, frame):
        """Process video frame"""
        img = frame.to_ndarray(format="bgr24")
        
        # Motion detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.previous_frame is None:
            self.previous_frame = gray
        else:
            frame_diff = cv2.absdiff(self.previous_frame, gray)
            thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            self.motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) < 1000:
                    continue
                    
                self.motion_detected = True
                self.motion_count += 1
                self.last_motion_time = datetime.now()
                
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(img, "MOTION", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            self.previous_frame = gray
        
        # Add overlays
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(img, f"LIVE: {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Motions: {self.motion_count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ------------------ SESSION STATE ------------------
# Initialize all session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_page = "🎥 CCTV"  # Track current page
    st.session_state.video_processor = None
    st.session_state.audio_system = None
    st.session_state.reminder_system = None
    st.session_state.motion_alerts = []
    st.session_state.announcements = []
    st.session_state.reminders = []
    st.session_state.triggered_reminders = []
    st.session_state.start_time = None
    st.session_state.last_audio_message = None

# Initialize audio system
if "audio_system" not in st.session_state or st.session_state.audio_system is None:
    st.session_state.audio_system = SimpleAudioSystem()

# Initialize reminder system
if "reminder_system" not in st.session_state or st.session_state.reminder_system is None:
    st.session_state.reminder_system = ReminderSystem()
    st.session_state.reminder_system.start_background_check()

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
                            st.session_state.start_time = datetime.now()
                            
                            # Create tables if they don't exist
                            cursor.execute("""
                                CREATE TABLE IF NOT EXISTS reminders (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    username VARCHAR(50),
                                    title VARCHAR(100),
                                    message TEXT,
                                    trigger_time DATETIME,
                                    repeat_type VARCHAR(20),
                                    audio_data LONGBLOB,
                                    status VARCHAR(20),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """)
                            db_conn.commit()
                            
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
                    st.session_state.start_time = datetime.now()
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
            # Play audio announcement
            if reminder.get("audio_message"):
                if st.session_state.audio_system:
                    st.session_state.audio_system.play(reminder["audio_message"])
            
            # Show alert
            st.toast(f"🔔 REMINDER: {reminder['title']}\n{reminder['message']}", icon="⏰")
            
            # Add to announcements
            st.session_state.announcements.append({
                "user": "REMINDER SYSTEM",
                "text": f"Reminder: {reminder['title']} - {reminder['message']}",
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "reminder"
            })
        
        # Clear triggered reminders
        st.session_state.triggered_reminders = []
    
    # Sidebar Navigation
    st.sidebar.markdown(f"**👤 User: {st.session_state.current_user}**")
    st.sidebar.markdown("---")
    
    # Navigation buttons that update session state
    if st.sidebar.button("🎥 CCTV", use_container_width=True, type="primary" if st.session_state.current_page == "🎥 CCTV" else "secondary"):
        st.session_state.current_page = "🎥 CCTV"
        st.rerun()
    
    if st.sidebar.button("🎤 Live Talk", use_container_width=True, type="primary" if st.session_state.current_page == "🎤 Live Talk" else "secondary"):
        st.session_state.current_page = "🎤 Live Talk"
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
    
    # System Status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Status")
    
    if st.session_state.video_processor:
        st.sidebar.metric("Motion Events", st.session_state.video_processor.motion_count)
    
    if st.session_state.reminder_system:
        pending_reminders = len(st.session_state.reminder_system.get_pending_reminders())
        st.sidebar.metric("Active Reminders", pending_reminders)
    else:
        st.sidebar.metric("Active Reminders", 0)
    
    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        # Stop reminder system
        if st.session_state.reminder_system:
            st.session_state.reminder_system.stop()
        
        # Clear session
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.current_page = "🎥 CCTV"
        st.rerun()
    
    # ------------------ CCTV PAGE ------------------
    if st.session_state.current_page == "🎥 CCTV":
        st.markdown(f"<h2 style='color:#FF5733;'>📹 CCTV MONITORING</h2>", unsafe_allow_html=True)
        
        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("Current Time", current_time)
        
        st.markdown("---")
        
        # Live Camera Feed
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
                if st.session_state.audio_system:
                    with st.spinner(f"Recording for {talk_duration} seconds..."):
                        audio = st.session_state.audio_system.record(talk_duration)
                        
                        if audio:
                            st.session_state.last_audio_message = audio
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            st.session_state.announcements.append({
                                "user": st.session_state.current_user,
                                "text": f"Quick talk ({talk_duration}s)",
                                "time": timestamp,
                                "audio": audio,
                                "type": "quick"
                            })
                            st.success(f"✅ Message recorded!")
                            
                            # Play immediately
                            st.session_state.audio_system.play(audio)
                else:
                    st.error("❌ Audio system not available")
        
        with col2:
            if st.session_state.last_audio_message:
                if st.button("🔊 PLAY LAST MESSAGE", use_container_width=True):
                    if st.session_state.audio_system:
                        st.session_state.audio_system.play(st.session_state.last_audio_message)
                    else:
                        st.error("❌ Audio system not available")
            else:
                st.info("No messages recorded yet")
    
    # ------------------ LIVE TALK PAGE ------------------
    elif st.session_state.current_page == "🎤 Live Talk":
        st.markdown(f"<h2 style='color:#FF5733;'>🎤 LIVE TALK INTERCOM</h2>", unsafe_allow_html=True)
        
        st.info("""
        **Live Talk Features:**
        - 🎤 **Press to talk** - Click button and speak
        - 🔊 **Immediate playback** - Audio plays instantly
        - 💾 **Save messages** - Store important announcements
        - ⚡ **Quick sounds** - Attention and doorbell sounds
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎤 Voice Recorder")
            
            record_duration = st.slider("Recording time (seconds)", 3, 30, 10)
            
            # Big record button
            if st.button("🎤 PRESS & HOLD TO TALK", use_container_width=True, type="primary"):
                if st.session_state.audio_system:
                    with st.spinner(f"Recording for {record_duration} seconds..."):
                        audio = st.session_state.audio_system.record(record_duration)
                        
                        if audio:
                            st.session_state.last_audio_message = audio
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            st.session_state.announcements.append({
                                "user": st.session_state.current_user,
                                "text": f"Live talk ({record_duration}s)",
                                "time": timestamp,
                                "audio": audio,
                                "type": "live"
                            })
                            st.success("✅ Recording complete!")
                            
                            # Play immediately
                            st.session_state.audio_system.play(audio)
                else:
                    st.error("❌ Audio system not available")
            
            st.markdown("---")
            
            # Playback controls
            st.subheader("🔊 Playback")
            
            if st.session_state.last_audio_message:
                if st.button("▶️ PLAY RECORDING", use_container_width=True):
                    if st.session_state.audio_system:
                        st.session_state.audio_system.play(st.session_state.last_audio_message)
                    else:
                        st.error("❌ Audio system not available")
            else:
                st.info("No recording available")
        
        with col2:
            st.subheader("⚡ Quick Sounds")
            
            # Quick sound buttons
            col_sound1, col_sound2 = st.columns(2)
            
            with col_sound1:
                if st.button("📣 ATTENTION", use_container_width=True):
                    if st.session_state.audio_system:
                        beep = st.session_state.audio_system.generate_beep(frequency=880, duration=2.0)
                        if beep:
                            st.session_state.audio_system.play(beep)
                            st.success("Attention sound played!")
                    else:
                        st.error("❌ Audio system not available")
            
            with col_sound2:
                if st.button("🔔 DOORBELL", use_container_width=True):
                    if st.session_state.audio_system:
                        # Create doorbell sound (two tones)
                        beep1 = st.session_state.audio_system.generate_beep(frequency=800, duration=0.5)
                        beep2 = st.session_state.audio_system.generate_beep(frequency=600, duration=0.5)
                        if beep1 and beep2:
                            st.session_state.audio_system.play(beep1)
                            time.sleep(0.5)
                            st.session_state.audio_system.play(beep2)
                            st.success("Doorbell sound played!")
                    else:
                        st.error("❌ Audio system not available")
            
            st.markdown("---")
            
            # Test microphone
            st.subheader("🎚️ Audio Test")
            
            if st.button("🔊 TEST MICROPHONE", use_container_width=True):
                if st.session_state.audio_system:
                    with st.spinner("Testing microphone for 3 seconds..."):
                        test_audio = st.session_state.audio_system.record(3)
                        if test_audio:
                            st.success("✅ Microphone test successful!")
                            st.session_state.audio_system.play(test_audio)
                        else:
                            st.error("❌ Microphone test failed")
                else:
                    st.error("❌ Audio system not available")
        
        # Recent Messages
        st.markdown("---")
        st.subheader("📋 Recent Messages")
        
        if st.session_state.announcements:
            # Show only live talk messages
            live_messages = [msg for msg in st.session_state.announcements if msg['type'] in ['live', 'quick']]
            
            if live_messages:
                for msg in reversed(live_messages[-5:]):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{msg['user']}** ({msg['time']}): {msg['text']}")
                        with col2:
                            if st.button("▶️ Play", key=f"play_{msg['time']}"):
                                if 'audio' in msg and st.session_state.audio_system:
                                    st.session_state.audio_system.play(msg['audio'])
                        st.markdown("---")
            else:
                st.info("No live talk messages yet")
        else:
            st.info("No messages yet. Start talking!")
    
    # ------------------ ANNOUNCE PAGE ------------------
    elif st.session_state.current_page == "📢 Announce":
        st.markdown(f"<h2 style='color:#FF5733;'>📢 ANNOUNCEMENT SYSTEM</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎤 Record Announcement")
            
            message_text = st.text_area(
                "Announcement text",
                value="Attention everyone! Please gather in the living room.",
                height=100
            )
            
            record_duration = st.slider("Duration (seconds)", 5, 60, 15)
            
            if st.button("🎤 RECORD ANNOUNCEMENT", use_container_width=True, type="primary"):
                if st.session_state.audio_system:
                    with st.spinner(f"Recording for {record_duration} seconds..."):
                        audio = st.session_state.audio_system.record(record_duration)
                        
                        if audio:
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            announcement = {
                                "user": st.session_state.current_user,
                                "text": message_text,
                                "time": timestamp,
                                "audio": audio,
                                "type": "announcement"
                            }
                            
                            st.session_state.announcements.append(announcement)
                            st.session_state.last_audio_message = audio
                            st.success(f"✅ Announcement recorded! ({record_duration}s)")
                            
                            # Play immediately
                            st.session_state.audio_system.play(audio)
                else:
                    st.error("❌ Audio system not available")
        
        with col2:
            st.subheader("📢 Quick Announcements")
            
            # Quick announcement buttons
            qa_col1, qa_col2 = st.columns(2)
            
            with qa_col1:
                if st.button("💊 MEDICINE TIME", use_container_width=True):
                    if st.session_state.audio_system:
                        msg = "Time to take your medicine!"
                        beep = st.session_state.audio_system.generate_beep(frequency=440, duration=3.0)
                        if beep:
                            st.session_state.announcements.append({
                                "user": "SYSTEM",
                                "text": msg,
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "audio": beep,
                                "type": "quick"
                            })
                            st.session_state.audio_system.play(beep)
                            st.success("Medicine reminder announced!")
                    else:
                        st.error("❌ Audio system not available")
            
            with qa_col2:
                if st.button("🍽️ MEAL TIME", use_container_width=True):
                    if st.session_state.audio_system:
                        msg = "Meal time! Please come to the dining area."
                        beep = st.session_state.audio_system.generate_beep(frequency=523, duration=3.0)  # C note
                        if beep:
                            st.session_state.announcements.append({
                                "user": "SYSTEM",
                                "text": msg,
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "audio": beep,
                                "type": "quick"
                            })
                            st.session_state.audio_system.play(beep)
                            st.success("Meal reminder announced!")
                    else:
                        st.error("❌ Audio system not available")
            
            st.markdown("---")
            
            # Saved Announcements
            st.subheader("💾 Saved Announcements")
            
            # Filter announcement type messages
            saved_announcements = [a for a in st.session_state.announcements if a['type'] == 'announcement']
            
            if saved_announcements:
                for ann in reversed(saved_announcements[-3:]):
                    st.write(f"**{ann['user']}** ({ann['time']}):")
                    st.write(f"{ann['text'][:100]}...")
                    if st.button("▶️ Play", key=f"play_ann_{ann['time']}"):
                        if 'audio' in ann and st.session_state.audio_system:
                            st.session_state.audio_system.play(ann['audio'])
                    st.markdown("---")
            else:
                st.info("No saved announcements")
    
    # ------------------ REMINDERS PAGE ------------------
    elif st.session_state.current_page == "⏰ Reminders":
        st.markdown(f"<h2 style='color:#FF5733;'>⏰ SMART REMINDERS</h2>", unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["➕ Set New Reminder", "📋 Active Reminders", "🎯 Quick Presets"])
        
        with tab1:
            st.subheader("➕ Set New Reminder")
            
            # Reminder details
            reminder_title = st.text_input("Reminder Title", "Medicine Reminder")
            reminder_message = st.text_area("Reminder Message", "Time to take your medicine! 💊")
            
            # Schedule options
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_type = st.radio(
                    "Schedule Type",
                    ["In X minutes", "Specific Time", "Daily", "Hourly"]
                )
                
                if schedule_type == "In X minutes":
                    minutes = st.number_input("Minutes from now", min_value=1, max_value=1440, value=5)
                    trigger_time = datetime.now() + timedelta(minutes=minutes)
                
                elif schedule_type == "Specific Time":
                    date = st.date_input("Date", datetime.now())
                    time_input = st.time_input("Time", datetime.now().time())
                    trigger_time = datetime.combine(date, time_input)
                
                elif schedule_type == "Daily":
                    time_input = st.time_input("Daily at", datetime.now().time())
                    trigger_time = datetime.combine(datetime.now().date(), time_input)
                    if trigger_time < datetime.now():
                        trigger_time += timedelta(days=1)
                
                elif schedule_type == "Hourly":
                    minute = st.number_input("Minute past each hour", min_value=0, max_value=59, value=0)
                    trigger_time = datetime.now().replace(minute=minute, second=0, microsecond=0)
                    if trigger_time < datetime.now():
                        trigger_time += timedelta(hours=1)
            
            with col2:
                # Audio options
                st.subheader("🔊 Audio Settings")
                
                audio_option = st.radio(
                    "Audio Announcement",
                    ["Record Voice Message", "Beep Sound", "No Audio"]
                )
                
                audio_data = None
                if audio_option == "Record Voice Message":
                    if st.button("🎤 Record Voice"):
                        if st.session_state.audio_system:
                            with st.spinner("Recording for 5 seconds..."):
                                audio_data = st.session_state.audio_system.record(5)
                                if audio_data:
                                    st.success("✅ Voice recorded!")
                                else:
                                    st.error("❌ Recording failed")
                        else:
                            st.error("❌ Audio system not available")
                
                elif audio_option == "Beep Sound":
                    audio_data = st.session_state.audio_system.generate_beep(duration=3.0)
            
            # Repeat option
            repeat_option = "once"
            if schedule_type in ["Daily", "Hourly"]:
                repeat_option = schedule_type.lower()
            else:
                repeat_option = st.selectbox(
                    "Repeat",
                    ["once", "daily", "hourly"]
                )
            
            # Set Reminder Button
            if st.button("✅ SET REMINDER", use_container_width=True, type="primary"):
                # Add reminder to system
                reminder = st.session_state.reminder_system.add_reminder(
                    title=reminder_title,
                    message=reminder_message,
                    trigger_time=trigger_time,
                    repeat=repeat_option,
                    audio_message=audio_data
                )
                
                st.session_state.reminders.append(reminder)
                
                # Save to database if available
                if db_available and audio_data:
                    try:
                        cursor = db_conn.cursor()
                        cursor.execute(
                            "INSERT INTO reminders (username, title, message, trigger_time, repeat_type, audio_data, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (st.session_state.current_user, reminder_title, reminder_message, 
                             trigger_time, repeat_option, 
                             audio_data.getvalue() if audio_data else None, 
                             "pending")
                        )
                        db_conn.commit()
                    except Exception as e:
                        st.warning(f"⚠️ Could not save to database: {e}")
                
                st.success(f"✅ Reminder set for {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show countdown
                time_diff = trigger_time - datetime.now()
                minutes = int(time_diff.total_seconds() // 60)
                seconds = int(time_diff.total_seconds() % 60)
                st.info(f"⏳ Reminder will trigger in {minutes} minutes {seconds} seconds")
        
        with tab2:
            st.subheader("📋 Active Reminders")
            
            pending_reminders = st.session_state.reminder_system.get_pending_reminders()
            
            if pending_reminders:
                for reminder in pending_reminders:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{reminder['title']}**")
                            st.write(reminder['message'])
                            
                            time_left = reminder['trigger_time'] - datetime.now()
                            if time_left.total_seconds() > 0:
                                minutes = int(time_left.total_seconds() // 60)
                                seconds = int(time_left.total_seconds() % 60)
                                st.caption(f"⏰ Triggers in: {minutes}m {seconds}s | {reminder['trigger_time'].strftime('%H:%M:%S')}")
                            else:
                                st.caption(f"⏰ Triggering now...")
                        
                        with col2:
                            if st.button("▶️ Test", key=f"test_{reminder['id']}"):
                                if reminder.get("audio_message") and st.session_state.audio_system:
                                    st.session_state.audio_system.play(reminder["audio_message"])
                        
                        with col3:
                            if st.button("❌ Cancel", key=f"cancel_{reminder['id']}"):
                                if st.session_state.reminder_system.cancel_reminder(reminder['id']):
                                    st.success("Reminder cancelled!")
                                    st.rerun()
                        
                        st.markdown("---")
            else:
                st.info("📭 No active reminders")
        
        with tab3:
            st.subheader("🎯 Quick Preset Reminders")
            
            presets = st.columns(2)
            
            with presets[0]:
                if st.button("💊 Medicine\n(5 minutes)", use_container_width=True):
                    trigger_time = datetime.now() + timedelta(minutes=5)
                    
                    if st.session_state.audio_system:
                        beep = st.session_state.audio_system.generate_beep(duration=3.0)
                        
                        reminder = st.session_state.reminder_system.add_reminder(
                            title="Medicine Time",
                            message="Take your prescribed medicine",
                            trigger_time=trigger_time,
                            audio_message=beep
                        )
                        st.session_state.reminders.append(reminder)
                        st.success(f"✅ Medicine reminder set for 5 minutes!")
            
            with presets[1]:
                if st.button("🍽️ Lunch\n(1 hour)", use_container_width=True):
                    trigger_time = datetime.now() + timedelta(hours=1)
                    
                    if st.session_state.audio_system:
                        beep = st.session_state.audio_system.generate_beep(frequency=523, duration=3.0)
                        
                        reminder = st.session_state.reminder_system.add_reminder(
                            title="Lunch Time",
                            message="Time to have your lunch",
                            trigger_time=trigger_time,
                            audio_message=beep
                        )
                        st.session_state.reminders.append(reminder)
                        st.success(f"✅ Lunch reminder set for 1 hour!")
    
    # ------------------ DASHBOARD PAGE ------------------
    elif st.session_state.current_page == "📊 Dashboard":
        st.markdown(f"<h2 style='color:#FF5733;'>📊 SYSTEM DASHBOARD</h2>", unsafe_allow_html=True)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Reminders", len(st.session_state.reminder_system.get_pending_reminders()))
        
        with col2:
            motion_count = st.session_state.video_processor.motion_count if st.session_state.video_processor else 0
            st.metric("Motion Events", motion_count)
        
        with col3:
            st.metric("Announcements", len(st.session_state.announcements))
        
        with col4:
            if st.session_state.start_time:
                uptime = datetime.now() - st.session_state.start_time
                hours = uptime.seconds // 3600
                minutes = (uptime.seconds % 3600) // 60
                st.metric("System Uptime", f"{hours}h {minutes}m")
            else:
                st.metric("System Uptime", "0h 0m")
        
        # Quick Talk Section
        st.markdown("---")
        st.subheader("🎤 Quick Talk")
        
        talk_col1, talk_col2 = st.columns(2)
        
        with talk_col1:
            if st.button("🎤 QUICK RECORD & PLAY", use_container_width=True, type="primary"):
                if st.session_state.audio_system:
                    with st.spinner("Recording for 5 seconds..."):
                        audio = st.session_state.audio_system.record(5)
                        if audio:
                            st.session_state.announcements.append({
                                "user": st.session_state.current_user,
                                "text": "Quick dashboard message",
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "audio": audio,
                                "type": "dashboard"
                            })
                            st.session_state.audio_system.play(audio)
                            st.success("✅ Message sent and played!")
                else:
                    st.error("❌ Audio system not available")
        
        with talk_col2:
            if st.session_state.last_audio_message:
                if st.button("🔊 PLAY LAST MESSAGE", use_container_width=True):
                    if st.session_state.audio_system:
                        st.session_state.audio_system.play(st.session_state.last_audio_message)
                    else:
                        st.error("❌ Audio system not available")
            else:
                st.info("No messages recorded yet")
        
        # Recent Activity
        st.markdown("---")
        st.subheader("📋 Recent Activity")
        
        if st.session_state.announcements:
            for ann in reversed(st.session_state.announcements[-10:]):
                st.write(f"**{ann['user']}** ({ann['time']}): {ann['text'][:100]}...")
                st.markdown("---")
        else:
            st.info("No recent activity")

# ------------------ DATABASE SETUP ------------------
with st.sidebar.expander("🔧 Database Setup"):
    st.write("""
    **To set up the database, run these SQL commands in MySQL:**
    
    **Step 1: Create database and tables**
    ```sql
    CREATE DATABASE IF NOT EXISTS login_system;
    USE login_system;
    
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Activity log table
    CREATE TABLE IF NOT EXISTS activity_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        activity VARCHAR(255),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Reminders table
    CREATE TABLE IF NOT EXISTS reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        title VARCHAR(100),
        message TEXT,
        trigger_time DATETIME,
        repeat_type VARCHAR(20),
        audio_data LONGBLOB,
        status VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```
    
    **Step 2: Insert test user (optional)**
    ```sql
    INSERT INTO users (username, password_hash) 
    VALUES ('admin', '1234');
    ```
    """)
    
    # Button to create tables automatically
    if st.button("🛠️ Create Tables Automatically"):
        try:
            cursor = db_conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create activity_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    activity VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create reminders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    title VARCHAR(100),
                    message TEXT,
                    trigger_time DATETIME,
                    repeat_type VARCHAR(20),
                    audio_data LONGBLOB,
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db_conn.commit()
            st.success("✅ Tables created successfully!")
            
        except Exception as e:
            st.error(f"❌ Error creating tables: {e}")

# ------------------ INSTALLATION ------------------
with st.sidebar.expander("📦 Installation"):
    st.write("""
    **Install packages:**
    ```bash
    pip install streamlit streamlit-webrtc opencv-python-headless 
    pip install mysql-connector-python pyngrok av pyaudio
    pip install schedule pytz
    ```
    
    **For Windows audio:**
    - Download PyAudio from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    - Install the .whl file matching your Python version
    """)

# ------------------ AUDIO TROUBLESHOOTING ------------------
with st.sidebar.expander("🔊 Audio Troubleshooting"):
    st.write("""
    **If audio doesn't work:**
    
    1. **Check microphone permissions**
    2. **Test PyAudio installation**
    3. **Try simple beep first**
    """)
    
    if st.button("🔊 Test Beep Sound"):
        if st.session_state.audio_system:
            beep = st.session_state.audio_system.generate_beep()
            if beep:
                st.session_state.audio_system.play(beep)
                st.success("✅ Beep sound played!")
            else:
                st.error("❌ Could not generate beep")
        else:
            st.error("❌ Audio system not available")

# Cleanup on app close
import atexit
@atexit.register
def cleanup():
    if "reminder_system" in st.session_state and st.session_state.reminder_system:
        st.session_state.reminder_system.stop()
    if db_available and 'db_conn' in locals():
        db_conn.close()