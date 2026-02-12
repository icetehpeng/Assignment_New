import streamlit as st
from datetime import datetime
from config import TIMEZONE

class NutritionTracker:
    def __init__(self, db_conn, db_available):
        self.db_conn = db_conn
        self.db_available = db_available
        
        # Nutritional database (simplified)
        self.food_database = {
            "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
            "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.3},
            "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fat": 0.3},
            "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
            "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3},
            "egg": {"calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3},
        }
    
    def log_meal(self, username, meal_name, food_items, timestamp=None):
        """Log a meal with food items"""
        if timestamp is None:
            timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO meals (username, meal_name, food_items, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (username, meal_name, str(food_items), timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging meal: {e}")
        
        if "meals" not in st.session_state:
            st.session_state.meals = []
        
        st.session_state.meals.append({
            "username": username,
            "meal_name": meal_name,
            "food_items": food_items,
            "timestamp": timestamp
        })
        return True
    
    def log_water_intake(self, username, amount_ml, timestamp=None):
        """Log water intake"""
        if timestamp is None:
            timestamp = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    INSERT INTO water_logs (username, amount_ml, timestamp)
                    VALUES (%s, %s, %s)
                """, (username, amount_ml, timestamp))
                self.db_conn.commit()
                return True
            except Exception as e:
                print(f"Error logging water: {e}")
        
        if "water_logs" not in st.session_state:
            st.session_state.water_logs = []
        
        st.session_state.water_logs.append({
            "username": username,
            "amount_ml": amount_ml,
            "timestamp": timestamp
        })
        return True
    
    def get_daily_nutrition(self, username):
        """Get daily nutritional summary"""
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT food_items FROM meals
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                meals = cursor.fetchall()
            except Exception as e:
                meals = []
        else:
            if "meals" not in st.session_state:
                meals = []
            else:
                meals = [m for m in st.session_state.meals if m["username"] == username]
        
        for meal in meals:
            food_items = meal[0] if isinstance(meal, tuple) else meal.get("food_items", [])
            if isinstance(food_items, str):
                food_items = eval(food_items)
            
            for food in food_items:
                if food.lower() in self.food_database:
                    nutrition = self.food_database[food.lower()]
                    for key in totals:
                        totals[key] += nutrition.get(key, 0)
        
        return totals
    
    def get_daily_water_intake(self, username):
        """Get daily water intake"""
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT SUM(amount_ml) FROM water_logs
                    WHERE username = %s AND DATE(timestamp) = CURDATE()
                """, (username,))
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
            except Exception as e:
                return 0
        
        if "water_logs" not in st.session_state:
            return 0
        
        logs = [w for w in st.session_state.water_logs if w["username"] == username]
        return sum(w["amount_ml"] for w in logs)
    
    def get_nutrition_recommendations(self, username, age=65, weight_kg=70):
        """Get personalized nutrition recommendations"""
        daily_nutrition = self.get_daily_nutrition(username)
        daily_water = self.get_daily_water_intake(username)
        
        # Recommended values for elderly (simplified)
        recommendations = {
            "calories": 2000,
            "protein": 50,  # grams
            "carbs": 250,   # grams
            "fat": 65,      # grams
            "water": 2000   # ml
        }
        
        analysis = {}
        for nutrient, recommended in recommendations.items():
            if nutrient == "water":
                actual = daily_water
            else:
                actual = daily_nutrition.get(nutrient, 0)
            
            percentage = (actual / recommended * 100) if recommended > 0 else 0
            analysis[nutrient] = {
                "actual": actual,
                "recommended": recommended,
                "percentage": round(percentage, 1),
                "status": "✅" if 80 <= percentage <= 120 else "⚠️" if percentage < 80 else "⚠️"
            }
        
        return analysis
    
    def generate_grocery_list(self, username, days=7):
        """Generate grocery list based on meal history"""
        grocery_list = {}
        
        if self.db_available:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("""
                    SELECT food_items FROM meals
                    WHERE username = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """, (username, days))
                meals = cursor.fetchall()
            except Exception as e:
                meals = []
        else:
            if "meals" not in st.session_state:
                meals = []
            else:
                meals = [m for m in st.session_state.meals if m["username"] == username]
        
        for meal in meals:
            food_items = meal[0] if isinstance(meal, tuple) else meal.get("food_items", [])
            if isinstance(food_items, str):
                food_items = eval(food_items)
            
            for food in food_items:
                if food not in grocery_list:
                    grocery_list[food] = 0
                grocery_list[food] += 1
        
        return sorted(grocery_list.items(), key=lambda x: x[1], reverse=True)
