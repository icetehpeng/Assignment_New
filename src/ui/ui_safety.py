import streamlit as st
from datetime import datetime
from config import TIMEZONE

def show_emergency_page():
    """Emergency Contact System UI"""
    st.markdown("<h2 style='color:#FF5733;'>🚨 EMERGENCY SYSTEM</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Contact", "📞 Contacts", "🆘 SOS"])
    
    with tab1:
        st.subheader("Add Emergency Contact")
        name = st.text_input("Contact Name")
        phone = st.text_input("Phone Number")
        priority = st.number_input("Priority (1=highest)", min_value=1, max_value=10, value=1)
        relation = st.text_input("Relation (e.g., Daughter, Son)")
        
        if st.button("✅ Add Contact", use_container_width=True, type="primary"):
            st.session_state.emergency.add_emergency_contact(st.session_state.current_user, name, phone, priority, relation)
            st.success(f"✅ {name} added!")
    
    with tab2:
        st.subheader("Emergency Contacts")
        contacts = st.session_state.emergency.get_emergency_contacts(st.session_state.current_user)
        
        if contacts:
            for contact in contacts:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{contact[0]}** ({contact[3]})")
                    st.caption(f"📞 {contact[1]} | Priority: {contact[2]}")
                with col2:
                    if st.button("Call", key=f"call_{contact[0]}"):
                        st.info(f"Calling {contact[0]}...")
        else:
            st.info("No emergency contacts added")
    
    with tab3:
        st.subheader("🆘 SOS Emergency Alert")
        st.warning("⚠️ This will immediately alert all emergency contacts!")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=3.1357)
        with col2:
            lon = st.number_input("Longitude", value=101.6880)
        
        if st.button("🚨 TRIGGER SOS", use_container_width=True, type="primary"):
            results = st.session_state.emergency.trigger_sos(st.session_state.current_user, lat, lon)
            st.success("✅ SOS triggered! Emergency contacts notified.")
            
            for result in results:
                st.write(f"📞 {result['contact']}: {result['status']}")

def show_geofencing_page():
    """Geofencing UI"""
    st.markdown("<h2 style='color:#FF5733;'>📍 GEOFENCING & LOCATION</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Create Safe Zone", "📍 Location History", "⚠️ Violations"])
    
    with tab1:
        st.subheader("Create Safe Zone")
        zone_name = st.text_input("Zone Name (e.g., Home)")
        lat = st.number_input("Latitude", value=3.1357)
        lon = st.number_input("Longitude", value=101.6880)
        radius = st.number_input("Radius (meters)", min_value=50, max_value=5000, value=500)
        
        if st.button("✅ Create Zone", use_container_width=True, type="primary"):
            st.session_state.geo_system.create_safe_zone(st.session_state.current_user, zone_name, lat, lon, radius)
            st.success(f"✅ {zone_name} created!")
    
    with tab2:
        st.subheader("Location History")
        history = st.session_state.geo_system.get_location_history(st.session_state.current_user, hours=24)
        
        if history:
            for lat, lon, timestamp in history:
                st.write(f"📍 {lat:.4f}, {lon:.4f} @ {timestamp}")
        else:
            st.info("No location history")
    
    with tab3:
        st.subheader("Safe Zones")
        zones = st.session_state.geo_system.get_safe_zones(st.session_state.current_user)
        
        if zones:
            for zone in zones:
                st.write(f"**{zone[0]}** - {zone[3]}m radius")
                st.caption(f"📍 {zone[1]:.4f}, {zone[2]:.4f}")
        else:
            st.info("No safe zones created")

def show_smart_home_page():
    """Smart Home Integration UI"""
    st.markdown("<h2 style='color:#FF5733;'>🏠 SMART HOME CONTROL</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Device", "💡 Control", "🤖 Routines", "⚠️ Alerts"])
    
    with tab1:
        st.subheader("Add Smart Device")
        device_id = st.text_input("Device ID")
        device_name = st.text_input("Device Name")
        device_type = st.selectbox("Device Type", ["light", "thermostat", "lock", "camera", "stove", "door", "window", "water_sensor"])
        ip_address = st.text_input("IP Address")
        port = st.number_input("Port", value=80)
        
        if st.button("✅ Add Device", use_container_width=True, type="primary"):
            st.session_state.smart_home.add_device(device_id, device_name, device_type, ip_address, port)
            st.success(f"✅ {device_name} added!")
    
    with tab2:
        st.subheader("Control Devices")
        st.info("Device control interface")
        
        if st.button("💡 Turn On Light"):
            st.session_state.smart_home.control_light("light_1", {"command": "on"})
            st.success("Light turned on!")
        
        if st.button("🌡️ Set Temperature"):
            temp = st.number_input("Temperature (°C)", value=22)
            st.session_state.smart_home.control_thermostat("thermostat_1", temp)
            st.success(f"Temperature set to {temp}°C")
    
    with tab3:
        st.subheader("Automated Routines")
        routine_name = st.text_input("Routine Name")
        trigger_type = st.selectbox("Trigger", ["time", "event"])
        
        if st.button("✅ Create Routine", use_container_width=True, type="primary"):
            st.success("Routine created!")
    
    with tab4:
        st.subheader("Safety Alerts")
        
        stove_alerts = st.session_state.smart_home.detect_stove_left_on()
        if stove_alerts:
            for alert in stove_alerts:
                st.warning(f"🚨 {alert['alert']}")
        
        door_alerts = st.session_state.smart_home.detect_door_window_open()
        if door_alerts:
            for alert in door_alerts:
                st.warning(f"⚠️ {alert['alert']}")
        
        water_alerts = st.session_state.smart_home.detect_water_leak()
        if water_alerts:
            for alert in water_alerts:
                st.error(f"🚨 {alert['alert']}")
        
        if not stove_alerts and not door_alerts and not water_alerts:
            st.success("✅ All systems normal")
