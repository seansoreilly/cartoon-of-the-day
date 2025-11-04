"""Cartoon of the Day - Redesigned with improved UX."""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import streamlit as st
from datetime import datetime
from pathlib import Path
import json
from streamlit_js_eval import streamlit_js_eval

from src.location_detector import LocationDetector
from src.news_fetcher import NewsFetcher
from src.cartoon_generator import CartoonGenerator
from src.image_generator import ImageGenerator
from src.utils import save_cartoon_data, format_date_for_location


# Page configuration
st.set_page_config(
    page_title="🎨 Cartoon of the Day",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced styling with more personality
st.markdown("""
<link href="https://cdn.tailwindcss.com" rel="stylesheet">
<style>
    /* Color palette with more vibrant, playful colors */
    :root {
        --primary: #8b5cf6;
        --primary-foreground: #ffffff;
        --secondary: #ec4899;
        --accent: #f59e0b;
        --success: #10b981;
        --error: #ef4444;
        --muted: #6b7280;
        --border: #e5e7eb;
        --input: #f9fafb;
        --background: #ffffff;
        --foreground: #1f2937;
        --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Dark theme */
    .dark {
        --primary: #a78bfa;
        --primary-foreground: #0b1020;
        --secondary: #f472b6;
        --accent: #fbbf24;
        --success: #34d399;
        --error: #f87171;
        --muted: #9ca3af;
        --border: #374151;
        --input: #111827;
        --background: #0b1020;
        --foreground: #e5e7eb;
        --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Main container styling */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }

    /* Hero header with personality */
    .hero-header {
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInDown 0.6s ease;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--muted);
        font-weight: 500;
    }

    /* Action card - the main interaction area */
    .action-card {
        background: var(--input);
        border: 2px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        animation: fadeInUp 0.6s ease;
    }

    .action-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--foreground);
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .action-subtitle {
        font-size: 1.1rem;
        color: var(--muted);
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Primary button - more prominent */
    .primary-btn {
        background: var(--gradient);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 700;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        width: 100%;
        margin: 0.5rem 0;
    }

    .primary-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
    }

    /* Secondary button */
    .secondary-btn {
        background: transparent;
        color: var(--primary);
        border: 2px solid var(--primary);
        padding: 0.9rem 1.8rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }

    .secondary-btn:hover {
        background: rgba(139, 92, 246, 0.1);
        transform: translateY(-2px);
    }

    /* Status bar - more prominent */
    .status-bar {
        background: var(--input);
        border-left: 4px solid var(--primary);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .status-bar.error {
        border-left-color: var(--error);
        background: rgba(239, 68, 68, 0.05);
    }

    .status-bar.success {
        border-left-color: var(--success);
        background: rgba(16, 185, 129, 0.05);
    }

    .status-icon {
        font-size: 1.5rem;
    }

    .status-text {
        flex: 1;
        color: var(--foreground);
        font-size: 1rem;
        font-weight: 500;
    }

    /* Simple 2-step progress */
    .progress-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        margin: 2rem 0;
    }

    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        background: var(--input);
        border: 2px solid var(--border);
        transition: all 0.3s ease;
    }

    .progress-step.active {
        border-color: var(--primary);
        background: rgba(139, 92, 246, 0.1);
    }

    .progress-step.completed {
        border-color: var(--success);
        background: rgba(16, 185, 129, 0.1);
    }

    .progress-number {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        background: var(--gradient);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
    }

    .progress-label {
        font-weight: 600;
        color: var(--foreground);
    }

    /* Cartoon result card */
    .result-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%);
        border: 2px solid var(--primary);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(139, 92, 246, 0.1);
        animation: fadeInUp 0.6s ease;
    }

    /* Location input field enhancement */
    .stTextInput input {
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.9rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        background-color: var(--background) !important;
        color: var(--foreground) !important;
    }

    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1) !important;
    }

    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    /* Fun decorative elements */
    .decoration {
        position: absolute;
        opacity: 0.1;
        pointer-events: none;
    }

    /* Improved button styling for Streamlit buttons */
    .stButton > button {
        background: var(--gradient) !important;
        color: white !important;
        border: none !important;
        padding: 0.9rem 1.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4) !important;
    }

    /* Footer with personality */
    .footer {
        text-align: center;
        color: var(--muted);
        font-size: 0.95rem;
        padding: 3rem 1rem 2rem;
        border-top: 1px solid var(--border);
        margin-top: 4rem;
    }

    .footer-emoji {
        font-size: 1.5rem;
        margin: 0 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


def get_stored_location():
    """Retrieve stored location from browser local storage."""
    try:
        location_json = streamlit_js_eval(
            javascript="window.localStorage.getItem('cartoon_location')",
            key="get_location"
        )
        if location_json:
            return json.loads(location_json)
    except Exception:
        pass
    return None


def save_location_to_storage(location_data, address_data):
    """Save location to browser local storage."""
    try:
        storage_data = {
            'location_data': location_data,
            'address_data': address_data,
            'timestamp': datetime.now().isoformat()
        }
        js_code = f"""
        window.localStorage.setItem('cartoon_location', {json.dumps(json.dumps(storage_data))});
        """
        streamlit_js_eval(javascript=js_code, key=f"save_location_{datetime.now().timestamp()}")
    except Exception:
        pass


def clear_stored_location():
    """Clear stored location from browser local storage."""
    try:
        streamlit_js_eval(
            javascript="window.localStorage.removeItem('cartoon_location')",
            key=f"clear_location_{datetime.now().timestamp()}"
        )
    except Exception:
        pass


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'location_data' not in st.session_state:
        st.session_state.location_data = None
    if 'address_data' not in st.session_state:
        st.session_state.address_data = None
    if 'news_data' not in st.session_state:
        st.session_state.news_data = None
    if 'cartoon_data' not in st.session_state:
        st.session_state.cartoon_data = None
    if 'image_path' not in st.session_state:
        st.session_state.image_path = None
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'location_mode' not in st.session_state:
        st.session_state.location_mode = None  # 'detect' or 'manual'

    # Load saved location from browser storage on first load
    if not st.session_state.address_data:
        stored = get_stored_location()
        if stored:
            st.session_state.location_data = stored.get('location_data')
            st.session_state.address_data = stored.get('address_data')


def display_hero_header():
    """Display the main hero header with personality."""
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">🎨 Cartoon of the Day</h1>
        <p class="hero-subtitle">AI-powered cartoons based on your local news</p>
    </div>
    """, unsafe_allow_html=True)


def display_simple_progress():
    """Display a simple 2-step progress indicator."""
    has_location = bool(st.session_state.address_data)
    has_cartoon = bool(st.session_state.cartoon_data)

    step1_class = "completed" if has_location else "active"
    step2_class = "completed" if has_cartoon else ("active" if has_location else "")

    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-step {step1_class}">
            <div class="progress-number">{'✓' if has_location else '1'}</div>
            <span class="progress-label">Set Location</span>
        </div>
        <span style="color: var(--muted);">→</span>
        <div class="progress-step {step2_class}">
            <div class="progress-number">{'✓' if has_cartoon else '2'}</div>
            <span class="progress-label">View Cartoon</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_status_message(message, status_type="info"):
    """Display a prominent status message."""
    icon = "💡" if status_type == "info" else "❌" if status_type == "error" else "✅"
    st.markdown(f"""
    <div class="status-bar {status_type}">
        <span class="status-icon">{icon}</span>
        <span class="status-text">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def location_and_generate_section():
    """Combined location selection and generation in one flow."""

    # If we already have a cartoon, show option to generate new one
    if st.session_state.cartoon_data:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate New Cartoon", use_container_width=True):
                st.session_state.news_data = None
                st.session_state.cartoon_data = None
                st.session_state.image_path = None
                st.session_state.generation_in_progress = False
                st.rerun()
        with col2:
            if st.button("📍 Change Location", use_container_width=True):
                clear_stored_location()
                st.session_state.location_data = None
                st.session_state.address_data = None
                st.session_state.news_data = None
                st.session_state.cartoon_data = None
                st.session_state.image_path = None
                st.session_state.generation_in_progress = False
                st.rerun()
        return

    # Main action card
    st.markdown("""
    <div class="action-card">
        <h2 class="action-title">🗞️ Get Your Daily Cartoon!</h2>
        <p class="action-subtitle">Tell us your location, and we'll generate a unique cartoon based on today's local news.</p>
    </div>
    """, unsafe_allow_html=True)

    # If location is set, show it and offer to generate
    if st.session_state.address_data:
        city = st.session_state.address_data.get('city', 'Unknown')
        country = st.session_state.address_data.get('country', 'Unknown')

        col1, col2 = st.columns([2, 1])
        with col1:
            display_status_message(f"📍 Location set: {city}, {country}", "success")
        with col2:
            if st.button("Change", use_container_width=True):
                clear_stored_location()
                st.session_state.location_data = None
                st.session_state.address_data = None
                st.rerun()

        # Big generate button
        if st.button("✨ Generate Today's Cartoon", use_container_width=True, type="primary"):
            generate_cartoon_with_progress()
        return

    # Location selection options
    st.markdown("<h3 style='text-align: center; margin: 1.5rem 0;'>How would you like to set your location?</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📍 Detect My Location", use_container_width=True):
            st.session_state.location_mode = "detect"
            st.rerun()

    with col2:
        if st.button("⌨️ Enter Location Manually", use_container_width=True):
            st.session_state.location_mode = "manual"
            st.rerun()

    # Handle location detection
    if st.session_state.location_mode == "detect":
        with st.spinner("🔍 Detecting your location..."):
            detector = LocationDetector()
            result = detector.get_location_with_fallback()

            if result:
                coords, address = result
                st.session_state.location_data = coords
                st.session_state.address_data = address
                save_location_to_storage(coords, address)
                st.session_state.location_mode = None
                st.success(f"✅ Location detected: {address.get('city', 'Unknown')}")
                st.rerun()
            else:
                st.session_state.error_message = "Could not detect location. Please try manual entry."
                st.session_state.location_mode = "manual"
                st.rerun()

    # Handle manual entry
    if st.session_state.location_mode == "manual":
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Enter Your Location</h3>", unsafe_allow_html=True)

        # Quick suggestions
        suggestions = ["London, UK", "New York, USA", "Tokyo, Japan", "Sydney, Australia"]
        cols = st.columns(len(suggestions))
        for idx, suggestion in enumerate(suggestions):
            with cols[idx]:
                if st.button(suggestion, use_container_width=True, key=f"suggest_{idx}"):
                    process_location(suggestion)

        # Manual input
        manual_location = st.text_input(
            "",
            placeholder="e.g., Paris, France",
            key="location_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.location_mode = None
                st.rerun()
        with col2:
            if manual_location and st.button("Use This Location", use_container_width=True, type="primary"):
                process_location(manual_location)

    # Status message
    if st.session_state.error_message:
        display_status_message(st.session_state.error_message, "error")
        st.session_state.error_message = None
    else:
        display_status_message("We use your location only to find relevant local news.", "info")


def process_location(location_text):
    """Process a location string and set it in session state."""
    with st.spinner(f"🔍 Finding {location_text}..."):
        detector = LocationDetector()
        result = detector.get_location_with_fallback(location_text)

        if result:
            coords, address = result
            st.session_state.location_data = coords
            st.session_state.address_data = address
            save_location_to_storage(coords, address)
            st.session_state.location_mode = None
            st.success(f"✅ Location set: {address.get('city', 'Unknown')}")
            st.rerun()
        else:
            st.session_state.error_message = f"Could not find '{location_text}'. Please try a different location."
            st.rerun()


def generate_cartoon_with_progress():
    """Generate cartoon with visual progress indicators."""
    st.session_state.generation_in_progress = True

    city = st.session_state.address_data.get('city', 'Unknown')
    country = st.session_state.address_data.get('country', 'Unknown')

    # Create a container for progress updates
    progress_container = st.container()

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Fetch News (30%)
            status_text.markdown("### 📰 Finding today's local news...")
            progress_bar.progress(10)

            fetcher = NewsFetcher()
            news_result = fetcher.fetch_and_summarize(city, country)
            st.session_state.news_data = news_result
            progress_bar.progress(30)

            # Step 2: Generate Concepts (60%)
            status_text.markdown("### 💭 Creating cartoon concepts...")
            progress_bar.progress(40)

            generator = CartoonGenerator()
            cartoon_data = generator.generate_concepts(
                news_result['dominant_topic'],
                f"{city}, {country}",
                news_result['summary']
            )
            st.session_state.cartoon_data = cartoon_data
            progress_bar.progress(60)

            # Step 3: Generate Image (90%)
            status_text.markdown("### 🎨 Drawing your cartoon...")
            progress_bar.progress(70)

            image_gen = ImageGenerator()
            image_path = image_gen.generate_and_save(
                cartoon_data,
                use_placeholder=False
            )
            st.session_state.image_path = image_path
            progress_bar.progress(90)

            # Step 4: Save data (100%)
            if image_path:
                save_cartoon_data(
                    f"{city}, {country}",
                    cartoon_data,
                    str(image_path),
                    news_result
                )

            progress_bar.progress(100)
            status_text.markdown("### ✅ Complete! Your cartoon is ready!")

            # Brief pause to show completion
            import time
            time.sleep(1)

            st.session_state.generation_in_progress = False
            st.balloons()
            st.rerun()

        except Exception as e:
            st.session_state.error_message = f"Oops! Something went wrong: {str(e)}"
            st.session_state.generation_in_progress = False
            st.rerun()


def display_cartoon_results():
    """Display the generated cartoon with enhanced presentation."""
    if not st.session_state.cartoon_data:
        return

    cartoon_data = st.session_state.cartoon_data

    # Topic header
    topic = cartoon_data.get('topic', 'News')
    st.markdown(f"""
    <div class="result-card">
        <h2 style="text-align: center; color: var(--primary); margin-bottom: 1.5rem;">
            📰 Today's Topic: {topic}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Winner display
    winner_title = cartoon_data.get('winner')
    ideas = cartoon_data.get('ideas', [])
    winner_concept = next((idea for idea in ideas if idea['title'] == winner_title), None)

    if winner_concept and st.session_state.image_path:
        col1, col2 = st.columns([1, 1])

        with col1:
            if Path(st.session_state.image_path).exists():
                st.image(str(st.session_state.image_path), use_container_width=True)

        with col2:
            st.markdown(f"### 🏆 {winner_concept['title']}")
            st.markdown(f"**Story:** {winner_concept['premise']}")
            st.markdown(f"*Why it's funny:* {winner_concept['why_funny']}")

            # Action buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if Path(st.session_state.image_path).exists():
                    with open(st.session_state.image_path, "rb") as file:
                        st.download_button(
                            label="💾 Download",
                            data=file,
                            file_name=Path(st.session_state.image_path).name,
                            mime="image/png",
                            use_container_width=True
                        )
            with col_b:
                share_text = f"{winner_concept['title']} — {winner_concept['premise']}"
                if st.button("📋 Share", use_container_width=True):
                    js_code = f"navigator.clipboard.writeText({json.dumps(share_text)});"
                    streamlit_js_eval(javascript=js_code, key=f"copy_{datetime.now().timestamp()}")
                    st.toast("✅ Copied to clipboard!", icon="📋")

    # Other concepts in expander
    with st.expander("📊 See All Concepts"):
        ranking = cartoon_data.get('ranking', [])
        for i, title in enumerate(ranking, 1):
            concept = next((idea for idea in ideas if idea['title'] == title), None)
            if concept:
                st.markdown(f"**{i}. {concept['title']}** {'🏆' if i == 1 else ''}")
                st.markdown(f"_{concept['premise']}_")
                st.markdown(f"Why funny: {concept['why_funny']}")
                st.markdown("---")


def display_sidebar():
    """Display sidebar with recent cartoons."""
    with st.sidebar:
        st.markdown("### 📚 Recent Cartoons")

        cartoons_dir = Path("data/cartoons")
        if not cartoons_dir.exists():
            st.info("No cartoons yet")
            return

        json_files = sorted(cartoons_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

        if not json_files:
            st.info("No cartoons yet")
            return

        for json_file in json_files:
            filename = json_file.stem
            png_file = json_file.with_suffix('.png')

            if st.button(f"📄 {filename[:20]}...", key=f"load_{filename}", use_container_width=True):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if png_file.exists():
                    st.session_state.cartoon_data = data
                    st.session_state.image_path = str(png_file)
                    if 'location' in data:
                        location_parts = data['location'].split(', ')
                        if len(location_parts) >= 2:
                            st.session_state.address_data = {
                                'city': location_parts[0],
                                'country': location_parts[-1]
                            }
                    st.rerun()


def main():
    """Main application function."""
    initialize_session_state()

    # Hero header
    display_hero_header()

    # Simple 2-step progress
    display_simple_progress()

    st.markdown("---")

    # Main content area - combined location and generation
    location_and_generate_section()

    # Display results if available
    if st.session_state.cartoon_data:
        display_cartoon_results()

    # Sidebar
    display_sidebar()

    # Footer with personality
    st.markdown("""
    <div class="footer">
        <span class="footer-emoji">🤖</span>
        Powered by Google Gemini AI
        <span class="footer-emoji">•</span>
        <span class="footer-emoji">❤️</span>
        Made with Streamlit
        <span class="footer-emoji">🎨</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()