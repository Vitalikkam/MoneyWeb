#!/usr/bin/env python3
"""
MCP Server for the Learning Module.
Exposes study tracking tools, resources, and prompts to AI assistants like Claude.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Optional

# Add project root to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from src.modules.learning.data import (
    get_subjects,
    get_subject,
    get_sessions,
    get_total_hours,
    get_study_streak,
    add_session,
    add_subject,
    add_milestone,
    get_milestones,
    update_subject_status,
    update_subject_progress,
    delete_session,
    delete_subject,
)

# Initialize MCP server
mcp = FastMCP("Learning Tracker")

# ============================================
# TOOLS (Actions the AI can perform)
# ============================================

@mcp.tool()
def add_study_session(subject_name: str, duration: int, content: str = "", rating: int = 3) -> str:
    """
    Log a study session for a subject.
    
    Args:
        subject_name: Name of the subject (e.g., "Machine Learning")
        duration: Duration in minutes
        content: What was studied (e.g., "Chapter 3: Neural Networks")
        rating: Rating 1-5 (1=low, 5=high)
    """
    # Find the subject by name
    subjects = get_subjects()
    subject_row = subjects[subjects['name'].str.lower() == subject_name.lower()]
    
    if subject_row.empty:
        return f"❌ Subject '{subject_name}' not found. Please add it first using add_subject."
    
    subject_id = subject_row.iloc[0]['id']
    
    # Add the session
    session_id = add_session(
        subject_id=subject_id,
        duration=duration,
        content=content if content else None,
        rating=rating
    )
    
    if session_id:
        return f"✅ Logged {duration}min study session for '{subject_name}' ({content if content else 'General study'}) with rating {rating}/5"
    else:
        return "❌ Failed to log session. Please try again."

@mcp.tool()
def add_subject_tool(name: str, category: str = "", priority: str = "Medium", goal: str = "") -> str:
    """
    Add a new learning subject.
    
    Args:
        name: Name of the subject (e.g., "Machine Learning")
        category: Category (e.g., "Course", "Book", "Language")
        priority: High, Medium, or Low
        goal: What you want to achieve
    """
    try:
        subject_id = add_subject(
            name=name,
            category=category if category else None,
            priority=priority,
            goal=goal if goal else None,
            status="Not Started"
        )
        return f"✅ Added subject '{name}' with ID {subject_id}"
    except Exception as e:
        return f"❌ Failed to add subject: {e}"

@mcp.tool()
def get_study_summary(subject_name: str = "") -> str:
    """
    Get study summary for a specific subject or all subjects.
    
    Args:
        subject_name: Name of the subject (leave empty for all subjects)
    """
    if subject_name:
        subjects = get_subjects()
        subject_row = subjects[subjects['name'].str.lower() == subject_name.lower()]
        
        if subject_row.empty:
            return f"❌ Subject '{subject_name}' not found."
        
        subject = subject_row.iloc[0]
        subject_id = subject['id']
        total_hours = get_total_hours(subject_id)
        sessions = get_sessions(subject_id)
        session_count = len(sessions)
        streak = get_study_streak()
        
        return f"""
📊 Study Summary for: {subject['name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Status: {subject['status']}
📈 Progress: {subject['completion_percentage'] or 0}%
⏱️ Total Hours: {total_hours}h
📝 Sessions: {session_count}
🔥 Streak: {streak} days
"""
    else:
        # All subjects summary
        subjects = get_subjects()
        if subjects.empty:
            return "No subjects found. Add your first subject using add_subject_tool."
        
        total_subjects = len(subjects)
        active = len(subjects[subjects['status'] == 'In Progress'])
        completed = len(subjects[subjects['status'] == 'Completed'])
        
        # Calculate total hours across all subjects
        total_hours = 0
        for _, row in subjects.iterrows():
            total_hours += get_total_hours(row['id'])
        
        streak = get_study_streak()
        
        result = f"""
📊 Study Summary (All Subjects)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Total Subjects: {total_subjects}
🔄 In Progress: {active}
✅ Completed: {completed}
⏱️ Total Hours: {total_hours:.1f}h
🔥 Streak: {streak} days
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return result

@mcp.tool()
def get_weekly_report() -> str:
    """
    Get a weekly study report with insights.
    """
    # Get sessions from the last 7 days
    import pandas as pd
    sessions = get_sessions(days=7)
    
    if sessions.empty:
        return "📊 No study activity in the last 7 days. Time to get started!"
    
    # Group by subject
    subjects = get_subjects()
    subject_names = {row['id']: row['name'] for _, row in subjects.iterrows()}
    
    # Calculate stats
    total_minutes = sessions['duration'].sum()
    total_hours = total_minutes / 60
    session_count = len(sessions)
    
    # Group by subject
    subject_totals = sessions.groupby('subject_id')['duration'].sum().sort_values(ascending=False)
    
    result = f"""
📅 Weekly Study Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Total Sessions: {session_count}
⏱️ Total Time: {total_hours:.1f}h ({total_minutes:.0f} min)

Top Subjects:
"""
    
    for subject_id, minutes in subject_totals.head(5).items():
        name = subject_names.get(subject_id, "Unknown")
        hours = minutes / 60
        result += f"  • {name}: {hours:.1f}h\n"
    
    # Calculate best day
    sessions['day'] = pd.to_datetime(sessions['date']).dt.strftime('%A')
    best_day = sessions.groupby('day')['duration'].sum().sort_values(ascending=False)
    if not best_day.empty:
        result += f"\n🏆 Best Day: {best_day.index[0]} ({best_day.iloc[0]} min)"
    
    # Check streak
    streak = get_study_streak()
    if streak > 0:
        result += f"\n🔥 Current Streak: {streak} days"
    
    return result

@mcp.tool()
def add_milestone_tool(subject_name: str, milestone_name: str, notes: str = "") -> str:
    """
    Add a milestone for a subject.
    
    Args:
        subject_name: Name of the subject
        milestone_name: Name of the milestone (e.g., "Finished Chapter 3")
        notes: Additional notes about the milestone
    """
    subjects = get_subjects()
    subject_row = subjects[subjects['name'].str.lower() == subject_name.lower()]
    
    if subject_row.empty:
        return f"❌ Subject '{subject_name}' not found."
    
    subject_id = subject_row.iloc[0]['id']
    
    try:
        milestone_id = add_milestone(subject_id, milestone_name, notes if notes else None)
        return f"✅ Added milestone '{milestone_name}' for '{subject_name}'"
    except Exception as e:
        return f"❌ Failed to add milestone: {e}"

@mcp.tool()
def update_subject_status_tool(subject_name: str, status: str) -> str:
    """
    Update the status of a subject.
    
    Args:
        subject_name: Name of the subject
        status: One of: "Not Started", "In Progress", "Completed", "On Hold"
    """
    valid_statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
    if status not in valid_statuses:
        return f"❌ Invalid status. Choose from: {', '.join(valid_statuses)}"
    
    subjects = get_subjects()
    subject_row = subjects[subjects['name'].str.lower() == subject_name.lower()]
    
    if subject_row.empty:
        return f"❌ Subject '{subject_name}' not found."
    
    subject_id = subject_row.iloc[0]['id']
    
    try:
        update_subject_status(subject_id, status)
        return f"✅ Updated '{subject_name}' status to '{status}'"
    except Exception as e:
        return f"❌ Failed to update status: {e}"

# ============================================
# RESOURCES (Read-only data)
# ============================================

@mcp.resource("subjects://active")
def get_active_subjects() -> str:
    """Get all active (In Progress) subjects."""
    subjects = get_subjects("In Progress")
    if subjects.empty:
        return "No active subjects."
    
    result = "📚 Active Subjects:\n"
    for _, row in subjects.iterrows():
        hours = get_total_hours(row['id'])
        progress = row['completion_percentage'] or 0
        result += f"  • {row['name']}: {progress}% complete, {hours}h studied\n"
    
    return result

@mcp.resource("streak://current")
def get_streak_resource() -> str:
    """Get the current study streak."""
    streak = get_study_streak()
    return f"🔥 Current streak: {streak} days"

@mcp.resource("milestones://recent")
def get_recent_milestones() -> str:
    """Get recent milestones."""
    milestones = get_milestones()
    if milestones.empty:
        return "No milestones yet."
    
    result = "🏆 Recent Milestones:\n"
    for _, row in milestones.head(5).iterrows():
        subject = get_subject(row['subject_id'])
        subject_name = subject['name'] if subject is not None else "Unknown"
        result += f"  • {row['name']} ({subject_name}) - {row['achieved_date']}\n"
    
    return result

# ============================================
# PROMPTS (Reusable templates)
# ============================================

@mcp.prompt()
def weekly_review_prompt() -> str:
    """Generate a prompt for a weekly study review."""
    return """
Please review my study activity for the past week and give me insights.

I want to know:
1. Which subjects I studied the most
2. How consistent I've been
3. Areas where I need to improve
4. Suggestions for next week

Use the get_weekly_report tool to get the data first.
"""

@mcp.prompt()
def daily_check_in() -> str:
    """Generate a prompt for a daily check-in."""
    return """
Check in on my daily learning progress.

1. What subjects should I focus on today?
2. Am I on track with my goals?
3. What should I study next?

Use the get_study_summary tool to see my current progress.
"""

@mcp.prompt()
def goal_setting() -> str:
    """Generate a prompt for setting new learning goals."""
    return """
Help me set new learning goals for the next month.

I want to:
1. Set realistic study targets
2. Plan my weekly schedule
3. Identify milestones to track

Use the get_study_summary tool to understand my current progress first.
"""

# ============================================
# RUN THE SERVER
# ============================================

if __name__ == "__main__":
    print("🎓 Learning Tracker MCP Server")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📚 Tools: add_study_session, add_subject_tool, get_study_summary")
    print("📊 Resources: subjects://active, streak://current, milestones://recent")
    print("📝 Prompts: weekly_review_prompt, daily_check_in, goal_setting")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Waiting for connections...")
    mcp.run(transport="stdio")
    print(f"Working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Database path: {os.path.expanduser('~/Mycode/MymoneyWeb/MymoneyWeb/finances.db')}", file=sys.stderr)