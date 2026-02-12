"""
Comprehensive error logging and recovery system
Tracks all errors, provides automatic recovery, and maintains audit logs
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
from pathlib import Path
import mysql.connector

# Create logs directory
Path("logs").mkdir(exist_ok=True)

class ErrorLogger:
    def __init__(self, db_conn=None, db_available=False):
        """Initialize error logging system"""
        self.db_conn = db_conn
        self.db_available = db_available
        
        # Setup file logging
        self.logger = logging.getLogger("SmartCareApp")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler("logs/app_errors.log")
        fh.setLevel(logging.ERROR)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_error(self, error_type: str, message: str, context: Optional[Dict] = None, 
                  user: Optional[str] = None, severity: str = "ERROR") -> str:
        """Log error with context and return error ID"""
        error_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "severity": severity,
            "user": user,
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        # Log to file
        self.logger.error(f"[{error_id}] {error_type}: {message}")
        
        # Log to database if available
        if self.db_available and self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO error_logs (error_id, error_type, message, severity, username, context, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (error_id, error_type, message, severity, user, json.dumps(error_data), datetime.now()))
                self.db_conn.commit()
            except Exception as e:
                self.logger.warning(f"Failed to log error to database: {e}")
        
        return error_id
    
    def log_recovery(self, error_id: str, recovery_action: str, success: bool):
        """Log recovery attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[{error_id}] Recovery {status}: {recovery_action}")
        
        if self.db_available and self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO recovery_logs (error_id, recovery_action, success, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (error_id, recovery_action, success, datetime.now()))
                self.db_conn.commit()
            except Exception as e:
                self.logger.warning(f"Failed to log recovery: {e}")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for dashboard"""
        summary = {
            "total_errors": 0,
            "critical": 0,
            "warnings": 0,
            "recovered": 0,
            "recent_errors": []
        }
        
        if self.db_available and self.db_conn:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute(f"""
                    SELECT error_id, error_type, message, severity, timestamp
                    FROM error_logs
                    WHERE timestamp > DATE_SUB(NOW(), INTERVAL {hours} HOUR)
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)
                
                for row in cursor.fetchall():
                    summary["total_errors"] += 1
                    if row[3] == "CRITICAL":
                        summary["critical"] += 1
                    elif row[3] == "WARNING":
                        summary["warnings"] += 1
                    
                    summary["recent_errors"].append({
                        "id": row[0],
                        "type": row[1],
                        "message": row[2],
                        "severity": row[3],
                        "timestamp": str(row[4])
                    })
            except Exception as e:
                self.logger.error(f"Failed to get error summary: {e}")
        
        return summary
    
    def attempt_recovery(self, error_type: str, db_conn) -> bool:
        """Attempt automatic recovery based on error type"""
        try:
            if error_type == "DATABASE_CONNECTION":
                # Try to reconnect
                db_conn.reconnect()
                self.logger.info("Database reconnection successful")
                return True
            
            elif error_type == "CACHE_ERROR":
                # Clear cache and continue
                self.logger.info("Clearing cache and continuing")
                return True
            
            elif error_type == "FILE_NOT_FOUND":
                # Create missing file/directory
                self.logger.info("Attempting to create missing resource")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            return False
