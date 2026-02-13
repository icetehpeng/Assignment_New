import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from config import TIMEZONE
import json
import os

class OfflineMode:
    def __init__(self):
        self.offline_db_path = ".offline_cache"
        self.ensure_offline_db()
    
    def ensure_offline_db(self):
        """Create offline database directory"""
        if not os.path.exists(self.offline_db_path):
            os.makedirs(self.offline_db_path)
    
    def queue_message(self, sender, receiver, content=None, audio_data=None):
        """Queue message for sending when online"""
        message = {
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "audio_data": audio_data,
            "timestamp": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
            "synced": False
        }
        
        queue_file = os.path.join(self.offline_db_path, "message_queue.json")
        
        try:
            if os.path.exists(queue_file):
                with open(queue_file, 'r') as f:
                    queue = json.load(f)
            else:
                queue = []
            
            queue.append(message)
            
            with open(queue_file, 'w') as f:
                json.dump(queue, f)
            
            return True
        except Exception as e:
            print(f"Error queuing message: {e}")
            return False
    
    def get_message_queue(self):
        """Get queued messages"""
        queue_file = os.path.join(self.offline_db_path, "message_queue.json")
        
        try:
            if os.path.exists(queue_file):
                with open(queue_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error reading message queue: {e}")
            return []
    
    def sync_messages(self, chat_manager):
        """Sync queued messages when online"""
        queue = self.get_message_queue()
        synced_count = 0
        
        for message in queue:
            if not message.get("synced"):
                try:
                    chat_manager.send_message(
                        message["sender"],
                        message["receiver"],
                        message.get("content"),
                        message.get("audio_data")
                    )
                    message["synced"] = True
                    synced_count += 1
                except Exception as e:
                    print(f"Error syncing message: {e}")
        
        # Save updated queue
        queue_file = os.path.join(self.offline_db_path, "message_queue.json")
        try:
            with open(queue_file, 'w') as f:
                json.dump(queue, f)
        except Exception as e:
            print(f"Error saving queue: {e}")
        
        return synced_count
    
    def cache_video_frame(self, frame_data, incident_id):
        """Cache video frame locally"""
        frame_dir = os.path.join(self.offline_db_path, "video_cache")
        if not os.path.exists(frame_dir):
            os.makedirs(frame_dir)
        
        frame_file = os.path.join(frame_dir, f"{incident_id}.jpg")
        
        try:
            with open(frame_file, 'wb') as f:
                f.write(frame_data)
            return True
        except Exception as e:
            print(f"Error caching frame: {e}")
            return False
    
    def get_cached_video_frames(self):
        """Get cached video frames"""
        frame_dir = os.path.join(self.offline_db_path, "video_cache")
        
        if not os.path.exists(frame_dir):
            return []
        
        frames = []
        for filename in os.listdir(frame_dir):
            if filename.endswith(".jpg"):
                frames.append({
                    "id": filename.replace(".jpg", ""),
                    "path": os.path.join(frame_dir, filename)
                })
        
        return frames
    
    def cache_local_data(self, data_type, data):
        """Cache any data locally"""
        cache_file = os.path.join(self.offline_db_path, f"{data_type}_cache.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error caching data: {e}")
            return False
    
    def get_cached_data(self, data_type):
        """Get cached data"""
        cache_file = os.path.join(self.offline_db_path, f"{data_type}_cache.json")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def get_sync_status(self):
        """Get sync status"""
        queue = self.get_message_queue()
        unsynced = len([m for m in queue if not m.get("synced")])
        
        return {
            "total_queued": len(queue),
            "unsynced": unsynced,
            "synced": len(queue) - unsynced,
            "status": "synced" if unsynced == 0 else "pending"
        }
    
    def clear_old_cache(self, days=30):
        """Clear cache older than specified days"""
        import time
        
        cache_dir = self.offline_db_path
        current_time = time.time()
        cutoff_time = current_time - (days * 86400)
        
        for filename in os.listdir(cache_dir):
            filepath = os.path.join(cache_dir, filename)
            if os.path.isfile(filepath):
                if os.stat(filepath).st_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Error removing cache file: {e}")
