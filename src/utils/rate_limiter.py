"""
Rate limiting system to prevent abuse of emergency alerts and API endpoints
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        """Initialize rate limiter"""
        self.limits = {
            "emergency_sos": {"max_calls": 5, "window": 3600},  # 5 per hour
            "medication_log": {"max_calls": 50, "window": 3600},  # 50 per hour
            "vital_sign": {"max_calls": 100, "window": 3600},  # 100 per hour
            "chat_message": {"max_calls": 200, "window": 3600},  # 200 per hour
            "voice_command": {"max_calls": 50, "window": 3600},  # 50 per hour
        }
        self.call_history: Dict[str, list] = {}
    
    def is_allowed(self, user: str, action: str) -> Tuple[bool, str]:
        """Check if action is allowed for user"""
        key = f"{user}:{action}"
        
        if action not in self.limits:
            return True, "Action not rate limited"
        
        limit_config = self.limits[action]
        max_calls = limit_config["max_calls"]
        window = limit_config["window"]
        
        now = datetime.now()
        cutoff = now - timedelta(seconds=window)
        
        # Initialize history for this key
        if key not in self.call_history:
            self.call_history[key] = []
        
        # Remove old calls outside the window
        self.call_history[key] = [
            call_time for call_time in self.call_history[key]
            if call_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.call_history[key]) >= max_calls:
            remaining_wait = (self.call_history[key][0] + timedelta(seconds=window) - now).total_seconds()
            logger.warning(f"Rate limit exceeded for {key}. Wait {remaining_wait:.0f}s")
            return False, f"Rate limit exceeded. Try again in {remaining_wait:.0f}s"
        
        # Record this call
        self.call_history[key].append(now)
        return True, "Allowed"
    
    def get_status(self, user: str, action: str) -> Dict:
        """Get rate limit status for user action"""
        key = f"{user}:{action}"
        
        if action not in self.limits:
            return {"limited": False, "message": "Not rate limited"}
        
        limit_config = self.limits[action]
        max_calls = limit_config["max_calls"]
        window = limit_config["window"]
        
        now = datetime.now()
        cutoff = now - timedelta(seconds=window)
        
        if key not in self.call_history:
            self.call_history[key] = []
        
        # Count calls in window
        recent_calls = [
            call_time for call_time in self.call_history[key]
            if call_time > cutoff
        ]
        
        remaining = max_calls - len(recent_calls)
        reset_time = (recent_calls[0] + timedelta(seconds=window)).isoformat() if recent_calls else None
        
        return {
            "action": action,
            "calls_used": len(recent_calls),
            "calls_limit": max_calls,
            "calls_remaining": max(0, remaining),
            "window_seconds": window,
            "reset_at": reset_time
        }
    
    def reset_user(self, user: str):
        """Reset all rate limits for a user"""
        keys_to_remove = [k for k in self.call_history.keys() if k.startswith(f"{user}:")]
        for key in keys_to_remove:
            del self.call_history[key]
        logger.info(f"Rate limits reset for {user}")
    
    def reset_action(self, action: str):
        """Reset rate limit for specific action across all users"""
        keys_to_remove = [k for k in self.call_history.keys() if k.endswith(f":{action}")]
        for key in keys_to_remove:
            del self.call_history[key]
        logger.info(f"Rate limits reset for action: {action}")
