import streamlit as st
import datetime
import json
import os
import random
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="PPL Split Fitness Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# File paths for each data type
WORKOUTS_FILE = DATA_DIR / "workouts.json" 
MEALS_FILE = DATA_DIR / "meals.json"
FOOD_DATABASE_FILE = DATA_DIR / "food_database.json"
WEEKLY_PLAN_FILE = DATA_DIR / "weekly_plan.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
HABITS_FILE = DATA_DIR / "habits.json"
HABIT_LOGS_FILE = DATA_DIR / "habit_logs.json"

# Initialize data files if they don't exist
def init_data_files():
    # Initialize workout tracking
    if not WORKOUTS_FILE.exists():
        with open(WORKOUTS_FILE, "w") as f:
            json.dump([], f)
    
    # Initialize meal tracking
    if not MEALS_FILE.exists():
        with open(MEALS_FILE, "w") as f:
            json.dump([], f)
    
    # Initialize food database (for auto calorie counting)
    if not FOOD_DATABASE_FILE.exists():
        sample_foods = [
            {
                "id": "1",
                "name": "Chicken Breast",
                "serving_size": "100g",
                "calories": 165,
                "protein": 31,
                "carbs": 0,
                "fat": 3.6
            },
            {
                "id": "2",
                "name": "Brown Rice",
                "serving_size": "100g cooked",
                "calories": 112,
                "protein": 2.6,
                "carbs": 23,
                "fat": 0.9
            },
            {
                "id": "3",
                "name": "Broccoli",
                "serving_size": "100g",
                "calories": 34,
                "protein": 2.8,
                "carbs": 6.6,
                "fat": 0.4
            },
            {
                "id": "4",
                "name": "Whole Eggs",
                "serving_size": "1 large egg",
                "calories": 72,
                "protein": 6.3,
                "carbs": 0.4,
                "fat": 5
            },
            {
                "id": "5",
                "name": "Salmon",
                "serving_size": "100g",
                "calories": 208,
                "protein": 20,
                "carbs": 0,
                "fat": 13
            }
        ]
        with open(FOOD_DATABASE_FILE, "w") as f:
            json.dump(sample_foods, f, indent=2)
    
    # Initialize daily habits tracking
    if not HABITS_FILE.exists():
        default_habits = [
            {
                "id": "1",
                "name": "Morning Meditation",
                "type": "morning",
                "time": "06:00",
                "description": "10 minutes of mindful meditation to start the day",
                "active": True
            },
            {
                "id": "2",
                "name": "Drink Water",
                "type": "recurring",
                "frequency": "every 2 hours",
                "description": "Drink a glass of water throughout the day",
                "target": 8,
                "unit": "glasses",
                "active": True
            },
            {
                "id": "3",
                "name": "Early Bedtime",
                "type": "evening",
                "time": "22:00",
                "description": "Go to bed early for better recovery",
                "active": True
            },
            {
                "id": "4",
                "name": "Read",
                "type": "evening",
                "time": "21:00",
                "description": "Read for 20 minutes before bed",
                "active": True
            }
        ]
        with open(HABITS_FILE, "w") as f:
            json.dump(default_habits, f, indent=2)
    
    # Initialize habit logs
    if not HABIT_LOGS_FILE.exists():
        with open(HABIT_LOGS_FILE, "w") as f:
            json.dump([], f)
    
    # Initialize weekly workout plan template
    if not WEEKLY_PLAN_FILE.exists():
        default_plan = {
            "Monday": {
                "type": "Rest",
                "is_rest_day": True,
                "exercises": []
            },
            "Tuesday": {
                "type": "Push",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Bench Press", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Shoulder Press", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Tricep Extensions", "sets": 3, "reps": "10-12", "notes": ""}
                ]
            },
            "Wednesday": {
                "type": "Pull",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Pull-ups", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Barbell Rows", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Bicep Curls", "sets": 3, "reps": "10-12", "notes": ""}
                ]
            },
            "Thursday": {
                "type": "Legs",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Squats", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Deadlifts", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Leg Extensions", "sets": 3, "reps": "10-12", "notes": ""}
                ]
            },
            "Friday": {
                "type": "Push",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Incline Bench Press", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Lateral Raises", "sets": 4, "reps": "10-12", "notes": ""},
                    {"name": "Dips", "sets": 3, "reps": "8-10", "notes": ""}
                ]
            },
            "Saturday": {
                "type": "Pull",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Lat Pulldowns", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Face Pulls", "sets": 3, "reps": "12-15", "notes": ""},
                    {"name": "Hammer Curls", "sets": 3, "reps": "10-12", "notes": ""}
                ]
            },
            "Sunday": {
                "type": "Legs",
                "is_rest_day": False,
                "exercises": [
                    {"name": "Front Squats", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Romanian Deadlifts", "sets": 4, "reps": "8-10", "notes": ""},
                    {"name": "Leg Press", "sets": 3, "reps": "10-12", "notes": ""},
                    {"name": "Calf Raises", "sets": 4, "reps": "15-20", "notes": ""}
                ]
            }
        }
        with open(WEEKLY_PLAN_FILE, "w") as f:
            json.dump(default_plan, f, indent=2)
    
    # Initialize settings (calorie goals, etc.)
    if not SETTINGS_FILE.exists():
        default_settings = {
            "daily_calorie_goal": 2000,
            "protein_goal": 160,  # in grams
            "carbs_goal": 200,    # in grams
            "fat_goal": 65,       # in grams
            "water_goal": 8,      # in glasses
            "wakeup_time": "06:00",
            "reminder_time": "07:00",
            "bedtime": "22:00",
            "enable_notifications": True,
            "weight_unit": "kg"
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f, indent=2)

# Data loading functions
def load_data(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Data saving functions
def save_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# Load settings function
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_settings = {
            "daily_calorie_goal": 2000,
            "protein_goal": 160,
            "carbs_goal": 200,
            "fat_goal": 65,
            "water_goal": 8,
            "wakeup_time": "06:00",
            "reminder_time": "07:00",
            "bedtime": "22:00",
            "enable_notifications": True,
            "weight_unit": "kg"
        }
        return default_settings

# Save settings function
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# Function to generate random motivational messages
def get_motivational_message():
    messages = [
        "No excuses. Get up and do your workout today!",
        "Success starts with discipline. Stick to your plan.",
        "Today's workout is tomorrow's progress.",
        "You're stronger than you think. Push yourself!",
        "Every rep counts. Every meal matters. Stay focused.",
        "Your body achieves what your mind believes.",
        "The only bad workout is the one that didn't happen.",
        "Small daily improvements lead to stunning results.",
        "Discipline equals freedom. Stay on track.",
        "Water. Sleep. Nutrition. Training. Don't skip the basics."
    ]
    return random.choice(messages)

# Skin care tips
def get_skincare_tip():
    tips = [
        "Always wear sunscreen, even on cloudy days. UV damage is cumulative.",
        "Hydrate from within: drink plenty of water for clear skin.",
        "Never sleep with makeup on, it clogs pores and causes breakouts.",
        "Use a gentle cleanser morning and night.",
        "Exfoliate 1-2 times per week to remove dead skin cells.",
        "Include antioxidants like Vitamin C in your skincare routine.",
        "Change your pillowcase at least once a week.",
        "Pat your face dry instead of rubbing to avoid irritation.",
        "Use a moisturizer appropriate for your skin type daily.",
        "Hands off! Avoid touching your face to prevent transferring bacteria."
    ]
    return random.choice(tips)

# Initialize the data files
init_data_files()

# Load all settings
settings = load_settings()

# Sidebar for navigation
st.sidebar.title("💪 PPL Split Fitness Tracker")
st.sidebar.caption("Push-Pull-Legs workout plan with calorie tracking")
selected_tab = st.sidebar.radio(
    "Navigate to:", 
    ["Dashboard", "Workout Plan", "Workout Log", "Meal Tracker", "Daily Habits", "Settings"]
)

# Current date selection
today = datetime.date.today()
selected_date = st.sidebar.date_input("Select Date", today)
selected_date_str = selected_date.strftime("%Y-%m-%d")

# Motivational message in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Today's Motivation")
st.sidebar.info(get_motivational_message())

# Show notification for morning routine
current_time = datetime.datetime.now().time()
wakeup_time_str = settings.get("wakeup_time", "06:00")
morning_time = datetime.time(int(wakeup_time_str.split(":")[0]), int(wakeup_time_str.split(":")[1]))

bedtime_str = settings.get("bedtime", "22:00") 
evening_time = datetime.time(int(bedtime_str.split(":")[0]), int(bedtime_str.split(":")[1]))

# Calculate one hour before bedtime for evening reminder
evening_reminder_hour = int(bedtime_str.split(":")[0]) - 1
evening_reminder_minute = int(bedtime_str.split(":")[1])
if evening_reminder_hour < 0:
    evening_reminder_hour = 23
evening_reminder_time = datetime.time(evening_reminder_hour, evening_reminder_minute)

# Dashboard Tab
if selected_tab == "Dashboard":
    st.title("💪 PPL Fitness Dashboard")
    st.markdown("Your Push-Pull-Legs training and nutrition tracker")
    
    # Load data
    workouts = load_data(WORKOUTS_FILE)
    meals = load_data(MEALS_FILE)
    
    # Morning notification - show between wake up time and +3 hours
    three_hours_after_wakeup = (
        datetime.datetime.combine(datetime.date.today(), morning_time) + 
        datetime.timedelta(hours=3)
    ).time()
    
    if morning_time <= current_time <= three_hours_after_wakeup:
        st.success(f"🌞 **Morning Routine Reminder!** (Wake up: {wakeup_time_str})\n\n"
                 "1. Drink a glass of water\n"
                 "2. 10-minute meditation session\n"
                 "3. 5 minutes of stretching\n"
                 "4. Healthy breakfast with protein")
    
    # Evening notification - show 1 hour before bedtime
    if evening_reminder_time <= current_time <= evening_time:
        st.info(f"🌙 **Evening Routine Reminder!** (Bedtime: {bedtime_str})\n\n"
               "1. Avoid screen time 30 minutes before bed\n"
               "2. Set out workout clothes for tomorrow\n"
               "3. Complete your evening skincare routine\n"
               "4. " + get_skincare_tip())
    
    # Filter data for selected date
    workouts_today = [w for w in workouts if w.get("date", "") == selected_date_str]
    meals_today = [m for m in meals if m.get("date", "") == selected_date_str]
    
    # Calculate stats for the day
    total_cal_consumed = sum(sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) 
                             for item in m.get("food_items", [])) 
                         for m in meals_today)
    
    total_protein = sum(sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) 
                        for item in m.get("food_items", [])) 
                    for m in meals_today)
    
    total_carbs = sum(sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) 
                      for item in m.get("food_items", [])) 
                  for m in meals_today)
    
    total_fat = sum(sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) 
                    for item in m.get("food_items", [])) 
                for m in meals_today)
    
    workout_done = len(workouts_today) > 0
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cal_diff = total_cal_consumed - settings["daily_calorie_goal"]
        cal_percent = min(100, int((total_cal_consumed / settings["daily_calorie_goal"]) * 100)) if settings["daily_calorie_goal"] > 0 else 0
        st.metric(
            label="Calories", 
            value=f"{total_cal_consumed} / {settings['daily_calorie_goal']}",
            delta=f"{cal_diff} kcal" if cal_diff != 0 else None
        )
        st.progress(cal_percent / 100)
        
    with col2:
        protein_percent = min(100, int((total_protein / settings["protein_goal"]) * 100)) if settings["protein_goal"] > 0 else 0
        st.metric(
            label="Protein", 
            value=f"{total_protein:.1f}g / {settings['protein_goal']}g",
            delta=None
        )
        st.progress(protein_percent / 100)
        
    with col3:
        workout_status = "Complete" if workout_done else "Not Done"
        st.metric(
            label="Workout", 
            value=workout_status,
            delta=None
        )
        
    with col4:
        # Get day of week and show scheduled workout type
        weekly_plan = load_data(WEEKLY_PLAN_FILE)
        day_of_week = selected_date.strftime("%A")
        if day_of_week in weekly_plan:
            if weekly_plan[day_of_week]["is_rest_day"]:
                st.metric(
                    label="Today's Plan", 
                    value="Rest Day",
                    delta=None
                )
            else:
                st.metric(
                    label="Today's Plan", 
                    value=weekly_plan[day_of_week]["type"],
                    delta=None
                )
        else:
            st.metric(
                label="Today's Plan", 
                value="Not Set",
                delta=None
            )
    
    # Macro breakdown
    st.subheader("Today's Macronutrient Breakdown")
    
    # Calculate percentages
    total_macro_calories = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
    if total_macro_calories > 0:
        protein_perc = round((total_protein * 4 / total_macro_calories) * 100)
        carbs_perc = round((total_carbs * 4 / total_macro_calories) * 100)
        fat_perc = round((total_fat * 9 / total_macro_calories) * 100)
    else:
        protein_perc, carbs_perc, fat_perc = 0, 0, 0
    
    # Create columns for macro percentages
    macro_cols = st.columns(3)
    
    with macro_cols[0]:
        st.markdown(f"**Protein: {protein_perc}%**")
        st.progress(protein_perc / 100)
        st.caption(f"{total_protein:.1f}g ({total_protein * 4:.0f} kcal)")
        
    with macro_cols[1]:
        st.markdown(f"**Carbs: {carbs_perc}%**")
        st.progress(carbs_perc / 100)
        st.caption(f"{total_carbs:.1f}g ({total_carbs * 4:.0f} kcal)")
        
    with macro_cols[2]:
        st.markdown(f"**Fat: {fat_perc}%**")
        st.progress(fat_perc / 100)
        st.caption(f"{total_fat:.1f}g ({total_fat * 9:.0f} kcal)")
    
    # Today's meals
    st.subheader("Today's Meals")
    if meals_today:
        for meal in meals_today:
            with st.expander(f"{meal.get('type', 'Meal')} - {meal.get('name', 'Unnamed')}"):
                # Calculate meal totals
                meal_calories = sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                meal_protein = sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                meal_carbs = sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                meal_fat = sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                
                st.write(f"**Calories:** {meal_calories} kcal")
                st.write(f"**Macros:** P: {meal_protein:.1f}g • C: {meal_carbs:.1f}g • F: {meal_fat:.1f}g")
                
                # Food items
                if meal.get("food_items"):
                    for item in meal.get("food_items", []):
                        quantity = item.get("quantity_multiplier", 1)
                        st.write(f"• {item.get('name', 'Unknown')} ({quantity}x): "
                                f"{item.get('calories', 0) * quantity:.0f} kcal, "
                                f"P: {item.get('protein', 0) * quantity:.1f}g, "
                                f"C: {item.get('carbs', 0) * quantity:.1f}g, "
                                f"F: {item.get('fat', 0) * quantity:.1f}g")
    else:
        st.info("No meals recorded for today. Add your meals in the Meal Tracker section.")
    
    # Today's workout
    st.subheader("Today's Workout")
    if workouts_today:
        for workout in workouts_today:
            with st.expander(f"{workout.get('name', 'Workout')} - {workout.get('type', 'Unknown type')}"):
                st.write(f"**Duration:** {workout.get('duration_minutes', 0)} minutes")
                
                # Exercises
                if workout.get("exercises"):
                    st.write("**Exercises:**")
                    for i, exercise in enumerate(workout.get("exercises", [])):
                        st.write(f"{i+1}. **{exercise.get('name', 'Unknown')}**: "
                                f"{exercise.get('sets', 0)} sets x {exercise.get('reps', 0)} reps "
                                f"@ {exercise.get('weight', 0)} {settings.get('weight_unit', 'kg')}")
                        if exercise.get("notes"):
                            st.caption(f"Notes: {exercise.get('notes', '')}")
                
                # Notes
                if workout.get("notes"):
                    st.write(f"**Notes:** {workout.get('notes', '')}")
    else:
        st.info("No workout recorded for today. Log your workout in the Workout Log section.")
    
    # Skin care tip of the day
    st.subheader("Skin Care Tip of the Day")
    st.info(get_skincare_tip())

# Workout Plan Tab
elif selected_tab == "Workout Plan":
    st.title("🏋️ Weekly Workout Plan")
    
    # Load weekly plan
    weekly_plan = load_data(WEEKLY_PLAN_FILE)
    
    st.markdown("""
    This is your weekly Push/Pull/Legs (PPL) split routine with a progressive rotation pattern.
    Your current cycle is:
    - **Monday**: Rest
    - **Tuesday**: Push (Chest, Shoulders, Triceps) 
    - **Wednesday**: Pull (Back, Biceps)
    - **Thursday**: Legs (Quads, Hamstrings, Calves)
    - **Friday**: Push (Chest, Shoulders, Triceps)
    - **Saturday**: Pull (Back, Biceps)
    - **Sunday**: Legs (Quads, Hamstrings, Calves)
    
    Each week, this pattern rotates forward by one day. Next week, Tuesday will be your Rest day,
    Wednesday will be Push, and so on. This rotation helps prevent scheduling conflicts while 
    maintaining consistent recovery periods.
    
    Customize exercises, sets, and reps for each day below.
    """)
    
    # Display weekly schedule
    plan_cols = st.columns(7)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i, day in enumerate(days):
        with plan_cols[i]:
            st.subheader(day[:3])  # Show abbreviated day name
            if day in weekly_plan:
                if weekly_plan[day]["is_rest_day"]:
                    st.markdown("**Rest Day**")
                else:
                    st.markdown(f"**{weekly_plan[day]['type']}**")
                    st.caption(f"{len(weekly_plan[day]['exercises'])} exercises")
            else:
                st.markdown("Not set")
    
    # Day selector for editing plans
    st.markdown("---")
    selected_day = st.selectbox("Select day to edit:", days)
    
    if selected_day:
        # Initialize this day if it doesn't exist
        if selected_day not in weekly_plan:
            weekly_plan[selected_day] = {
                "type": "Push",
                "is_rest_day": False,
                "exercises": []
            }
        
        day_plan = weekly_plan[selected_day]
        
        # Rest day toggle
        is_rest_day = st.checkbox("Rest Day", value=day_plan.get("is_rest_day", False))
        
        if not is_rest_day:
            # Workout type
            workout_options = ["Push", "Pull", "Legs", "Full Body", "Upper Body", "Lower Body", "Cardio", "Other"]
            default_type = day_plan.get("type", "Push")
            # If the current type isn't in our list (like "Rest"), default to "Push"
            if default_type not in workout_options:
                default_type = "Push"
            
            workout_type = st.selectbox(
                "Workout Type:",
                options=workout_options,
                index=workout_options.index(default_type)
            )
            
            # Exercise editor
            st.subheader(f"Exercises for {selected_day} ({workout_type})")
            
            # Get existing exercises
            exercises = day_plan.get("exercises", [])
            
            # Add new exercise form
            with st.form(f"add_exercise_{selected_day}"):
                st.subheader("Add New Exercise")
                new_exercise_name = st.text_input("Exercise Name")
                new_exercise_sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
                new_exercise_reps = st.text_input("Reps (e.g. '8-10' or '12')", value="8-10")
                new_exercise_notes = st.text_area("Notes (equipment, form cues, etc.)")
                
                add_exercise = st.form_submit_button("Add Exercise")
                if add_exercise and new_exercise_name:
                    new_exercise = {
                        "name": new_exercise_name,
                        "sets": new_exercise_sets,
                        "reps": new_exercise_reps,
                        "notes": new_exercise_notes
                    }
                    exercises.append(new_exercise)
                    
                    # Update the plan
                    weekly_plan[selected_day] = {
                        "type": workout_type,
                        "is_rest_day": False,
                        "exercises": exercises
                    }
                    save_data(weekly_plan, WEEKLY_PLAN_FILE)
                    st.success(f"Added {new_exercise_name} to {selected_day}'s {workout_type} workout")
                    st.experimental_rerun()
            
            # Show existing exercises
            if exercises:
                st.subheader("Current Exercises")
                for i, exercise in enumerate(exercises):
                    col1, col2, col3 = st.columns([5, 3, 2])
                    
                    with col1:
                        st.markdown(f"**{exercise['name']}**")
                        if exercise.get("notes"):
                            st.caption(exercise["notes"])
                    
                    with col2:
                        st.markdown(f"{exercise['sets']} sets x {exercise['reps']} reps")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_{selected_day}_{i}"):
                            exercises.pop(i)
                            
                            # Update the plan
                            weekly_plan[selected_day]["exercises"] = exercises
                            save_data(weekly_plan, WEEKLY_PLAN_FILE)
                            st.success(f"Removed exercise from {selected_day}'s workout")
                            st.experimental_rerun()
            else:
                st.info("No exercises set up yet for this day.")
        else:
            # Update as rest day
            weekly_plan[selected_day] = {
                "type": "Rest",
                "is_rest_day": True,
                "exercises": []
            }
            save_data(weekly_plan, WEEKLY_PLAN_FILE)
            st.success(f"Updated {selected_day} as a rest day")

# Workout Log Tab
elif selected_tab == "Workout Log":
    st.title("💪 Workout Log")
    
    # Load workouts and weekly plan
    workouts = load_data(WORKOUTS_FILE)
    weekly_plan = load_data(WEEKLY_PLAN_FILE)
    
    # Find workouts for selected date
    workouts_today = [w for w in workouts if w.get("date", "") == selected_date_str]
    
    # Get day of week for selected date
    day_of_week = selected_date.strftime("%A")
    
    # Check if we have a plan for this day
    today_plan = weekly_plan.get(day_of_week, {
        "type": "Not Scheduled",
        "is_rest_day": False,
        "exercises": []
    })
    
    # Workout form
    st.subheader(f"Log Workout for {selected_date_str}")
    
    if today_plan.get("is_rest_day", False):
        st.info(f"Today ({day_of_week}) is scheduled as a Rest Day in your weekly plan.")
    
    with st.form("log_workout_form"):
        # If we already have a workout for today, show its data for editing
        existing_workout = workouts_today[0] if workouts_today else None
        
        # Workout details
        workout_name = st.text_input(
            "Workout Name", 
            value=existing_workout.get("name", today_plan.get("type", "")) if existing_workout else today_plan.get("type", "")
        )
        
        workout_options = ["Push", "Pull", "Legs", "Full Body", "Upper Body", "Lower Body", "Cardio", "Other"]
        default_type = existing_workout.get("type", today_plan.get("type", "Push")) if existing_workout else today_plan.get("type", "Push")
        # If the current type isn't in our list (like "Rest"), default to "Push"
        if default_type not in workout_options:
            default_type = "Push"
            
        workout_type = st.selectbox(
            "Workout Type",
            options=workout_options,
            index=workout_options.index(default_type)
        )
        
        duration_minutes = st.number_input(
            "Duration (minutes)", 
            min_value=1, 
            value=existing_workout.get("duration_minutes", 45) if existing_workout else 45
        )
        
        # Exercise section
        st.subheader("Exercises")
        
        # If there's an existing workout, use its exercises. Otherwise use the plan's exercises
        initial_exercises = []
        if existing_workout and "exercises" in existing_workout:
            initial_exercises = existing_workout["exercises"]
        elif not today_plan.get("is_rest_day", False) and "exercises" in today_plan:
            # Convert plan exercises to workout exercises format
            for ex in today_plan["exercises"]:
                initial_exercises.append({
                    "name": ex["name"],
                    "sets": ex["sets"],
                    "reps": ex["reps"],
                    "weight": 0,
                    "notes": ex.get("notes", "")
                })
        
        # Determine number of exercises 
        num_exercises = len(initial_exercises) if initial_exercises else 1
        num_exercises = st.number_input("Number of Exercises", min_value=1, max_value=20, value=num_exercises)
        
        exercises = []
        for i in range(num_exercises):
            st.markdown(f"##### Exercise {i+1}")
            
            # Get values from initial_exercises if available
            init_name = initial_exercises[i]["name"] if i < len(initial_exercises) else ""
            init_sets = initial_exercises[i]["sets"] if i < len(initial_exercises) else 3
            init_reps = initial_exercises[i]["reps"] if i < len(initial_exercises) else "8-10"
            init_weight = initial_exercises[i].get("weight", 0) if i < len(initial_exercises) else 0
            init_notes = initial_exercises[i].get("notes", "") if i < len(initial_exercises) else ""
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                ex_name = st.text_input("Name", value=init_name, key=f"ex_name_{i}")
            
            with col2:
                ex_sets = st.number_input("Sets", min_value=1, value=init_sets, key=f"ex_sets_{i}")
            
            col3, col4 = st.columns([1, 1])
            
            with col3:
                ex_reps = st.text_input("Reps", value=init_reps, key=f"ex_reps_{i}")
            
            with col4:
                ex_weight = st.number_input(
                    f"Weight ({settings.get('weight_unit', 'kg')})", 
                    min_value=0.0, 
                    step=2.5, 
                    value=float(init_weight), 
                    key=f"ex_weight_{i}"
                )
            
            ex_notes = st.text_input("Notes (optional)", value=init_notes, key=f"ex_notes_{i}")
            
            if ex_name:
                exercises.append({
                    "name": ex_name,
                    "sets": ex_sets,
                    "reps": ex_reps,
                    "weight": ex_weight,
                    "notes": ex_notes
                })
        
        notes = st.text_area(
            "Workout Notes", 
            value=existing_workout.get("notes", "") if existing_workout else ""
        )
        
        submit_workout = st.form_submit_button("Save Workout")
        
        if submit_workout and workout_name and exercises:
            # Create or update workout
            workout_data = {
                "id": existing_workout.get("id", str(len(workouts) + 1)) if existing_workout else str(len(workouts) + 1),
                "name": workout_name,
                "type": workout_type,
                "date": selected_date_str,
                "duration_minutes": duration_minutes,
                "exercises": exercises,
                "notes": notes,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # If existing workout, update it
            if existing_workout:
                for i, w in enumerate(workouts):
                    if w.get("id") == existing_workout.get("id"):
                        workouts[i] = workout_data
                        break
            else:
                # Add new workout
                workouts.append(workout_data)
            
            save_data(workouts, WORKOUTS_FILE)
            st.success(f"Workout saved for {selected_date_str}")
            st.experimental_rerun()
    
    # Display workout history
    st.markdown("---")
    st.subheader("Workout History")
    
    if workouts:
        # Sort by date (newest first)
        sorted_workouts = sorted(
            workouts, 
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        for workout in sorted_workouts[:10]:  # Show last 10 workouts
            workout_date = workout.get("date", "Unknown date")
            with st.expander(f"{workout_date} - {workout.get('name', 'Workout')} ({workout.get('type', 'Unknown type')})"):
                st.write(f"**Duration:** {workout.get('duration_minutes', 0)} minutes")
                
                # Exercises
                if workout.get("exercises"):
                    st.write("**Exercises:**")
                    
                    # Create a table view
                    exercise_data = []
                    for ex in workout.get("exercises", []):
                        exercise_data.append([
                            ex.get("name", ""),
                            f"{ex.get('sets', 0)} sets",
                            ex.get("reps", ""),
                            f"{ex.get('weight', 0)} {settings.get('weight_unit', 'kg')}",
                            ex.get("notes", "")
                        ])
                    
                    # Display as a table
                    st.table({
                        "Exercise": [row[0] for row in exercise_data],
                        "Sets": [row[1] for row in exercise_data],
                        "Reps": [row[2] for row in exercise_data],
                        "Weight": [row[3] for row in exercise_data],
                        "Notes": [row[4] for row in exercise_data]
                    })
                
                # Notes
                if workout.get("notes"):
                    st.write(f"**Notes:** {workout.get('notes', '')}")
                
                # Delete button
                if st.button("Delete Workout", key=f"delete_workout_{workout['id']}"):
                    workouts.remove(workout)
                    save_data(workouts, WORKOUTS_FILE)
                    st.success(f"Deleted workout from {workout_date}")
                    st.experimental_rerun()
    else:
        st.info("No workouts recorded yet. Start logging your workouts above!")
        
    # Exercise progress tracking
    st.markdown("---")
    st.subheader("Exercise Progress Tracking")
    
    if workouts:
        # Get a list of all unique exercises
        all_exercises = set()
        for workout in workouts:
            for exercise in workout.get("exercises", []):
                all_exercises.add(exercise.get("name", ""))
        
        # Sort exercises alphabetically
        sorted_exercises = sorted(list(all_exercises))
        
        if sorted_exercises:
            # Let user select an exercise to track
            selected_exercise = st.selectbox("Select exercise to track:", sorted_exercises)
            
            if selected_exercise:
                # Find all workout instances with this exercise
                exercise_history = []
                for workout in sorted(workouts, key=lambda x: x.get("date", "")):
                    workout_date = workout.get("date", "")
                    for exercise in workout.get("exercises", []):
                        if exercise.get("name", "") == selected_exercise:
                            exercise_history.append({
                                "date": workout_date,
                                "sets": exercise.get("sets", 0),
                                "reps": exercise.get("reps", ""),
                                "weight": exercise.get("weight", 0)
                            })
                
                if exercise_history:
                    st.write(f"**Progress for {selected_exercise}:**")
                    
                    # Create a progress table
                    st.table({
                        "Date": [entry["date"] for entry in exercise_history],
                        "Sets": [entry["sets"] for entry in exercise_history],
                        "Reps": [entry["reps"] for entry in exercise_history],
                        "Weight": [f"{entry['weight']} {settings.get('weight_unit', 'kg')}" for entry in exercise_history]
                    })
                    
                    # Highlight progress
                    if len(exercise_history) > 1:
                        first_weight = exercise_history[0]["weight"]
                        latest_weight = exercise_history[-1]["weight"]
                        if latest_weight > first_weight:
                            st.success(f"Great progress! You've increased your weight from {first_weight} to {latest_weight} {settings.get('weight_unit', 'kg')}.")
                        elif latest_weight < first_weight:
                            st.warning(f"Your weight has decreased from {first_weight} to {latest_weight} {settings.get('weight_unit', 'kg')}.")
                        else:
                            st.info("Your weight has remained consistent. Consider increasing the challenge!")
                else:
                    st.info(f"No history found for {selected_exercise}.")
        else:
            st.info("No exercises found in your workout history.")
    else:
        st.info("Start logging workouts to track your exercise progress.")

# Meal Tracker Tab
elif selected_tab == "Meal Tracker":
    st.title("🍽️ Meal Tracker")
    
    # Load meals and food database
    meals = load_data(MEALS_FILE)
    food_database = load_data(FOOD_DATABASE_FILE)
    
    # Tabs for different sections
    meal_tabs = st.tabs(["Log Meals", "Food Database", "Meal Templates", "Nutrition Analysis"])
    
    # Log Meals Tab
    with meal_tabs[0]:
        st.subheader(f"Log Meals for {selected_date_str}")
        
        # Get meals for today
        meals_today = [m for m in meals if m.get("date", "") == selected_date_str]
        
        # Daily nutrition summary
        if meals_today:
            # Calculate totals
            daily_calories = sum(sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) for item in m.get("food_items", [])) for m in meals_today)
            daily_protein = sum(sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) for item in m.get("food_items", [])) for m in meals_today)
            daily_carbs = sum(sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) for item in m.get("food_items", [])) for m in meals_today)
            daily_fat = sum(sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) for item in m.get("food_items", [])) for m in meals_today)
            
            # Display summary
            st.write("### Today's Nutrition Summary")
            
            # Create columns for summary
            sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
            
            with sum_col1:
                cal_percent = min(100, int((daily_calories / settings["daily_calorie_goal"]) * 100)) if settings["daily_calorie_goal"] > 0 else 0
                st.metric("Calories", f"{daily_calories} / {settings['daily_calorie_goal']}")
                st.progress(cal_percent / 100)
            
            with sum_col2:
                protein_percent = min(100, int((daily_protein / settings["protein_goal"]) * 100)) if settings["protein_goal"] > 0 else 0
                st.metric("Protein", f"{daily_protein:.1f}g / {settings['protein_goal']}g")
                st.progress(protein_percent / 100)
            
            with sum_col3:
                carbs_percent = min(100, int((daily_carbs / settings["carbs_goal"]) * 100)) if settings["carbs_goal"] > 0 else 0
                st.metric("Carbs", f"{daily_carbs:.1f}g / {settings['carbs_goal']}g")
                st.progress(carbs_percent / 100)
            
            with sum_col4:
                fat_percent = min(100, int((daily_fat / settings["fat_goal"]) * 100)) if settings["fat_goal"] > 0 else 0
                st.metric("Fat", f"{daily_fat:.1f}g / {settings['fat_goal']}g")
                st.progress(fat_percent / 100)
            
            st.markdown("---")
        
        # Form to add a new meal
        with st.form("add_meal_form"):
            st.write("### Add New Meal")
            
            meal_name = st.text_input("Meal Name (e.g., 'Post-workout shake')")
            meal_type = st.selectbox(
                "Meal Type",
                options=["Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"]
            )
            meal_time = st.time_input("Time", datetime.time(12, 0))
            
            # Food selection
            st.write("### Add Food Items")
            
            # Option to select from database or enter manually
            food_entry_method = st.radio("Food Entry Method:", ["Select from Database", "Enter Manually"])
            
            food_items = []
            
            if food_entry_method == "Select from Database":
                if food_database:
                    # Get food database sorted alphabetically
                    sorted_foods = sorted(food_database, key=lambda x: x.get("name", "").lower())
                    
                    # Let user select multiple foods
                    num_foods = st.number_input("Number of Food Items", min_value=1, max_value=15, value=1)
                    
                    for i in range(num_foods):
                        st.markdown(f"#### Food Item {i+1}")
                        
                        # Create a select box with food names
                        food_names = [food["name"] for food in sorted_foods]
                        selected_food_name = st.selectbox(
                            "Select Food", 
                            options=food_names,
                            key=f"food_select_{i}"
                        )
                        
                        # Find the selected food in the database
                        selected_food = next((food for food in sorted_foods if food["name"] == selected_food_name), None)
                        
                        if selected_food:
                            # Display food details
                            st.write(f"**Serving Size:** {selected_food.get('serving_size', '')}")
                            st.write(f"**Nutrition (per serving):** {selected_food.get('calories', 0)} kcal, "
                                    f"P: {selected_food.get('protein', 0)}g, C: {selected_food.get('carbs', 0)}g, F: {selected_food.get('fat', 0)}g")
                            
                            # Allow adjusting quantity
                            quantity = st.number_input(
                                "Quantity (servings)", 
                                min_value=0.25, 
                                max_value=10.0, 
                                value=1.0, 
                                step=0.25,
                                key=f"food_quantity_{i}"
                            )
                            
                            # Add to food items
                            if quantity > 0:
                                food_item = selected_food.copy()
                                food_item["quantity_multiplier"] = quantity
                                food_items.append(food_item)
                else:
                    st.warning("No foods in database. Please add foods in the Food Database tab first.")
            else:  # Manual entry
                num_foods = st.number_input("Number of Food Items", min_value=1, max_value=15, value=1)
                
                for i in range(num_foods):
                    st.markdown(f"#### Food Item {i+1}")
                    food_name = st.text_input("Food Name", key=f"manual_name_{i}")
                    serving_size = st.text_input("Serving Size (e.g., '100g', '1 cup')", key=f"manual_serving_{i}")
                    food_calories = st.number_input("Calories", min_value=0, key=f"manual_cal_{i}")
                    food_protein = st.number_input("Protein (g)", min_value=0.0, step=0.1, key=f"manual_protein_{i}")
                    food_carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1, key=f"manual_carbs_{i}")
                    food_fat = st.number_input("Fat (g)", min_value=0.0, step=0.1, key=f"manual_fat_{i}")
                    quantity = st.number_input(
                        "Quantity (servings)", 
                        min_value=0.25, 
                        max_value=10.0, 
                        value=1.0, 
                        step=0.25,
                        key=f"manual_quantity_{i}"
                    )
                    
                    if food_name:
                        food_items.append({
                            "name": food_name,
                            "serving_size": serving_size,
                            "calories": food_calories,
                            "protein": food_protein,
                            "carbs": food_carbs,
                            "fat": food_fat,
                            "quantity_multiplier": quantity
                        })
            
            notes = st.text_area("Notes (optional)")
            save_as_template = st.checkbox("Save as template for future use")
            
            submit_meal = st.form_submit_button("Save Meal")
            
            if submit_meal and meal_name and food_items:
                # Calculate totals for confirmation
                total_calories = sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) for item in food_items)
                total_protein = sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) for item in food_items)
                total_carbs = sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) for item in food_items)
                total_fat = sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) for item in food_items)
                
                # Create meal object
                new_meal = {
                    "id": str(len(meals) + 1),
                    "name": meal_name,
                    "type": meal_type,
                    "date": selected_date_str,
                    "time": meal_time.strftime("%H:%M"),
                    "food_items": food_items,
                    "notes": notes,
                    "is_template": save_as_template,
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                meals.append(new_meal)
                save_data(meals, MEALS_FILE)
                
                st.success(f"Added {meal_name} with {len(food_items)} items ({total_calories} kcal, P:{total_protein:.1f}g, C:{total_carbs:.1f}g, F:{total_fat:.1f}g)")
                st.experimental_rerun()
        
        # Display meals for today
        st.markdown("---")
        st.subheader(f"Meals for {selected_date_str}")
        
        if meals_today:
            # Sort by time
            sorted_meals = sorted(meals_today, key=lambda x: x.get("time", "00:00"))
            
            for meal in sorted_meals:
                meal_time = meal.get("time", "")
                meal_title = f"{meal_time} - {meal.get('type', 'Meal')}: {meal.get('name', 'Unnamed')}"
                
                with st.expander(meal_title):
                    # Calculate meal totals
                    meal_calories = sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                    meal_protein = sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                    meal_carbs = sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                    meal_fat = sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) for item in meal.get("food_items", []))
                    
                    st.write(f"**Total Nutrition:** {meal_calories} kcal, P: {meal_protein:.1f}g, C: {meal_carbs:.1f}g, F: {meal_fat:.1f}g")
                    
                    # Food items
                    st.write("**Food Items:**")
                    for item in meal.get("food_items", []):
                        quantity = item.get("quantity_multiplier", 1)
                        st.write(f"• {item.get('name', 'Unknown')} "
                                f"({quantity}x {item.get('serving_size', '')}): "
                                f"{item.get('calories', 0) * quantity:.0f} kcal, "
                                f"P: {item.get('protein', 0) * quantity:.1f}g, "
                                f"C: {item.get('carbs', 0) * quantity:.1f}g, "
                                f"F: {item.get('fat', 0) * quantity:.1f}g")
                    
                    # Notes
                    if meal.get("notes"):
                        st.write(f"**Notes:** {meal.get('notes', '')}")
                    
                    # Delete button
                    if st.button("Delete Meal", key=f"delete_meal_{meal['id']}"):
                        meals.remove(meal)
                        save_data(meals, MEALS_FILE)
                        st.success(f"Deleted: {meal.get('name', 'Unnamed meal')}")
                        st.experimental_rerun()
        else:
            st.info("No meals recorded for today yet. Add your first meal using the form above.")
    
    # Food Database Tab
    with meal_tabs[1]:
        st.subheader("Food Database")
        st.write("Manage your foods for automatic calorie counting.")
        
        # Form to add new food
        with st.form("add_food_form"):
            st.write("### Add New Food")
            
            food_name = st.text_input("Food Name")
            serving_size = st.text_input("Serving Size (e.g., '100g', '1 cup')")
            calories = st.number_input("Calories", min_value=0)
            protein = st.number_input("Protein (g)", min_value=0.0, step=0.1)
            carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1)
            fat = st.number_input("Fat (g)", min_value=0.0, step=0.1)
            
            submit_food = st.form_submit_button("Add to Database")
            
            if submit_food and food_name:
                # Check if food already exists
                existing_food = next((f for f in food_database if f.get("name", "").lower() == food_name.lower()), None)
                
                if existing_food:
                    st.warning(f"{food_name} already exists in the database. Please use a different name or update the existing entry.")
                else:
                    # Create new food
                    new_food = {
                        "id": str(len(food_database) + 1),
                        "name": food_name,
                        "serving_size": serving_size,
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat
                    }
                    
                    food_database.append(new_food)
                    save_data(food_database, FOOD_DATABASE_FILE)
                    st.success(f"Added {food_name} to database")
                    st.experimental_rerun()
        
        # Display and manage foods
        st.markdown("---")
        st.subheader("Manage Foods")
        
        if food_database:
            # Filter option
            search_term = st.text_input("Search foods", "")
            
            # Sort and filter foods
            sorted_foods = sorted(food_database, key=lambda x: x.get("name", "").lower())
            
            if search_term:
                filtered_foods = [f for f in sorted_foods if search_term.lower() in f.get("name", "").lower()]
            else:
                filtered_foods = sorted_foods
            
            if filtered_foods:
                for food in filtered_foods:
                    col1, col2, col3 = st.columns([3, 4, 1])
                    
                    with col1:
                        st.write(f"**{food.get('name', '')}**")
                        st.caption(f"Serving: {food.get('serving_size', '')}")
                    
                    with col2:
                        st.write(f"{food.get('calories', 0)} kcal | "
                                f"P: {food.get('protein', 0)}g | "
                                f"C: {food.get('carbs', 0)}g | "
                                f"F: {food.get('fat', 0)}g")
                    
                    with col3:
                        if st.button("Delete", key=f"delete_food_{food['id']}"):
                            food_database.remove(food)
                            save_data(food_database, FOOD_DATABASE_FILE)
                            st.success(f"Deleted: {food.get('name', 'food')}")
                            st.experimental_rerun()
                    
                    st.markdown("---")
            else:
                st.info("No foods found matching your search.")
        else:
            st.info("No foods in database yet. Add your first food using the form above.")
    
    # Meal Templates Tab
    with meal_tabs[2]:
        st.subheader("Meal Templates")
        st.write("Save and reuse your favorite meals.")
        
        # Get templates
        templates = [m for m in meals if m.get("is_template", False)]
        
        if templates:
            # Group by type
            template_types = {}
            for template in templates:
                t_type = template.get("type", "Other")
                if t_type not in template_types:
                    template_types[t_type] = []
                template_types[t_type].append(template)
            
            # Display templates by type
            for t_type, type_templates in template_types.items():
                st.write(f"### {t_type} Templates")
                
                for template in type_templates:
                    with st.expander(f"{template.get('name', 'Unnamed Template')}"):
                        # Calculate totals
                        total_calories = sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) for item in template.get("food_items", []))
                        total_protein = sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) for item in template.get("food_items", []))
                        total_carbs = sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) for item in template.get("food_items", []))
                        total_fat = sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) for item in template.get("food_items", []))
                        
                        st.write(f"**Total Nutrition:** {total_calories} kcal, P: {total_protein:.1f}g, C: {total_carbs:.1f}g, F: {total_fat:.1f}g")
                        
                        # Food items
                        st.write("**Food Items:**")
                        for item in template.get("food_items", []):
                            quantity = item.get("quantity_multiplier", 1)
                            st.write(f"• {item.get('name', 'Unknown')} "
                                    f"({quantity}x {item.get('serving_size', '')}): "
                                    f"{item.get('calories', 0) * quantity:.0f} kcal, "
                                    f"P: {item.get('protein', 0) * quantity:.1f}g, "
                                    f"C: {item.get('carbs', 0) * quantity:.1f}g, "
                                    f"F: {item.get('fat', 0) * quantity:.1f}g")
                        
                        # Use template button
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Use Template", key=f"use_template_{template['id']}"):
                                # Create new meal from template
                                new_meal = template.copy()
                                new_meal["id"] = str(len(meals) + 1)
                                new_meal["date"] = selected_date_str
                                new_meal["time"] = datetime.datetime.now().strftime("%H:%M")
                                new_meal["is_template"] = False
                                new_meal["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                meals.append(new_meal)
                                save_data(meals, MEALS_FILE)
                                st.success(f"Added meal from template: {template.get('name', 'Unnamed')}")
                                st.experimental_rerun()
                        
                        with col2:
                            if st.button("Delete Template", key=f"delete_template_{template['id']}"):
                                meals.remove(template)
                                save_data(meals, MEALS_FILE)
                                st.success(f"Deleted template: {template.get('name', 'Unnamed')}")
                                st.experimental_rerun()
        else:
            st.info("No meal templates yet. Save a meal as a template in the Log Meals tab.")
    
    # Nutrition Analysis Tab
    with meal_tabs[3]:
        st.subheader("Nutrition Analysis")
        
        # Date range selection for analysis
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=today - datetime.timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=today)
        
        # Make sure end date is not before start date
        if start_date > end_date:
            st.error("Error: End date must be after start date.")
        else:
            # Convert to string format for comparison
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Get meals in the date range
            range_meals = [m for m in meals if not m.get("is_template", False) and 
                          start_date_str <= m.get("date", "") <= end_date_str]
            
            if range_meals:
                # Group by date
                meals_by_date = {}
                for meal in range_meals:
                    meal_date = meal.get("date", "")
                    if meal_date not in meals_by_date:
                        meals_by_date[meal_date] = []
                    meals_by_date[meal_date].append(meal)
                
                # Calculate daily totals
                daily_totals = {}
                for date, date_meals in meals_by_date.items():
                    calories = sum(sum(item.get("calories", 0) * item.get("quantity_multiplier", 1) 
                                    for item in meal.get("food_items", [])) 
                                for meal in date_meals)
                    protein = sum(sum(item.get("protein", 0) * item.get("quantity_multiplier", 1) 
                                   for item in meal.get("food_items", [])) 
                               for meal in date_meals)
                    carbs = sum(sum(item.get("carbs", 0) * item.get("quantity_multiplier", 1) 
                                 for item in meal.get("food_items", [])) 
                             for meal in date_meals)
                    fat = sum(sum(item.get("fat", 0) * item.get("quantity_multiplier", 1) 
                               for item in meal.get("food_items", [])) 
                           for meal in date_meals)
                    
                    daily_totals[date] = {
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat
                    }
                
                # Sort dates
                sorted_dates = sorted(daily_totals.keys())
                
                # Display table
                st.write("### Daily Nutrition Summary")
                
                # Create a data table
                date_list = []
                calories_list = []
                protein_list = []
                carbs_list = []
                fat_list = []
                
                for date in sorted_dates:
                    date_list.append(date)
                    calories_list.append(f"{daily_totals[date]['calories']:.0f}")
                    protein_list.append(f"{daily_totals[date]['protein']:.1f}")
                    carbs_list.append(f"{daily_totals[date]['carbs']:.1f}")
                    fat_list.append(f"{daily_totals[date]['fat']:.1f}")
                
                # Display the table
                st.table({
                    "Date": date_list,
                    "Calories": calories_list,
                    "Protein (g)": protein_list,
                    "Carbs (g)": carbs_list,
                    "Fat (g)": fat_list
                })
                
                # Calculate averages
                avg_calories = sum(daily_totals[date]["calories"] for date in sorted_dates) / len(sorted_dates)
                avg_protein = sum(daily_totals[date]["protein"] for date in sorted_dates) / len(sorted_dates)
                avg_carbs = sum(daily_totals[date]["carbs"] for date in sorted_dates) / len(sorted_dates)
                avg_fat = sum(daily_totals[date]["fat"] for date in sorted_dates) / len(sorted_dates)
                
                # Display averages
                st.write("### Averages for Selected Period")
                avg_col1, avg_col2, avg_col3, avg_col4 = st.columns(4)
                
                with avg_col1:
                    st.metric("Avg. Calories", f"{avg_calories:.0f}")
                
                with avg_col2:
                    st.metric("Avg. Protein", f"{avg_protein:.1f}g")
                
                with avg_col3:
                    st.metric("Avg. Carbs", f"{avg_carbs:.1f}g")
                
                with avg_col4:
                    st.metric("Avg. Fat", f"{avg_fat:.1f}g")
                
                # Nutrition insight
                st.write("### Nutrition Insights")
                
                # Calorie trend
                if len(sorted_dates) > 1:
                    first_cal = daily_totals[sorted_dates[0]]["calories"]
                    last_cal = daily_totals[sorted_dates[-1]]["calories"]
                    
                    if last_cal > first_cal * 1.15:  # 15% increase
                        st.warning("⚠️ Your calorie intake has increased significantly over this period.")
                    elif last_cal < first_cal * 0.85:  # 15% decrease
                        st.success("✅ Your calorie intake has decreased over this period.")
                
                # Protein adequacy
                protein_per_kg = avg_protein / 70  # assuming 70kg person, adjust as needed
                if protein_per_kg < 1.6:
                    st.warning(f"⚠️ Your average protein intake ({avg_protein:.1f}g) may be too low for muscle building. Aim for at least 1.6-2.2g per kg of bodyweight.")
                else:
                    st.success(f"✅ Your average protein intake ({avg_protein:.1f}g) is good for muscle building.")
                
                # Macro ratio analysis
                total_macro_calories = (avg_protein * 4) + (avg_carbs * 4) + (avg_fat * 9)
                if total_macro_calories > 0:
                    protein_perc = round((avg_protein * 4 / total_macro_calories) * 100)
                    carbs_perc = round((avg_carbs * 4 / total_macro_calories) * 100)
                    fat_perc = round((avg_fat * 9 / total_macro_calories) * 100)
                    
                    st.write(f"**Macro Ratio:** Protein: {protein_perc}% | Carbs: {carbs_perc}% | Fat: {fat_perc}%")
                    
                    if protein_perc < 20:
                        st.warning("⚠️ Your protein percentage is low. Consider increasing protein intake.")
                    if fat_perc > 40:
                        st.warning("⚠️ Your fat percentage is high. Consider moderating fat intake.")
            else:
                st.info("No meal data available for the selected date range.")

# Daily Habits Tab
elif selected_tab == "Daily Habits":
    st.title("📌 Daily Habits & Personal Growth")
    
    # Load habits and habit logs
    habits = load_data(HABITS_FILE)
    habit_logs = load_data(HABIT_LOGS_FILE)
    
    # Filter logs for selected date
    today_logs = [log for log in habit_logs if log.get("date") == selected_date_str]
    
    # Create a dictionary to easily access today's logs
    today_log_dict = {log.get("habit_id"): log for log in today_logs}
    
    st.markdown("""
    Track your daily habits to transform your life. Early morning routines, meditation, 
    water intake, and consistent sleep patterns are the foundation of personal growth.
    """)
    
    # Morning routine section
    st.header("🌅 Morning Routine")
    st.markdown("Start your day with intention")
    
    morning_habits = [h for h in habits if h.get("type") == "morning" and h.get("active", True)]
    
    # Morning routine tracking
    morning_cols = st.columns(len(morning_habits) if morning_habits else 1)
    
    if morning_habits:
        for i, habit in enumerate(morning_habits):
            with morning_cols[i]:
                habit_id = habit.get("id")
                habit_name = habit.get("name")
                habit_time = habit.get("time", "06:00")
                
                # Check if this habit is completed today
                completed = habit_id in today_log_dict
                
                st.subheader(habit_name)
                st.caption(f"Target time: {habit_time}")
                
                # Add description
                st.markdown(habit.get("description", ""))
                
                # Completion checkbox
                if st.checkbox(
                    "Completed", 
                    value=completed,
                    key=f"morning_{habit_id}"
                ):
                    if not completed:
                        # Add new log
                        new_log = {
                            "id": str(len(habit_logs) + 1),
                            "habit_id": habit_id,
                            "date": selected_date_str,
                            "completed": True,
                            "time": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        habit_logs.append(new_log)
                        save_data(habit_logs, HABIT_LOGS_FILE)
                        st.success(f"Marked {habit_name} as completed!")
                else:
                    if completed:
                        # Remove existing log
                        habit_logs = [log for log in habit_logs 
                                      if not (log.get("habit_id") == habit_id and log.get("date") == selected_date_str)]
                        save_data(habit_logs, HABIT_LOGS_FILE)
    else:
        st.info("No morning habits configured. Add them in the settings.")
    
    # Water intake tracking
    st.header("💧 Water Intake")
    
    # Find water tracking habit
    water_habit = next((h for h in habits if "water" in h.get("name", "").lower()), None)
    
    if water_habit:
        water_target = water_habit.get("target", 8)
        water_unit = water_habit.get("unit", "glasses")
        
        # Get current water count
        water_log = next((log for log in today_logs if log.get("habit_id") == water_habit.get("id")), None)
        current_water = water_log.get("count", 0) if water_log else 0
        
        st.markdown(f"**Target: {water_target} {water_unit}**")
        st.progress(min(1.0, current_water / water_target))
        st.write(f"Current: {current_water} of {water_target} {water_unit}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Water"):
                # Update water log
                if water_log:
                    # Update existing log
                    for log in habit_logs:
                        if log.get("id") == water_log.get("id"):
                            log["count"] = current_water + 1
                            log["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            break
                else:
                    # Create new log
                    new_log = {
                        "id": str(len(habit_logs) + 1),
                        "habit_id": water_habit.get("id"),
                        "date": selected_date_str,
                        "count": 1,
                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    habit_logs.append(new_log)
                
                save_data(habit_logs, HABIT_LOGS_FILE)
                st.experimental_rerun()
        
        with col2:
            if current_water > 0 and st.button("➖ Remove Water"):
                # Update water log
                for log in habit_logs:
                    if log.get("id") == water_log.get("id"):
                        log["count"] = max(0, current_water - 1)
                        log["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break
                
                save_data(habit_logs, HABIT_LOGS_FILE)
                st.experimental_rerun()
    
    # Evening routine section
    st.header("🌙 Evening Routine")
    st.markdown("Wind down properly for better recovery")
    
    evening_habits = [h for h in habits if h.get("type") == "evening" and h.get("active", True)]
    
    # Evening routine tracking
    evening_cols = st.columns(len(evening_habits) if evening_habits else 1)
    
    if evening_habits:
        for i, habit in enumerate(evening_habits):
            with evening_cols[i]:
                habit_id = habit.get("id")
                habit_name = habit.get("name")
                habit_time = habit.get("time", "22:00")
                
                # Check if this habit is completed today
                completed = habit_id in today_log_dict
                
                st.subheader(habit_name)
                st.caption(f"Target time: {habit_time}")
                
                # Add description
                st.markdown(habit.get("description", ""))
                
                # Completion checkbox
                if st.checkbox(
                    "Completed", 
                    value=completed,
                    key=f"evening_{habit_id}"
                ):
                    if not completed:
                        # Add new log
                        new_log = {
                            "id": str(len(habit_logs) + 1),
                            "habit_id": habit_id,
                            "date": selected_date_str,
                            "completed": True,
                            "time": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        habit_logs.append(new_log)
                        save_data(habit_logs, HABIT_LOGS_FILE)
                        st.success(f"Marked {habit_name} as completed!")
                else:
                    if completed:
                        # Remove existing log
                        habit_logs = [log for log in habit_logs 
                                      if not (log.get("habit_id") == habit_id and log.get("date") == selected_date_str)]
                        save_data(habit_logs, HABIT_LOGS_FILE)
    else:
        st.info("No evening habits configured. Add them in the settings.")
    
    # Add New Habit section
    st.markdown("---")
    st.header("➕ Add Custom Habit")
    
    with st.form("add_habit_form"):
        habit_name = st.text_input("Habit Name")
        habit_type = st.selectbox(
            "Habit Type",
            options=["morning", "evening", "recurring"]
        )
        
        if habit_type in ["morning", "evening"]:
            habit_time = st.time_input("Target Time", 
                                      datetime.time(6, 0) if habit_type == "morning" else datetime.time(22, 0))
            habit_description = st.text_area("Description")
            
            habit_data = {
                "name": habit_name,
                "type": habit_type,
                "time": habit_time.strftime("%H:%M"),
                "description": habit_description,
                "active": True
            }
        else:
            habit_frequency = st.text_input("Frequency (e.g., 'every 2 hours')")
            habit_target = st.number_input("Daily Target", min_value=1, value=1)
            habit_unit = st.text_input("Unit (e.g., 'times', 'glasses')")
            habit_description = st.text_area("Description")
            
            habit_data = {
                "name": habit_name,
                "type": habit_type,
                "frequency": habit_frequency,
                "target": habit_target,
                "unit": habit_unit,
                "description": habit_description,
                "active": True
            }
        
        submit_habit = st.form_submit_button("Add Habit")
        
        if submit_habit and habit_name:
            # Add ID to habit data
            habit_data["id"] = str(len(habits) + 1)
            habits.append(habit_data)
            save_data(habits, HABITS_FILE)
            st.success(f"Added new habit: {habit_name}")
            st.experimental_rerun()
    
    # Habit Statistics
    st.markdown("---")
    st.header("📊 Habit Streak Statistics")
    
    if habits:
        # Calculate streaks for each habit
        habit_streaks = {}
        for habit in habits:
            habit_id = habit.get("id")
            logs_for_habit = [log for log in habit_logs if log.get("habit_id") == habit_id]
            logs_for_habit.sort(key=lambda x: x.get("date", ""))
            
            # Calculate current streak
            current_streak = 0
            if logs_for_habit:
                dates = [datetime.datetime.strptime(log.get("date"), "%Y-%m-%d").date() for log in logs_for_habit]
                dates.sort(reverse=True)
                
                today = datetime.date.today()
                current_date = today
                for date in dates:
                    if (current_date - date).days <= 1:
                        current_streak += 1
                        current_date = date
                    else:
                        break
            
            habit_streaks[habit_id] = current_streak
        
        # Display streaks
        streak_col1, streak_col2 = st.columns(2)
        
        with streak_col1:
            st.subheader("Current Streaks")
            for habit in habits:
                habit_id = habit.get("id")
                streak = habit_streaks.get(habit_id, 0)
                st.write(f"**{habit.get('name')}**: {streak} {'days' if streak != 1 else 'day'}")
        
        with streak_col2:
            st.subheader("Completion Rate")
            # Calculate completion rate for last 7 days
            seven_days_ago = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            recent_logs = [log for log in habit_logs if log.get("date", "") >= seven_days_ago]
            
            for habit in habits:
                habit_id = habit.get("id")
                logs_for_habit = [log for log in recent_logs if log.get("habit_id") == habit_id]
                completion_rate = min(100, int((len(logs_for_habit) / 7) * 100))
                
                st.write(f"**{habit.get('name')}**: {completion_rate}%")
                st.progress(completion_rate / 100)
    else:
        st.info("No habits to track statistics for. Add some habits above.")

# Settings Tab
elif selected_tab == "Settings":
    st.title("⚙️ Settings")
    
    # Nutrition Goals Section
    st.subheader("Nutrition Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        daily_calories = st.number_input("Daily Calorie Goal", min_value=500, max_value=10000, value=settings["daily_calorie_goal"])
        protein_goal = st.number_input("Protein Goal (g)", min_value=0, max_value=500, value=settings["protein_goal"])
    
    with col2:
        carbs_goal = st.number_input("Carbs Goal (g)", min_value=0, max_value=1000, value=settings["carbs_goal"])
        fat_goal = st.number_input("Fat Goal (g)", min_value=0, max_value=500, value=settings["fat_goal"])
    
    water_goal = st.number_input("Daily Water Goal (glasses)", min_value=0, max_value=20, value=settings["water_goal"])
    
    st.markdown("---")
    
    # Workout Settings
    st.subheader("Workout Settings")
    weight_unit = st.selectbox("Weight Unit", options=["kg", "lbs"], index=0 if settings.get("weight_unit", "kg") == "kg" else 1)
    
    st.markdown("---")
    
    # Notification Settings
    st.subheader("Notification Settings")
    enable_notifications = st.checkbox("Enable Notifications", value=settings.get("enable_notifications", True))
    
    st.write("**Daily Schedule**")
    wakeup_time = st.time_input("Morning Wake-Up Time", 
                               value=datetime.time(
                                   hour=int(settings.get("wakeup_time", "06:00").split(":")[0]),
                                   minute=int(settings.get("wakeup_time", "06:00").split(":")[1])
                               ))
    
    reminder_time = st.time_input("Morning Reminder Time", 
                                 value=datetime.time(
                                     hour=int(settings.get("reminder_time", "07:00").split(":")[0]),
                                     minute=int(settings.get("reminder_time", "07:00").split(":")[1])
                                 ))
    
    bedtime = st.time_input("Target Bedtime", 
                           value=datetime.time(
                               hour=int(settings.get("bedtime", "22:00").split(":")[0]),
                               minute=int(settings.get("bedtime", "22:00").split(":")[1])
                           ))
    
    st.caption("Set your wake-up time for meditation and your target bedtime for better sleep quality.")
    
    st.markdown("---")
    
    # Data Management
    st.subheader("Data Management")
    
    if st.button("Reset All Data"):
        confirm = st.checkbox("Are you sure? This will delete ALL your data and cannot be undone.")
        if confirm:
            # Delete all data files
            try:
                if WORKOUTS_FILE.exists():
                    WORKOUTS_FILE.unlink()
                if MEALS_FILE.exists():
                    MEALS_FILE.unlink()
                if FOOD_DATABASE_FILE.exists():
                    FOOD_DATABASE_FILE.unlink()
                if WEEKLY_PLAN_FILE.exists():
                    WEEKLY_PLAN_FILE.unlink()
                if SETTINGS_FILE.exists():
                    SETTINGS_FILE.unlink()
                
                # Re-initialize with defaults
                init_data_files()
                
                st.success("All data has been reset. Reloading page...")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error resetting data: {e}")
    
    # Save settings button
    if st.button("Save Settings"):
        # Update settings
        settings["daily_calorie_goal"] = daily_calories
        settings["protein_goal"] = protein_goal
        settings["carbs_goal"] = carbs_goal
        settings["fat_goal"] = fat_goal
        settings["water_goal"] = water_goal
        settings["weight_unit"] = weight_unit
        settings["enable_notifications"] = enable_notifications
        settings["wakeup_time"] = wakeup_time.strftime("%H:%M")
        settings["reminder_time"] = reminder_time.strftime("%H:%M")
        settings["bedtime"] = bedtime.strftime("%H:%M")
        
        # Save to file
        save_settings(settings)
        st.success("Settings saved successfully!")
        st.experimental_rerun()
    
    # Skin Care Tips
    st.markdown("---")
    st.subheader("Skin Care Tips")
    
    # Display random skin care tips
    for _ in range(3):
        st.info(get_skincare_tip())
    
    # Display more comprehensive skin care routine
    with st.expander("View Comprehensive Skin Care Routine"):
        st.write("""
        ### Morning Routine:
        1. **Cleanser**: Start with a gentle cleanser to remove overnight oil build-up
        2. **Toner**: Apply alcohol-free toner to balance skin pH
        3. **Vitamin C Serum**: Apply for antioxidant protection and brightening
        4. **Moisturizer**: Use a lightweight moisturizer appropriate for your skin type
        5. **Sunscreen**: Apply SPF 30+ sunscreen (the most important step!)
        
        ### Evening Routine:
        1. **Oil Cleanser/Makeup Remover**: Remove makeup and sunscreen
        2. **Water-based Cleanser**: Double cleanse to remove remaining impurities
        3. **Exfoliate**: 1-2 times per week with BHA (salicylic acid) or AHA (glycolic acid)
        4. **Treatment**: Apply retinol, niacinamide, or other active ingredients
        5. **Moisturizer**: Use a richer night cream to lock in hydration
        
        ### Weekly:
        - Use a clay or hydrating mask 1-2 times per week
        - Perform a deeper exfoliation once a week
        
        ### General Tips:
        - Change pillowcases at least once a week
        - Don't touch your face with unwashed hands
        - Stay hydrated
        - Get enough sleep
        - Manage stress levels
        """)
    
    # Transformation tips
    st.markdown("---")
    st.subheader("1-Year Transformation Tips")
    
    st.write("""
    ### Keys to a Successful 1-Year Body Transformation:
    
    #### 1. Consistency Over Intensity
    - Showing up consistently (4-5 workouts/week) is more important than any single workout
    - Track adherence: aim for 85%+ consistency with your workout plan
    
    #### 2. Progressive Overload
    - Gradually increase weight, reps, or sets over time
    - Record your lifts and aim to improve each week, even slightly
    
    #### 3. Nutrition Fundamentals
    - Protein: 1.6-2.2g per kg of bodyweight daily
    - Track calories consistently at first to understand your needs
    - 80/20 rule: 80% whole foods, 20% flexible
    
    #### 4. Recovery is Growth
    - Prioritize 7-9 hours of quality sleep
    - Include deliberate rest days
    - Manage stress through meditation, walks in nature, or hobbies
    
    #### 5. Monthly Check-ins
    - Take progress photos monthly (same lighting, time of day, poses)
    - Adjust your program every 8-12 weeks
    - Set performance goals, not just aesthetic ones
    """)
    
    # Motivational quote
    st.markdown("---")
    st.info(f"**Quote of the Day:** {get_motivational_message()}")