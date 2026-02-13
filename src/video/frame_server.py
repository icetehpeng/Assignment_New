"""
Flask server that serves camera frames and performs fall detection
Runs on port 5000 alongside Streamlit
"""

from flask import Flask, Response, jsonify
import cv2
import threading
import time
import base64
import sys
from pathlib import Path

# Add src directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fall_detector import FallDetector

app = Flask(__name__)

# Global state
latest_frame = None
frame_lock = threading.Lock()
last_frame_time = 0
camera = None
fall_detector = FallDetector(confidence_threshold=0.50)
last_detection = {
    'fall_detected': False,
    'confidence': 0.0,
    'timestamp': 0
}
fall_alert_time = 0  # When fall was detected
fall_alert_duration = 5  # Keep alert active for 5 seconds

def init_camera():
    """Initialize camera capture"""
    global camera
    if camera is None:
        try:
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            camera.set(cv2.CAP_PROP_FPS, 30)
            print("✓ Camera initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing camera: {e}")
            camera = None
    return camera

def capture_and_analyze():
    """Continuously capture frames and analyze for falls"""
    global latest_frame, last_frame_time, camera, last_detection, fall_alert_time
    
    init_camera()
    
    while True:
        try:
            if camera is not None:
                ret, frame = camera.read()
                if ret:
                    with frame_lock:
                        latest_frame = frame.copy()
                        last_frame_time = time.time()
                    
                    # Analyze frame for falls
                    detection = fall_detector.analyze_frame(frame)
                    
                    # Debug output every 30 frames (1 second at 30 FPS)
                    if int(time.time() * 10) % 3 == 0:  # Every ~1 second
                        aspect_str = f"{detection['aspect_ratio']:.2f}" if detection['aspect_ratio'] else "N/A"
                        print(f"📊 Detection: Conf={detection['confidence']:.2%} | Aspect={aspect_str} | Motion={detection['motion']} | Fall={detection['fall_detected']}")
                    
                    if detection['fall_detected']:
                        fall_alert_time = time.time()
                        print(f"🚨 FALL DETECTED! Confidence: {detection['confidence']:.2%}")
                    
                    # Update detection status
                    # Keep alert active for fall_alert_duration seconds
                    current_time = time.time()
                    is_alert_active = (current_time - fall_alert_time) < fall_alert_duration
                    
                    last_detection = {
                        'fall_detected': is_alert_active,
                        'confidence': detection['confidence'],
                        'timestamp': current_time,
                        'aspect_ratio': detection['aspect_ratio'],
                        'motion': detection['motion'],
                        'alert_active_for': max(0, fall_alert_duration - (current_time - fall_alert_time))
                    }
                else:
                    print("✗ Failed to read frame from camera")
                    camera = None
                    init_camera()
            time.sleep(0.033)  # ~30 FPS
        except Exception as e:
            print(f"✗ Error in capture_and_analyze: {e}")
            time.sleep(1)

@app.route('/api/frame', methods=['GET'])
def get_frame():
    """Return latest frame as JPEG"""
    global latest_frame
    
    with frame_lock:
        if latest_frame is not None:
            try:
                _, buffer = cv2.imencode('.jpg', latest_frame)
                return Response(buffer.tobytes(), mimetype='image/jpeg')
            except Exception as e:
                print(f"✗ Error encoding frame: {e}")
                return '', 500
    
    return '', 404

@app.route('/api/detection', methods=['GET'])
def get_detection():
    """Return latest fall detection result"""
    global last_detection
    
    return jsonify(last_detection), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return detection statistics"""
    stats = fall_detector.get_statistics()
    return jsonify(stats), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    global latest_frame, last_frame_time
    frame_age = time.time() - last_frame_time if last_frame_time > 0 else -1
    
    return jsonify({
        'status': 'ok',
        'has_frame': latest_frame is not None,
        'frame_age_seconds': frame_age,
        'last_detection': last_detection
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Fall Detection Frame Server")
    print("=" * 60)
    print("Starting on http://0.0.0.0:5000")
    print("\nEndpoints:")
    print("  GET /api/frame - Returns JPEG frame")
    print("  GET /api/detection - Returns fall detection result")
    print("  GET /api/stats - Returns detection statistics")
    print("  GET /health - Health check")
    print("=" * 60)
    
    # Start frame capture in background thread
    capture_thread = threading.Thread(target=capture_and_analyze, daemon=True)
    capture_thread.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
