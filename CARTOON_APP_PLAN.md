# 🎨 Cartoon-of-the-Day App Plan

## Overview
A Streamlit application that generates daily cartoon concepts based on local news from the user's location using Google Gemini's all-in-one AI capabilities.

## 🎯 Core Features

### MVP Features
1. **Location Detection**: Automatically detect user's city/region from browser
2. **Local News Fetching**: Retrieve 3-5 current news headlines from user's location
3. **Topic Selection**: AI selects ONE dominant news topic
4. **Comedy Generation**: Creates 5 original cartoon concepts
5. **Ranking System**: Ranks concepts from funniest to least funny
6. **Image Generation**: Creates a cartoon image for the winner
7. **JSON Output**: Structured data output for all concepts

### Each Cartoon Concept Includes
- Title
- One-sentence premise
- Why it's funny (≤15 words)
- Ranking position
- Winner designation

## 🛠️ Technology Stack

### Primary Technology: **Google Gemini All-in-One**
- **Gemini 2.5 Pro**: Text generation with web grounding for news
- **Gemini 2.5 Flash Image**: Cartoon image generation
- **Single API**: Simplified management and deployment

### Framework & Libraries
```python
# Core
streamlit==1.32.0
google-generativeai==0.5.0  # Gemini API

# Location Detection
streamlit-js-eval==0.1.5  # Browser geolocation API
geopy==2.4.1  # Reverse geocoding
geocoder==1.38.1  # Alternative geocoding

# Utilities
python-dotenv==1.0.0  # Environment management
pytz==2024.1  # Timezone handling
Pillow==10.2.0  # Image handling
timezonefinder==6.2.0  # Timezone from coordinates

# Optional Enhancements
streamlit-lottie==0.0.5  # Animations
streamlit-extras==0.4.0  # UI components
```

## 💰 Cost Analysis

### Per Cartoon Generation
- **News Search (Grounding)**: ~$0.035
- **Comedy Concept Generation**: ~$0.05-0.10 (200-400 tokens)
- **Image Generation**: $0.039
- **Total**: ~$0.12-0.17 per cartoon

### Monthly Estimates
- **Daily Use**: $0.20-0.30/day
- **Monthly Cost**: $6-9
- **Annual Cost**: $73-110

### Free Tier Benefits
- 1,000 free images/month with Gemini
- Generous text generation quotas
- Perfect for testing and low-volume use

## 📁 Project Structure

```
cartoon-of-the-day/
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml          # API keys (local only)
├── src/
│   ├── __init__.py
│   ├── location_detector.py  # Browser geolocation & geocoding
│   ├── news_fetcher.py      # Location-based news search
│   ├── cartoon_generator.py  # Comedy concept generation
│   ├── image_generator.py    # Cartoon image creation
│   └── utils.py              # Helper functions
├── data/
│   └── cartoons/             # Saved cartoon outputs by location
├── tests/
│   └── test_app.py           # Unit tests
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── .env.example              # Environment template
├── .gitignore
└── CARTOON_APP_PLAN.md       # This file

```

## 🔧 Implementation Steps

### Phase 1: Setup & Configuration (Day 1)
- [ ] Initialize project structure
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure Streamlit settings
- [ ] Get Google AI Studio API key
- [ ] Test basic Gemini connection

### Phase 2: Core Functionality (Day 2-3)
- [ ] Implement browser geolocation detection
- [ ] Add reverse geocoding for city/region names
- [ ] Create location-based news fetcher with Gemini grounding
- [ ] Build cartoon concept generator
- [ ] Add ranking logic
- [ ] Implement JSON output structure
- [ ] Handle location fallback (IP-based if browser denied)

### Phase 3: Image Generation (Day 4)
- [ ] Integrate Gemini 2.5 Flash Image
- [ ] Create prompt optimization for cartoon style
- [ ] Add image display in Streamlit
- [ ] Implement image saving functionality

### Phase 4: UI/UX Enhancement (Day 5)
- [ ] Design clean Streamlit interface
- [ ] Add loading animations
- [ ] Create concept cards display
- [ ] Highlight winning concept
- [ ] Add refresh/regenerate buttons

### Phase 5: Testing & Deployment (Day 6-7)
- [ ] Write unit tests
- [ ] Handle API errors gracefully
- [ ] Add rate limiting
- [ ] Deploy to Streamlit Cloud
- [ ] Configure secrets management
- [ ] Monitor and optimize

## 🎨 UI Design

### Layout
```
┌─────────────────────────────────────┐
│       🎨 Cartoon of the Day         │
│      📍 [City, Country]             │
├─────────────────────────────────────┤
│   [Detect My Location] or           │
│   [Enter Location: ________]        │
│   [Generate Today's Cartoon]        │
├─────────────────────────────────────┤
│  📰 Today's Topic: [News Topic]     │
├─────────────────────────────────────┤
│  🏆 WINNER: [Cartoon Title]         │
│  ┌─────────────────────────────┐   │
│  │                               │   │
│  │    [Generated Image]          │   │
│  │                               │   │
│  └─────────────────────────────┘   │
│  Premise: [One-sentence premise]    │
│  Why funny: [Explanation]           │
├─────────────────────────────────────┤
│  📊 All Concepts (Ranked)           │
│  1. [Title] - [Premise]             │
│  2. [Title] - [Premise]             │
│  3. [Title] - [Premise]             │
│  4. [Title] - [Premise]             │
│  5. [Title] - [Premise]             │
├─────────────────────────────────────┤
│  [Save] [Share] [New Cartoon]       │
└─────────────────────────────────────┘
```

## 📝 Sample Code Implementation

### Main App Structure (app.py)
```python
import streamlit as st
import google.generativeai as genai
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
from datetime import datetime
import pytz
import json
from timezonefinder import TimezoneFinder

# Configure Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🎨 Cartoon of the Day")

# Location Detection
if 'location' not in st.session_state:
    st.session_state.location = None
    st.session_state.city = None
    st.session_state.country = None

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("📍 Detect My Location"):
        # Get browser geolocation
        loc = get_geolocation()
        if loc:
            # Reverse geocode to get city name
            geolocator = Nominatim(user_agent="cartoon-app")
            location = geolocator.reverse(f"{loc['coords']['latitude']}, {loc['coords']['longitude']}")

            st.session_state.location = location.address
            st.session_state.city = location.raw['address'].get('city',
                                     location.raw['address'].get('town',
                                     location.raw['address'].get('village', 'Unknown')))
            st.session_state.country = location.raw['address'].get('country', 'Unknown')

with col2:
    manual_location = st.text_input("Or enter a location:",
                                   placeholder="e.g., Paris, France")
    if manual_location:
        st.session_state.city = manual_location.split(',')[0].strip()
        st.session_state.location = manual_location

# Display detected/entered location
if st.session_state.city:
    st.info(f"📍 Location: **{st.session_state.city}**")

# Get local timezone
if st.session_state.location:
    tf = TimezoneFinder()
    if 'latitude' in locals():
        timezone_str = tf.timezone_at(lat=loc['coords']['latitude'],
                                     lng=loc['coords']['longitude'])
    else:
        timezone_str = 'UTC'  # Fallback for manual entry

    local_tz = pytz.timezone(timezone_str or 'UTC')
    today = datetime.now(local_tz).strftime('%Y-%m-%d')

    if st.button("Generate Today's Cartoon", type="primary"):
        with st.spinner(f"Finding {st.session_state.city} news..."):
            # 1. Search for local news with grounding
            model = genai.GenerativeModel(
                'gemini-2.5-pro',
                tools=['google_search_retrieval']
            )

            news_prompt = f"""
            Find 3-5 major news headlines from {st.session_state.city}, {st.session_state.country}
            from today {today}. Focus on local stories specific to this location.
            """
            news = model.generate_content(news_prompt)

        with st.spinner("Creating comedy concepts..."):
            # 2. Generate cartoon concepts
            cartoon_prompt = f"""
            You are a comedy writer in {st.session_state.city}. Today is {today}.
            Based on these local news: {news.text}

            Pick ONE dominant topic and produce exactly 5 cartoon concepts.

            Return JSON only:
            {{
              "topic": "<dominant news topic>",
              "location": "{st.session_state.city}",
              "ideas": [
                {{"title": "...", "premise": "...", "why_funny": "..."}},
                ...
              ],
              "ranking": ["<title #1>", "<title #2>", ...],
              "winner": "<title #1>"
            }}
            """

            response = model.generate_content(cartoon_prompt)
            cartoon_data = json.loads(response.text)

        # 3. Generate image for winner
        with st.spinner("Drawing cartoon..."):
            image_model = genai.ImageGenerationModel('gemini-2.5-flash-image')
            winner = cartoon_data['winner']
            winner_premise = next(
                idea['premise']
                for idea in cartoon_data['ideas']
                if idea['title'] == winner
            )

            image_prompt = f"""
            Create a funny cartoon strip about: {winner_premise}
            Setting: {st.session_state.city}
            Style: Clean, colorful, newspaper comic strip
            """
            image = image_model.generate_images(image_prompt)[0]

        # 4. Display results
        st.success(f"Cartoon generated for {st.session_state.city}!")
        st.image(image.image)
        st.write(f"**{winner}**")
        st.write(winner_premise)

        # Show all concepts
        with st.expander("All Concepts (Ranked)"):
            for i, title in enumerate(cartoon_data['ranking'], 1):
                concept = next(
                    idea for idea in cartoon_data['ideas']
                    if idea['title'] == title
                )
                st.write(f"{i}. **{title}**")
                st.write(f"   {concept['premise']}")
                st.write(f"   *Why: {concept['why_funny']}*")
else:
    st.info("👆 Please detect or enter your location to generate local cartoons")
```

## 🚀 Deployment to Streamlit Cloud

### Prerequisites
1. GitHub repository with the code
2. Streamlit Cloud account (free)
3. Google AI Studio API key

### Steps
1. Push code to GitHub
2. Connect repo to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here"
   ```
4. Deploy and monitor

## 🔒 Security Considerations

- **API Key Management**: Use Streamlit secrets, never commit keys
- **Rate Limiting**: Implement daily limits to control costs
- **Error Handling**: Graceful fallbacks for API failures
- **Content Filtering**: Consider adding safety checks for generated content
- **Data Privacy**: Don't store personal data or API responses

## 🎯 Success Metrics

- **Performance**: < 30 seconds total generation time
- **Quality**: 80%+ user satisfaction with humor
- **Reliability**: 99% uptime
- **Cost**: Stay under $10/month
- **Usage**: Track daily active users

## 🔄 Future Enhancements

### Phase 2 Features
- User voting on funniest concepts
- Archive of past cartoons by location
- Social media sharing with location tags
- Multiple art styles
- User-submitted news topics
- Popular locations leaderboard
- Save favorite locations

### Phase 3 Features
- Animated cartoons
- Voice narration
- Multi-panel comic strips
- Personalization based on humor preferences
- API for other applications
- Global news comparison (multiple cities)
- Location-specific humor styles

## 📚 Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Deployment](https://streamlit.io/cloud)

## ⏰ Timeline

- **Week 1**: MVP development and testing
- **Week 2**: UI polish and deployment
- **Week 3**: User feedback and iteration
- **Month 2**: Feature enhancements based on usage

## 📧 Contact & Support

- Project Lead: [Your Name]
- Repository: [GitHub URL]
- Live App: [Streamlit Cloud URL]

---

*Last Updated: November 2025*