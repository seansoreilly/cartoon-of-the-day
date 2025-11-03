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

    col1, col2 = st.columns([1, 2])

    with col1:
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
                    st.error("Could not detect location. Please enter manually.")

    with col2:
        manual_location = st.text_input(
            "Or enter a location:",
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
        st.info("👆 Please set your location first to generate cartoons")
        return

    st.subheader("🎨 Step 2: Generate Today's Cartoon")

    if st.button("✨ Generate Cartoon", use_container_width=True, type="primary"):
        city = st.session_state.address_data.get('city', 'Unknown')
        country = st.session_state.address_data.get('country', 'Unknown')

        # Step 1: Fetch News
        with st.spinner(f"📰 Finding news in {city}..."):
            fetcher = NewsFetcher()
            news_result = fetcher.fetch_and_summarize(city, country)
            st.session_state.news_data = news_result

        # Step 2: Generate Cartoons
        with st.spinner("💭 Creating cartoon concepts..."):
            generator = CartoonGenerator()
            cartoon_data = generator.generate_concepts(
                news_result['dominant_topic'],
                f"{city}, {country}",
                news_result['summary']
            )
            st.session_state.cartoon_data = cartoon_data

        # Step 3: Generate Image
        with st.spinner("🎨 Drawing cartoon..."):
            image_gen = ImageGenerator()
            image_path = image_gen.generate_and_save(
                cartoon_data,
                use_placeholder=False  # Generate real images with Gemini
            )
            st.session_state.image_path = image_path

        # Step 4: Save data
        if image_path:
            save_cartoon_data(
                f"{city}, {country}",
                cartoon_data,
                str(image_path)
            )

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
                if st.session_state.news_data and 'headlines' in st.session_state.news_data:
                    st.markdown("---")
                    st.markdown("**📰 Based on:**")
                    headlines = st.session_state.news_data.get('headlines', [])
                    for headline in headlines[:3]:  # Show top 3 headlines
                        url = headline.get('url', '')
                        source = headline.get('source', 'News')
                        title_text = headline.get('title', '')

                        if url:
                            st.markdown(f"• [{title_text}]({url}) *— {source}*")
                        else:
                            st.markdown(f"• {title_text} *— {source}*")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

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
                    label="💾 Download Image",
                    data=file,
                    file_name=Path(st.session_state.image_path).name,
                    mime="image/png",
                    use_container_width=True
                )


def main():
    """Main application function."""
    initialize_session_state()
    display_header()

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
