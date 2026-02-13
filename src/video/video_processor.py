import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import av
from datetime import datetime
import time
import psutil
import os
from config import TIMEZONE

class VideoProcessor:
    """Ultra-simple video processor - just display frames with monitoring"""
    
    def __init__(self):
        self.frame_count = 0
        self.motion_count = 0
        self.pending_incidents = []
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.frame_times = []  # Last 30 frame times for FPS calculation
        self.process = psutil.Process(os.getpid())
        
    def get_fps(self):
        """Calculate current FPS from recent frame times"""
        if len(self.frame_times) < 2:
            return 0
        time_diff = self.frame_times[-1] - self.frame_times[0]
        if time_diff == 0:
            return 0
        return len(self.frame_times) / time_diff
    
    def get_latency(self):
        """Estimate latency in milliseconds"""
        if len(self.frame_times) < 2:
            return 0
        return (self.frame_times[-1] - self.frame_times[-2]) * 1000
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            return self.process.cpu_percent(interval=0.1)
        except:
            return 0
    
    def get_memory_usage(self):
        """Get memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0
        
    def recv(self, frame):
        """Process video frame - minimal processing"""
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1
        
        # Track frame timing
        current_time = time.time()
        self.frame_times.append(current_time)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        # Add timestamp overlay
        timestamp = datetime.now(TIMEZONE).strftime("%H:%M:%S")
        cv2.putText(img, f"LIVE: {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add monitoring info overlay (every 10 frames to reduce overhead)
        if self.frame_count % 10 == 0:
            fps = self.get_fps()
            latency = self.get_latency()
            cpu = self.get_cpu_usage()
            
            # Add FPS
            cv2.putText(img, f"FPS: {fps:.1f}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Add latency
            cv2.putText(img, f"Latency: {latency:.0f}ms", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Add CPU usage
            cv2.putText(img, f"CPU: {cpu:.1f}%", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")
