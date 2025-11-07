# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit application that generates AI-powered cartoon concepts based on local news. The app uses:
- Google News (GNews library) for real-time local news fetching
- Google Gemini 2.0-flash-exp for concept generation and ranking
- Gemini 2.5-flash-image with comic strip scripting for image generation
- Mark Knight newspaper cartoon style (expressive caricatures, exaggerated features)

## Development Commands

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the Streamlit app
streamlit run app.py

# App opens at http://localhost:8501
```

### Testing
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Quick test run (no coverage)
pytest tests/ -v

# Run specific test file
pytest tests/test_cartoon_generator.py -v

# Run specific test
pytest tests/test_cartoon_generator.py::TestCartoonGenerator::test_generate_concepts_success -v
```

### Code Quality
```bash
# Linting (must pass with score >= 8)
pylint src/ --fail-under=8
flake8 src/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports

# Code formatting
black src/ --check
black src/  # to actually format
```

## Architecture

### Core Components

The application follows a pipeline architecture with four main stages:

1. **LocationDetector** ([src/location_detector.py](src/location_detector.py))
   - 3-tier location detection: Browser GPS → Manual entry → IP-based fallback
   - Reverse geocoding with geopy
   - Timezone detection using timezonefinder
   - Returns structured location data with coordinates, address, and timezone

2. **NewsFetcher** ([src/news_fetcher.py](src/news_fetcher.py))
   - Uses Google News (GNews library) for real-time local news (no API key required)
   - Location-based filtering: prioritizes title matches over description matches
   - Configurable sorting: popularity (trending) or recency (latest)
   - Falls back to fictional news if no real results found
   - Returns up to 5 headlines with dominant topic identification

3. **CartoonGenerator** ([src/cartoon_generator.py](src/cartoon_generator.py))
   - Uses Gemini 2.0-flash-exp for concept generation
   - Creates 5 ranked cartoon concepts per news topic
   - Each concept has: title, premise, why_funny (≤15 words)
   - Validates structure and auto-fixes malformed responses
   - Returns winner as first-ranked concept

4. **ImageGenerator** ([src/image_generator.py](src/image_generator.py))
   - Two-stage process: comic strip scripting → image generation
   - Scripting stage: Gemini 2.0-flash generates detailed panel descriptions grounded in actual news story
   - Image generation: Gemini 2.5-flash-image creates images from panel descriptions
   - Mark Knight style: expressive caricatures, exaggerated features, bold line work, selective color
   - Saves images as PNG to `data/cartoons/`
   - Alternative: `image_generator_openrouter.py` uses Claude 3.5 Sonnet for scripting (OpenRouter API)

### State Management

Streamlit session state manages the application flow and persists across reruns:
- `location_data`: GPS coordinates and location metadata (cached, cleared on location change)
- `address_data`: Human-readable address from reverse geocoding
- `news_data`: Headlines, topic, and date
- `cartoon_data`: Generated concepts with ranking
- `comic_script`: Multi-panel comic strip description (grounded in news story)
- `image_path`: Path to saved cartoon image

Rate limiting: 2 image generations per minute per session (in-memory storage)

### Data Flow

```
User Location → Detect Location → Fetch News → Generate Concepts → Script Comic → Generate Image
     ↓               ↓                 ↓              ↓                 ↓              ↓
Browser GPS    3-tier fallback   Google News    Gemini 2.0    Gemini 2.0-flash  Gemini 2.5
                (IP fallback)      (GNews)      (concept +     (story-grounded    (image
                                                 ranking)       panel descriptions) creation)
```

All generated data is saved to `data/cartoons/` with naming pattern:
`{location}_{date}.json` (cartoon metadata) and `{location}_{date}.png` (image file)

## API Configuration

### Required API Keys

1. **GOOGLE_API_KEY** (required) - Get from [Google AI Studio](https://aistudio.google.com/)
   - Used for: Cartoon generation, image generation
   - Configure in: `.env` or `.streamlit/secrets.toml`

2. **OPENROUTER_API_KEY** (optional) - Get from [OpenRouter](https://openrouter.ai/)
   - Used for: Alternative comic script generation using Claude 3.5 Sonnet
   - Configure in: `.env`
   - Enables `image_generator_openrouter.py` as alternative to Gemini scripting

### News Fetching

- **Google News**: Uses free GNews library (no API key required)
- Real-time local news with location-based filtering
- Sorting options: popularity (trending stories) or recency (latest stories)
- Falls back to fictional news if no real results found
- No API authentication or external rate limits

### Configuration Files

- `.env`: Local development secrets (not committed)
- `.streamlit/secrets.toml`: Deployment secrets for Streamlit Cloud
- `.streamlit/config.toml`: Streamlit UI configuration (theme, server settings)

## Testing Patterns

### Test Structure
- All tests use pytest with extensive mocking
- Tests are organized in classes matching source files
- Mock external API calls (Gemini, NewsAPI)
- Use `pytest-mock` for patching
- Fixtures defined in individual test files

### Naming Conventions
- Test files: `test_{module_name}.py`
- Test classes: `Test{ClassName}`
- Test methods: `test_{method_name}_{scenario}`

Example:
```python
class TestCartoonGenerator:
    def test_generate_concepts_success(self, ...):
        # Test normal operation

    def test_generate_concepts_error(self, ...):
        # Test error handling
```

### Coverage Requirements
- Maintain >85% code coverage
- Run with: `pytest tests/ -v --cov=src --cov-report=term-missing`
- Current status: 88/88 tests passing, 89% coverage

## Key Implementation Details

### Rate Limiting

- **Implementation**: `limits` library with in-memory storage
- **Current limit**: 2 image generations per minute per session
- **Location**: [app.py](app.py) lines 22-31
- **Note**: Scales to single process only; use Redis for multi-process deployment

### Location Caching & Invalidation

- **Location data** is cached in session state to avoid redundant API calls
- **Cache cleared** when user changes location (reset in callback)
- **GPS coordinates** persist across reruns until explicitly changed

### Comic Strip Scripting

- **Grounding**: Comic panel descriptions are grounded in actual news story details
- **Process**: Headlines + topic → detailed multi-panel script → image generation
- **Models**: Gemini 2.0-flash for scripting, Gemini 2.5-flash-image for rendering
- **Display**: Script shown to user before image generation (UI enhancement)

### Error Handling Pattern

All main classes follow consistent error handling:
1. Try API call with appropriate timeout
2. On failure, use fallback response (fictional news/placeholder image)
3. Display warning in Streamlit UI with `st.warning()` or `st.error()`
4. Never crash the app - always return valid data structure

### JSON Data Validation

Cartoon data must match this structure:
```python
{
    "topic": str,
    "location": str,
    "ideas": [{"title": str, "premise": str, "why_funny": str}, ...],  # exactly 5
    "ranking": [str, str, str, str, str],  # 5 titles in order
    "winner": str  # first in ranking
}
```

Use `validate_cartoon_data()` from [src/utils.py](src/utils.py) to check structure.

### Image Generation Style

The ImageGenerator applies Mark Knight newspaper cartoon style:
- Bold, exaggerated caricatures
- Expressive facial features and body language
- Clear, strong line work
- Selective color with emphasis on key elements
- Professional newspaper comic strip format

Comic strips are scripted in detail before image generation to ensure visual coherence.

### Date Handling

All dates are location-aware using pytz and timezonefinder:
- `format_date_for_location()` converts dates to local timezone
- Format: "YYYYMMDD_HHMMSS" for filenames
- Format: "YYYY-MM-DD" for API calls
- Timezone detection from GPS coordinates

### UI & Styling

- **Layout**: Centered 900px max-width container (matches specification)
- **Theme**: Purple-to-pink gradient header (color: #8b5cf6 → #ec4899)
- **CSS-in-JS**: Custom Streamlit styling in [app.py](app.py)
- **Key elements**:
  - Hidden Streamlit footer and menu
  - Progress indicators for multi-step workflow
  - Gradient buttons for primary actions
  - Full-width containers with proper spacing
  - Download button with gradient styling
- **Recent fixes**: Action button alignment, expander nesting, gradient consistency

## File Locations

### Source Code
- `app.py` - Main Streamlit application
- `src/` - Core modules (4 main classes + utils)
- `tests/` - Unit tests (mirrors src/ structure)

### Data & Config
- `data/cartoons/` - Generated cartoon JSON and PNG files
- `.streamlit/` - Streamlit configuration
- `.env` - Local environment variables (not committed)

### Documentation
- `README.md` - User-facing documentation
- `USAGE.md` - Detailed user guide
- `DEPLOYMENT.md` - Deployment instructions
- `CARTOON_APP_PLAN.md` - Original design document

## Important Development Patterns

### Prompt Engineering

Prompts are in `_build_generation_prompt()` methods:
- **CartoonGenerator** ([src/cartoon_generator.py](src/cartoon_generator.py)):
  - Takes headlines as context for concept generation
  - Enforces strict JSON structure validation
  - Auto-fixes malformed responses (missing fields, invalid JSON)
- **ImageGenerator** ([src/image_generator.py](src/image_generator.py)):
  - Stage 1: Generates detailed comic strip script grounded in news story
  - Stage 2: Converts script to Mark Knight style image description
  - Both stages must maintain news relevance

### Adding New Models

When upgrading Gemini or alternative models:
1. Update model name in class `__init__`
2. Verify prompt compatibility (especially JSON schema if applicable)
3. Run full test suite: `pytest tests/ -v --cov=src`
4. Check cost implications in README.md
5. Validate output structure doesn't break validation logic

### Location Detection Flow

LocationDetector implements 3-tier fallback in priority order:
1. `get_browser_location()` - GPS from browser (HTTPS required)
2. Manual entry via Streamlit text input
3. `get_ip_location()` - IP-based geocoding fallback

Cache invalidation: When user changes location, `location_cache_key` in session state is reset.

## Deployment Notes

### Environment Configuration

**Development**: Use `.env` file (auto-loaded by python-dotenv)
**Production**: Use `.streamlit/secrets.toml` for Streamlit Cloud deployment

### Streamlit Cloud Deployment

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io/)
3. Add `GOOGLE_API_KEY` to secrets
4. HTTPS is automatic (required for browser geolocation)
5. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

### Cost Analysis

Per cartoon generation:
- Google News (GNews): Free (no API key)
- Gemini 2.0-flash-exp (concept generation): ~$0.05-0.10
- Gemini 2.5-flash-image (image generation): ~$0.039

**Estimated total**: $0.12-0.17 per complete cartoon

### Multi-Process Scaling

Current rate limiting uses in-memory storage. For production with multiple Streamlit processes, migrate to Redis:
- Replace `MemoryStorage()` with `RedisStorage()`
- Update `app.py` rate limiting setup (lines 22-31)
- Requires Redis server running
