import streamlit as st
from datetime import datetime
from config import TIMEZONE

def show_nutrition_page():
    """Nutrition Tracking UI"""
    st.markdown("<h2 style='color:#FF5733;'>🍽️ NUTRITION TRACKING</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Log Meal", "💧 Water Intake", "📊 Daily Analysis", "🛒 Grocery List"])
    
    with tab1:
        st.subheader("Log Meal")
        meal_name = st.text_input("Meal Name (e.g., Breakfast)")
        food_items = st.multiselect("Food Items", ["apple", "banana", "chicken", "rice", "broccoli", "milk", "egg", "bread", "fish", "vegetables"])
        
        if st.button("✅ Log Meal", use_container_width=True, type="primary"):
            st.session_state.nutrition.log_meal(st.session_state.current_user, meal_name, food_items)
            st.success(f"✅ {meal_name} logged!")
    
    with tab2:
        st.subheader("Water Intake")
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount (ml)", min_value=100, max_value=1000, value=250, step=50)
        
        with col2:
            if st.button("✅ Log Water", use_container_width=True, type="primary"):
                st.session_state.nutrition.log_water_intake(st.session_state.current_user, amount)
                st.success(f"✅ {amount}ml logged!")
        
        daily_water = st.session_state.nutrition.get_daily_water_intake(st.session_state.current_user)
        st.metric("Today's Water Intake", f"{daily_water}ml / 2000ml")
        st.progress(min(daily_water / 2000, 1.0))
    
    with tab3:
        st.subheader("Daily Nutritional Analysis")
        nutrition = st.session_state.nutrition.get_daily_nutrition(st.session_state.current_user)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories", f"{nutrition['calories']:.0f}")
        with col2:
            st.metric("Protein", f"{nutrition['protein']:.1f}g")
        with col3:
            st.metric("Carbs", f"{nutrition['carbs']:.1f}g")
        with col4:
            st.metric("Fat", f"{nutrition['fat']:.1f}g")
        
        st.markdown("---")
        st.subheader("Recommendations")
        recommendations = st.session_state.nutrition.get_nutrition_recommendations(st.session_state.current_user)
        
        for nutrient, data in recommendations.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{nutrient.upper()}**")
            with col2:
                st.write(f"{data['actual']:.0f} / {data['recommended']:.0f}")
            with col3:
                st.write(f"{data['status']} {data['percentage']:.0f}%")
    
    with tab4:
        st.subheader("Grocery List")
        grocery_list = st.session_state.nutrition.generate_grocery_list(st.session_state.current_user, days=7)
        
        if grocery_list:
            st.write("**Items to buy (based on last 7 days):**")
            for item, count in grocery_list:
                st.write(f"- {item} (used {count}x)")
        else:
            st.info("No meals logged yet")

def show_activity_page():
    """Activity Recognition UI"""
    st.markdown("<h2 style='color:#FF5733;'>🚶 ACTIVITY TRACKING</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Log Activity", "📊 Summary", "⚠️ Alerts"])
    
    with tab1:
        st.subheader("Log Activity")
        activity_type = st.selectbox("Activity Type", ["walking", "running", "sitting", "sleeping", "exercise", "other"])
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
        
        if st.button("✅ Log Activity", use_container_width=True, type="primary"):
            st.session_state.activity.log_activity(st.session_state.current_user, activity_type, duration)
            st.success(f"✅ {activity_type} for {duration}min logged!")
    
    with tab2:
        st.subheader("Activity Summary (Last 7 Days)")
        summary = st.session_state.activity.get_activity_summary(st.session_state.current_user, days=7)
        
        if summary:
            for activity_type, count, total_minutes in summary:
                st.write(f"**{activity_type}**: {count} times, {total_minutes}min total")
        else:
            st.info("No activities logged")
    
    with tab3:
        st.subheader("Activity Alerts")
        
        inactivity = st.session_state.activity.detect_unusual_inactivity(st.session_state.current_user)
        if inactivity.get("inactive"):
            st.warning(f"⚠️ {inactivity.get('alert', 'Unusual inactivity detected')}")
        else:
            st.success(f"✅ Active - {inactivity.get('hours_inactive', 0):.1f}h since last activity")
        
        sleep_check = st.session_state.activity.detect_excessive_sleep(st.session_state.current_user)
        if sleep_check.get("excessive"):
            st.warning(f"⚠️ {sleep_check.get('alert', 'Excessive sleep detected')}")
        else:
            st.success(f"✅ Sleep normal - {sleep_check.get('sleep_hours', 0):.1f}h today")
        
        anomaly = st.session_state.activity.detect_movement_pattern_anomaly(st.session_state.current_user)
        if anomaly.get("anomaly"):
            st.warning("⚠️ Unusual movement pattern detected")
            for anom in anomaly.get("anomalies", []):
                st.write(f"Hour {anom['hour']}: Expected {anom['expected']:.0f}, Got {anom['actual']}")
