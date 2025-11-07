# Cartoon-of-the-Day: Complete Codebase Architecture Analysis

## Project Overview

**Cartoon of the Day** is a Streamlit application that generates AI-powered cartoon concepts based on local news headlines. The application combines location detection, news fetching, AI concept generation, and image generation into a seamless multi-step workflow.

- **Total Codebase**: ~3,570 lines (1,900 source + 1,670 tests)
- **Python Version**: 3.10+
- **Main Framework**: Streamlit 1.32.0+
- **Primary AI Model**: Google Gemini (2.0-flash-exp for concepts, 2.5-flash-image for images)
- **Current Branch**: master
- **Test Coverage**: 89% (88 tests passing)

---

## Core Architecture: Pipeline Design

The application follows a **4-stage pipeline architecture** with fallbacks at each stage:

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: LOCATION DETECTION (LocationDetector)                 │
│ Priority: Manual Input > Browser GPS > IP-Based Geolocation    │
│ Output: (coordinates dict, address dict)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ STAGE 2: NEWS FETCHING (NewsFetcher)                           │
│ Primary: NewsAPI.org with location-based filtering             │
│ Fallback: Fictional but realistic news                         │
│ Output: {headlines, dominant_topic, summary, source}           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ STAGE 3: CONCEPT GENERATION (CartoonGenerator)                 │
│ Model: Gemini 2.0-flash-exp                                    │
│ Output: 5 ranked concepts with validation/auto-fix             │
│ Structure: {topic, location, ideas[], ranking[], winner}       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│ STAGE 4: IMAGE GENERATION (ImageGenerator)                     │
│ Two-step: Comic script (Gemini 2.0-flash or OpenRouter)        │
│         + Image generation (Gemini 2.5-flash-image)            │
│ Fallback: Placeholder image with text                          │
│ Output: PNG file saved to data/cartoons/                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
cartoon-of-the-day/
├── app.py                          # Main Streamlit application (550 lines)
├── src/                            # Core modules (1,905 lines total)
│   ├── __init__.py
│   ├── location_detector.py         # 248 lines - 3-tier location detection
│   ├── news_fetcher.py              # 299 lines - NewsAPI integration + fallback
│   ├── cartoon_generator.py         # 330 lines - Gemini concept generation
│   ├── image_generator.py           # 382 lines - Standard image generation
│   ├── image_generator_openrouter.py # 459 lines - OpenRouter-enhanced version
│   └── utils.py                     # 187 lines - Shared utilities
├── tests/                           # Unit tests (1,669 lines total)
│   ├── __init__.py
│   ├── test_app.py                  # 170 lines
│   ├── test_cartoon_generator.py    # 333 lines
│   ├── test_image_generator.py      # 336 lines
│   ├── test_location_detector.py    # 305 lines
│   ├── test_news_fetcher.py         # 301 lines
│   └── test_utils.py                # 224 lines
├── data/cartoons/                   # Generated output (JSON + PNG files)
├── .streamlit/                      # Streamlit configuration
│   ├── config.toml                  # Theme & server settings
│   └── secrets.toml                 # Deployment secrets
├── .env                             # Local development secrets (not committed)
├── requirements.txt                 # Dependencies (28 packages)
└── README.md, CLAUDE.md, DEPLOYMENT.md  # Documentation
```

---

## Component Deep Dive

### 1. LocationDetector (src/location_detector.py)

**Purpose**: Determine user location with intelligent fallback strategy

**Key Methods**:
- `get_location_with_fallback(manual_location?)` - Main entry point with 3-tier fallback
- `get_browser_location()` - Uses streamlit-js-eval for GPS access
- `get_ip_location()` - Fallback using geocoder library
- `parse_manual_location(location_str)` - User-entered location via Nominatim
- `reverse_geocode(lat, lon)` - Convert coordinates to city/country using Nominatim

**Data Structures**:
```python
# Coordinates Dict
{
    'latitude': float,
    'longitude': float,
    'accuracy': float,  # optional
    'source': 'browser' | 'ip' | 'manual'
}

# Address Dict
{
    'city': str,
    'state': str,
    'country': str,
    'country_code': str,
    'full_address': str
}
```

**Priority Strategy**:
1. Manual location input (if provided) + reverse geocode
2. Browser geolocation (requires HTTPS) + reverse geocode
3. IP-based geolocation (fallback, may lack reverse geocoding)

**Dependencies**: 
- geopy.Nominatim for geocoding
- geocoder for IP location
- streamlit-js-eval for browser GPS
- timezonefinder for timezone detection

---

### 2. NewsFetcher (src/news_fetcher.py)

**Purpose**: Fetch local news headlines and identify dominant topic

**Key Methods**:
- `fetch_and_summarize(city, country, date?)` - Main entry point
- `fetch_local_news(city, country, date?, num_headlines?)` - Fetch with fallback
- `_fetch_from_newsapi()` - Real NewsAPI integration
- `_get_fictional_news()` - Fallback generator
- `select_dominant_topic()` - Extract primary topic from headlines

**API Integration**:
- **Primary**: NewsAPI.org `/v2/everything` endpoint
- **Query Building**: `"{city} {country}"` with 24-hour window
- **Filtering Logic**: 
  - Prioritizes articles with city name in title (strong signal)
  - Secondary: city in description (100+ chars)
  - Combines: title matches + description matches
  - Fetches 3x headlines needed, filters to 5
- **Fallback**: Generates 5 realistic news headlines locally

**NewsAPI Country Codes**:
```python
{"USA": "us", "UK": "gb", "Australia": "au", "Japan": "jp", 
 "France": "fr", "Germany": "de", "Canada": "ca", "India": "in", "Brazil": "br"}
```

**Output Structure**:
```python
{
    'news_data': {headlines, date, location, source},
    'dominant_topic': str,
    'summary': str,
    'location': str,
    'date': str
}
```

**Configuration**:
- Requires `NEWSAPI_KEY` environment variable
- Falls back gracefully to fictional news if key missing or API fails
- Warning displayed in UI when using fallback

---

### 3. CartoonGenerator (src/cartoon_generator.py)

**Purpose**: Generate 5 ranked cartoon concepts from news topic

**Key Methods**:
- `generate_concepts(topic, location, news_context?)` - Main entry point
- `_build_generation_prompt()` - Constructs detailed prompt
- `_parse_response()` - Extracts JSON from API response
- `_fix_cartoon_data()` - Auto-fixes malformed responses
- `_create_fallback_response()` - Fallback if generation fails
- `get_winner()` - Extract winning concept
- `rank_concepts()` - Return concepts in ranked order

**Model**: `gemini-2.0-flash-exp` (latest best model for creative generation)

**Prompt Strategy**:
- Explicitly requests exactly 5 concepts
- Specifies ranking order (funniest to least funny)
- Constraints: max 15 words for "why_funny"
- Requests location-specific humor
- Demands ONLY JSON output (no markdown)
- Includes optional news context section

**Output Structure**:
```python
{
    'topic': str,
    'location': str,
    'ideas': [
        {
            'title': str,
            'premise': str,  # 1 sentence
            'why_funny': str  # ≤15 words
        },
        # ... 4 more
    ],
    'ranking': [str, str, str, str, str],  # titles in order
    'winner': str  # first in ranking
}
```

**Error Handling**:
1. Attempts JSON parsing with markdown cleanup
2. Regex search for JSON object if full parse fails
3. Validates structure with `validate_cartoon_data()`
4. Auto-fixes if invalid (pads to 5 ideas, ensures ranking)
5. Falls back to generated placeholder concepts

**Validation**: Must have exactly 5 ideas with title/premise/why_funny

---

### 4. ImageGenerator (src/image_generator.py) & ImageGenerator-OpenRouter (src/image_generator_openrouter.py)

**Purpose**: Generate or script comic strip images

**Two Implementations Available**:

#### Standard Version (image_generator.py)
- Uses Gemini 2.0-flash for text scripting
- Uses Gemini 2.5-flash-image for image generation
- Auto-imports if OpenRouter unavailable

#### OpenRouter-Enhanced Version (image_generator_openrouter.py)
- Uses Claude 3.5 Sonnet (OpenRouter) for superior scripting
- Uses Gemini 2.5-flash-image for image generation
- Falls back to Gemini if OpenRouter key missing
- Attempts auto-import first (app.py tries this first)

**Key Methods**:
- `script_comic_strip()` - Generate detailed panel descriptions
- `generate_cartoon_image()` - Create image from script
- `_build_image_prompt()` - Construct image generation prompt
- `create_placeholder_image()` - Fallback visual
- `save_image()` - Persist to PNG
- `generate_and_save()` - Complete pipeline

**Comic Strip Script Format**:
```
1. Panel descriptions (visual appearance)
2. Character positions and expressions
3. Dialogue/speech bubbles
4. Visual gags and details
5. Color notes and emphasis
6. Key visual elements
```

**Mark Knight Style Influence**:
- Sharp, precise line art
- Professional newspaper quality
- Expressive, well-defined characters
- Clever visual humor
- Clear visual storytelling
- Bright, vibrant colors
- Editorial cartoon aesthetics

**Placeholder Image**:
- Created with PIL if generation fails
- White background with border
- Title and premise text
- "Coming Soon" message
- Returns valid PNG path

**Output**: 
- Filename: `{sanitized_location}_{YYYYMMDD_HHMMSS}.png`
- Location: `data/cartoons/`
- Format: PNG with quality 95

---

### 5. Utils (src/utils.py)

**Purpose**: Shared utility functions

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `get_api_key()` | Fetch GOOGLE_API_KEY from secrets or env |
| `save_cartoon_data()` | Save cartoon JSON with metadata to file |
| `get_local_time(lat, lon)` | Get timezone-aware local time |
| `format_date_for_location()` | Human-readable date for location |
| `sanitize_filename()` | Remove invalid filename characters |
| `validate_location_data()` | Check location dict structure |
| `validate_cartoon_data()` | Check cartoon dict structure |

**API Key Lookup Order**:
1. `st.secrets["GOOGLE_API_KEY"]` (Streamlit deployment)
2. `os.getenv("GOOGLE_API_KEY")` (local .env file)
3. Raises ValueError if not found

**Saved Data Structure**:
```python
{
    'topic': str,
    'location': str,
    'ideas': [...],
    'ranking': [...],
    'winner': str,
    'metadata': {
        'location': str,
        'generated_at': ISO timestamp,
        'image_path': str
    },
    'news_data': {
        'headlines': [...],
        'dominant_topic': str,
        'summary': str,
        'source': str,
        'date': str
    }
}
```

---

## Streamlit App Flow (app.py)

**State Management**: Session state controls workflow progression

```python
st.session_state keys:
├── location_data: Dict[str, Any] | None
├── address_data: Dict[str, str] | None
├── news_data: Dict[str, Any] | None
├── cartoon_data: Dict[str, Any] | None
├── image_path: str | None
├── show_manual_entry: bool
└── generating: bool
```

**UI States** (5 mutually exclusive renders):

1. **State A - No Location** (empty)
   - Title: "Get Your Daily Cartoon!"
   - Buttons: "Detect My Location" | "Enter Location Manually"

2. **State B - Manual Entry Shown**
   - Quick suggestions: London, NYC, Tokyo, Sydney
   - Text input field
   - Buttons: Cancel | Use This Location

3. **State C - Location Set** (but no cartoon)
   - Success message: "📍 Location set: {city}, {country}"
   - Buttons: Change Location | Generate Today's Cartoon
   - Progress shows: Step 1 ✓, Step 2 active

4. **State D - Generating** (spinner + progress bar)
   - Shows: "Finding local news..." → "Creating concepts..." → "Drawing cartoon..."
   - Progress increments: 10% → 30% → 60% → 90% → 100%

5. **State E - Cartoon Results**
   - Displays: Topic, Winner cartoon image, Title, Premise, Why Funny
   - Expandable "See All Concepts" section
   - Buttons: New Cartoon | Change Location | Download

**Progress Indicator UI**:
- Step 1: "Set Location" (pending/active/completed)
- Step 2: "View Cartoon" (pending/active/completed)
- Visual: Circle icons with status colors (purple/green)

**CSS Styling**:
- 900px max-width centered layout
- Gradient purple-to-pink theme
- Custom button styles with hover effects
- Input field focus states
- Success message styling
- Responsive media query for mobile

**Event Handlers**:
- `detect_location()` - Browser GPS + fallback
- `process_location(location_text)` - Manual input parsing
- `generate_cartoon()` - 4-stage pipeline execution

---

## Dependencies & Configuration

### Core Dependencies (requirements.txt)

**AI & APIs**:
- `google-generativeai>=0.5.0` - Gemini API
- `requests>=2.31.0` - HTTP requests for NewsAPI

**Location**:
- `streamlit-js-eval>=0.1.5` - Browser geolocation
- `geopy>=2.4.1` - Geocoding (Nominatim)
- `geocoder>=1.38.1` - IP-based geolocation
- `timezonefinder>=6.2.0` - Timezone detection
- `pytz>=2024.1` - Timezone handling

**Utilities**:
- `streamlit>=1.32.0` - Web framework
- `python-dotenv>=1.0.0` - .env file loading
- `Pillow>=10.3.0` - Image processing

**Testing**:
- `pytest>=8.0.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.12.0` - Mocking utilities

**Code Quality**:
- `black>=24.1.0` - Code formatter
- `pylint>=3.0.3` - Linter (requires ≥8 score)
- `flake8>=7.0.0` - Style checker (max 100 chars)
- `mypy>=1.8.0` - Type checking

### Configuration Files

**`.streamlit/config.toml`**:
```toml
[theme]
primaryColor = "#FF6B6B"      # Red accent
backgroundColor = "#FFFFFF"   # White background
secondaryBackgroundColor = "#F0F2F6"  # Light gray
textColor = "#262730"         # Dark text
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

**`.env` (local development)**:
```
GOOGLE_API_KEY=your-key-here
NEWSAPI_KEY=your-key-here (optional)
OPENROUTER_API_KEY=your-key-here (optional for enhanced image scripting)
```

**`.streamlit/secrets.toml` (production)**:
```toml
GOOGLE_API_KEY = "your-key-here"
```

---

## Testing Patterns & Coverage

**Test Organization**:
- Mirrors source structure (test_* files match src/* modules)
- Class-based tests matching source classes
- Extensive mocking of external APIs
- Coverage: 89% (88 tests passing)

**Test Structure Example** (test_cartoon_generator.py):
```python
class TestCartoonGenerator:
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_generate_concepts_success(self, mock_model_class):
        """Test successful concept generation"""
        # Setup mock response
        mock_response.text = json.dumps(valid_cartoon_data)
        # Execute
        result = generator.generate_concepts(topic, location)
        # Assert
        assert result['winner'] == expected_title
```

**Mocking Strategy**:
- `@patch` decorators for external libraries (genai, requests)
- MagicMock for API responses
- Fixtures in individual test files
- No integration tests (all external APIs mocked)

**Key Test Files**:
| File | Lines | Focus |
|------|-------|-------|
| test_app.py | 170 | App structure, session state |
| test_cartoon_generator.py | 333 | Concept generation, JSON parsing, validation |
| test_image_generator.py | 336 | Image generation, placeholders, file I/O |
| test_location_detector.py | 305 | 3-tier fallback, geocoding |
| test_news_fetcher.py | 301 | NewsAPI integration, filtering, fallback |
| test_utils.py | 224 | Validation, file operations, timezone |

---

## Data Flow & State Persistence

### User Journey
```
1. App starts → Initialize session state (all None)
2. Display progress (Step 1 pending)
3. User clicks "Detect Location" or enters manually
4. LocationDetector.get_location_with_fallback()
   └─ Store coords + address in session state
5. Progress updates to Step 1 ✓, Step 2 active
6. User clicks "Generate Cartoon"
7. Generate workflow:
   a. NewsFetcher.fetch_and_summarize() → store news_data
   b. CartoonGenerator.generate_concepts() → store cartoon_data
   c. ImageGenerator.generate_and_save() → store image_path
8. Save all data to data/cartoons/{location}_{timestamp}.json
9. Display results with download option
10. User can "New Cartoon" (reset news/cartoon/image) or "Change Location"
```

### File Storage
```
data/cartoons/
├── Melbourne_Australia_20251104_195445.json
├── Melbourne_Australia_20251104_195445.png
├── New_York_United_States_20251103_215119.json
├── New_York_United_States_20251103_215119.png
└── ... (many more)
```

JSON file includes:
- Cartoon concepts (ideas, ranking, winner)
- News data (headlines, dominant_topic, source)
- Metadata (location, generated_at, image_path)

---

## Special Patterns & Conventions

### Error Handling Pattern
All main classes follow consistent pattern:
```python
try:
    # Attempt primary operation
    response = api.call()
except Exception as e:
    # Display warning in Streamlit
    st.warning(f"Error: {e}")
    # Return fallback response
    return fallback_data()
```

### Response Validation
- CartoonGenerator validates structure and auto-fixes
- ImageGenerator creates placeholder if generation fails
- NewsFetcher uses fictional news as fallback

### Filename Sanitization
```python
# Remove non-alphanumeric except space, dash, underscore
valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
sanitized = ''.join(c for c in filename if c in valid_chars)
sanitized = sanitized.replace(' ', '_')  # Replace spaces with underscores
```

### JSON Parsing Robustness
1. Strip markdown code blocks
2. Regex search for JSON object
3. Try to parse JSON
4. If fails, call auto-fix method
5. Return fallback if all fails

---

## Deployment & Configuration

### Streamlit Cloud
1. Push to GitHub
2. Connect at share.streamlit.io
3. Add secrets in dashboard:
   - `GOOGLE_API_KEY` (required)
   - `NEWSAPI_KEY` (optional, for real news)
4. App available at `https://username-cartoon-of-the-day.streamlit.app`

### Cost Estimates
- Gemini 2.0-flash-exp: ~$0.05-0.10 per concept generation
- Gemini 2.5-flash-image: ~$0.039 per image
- NewsAPI: Free tier (100 requests/day)
- **Per cartoon**: ~$0.12-0.17 total API cost

### HTTPS Requirement
- Browser geolocation requires HTTPS
- Streamlit Cloud provides HTTPS automatically
- Local development uses HTTP (geolocation unavailable, falls back to IP)

---

## Recent Development (Git History)

| Commit | Message |
|--------|---------|
| d6ac6ca | fix(models): update deprecated gemini models |
| cf97b54 | refactor: consolidate app files, upgrade Gemini models |
| e624997 | feat(ui): redesigned UI with improved UX |
| 00c2b4b | chore(config): remove .env.example |
| b3a4c6b | fix(config): load environment variables from .env |
| 7110245 | feat(ui): add visual progress indicator |
| 01b2045 | refactor(ui): make empty state compact |
| 5d70eef | feat(ui): add location confirmation card |

Latest changes focus on UI refinement and model upgrades to latest Gemini versions.

---

## Key Non-Obvious Architectural Decisions

1. **Two ImageGenerator Versions**: App tries OpenRouter-enhanced version first (superior creative writing with Claude 3.5), falls back to standard Gemini version

2. **3-Tier Location Fallback**: Manual > Browser > IP ensures users always get location even without GPS

3. **Comic Strip Scripting**: Two-stage image generation (script first, then image) ensures visual coherence instead of direct prompting

4. **Aggressive API Fallback**: NewsAPI failure instantly switches to fictional news, keeping app always functional

5. **Session State Workflow**: Streamlit's session_state enables multi-step flow without re-fetching data on each rerun

6. **JSON Auto-Fix**: CartoonGenerator validates and repairs malformed responses instead of failing, improving reliability

7. **Location-Aware Filtering**: NewsAPI filtering prioritizes city in title over description to reduce false positives

8. **Timezone-Aware Dates**: All timestamps converted to local timezone before storage/display for user relevance

---

## Summary Table

| Component | File | Lines | Purpose | Key Dependencies |
|-----------|------|-------|---------|------------------|
| App | app.py | 550 | Main Streamlit interface & flow | streamlit, all modules |
| Location | src/location_detector.py | 248 | 3-tier location detection | geopy, geocoder, streamlit-js-eval |
| News | src/news_fetcher.py | 299 | Headline fetching + filtering | requests, NewsAPI |
| Concepts | src/cartoon_generator.py | 330 | Concept generation + validation | google-generativeai, Gemini 2.0-flash-exp |
| Images (std) | src/image_generator.py | 382 | Image generation + scripting | google-generativeai, Gemini 2.5-flash-image |
| Images (OR) | src/image_generator_openrouter.py | 459 | Enhanced scripting with Claude 3.5 | openrouter API, Gemini 2.5-flash-image |
| Utils | src/utils.py | 187 | Shared functions | pytz, Pillow, pathlib |

This is a well-architected project with strong separation of concerns, comprehensive error handling, and pragmatic fallbacks at every stage.
