"""Cartoon of the Day - Redesigned to match exact UI specification."""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import streamlit as st
from pathlib import Path
import time
import json

from src.location_detector import LocationDetector
from src.news_fetcher import NewsFetcher
from src.cartoon_generator import CartoonGenerator
from src.image_generator import ImageGenerator
from src.utils import save_cartoon_data
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

# --- Rate Limiting Setup ---
# In-memory storage for rate limiting.
# Note: This is per-process. If you scale to multiple Streamlit processes,
# you would need a centralized storage like Redis.
storage = MemoryStorage()
limiter = FixedWindowRateLimiter(storage)
# Limit to 2 image generations per minute per user session.
# Streamlit reruns scripts, so we use st.session_state to get a unique identifier.
# A simple way is to use the initial session_id.
rate_limit_item = parse("2/minute")


# Page configuration
st.set_page_config(
    page_title="🎨 Cartoon of the Day",
    page_icon="🎨",
    layout="centered",  # Changed to centered for 900px max-width
    initial_sidebar_state="collapsed"
)

# Exact styling from specification
st.markdown("""
<style>
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* Main app container - 900px max width */
    .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}

    /* Header Title - exact spec */
    .header-title {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Header Subtitle - exact spec */
    .header-subtitle {
        font-size: 1.25rem;
        color: #6b7280;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }

    /* Progress Container */
    .progress-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }

    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .progress-circle {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
    }

    .progress-circle.active {
        background: rgba(139, 92, 246, 0.1);
        border: 2px solid #8b5cf6;
        color: #8b5cf6;
    }

    .progress-circle.pending {
        background: #f3f4f6;
        border: 2px solid #e5e7eb;
        color: #6b7280;
    }

    .progress-circle.completed {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid #10b981;
        color: #10b981;
    }

    .progress-label {
        font-size: 1rem;
        font-weight: 500;
    }

    .progress-connector {
        color: #9ca3af;
        font-size: 1.5rem;
    }

    /* Action Card - exact spec */
    .action-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        padding: 2rem;
        margin-top: 2rem;
        text-align: center;
    }

    /* Card Title */
    .card-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    /* Card Subtitle */
    .card-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* Button styling - exact spec */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1) !important;
    }

    /* Secondary button style */
    .secondary-button > button {
        background: transparent !important;
        color: #8b5cf6 !important;
        border: 2px solid #8b5cf6 !important;
    }

    .secondary-button > button:hover {
        background: rgba(139, 92, 246, 0.1) !important;
    }

    /* Input field - exact spec */
    .stTextInput > div > div > input {
        padding: 0.9rem !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1) !important;
    }

    /* Success message */
    .success-msg {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #065f46;
        font-weight: 500;
    }

    /* Footer - exact spec */
    .footer-text {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        font-size: 0.875rem;
        color: #6b7280;
    }

    /* Hide Streamlit elements we don't need */
    .css-1d391kg {padding-top: 0;}
    .css-18e3th9 {padding-top: 0;}

    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        .progress-label {
            display: none;
        }
    }
</style>
""", unsafe_allow_html=True)


def save_location_to_storage(location_data, address_data):
    """Save location to browser localStorage and server-side cache."""
    if location_data and address_data:
        storage_data = {
            'location_data': location_data,
            'address_data': address_data
        }
        storage_json = json.dumps(storage_data)

        # Save to server-side cache file
        try:
            cache_dir = Path('.streamlit_cache')
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / 'location.json'
            with open(cache_file, 'w') as f:
                json.dump(storage_data, f)
        except Exception as e:
            print(f"Could not save location to cache: {e}")

        # Inject JavaScript to save to browser localStorage
        script = f"""
            <script>
            try {{
                const data = {storage_json};
                localStorage.setItem('cartoon_location', JSON.stringify(data));
                console.log('Location saved to localStorage');
            }} catch (e) {{
                console.error('Could not save to localStorage:', e);
            }}
            </script>
            """
        st.markdown(script, unsafe_allow_html=True)


def restore_location_from_storage():
    """Restore location from server-side cache or browser localStorage."""
    # Check if location was already restored
    if st.session_state.location_data and st.session_state.address_data:
        return

    # Try to restore from server-side cache file
    try:
        cache_file = Path('.streamlit_cache/location.json')
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                stored_data = json.load(f)
                location_data = stored_data.get('location_data')
                address_data = stored_data.get('address_data')
                if location_data and address_data:
                    st.session_state.location_data = location_data
                    st.session_state.address_data = address_data
                    print(f"Restored location from cache: {address_data.get('city')}")
                    return
    except Exception as e:
        print(f"Could not restore from cache: {e}")

    # Inject JavaScript to attempt localStorage restoration
    st.markdown(
        """
        <script>
        (function() {
            try {
                const stored = localStorage.getItem('cartoon_location');
                if (stored) {
                    const data = JSON.parse(stored);
                    console.log('Location available in browser storage:', data);
                    // Store in window for reference
                    window.cartoonStoredLocation = data;
                }
            } catch (e) {
                console.error('Error accessing localStorage:', e);
            }
        })();
        </script>
        """,
        unsafe_allow_html=True
    )


def initialize_session_state():
    """Initialize session state variables."""
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
    if 'show_manual_entry' not in st.session_state:
        st.session_state.show_manual_entry = False
    if 'generating' not in st.session_state:
        st.session_state.generating = False
    if 'stored_location' not in st.session_state:
        st.session_state.stored_location = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id


def display_header():
    """Display the header section exactly as specified."""
    st.markdown("""
        <h1 class="header-title">🎨 Cartoon of the Day</h1>
        <p class="header-subtitle">AI-powered cartoons based on your local news</p>
    """, unsafe_allow_html=True)


def display_progress():
    """Display the 2-step progress indicator exactly as specified."""
    has_location = bool(st.session_state.address_data)
    has_cartoon = bool(st.session_state.cartoon_data)

    # Determine states
    step1_state = "completed" if has_location else "active"
    step1_icon = "✓" if has_location else "1"
    step2_state = "completed" if has_cartoon else ("active" if has_location else "pending")
    step2_icon = "✓" if has_cartoon else "2"

    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-step">
                <div class="progress-circle {step1_state}">{step1_icon}</div>
                <span class="progress-label" style="color: {'#10b981' if has_location else '#8b5cf6'}">Set Location</span>
            </div>
            <span class="progress-connector">→</span>
            <div class="progress-step">
                <div class="progress-circle {step2_state}">{step2_icon}</div>
                <span class="progress-label" style="color: {'#10b981' if has_cartoon else '#8b5cf6' if has_location else '#6b7280'}">View Cartoon</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def display_main_action_area():
    """Display the main action card area."""
    # Card container
    st.markdown('<div class="action-card">', unsafe_allow_html=True)

    if st.session_state.cartoon_data:
        # State: Cartoon Generated - show results
        display_cartoon_results()

    elif st.session_state.address_data:
        # State C: Location Set
        city = st.session_state.address_data.get('city', 'Unknown')
        country = st.session_state.address_data.get('country', 'Unknown')

        # Success message with change button
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div class="success-msg">
                    📍 Location set: {city}, {country}
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Change", key="change_location"):
                st.session_state.location_data = None
                st.session_state.address_data = None
                st.session_state.show_manual_entry = False
                st.rerun()

        # Generate button
        if st.button("✨ Generate Today's Cartoon", key="generate_cartoon", help="Click to generate a cartoon"):
            generate_cartoon()

    elif st.session_state.show_manual_entry:
        # State B: Manual Entry
        st.markdown("""
            <h2 class="card-title">📍 Enter Your Location</h2>
        """, unsafe_allow_html=True)

        # Quick suggestions
        st.markdown("<p style='color: #6b7280; margin: 1rem 0;'>Quick suggestions:</p>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        suggestions = ["London, UK", "New York, USA", "Tokyo, Japan", "Sydney, Australia"]
        for col, suggestion in zip([col1, col2, col3, col4], suggestions):
            with col:
                if st.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
                    process_location(suggestion)

        # Input field
        location_input = st.text_input("", placeholder="e.g., Paris, France", key="location_input", label_visibility="collapsed")

        # Cancel and Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_entry", use_container_width=True):
                st.session_state.show_manual_entry = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="primary-button">', unsafe_allow_html=True)
            if st.button("Use This Location", key="use_location", use_container_width=True):
                if location_input:
                    process_location(location_input)
                else:
                    st.error("Please enter a location")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # State A: No Location Set
        st.markdown("""
            <h2 class="card-title">🗞️ Get Your Daily Cartoon!</h2>
            <p class="card-subtitle">Tell us your location, and we'll generate a unique cartoon based on today's local news.</p>
        """, unsafe_allow_html=True)

        # Two action buttons side by side
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📍 Detect My Location", key="detect_location", use_container_width=True):
                detect_location()

        with col2:
            if st.button("⌨️ Enter Location Manually", key="manual_entry", use_container_width=True):
                st.session_state.show_manual_entry = True
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def detect_location():
    """Handle location detection."""
    with st.spinner("🔍 Detecting your location..."):
        detector = LocationDetector()
        result = detector.get_location_with_fallback()

        if result:
            coords, address = result
            st.session_state.location_data = coords
            st.session_state.address_data = address
            # Save location to localStorage
            save_location_to_storage(coords, address)
            st.success(f"✅ Location detected: {address.get('city', 'Unknown')}")
            st.rerun()
        else:
            st.error("Could not detect location. Please enter manually.")
            st.session_state.show_manual_entry = True
            st.rerun()


def process_location(location_text):
    """Process a manually entered location."""
    with st.spinner(f"🔍 Finding {location_text}..."):
        detector = LocationDetector()
        result = detector.get_location_with_fallback(location_text)

        if result:
            coords, address = result
            st.session_state.location_data = coords
            st.session_state.address_data = address
            # Save location to localStorage
            save_location_to_storage(coords, address)
            st.session_state.show_manual_entry = False
            st.success(f"✅ Location set: {address.get('city', 'Unknown')}")
            st.rerun()
        else:
            st.error(f"Could not find '{location_text}'. Please try a different location.")


def generate_cartoon():
    """Generate the cartoon with progress indicators and rate limiting."""
    try:
        # Hit the rate limiter before doing anything else
        if not limiter.hit(rate_limit_item, st.session_state.session_id):
            # The cost of this check is very low
            time_left = limiter.get_window_stats(rate_limit_item, st.session_state.session_id)[1]
            st.error(f"⏳ Rate limit exceeded. Please try again in {int(time_left)} seconds.")
            return

        st.session_state.generating = True

        city = st.session_state.address_data.get('city', 'Unknown')
        country = st.session_state.address_data.get('country', 'Unknown')

        progress_placeholder = st.empty()
        progress_bar = st.progress(0)

        # Step 1: Fetch News (30%)
        progress_placeholder.markdown("### 📰 Finding today's local news...")
        progress_bar.progress(10)

        fetcher = NewsFetcher()
        news_result = fetcher.fetch_and_summarize(city, country)
        st.session_state.news_data = news_result
        progress_bar.progress(30)

        # Step 2: Generate Concepts (60%)
        progress_placeholder.markdown("### 💭 Creating cartoon concepts...")
        progress_bar.progress(40)

        generator = CartoonGenerator()
        # Get headlines from nested news_data structure
        headlines = news_result.get('news_data', {}).get('headlines', [])
        cartoon_data = generator.generate_concepts(
            news_result['dominant_topic'],
            f"{city}, {country}",
            news_result['summary'],
            headlines
        )
        st.session_state.cartoon_data = cartoon_data
        progress_bar.progress(60)

        # Step 3: Generate Image (90%)
        progress_placeholder.markdown("### 🎨 Drawing your cartoon...")
        progress_bar.progress(70)

        image_gen = ImageGenerator()
        image_path = image_gen.generate_and_save(cartoon_data, use_placeholder=False, news_data=news_result)
        st.session_state.image_path = image_path
        progress_bar.progress(90)

        # Save data
        if image_path:
            save_cartoon_data(
                f"{city}, {country}",
                cartoon_data,
                str(image_path),
                news_result
            )

        progress_bar.progress(100)
        progress_placeholder.markdown("### ✅ Complete! Your cartoon is ready!")

        # Small delay to show completion
        time.sleep(1)

        st.session_state.generating = False
        st.balloons()
        st.rerun()

    except Exception as e:
        st.error(f"❌ Oops! Something went wrong: {str(e)}")
        st.session_state.generating = False




def display_cartoon_results():
    """Display the generated cartoon results."""
    if not st.session_state.cartoon_data:
        return

    cartoon_data = st.session_state.cartoon_data

    # Topic
    topic = cartoon_data.get('topic', 'News')
    st.markdown(f"### 📰 Today's Topic: {topic}")

    # Winner display
    winner_title = cartoon_data.get('winner')
    ideas = cartoon_data.get('ideas', [])
    winner_concept = next((idea for idea in ideas if idea['title'] == winner_title), None)

    if winner_concept and st.session_state.image_path:
        # Display image
        if Path(st.session_state.image_path).exists():
            st.image(str(st.session_state.image_path), use_container_width=True)

        # Display winner details
        st.markdown(f"### 🏆 {winner_concept['title']}")
        st.markdown(f"**Story:** {winner_concept['premise']}")
        st.markdown(f"*Why it's funny:* {winner_concept['why_funny']}")

        # Display comic strip script if available
        if winner_concept.get('script'):
            st.markdown("### 📖 Comic Strip Script")
            script_lines = winner_concept['script'].split('\n')
            script_display = '\n\n'.join(script_lines)
            st.text(script_display)

        # Display news source link if available
        if winner_concept.get('news_url') and winner_concept.get('news_source'):
            st.markdown(
                f"📰 [Read full story on {winner_concept['news_source']}]({winner_concept['news_url']})",
                unsafe_allow_html=False
            )

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 New Cartoon", key="new_cartoon", use_container_width=True):
                st.session_state.news_data = None
                st.session_state.cartoon_data = None
                st.session_state.image_path = None
                st.rerun()

        with col2:
            if st.button("📍 Change Location", key="change_loc_results", use_container_width=True):
                st.session_state.location_data = None
                st.session_state.address_data = None
                st.session_state.news_data = None
                st.session_state.cartoon_data = None
                st.session_state.image_path = None
                st.session_state.show_manual_entry = False
                st.rerun()

        with col3:
            file_exists = Path(st.session_state.image_path).exists()
            if file_exists:
                with open(st.session_state.image_path, "rb") as file:
                    st.download_button(
                        label="💾 Download",
                        data=file,
                        file_name=Path(st.session_state.image_path).name,
                        mime="image/png",
                        key="download_cartoon",
                        use_container_width=True
                    )
            else:
                st.button("💾 Download", disabled=True, key="download_cartoon_disabled", use_container_width=True)

    # Show other concepts in expander
    with st.expander("📊 See All Concepts"):
        ranking = cartoon_data.get('ranking', [])
        for i, title in enumerate(ranking, 1):
            concept = next((idea for idea in ideas if idea['title'] == title), None)
            if concept:
                st.markdown(f"**{i}. {concept['title']}** {'🏆' if i == 1 else ''}")
                st.markdown(f"_{concept['premise']}_")
                st.markdown(f"Why funny: {concept['why_funny']}")

                # Display comic strip script if available
                if concept.get('script'):
                    st.markdown("#### 📖 Comic Strip Script")
                    script_lines = concept['script'].split('\n')
                    script_display = '\n\n'.join(script_lines)
                    st.text(script_display)

                # Display news source link if available
                if concept.get('news_url') and concept.get('news_source'):
                    st.markdown(
                        f"📰 [Read full story on {concept['news_source']}]({concept['news_url']})"
                    )

                st.markdown("---")


def display_footer():
    """Display the footer exactly as specified."""
    st.markdown("""
        <div class="footer-text">
            🤖 Powered by Google Gemini AI • ❤️ Made with Streamlit 🎨
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    initialize_session_state()

    # Load location from localStorage on startup
    restore_location_from_storage()

    # Header
    display_header()

    # Progress indicator
    display_progress()

    # Main action area
    display_main_action_area()

    # Footer
    display_footer()


if __name__ == "__main__":
    main()