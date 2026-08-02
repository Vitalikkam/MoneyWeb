"""
Exercise tracker UI – log workouts, view history, see stats.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from .data import log_exercise, get_exercises, delete_exercise, get_stats, get_streak

WORKOUT_TYPES = [
    "🏋️ Gym", "🏃 Run", "🚴 Cycling", "🧘 Yoga", "🥊 Boxing",
    "🏊 Swimming", "⚽ Football", "🏀 Basketball", "🚶 Walk", "💪 Home workout", "Other"
]

ENERGY_LABELS = {
    1: "😴 Exhausted",
    2: "😐 Low",
    3: "🙂 Normal",
    4: "😊 Good",
    5: "🔥 Amazing"
}


def render_exercise_tracker():
    """Main exercise tracker interface."""
    st.title("🏋️ Exercise Tracker")
    st.caption("Log your workouts and track consistency")

    tab1, tab2, tab3 = st.tabs([
        "➕ Log Workout",
        "📋 History",
        "📊 Stats"
    ])

    with tab1:
        render_log_tab()
    with tab2:
        render_history_tab()
    with tab3:
        render_stats_tab()


def render_log_tab():
    """Quick workout logging form."""
    streak = get_streak()
    if streak > 0:
        st.markdown(
            f'<div style="display:inline-block;background:#4ade8022;border:1px solid #4ade8055;'
            f'color:#4ade80;padding:6px 16px;border-radius:20px;font-weight:700;font-size:14px;margin-bottom:16px;">'
            f'🔥 {streak} day streak</div>',
            unsafe_allow_html=True
        )

    st.subheader("How was your workout?")

    with st.form("log_exercise_form", clear_on_submit=True):
        date = st.date_input("Date", value=datetime.today())

        col1, col2 = st.columns(2)
        with col1:
            workout_type = st.selectbox("Type", WORKOUT_TYPES)
        with col2:
            custom_type = st.text_input("Or type your own", placeholder="e.g. Pilates")

        energy = st.select_slider(
            "How did you feel?",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: ENERGY_LABELS[x]
        )

        notes = st.text_area("Notes (optional)", placeholder="What did you do? Any PRs? How was it?", max_chars=500)

        submitted = st.form_submit_button("✅ Log Workout", type="primary", use_container_width=True)

    if submitted:
        final_type = custom_type.strip() if custom_type.strip() else workout_type
        if log_exercise(
            date=date.strftime('%Y-%m-%d'),
            workout_type=final_type,
            notes=notes.strip() if notes else None,
            energy_level=energy
        ):
            st.success(f"Workout logged! {ENERGY_LABELS[energy]}")
            st.balloons()
        else:
            st.error("Failed to save. Try again.")

    _render_today_summary()


def _render_today_summary():
    """Show what was logged today, if anything."""
    today = datetime.today().strftime('%Y-%m-%d')
    df = get_exercises(days=1)
    if df.empty:
        return
    today_df = df[pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d') == today]
    if today_df.empty:
        return

    st.divider()
    st.caption("Today's logged workout(s)")
    for _, row in today_df.iterrows():
        _render_workout_row(row, show_date=False, key_prefix="today")


def render_history_tab():
    """Paginated workout history."""
    st.subheader("📋 Workout History")

    df = get_exercises()
    if df.empty:
        st.info("No workouts logged yet. Go to 'Log Workout' to get started!")
        return

    col1, col2 = st.columns(2)
    with col1:
        type_options = ["All"] + sorted(df['workout_type'].dropna().unique().tolist())
        type_filter = st.selectbox("Filter by type", type_options)
    with col2:
        period = st.selectbox("Period", ["All time", "This week", "This month", "Last 30 days"])

    filtered = df.copy()
    filtered['date_parsed'] = pd.to_datetime(filtered['date']).dt.date
    today = datetime.today().date()

    if period == "This week":
        week_start = today - pd.Timedelta(days=today.weekday())
        filtered = filtered[filtered['date_parsed'] >= week_start]
    elif period == "This month":
        filtered = filtered[filtered['date_parsed'] >= today.replace(day=1)]
    elif period == "Last 30 days":
        filtered = filtered[filtered['date_parsed'] >= today - pd.Timedelta(days=30)]

    if type_filter != "All":
        filtered = filtered[filtered['workout_type'] == type_filter]

    filtered = filtered.sort_values('date', ascending=False)

    if filtered.empty:
        st.info("No workouts match your filters.")
        return

    st.caption(f"{len(filtered)} workout(s)")
    st.divider()

    PAGE_SIZE = 10
    total_pages = max(1, -(-len(filtered) // PAGE_SIZE))
    page = st.session_state.get('exercise_page', 1)

    start = (page - 1) * PAGE_SIZE
    page_df = filtered.iloc[start:start + PAGE_SIZE]

    for _, row in page_df.iterrows():
        _render_workout_row(row, show_date=True, key_prefix="history")

    if total_pages > 1:
        col_prev, col_mid, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("← Prev", disabled=(page <= 1), use_container_width=True, key="ex_prev"):
                st.session_state.exercise_page = page - 1
                st.rerun()
        with col_mid:
            st.caption(f"Page {page} / {total_pages}")
        with col_next:
            if st.button("Next →", disabled=(page >= total_pages), use_container_width=True, key="ex_next"):
                st.session_state.exercise_page = page + 1
                st.rerun()


def _render_workout_row(row, show_date=True, key_prefix="ex"):
    """Render a single workout entry as a card row."""
    energy = int(row.get('energy_level', 3))
    energy_label = ENERGY_LABELS.get(energy, "")
    date_str = pd.to_datetime(row['date']).strftime('%a, %b %d') if show_date else ""
    workout_type = row.get('workout_type', 'Workout')
    notes = row.get('notes', '')

    col_main, col_action = st.columns([10, 1])
    with col_main:
        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #2a3a4b;border-radius:12px;padding:14px 18px;margin:4px 0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            f'<span style="font-size:17px;font-weight:600;color:#f8fafc;">{workout_type}</span>'
            f'<span style="display:flex;gap:10px;align-items:center;">'
            f'<span style="color:#94a3b8;font-size:13px;">{energy_label}</span>'
            f'{"<span style=color:#64748b;font-size:12px;>" + date_str + "</span>" if date_str else ""}'
            f'</span>'
            f'</div>'
            f'{"<div style=color:#94a3b8;font-size:13px;margin-top:6px;>" + notes + "</div>" if notes else ""}'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_action:
        # key_prefix ensures no collision between today summary and history list
        if st.button("🗑️", key=f"{key_prefix}_del_{row['id']}", help="Delete"):
            if delete_exercise(row['id']):
                st.rerun()


def render_stats_tab():
    """Exercise statistics."""
    st.subheader("📊 Your Stats")

    stats = get_stats()

    if stats['total_workouts'] == 0:
        st.info("Log some workouts to see your stats here!")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💪 Total Workouts", stats['total_workouts'])
    col2.metric("📅 This Week", stats['this_week'])
    col3.metric("🗓️ This Month", stats['this_month'])
    col4.metric("🔥 Streak", f"{stats['streak']} days")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        if stats['by_type']:
            st.subheader("By type")
            type_df = pd.DataFrame({
                'Type': list(stats['by_type'].keys()),
                'Workouts': list(stats['by_type'].values())
            }).sort_values('Workouts', ascending=False)
            st.bar_chart(type_df.set_index('Type'))

    with col_right:
        df = get_exercises(days=56)
        if not df.empty:
            st.subheader("Workouts per week")
            df['week'] = pd.to_datetime(df['date']).dt.to_period('W').astype(str)
            weekly = df.groupby('week').size().reset_index(name='Workouts')
            weekly = weekly.sort_values('week')
            st.bar_chart(weekly.set_index('week'))
