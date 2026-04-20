"""
All LLM prompts in one place.
"""

DIET_PROMPT = """
You are a nutritionist. Create a 30-day diet plan split into 4 weeks.

User:
- Age: {age} | Weight: {weight}kg | Height: {height}cm
- Goal: {goal} | Daily calorie target: {calories} kcal

Rules:
- Vary the meals across weeks (week2, week3, week4 must be different from week1)
- Use realistic Indian or international meals
- Reply ONLY with valid JSON — no markdown fences, no extra text

JSON format:
{{
  "overview": "2-sentence strategy",
  "macros": {{"protein_g": 0, "carbs_g": 0, "fat_g": 0}},
  "week1": {{
    "Monday":    {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Tuesday":   {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Wednesday": {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Thursday":  {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Friday":    {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Saturday":  {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}},
    "Sunday":    {{"breakfast": "...", "lunch": "...", "dinner": "...", "snack": "..."}}
  }},
  "week2": {{ same structure, different meals }},
  "week3": {{ same structure, different meals }},
  "week4": {{ same structure, different meals }},
  "tips": ["tip1", "tip2", "tip3"],
  "avoid": ["food1", "food2", "food3"]
}}
"""

WORKOUT_PROMPT = """
You are a fitness coach. Create a full 30-day workout plan split into 4 weeks.

User:
- Age: {age} | Weight: {weight}kg | Goal: {goal}
- Workout days per week: {days}

Rules:
- Each week must have exactly {days} workout days + rest days labelled clearly
- Apply progressive overload: week2 harder than week1, week3 harder than week2, week4 is a deload
- Reply ONLY with valid JSON — no markdown fences, no extra text

JSON format:
{{
  "overview": "2-sentence strategy",
  "week1": {{
    "Day1": {{"focus": "Upper Body", "exercises": [{{"name": "Push-ups", "sets": 3, "reps": "12"}}], "duration_min": 40}},
    "Day2": {{"focus": "Lower Body", "exercises": [{{"name": "Squats", "sets": 3, "reps": "15"}}], "duration_min": 40}},
    "rest_days": ["Wednesday", "Friday", "Sunday"]
  }},
  "week2": {{ same structure, higher intensity }},
  "week3": {{ same structure, higher intensity }},
  "week4": {{ same structure, deload week }},
  "equipment": ["item1", "item2"],
  "tips": ["tip1", "tip2", "tip3"]
}}
"""

SUMMARY_PROMPT = """
Write a warm, motivating 3-paragraph summary for someone starting a 30-day fitness journey.

Profile: {profile}
Diet: {diet_overview}
Workout: {workout_overview}

No bullet points. Keep it personal and encouraging.
"""
