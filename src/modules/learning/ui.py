"""
Learning module UI — quest board, heatmap dashboard, weekly goal.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from .data import (
    add_subject,
    get_subjects,
    get_subject,
    update_subject_status,
    update_subject_progress,
    delete_subject,
    add_session,
    get_sessions,
    get_total_hours,
    get_study_streak,
    delete_session,
    add_milestone,
    get_milestones,
    delete_milestone,
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
STATUS_COLORS = {
    "Not Started": "#64748b",
    "In Progress":  "#60a5fa",
    "Completed":    "#4ade80",
    "On Hold":      "#fbbf24",
}
STATUS_ICONS = {
    "Not Started": "🔘",
    "In Progress":  "⚡",
    "Completed":    "✅",
    "On Hold":      "⏸️",
}
PRIORITY_COLORS = {
    "High":   "#f87171",
    "Medium": "#fbbf24",
    "Low":    "#94a3b8",
}
WEEKLY_GOAL_KEY = "learning_weekly_goal"
DEFAULT_WEEKLY_GOAL = 5


# ─────────────────────────────────────────────
# MAIN ENTRY
# ─────────────────────────────────────────────
def render_learning_tracker():
    st.title("🎓 Learning Tracker")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Dashboard",
        "⚔️ Quest Board",
        "⏱️ Log Session",
        "🏆 Milestones",
    ])

    with tab1:
        render_dashboard()
    with tab2:
        render_quest_board()
    with tab3:
        render_log_session()
    with tab4:
        render_milestones()


# ─────────────────────────────────────────────
# DASHBOARD — heatmap + streak + weekly goal
# ─────────────────────────────────────────────
def render_dashboard():
    subjects  = get_subjects()
    sessions  = get_sessions(days=365)
    streak    = get_study_streak()
    today     = datetime.today().date()

    # ── Top metrics ──
    active    = len(subjects[subjects['status'] == 'In Progress'])   if not subjects.empty else 0
    completed = len(subjects[subjects['status'] == 'Completed'])     if not subjects.empty else 0
    total_h   = round(sessions['duration'].sum() / 60, 1)            if not sessions.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔥 Streak",     f"{streak} days")
    c2.metric("⚡ Active",     active)
    c3.metric("✅ Completed",  completed)
    c4.metric("⏱️ Total Hours", f"{total_h}h")

    st.divider()

    # ── Weekly goal ──
    render_weekly_goal(sessions, today)

    st.divider()

    # ── Heatmap ──
    render_heatmap(sessions, today)

    st.divider()

    # ── Recent sessions ──
    st.subheader("📋 Recent Sessions")
    recent = get_sessions(days=14)
    if recent.empty:
        st.info("No sessions yet — log your first one in the ⏱️ tab!")
        return

    for _, row in recent.head(6).iterrows():
        subj = get_subject(row['subject_id'])
        name = subj['name'] if subj is not None else "Unknown"
        dur  = row.get('duration', 0) or 0
        rating = row.get('rating') or 0
        stars  = "⭐" * int(rating) if rating else ""
        date_fmt = pd.to_datetime(row['date']).strftime('%b %d')
        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #2a3a4b;border-radius:10px;'
            f'padding:10px 16px;margin:4px 0;display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<span style="color:#f8fafc;font-weight:600;">{name}</span>'
            f'{"<span style=color:#94a3b8;font-size:13px;margin-left:10px;>" + row["content"] + "</span>" if row.get("content") else ""}'
            f'</div>'
            f'<div style="display:flex;gap:12px;align-items:center;">'
            f'<span style="color:#64748b;font-size:12px;">{date_fmt}</span>'
            f'<span style="color:#94a3b8;font-size:13px;">⏱️ {int(dur)} min</span>'
            f'{"<span>" + stars + "</span>" if stars else ""}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_weekly_goal(sessions, today):
    """Weekly goal progress bar."""
    st.subheader("🎯 Weekly Goal")

    # Goal setting
    col_goal, col_label = st.columns([1, 3])
    with col_goal:
        goal = st.number_input(
            "Sessions / week",
            min_value=1, max_value=30,
            value=st.session_state.get(WEEKLY_GOAL_KEY, DEFAULT_WEEKLY_GOAL),
            step=1, key="weekly_goal_input", label_visibility="collapsed"
        )
        st.session_state[WEEKLY_GOAL_KEY] = goal

    # Count sessions this week
    week_start = today - timedelta(days=today.weekday())
    if not sessions.empty:
        sessions_dates = pd.to_datetime(sessions['date']).dt.date
        this_week = int((sessions_dates >= week_start).sum())
    else:
        this_week = 0

    pct = min(this_week / goal, 1.0)
    remaining = max(goal - this_week, 0)

    with col_label:
        if this_week >= goal:
            st.markdown(
                f'<div style="background:#4ade8022;border:1px solid #4ade8055;border-radius:10px;'
                f'padding:10px 16px;color:#4ade80;font-weight:700;">🏆 Goal reached! {this_week}/{goal} sessions this week</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="color:#94a3b8;font-size:14px;padding-top:8px;">'
                f'{this_week} of {goal} sessions · {remaining} to go</div>',
                unsafe_allow_html=True
            )

    st.progress(pct)


def render_heatmap(sessions, today):
    """GitHub-style contribution heatmap for the last 12 weeks."""
    st.subheader("📅 Activity — Last 12 Weeks")

    # Build date → session count map
    if not sessions.empty:
        counts = pd.to_datetime(sessions['date']).dt.date.value_counts().to_dict()
    else:
        counts = {}

    # Build 12 × 7 grid (Mon–Sun), most recent week on the right
    weeks = 12
    # Start from the Monday 12 weeks ago
    grid_end   = today
    grid_start = grid_end - timedelta(weeks=weeks) + timedelta(days=1)
    # Align to Monday
    grid_start -= timedelta(days=grid_start.weekday())

    # Collect columns (each column = one week, 7 days Mon–Sun)
    all_days = []
    d = grid_start
    while d <= grid_end:
        all_days.append(d)
        d += timedelta(days=1)

    # Group into weeks
    week_cols = [all_days[i:i+7] for i in range(0, len(all_days), 7)]

    # Color scale: 0=empty, 1=light, 2=mid, 3=dark, 4+=darkest
    def day_color(n):
        if n == 0:   return "#1e293b"
        if n == 1:   return "#166534"
        if n == 2:   return "#16a34a"
        if n == 3:   return "#4ade80"
        return "#bbf7d0"

    # Day labels on the left
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Build HTML grid
    cell = 14  # px per cell
    gap  = 3

    # Month labels row
    month_labels_html = '<div style="display:flex;gap:{g}px;margin-left:32px;margin-bottom:2px;">'.format(g=gap)
    prev_month = None
    for week in week_cols:
        first_day = week[0]
        label = first_day.strftime('%b') if first_day.month != prev_month else ""
        prev_month = first_day.month
        month_labels_html += f'<div style="width:{cell}px;font-size:10px;color:#64748b;text-align:center;">{label}</div>'
    month_labels_html += '</div>'

    # Grid rows (one per day of week)
    rows_html = '<div style="display:flex;gap:{g}px;">'.format(g=gap)

    # Day labels column
    rows_html += '<div style="display:flex;flex-direction:column;gap:{g}px;margin-right:4px;">'.format(g=gap)
    for label in day_labels:
        rows_html += f'<div style="height:{cell}px;line-height:{cell}px;font-size:10px;color:#64748b;width:26px;text-align:right;">{label}</div>'
    rows_html += '</div>'

    # Week columns
    for week in week_cols:
        rows_html += f'<div style="display:flex;flex-direction:column;gap:{gap}px;">'
        for day in week:
            n     = counts.get(day, 0)
            color = day_color(n)
            is_today = "border:1px solid #4ade80;" if day == today else ""
            future   = "opacity:0.3;" if day > today else ""
            title    = f"{day.strftime('%b %d')}: {n} session{'s' if n != 1 else ''}"
            rows_html += (
                f'<div title="{title}" style="width:{cell}px;height:{cell}px;'
                f'border-radius:3px;background:{color};{is_today}{future}"></div>'
            )
        rows_html += '</div>'

    rows_html += '</div>'

    # Legend
    legend_html = (
        '<div style="display:flex;align-items:center;gap:6px;margin-top:8px;">'
        '<span style="font-size:11px;color:#64748b;">Less</span>'
    )
    for color in ["#1e293b", "#166534", "#16a34a", "#4ade80", "#bbf7d0"]:
        legend_html += f'<div style="width:{cell}px;height:{cell}px;border-radius:3px;background:{color};"></div>'
    legend_html += '<span style="font-size:11px;color:#64748b;">More</span></div>'

    st.markdown(month_labels_html + rows_html + legend_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# QUEST BOARD
# ─────────────────────────────────────────────
def render_quest_board():
    st.subheader("⚔️ Quest Board")
    st.caption("Your subjects as quests. Complete them. Level up.")

    # Add quest expander
    with st.expander("➕ New Quest", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            name     = st.text_input("Quest name", placeholder="e.g. Learn Rust")
            category = st.text_input("Category",   placeholder="e.g. Programming, Language, Book")
        with col2:
            priority    = st.selectbox("Priority", ["High", "Medium", "Low"])
            goal        = st.text_input("Goal", placeholder="e.g. Build a CLI tool")
        target_date = st.date_input("Target date", value=None)

        if st.button("⚔️ Add Quest", type="primary"):
            if name.strip():
                add_subject(
                    name=name.strip(),
                    category=category or None,
                    priority=priority,
                    goal=goal or None,
                    target_date=target_date.strftime('%Y-%m-%d') if target_date else None
                )
                st.success(f"Quest '{name}' added!")
                st.rerun()
            else:
                st.error("Quest needs a name.")

    subjects = get_subjects()
    if subjects.empty:
        st.info("No quests yet. Add your first one above!")
        return

    # Status filter as pills
    status_options = ["All", "In Progress", "Not Started", "On Hold", "Completed"]
    filter_val = st.session_state.get('quest_filter', 'All')
    cols = st.columns(len(status_options))
    for i, s in enumerate(status_options):
        with cols[i]:
            if st.button(
                s, key=f"qf_{s}",
                type="primary" if filter_val == s else "secondary",
                use_container_width=True
            ):
                st.session_state.quest_filter = s
                st.rerun()

    if filter_val != 'All':
        subjects = subjects[subjects['status'] == filter_val]

    if subjects.empty:
        st.info(f"No quests with status '{filter_val}'.")
        return

    st.divider()

    # Render quest cards — 2 per row
    rows = [subjects.iloc[i:i+2] for i in range(0, len(subjects), 2)]
    for row_df in rows:
        cols = st.columns(2)
        for col_idx, (_, subj) in enumerate(row_df.iterrows()):
            with cols[col_idx]:
                render_quest_card(subj)


def render_quest_card(subj):
    """Render a single quest card."""
    status   = subj.get('status', 'Not Started')
    priority = subj.get('priority', 'Medium')
    progress = int(subj.get('completion_percentage') or 0)
    hours    = get_total_hours(subj['id'])

    s_color  = STATUS_COLORS.get(status, "#64748b")
    s_icon   = STATUS_ICONS.get(status, "🔘")
    p_color  = PRIORITY_COLORS.get(priority, "#94a3b8")

    # Days until target
    target_html = ""
    if subj.get('target_date'):
        try:
            target = datetime.strptime(str(subj['target_date'])[:10], '%Y-%m-%d').date()
            days_left = (target - datetime.today().date()).days
            if days_left < 0:
                target_html = f'<span style="color:#f87171;font-size:11px;">⚠️ {abs(days_left)}d overdue</span>'
            elif days_left <= 7:
                target_html = f'<span style="color:#fbbf24;font-size:11px;">⏰ {days_left}d left</span>'
            else:
                target_html = f'<span style="color:#64748b;font-size:11px;">📅 {days_left}d left</span>'
        except Exception:
            pass

    # Progress bar HTML
    bar_html = (
        f'<div style="background:#0f172a;border-radius:4px;height:6px;margin:10px 0 4px;">'
        f'<div style="background:{s_color};width:{progress}%;height:6px;border-radius:4px;transition:width 0.3s;"></div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;">'
        f'<span style="color:#64748b;font-size:11px;">{progress}% complete</span>'
        f'<span style="color:#64748b;font-size:11px;">⏱️ {hours}h</span>'
        f'</div>'
    )

    st.markdown(
        f'<div style="background:#1e293b;border:1px solid {s_color}44;border-radius:14px;padding:16px;margin-bottom:8px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">'
        f'<span style="font-size:16px;font-weight:700;color:#f8fafc;">{s_icon} {subj["name"]}</span>'
        f'<span style="background:{p_color}22;color:{p_color};border:1px solid {p_color}55;'
        f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;">{priority}</span>'
        f'</div>'
        f'{"<div style=color:#94a3b8;font-size:12px;margin-bottom:4px;>📂 " + subj["category"] + "</div>" if subj.get("category") else ""}'
        f'{"<div style=color:#94a3b8;font-size:12px;margin-bottom:4px;>🎯 " + subj["goal"] + "</div>" if subj.get("goal") else ""}'
        f'{target_html}'
        f'<div style="background:{s_color}22;color:{s_color};border:1px solid {s_color}44;'
        f'font-size:11px;font-weight:600;padding:2px 8px;border-radius:8px;display:inline-block;margin:6px 0;">'
        f'{status}</div>'
        f'{bar_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Action row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_progress = st.number_input(
            "%", min_value=0, max_value=100, value=progress, step=5,
            key=f"prog_{subj['id']}", label_visibility="collapsed"
        )
        if new_progress != progress:
            update_subject_progress(subj['id'], new_progress)
            st.rerun()
    with col2:
        status_opts = ["Not Started", "In Progress", "On Hold", "Completed"]
        cur_idx = status_opts.index(status) if status in status_opts else 0
        new_status = st.selectbox(
            "Status", status_opts, index=cur_idx,
            key=f"stat_{subj['id']}", label_visibility="collapsed"
        )
        if new_status != status:
            update_subject_status(subj['id'], new_status)
            st.rerun()
    with col3:
        st.write("")  # spacer
    with col4:
        if st.button("🗑️", key=f"del_{subj['id']}", help="Delete quest"):
            delete_subject(subj['id'])
            st.rerun()


# ─────────────────────────────────────────────
# LOG SESSION
# ─────────────────────────────────────────────
def render_log_session():
    st.subheader("⏱️ Log a Study Session")

    subjects = get_subjects()
    if subjects.empty:
        st.info("Add a quest first in the ⚔️ Quest Board tab.")
        return

    subject_names = {row['id']: row['name'] for _, row in subjects.iterrows()}

    with st.form("log_session_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject_id = st.selectbox(
                "Quest",
                options=list(subject_names.keys()),
                format_func=lambda x: subject_names[x]
            )
            duration = st.slider("Duration (min)", 5, 240, 30, step=5)
        with col2:
            content = st.text_input("What did you study?", placeholder="e.g. Chapter 3 — Closures")
            rating  = st.select_slider(
                "Session quality",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: {1:"😴 Rough", 2:"😐 Okay", 3:"🙂 Good", 4:"😊 Great", 5:"🔥 Flow state"}[x]
            )
        notes = st.text_area("Notes (optional)", placeholder="Key takeaways, questions, ideas...")

        if st.form_submit_button("✅ Log Session", type="primary", use_container_width=True):
            add_session(
                subject_id=subject_id,
                duration=duration,
                content=content or None,
                notes=notes or None,
                rating=rating
            )
            st.success("Session logged! 🎉")
            st.rerun()

    # Recent sessions
    st.divider()
    st.subheader("📋 Recent Sessions")
    recent = get_sessions(days=7)
    if recent.empty:
        st.info("No sessions in the last 7 days.")
        return

    for _, row in recent.head(8).iterrows():
        subj = get_subject(row['subject_id'])
        name = subj['name'] if subj is not None else "Unknown"
        dur  = row.get('duration', 0) or 0
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"**{name}**")
            if row.get('content'):
                st.caption(row['content'])
        with col2:
            st.write(f"⏱️ {int(dur)} min")
        with col3:
            if st.button("🗑️", key=f"del_sess_{row['id']}"):
                delete_session(row['id'])
                st.rerun()
        st.divider()


# ─────────────────────────────────────────────
# MILESTONES
# ─────────────────────────────────────────────
def render_milestones():
    st.subheader("🏆 Milestones")

    subjects = get_subjects()
    if subjects.empty:
        st.info("Add some quests first to start tracking milestones.")
        return

    with st.expander("➕ Add Milestone", expanded=False):
        subject_names = {row['id']: row['name'] for _, row in subjects.iterrows()}
        subj_id = st.selectbox(
            "Quest", options=list(subject_names.keys()),
            format_func=lambda x: subject_names[x], key="ms_subject"
        )
        ms_name  = st.text_input("Milestone", placeholder="e.g. Finished Part 1")
        ms_notes = st.text_area("Notes (optional)")

        if st.button("🏆 Add Milestone", type="primary"):
            if ms_name.strip():
                add_milestone(subj_id, ms_name.strip(), ms_notes or None)
                st.success("Milestone added! 🎉")
                st.rerun()
            else:
                st.error("Enter a milestone name.")

    milestones = get_milestones()
    if milestones.empty:
        st.info("No milestones yet. Celebrate your wins!")
        return

    for _, row in milestones.iterrows():
        subj = get_subject(row['subject_id'])
        subj_name = subj['name'] if subj is not None else "Unknown"
        date_fmt  = pd.to_datetime(row['achieved_date']).strftime('%b %d, %Y')

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #4ade8033;border-radius:10px;padding:12px 16px;">'
                f'<div style="font-weight:700;color:#f8fafc;">🏆 {row["name"]}</div>'
                f'<div style="color:#94a3b8;font-size:12px;margin-top:4px;">📚 {subj_name} · 📅 {date_fmt}</div>'
                f'{"<div style=color:#64748b;font-size:12px;margin-top:4px;>" + row["notes"] + "</div>" if row.get("notes") else ""}'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            if st.button("🗑️", key=f"del_ms_{row['id']}"):
                delete_milestone(row['id'])
                st.rerun()
        st.write("")
