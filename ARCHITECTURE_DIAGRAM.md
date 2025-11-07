# Cartoon-of-the-Day: Architecture Diagrams

## 1. 4-Stage Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT APP (app.py)                      │
│                     Session State + UI Rendering                    │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                ┌─────────▼─────────┐
                │  LOCATION DETECTION  │
                │                      │
                │ LocationDetector     │
                │ ✓ Manual Entry       │
                │ ✓ Browser GPS        │
                │ ✓ IP Fallback        │
                │ ✓ Reverse Geocoding  │
                │                      │
                │ Output:              │
                │ • Lat/Lon            │
                │ • City/Country       │
                │ • Timezone           │
                └─────────┬────────────┘
                          │
                ┌─────────▼────────┐
                │  NEWS FETCHING   │
                │                  │
                │  NewsFetcher     │
                │  ✓ NewsAPI.org   │
                │  ✓ Location      │
                │    Filtering     │
                │  ✓ Fictional     │
                │    Fallback      │
                │                  │
                │  Output:         │
                │  • 5 Headlines   │
                │  • Dominant      │
                │    Topic         │
                │  • Summary       │
                └─────────┬────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │  CONCEPT GENERATION               │
        │                                    │
        │  CartoonGenerator                 │
        │  (Gemini 2.0-flash-exp)          │
        │  ✓ 5 Ranked Concepts             │
        │  ✓ JSON Parsing + Auto-Fix       │
        │  ✓ Validation                    │
        │  ✓ Fallback Generation           │
        │                                    │
        │  Output:                          │
        │  • Topic                          │
        │  • 5 Ideas with:                  │
        │    - Title                        │
        │    - Premise                      │
        │    - Why Funny (≤15 words)        │
        │  • Ranking List                   │
        │  • Winner (first ranked)          │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │  IMAGE GENERATION (2-STAGE)       │
        │                                    │
        │  STAGE 1: Comic Strip Scripting   │
        │  • OpenRouter (Claude 3.5)         │
        │    OR                              │
        │  • Gemini 2.0-flash               │
        │                                    │
        │  STAGE 2: Image Generation        │
        │  • Gemini 2.5-flash-image         │
        │                                    │
        │  ImageGenerator                   │
        │  ✓ Panel Descriptions             │
        │  ✓ Character Details              │
        │  ✓ Visual Gags                    │
        │  ✓ Mark Knight Style              │
        │  ✓ Placeholder Fallback           │
        │                                    │
        │  Output:                          │
        │  • PNG Image File                 │
        │  • Saved to data/cartoons/        │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │  STORAGE + DISPLAY                │
        │                                    │
        │  save_cartoon_data() →            │
        │  {location}_{timestamp}.json      │
        │                                    │
        │  Display in Streamlit:            │
        │  ✓ Image                          │
        │  ✓ Winner Details                 │
        │  ✓ All Concepts (Expandable)      │
        │  ✓ Download Button                │
        └────────────────────────────────────┘
```

---

## 2. Streamlit Session State Flow

```
App Starts
    │
    ├─ Initialize Session State
    │  ├─ location_data: None
    │  ├─ address_data: None
    │  ├─ news_data: None
    │  ├─ cartoon_data: None
    │  ├─ image_path: None
    │  ├─ show_manual_entry: False
    │  └─ generating: False
    │
    ├─ Display Header + Progress Indicator
    │
    ├─ Render State A (No Location) ─────────┐
    │  ├─ "Detect Location" Button           │
    │  └─ "Enter Manually" Button            │
    │                                         │
    ├─ → User Clicks Button ────────────────▶│
    │                                        │
    ├─ Render State B (Manual Entry) ◀──────┘
    │  ├─ Show Input Field
    │  ├─ Quick Suggestions
    │  ├─ Cancel | Use This Location
    │  │
    │  └─ → User Submits
    │      │
    │      ▼
    │  Location Processing
    │  └─ parse_manual_location()
    │  └─ reverse_geocode()
    │  └─ Store in session_state
    │  └─ st.rerun()
    │
    ├─ Render State C (Location Set)
    │  ├─ Success Message
    │  ├─ "Change Location" Button
    │  └─ "Generate Cartoon" Button
    │
    ├─ → User Clicks Generate ─────────────┐
    │                                       │
    ├─ Render State D (Generating) ◀──────┘
    │  ├─ Progress Bar (0% → 100%)
    │  ├─ Status Updates:
    │  │  - "Finding local news..." (10%)
    │  │  - "Creating concepts..." (60%)
    │  │  - "Drawing cartoon..." (90%)
    │  │  - "Complete!" (100%)
    │  │
    │  └─ Background Execution:
    │     ├─ fetch_and_summarize()
    │     │  └─ Store news_data
    │     ├─ generate_concepts()
    │     │  └─ Store cartoon_data
    │     ├─ generate_and_save()
    │     │  └─ Store image_path
    │     └─ save_cartoon_data()
    │
    ├─ Render State E (Results)
    │  ├─ Display Image
    │  ├─ Topic Headline
    │  ├─ Winner Details:
    │  │  ├─ Title
    │  │  ├─ Premise
    │  │  └─ Why Funny
    │  ├─ Expandable All Concepts
    │  └─ Action Buttons:
    │     ├─ New Cartoon (reset news/cartoon/image)
    │     ├─ Change Location (reset all)
    │     └─ Download (save PNG)
    │
    └─ Loop: User can restart from any state
```

---

## 3. Data Structure Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                  CARTOON_DATA (JSON on disk)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  {                                                              │
│    "topic": "Local Politics",                                   │
│    "location": "Melbourne, Australia",                          │
│    "ideas": [                                                   │
│      {                                                          │
│        "title": "Politicians Debate Weather",                   │
│        "premise": "City council argues about temperature",      │
│        "why_funny": "They can't agree on anything"             │
│      },                                                         │
│      ... (4 more ideas)                                         │
│    ],                                                           │
│    "ranking": ["Title 1", "Title 2", ..., "Title 5"],          │
│    "winner": "Title 1",                                         │
│    "metadata": {                                                │
│      "location": "Melbourne, Australia",                        │
│      "generated_at": "2025-11-04T19:54:45",                    │
│      "image_path": "data/cartoons/Melbourne_...png"            │
│    },                                                           │
│    "news_data": {                                               │
│      "headlines": [                                             │
│        {                                                        │
│          "title": "Melbourne City Council Votes...",            │
│          "summary": "Council passes new initiative...",         │
│          "url": "https://...",                                  │
│          "source": "Herald"                                     │
│        },                                                       │
│        ... (4 more)                                             │
│      ],                                                         │
│      "dominant_topic": "Local Politics",                        │
│      "summary": "Five headlines about local news",              │
│      "source": "NewsAPI",                                       │
│      "date": "2025-11-04",                                      │
│      "location": "Melbourne, Australia"                         │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Dependency Graph

```
                          ┌──────────────┐
                          │   app.py     │
                          │  (Main UI)   │
                          └──────┬───────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
        ┌────────▼────────┐      │      ┌────────▼────────┐
        │LocationDetector │      │      │  CartoonGenerator│
        │                 │      │      │                  │
        │ Dependencies:   │      │      │ Dependencies:    │
        │ • geopy         │      │      │ • google-genai   │
        │ • geocoder      │      │      │ • utils.py       │
        │ • streamlit-js  │      │      │ • json, re       │
        │ • timezonefinder│      │      └──────────────────┘
        └────────────────┘       │
                                 │
        ┌────────▼────────┐      │      ┌─────────▼───────────┐
        │   NewsFetcher   │      │      │  ImageGenerator(s)  │
        │                 │      │      │  (2 versions)       │
        │ Dependencies:   │      │      │                      │
        │ • requests      │      │      │ Dependencies:        │
        │ • NewsAPI       │      │      │ • google-genai       │
        │ • utils.py      │      │      │ • Pillow             │
        └────────────────┘       │      │ • openrouter (opt)   │
                                 │      │ • utils.py           │
                                 │      └──────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   utils.py      │
                        │                 │
                        │ • get_api_key() │
                        │ • validate_*()  │
                        │ • save_*()      │
                        │ • sanitize_*()  │
                        │ • format_*()    │
                        └─────────────────┘

KEY PATTERNS:
• All components → utils.py for shared functions
• LocationDetector is standalone
• NewsFetcher and CartoonGenerator are sequential
• ImageGenerator (2 versions) is final stage
• All error handling → Streamlit warnings + fallbacks
• All data → JSON serialization in data/cartoons/
```

---

## 5. Error Handling & Fallback Strategy

```
┌──────────────────────────────────────────┐
│     LOCATION DETECTION FALLBACK           │
├──────────────────────────────────────────┤
│                                          │
│  1. Manual Input? → parse_manual()       │
│     ❌ No                                │
│         ↓                                │
│  2. Browser GPS? → get_browser()         │
│     ❌ Not HTTPS/Denied/Unavailable     │
│         ↓                                │
│  3. IP Location? → get_ip_location()    │
│     ❌ Still Failed                     │
│         ↓                                │
│  ✓ User must enter manually             │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│      NEWS FETCHING FALLBACK              │
├──────────────────────────────────────────┤
│                                          │
│  1. NewsAPI Key Set?                     │
│     ❌ No or API Fails                   │
│         ↓                                │
│  2. Generate Fictional News              │
│     • Realistic headlines template      │
│     • Location-aware content            │
│     • Show warning to user              │
│     ✓ App continues seamlessly          │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│   CARTOON GENERATION FALLBACK            │
├──────────────────────────────────────────┤
│                                          │
│  1. Generate JSON from Gemini            │
│     ❌ Parse fails                       │
│         ↓                                │
│  2. Auto-fix structure:                  │
│     • Pad to 5 ideas if needed          │
│     • Fix title/premise/why_funny       │
│     • Create ranking from ideas         │
│     ✓ Continue with fixed data          │
│         ❌ Still invalid                │
│         ↓                                │
│  3. Use fallback concepts:               │
│     • "News Update: {topic}"            │
│     • Generic but functional            │
│     ✓ App always returns valid JSON     │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│      IMAGE GENERATION FALLBACK           │
├──────────────────────────────────────────┤
│                                          │
│  1. Generate Image from Gemini           │
│     ❌ Generation Fails                  │
│         ↓                                │
│  2. Create Placeholder:                  │
│     • White background                  │
│     • Title + Premise text              │
│     • "Coming Soon" message             │
│     ✓ Valid PNG file saved              │
│     ✓ Same interface as real image      │
└──────────────────────────────────────────┘
```

---

## 6. File Organization & Data Storage

```
cartoon-of-the-day/
│
├── 📄 app.py
│   └─ 550 lines
│   └─ Main Streamlit entry point
│   └─ Session state management
│   └─ UI rendering (5 states)
│
├── 📁 src/
│   ├── 📄 location_detector.py (248 lines)
│   │   └─ LocationDetector class
│   │   └─ 3-tier fallback strategy
│   │
│   ├── 📄 news_fetcher.py (299 lines)
│   │   └─ NewsFetcher class
│   │   └─ NewsAPI integration + fallback
│   │
│   ├── 📄 cartoon_generator.py (330 lines)
│   │   └─ CartoonGenerator class
│   │   └─ Gemini 2.0-flash-exp
│   │
│   ├── 📄 image_generator.py (382 lines)
│   │   └─ Standard ImageGenerator
│   │   └─ Gemini 2.0-flash + 2.5-flash-image
│   │
│   ├── 📄 image_generator_openrouter.py (459 lines)
│   │   └─ Enhanced ImageGenerator
│   │   └─ Claude 3.5 Sonnet + Gemini
│   │
│   └── 📄 utils.py (187 lines)
│       └─ Shared utilities
│       └─ API key management
│       └─ Validation functions
│
├── 📁 tests/
│   ├── 📄 test_app.py (170 lines)
│   ├── 📄 test_cartoon_generator.py (333 lines)
│   ├── 📄 test_image_generator.py (336 lines)
│   ├── 📄 test_location_detector.py (305 lines)
│   ├── 📄 test_news_fetcher.py (301 lines)
│   └── 📄 test_utils.py (224 lines)
│   └─ Total: 1,669 lines, 89% coverage
│
├── 📁 data/cartoons/
│   ├── Melbourne_Australia_20251104_195445.json
│   ├── Melbourne_Australia_20251104_195445.png
│   ├── New_York_United_States_20251103_215119.json
│   ├── New_York_United_States_20251103_215119.png
│   └── ... (multiple location/date combinations)
│
├── 📁 .streamlit/
│   ├── 📄 config.toml (Theme & server settings)
│   └── 📄 secrets.toml (Deployment API keys)
│
├── 📄 .env (Local dev secrets - not committed)
├── 📄 requirements.txt (28 packages)
├── 📄 README.md (User documentation)
├── 📄 DEPLOYMENT.md (Production setup)
└── 📄 CLAUDE.md (Development guide)

NAMING CONVENTION:
├── Saved JSON: {sanitized_location}_{YYYYMMDD_HHMMSS}.json
└── Saved PNG:  {sanitized_location}_{YYYYMMDD_HHMMSS}.png

EXAMPLE:
├── Melbourne_Australia_20251104_195445.json
└── Melbourne_Australia_20251104_195445.png
    (Both created at same time, same location)
```

---

## 7. API Integration Points

```
┌─────────────────────────────────────────────────────┐
│                  EXTERNAL APIs                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. GOOGLE GEMINI (REQUIRED)                        │
│     ├─ gemini-2.0-flash-exp → Concept generation  │
│     ├─ gemini-2.5-flash-image → Image generation  │
│     ├─ Config: google-generativeai library        │
│     └─ Key: GOOGLE_API_KEY                        │
│                                                    │
│  2. NEWSAPI.ORG (OPTIONAL)                          │
│     ├─ /v2/everything endpoint                     │
│     ├─ Query: "{city} {country}"                   │
│     ├─ Time window: 24 hours                       │
│     ├─ Fallback: Fictional news if unavailable    │
│     └─ Key: NEWSAPI_KEY                           │
│                                                    │
│  3. OPENROUTER (OPTIONAL - FOR ENHANCED SCRIPTS)   │
│     ├─ Model: anthropic/claude-3.5-sonnet:beta   │
│     ├─ Purpose: Superior comic strip scripting    │
│     ├─ Fallback: Gemini 2.0-flash if unavailable │
│     └─ Key: OPENROUTER_API_KEY                    │
│                                                    │
│  4. GEOLOCATION SERVICES                           │
│     ├─ Browser Geolocation API (via streamlit-js) │
│     ├─ IP Geolocation (geocoder library)          │
│     ├─ Nominatim (geopy) → Reverse geocoding      │
│     └─ No API keys required                       │
│                                                    │
└─────────────────────────────────────────────────────┘
```

---

## 8. Development vs. Production Configuration

```
┌──────────────────────────────────────────────────────┐
│          LOCAL DEVELOPMENT (.env file)              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  GOOGLE_API_KEY=AIzaSyB3vVvIu...                   │
│  NEWSAPI_KEY=68ffd07cc1fd...                       │
│  OPENROUTER_API_KEY=sk-or-v1-a786...              │
│                                                     │
│  ✓ Loads via python-dotenv in app.py             │
│  ✓ Not committed to git (.gitignore)              │
│  ✓ Accessible via os.getenv()                     │
│                                                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│      STREAMLIT CLOUD (.streamlit/secrets.toml)      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [secrets]                                          │
│  GOOGLE_API_KEY = "AIzaSyB3vVvIu..."              │
│  NEWSAPI_KEY = "68ffd07cc1fd..."                  │
│  OPENROUTER_API_KEY = "sk-or-v1-a786..."          │
│                                                     │
│  ✓ Set via Streamlit Cloud dashboard              │
│  ✓ Accessed via st.secrets dict                    │
│  ✓ Never exposed in logs                          │
│                                                     │
└──────────────────────────────────────────────────────┘

API KEY LOOKUP PRIORITY (in utils.get_api_key()):
1. st.secrets["GOOGLE_API_KEY"] (Streamlit Cloud)
2. os.getenv("GOOGLE_API_KEY") (Local .env)
3. Raise ValueError if not found
```

---

This architecture provides robust error handling, intelligent fallbacks, and a clean separation of concerns across all components.
