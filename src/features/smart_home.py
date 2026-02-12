import streamlit as st
from datetime import datetime
from config import TIMEZONE
import requests

class SmartHomeController:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
        self.devices = {}
    
    def add_device(self, device_id, device_name, device_type, ip_address, port=80):
        """Add a smart home device"""
        device = {
            "id": device_id,
            "name": device_name,
            "type": device_type,  # light, thermostat, lock, camera, etc.
            "ip": ip_address,
            "port": port,
            "status": "offline"
        }
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO smart_devices (device_id, device_name, device_type, ip_address, port)
                    VALUES (%s, %s, %s, %s, %s)
                """, (device_id, device_name, device_type, ip_address, port))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error adding device: {e}")
        
        if "smart_devices" not in st.session_state:
            st.session_state.smart_devices = {}
        
        st.session_state.smart_devices[device_id] = device
        return device
    
    def control_light(self, device_id, action):
        """Control light (on/off/brightness)"""
        # action: {"command": "on/off/brightness", "value": 0-100}
        
        result = self._send_command(device_id, action)
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO device_logs (device_id, action, timestamp)
                    VALUES (%s, %s, %s)
                """, (device_id, str(action), datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error logging action: {e}")
        
        return result
    
    def control_thermostat(self, device_id, temperature):
        """Set thermostat temperature"""
        action = {"command": "set_temperature", "value": temperature}
        return self._send_command(device_id, action)
    
    def control_lock(self, device_id, action):
        """Control door lock (lock/unlock)"""
        # action: "lock" or "unlock"
        cmd = {"command": action}
        return self._send_command(device_id, cmd)
    
    def _send_command(self, device_id, command):
        """Send command to device"""
        if device_id not in st.session_state.get("smart_devices", {}):
            return {"status": "error", "message": "Device not found"}
        
        device = st.session_state.smart_devices[device_id]
        
        try:
            url = f"http://{device['ip']}:{device['port']}/api/command"
            response = requests.post(url, json=command, timeout=5)
            
            if response.status_code == 200:
                return {"status": "success", "message": "Command sent"}
            else:
                return {"status": "error", "message": "Device error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_routine(self, routine_name, trigger, actions):
        """Create automated routine"""
        # trigger: {"type": "time", "value": "08:00"} or {"type": "event", "value": "motion_detected"}
        # actions: list of device commands
        
        routine = {
            "name": routine_name,
            "trigger": trigger,
            "actions": actions,
            "enabled": True,
            "created_at": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO routines (routine_name, trigger, actions, enabled)
                    VALUES (%s, %s, %s, %s)
                """, (routine_name, str(trigger), str(actions), True))
                self.db_conn.commit()
            except Exception as e:
                print(f"Error creating routine: {e}")
        
        if "routines" not in st.session_state:
            st.session_state.routines = []
        
        st.session_state.routines.append(routine)
        return routine
    
    def get_device_status(self, device_id):
        """Get device status"""
        if device_id not in st.session_state.get("smart_devices", {}):
            return {"status": "unknown"}
        
        device = st.session_state.smart_devices[device_id]
        
        try:
            url = f"http://{device['ip']}:{device['port']}/api/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "offline"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    def detect_stove_left_on(self):
        """Alert if stove is left on"""
        # Check stove device status
        stove_devices = [d for d in st.session_state.get("smart_devices", {}).values() 
                        if d["type"] == "stove"]
        
        alerts = []
        for device in stove_devices:
            status = self.get_device_status(device["id"])
            if status.get("power") == "on":
                alerts.append({
                    "device": device["name"],
                    "alert": "⚠️ Stove left on!",
                    "timestamp": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return alerts
    
    def detect_door_window_open(self):
        """Alert if door/window is open"""
        alerts = []
        
        for device in st.session_state.get("smart_devices", {}).values():
            if device["type"] in ["door", "window"]:
                status = self.get_device_status(device["id"])
                if status.get("state") == "open":
                    alerts.append({
                        "device": device["name"],
                        "alert": f"⚠️ {device['name']} is open",
                        "timestamp": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        return alerts
    
    def detect_water_leak(self):
        """Alert if water leak detected"""
        alerts = []
        
        for device in st.session_state.get("smart_devices", {}).values():
            if device["type"] == "water_sensor":
                status = self.get_device_status(device["id"])
                if status.get("leak_detected") == True:
                    alerts.append({
                        "device": device["name"],
                        "alert": "🚨 Water leak detected!",
                        "timestamp": datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        return alerts
