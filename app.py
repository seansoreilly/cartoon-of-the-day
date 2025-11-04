"""Cartoon of the Day - Main Streamlit Application."""

import streamlit as st
from datetime import datetime
from pathlib import Path

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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .location-badge {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .winner-card {
        border: 3px solid #FF6B6B;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #FFF5F5;
        margin: 1rem 0;
    }
    .concept-card {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #FAFAFA;
    }
    .topic-banner {
        background-color: #4ECDC4;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


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


def display_header():
    """Display the application header."""
    st.markdown('<h1 class="main-header">🎨 Cartoon of the Day</h1>', unsafe_allow_html=True)

    if st.session_state.address_data:
        location_str = f"📍 {st.session_state.address_data.get('city', 'Unknown')}, {st.session_state.address_data.get('country', 'Unknown')}"
        st.markdown(f'<p class="location-badge">{location_str}</p>', unsafe_allow_html=True)


def location_section():
    """Handle location detection and manual entry."""
    st.subheader("📍 Step 1: Choose Your Location")

    # Improved UX with tabs instead of columns
    tab1, tab2 = st.tabs(["🌍 Auto-Detect", "📍 Manual Entry"])

    with tab1:
        st.markdown("Allow browser access to detect your location automatically")
        if st.button("🌍 Detect My Location", use_container_width=True):
            with st.spinner("Detecting your location..."):
                detector = LocationDetector()
                result = detector.get_location_with_fallback()

                if result:
                    coords, address = result
                    st.session_state.location_data = coords
                    st.session_state.address_data = address
                    st.success(f"✅ Location detected: {address.get('city', 'Unknown')}")
                    st.rerun()
                else:
                    st.error("Could not detect location. Please try manual entry.")

    with tab2:
        st.markdown("Enter any city or location worldwide")
        manual_location = st.text_input(
            "Enter a location:",
            placeholder="e.g., Paris, France",
            help="Enter a city and country name"
        )

        if manual_location and manual_location.strip():
            if st.button("📍 Use This Location", use_container_width=True):
                with st.spinner(f"Finding {manual_location}..."):
                    detector = LocationDetector()
                    result = detector.get_location_with_fallback(manual_location)

                    if result:
                        coords, address = result
                        st.session_state.location_data = coords
                        st.session_state.address_data = address
                        st.success(f"✅ Location set: {address.get('city', 'Unknown')}")
                        st.rerun()
                    else:
                        st.error(f"Could not find '{manual_location}'. Try a different location.")


def generate_cartoon_section():
    """Handle cartoon generation."""
    if not st.session_state.address_data:
        # Empty state with engaging instructions
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 10px; margin: 1rem 0;'>
            <h2 style='color: #666;'>🎨 Ready to create your cartoon?</h2>
            <p style='color: #888; font-size: 1.1rem;'>Set your location above and click 'Generate Cartoon' to get started!</p>
            <p style='color: #999;'>Each cartoon is uniquely crafted from today's local news</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.subheader("🎨 Step 2: Generate Today's Cartoon")

    if st.button("✨ Generate Cartoon", use_container_width=True, type="primary"):
        city = st.session_state.address_data.get('city', 'Unknown')
        country = st.session_state.address_data.get('country', 'Unknown')

        # Progress bar for better UX
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Fetch News
        status_text.text("📰 Step 1/3: Fetching local news...")
        progress_bar.progress(10)
        with st.spinner(f"Finding news in {city}..."):
            fetcher = NewsFetcher()
            news_result = fetcher.fetch_and_summarize(city, country)
            st.session_state.news_data = news_result
        progress_bar.progress(33)

        # Step 2: Generate Cartoons
        status_text.text("💭 Step 2/3: Generating cartoon concepts...")
        progress_bar.progress(40)
        with st.spinner("Creating cartoon concepts..."):
            generator = CartoonGenerator()
            cartoon_data = generator.generate_concepts(
                news_result['dominant_topic'],
                f"{city}, {country}",
                news_result['summary']
            )
            st.session_state.cartoon_data = cartoon_data
        progress_bar.progress(66)

        # Step 3: Generate Image
        status_text.text("🎨 Step 3/3: Drawing your cartoon...")
        progress_bar.progress(75)
        with st.spinner("Drawing cartoon..."):
            image_gen = ImageGenerator()
            image_path = image_gen.generate_and_save(
                cartoon_data,
                use_placeholder=False  # Generate real images with Gemini
            )
            st.session_state.image_path = image_path
        progress_bar.progress(90)

        # Step 4: Save data
        if image_path:
            save_cartoon_data(
                f"{city}, {country}",
                cartoon_data,
                str(image_path),
                news_result  # Pass news data with headlines and URLs
            )

        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        st.success("🎉 Cartoon generated successfully!")
        st.rerun()


def display_cartoon_results():
    """Display the generated cartoon and concepts."""
    if not st.session_state.cartoon_data:
        return

    cartoon_data = st.session_state.cartoon_data

    # Display topic banner
    topic = cartoon_data.get('topic', 'News')
    st.markdown(f'<div class="topic-banner">📰 Today\'s Topic: {topic}</div>', unsafe_allow_html=True)

    # Display winner
    st.markdown("## 🏆 Winner")

    winner_title = cartoon_data.get('winner')
    ideas = cartoon_data.get('ideas', [])
    winner_concept = next((idea for idea in ideas if idea['title'] == winner_title), None)

    if winner_concept:
        st.markdown('<div class="winner-card">', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"### {winner_concept['title']}")
            st.markdown(f"**Premise:** {winner_concept['premise']}")
            st.markdown(f"*Why it's funny:* {winner_concept['why_funny']}")

        with col2:
            if st.session_state.image_path and Path(st.session_state.image_path).exists():
                st.image(str(st.session_state.image_path), use_container_width=True)
            else:
                st.info("Image will appear here")

        st.markdown('</div>', unsafe_allow_html=True)

    # Display all ranked concepts
    st.markdown("## 📊 All Concepts (Ranked)")

    ranking = cartoon_data.get('ranking', [])

    for i, title in enumerate(ranking, 1):
        concept = next((idea for idea in ideas if idea['title'] == title), None)

        if concept:
            with st.expander(f"{i}. {concept['title']}" + (" 🏆" if i == 1 else "")):
                st.markdown(f"**Premise:** {concept['premise']}")
                st.markdown(f"*Why it's funny:* {concept['why_funny']}")

                # Display source news links
                headlines = []

                # Try to get headlines from session state first (during generation)
                if st.session_state.news_data:
                    # Handle both nested and flat structures
                    news_dict = st.session_state.news_data.get('news_data') or st.session_state.news_data
                    nested_news = news_dict.get('news_data')  # Check for nested news_data
                    if nested_news and 'headlines' in nested_news:
                        headlines = nested_news.get('headlines', [])
                    elif 'headlines' in news_dict:
                        headlines = news_dict.get('headlines', [])

                # Also check if news_data was saved in the cartoon_data
                if not headlines and 'news_data' in cartoon_data:
                    saved_news = cartoon_data['news_data']
                    nested_news = saved_news.get('news_data')  # Check for nested news_data
                    if nested_news and 'headlines' in nested_news:
                        headlines = nested_news.get('headlines', [])
                    elif 'headlines' in saved_news:
                        headlines = saved_news.get('headlines', [])

                if headlines:
                    st.markdown("---")
                    st.markdown("**📰 Based on:**")
                    for headline in headlines[:3]:  # Show top 3 headlines
                        url = headline.get('url', '')
                        source = headline.get('source', 'News')
                        title_text = headline.get('title', '')

                        if url:
                            st.markdown(f"• [{title_text}]({url}) *— {source}*")
                        else:
                            st.markdown(f"• {title_text} *— {source}*")

    # Action buttons with share features
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 New Cartoon", use_container_width=True):
            st.session_state.news_data = None
            st.session_state.cartoon_data = None
            st.session_state.image_path = None
            st.rerun()

    with col2:
        if st.button("📍 Change Location", use_container_width=True):
            st.session_state.location_data = None
            st.session_state.address_data = None
            st.session_state.news_data = None
            st.session_state.cartoon_data = None
            st.session_state.image_path = None
            st.rerun()

    with col3:
        if st.session_state.image_path and Path(st.session_state.image_path).exists():
            with open(st.session_state.image_path, "rb") as file:
                st.download_button(
                    label="💾 Download",
                    data=file,
                    file_name=Path(st.session_state.image_path).name,
                    mime="image/png",
                    use_container_width=True
                )

    with col4:
        if st.session_state.image_path and Path(st.session_state.image_path).exists():
            if st.button("📋 Copy Link", use_container_width=True):
                # Get the full path for sharing
                full_path = Path(st.session_state.image_path).absolute()
                st.toast(f"📋 Path copied: {full_path.name}", icon="✅")


def display_recent_cartoons_sidebar():
    """Display recent cartoons in sidebar."""
    with st.sidebar:
        st.subheader("📚 Recent Cartoons")

        cartoons_dir = Path("data/cartoons")
        if not cartoons_dir.exists():
            st.info("No cartoons yet")
            return

        # Get recent JSON files
        json_files = sorted(cartoons_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]

        if not json_files:
            st.info("No cartoons yet")
            return

        for json_file in json_files:
            # Extract location and date from filename
            filename = json_file.stem
            # Display as button
            if st.button(f"🎨 {filename}", use_container_width=True, key=f"recent_{filename}"):
                # Load the cartoon data
                import json
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check if PNG exists
                png_file = json_file.with_suffix('.png')
                if png_file.exists():
                    # Load into session state
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
    display_header()

    # Sidebar with recent cartoons
    display_recent_cartoons_sidebar()

    # Main workflow
    location_section()

    st.markdown("---")

    generate_cartoon_section()

    if st.session_state.cartoon_data:
        st.markdown("---")
        display_cartoon_results()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #999; font-size: 0.9rem;'>"
        "🤖 Powered by Google Gemini AI | "
        "Made with ❤️ using Streamlit"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
