"""
Food tracker UI components.
"""

import streamlit as st
from datetime import datetime
from src.modules.food.data import (
    get_today_food_entries,
    get_daily_summary,
    add_food_entry,
    delete_food_entry
)
from src.modules.food.nutrition_api import NutritionAPI

VITAMIN_GOALS = {
    'total_vitamin_a': ('🅰️ Vitamin A', 900, 'µg'),
    'total_vitamin_c': ('🅲 Vitamin C', 200, 'mg'),
    'total_vitamin_d': ('🅳 Vitamin D', 75, 'µg'),
    'total_calcium':   ('🧂 Calcium',   1100, 'mg'),
    'total_iron':      ('🔩 Iron',       9, 'mg'),
    'total_magnesium': ('🧲 Magnesium',  400, 'mg'),
    'total_zinc':      ('🔋 Zinc',       13, 'mg'),
    'total_potassium': ('🍌 Potassium',  4000, 'mg'),
}

def render_vitamin_progress(summary, key_prefix='total_'):
    """Shared helper: render vitamin/mineral progress bars from a summary dict."""
    has_any = False
    for key, (label, goal, unit) in VITAMIN_GOALS.items():
        # support both 'total_vitamin_a' and 'vitamin_a' prefixes
        value = summary.get(key, 0) or summary.get(key.replace('total_', ''), 0) or 0
        if value > 0:
            has_any = True
            pct = min(value / goal, 1.0)
            decimals = 1 if unit == 'mg' and goal < 20 else 0
            st.progress(pct, text=f"{label}: {value:.{decimals}f} / {goal} {unit}  ({pct*100:.0f}%)")
    if not has_any:
        st.caption("No vitamins or minerals logged yet.")
    """Main food tracker interface."""
    st.title("🍽️ Food Tracker")
    st.caption("Log your meals and track your nutrition")
    
    render_daily_summary()
    st.divider()
    
    tab1, tab2 = st.tabs(["🔍 Search with API", "✏️ Manual Entry"])
    
    with tab1:
        render_api_form()
    
    with tab2:
        render_manual_form()
    
    st.divider()
    render_meal_list()

def render_daily_summary():
    """Show today's nutrition summary."""
    summary = get_daily_summary()

    if summary['meal_count'] == 0:
        st.info("No meals logged today yet. Start tracking your nutrition!")
        return

    # Macros as progress bars
    col1, col2 = st.columns(2)
    with col1:
        st.progress(min(summary['total_calories'] / 3000, 1.0),
            text=f"🔥 Calories: {summary['total_calories']:.0f} / 3000 kcal ({min(summary['total_calories']/3000*100,100):.0f}%)")
        st.progress(min(summary['total_protein'] / 155, 1.0),
            text=f"💪 Protein: {summary['total_protein']:.1f} / 155 g ({min(summary['total_protein']/155*100,100):.0f}%)")
    with col2:
        st.progress(min(summary['total_carbs'] / 350, 1.0),
            text=f"🍞 Carbs: {summary['total_carbs']:.1f} / 350 g ({min(summary['total_carbs']/350*100,100):.0f}%)")
        st.progress(min(summary['total_fat'] / 80, 1.0),
            text=f"🥑 Fat: {summary['total_fat']:.1f} / 80 g ({min(summary['total_fat']/80*100,100):.0f}%)")

    # Vitamins & Minerals
    st.subheader("🧬 Vitamins & Minerals")
    render_vitamin_progress(summary)

def render_api_form():
    """Render the API-based food entry form."""
    st.subheader("🔍 Search for Food")
    st.caption("Enter a food description and let the API find the nutrition data")
    
    if 'api_preview' not in st.session_state:
        st.session_state.api_preview = None
    
    food_query = st.text_input(
        "What did you eat?",
        placeholder='e.g., "100g chicken breast", "1 cup oatmeal with banana"',
        help="Be specific with quantities for better results"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_btn = st.button("🔍 Search", type="primary", width='stretch')
    
    with col2:
        if st.button("🔄 Clear Preview", width='stretch'):
            st.session_state.api_preview = None
            st.rerun()
    
    if search_btn and food_query:
        with st.spinner("🔎 Analyzing your meal..."):
            api = NutritionAPI()
            result = api.analyze_food(food_query)
            if result and result.get('success'):
                st.session_state.api_preview = {
                    'query': food_query,
                    'data': result
                }
                st.success("✅ Found nutrition data! Review below.")
            else:
                st.warning("🤔 Couldn't analyze that. Please try a different description or use manual entry.")
                st.session_state.api_preview = None
    
    if st.session_state.api_preview:
        render_api_preview(st.session_state.api_preview)

def render_api_preview(preview_data):
    """Render the API preview with save option."""
    data = preview_data['data']
    query = preview_data.get('query', '')
    
    st.subheader("📊 Nutrition Preview")
    
    # Macros (always show)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔥 Calories", f"{data.get('calories', 0):.0f} kcal")
    with col2:
        st.metric("💪 Protein", f"{data.get('protein', 0):.1f} g")
    with col3:
        st.metric("🍞 Carbs", f"{data.get('carbs', 0):.1f} g")
    with col4:
        st.metric("🥑 Fat", f"{data.get('fat', 0):.1f} g")
    
    # Vitamins & Minerals (only show if > 0)
    st.subheader("🧬 Vitamins & Minerals")
    
    # Define all nutrients with their icons, keys, and units
    nutrients = [
        ('vitamin_a', '🅰️ Vitamin A', 'µg'),
        ('vitamin_c', '🅲 Vitamin C', 'mg'),
        ('vitamin_d', '🅳 Vitamin D', 'µg'),
        ('calcium', '🧂 Calcium', 'mg'),
        ('iron', '🔩 Iron', 'mg'),
        ('magnesium', '🧲 Magnesium', 'mg'),
        ('zinc', '🔋 Zinc', 'mg'),
        ('potassium', '🍌 Potassium', 'mg'),
    ]
    
    # Split into two columns
    col1, col2 = st.columns(2)
    
    has_values = False
    for i, (key, label, unit) in enumerate(nutrients):
        value = data.get(key, 0)
        
        # Only show if value > 0
        if value > 0:
            has_values = True
            with col1 if i < 4 else col2:
                if unit == 'µg':
                    st.metric(label, f"{value:.0f} {unit}")
                elif unit == 'mg' and key in ['iron', 'zinc']:
                    st.metric(label, f"{value:.1f} {unit}")
                else:
                    st.metric(label, f"{value:.0f} {unit}")
    
    if not has_values:
        st.info("No vitamin or mineral data available for this food.")
    
    # Raw data expander
    with st.expander("📋 View All Nutrition Details"):
        for key, value in data.items():
            if key not in ['calories', 'protein', 'carbs', 'fat', 'vitamin_a', 'vitamin_c', 'vitamin_d', 'calcium', 'iron', 'magnesium', 'zinc', 'potassium']:
                st.write(f"**{key}:** {value}")
    
    # Save form
    st.subheader("💾 Save This Meal")
    
    col1, col2 = st.columns(2)
    with col1:
        meal_date = st.date_input("Date", datetime.today().date(), key="api_date")
    with col2:
        meal_type = st.selectbox(
            "Meal Type",
            ["Breakfast", "Lunch", "Dinner", "Snack", "Anytime"],
            key="api_meal_type"
        )
    
    food_name = st.text_input(
        "Food Name (optional)",
        value=query[:50] if query else "",
        placeholder="e.g., Oatmeal Breakfast"
    )
    
    if st.button("💾 Save Meal from API", type="primary"):
        if not food_name:
            food_name = query[:50] if query else "Unknown Meal"
        
        add_food_entry(
            date=meal_date.strftime('%Y-%m-%d'),
            meal_type=meal_type.lower(),
            food_name=food_name,
            calories=data.get('calories', 0),
            protein=data.get('protein', 0),
            carbs=data.get('carbs', 0),
            fat=data.get('fat', 0),
            vitamin_a=data.get('vitamin_a', 0),
            vitamin_c=data.get('vitamin_c', 0),
            vitamin_d=data.get('vitamin_d', 0),
            calcium=data.get('calcium', 0),
            iron=data.get('iron', 0),
            magnesium=data.get('magnesium', 0),
            zinc=data.get('zinc', 0),
            potassium=data.get('potassium', 0)
        )
        st.success(f"✅ Saved: {food_name} ({data.get('calories', 0):.0f} kcal)")
        st.session_state.api_preview = None
        st.rerun()

def render_manual_form():
    """Render the manual food entry form."""
    st.subheader("✏️ Manual Entry")
    st.caption("Enter nutrition data manually")
    
    with st.form(key="manual_food_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.today().date())
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack", "Anytime"]
            )
            food_name = st.text_input("Food Name", placeholder="e.g., Homemade chicken soup")
        
        with col2:
            st.subheader("📊 Macros")
            col_a, col_b = st.columns(2)
            with col_a:
                calories = st.number_input("Calories", min_value=0, step=10)
                protein = st.number_input("Protein (g)", min_value=0.0, step=0.1)
                carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1)
            with col_b:
                fat = st.number_input("Fat (g)", min_value=0.0, step=0.1)
        
        st.subheader("🧬 Vitamins & Minerals")
        col1, col2, col3 = st.columns(3)
        with col1:
            vitamin_a = st.number_input("Vitamin A (µg)", min_value=0.0, step=1.0)
            vitamin_c = st.number_input("Vitamin C (mg)", min_value=0.0, step=1.0)
            vitamin_d = st.number_input("Vitamin D (µg)", min_value=0.0, step=1.0)
        with col2:
            calcium = st.number_input("Calcium (mg)", min_value=0.0, step=1.0)
            iron = st.number_input("Iron (mg)", min_value=0.0, step=0.1)
            magnesium = st.number_input("Magnesium (mg)", min_value=0.0, step=1.0)
        with col3:
            zinc = st.number_input("Zinc (mg)", min_value=0.0, step=0.1)
            potassium = st.number_input("Potassium (mg)", min_value=0.0, step=1.0)
        
        submitted = st.form_submit_button("💾 Save Manual Entry", type="primary")
        
        if submitted:
            if not food_name:
                st.error("Please enter a food name.")
            elif calories <= 0:
                st.error("Please enter calories (must be > 0).")
            else:
                add_food_entry(
                    date=date.strftime('%Y-%m-%d'),
                    meal_type=meal_type.lower(),
                    food_name=food_name,
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fat=fat,
                    vitamin_a=vitamin_a,
                    vitamin_c=vitamin_c,
                    vitamin_d=vitamin_d,
                    calcium=calcium,
                    iron=iron,
                    magnesium=magnesium,
                    zinc=zinc,
                    potassium=potassium
                )
                st.success(f"✅ Saved: {food_name} ({calories} kcal)")
                st.rerun()

def render_meal_list():
    """Show today's meals."""
    st.subheader("📋 Today's Meals")
    
    entries = get_today_food_entries()
    if entries.empty:
        st.info("No meals logged today yet.")
        return
    
    for _, row in entries.iterrows():
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.write(f"**{row['meal_type'].title()}** – {row['food_name']}")
                st.caption(f"🔥 {row['calories']} kcal | 💪 {row['protein']:.1f}g | 🍞 {row['carbs']:.1f}g | 🥑 {row['fat']:.1f}g")
                vitamin_text = ""
                if row.get('vitamin_a', 0) > 0:
                    vitamin_text += f"🅰️{row['vitamin_a']:.0f}µg "
                if row.get('vitamin_c', 0) > 0:
                    vitamin_text += f"🅲{row['vitamin_c']:.0f}mg "
                if row.get('vitamin_d', 0) > 0:
                    vitamin_text += f"🅳{row['vitamin_d']:.0f}µg "
                if row.get('calcium', 0) > 0:
                    vitamin_text += f"🧂{row['calcium']:.0f}mg "
                if row.get('iron', 0) > 0:
                    vitamin_text += f"🔩{row['iron']:.1f}mg "
                if row.get('magnesium', 0) > 0:
                    vitamin_text += f"🧲{row['magnesium']:.0f}mg "
                if row.get('zinc', 0) > 0:
                    vitamin_text += f"🔋{row['zinc']:.1f}mg "
                if row.get('potassium', 0) > 0:
                    vitamin_text += f"🍌{row['potassium']:.0f}mg "
                if vitamin_text:
                    st.caption(vitamin_text)

            with col2:
                if st.button("🗑️", key=f"delete_food_{row['id']}", type="secondary"):
                    if delete_food_entry(row['id']):
                        st.success(f"Deleted: {row['food_name']}")
                        st.rerun()
                    else:
                        st.error("Failed to delete meal")

        st.divider()