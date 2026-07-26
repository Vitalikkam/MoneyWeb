"""
Learning module UI components.
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

def render_learning_tracker():
    """Main learning tracker interface."""
    st.title("🎓 Learning Tracker")
    st.caption("Track your study progress across any subject")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Dashboard",
        "📖 Subjects",
        "⏱️ Log Session",
        "🏆 Milestones"
    ])
    
    with tab1:
        render_dashboard()
    with tab2:
        render_subjects()
    with tab3:
        render_log_session()
    with tab4:
        render_milestones()

def render_dashboard():
    """Render the learning dashboard."""
    st.subheader("📊 Learning Dashboard")
    
    # Stats
    subjects = get_subjects()
    total_subjects = len(subjects)
    active_subjects = len(subjects[subjects['status'] == 'In Progress']) if not subjects.empty else 0
    completed_subjects = len(subjects[subjects['status'] == 'Completed']) if not subjects.empty else 0
    
    streak = get_study_streak()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Total Subjects", total_subjects)
    col2.metric("🔄 In Progress", active_subjects)
    col3.metric("✅ Completed", completed_subjects)
    col4.metric("🔥 Streak", f"{streak} days")
    
    # Recent sessions
    st.subheader("📋 Recent Study Sessions")
    sessions = get_sessions(days=30)
    if sessions.empty:
        st.info("No study sessions logged yet. Start tracking your learning!")
    else:
        # Show last 5 sessions
        for _, row in sessions.head(5).iterrows():
            subject = get_subject(row['subject_id'])
            subject_name = subject['name'] if subject is not None else "Unknown"
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{subject_name}**")
                    if row['content']:
                        st.caption(row['content'])
                with col2:
                    st.write(f"⏱️ {row['duration']} min")
                with col3:
                    if row['rating']:
                        stars = "⭐" * row['rating']
                        st.write(stars)
                st.divider()
    
    # Quick add session button
    if st.button("➕ Log Study Session", use_container_width=True):
        st.session_state.learning_tab = "⏱️ Log Session"
        st.rerun()

def render_subjects():
    """Render subjects management."""
    st.subheader("📖 Your Subjects")
    
    # Add new subject form
    with st.expander("➕ Add New Subject", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Subject Name", placeholder="e.g., Machine Learning")
            category = st.text_input("Category", placeholder="e.g., Course, Book, Language")
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            goal = st.text_input("Goal", placeholder="e.g., Finish by December")
        
        target_date = st.date_input("Target Date", value=None)
        
        if st.button("💾 Add Subject", type="primary"):
            if name:
                add_subject(
                    name=name,
                    category=category if category else None,
                    priority=priority,
                    goal=goal if goal else None,
                    target_date=target_date.strftime('%Y-%m-%d') if target_date else None
                )
                st.success(f"✅ Added subject: {name}")
                st.rerun()
            else:
                st.error("Please enter a subject name.")
    
    # Display subjects
    subjects = get_subjects()
    if subjects.empty:
        st.info("No subjects yet. Add your first subject above!")
        return
    
    # Filter
    status_filter = st.selectbox("Filter by status", ["All", "Not Started", "In Progress", "Completed", "On Hold"])
    if status_filter != "All":
        subjects = subjects[subjects['status'] == status_filter]
    
    # Show subjects as cards
    for _, row in subjects.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {row['name']}")
                if row['category']:
                    st.caption(f"📂 {row['category']}")
                if row['goal']:
                    st.caption(f"🎯 {row['goal']}")
                hours = get_total_hours(row['id'])
                st.caption(f"⏱️ {hours}h studied")
                
                # Progress bar
                progress = row['completion_percentage'] or 0
                st.progress(progress / 100, text=f"{progress}%")
            
            with col2:
                # Status badge
                status_colors = {
                    "Not Started": "#64748b",
                    "In Progress": "#60a5fa",
                    "Completed": "#4ade80",
                    "On Hold": "#fbbf24",
                }
                color = status_colors.get(row['status'], "#64748b")
                st.markdown(f"""
                <span style="background:{color};color:#0f172a;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">
                    {row['status']}
                </span>
                """, unsafe_allow_html=True)
            
            with col3:
                # Actions
                if st.button("🗑️", key=f"del_subject_{row['id']}"):
                    delete_subject(row['id'])
                    st.rerun()
            
            st.divider()

def render_log_session():
    """Render study session logging."""
    st.subheader("⏱️ Log a Study Session")
    
    subjects = get_subjects()
    if subjects.empty:
        st.info("Please add a subject first before logging sessions.")
        return
    
    subject_names = {row['id']: row['name'] for _, row in subjects.iterrows()}
    
    with st.form("log_session_form"):
        col1, col2 = st.columns(2)
        with col1:
            subject_id = st.selectbox(
                "Subject",
                options=list(subject_names.keys()),
                format_func=lambda x: subject_names[x]
            )
            duration = st.number_input("Duration (minutes)", min_value=1, step=5, value=30)
        with col2:
            content = st.text_input("Content", placeholder="e.g., Chapter 3: Neural Networks")
            rating = st.slider("Rating", 1, 5, 3, help="How productive was this session?")
            notes = st.text_area("Notes (optional)", placeholder="Key takeaways...")
        
        if st.form_submit_button("💾 Log Session", type="primary"):
            add_session(
                subject_id=subject_id,
                duration=duration,
                content=content if content else None,
                notes=notes if notes else None,
                rating=rating
            )
            st.success("✅ Session logged!")
            st.rerun()
    
    # Show recent sessions
    st.subheader("📋 Recent Sessions")
    sessions = get_sessions(days=7)
    if sessions.empty:
        st.info("No sessions logged in the last 7 days.")
    else:
        for _, row in sessions.head(5).iterrows():
            subject = get_subject(row['subject_id'])
            subject_name = subject['name'] if subject is not None else "Unknown"
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{subject_name}**")
                if row['content']:
                    st.caption(row['content'])
            with col2:
                st.write(f"⏱️ {row['duration']} min")
            with col3:
                if st.button("❌", key=f"del_session_{row['id']}"):
                    delete_session(row['id'])
                    st.rerun()
            st.divider()

def render_milestones():
    """Render milestones management."""
    st.subheader("🏆 Milestones")
    
    subjects = get_subjects()
    if subjects.empty:
        st.info("Add some subjects first to start tracking milestones.")
        return
    
    # Add milestone
    with st.expander("➕ Add Milestone", expanded=False):
        subject_names = {row['id']: row['name'] for _, row in subjects.iterrows()}
        subject_id = st.selectbox(
            "Subject",
            options=list(subject_names.keys()),
            format_func=lambda x: subject_names[x],
            key="milestone_subject"
        )
        milestone_name = st.text_input("Milestone", placeholder="e.g., Finished Chapter 3")
        milestone_notes = st.text_area("Notes (optional)")
        
        if st.button("💾 Add Milestone", type="primary"):
            if milestone_name:
                add_milestone(subject_id, milestone_name, milestone_notes if milestone_notes else None)
                st.success("✅ Milestone added!")
                st.rerun()
            else:
                st.error("Please enter a milestone name.")
    
    # Display milestones
    milestones = get_milestones()
    if milestones.empty:
        st.info("No milestones yet. Start celebrating your achievements!")
        return
    
    for _, row in milestones.iterrows():
        subject = get_subject(row['subject_id'])
        subject_name = subject['name'] if subject is not None else "Unknown"
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"**{row['name']}**")
                st.caption(f"📚 {subject_name}")
                if row['notes']:
                    st.caption(f"📝 {row['notes']}")
            with col2:
                st.caption(f"📅 {row['achieved_date']}")
            with col3:
                if st.button("❌", key=f"del_milestone_{row['id']}"):
                    delete_milestone(row['id'])
                    st.rerun()
            st.divider()