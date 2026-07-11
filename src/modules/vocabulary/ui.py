"""
Vocabulary UI components – suggestion, review, list views.
"""

import streamlit as st
import pandas as pd
import streamlit_card
from streamlit_card import card
from datetime import datetime
from .data import (
    add_vocabulary,
    get_all_vocabulary,
    get_words_due_for_review,
    update_review,
    delete_vocabulary,
    get_stats,
    word_exists
)
from .api import VocabularyAPI
from .config import get_cefr_level, get_word_count_by_level
from .images import ImageAPI

def render_vocabulary_tracker():
    """Main vocabulary tracker interface."""
    st.title("📚 Vocabulary Tracker")
    st.caption("Learn and track C1-C2 English words")
    
    # Initialize API
    api = VocabularyAPI()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Learn New Words",
        "📖 My Vocabulary",
        "🔄 Daily Review",
        "📊 Stats"
    ])
    
    with tab1:
        render_suggestion_tab(api)
    
    with tab2:
        render_vocabulary_list()
    
    with tab3:
        render_review_tab()
    
    with tab4:
        render_stats_tab()

def render_suggestion_tab(api):
    """Render the word suggestion tab."""
    st.subheader("🎯 Discover New Words")
    
    # Show word count info
    counts = get_word_count_by_level()
    st.caption(f"📚 Available words: {counts['C1']} C1 + {counts['C2']} C2 = {counts['C1'] + counts['C2']} total")
    
    # Initialize session state for suggestion
    if 'current_suggestion' not in st.session_state:
        st.session_state.current_suggestion = None
    
    # Get a new suggestion if none exists
    if st.session_state.current_suggestion is None:
        with st.spinner("Finding a new word..."):
            suggestion = api.get_random_suggestion()
            if suggestion and suggestion.get('found'):
                st.session_state.current_suggestion = suggestion
    
    # Buttons row
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 New Word", type="primary", use_container_width=True):
            with st.spinner("Finding a new word..."):
                suggestion = api.get_random_suggestion()
                if suggestion and suggestion.get('found'):
                    st.session_state.current_suggestion = suggestion
                    st.rerun()
                else:
                    st.warning("Could not fetch a new word. Please try again.")
    
    with col2:
        if st.button("📚 Add Own", use_container_width=True):
            st.session_state.show_add_own = not st.session_state.get('show_add_own', False)
            st.rerun()
    
    # Manual add own word
    if st.session_state.get('show_add_own', False):
        render_add_own_form()
    
    # Display current suggestion as a card
    if st.session_state.current_suggestion:
        render_word_card(st.session_state.current_suggestion)
    else:
        st.info("Click 'New Word' to discover C1-C2 vocabulary!")

def render_add_own_form():
    """Render the add own word form with translation."""
    with st.container():
        st.markdown("---")
        st.subheader("✏️ Add Your Own Word")
        
        col1, col2 = st.columns(2)
        with col1:
            own_word = st.text_input("Word", placeholder="Enter a word...")
            own_level = st.selectbox("CEFR Level", ["B2", "C1", "C2", "Unknown"])
        with col2:
            own_translation = st.text_input("Russian Translation (optional)", placeholder="e.g., глубокий")
            own_definition = st.text_area("Definition", placeholder="Enter the definition...")
            own_example = st.text_area("Example (optional)", placeholder="Enter an example sentence...")
        
        # Auto-translate button
        if own_word and not own_translation:
            if st.button("🔄 Auto-translate to Russian", use_container_width=True):
                from .translation import TranslationService
                translator = TranslationService()
                with st.spinner("Translating..."):
                    translation = translator.translate_to_russian(own_word)
                    if translation:
                        st.session_state.auto_translation = translation
                        st.rerun()
                    else:
                        st.warning("Could not auto-translate. Please enter manually.")
        
        # Show auto-translation if available
        if st.session_state.get('auto_translation'):
            st.info(f"💡 Translation: {st.session_state.auto_translation}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Use this translation", use_container_width=True):
                    st.session_state.manual_translation = st.session_state.auto_translation
                    st.session_state.auto_translation = None
                    st.rerun()
            with col2:
                if st.button("❌ Try again", use_container_width=True):
                    st.session_state.auto_translation = None
                    st.rerun()
        
        # Use manual translation if set
        translation_value = st.session_state.get('manual_translation', own_translation)
        
        if st.button("💾 Add to Vocabulary", type="primary"):
            if own_word and own_definition:
                word = own_word.lower().strip()
                if word_exists(word):
                    st.warning(f"'{word}' is already in your vocabulary!")
                else:
                    level = own_level if own_level != "Unknown" else None
                    if add_vocabulary(
                        word=word,
                        cefr_level=level,
                        definition=own_definition,
                        example=own_example,
                        translation=translation_value if translation_value else None,
                        importance=3,
                        category="manual",
                        mastery=3
                    ):
                        st.success(f"✅ Added '{word}' to your vocabulary!")
                        st.session_state.show_add_own = False
                        st.session_state.auto_translation = None
                        st.session_state.manual_translation = None
                        st.rerun()
                    else:
                        st.error("Failed to add word.")
            else:
                st.error("Please enter a word and definition.")
        st.markdown("---")

def render_word_card(word_data):
    """Render a word card using pure Streamlit components."""

    word_display = word_data.get('word', '').title()
    word_key = word_data.get('word', '').lower()
    level = word_data.get('cefr_level')
    definition = word_data.get('definition', 'No definition available')
    example = word_data.get('example', '')
    part_of_speech = word_data.get('part_of_speech', '')
    audio_url = word_data.get('audio_url', '')
    phonetic = word_data.get('phonetic', '')
    translation = word_data.get('translation', '')

    # --- Get image ---
    image_api = ImageAPI()
    image_data = image_api.get_image_url(word_display)

    # --- Build image HTML (single-line to avoid Streamlit code block detection) ---
    if image_data.get("url"):
        photographer = image_data.get('photographer', 'Unknown')
        photographer_url = image_data.get('photographer_url', '#')
        image_html = (
            f'<div class="word-image">'
            f'<img src="{image_data["url"]}" alt="Image of {word_display}">'
            f'<div class="credit">📷 Photo by <a href="{photographer_url}" target="_blank">{photographer}</a> on Pexels</div>'
            f'</div>'
        )
    elif image_data.get("emoji"):
        image_html = f'<div class="word-emoji">{image_data["emoji"]}</div>'
    else:
        image_html = ''

    # --- Build optional fields HTML ---
    level_badge = f'<span class="word-level">{level}</span>' if level else '<span class="word-level" style="color:#94a3b8;">? Level</span>'
    translation_html = f'<div class="word-translation"> {translation}</div>' if translation else ''
    pos_html = f'<div class="word-pos">📖 {part_of_speech}</div>' if part_of_speech else ''
    example_html = f'<div class="word-example">💬 &ldquo;{example}&rdquo;</div>' if example else ''
    phonetic_html = f'<div class="word-phonetic">🔊 {phonetic}</div>' if phonetic else ''

    # --- Inject styles once (separate call avoids markdown processing issues) ---
    st.markdown("""<style>
.word-card-container {background: linear-gradient(145deg, #1e293b, #172032); border: 1px solid #2a3a4b; border-radius: 16px; padding: 24px; margin: 16px 0; box-shadow: 0 8px 24px rgba(0,0,0,0.4); transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;}
.word-card-container:hover {border-color: #4ade80; transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0,0,0,0.5);}
.word-header {display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;}
.word-title {font-size: 28px; font-weight: 700; color: #f8fafc;}
.word-level {background: #2a3a4b; color: #4ade80; padding: 2px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block;}
.word-translation {color: #a78bfa; font-size: 18px; margin: 6px 0;}
.word-pos {color: #94a3b8; font-size: 13px; margin: 4px 0;}
.word-definition {color: #e2e8f0; font-size: 15px; line-height: 1.6; margin: 10px 0; padding: 10px 14px; background: #0f172a; border-radius: 8px; border-left: 3px solid #4ade80;}
.word-example {background: #0f172a; padding: 10px 14px; border-radius: 8px; margin: 10px 0; color: #94a3b8; font-size: 14px; font-style: italic; border-left: 2px solid #4ade80;}
.word-phonetic {color: #64748b; font-size: 13px; margin-top: 8px;}
.word-image {text-align: center; margin-bottom: 16px;}
.word-image img {max-width: 100%; max-height: 250px; border-radius: 12px; border: 1px solid #2a3a4b; object-fit: cover;}
.word-image .credit {color: #64748b; font-size: 11px; margin-top: 4px;}
.word-image .credit a {color: #4ade80; text-decoration: none;}
.word-emoji {text-align: center; font-size: 80px; padding: 16px; background: #0f172a; border-radius: 12px; border: 1px solid #2a3a4b; margin-bottom: 16px;}
</style>""", unsafe_allow_html=True)

    # --- Render card HTML (no f-string braces in CSS, no indentation issues) ---
    card_html = (
        '<div class="word-card-container">'
        + image_html
        + '<div class="word-header">'
        + f'<span class="word-title">{word_display}</span>'
        + level_badge
        + '</div>'
        + translation_html
        + pos_html
        + f'<div class="word-definition">📖 {definition}</div>'
        + example_html
        + phonetic_html
        + '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # --- Audio (Streamlit widget, must live outside HTML) ---
    if audio_url:
        st.audio(audio_url, format="audio/mpeg")

    # --- Buttons ---
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📚 Learn This Word", type="primary", use_container_width=True):
            if word_exists(word_key):
                st.warning(f"'{word_key}' is already in your vocabulary!")
            else:
                translation_text = translation if translation else None
                if add_vocabulary(
                    word=word_key,
                    cefr_level=level,
                    definition=word_data.get('definition', ''),
                    example=word_data.get('example', ''),
                    translation=translation_text,
                    importance=4 if level in ['C1', 'C2'] else 3,
                    category="suggested",
                    mastery=4
                ):
                    st.success(f"✅ Added '{word_key}' to your vocabulary!")
                    st.session_state.current_suggestion = None
                    st.rerun()
                else:
                    st.error("Failed to add word.")

    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            st.session_state.current_suggestion = None
            st.rerun()

def render_vocabulary_list():
    """Render the vocabulary list with filters and actions."""
    st.subheader("📖 My Vocabulary")
    
    df = get_all_vocabulary()
    if df.empty:
        st.info("You haven't added any words yet. Go to 'Learn New Words' tab to start!")
        return
    
    # --- Stats Summary ---
    total = len(df)
    c1_count = len(df[df['cefr_level'] == 'C1']) if 'cefr_level' in df.columns else 0
    c2_count = len(df[df['cefr_level'] == 'C2']) if 'cefr_level' in df.columns else 0
    b2_count = len(df[df['cefr_level'] == 'B2']) if 'cefr_level' in df.columns else 0
    unknown_count = total - c1_count - c2_count - b2_count
    
    avg_mastery = df['mastery'].mean() if 'mastery' in df.columns else 0
    
    # Due for review
    due_words = get_words_due_for_review()
    due_count = len(due_words)
    
    # Stats row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📚 Total", total)
    with col2:
        st.metric("🟢 C1", c1_count)
    with col3:
        st.metric("🔵 C2", c2_count)
    with col4:
        st.metric("⭐ Mastery", f"{avg_mastery:.1f}/5")
    with col5:
        st.metric("🔄 Due", due_count, delta=None)
    
    st.divider()
    
    # --- Filters ---
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search words", placeholder="Type a word...")
    
    with col2:
        level_filter = st.selectbox("Level", ["All", "B2", "C1", "C2", "Unknown"])
    
    with col3:
        mastery_filter = st.selectbox("Mastery", ["All", "1", "2", "3", "4", "5"])
    
    # --- Apply filters ---
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['word'].str.contains(search_term, case=False)]
    
    if level_filter != "All":
        filtered_df = filtered_df[filtered_df['cefr_level'] == level_filter]
    
    if mastery_filter != "All":
        filtered_df = filtered_df[filtered_df['mastery'] == int(mastery_filter)]
    
    # --- Display filtered results ---
    if filtered_df.empty:
        st.info("No words match your filters.")
        return
    
    st.caption(f"Showing {len(filtered_df)} of {total} words")
    
    # --- Sort options ---
    sort_options = ["Word (A-Z)", "Word (Z-A)", "Newest", "Oldest", "Mastery (Low-High)", "Mastery (High-Low)"]
    sort_by = st.selectbox("Sort by", sort_options, index=0)
    
    if sort_by == "Word (A-Z)":
        filtered_df = filtered_df.sort_values('word')
    elif sort_by == "Word (Z-A)":
        filtered_df = filtered_df.sort_values('word', ascending=False)
    elif sort_by == "Newest":
        filtered_df = filtered_df.sort_values('date_added', ascending=False)
    elif sort_by == "Oldest":
        filtered_df = filtered_df.sort_values('date_added')
    elif sort_by == "Mastery (Low-High)":
        filtered_df = filtered_df.sort_values('mastery')
    elif sort_by == "Mastery (High-Low)":
        filtered_df = filtered_df.sort_values('mastery', ascending=False)
    
    # --- Display as cards ---
    st.divider()
    
    # Show words as cards (3 per row)
    cols_per_row = 3
    rows = [filtered_df.iloc[i:i+cols_per_row] for i in range(0, len(filtered_df), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, (_, word) in enumerate(row.iterrows()):
            with cols[idx]:
                render_vocabulary_card(word)
    
    # --- Pagination (if too many words) ---
    if len(filtered_df) > 30:
        st.caption(f"Showing {len(filtered_df)} words. Use filters to narrow down.")

def render_vocabulary_card(word):
    """Render a small card for a vocabulary word with translation."""
    
    level_colors = {
        "C2": "#4ade80",
        "C1": "#60a5fa",
        "B2": "#fbbf24",
        None: "#94a3b8",
    }
    level_color = level_colors.get(word.get('cefr_level'), "#94a3b8")
    
    mastery = word.get('mastery', 0)
    stars = "⭐" * mastery + "☆" * (5 - mastery) if mastery else "☆☆☆☆☆"
    
    translation = word.get('translation', '')
    translation_html = f'<div style="color: #a78bfa; font-size: 14px;">🇷🇺 {translation}</div>' if translation else ''
    
    st.markdown(f"""
    <div style="
        background: #1e293b;
        border: 1px solid #2a3a4b;
        border-radius: 12px;
        padding: 16px;
        margin: 4px 0;
        transition: all 0.2s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; font-weight: 600; color: #f8fafc;">{word['word']}</span>
            <span style="background: {level_color}; color: #0f172a; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                {word.get('cefr_level', '?')}
            </span>
        </div>
        {translation_html}
        <div style="color: #94a3b8; font-size: 13px; margin: 4px 0;">
            {word.get('definition', 'No definition')[:80]}{'...' if len(word.get('definition', '')) > 80 else ''}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
            <span style="color: #64748b; font-size: 12px;">{stars}</span>
            <span style="color: #64748b; font-size: 11px;">{word.get('last_reviewed', 'Never')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔊", key=f"audio_{word['word']}", help="Listen"):
            # Will implement audio player here later
            pass
    with col2:
        if st.button("🔄", key=f"review_{word['word']}", help="Review now"):
            st.session_state.current_review_word = word['word']
            st.rerun()
    with col3:
        if st.button("🗑️", key=f"delete_{word['word']}", help="Delete"):
            if delete_vocabulary(word['word']):
                st.success(f"Deleted '{word['word']}'")
                st.rerun()

def render_review_tab():
    """Render the daily review tab."""
    st.subheader("🔄 Daily Review")
    
    due_words = get_words_due_for_review()
    
    if due_words.empty:
        st.success("🎉 No words due for review today! Great job!")
        return
    
    st.info(f"📚 You have {len(due_words)} word(s) due for review today.")
    
    # Initialize review state
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0
    
    if 'review_words' not in st.session_state:
        st.session_state.review_words = due_words.to_dict('records')
    
    if st.session_state.review_index >= len(st.session_state.review_words):
        st.session_state.review_index = 0
        st.session_state.review_words = due_words.to_dict('records')
    
    # Show current word
    if st.session_state.review_words:
        word_data = st.session_state.review_words[st.session_state.review_index]
        
        st.markdown("---")
        st.markdown(f"### Word: **{word_data['word']}**")
        st.markdown(f"**Definition:** {word_data.get('definition', 'No definition')}")
        st.markdown(f"**Example:** *{word_data.get('example_sentence', 'No example')}*")
        st.markdown(f"**Level:** {word_data.get('cefr_level', 'Unknown')}")
        
        # Mastery rating
        st.markdown("---")
        st.caption("How well do you know this word?")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("1️⃣", use_container_width=True):
                update_review(word_data['word'], 1)
                st.session_state.review_index += 1
                st.rerun()
            st.caption("Mastered")
        
        with col2:
            if st.button("2️⃣", use_container_width=True):
                update_review(word_data['word'], 2)
                st.session_state.review_index += 1
                st.rerun()
            st.caption("Good")
        
        with col3:
            if st.button("3️⃣", use_container_width=True):
                update_review(word_data['word'], 3)
                st.session_state.review_index += 1
                st.rerun()
            st.caption("Okay")
        
        with col4:
            if st.button("4️⃣", use_container_width=True):
                update_review(word_data['word'], 4)
                st.session_state.review_index += 1
                st.rerun()
            st.caption("Struggling")
        
        with col5:
            if st.button("5️⃣", use_container_width=True):
                update_review(word_data['word'], 5)
                st.session_state.review_index += 1
                st.rerun()
            st.caption("New")
        
        st.progress(
            st.session_state.review_index / len(st.session_state.review_words),
            text=f"Progress: {st.session_state.review_index + 1}/{len(st.session_state.review_words)}"
        )
        
        if st.button("🔄 Reset Review Session"):
            st.session_state.review_index = 0
            st.session_state.review_words = due_words.to_dict('records')
            st.rerun()

def render_stats_tab():
    """Render vocabulary statistics."""
    st.subheader("📊 Vocabulary Statistics")
    
    stats = get_stats()
    counts = get_word_count_by_level()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Words", stats['total'])
    with col2:
        st.metric("🔄 Due for Review", stats['due'])
    with col3:
        st.metric("⭐ Avg Mastery", f"{stats['avg_mastery']}/5")
    with col4:
        st.metric("📊 Available Words", counts['C1'] + counts['C2'])
    
    # Level breakdown
    if stats['by_level']:
        st.subheader("📊 Words by CEFR Level")
        level_data = pd.DataFrame({
            'Level': list(stats['by_level'].keys()),
            'Count': list(stats['by_level'].values())
        })
        st.bar_chart(level_data.set_index('Level'))
    
    # Show all words with stats
    df = get_all_vocabulary()
    if not df.empty:
        st.subheader("📋 All Words")
        st.dataframe(
            df[['word', 'cefr_level', 'mastery', 'times_reviewed', 'next_review_date']],
            use_container_width=True,
            hide_index=True
        )