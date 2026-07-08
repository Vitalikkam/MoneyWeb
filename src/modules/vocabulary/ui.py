"""
Vocabulary UI components – suggestion, review, list views.
"""

import streamlit as st
import pandas as pd
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
    """Render the add own word form."""
    with st.container():
        st.markdown("---")
        st.subheader("✏️ Add Your Own Word")
        
        col1, col2 = st.columns(2)
        with col1:
            own_word = st.text_input("Word", placeholder="Enter a word...")
            own_level = st.selectbox("CEFR Level", ["B2", "C1", "C2", "Unknown"])
        with col2:
            own_definition = st.text_area("Definition", placeholder="Enter the definition...")
            own_example = st.text_area("Example (optional)", placeholder="Enter an example sentence...")
        
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
                        importance=3,
                        category="manual",
                        mastery=3
                    ):
                        st.success(f"✅ Added '{word}' to your vocabulary!")
                        st.session_state.show_add_own = False
                        st.rerun()
                    else:
                        st.error("Failed to add word.")
            else:
                st.error("Please enter a word and definition.")
        st.markdown("---")

def render_word_card(word_data):
    """Render a beautiful word suggestion card with audio and image."""
    
    # CSS for the card
    st.markdown("""
    <style>
    .word-card {
        background: linear-gradient(145deg, #1e293b, #172032);
        border: 1px solid #2a3a4b;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
    }
    .word-card:hover {
        border-color: #4ade80;
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.5);
    }
    .word-title {
        font-size: 32px;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .word-level {
        display: inline-block;
        background: #2a3a4b;
        color: #4ade80;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-left: 8px;
    }
    .word-level-unknown {
        background: #2a3a4b;
        color: #94a3b8;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-left: 8px;
    }
    .word-definition {
        color: #e2e8f0;
        font-size: 16px;
        line-height: 1.6;
        margin: 12px 0;
        padding: 12px 16px;
        background: #0f172a;
        border-radius: 8px;
        border-left: 3px solid #4ade80;
    }
    .word-example {
        color: #94a3b8;
        font-size: 14px;
        font-style: italic;
        padding: 8px 16px;
        background: #0f172a;
        border-radius: 8px;
        margin: 8px 0;
    }
    .word-pos {
        color: #64748b;
        font-size: 13px;
        margin: 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    word = word_data.get('word', '').title()
    level = word_data.get('cefr_level')
    definition = word_data.get('definition', 'No definition available')
    example = word_data.get('example', '')
    part_of_speech = word_data.get('part_of_speech', '')
    audio_url = word_data.get('audio_url', '')
    phonetic = word_data.get('phonetic', '')
    
    # --- GET IMAGE ---
    image_api = ImageAPI()
    image_data = image_api.get_image_url(word)
    
    # --- DISPLAY IMAGE WITH ST.IMAGE() ---
    if image_data.get("url"):
        st.image(image_data['url'], caption=f"📷 Photo by {image_data.get('photographer', 'Unknown')} on Pexels")
    elif image_data.get("emoji"):
        st.markdown(f"<div style='text-align:center;font-size:80px;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;'>{image_data['emoji']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:center;font-size:40px;padding:20px;background:#0f172a;border-radius:12px;border:1px solid #2a3a4b;color:#64748b;'>📚 No image available</div>", unsafe_allow_html=True)
    
    # --- BUILD THE CARD (without image) ---
    if level:
        level_html = f'<span class="word-level">{level}</span>'
    else:
        level_html = '<span class="word-level-unknown">Not in Oxford list</span>'
    
    pos_html = f'<div class="word-pos">📖 {part_of_speech}</div>' if part_of_speech else ''
    example_html = f'<div class="word-example">💬 "{example}"</div>' if example else ''
    
    card_html = f"""
    <div class="word-card">
        <div>
            <span class="word-title">{word}</span>
            {level_html}
        </div>
        {pos_html}
        <div class="word-definition">📖 {definition}</div>
        {example_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # --- AUDIO PLAYER ---
    if audio_url:
        st.markdown(f"<span style='color:#94a3b8;font-size:14px;'>🔊 {phonetic if phonetic else 'Listen'}</span>", unsafe_allow_html=True)
        st.audio(audio_url, format="audio/mpeg")
    elif phonetic:
        st.markdown(f"<span style='color:#94a3b8;font-size:14px;'>🔊 {phonetic} <span style='color:#64748b;font-size:12px;'>(Audio not available)</span></span>", unsafe_allow_html=True)
    
    # Buttons below the card
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📚 Learn This Word", type="primary", use_container_width=True):
            word = word_data.get('word', '').lower()
            if word_exists(word):
                st.warning(f"'{word}' is already in your vocabulary!")
            else:
                level = word_data.get('cefr_level')
                if add_vocabulary(
                    word=word,
                    cefr_level=level,
                    definition=word_data.get('definition', ''),
                    example=word_data.get('example', ''),
                    importance=4 if level in ['C1', 'C2'] else 3,
                    category="suggested",
                    mastery=4
                ):
                    st.success(f"✅ Added '{word}' to your vocabulary!")
                    st.session_state.current_suggestion = None
                    st.rerun()
                else:
                    st.error("Failed to add word.")
    
    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            st.session_state.current_suggestion = None
            st.rerun()

def render_vocabulary_list():
    """Render the vocabulary list."""
    st.subheader("📖 My Vocabulary")
    
    df = get_all_vocabulary()
    if df.empty:
        st.info("You haven't added any words yet. Go to 'Learn New Words' tab to start!")
        return
    
    # Show stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Words", len(df))
    with col2:
        if 'cefr_level' in df.columns:
            levels = df['cefr_level'].value_counts()
            most_common = levels.index[0] if not levels.empty else "N/A"
            st.metric("Most Common Level", most_common)
    with col3:
        avg_mastery = df['mastery'].mean() if 'mastery' in df.columns else 0
        st.metric("Average Mastery", f"{avg_mastery:.1f}/5")
    
    # Display table
    st.dataframe(
        df[['word', 'cefr_level', 'definition', 'category', 'mastery', 'importance']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "word": "Word",
            "cefr_level": "Level",
            "definition": "Definition",
            "category": "Category",
            "mastery": st.column_config.NumberColumn("Mastery", format="%.0f/5"),
            "importance": st.column_config.NumberColumn("Importance", format="%.0f/5")
        }
    )
    
    # Delete option
    st.subheader("🗑️ Delete Word")
    words_to_delete = df['word'].tolist()
    word_to_delete = st.selectbox("Select word to delete:", words_to_delete)
    if st.button("Delete", type="secondary"):
        if delete_vocabulary(word_to_delete):
            st.success(f"Deleted '{word_to_delete}'")
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