import mysql.connector
from datetime import datetime
from io import BytesIO

class ChatManager:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available

    def get_users(self, current_user):
        """Fetch all usernames except the current user"""
        import streamlit as st
        users = []
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username != %s", (current_user,))
                users = [u[0] for u in cursor.fetchall()]
            except Exception as e:
                print(f"Error fetching users: {e}")
        
        # Fallback to local users if DB failed or empty
        if not users and "local_users" in st.session_state:
            users = [u for u in st.session_state.local_users.keys() if u != current_user]
        return users

    def get_messages(self, user1, user2):
        """Fetch message history between two users"""
        import streamlit as st
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                u1 = str(user1).strip().lower()
                u2 = str(user2).strip().lower()
                # Query that is very loose on case and whitespace
                cursor.execute("""
                    SELECT sender, content, audio_data, timestamp 
                    FROM messages 
                    WHERE (LOWER(TRIM(sender)) = %s AND LOWER(TRIM(receiver)) = %s) 
                       OR (LOWER(TRIM(sender)) = %s AND LOWER(TRIM(receiver)) = %s)
                    ORDER BY timestamp ASC
                """, (u1, u2, u2, u1))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error fetching messages: {e}")
        
        # Fallback to session state
        if "local_messages" not in st.session_state:
            st.session_state.local_messages = []
        
        filtered = []
        for msg in st.session_state.local_messages:
            if (msg['sender'] == user1 and msg['receiver'] == user2) or \
               (msg['sender'] == user2 and msg['receiver'] == user1):
                # Convert dict to tuple format matching DB schema: (sender, content, audio_data, timestamp)
                filtered.append((msg['sender'], msg.get('content'), msg.get('audio_data'), msg['timestamp']))
        return filtered

    def send_message(self, sender, receiver, content=None, audio_data=None):
        """Send a new text or voice message"""
        import streamlit as st
        success = False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                # Store as trimmed but original case, but query is case-insensitive
                s = str(sender).strip()
                r = str(receiver).strip()
                if audio_data:
                    cursor.execute(
                        "INSERT INTO messages (sender, receiver, audio_data) VALUES (%s, %s, %s)",
                        (s, r, audio_data)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO messages (sender, receiver, content) VALUES (%s, %s, %s)",
                        (s, r, content)
                    )
                self.db_conn.commit()
                success = True
            except Exception as e:
                print(f"Error sending message: {e}")

        # Always save to local session state as well (for and as fallback)
        if "local_messages" not in st.session_state:
            st.session_state.local_messages = []
        
        st.session_state.local_messages.append({
            'sender': sender,
            'receiver': receiver,
            'content': content,
            'audio_data': audio_data,
            'timestamp': timestamp
        })
        
        return True # Always return True since local save succeeded

    def get_latest_message_id(self, user1, user2):
        """Get the ID of the latest message for fresh check"""
        if not self.db_available:
            return 0
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT MAX(id) FROM messages 
                WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)
            """, (user1, user2, user1, user2))
            res = cursor.fetchone()
            return res[0] if res and res[0] else 0
        except Exception as e:
            return 0
