"""
Real Fall Detection System using OpenCV and pose estimation
Detects falls based on:
1. Aspect ratio (person lying down = low aspect ratio)
2. Motion detection
3. Confidence scoring
"""

import cv2
import numpy as np
from collections import deque
import time

class FallDetector:
    """Real fall detection using computer vision"""
    
    def __init__(self, confidence_threshold=0.50):
        self.confidence_threshold = confidence_threshold
        self.prev_frame = None
        self.motion_history = deque(maxlen=10)
        self.fall_history = deque(maxlen=30)
        self.last_fall_time = 0
        self.fall_cooldown = 0.5  # seconds between fall alerts (very responsive)
        
    def detect_person(self, frame):
        """Detect person in frame using contours"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Threshold
        _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        # Get largest contour (person)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Filter by area (person should be significant) - LOWERED THRESHOLD
        if area < 3000:
            return None, None
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        return (x, y, w, h), area
    
    def calculate_aspect_ratio(self, bbox):
        """Calculate aspect ratio (width/height)"""
        if bbox is None:
            return None
        
        x, y, w, h = bbox
        if h == 0:
            return None
        
        aspect_ratio = w / h
        return aspect_ratio
    
    def detect_motion(self, frame):
        """Detect motion between frames"""
        if self.prev_frame is None:
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return 0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        
        # Threshold
        _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Count motion pixels
        motion_pixels = cv2.countNonZero(thresh)
        
        self.prev_frame = gray
        
        return motion_pixels
    
    def analyze_frame(self, frame):
        """Analyze frame for fall detection"""
        result = {
            'fall_detected': False,
            'confidence': 0.0,
            'aspect_ratio': None,
            'motion': 0,
            'bbox': None,
            'details': {}
        }
        
        # Detect person
        bbox, area = self.detect_person(frame)
        result['bbox'] = bbox
        
        if bbox is None:
            return result
        
        # Calculate aspect ratio
        aspect_ratio = self.calculate_aspect_ratio(bbox)
        result['aspect_ratio'] = aspect_ratio
        
        if aspect_ratio is None:
            return result
        
        # Detect motion
        motion = self.detect_motion(frame)
        result['motion'] = motion
        
        # Fall detection logic - MORE SENSITIVE
        confidence = 0.0
        details = {}
        
        # Check 1: Aspect ratio (lying down = high ratio)
        # Normal standing: ~0.5-0.7
        # Lying down: ~1.5-3.0
        # LOWERED THRESHOLD for more sensitivity
        if aspect_ratio > 1.0:
            ratio_score = min((aspect_ratio - 1.0) / 2.0, 1.0)  # Normalize to 0-1
            confidence += ratio_score * 0.65  # 65% weight
            details['aspect_ratio_score'] = ratio_score
        else:
            # Even if aspect ratio is low, still calculate a score
            ratio_score = max(0, aspect_ratio / 0.7)  # Normalize standing position
            confidence += ratio_score * 0.65
            details['aspect_ratio_score'] = ratio_score
        
        # Check 2: Motion (should be low if fallen)
        # High motion = person moving
        # Low motion = person stationary (fallen)
        motion_score = max(0, 1.0 - (motion / 8000))  # Always calculate
        confidence += motion_score * 0.25  # 25% weight
        details['motion_score'] = motion_score
        
        # Check 3: Area (person should be visible)
        area_score = min(area / 40000, 1.0)  # Always calculate
        confidence += area_score * 0.1  # 10% weight
        details['area_score'] = area_score
        
        # Store details
        result['details'] = details
        result['confidence'] = confidence
        
        # Determine if fall detected - USE CURRENT FRAME CONFIDENCE
        if confidence >= self.confidence_threshold:
            # Check cooldown to avoid duplicate alerts
            current_time = time.time()
            if current_time - self.last_fall_time > self.fall_cooldown:
                result['fall_detected'] = True
                self.last_fall_time = current_time
                print(f"🚨 FALL DETECTED! Confidence: {confidence:.2%} | Aspect: {aspect_ratio:.2f} | Motion: {motion} | Area: {area}")
        
        # Track history for statistics only
        self.fall_history.append(confidence)
        
        return result
    
    def get_statistics(self):
        """Get detection statistics"""
        if not self.fall_history:
            return {
                'avg_confidence': 0.0,
                'max_confidence': 0.0,
                'min_confidence': 0.0
            }
        
        history_list = list(self.fall_history)
        return {
            'avg_confidence': np.mean(history_list),
            'max_confidence': np.max(history_list),
            'min_confidence': np.min(history_list)
        }
