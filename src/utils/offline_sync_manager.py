"""
Enhanced offline-first architecture with automatic sync
Queues operations when offline and syncs when connection returns
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OfflineSyncManager:
    def __init__(self, db_path: str = ".offline_cache/sync_queue.db"):
        """Initialize offline sync manager"""
        Path(".offline_cache").mkdir(exist_ok=True)
        self.db_path = db_path
        self.init_local_db()
    
    def init_local_db(self):
        """Initialize local SQLite database for offline queue"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create sync queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT,
                    table_name TEXT,
                    data JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT 0,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            
            # Create local cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS local_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE,
                    data JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ttl INTEGER
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Local sync database initialized")
        except Exception as e:
            logger.error(f"Error initializing local database: {e}")
    
    def queue_operation(self, operation_type: str, table_name: str, data: Dict) -> bool:
        """Queue an operation for later sync"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sync_queue (operation_type, table_name, data)
                VALUES (?, ?, ?)
            """, (operation_type, table_name, json.dumps(data)))
            
            conn.commit()
            conn.close()
            logger.info(f"Operation queued: {operation_type} on {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error queuing operation: {e}")
            return False
    
    def get_pending_operations(self) -> List[Dict]:
        """Get all pending operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sync_queue WHERE synced=0 ORDER BY timestamp ASC
            """)
            
            operations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return operations
        except Exception as e:
            logger.error(f"Error fetching pending operations: {e}")
            return []
    
    def mark_synced(self, operation_id: int) -> bool:
        """Mark operation as synced"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sync_queue SET synced=1 WHERE id=?
            """, (operation_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error marking operation as synced: {e}")
            return False
    
    def sync_to_server(self, db_conn, db_available: bool) -> Dict:
        """Sync all pending operations to server"""
        if not db_available or not db_conn:
            logger.warning("Database not available for sync")
            return {"synced": 0, "failed": 0, "pending": len(self.get_pending_operations())}
        
        operations = self.get_pending_operations()
        synced_count = 0
        failed_count = 0
        
        try:
            cursor = db_conn.cursor()
            
            for op in operations:
                try:
                    data = json.loads(op['data'])
                    
                    if op['operation_type'] == 'INSERT':
                        # Build INSERT query dynamically
                        columns = ', '.join(data.keys())
                        placeholders = ', '.join(['%s'] * len(data))
                        query = f"INSERT INTO {op['table_name']} ({columns}) VALUES ({placeholders})"
                        cursor.execute(query, tuple(data.values()))
                    
                    elif op['operation_type'] == 'UPDATE':
                        # Build UPDATE query
                        set_clause = ', '.join([f"{k}=%s" for k in data.keys() if k != 'id'])
                        query = f"UPDATE {op['table_name']} SET {set_clause} WHERE id=%s"
                        values = [v for k, v in data.items() if k != 'id'] + [data.get('id')]
                        cursor.execute(query, values)
                    
                    db_conn.commit()
                    self.mark_synced(op['id'])
                    synced_count += 1
                    logger.info(f"Synced operation {op['id']}")
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to sync operation {op['id']}: {e}")
                    # Increment retry count
                    try:
                        conn = sqlite3.connect(self.db_path)
                        c = conn.cursor()
                        c.execute("UPDATE sync_queue SET retry_count=retry_count+1 WHERE id=?", (op['id'],))
                        conn.commit()
                        conn.close()
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
        
        return {
            "synced": synced_count,
            "failed": failed_count,
            "pending": len(self.get_pending_operations())
        }
    
    def cache_locally(self, key: str, data: Dict, ttl: int = 3600) -> bool:
        """Cache data locally for offline access"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO local_cache (cache_key, data, ttl)
                VALUES (?, ?, ?)
            """, (key, json.dumps(data), ttl))
            
            conn.commit()
            conn.close()
            logger.debug(f"Data cached locally: {key}")
            return True
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data, timestamp, ttl FROM local_cache WHERE cache_key=?
            """, (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                data, timestamp, ttl = result
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(timestamp)
                if (datetime.now() - cache_time).total_seconds() < ttl:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(data)
                else:
                    logger.debug(f"Cache EXPIRED: {key}")
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached data: {e}")
            return None
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE synced=0")
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE synced=1")
            synced = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM local_cache")
            cached = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "pending": pending,
                "synced": synced,
                "cached": cached,
                "total_queued": pending + synced
            }
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {"pending": 0, "synced": 0, "cached": 0, "total_queued": 0}
    
    def clear_old_cache(self, days: int = 7) -> int:
        """Clear cache older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM local_cache 
                WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f"Cleared {deleted} old cache entries")
            return deleted
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
