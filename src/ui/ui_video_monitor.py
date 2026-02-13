import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from config import TIMEZONE
import requests
import time
import subprocess

def show_video_monitor():
    """Display live video feed from Flask with fall detection status"""
    
    st.markdown(f"<h2 style='color:#FF5733;'>📹 LIVE VIDEO FEED</h2>", unsafe_allow_html=True)
    
    # Flask server URL
    FLASK_URL = "http://127.0.0.1:5000"
    
    # Initialize session state for monitoring
    if 'video_monitoring_active' not in st.session_state:
        st.session_state.video_monitoring_active = True
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Live Camera Feed")
        
        # Create a placeholder for the video feed
        video_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (every 2 seconds)", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 2)
        
        # Control buttons
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            if st.button("🔄 Refresh Now"):
                st.rerun()
        
        with col_btn2:
            if st.button("⏹️ Stop Monitoring"):
                st.session_state.video_monitoring_active = False
                st.success("Monitoring stopped. Click 'Start Monitoring' to resume.")
        
        with col_btn3:
            if st.button("▶️ Start Monitoring"):
                try:
                    # First, kill any existing frame server process on port 5000
                    result = subprocess.run(
                        'netstat -ano | findstr :5000',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) > 0:
                                pid = parts[-1]
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                        time.sleep(1)
                    
                    # Start the frame server process
                    frame_server_path = str(Path(__file__).parent.parent / "video" / "frame_server.py")
                    subprocess.Popen(
                        ['python', frame_server_path],
                        cwd=str(Path(__file__).parent.parent.parent),
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    
                    time.sleep(2)  # Wait for server to start
                    st.session_state.video_monitoring_active = True
                    st.success("✅ Frame Server restarted successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error restarting frame server: {str(e)}")
        
        with col_btn4:
            if st.button("🛑 Kill Frame Server"):
                try:
                    # Kill process listening on port 5000
                    # First, find the PID using netstat
                    result = subprocess.run(
                        'netstat -ano | findstr :5000',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        # Extract PID from netstat output
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) > 0:
                                pid = parts[-1]
                                # Kill the process
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                        
                        st.session_state.video_monitoring_active = False
                        st.error("🛑 Frame Server process terminated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ Frame Server not found on port 5000")
                except Exception as e:
                    st.error(f"Error killing process: {str(e)}")
    
    with col2:
        st.subheader("Detection Status")
        detection_status = st.empty()
        confidence_metric = st.empty()
        motion_metric = st.empty()
    
    # Check if monitoring is active
    if not st.session_state.video_monitoring_active:
        st.warning("⏹️ Monitoring is stopped. Click 'Start Monitoring' to resume.")
        return
    
    # Fetch and display video frame
    try:
        response = requests.get(f"{FLASK_URL}/api/frame", timeout=5)
        if response.status_code == 200:
            video_placeholder.image(response.content, caption="Live Camera Feed", use_column_width=True)
        else:
            video_placeholder.error(f"Failed to fetch frame: {response.status_code}")
    except requests.exceptions.ConnectionError:
        video_placeholder.error("❌ Cannot connect to Flask server. Make sure frame_server.py is running on port 5000")
    except Exception as e:
        video_placeholder.error(f"Error fetching video: {str(e)}")
    
    # Fetch detection status
    try:
        response = requests.get(f"{FLASK_URL}/api/detection", timeout=5)
        if response.status_code == 200:
            detection = response.json()
            
            # Display detection status
            if detection.get('fall_detected'):
                detection_status.error("🚨 FALL DETECTED!")
                status_placeholder.warning(f"⚠️ Fall detected at {datetime.now(TIMEZONE).strftime('%H:%M:%S')}")
            else:
                detection_status.success("✅ No Fall Detected")
                status_placeholder.info("Normal activity detected")
            
            # Display metrics
            confidence = detection.get('confidence', 0)
            motion = detection.get('motion', 0)
            
            confidence_metric.metric("Confidence", f"{confidence*100:.1f}%", 
                                    delta=f"Threshold: 50%",
                                    delta_color="inverse" if confidence >= 0.5 else "normal")
            motion_metric.metric("Motion Level", f"{motion}", 
                                delta=f"Threshold: 1000",
                                delta_color="inverse" if motion < 1000 else "normal")
        else:
            detection_status.error(f"Failed to fetch detection: {response.status_code}")
    except requests.exceptions.ConnectionError:
        detection_status.error("❌ Cannot connect to Flask")
    except Exception as e:
        detection_status.error(f"Error: {str(e)}")
    
    # Display detection history
    st.markdown("---")
    st.subheader("📊 Detection Details")
    
    try:
        response = requests.get(f"{FLASK_URL}/api/detection", timeout=5)
        if response.status_code == 200:
            detection = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Confidence", f"{detection.get('confidence', 0)*100:.1f}%")
            
            with col2:
                st.metric("Motion", detection.get('motion', 0))
            
            with col3:
                aspect_ratio = detection.get('aspect_ratio', 0)
                st.metric("Aspect Ratio", f"{aspect_ratio:.2f}" if aspect_ratio else "N/A")
            
            with col4:
                timestamp = detection.get('timestamp', 0)
                st.metric("Last Update", f"{datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}")
            
            # Show raw detection data
            with st.expander("📋 Raw Detection Data"):
                st.json(detection)
    except Exception as e:
        st.error(f"Could not fetch detection details: {str(e)}")
    
    # Health check
    st.markdown("---")
    st.subheader("🏥 System Health")
    
    try:
        response = requests.get(f"{FLASK_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_color = "green" if health.get('status') == 'ok' else "red"
                st.markdown(f"<h4 style='color:{status_color};'>Status: {health.get('status', 'unknown').upper()}</h4>", 
                           unsafe_allow_html=True)
            
            with col2:
                has_frame = "✅ Yes" if health.get('has_frame') else "❌ No"
                st.metric("Has Frame", has_frame)
            
            with col3:
                frame_age = health.get('frame_age_seconds', -1)
                if frame_age >= 0:
                    st.metric("Frame Age", f"{frame_age:.2f}s")
                else:
                    st.metric("Frame Age", "N/A")
    except Exception as e:
        st.error(f"Health check failed: {str(e)}")
    
    # Auto-refresh logic
    if auto_refresh and st.session_state.video_monitoring_active:
        time.sleep(refresh_interval)
        st.rerun()
