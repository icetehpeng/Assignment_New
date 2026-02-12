import streamlit as st
from datetime import datetime
from config import TIMEZONE

class VoiceControl:
    def __init__(self):
        self.commands = {
            "set reminder": self._handle_reminder,
            "call": self._handle_call,
            "show camera": self._handle_camera,
            "turn on": self._handle_light_on,
            "turn off": self._handle_light_off,
            "set temperature": self._handle_temperature,
            "lock door": self._handle_lock,
            "unlock door": self._handle_unlock,
            "play music": self._handle_music,
            "what time": self._handle_time,
            "weather": self._handle_weather,
            "help": self._handle_help
        }
    
    def process_voice_command(self, text):
        """Process voice command"""
        text_lower = text.lower().strip()
        
        # Find matching command
        for command_key, handler in self.commands.items():
            if command_key in text_lower:
                return handler(text)
        
        return {
            "status": "unknown",
            "message": "Command not recognized. Say 'help' for available commands."
        }
    
    def _handle_reminder(self, text):
        """Handle reminder command"""
        # Example: "set reminder for 2pm take medicine"
        return {
            "status": "success",
            "action": "create_reminder",
            "message": "Reminder set"
        }
    
    def _handle_call(self, text):
        """Handle call command"""
        # Example: "call my daughter"
        return {
            "status": "success",
            "action": "initiate_call",
            "message": "Calling..."
        }
    
    def _handle_camera(self, text):
        """Handle camera command"""
        return {
            "status": "success",
            "action": "show_camera",
            "message": "Showing camera feed"
        }
    
    def _handle_light_on(self, text):
        """Handle light on command"""
        # Example: "turn on bedroom light"
        return {
            "status": "success",
            "action": "control_light",
            "command": "on",
            "message": "Light turned on"
        }
    
    def _handle_light_off(self, text):
        """Handle light off command"""
        return {
            "status": "success",
            "action": "control_light",
            "command": "off",
            "message": "Light turned off"
        }
    
    def _handle_temperature(self, text):
        """Handle temperature command"""
        # Example: "set temperature to 22 degrees"
        return {
            "status": "success",
            "action": "set_temperature",
            "message": "Temperature adjusted"
        }
    
    def _handle_lock(self, text):
        """Handle lock command"""
        return {
            "status": "success",
            "action": "lock_door",
            "message": "Door locked"
        }
    
    def _handle_unlock(self, text):
        """Handle unlock command"""
        return {
            "status": "success",
            "action": "unlock_door",
            "message": "Door unlocked"
        }
    
    def _handle_music(self, text):
        """Handle music command"""
        return {
            "status": "success",
            "action": "play_music",
            "message": "Playing music"
        }
    
    def _handle_time(self, text):
        """Handle time query"""
        current_time = datetime.now(TIMEZONE).strftime("%H:%M")
        return {
            "status": "success",
            "action": "speak",
            "message": f"It is {current_time}"
        }
    
    def _handle_weather(self, text):
        """Handle weather query"""
        return {
            "status": "success",
            "action": "speak",
            "message": "Weather information not available"
        }
    
    def _handle_help(self, text):
        """Handle help command"""
        commands = [
            "Set reminder for [time] [task]",
            "Call [contact name]",
            "Show camera",
            "Turn on/off [device]",
            "Set temperature to [degrees]",
            "Lock/unlock door",
            "Play music",
            "What time is it",
            "Weather"
        ]
        return {
            "status": "success",
            "action": "speak",
            "message": "Available commands: " + ", ".join(commands)
        }
    
    def get_available_commands(self):
        """Get list of available voice commands"""
        return list(self.commands.keys())
