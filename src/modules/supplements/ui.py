"""
Supplements matrix UI components.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
from .data import (
    get_supplements_for_month,
    get_supplements_for_date,
    set_supplement_taken,
    get_daily_summary,
    get_weekly_summary
)
from .config import DEFAULT_SUPPLEMENTS, get_supplement_dosage

def render_supplement_tracker():
    """Main supplements matrix interface."""
    st.title("💊 Supplements Tracker")
    st.caption("Track your daily supplements with a matrix view")
    
    # Initialize session state
    if 'supplement_week_start' not in st.session_state:
        today = datetime.today().date()
        st.session_state.supplement_week_start = today - timedelta(days=today.weekday())
    
    # Week navigation
    col1, col2, col3, col4, col5 = st.columns([0.8, 0.8, 2, 0.8, 0.8])
    
    with col1:
        if st.button("◀", use_container_width=True):
            st.session_state.supplement_week_start -= timedelta(days=7)
            st.rerun()
    with col2:
        st.caption("Prev")
    with col3:
        week_end = st.session_state.supplement_week_start + timedelta(days=6)
        st.markdown(
            f"<div style='text-align: center; font-size: 16px; font-weight: 600; color: #f8fafc;'>"
            f"📅 {st.session_state.supplement_week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
            f"</div>",
            unsafe_allow_html=True
        )
    with col4:
        st.caption("Next")
    with col5:
        if st.button("▶", use_container_width=True):
            st.session_state.supplement_week_start += timedelta(days=7)
            st.rerun()
    
    # Today button
    if st.button("📅 This Week", use_container_width=True):
        today = datetime.today().date()
        st.session_state.supplement_week_start = today - timedelta(days=today.weekday())
        st.rerun()
    
    st.divider()
    
    # Render the matrix
    render_weekly_matrix(st.session_state.supplement_week_start)

def render_weekly_matrix(week_start):
    """Render the supplements matrix for a specific week."""
    
    # Get the 7 days of the week
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    date_strings = [d.strftime("%Y-%m-%d") for d in week_dates]
    day_names = [d.strftime("%a") for d in week_dates]
    day_numbers = [d.strftime("%d") for d in week_dates]
    
    # Get data for this week
    start_date = week_start.strftime("%Y-%m-%d")
    end_date = (week_start + timedelta(days=6)).strftime("%Y-%m-%d")
    
    from .data import get_supplements
    df = get_supplements(start_date, end_date)
    
    # Create a lookup for quick access
    supplement_data = {}
    for _, row in df.iterrows():
        date = row['Date']
        name = row['supplement_name']
        if date not in supplement_data:
            supplement_data[date] = {}
        supplement_data[date][name] = {
            'taken': row['taken'],
            'dosage': row['dosage'],
            'unit': row['unit']
        }
    
    # Create the matrix data
    matrix_data = {}
    for supp in DEFAULT_SUPPLEMENTS:
        name = supp['name']
        matrix_data[name] = {
            'dosage': supp['dosage'],
            'unit': supp['unit'],
            'days': []
        }
        for date in date_strings:
            if date in supplement_data and name in supplement_data[date]:
                matrix_data[name]['days'].append(bool(supplement_data[date][name]['taken']))
            else:
                matrix_data[name]['days'].append(False)
    
    # Calculate daily totals
    daily_totals = []
    for i in range(7):
        taken = 0
        total = len(DEFAULT_SUPPLEMENTS)
        for name in matrix_data:
            if matrix_data[name]['days'][i]:
                taken += 1
        daily_totals.append(f"{taken}/{total}")
    
    today = datetime.today().date()
    
    # --- Render the matrix with custom styling ---
    st.markdown("""
    <style>
    .matrix-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #2a3a4b;
    }
    .supplement-name {
        font-weight: 500;
        color: #f8fafc;
    }
    .supplement-dosage {
        font-size: 11px;
        color: #94a3b8;
    }
    .day-header {
        font-weight: 600;
        color: #94a3b8;
        text-align: center;
        font-size: 13px;
    }
    .day-number {
        font-size: 11px;
        color: #64748b;
        text-align: center;
    }
    .total-label {
        font-weight: 600;
        color: #94a3b8;
    }
    .total-value {
        font-weight: 600;
        color: #4ade80;
        text-align: center;
    }
    .future-cell {
        opacity: 0.4;
        pointer-events: none;
    }
    .future-label {
        color: #64748b;
        font-size: 12px;
        text-align: center;
        padding: 8px 0;
    }
    .checkbox-disabled {
        opacity: 0.3;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("📋 Supplement Matrix")
    st.caption("💡 Click a checkbox to mark a supplement as taken. Changes auto-save.")
    
    # Headers
    cols = st.columns([1.5] + [0.8] * 7)
    with cols[0]:
        st.markdown("**Supplement**")
    for i, (day, num) in enumerate(zip(day_names, day_numbers)):
        with cols[i + 1]:
            st.markdown(f"**{day}**")
            st.caption(f"{num}")
    
    st.divider()
    
    # Rows for each supplement
    for supp_name, supp_data in matrix_data.items():
        cols = st.columns([1.5] + [0.8] * 7)
        
        with cols[0]:
            dosage_text = get_supplement_dosage(supp_name)
            st.write(f"**{supp_name}**")
            st.caption(dosage_text)
        
        for i, date_str in enumerate(date_strings):
            with cols[i + 1]:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                is_future = date_obj > today
                current_value = bool(supp_data['days'][i])
                dosage = supp_data['dosage']
                unit = supp_data['unit']
                
                if is_future:
                    # Future date - show lock icon
                    st.markdown(
                        f"<div style='text-align: center; font-size: 18px; opacity: 0.3;'>🔒</div>",
                        unsafe_allow_html=True
                    )
                    # Hidden checkbox for consistency
                    st.checkbox(
                        f"Future: {supp_name} on {date_str}",
                        value=False,
                        key=f"supp_{supp_name}_{date_str}_future",
                        disabled=True,
                        label_visibility="collapsed"
                    )
                else:
                    # Past or today - show checkbox with proper label
                    new_value = st.checkbox(
                        f"Taken {supp_name} on {date_str}",
                        value=current_value,
                        key=f"supp_{supp_name}_{date_str}",
                        disabled=False,
                        label_visibility="collapsed"
                    )

                    if new_value != current_value:
                        set_supplement_taken(date_str, supp_name, dosage, unit, new_value)
    
    # Daily totals row
    st.divider()
    cols = st.columns([1.5] + [0.8] * 7)
    with cols[0]:
        st.markdown("**Total**")
    for i, total in enumerate(daily_totals):
        with cols[i + 1]:
            st.markdown(f"**{total}**")
    
    # Legend
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("✅ = Taken")
    with col2:
        st.markdown("⬜ = Not taken")
    with col3:
        st.markdown("🔒 = Future date")
    with col4:
        st.markdown("📅 = Today")