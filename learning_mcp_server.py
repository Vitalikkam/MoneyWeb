#!/usr/bin/env python3
"""
Life Dashboard MCP Server
Covers: Learning, Exercises, Vocabulary, Supplements
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force production DB
os.environ["APP_ENV"] = "prod"

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Life Dashboard")


# ─────────────────────────────────────────────────────────────
# LEARNING
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def log_study_session(subject_name: str, duration: int, content: str = "", rating: int = 3) -> str:
    """
    Log a study session.

    Args:
        subject_name: Name of the subject (e.g. "Machine Learning")
        duration: Duration in minutes
        content: What you studied (e.g. "Chapter 5 — backprop")
        rating: How productive it felt, 1–5
    """
    from src.modules.learning.data import get_subjects, add_session
    subjects = get_subjects()
    match = subjects[subjects['name'].str.lower() == subject_name.lower()]
    if match.empty:
        # fuzzy — try contains
        match = subjects[subjects['name'].str.lower().str.contains(subject_name.lower())]
    if match.empty:
        names = subjects['name'].tolist()
        return f"❌ Subject '{subject_name}' not found. Available: {names}"
    subject_id = match.iloc[0]['id']
    add_session(subject_id=subject_id, duration=duration, content=content or None, rating=rating)
    return f"✅ Logged {duration}min on '{match.iloc[0]['name']}'" + (f" — {content}" if content else "") + f" (rating {rating}/5)"


@mcp.tool()
def add_learning_subject(name: str, category: str = "", priority: str = "Medium", goal: str = "") -> str:
    """
    Add a new learning subject / quest.

    Args:
        name: Subject name
        category: e.g. Course, Book, Language
        priority: High / Medium / Low
        goal: What you want to achieve
    """
    from src.modules.learning.data import add_subject
    add_subject(name=name, category=category or None, priority=priority, goal=goal or None)
    return f"✅ Added subject '{name}'"


@mcp.tool()
def get_learning_summary() -> str:
    """Get an overview of all learning subjects and recent activity."""
    from src.modules.learning.data import get_subjects, get_sessions, get_total_hours, get_study_streak
    subjects = get_subjects()
    streak = get_study_streak()
    sessions = get_sessions(days=7)
    week_count = len(sessions)
    week_min = int(sessions['duration'].sum()) if not sessions.empty else 0

    lines = [f"🔥 Streak: {streak} days | 📅 This week: {week_count} sessions ({week_min} min)\n"]
    if subjects.empty:
        lines.append("No subjects yet.")
    else:
        for _, s in subjects.iterrows():
            h = get_total_hours(s['id'])
            p = int(s.get('completion_percentage') or 0)
            lines.append(f"  • {s['name']} [{s['status']}] — {p}% · {h}h total")
    return "\n".join(lines)


@mcp.tool()
def update_learning_progress(subject_name: str, percentage: int) -> str:
    """
    Update completion percentage for a subject.

    Args:
        subject_name: Subject name
        percentage: 0–100
    """
    from src.modules.learning.data import get_subjects, update_subject_progress
    subjects = get_subjects()
    match = subjects[subjects['name'].str.lower().str.contains(subject_name.lower())]
    if match.empty:
        return f"❌ Subject '{subject_name}' not found."
    update_subject_progress(match.iloc[0]['id'], percentage)
    return f"✅ Set '{match.iloc[0]['name']}' to {percentage}%"


@mcp.tool()
def add_learning_milestone(subject_name: str, milestone: str, notes: str = "") -> str:
    """
    Add a milestone for a subject.

    Args:
        subject_name: Subject name
        milestone: e.g. "Finished Part 1"
        notes: Optional notes
    """
    from src.modules.learning.data import get_subjects, add_milestone
    subjects = get_subjects()
    match = subjects[subjects['name'].str.lower().str.contains(subject_name.lower())]
    if match.empty:
        return f"❌ Subject '{subject_name}' not found."
    add_milestone(match.iloc[0]['id'], milestone, notes or None)
    return f"✅ Milestone '{milestone}' added to '{match.iloc[0]['name']}'"


# ─────────────────────────────────────────────────────────────
# EXERCISES
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def log_workout(workout_type: str, energy_level: int = 3, notes: str = "", date: str = "") -> str:
    """
    Log a workout. Call this when the user mentions exercising, going to the gym, running, etc.

    Args:
        workout_type: e.g. "Gym", "Run", "Yoga", "Cycling", "Walk", "Boxing", "Home workout"
        energy_level: How they felt, 1 (exhausted) to 5 (amazing)
        notes: What they did, any details
        date: YYYY-MM-DD, defaults to today
    """
    from src.modules.exercises.data import log_exercise
    d = date if date else datetime.today().strftime('%Y-%m-%d')
    log_exercise(date=d, workout_type=workout_type, notes=notes or None, energy_level=energy_level)
    energy_labels = {1: "😴 Exhausted", 2: "😐 Low", 3: "🙂 Normal", 4: "😊 Good", 5: "🔥 Amazing"}
    return f"✅ Logged {workout_type} on {d} — {energy_labels.get(energy_level, '')}" + (f" | {notes}" if notes else "")


@mcp.tool()
def get_exercise_summary() -> str:
    """Get workout stats: streak, this week, this month, recent workouts."""
    from src.modules.exercises.data import get_stats, get_exercises
    stats = get_stats()
    recent = get_exercises(days=7)

    lines = [
        f"💪 Total: {stats['total_workouts']} workouts",
        f"📅 This week: {stats['this_week']} | 🗓️ This month: {stats['this_month']}",
        f"🔥 Streak: {stats['streak']} days",
    ]
    if not recent.empty:
        lines.append("\nRecent workouts:")
        for _, row in recent.head(5).iterrows():
            d = str(row['date'])[:10]
            lines.append(f"  • {row['workout_type']} on {d}" + (f" — {row['notes']}" if row.get('notes') else ""))
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# VOCABULARY
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def add_word(word: str, definition: str, cefr_level: str = "C1",
             example: str = "", translation: str = "") -> str:
    """
    Add a word to vocabulary.

    Args:
        word: The English word
        definition: Its definition
        cefr_level: B2 / C1 / C2
        example: Example sentence
        translation: Russian translation
    """
    from src.modules.vocabulary.data import add_vocabulary, word_exists
    w = word.lower().strip()
    if word_exists(w):
        return f"⚠️ '{w}' is already in your vocabulary."
    add_vocabulary(
        word=w,
        cefr_level=cefr_level,
        definition=definition,
        example=example or "",
        translation=translation or None,
        importance=3,
        category="manual",
        mastery=3
    )
    return f"✅ Added '{w}' ({cefr_level})" + (f" — {translation}" if translation else "")


@mcp.tool()
def lookup_and_add_word(word: str) -> str:
    """
    Fetch word data from dictionary API and add it to vocabulary automatically.
    Use this when user mentions a word they want to learn.

    Args:
        word: The English word to look up and add
    """
    from src.modules.vocabulary.api import VocabularyAPI
    from src.modules.vocabulary.data import add_vocabulary, word_exists
    w = word.lower().strip()
    if word_exists(w):
        return f"⚠️ '{w}' is already in your vocabulary."
    api = VocabularyAPI()
    data = api.get_word_data(w)
    if not data.get('found'):
        return f"⚠️ '{w}' not found in dictionary. Use add_word with a manual definition."
    add_vocabulary(
        word=w,
        cefr_level=data.get('cefr_level') or 'C1',
        definition=data.get('definition', ''),
        example=data.get('example', ''),
        translation=data.get('translation'),
        importance=3,
        category="manual",
        mastery=3
    )
    return (
        f"✅ Added '{w}' ({data.get('cefr_level', 'C1')})\n"
        f"📖 {data.get('definition', '')}\n"
        + (f"🇷🇺 {data.get('translation')}" if data.get('translation') else "")
    )


@mcp.tool()
def get_vocabulary_summary() -> str:
    """Get vocabulary stats and words due for review."""
    from src.modules.vocabulary.data import get_stats, get_words_due_for_review
    stats = get_stats()
    due = get_words_due_for_review()
    lines = [
        f"📚 Total words: {stats['total']}",
        f"🔄 Due for review: {stats['due']}",
        f"⭐ Avg mastery: {stats['avg_mastery']}/5",
    ]
    if stats['by_level']:
        lines.append("By level: " + " | ".join(f"{k}: {v}" for k, v in stats['by_level'].items()))
    if not due.empty:
        lines.append(f"\nWords to review: {', '.join(due['word'].head(10).tolist())}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# SUPPLEMENTS
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def log_supplement(supplement_name: str, taken: bool = True, date: str = "") -> str:
    """
    Mark a supplement as taken or not taken.

    Args:
        supplement_name: e.g. "Vitamin D", "Magnesium", "Omega 3"
        taken: True = taken, False = not taken
        date: YYYY-MM-DD, defaults to today
    """
    from src.modules.supplements.data import set_supplement_taken
    from src.modules.supplements.config import DEFAULT_SUPPLEMENTS, get_supplement_dosage
    d = date if date else datetime.today().strftime('%Y-%m-%d')

    # Find matching supplement (fuzzy)
    name_match = None
    for s in DEFAULT_SUPPLEMENTS:
        if supplement_name.lower() in s['name'].lower() or s['name'].lower() in supplement_name.lower():
            name_match = s
            break

    if not name_match:
        available = [s['name'] for s in DEFAULT_SUPPLEMENTS]
        return f"❌ '{supplement_name}' not found. Available: {available}"

    set_supplement_taken(d, name_match['name'], name_match['dosage'], name_match['unit'], taken)
    status = "✅ taken" if taken else "❌ not taken"
    return f"{status}: {name_match['name']} ({name_match['dosage']}{name_match['unit']}) on {d}"


@mcp.tool()
def log_all_supplements(taken: bool = True, date: str = "") -> str:
    """
    Mark all supplements as taken (or not taken) for a given day.
    Use when user says "took all my supplements" or "took my pills".

    Args:
        taken: True = all taken, False = none taken
        date: YYYY-MM-DD, defaults to today
    """
    from src.modules.supplements.data import set_supplement_taken
    from src.modules.supplements.config import DEFAULT_SUPPLEMENTS
    d = date if date else datetime.today().strftime('%Y-%m-%d')
    for s in DEFAULT_SUPPLEMENTS:
        set_supplement_taken(d, s['name'], s['dosage'], s['unit'], taken)
    status = "✅ All supplements marked as taken" if taken else "❌ All supplements marked as not taken"
    return f"{status} for {d}"


@mcp.tool()
def get_supplement_status(date: str = "") -> str:
    """
    Get supplement status for a given day.

    Args:
        date: YYYY-MM-DD, defaults to today
    """
    from src.modules.supplements.data import get_supplements_for_date
    from src.modules.supplements.config import DEFAULT_SUPPLEMENTS
    d = date if date else datetime.today().strftime('%Y-%m-%d')
    df = get_supplements_for_date(d)

    taken_names = set()
    if not df.empty:
        taken_names = set(df[df['taken'] == True]['supplement_name'].tolist()) | \
                      set(df[df['taken'] == 1]['supplement_name'].tolist())

    lines = [f"💊 Supplements for {d}:"]
    for s in DEFAULT_SUPPLEMENTS:
        icon = "✅" if s['name'] in taken_names else "⬜"
        lines.append(f"  {icon} {s['name']} ({s['dosage']}{s['unit']})")

    total = len(DEFAULT_SUPPLEMENTS)
    done = len(taken_names)
    lines.append(f"\n{done}/{total} taken")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# DAILY OVERVIEW
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def get_daily_overview(date: str = "") -> str:
    """
    Get a full overview of today's activity across all modules.
    Great for a morning check-in or evening recap.

    Args:
        date: YYYY-MM-DD, defaults to today
    """
    from src.modules.exercises.data import get_exercises
    from src.modules.learning.data import get_sessions, get_study_streak
    from src.modules.supplements.data import get_supplements_for_date
    from src.modules.supplements.config import DEFAULT_SUPPLEMENTS

    d = date if date else datetime.today().strftime('%Y-%m-%d')
    lines = [f"📊 Daily Overview — {d}\n{'─'*36}"]

    # Supplements
    supp_df = get_supplements_for_date(d)
    taken_names = set()
    if not supp_df.empty:
        taken_names = set(supp_df[supp_df['taken'] == True]['supplement_name'].tolist()) | \
                      set(supp_df[supp_df['taken'] == 1]['supplement_name'].tolist())
    total_s = len(DEFAULT_SUPPLEMENTS)
    done_s = len(taken_names)
    lines.append(f"💊 Supplements: {done_s}/{total_s} taken")

    # Exercise
    ex_df = get_exercises(days=1)
    if not ex_df.empty:
        today_ex = ex_df[ex_df['date'].astype(str).str[:10] == d]
        if not today_ex.empty:
            types = ", ".join(today_ex['workout_type'].tolist())
            lines.append(f"🏋️ Workout: {types}")
        else:
            lines.append("🏋️ Workout: none logged")
    else:
        lines.append("🏋️ Workout: none logged")

    # Learning
    streak = get_study_streak()
    sessions_today = get_sessions(days=1)
    if not sessions_today.empty:
        today_sess = sessions_today[sessions_today['date'].astype(str).str[:10] == d]
        if not today_sess.empty:
            total_min = int(today_sess['duration'].sum())
            lines.append(f"📚 Study: {len(today_sess)} session(s), {total_min} min")
        else:
            lines.append("📚 Study: none logged")
    else:
        lines.append("📚 Study: none logged")

    lines.append(f"🔥 Study streak: {streak} days")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Life Dashboard MCP Server", file=sys.stderr)
    print("Tools: log_workout, log_study_session, log_supplement, log_all_supplements,", file=sys.stderr)
    print("       add_word, lookup_and_add_word, get_daily_overview, and more", file=sys.stderr)
    mcp.run(transport="stdio")
