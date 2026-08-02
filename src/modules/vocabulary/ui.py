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
from .translation import TranslationService

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

    # Only auto-fetch once per session — not on every tab revisit
    if 'suggestion_loaded' not in st.session_state:
        st.session_state.suggestion_loaded = False
        st.session_state.current_suggestion = None

    if not st.session_state.suggestion_loaded and st.session_state.current_suggestion is None:
        with st.spinner("Finding a new word..."):
            suggestion = api.get_random_suggestion()
            if suggestion and suggestion.get('found'):
                st.session_state.current_suggestion = suggestion
                st.session_state.suggestion_loaded = True

    # Buttons row
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 New Word", type="primary", use_container_width=True):
            with st.spinner("Finding a new word..."):
                suggestion = api.get_random_suggestion()
                if suggestion and suggestion.get('found'):
                    st.session_state.current_suggestion = suggestion
                    st.session_state.suggestion_loaded = True
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
        st.info("Click '🔄 New Word' to discover C1-C2 vocabulary!")

def render_add_own_form():
    """Render the add own word form with fetch-first flow."""

    # Session state keys used by this form
    OWN_FETCHED  = 'add_own_fetched'   # dict of fetched word data
    OWN_WORD_KEY = 'add_own_last_word' # word that was last fetched

    st.markdown("---")
    st.subheader("✏️ Add Your Own Word")

    # --- Word input + Fetch button ---
    col_word, col_btn = st.columns([3, 1])
    with col_word:
        own_word = st.text_input("Word", placeholder="Enter a word...", key="add_own_word_input")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)  # align button with input
        fetch_clicked = st.button("🔍 Fetch", use_container_width=True, key="add_own_fetch_btn")

    # --- Fetch from API when button clicked ---
    if fetch_clicked:
        if own_word.strip():
            # Clear stale fetched data if word changed
            st.session_state[OWN_FETCHED] = None
            st.session_state[OWN_WORD_KEY] = None
            with st.spinner(f"Fetching data for '{own_word.strip()}'..."):
                api = VocabularyAPI()
                data = api.get_word_data(own_word.strip().lower())
                # Translation is already inside data from VocabularyAPI
                st.session_state[OWN_FETCHED] = data
                st.session_state[OWN_WORD_KEY] = own_word.strip().lower()
            st.rerun()
        else:
            st.warning("Enter a word first.")

    # --- Pre-fill fields from fetched data if word matches ---
    fetched = st.session_state.get(OWN_FETCHED)
    last_word = st.session_state.get(OWN_WORD_KEY, '')
    word_changed = own_word.strip().lower() != last_word

    if fetched and not word_changed:
        # Show fetch success notice
        if fetched.get('found'):
            st.success("✅ Found in dictionary — fields pre-filled. Edit anything before saving.")
        else:
            st.warning("⚠️ Word not found in dictionary — CEFR level and definition filled where available. Complete manually.")

        prefill_phonetic = fetched.get('phonetic', '')

        # Write fetched values directly into widget session state so Streamlit picks them up
        st.session_state['add_own_definition']  = fetched.get('definition', '')
        st.session_state['add_own_example']     = fetched.get('example', '')
        st.session_state['add_own_translation'] = fetched.get('translation', '')

        # Infer CEFR index for selectbox
        level_options = ["B2", "C1", "C2", "Unknown"]
        fetched_level = fetched.get('cefr_level')
        level_index = level_options.index(fetched_level) if fetched_level in level_options else 3

        # Clear fetched data so we don't overwrite user edits on next rerun
        st.session_state[OWN_FETCHED] = None
    else:
        prefill_phonetic = ''
        level_index      = 3  # default Unknown

    # --- Editable fields (pre-filled when fetched) ---
    col_left, col_right = st.columns(2)
    with col_left:
        own_level = st.selectbox(
            "CEFR Level", ["B2", "C1", "C2", "Unknown"],
            index=level_index, key="add_own_level"
        )
        own_translation = st.text_input(
            "Russian Translation",
            placeholder="e.g., глубокий",
            key="add_own_translation"
        )
        if prefill_phonetic:
            st.caption(f"🔊 {prefill_phonetic}")

    with col_right:
        own_definition = st.text_area(
            "Definition",
            placeholder="Enter or fetch the definition...",
            key="add_own_definition"
        )
        own_example = st.text_area(
            "Example (optional)",
            placeholder="Enter or fetch an example sentence...",
            key="add_own_example"
        )

    # --- Save button ---
    if st.button("💾 Add to Vocabulary", type="primary", key="add_own_save_btn"):
        word = own_word.strip().lower()
        if not word or not own_definition.strip():
            st.error("Word and definition are required.")
        elif word_exists(word):
            st.warning(f"'{word}' is already in your vocabulary!")
        else:
            level = own_level if own_level != "Unknown" else None
            if add_vocabulary(
                word=word,
                cefr_level=level,
                definition=own_definition.strip(),
                example=own_example.strip(),
                translation=own_translation.strip() if own_translation.strip() else None,
                importance=3,
                category="manual",
                mastery=3
            ):
                st.success(f"✅ Added '{word}' to your vocabulary!")
                # Clean up all form state
                for key in [OWN_FETCHED, OWN_WORD_KEY, 'show_add_own']:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("Failed to add word.")

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

    # --- Level-based accent color ---
    level_colors = {"C2": "#4ade80", "C1": "#60a5fa", "B2": "#fbbf24"}
    accent = level_colors.get(level, "#94a3b8")

    # --- Build image section: full-width hero using <img> (background-image gets stripped by Streamlit Cloud CSP) ---
    if image_data.get("url"):
        photographer = image_data.get('photographer', 'Unknown')
        photographer_url = image_data.get('photographer_url', '#')
        image_section = (
            f'<div class="wc-hero">'
            f'<img src="{image_data["url"]}" alt="Image of {word_display}" style="width:100%;height:320px;object-fit:cover;object-position:center;display:block;">'
            f'<div class="wc-hero-overlay" style="background:linear-gradient(to bottom, rgba(15,23,42,0.2) 0%, rgba(15,23,42,0.92) 100%);">'
            f'<div class="wc-hero-content">'
            f'<div class="wc-title-row">'
            f'<span class="wc-title">{word_display}</span>'
            f'<span class="wc-badge" style="background:{accent}22;color:{accent};border:1px solid {accent}55;">{level or "?"}</span>'
            f'</div>'
            f'{"<span class=wc-phonetic>" + phonetic + "</span>" if phonetic else ""}'
            f'{"<span class=wc-translation>" + translation + "</span>" if translation else ""}'
            f'</div>'
            f'<div class="wc-credit">📷 <a href="{photographer_url}" target="_blank">{photographer}</a> · Pexels</div>'
            f'</div></div>'
        )
    elif image_data.get("emoji"):
        image_section = (
            f'<div class="wc-emoji-hero" style="border-bottom:1px solid {accent}33;">'
            f'<div style="font-size:72px;line-height:1;">{image_data["emoji"]}</div>'
            f'<div class="wc-title-row" style="margin-top:12px;">'
            f'<span class="wc-title" style="color:#f8fafc;">{word_display}</span>'
            f'<span class="wc-badge" style="background:{accent}22;color:{accent};border:1px solid {accent}55;">{level or "?"}</span>'
            f'</div>'
            f'{"<span class=wc-phonetic style=color:#94a3b8>" + phonetic + "</span>" if phonetic else ""}'
            f'{"<span class=wc-translation>" + translation + "</span>" if translation else ""}'
            f'</div>'
        )
    else:
        image_section = (
            f'<div class="wc-title-row" style="margin-bottom:8px;">'
            f'<span class="wc-title" style="color:#f8fafc;">{word_display}</span>'
            f'<span class="wc-badge" style="background:{accent}22;color:{accent};border:1px solid {accent}55;">{level or "?"}</span>'
            f'</div>'
            f'{"<span class=wc-phonetic>" + phonetic + "</span>" if phonetic else ""}'
            f'{"<span class=wc-translation>" + translation + "</span>" if translation else ""}'
        )

    pos_html      = f'<span class="wc-pos">{part_of_speech}</span>' if part_of_speech else ''
    example_html  = f'<div class="wc-example">❝ {example} ❞</div>' if example else ''

    # --- Styles ---
    st.markdown(f"""<style>
.wc-card {{background:rgba(15,23,42,0.7);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid {accent}44;border-radius:20px;overflow:hidden;box-shadow:0 0 32px {accent}22, 0 8px 32px rgba(0,0,0,0.5);transition:box-shadow 0.3s,transform 0.3s;margin:16px 0;}}
.wc-card:hover {{box-shadow:0 0 48px {accent}44, 0 12px 40px rgba(0,0,0,0.6);transform:translateY(-3px);}}
.wc-hero {{width:100%;position:relative;overflow:hidden;}}
.wc-hero-overlay {{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:20px;}}
.wc-hero-content {{display:flex;flex-direction:column;gap:4px;}}
.wc-emoji-hero {{padding:28px 24px 20px;text-align:center;background:linear-gradient(145deg,#1e293b,#0f172a);}}
.wc-title-row {{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}}
.wc-title {{font-size:32px;font-weight:800;color:#f8fafc;letter-spacing:-0.5px;text-shadow:0 2px 8px rgba(0,0,0,0.8);}}
.wc-badge {{font-size:12px;font-weight:700;padding:3px 12px;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;}}
.wc-phonetic {{color:#94a3b8;font-size:14px;font-style:italic;}}
.wc-translation {{color:#c4b5fd;font-size:16px;font-weight:500;}}
.wc-body {{padding:20px 24px 24px;}}
.wc-pos {{display:inline-block;color:{accent};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;}}
.wc-definition {{color:#e2e8f0;font-size:15px;line-height:1.7;padding:14px 16px;background:rgba(255,255,255,0.04);border-radius:10px;border-left:3px solid {accent};margin-bottom:12px;}}
.wc-example {{color:#94a3b8;font-size:14px;font-style:italic;line-height:1.6;padding:12px 16px;background:rgba(255,255,255,0.03);border-radius:10px;border-left:2px solid {accent}88;}}
.wc-credit {{font-size:10px;color:#475569;text-align:right;}} .wc-credit a {{color:{accent}99;text-decoration:none;}}
.wc-buttons div[data-testid="stHorizontalBlock"] {{gap:12px;}}
.wc-buttons button[kind="primary"] {{background:linear-gradient(135deg,{accent},{accent}cc) !important;border:none !important;color:#0f172a !important;font-weight:700 !important;font-size:15px !important;border-radius:12px !important;padding:12px 0 !important;box-shadow:0 4px 16px {accent}44 !important;transition:all 0.2s !important;}}
.wc-buttons button[kind="primary"]:hover {{transform:translateY(-1px) !important;box-shadow:0 6px 20px {accent}66 !important;}}
.wc-buttons button[kind="secondary"] {{background:rgba(255,255,255,0.06) !important;border:1px solid rgba(255,255,255,0.12) !important;color:#94a3b8 !important;font-weight:600 !important;font-size:15px !important;border-radius:12px !important;padding:12px 0 !important;transition:all 0.2s !important;}}
.wc-buttons button[kind="secondary"]:hover {{background:rgba(255,255,255,0.1) !important;color:#f8fafc !important;border-color:rgba(255,255,255,0.2) !important;}}
</style>""", unsafe_allow_html=True)

    # --- Render card ---
    card_html = (
        '<div class="wc-card">'
        + image_section
        + '<div class="wc-body">'
        + pos_html
        + f'<div class="wc-definition">{definition}</div>'
        + example_html
        + '</div>'
        + '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # --- Audio (Streamlit widget, must live outside HTML) ---
    if audio_url:
        # Normalize protocol-relative URLs (e.g. //ssl.gstatic.com/... -> https://...)
        if audio_url.startswith("//"):
            audio_url = "https:" + audio_url
        print(f"🔊 Audio URL: {audio_url}")
        st.audio(audio_url, format="audio/mpeg")

    # --- Styled action buttons ---
    st.markdown('<div class="wc-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("＋ Add to Vocabulary", type="primary", use_container_width=True, key="wc_learn"):
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
                    st.success(f"✅ Added '{word_key}'!")
                    st.session_state.current_suggestion = None
                    st.session_state.suggestion_loaded = False
                    st.rerun()
                else:
                    st.error("Failed to add word.")
    with col2:
        if st.button("→ Next Word", use_container_width=True, key="wc_skip"):
            st.session_state.current_suggestion = None
            st.session_state.suggestion_loaded = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    # --- Display as cards with pagination ---
    st.divider()

    PAGE_SIZE = 12
    total_filtered = len(filtered_df)
    total_pages = max(1, -(-total_filtered // PAGE_SIZE))  # ceil division

    # Page selector
    if total_pages > 1:
        col_info, col_nav = st.columns([3, 2])
        with col_info:
            st.caption(f"Showing {total_filtered} words · Page {st.session_state.get('vocab_page', 1)} of {total_pages}")
        with col_nav:
            page = st.number_input(
                "Page", min_value=1, max_value=total_pages,
                value=st.session_state.get('vocab_page', 1),
                step=1, key="vocab_page_input", label_visibility="collapsed"
            )
            st.session_state.vocab_page = page
    else:
        page = 1
        st.caption(f"Showing {total_filtered} words")

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_df = filtered_df.iloc[start:end]

    # Show words as cards (3 per row)
    cols_per_row = 3
    rows = [page_df.iloc[i:i+cols_per_row] for i in range(0, len(page_df), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, (_, word) in enumerate(row.iterrows()):
            with cols[idx]:
                render_vocabulary_card(word)

    # Bottom page navigation
    if total_pages > 1:
        col_prev, col_mid, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("← Prev", disabled=(page <= 1), use_container_width=True, key="vocab_prev"):
                st.session_state.vocab_page = page - 1
                st.rerun()
        with col_mid:
            st.caption(f"Page {page} / {total_pages}", )
        with col_next:
            if st.button("Next →", disabled=(page >= total_pages), use_container_width=True, key="vocab_next"):
                st.session_state.vocab_page = page + 1
                st.rerun()

def _format_last_reviewed(date_str):
    """Format a date string as human-readable relative time."""
    if not date_str or date_str == 'Never':
        return 'Never reviewed'
    try:
        reviewed = datetime.strptime(str(date_str)[:10], '%Y-%m-%d')
        delta = (datetime.today() - reviewed).days
        if delta == 0:
            return 'Today'
        elif delta == 1:
            return 'Yesterday'
        elif delta < 7:
            return f'{delta} days ago'
        elif delta < 30:
            weeks = delta // 7
            return f'{weeks} week{"s" if weeks > 1 else ""} ago'
        else:
            return reviewed.strftime('%b %d, %Y')
    except Exception:
        return str(date_str)


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

    last_reviewed = _format_last_reviewed(word.get('last_reviewed'))

    st.markdown(
        f'<div style="background:#1e293b;border:1px solid #2a3a4b;border-radius:12px;padding:16px;margin:4px 0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="font-size:18px;font-weight:600;color:#f8fafc;">{word["word"]}</span>'
        f'<span style="background:{level_color};color:#0f172a;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">{word.get("cefr_level", "?")}</span>'
        f'</div>'
        f'{translation_html}'
        f'<div style="color:#94a3b8;font-size:13px;margin:4px 0;">{word.get("definition", "No definition")[:80]}{"..." if len(word.get("definition", "")) > 80 else ""}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">'
        f'<span style="color:#64748b;font-size:12px;">{stars}</span>'
        f'<span style="color:#64748b;font-size:11px;">{last_reviewed}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔊", key=f"audio_{word['word']}", help="Listen to pronunciation"):
            with st.spinner(""):
                api = VocabularyAPI()
                data = api.get_word_data(word['word'])
                audio_url = data.get('audio_url')
                if audio_url:
                    st.audio(audio_url, format="audio/mpeg")
                else:
                    st.caption("No audio available")
    with col2:
        if st.button("🔄", key=f"review_{word['word']}", help="Review now"):
            st.session_state.current_page = 'vocabulary'
            st.session_state.vocab_tab = 'review'
            st.session_state.review_word_focus = word['word']
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

    total_due = len(due_words)
    st.info(f"📚 You have {total_due} word(s) due for review today.")

    # Initialize review state
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0
    if 'review_words' not in st.session_state:
        st.session_state.review_words = due_words.to_dict('records')

    # Reset if we've gone past the end
    if st.session_state.review_index >= len(st.session_state.review_words):
        st.balloons()
        st.success("🎉 You've reviewed all due words! Great session.")
        if st.button("🔄 Start Over"):
            st.session_state.review_index = 0
            st.session_state.review_words = due_words.to_dict('records')
            st.rerun()
        return

    word_data = st.session_state.review_words[st.session_state.review_index]
    current = st.session_state.review_index + 1
    total = len(st.session_state.review_words)

    # Progress bar — current/total, no off-by-one
    st.progress(current / total, text=f"Word {current} of {total}")

    st.markdown("---")

    # Word card
    col_word, col_meta = st.columns([3, 1])
    with col_word:
        st.markdown(f"## {word_data['word']}")
        if word_data.get('translation'):
            st.markdown(f"🇷🇺 *{word_data['translation']}*")
    with col_meta:
        level = word_data.get('cefr_level', '')
        if level:
            st.markdown(f"<div style='text-align:right;margin-top:8px;'><span style='background:#2a3a4b;color:#4ade80;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;'>{level}</span></div>", unsafe_allow_html=True)

    if word_data.get('definition'):
        st.markdown(f"**Definition:** {word_data['definition']}")

    # DB column is example_sentence
    example = word_data.get('example_sentence') or word_data.get('example', '')
    if example:
        st.markdown(f"**Example:** *{example}*")

    # Mastery rating — 1 = New (worst), 5 = Mastered (best)
    st.markdown("---")
    st.caption("How well do you know this word?")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("1️⃣\nNew", use_container_width=True, key="review_1"):
            update_review(word_data['word'], 1)
            st.session_state.review_index += 1
            st.rerun()
        st.caption("🔴 New")

    with col2:
        if st.button("2️⃣", use_container_width=True, key="review_2"):
            update_review(word_data['word'], 2)
            st.session_state.review_index += 1
            st.rerun()
        st.caption("🟠 Struggling")

    with col3:
        if st.button("3️⃣", use_container_width=True, key="review_3"):
            update_review(word_data['word'], 3)
            st.session_state.review_index += 1
            st.rerun()
        st.caption("🟡 Okay")

    with col4:
        if st.button("4️⃣", use_container_width=True, key="review_4"):
            update_review(word_data['word'], 4)
            st.session_state.review_index += 1
            st.rerun()
        st.caption("🟢 Good")

    with col5:
        if st.button("5️⃣", use_container_width=True, key="review_5"):
            update_review(word_data['word'], 5)
            st.session_state.review_index += 1
            st.rerun()
        st.caption("⭐ Mastered")

    st.markdown("---")
    if st.button("🔄 Reset Review Session", key="review_reset"):
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