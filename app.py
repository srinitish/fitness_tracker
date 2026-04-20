"""
Streamlit UI — 30-Day AI Fitness Planner
Run: streamlit run app.py
"""
import streamlit as st
from graph import run

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Fitness Planner", page_icon="🏋️", layout="wide")

st.markdown("""
<style>
  /* Week tab buttons */
  div[data-testid="stHorizontalBlock"] button {
    border-radius: 8px !important;
  }
  /* Expander header */
  details summary { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🏋️ 30-Day AI Fitness Planner")
st.caption("Powered by LangGraph + Groq · API key stored securely in config.py")
st.divider()

# ── Sidebar inputs (no API key field) ────────────────────────────────────────
with st.sidebar:
    st.header("📋 Your Details")
    age    = st.number_input("Age (years)",       min_value=15, max_value=80,  value=25)
    weight = st.number_input("Weight (kg)",       min_value=30, max_value=200, value=70,  step=1)
    height = st.number_input("Height (cm)",       min_value=100, max_value=220, value=170, step=1)
    days   = st.selectbox("Workout days / week",  [3, 4, 5, 6], index=1)
    goal   = st.selectbox("Your Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintenance"])
    st.divider()
    generate = st.button("⚡ Generate My 30-Day Plan", use_container_width=True, type="primary")

# ── Placeholder before generate ───────────────────────────────────────────────
if not generate:
    st.info("👈 Fill in your details in the sidebar, then click **Generate My 30-Day Plan**.")
    st.stop()

# ── Run pipeline ──────────────────────────────────────────────────────────────
with st.spinner("🤖 LangGraph is building your plan... (~20 seconds)"):
    try:
        result = run(age, weight, height, days, goal)
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

diet    = result["diet"]
workout = result["workout"]

# ── Metrics strip ─────────────────────────────────────────────────────────────
st.subheader("📊 Your Stats")
m1, m2, m3, m4 = st.columns(4)
m1.metric("BMI",            result["bmi"])
m2.metric("Daily Calories", f"{result['calories']} kcal")
m3.metric("Goal",           goal)
m4.metric("Workout Days",   f"{days}x / week")
st.divider()

# ── Summary ───────────────────────────────────────────────────────────────────
st.subheader("📝 Your Personal Summary")
st.info(result["summary"])
st.divider()

# ── Helper: render one week of diet ──────────────────────────────────────────
def show_diet_week(week_data: dict):
    if not isinstance(week_data, dict):
        st.warning("No data for this week.")
        return
    for day, meals in week_data.items():
        if not isinstance(meals, dict):
            continue
        with st.expander(f"📅 {day}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**🌅 Breakfast**\n\n{meals.get('breakfast','—')}")
            c2.markdown(f"**☀️ Lunch**\n\n{meals.get('lunch','—')}")
            c3.markdown(f"**🌙 Dinner**\n\n{meals.get('dinner','—')}")
            c4.markdown(f"**🍎 Snack**\n\n{meals.get('snack','—')}")

# ── Helper: render one week of workout ───────────────────────────────────────
def show_workout_week(week_data: dict):
    if not isinstance(week_data, dict):
        st.warning("No data for this week.")
        return
    rest = week_data.get("rest_days", [])
    if rest:
        st.success(f"😴 Rest days: {', '.join(rest)}")
    for key, info in week_data.items():
        if key == "rest_days" or not isinstance(info, dict):
            continue
        label = f"💪 {key} — {info.get('focus','Training')}  ·  ⏱ {info.get('duration_min','?')} min"
        with st.expander(label):
            exercises = info.get("exercises", [])
            if exercises:
                st.table({
                    "Exercise": [e.get("name", "")     for e in exercises],
                    "Sets":     [str(e.get("sets", "")) for e in exercises],
                    "Reps":     [str(e.get("reps", "")) for e in exercises],
                })
            else:
                st.write("No exercises listed.")

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_diet, tab_work, tab_tips = st.tabs(["🥗 Diet Plan", "🏋️ Workout Plan", "💡 Tips & Nutrition"])

# ─── DIET TAB ─────────────────────────────────────────────────────────────────
with tab_diet:
    if diet.get("parse_error"):
        st.error("Could not parse diet JSON. Raw response below:")
        st.code(diet["parse_error"])
    else:
        st.info(f"**Strategy:** {diet.get('overview', '')}")

        # Fixed 4 week tabs — no interactive selector
        w1, w2, w3, w4 = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
        with w1: show_diet_week(diet.get("week1", {}))
        with w2: show_diet_week(diet.get("week2", {}))
        with w3: show_diet_week(diet.get("week3", {}))
        with w4: show_diet_week(diet.get("week4", {}))

# ─── WORKOUT TAB ──────────────────────────────────────────────────────────────
with tab_work:
    if workout.get("parse_error"):
        st.error("Could not parse workout JSON. Raw response below:")
        st.code(workout["parse_error"])
    else:
        st.info(f"**Strategy:** {workout.get('overview', '')}")

        # Fixed 4 week tabs — no interactive selector
        w1, w2, w3, w4 = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
        with w1: show_workout_week(workout.get("week1", {}))
        with w2: show_workout_week(workout.get("week2", {}))
        with w3: show_workout_week(workout.get("week3", {}))
        with w4: show_workout_week(workout.get("week4", {}))

# ─── TIPS TAB ─────────────────────────────────────────────────────────────────
with tab_tips:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Daily Macros")
        macros = diet.get("macros", {})
        if macros:
            st.metric("🥩 Protein", f"{macros.get('protein_g','?')} g")
            st.metric("🍚 Carbs",   f"{macros.get('carbs_g','?')} g")
            st.metric("🥑 Fat",     f"{macros.get('fat_g','?')} g")

        st.subheader("🚫 Foods to Avoid")
        for item in diet.get("avoid", []):
            st.write(f"• {item}")

    with col2:
        st.subheader("🥗 Diet Tips")
        for tip in diet.get("tips", []):
            st.write(f"✅ {tip}")

        st.subheader("🏋️ Workout Tips")
        for tip in workout.get("tips", []):
            st.write(f"✅ {tip}")

        st.subheader("🎽 Equipment Needed")
        for item in workout.get("equipment", []):
            st.write(f"• {item}")
