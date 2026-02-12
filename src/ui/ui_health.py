import streamlit as st
from datetime import datetime
from config import TIMEZONE

def show_vital_signs_page():
    """Vital Signs Tracking UI"""
    st.markdown("<h2 style='color:#FF5733;'>❤️ VITAL SIGNS MONITORING</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Log Vitals", "📈 History", "⚠️ Alerts"])
    
    with tab1:
        st.subheader("Log Vital Signs")
        col1, col2 = st.columns(2)
        
        with col1:
            vital_type = st.selectbox("Vital Type", ["heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic", "temperature", "blood_oxygen"])
            value = st.number_input("Value", min_value=0.0, max_value=300.0)
        
        with col2:
            units = {
                "heart_rate": "bpm",
                "blood_pressure_systolic": "mmHg",
                "blood_pressure_diastolic": "mmHg",
                "temperature": "°C",
                "blood_oxygen": "%"
            }
            unit = units.get(vital_type, "")
            st.metric("Unit", unit)
        
        if st.button("✅ Record Vital Sign", use_container_width=True, type="primary"):
            st.session_state.vital_tracker.add_vital_sign(st.session_state.current_user, vital_type, value, unit)
            st.success(f"✅ {vital_type}: {value} {unit} recorded!")
    
    with tab2:
        st.subheader("Vital Signs History")
        vitals = st.session_state.vital_tracker.get_vital_signs(st.session_state.current_user, days=7)
        
        if vitals:
            for vital_type, value, unit, timestamp in vitals:
                st.write(f"**{vital_type}**: {value} {unit} @ {timestamp}")
        else:
            st.info("No vital signs recorded yet")
    
    with tab3:
        st.subheader("Abnormal Readings Alert")
        alerts = st.session_state.vital_tracker.check_abnormal_readings(st.session_state.current_user)
        
        if alerts:
            for alert in alerts:
                st.warning(f"⚠️ {alert['vital']}: {alert['value']} {alert['unit']} (Abnormal)")
        else:
            st.success("✅ All vital signs are normal!")

def show_medication_page():
    """Medication Management UI"""
    st.markdown("<h2 style='color:#FF5733;'>💊 MEDICATION MANAGEMENT</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Medication", "📋 Active Meds", "✅ Log Taken", "📊 Compliance"])
    
    with tab1:
        st.subheader("Add New Medication")
        name = st.text_input("Medication Name")
        dosage = st.text_input("Dosage (e.g., 100mg)")
        frequency = st.selectbox("Frequency", ["once", "daily", "twice daily", "three times daily"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date (optional)")
        notes = st.text_area("Notes")
        
        if st.button("✅ Add Medication", use_container_width=True, type="primary"):
            st.session_state.med_manager.add_medication(st.session_state.current_user, name, dosage, frequency, start_date, end_date, notes)
            st.success(f"✅ {name} added!")
    
    with tab2:
        st.subheader("Active Medications")
        meds = st.session_state.med_manager.get_active_medications(st.session_state.current_user)
        
        if meds:
            for med in meds:
                st.write(f"**{med[0]}** - {med[1]} {med[2]}")
                st.caption(f"Notes: {med[4] if med[4] else 'None'}")
        else:
            st.info("No active medications")
    
    with tab3:
        st.subheader("Log Medication Taken")
        meds = st.session_state.med_manager.get_active_medications(st.session_state.current_user)
        
        if meds:
            med_names = [m[0] for m in meds]
            selected_med = st.selectbox("Select Medication", med_names)
            
            if st.button("✅ Mark as Taken", use_container_width=True, type="primary"):
                st.session_state.med_manager.log_medication_taken(st.session_state.current_user, selected_med)
                st.success(f"✅ {selected_med} marked as taken!")
        else:
            st.info("No medications to log")
    
    with tab4:
        st.subheader("Medication Compliance")
        compliance = st.session_state.med_manager.get_medication_compliance(st.session_state.current_user)
        st.metric("Compliance Rate (7 days)", f"{compliance:.1f}%")
        
        refills = st.session_state.med_manager.check_refill_needed(st.session_state.current_user)
        if refills:
            st.warning("⚠️ Medications needing refill:")
            for refill in refills:
                st.write(f"- {refill['medication']} ({refill['days_left']} days left)")

def show_mood_page():
    """Mood & Mental Health UI"""
    st.markdown("<h2 style='color:#FF5733;'>😊 MOOD & MENTAL HEALTH</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["😊 Daily Check-in", "📈 Trends", "🧠 Depression Screening", "🎮 Cognitive Games"])
    
    with tab1:
        st.subheader("Daily Mood Check-in")
        mood_emoji = st.selectbox("How are you feeling?", ["😄", "😊", "😐", "😔", "😢"])
        mood_text = st.selectbox("Mood", ["Very Happy", "Happy", "Neutral", "Sad", "Very Sad"])
        notes = st.text_area("Any notes?")
        
        if st.button("✅ Log Mood", use_container_width=True, type="primary"):
            st.session_state.mood.log_mood(st.session_state.current_user, mood_emoji, mood_text, notes)
            st.success("✅ Mood logged!")
    
    with tab2:
        st.subheader("Mood Trends")
        trends = st.session_state.mood.get_mood_trends(st.session_state.current_user)
        st.metric("Trend", trends["trend"])
        st.metric("Average Mood", f"{trends['average_mood']}/5")
        
        if trends["mood_scores"]:
            st.line_chart(trends["mood_scores"])
    
    with tab3:
        st.subheader("PHQ-9 Depression Screening")
        st.info("Answer 9 questions (0=Not at all, 3=Nearly every day)")
        
        responses = []
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself",
            "Trouble concentrating on things",
            "Moving or speaking slowly/restlessly",
            "Thoughts that you'd be better off dead"
        ]
        
        for i, q in enumerate(questions):
            response = st.slider(q, 0, 3, 0, key=f"phq9_{i}")
            responses.append(response)
        
        if st.button("✅ Submit Screening", use_container_width=True, type="primary"):
            result = st.session_state.mood.run_depression_screening(st.session_state.current_user, responses)
            st.metric("PHQ-9 Score", result["score"])
            st.metric("Severity", result["severity"])
            st.info(result["recommendation"])
    
    with tab4:
        st.subheader("Cognitive Games")
        games = st.session_state.mood.get_cognitive_games()
        
        for game in games:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{game['name']}** - {game['description']}")
                st.caption(f"Difficulty: {game['difficulty']} | Duration: {game['duration_minutes']}min")
            with col2:
                if st.button("Play", key=f"game_{game['name']}"):
                    st.info(f"Starting {game['name']}...")
