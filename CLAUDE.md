# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit application that generates AI-powered cartoon concepts based on local news. The app uses Google Gemini for news fetching, concept generation, and image creation with Mark Knight comic strip style influence.

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
   - Uses Google News (via GNews library) for real-time local news
   - No API key required (free, no authentication needed)
   - Falls back to fictional news if no results found
   - Location-based filtering prioritizes title matches over description
   - Returns 5 headlines with dominant topic identification

3. **CartoonGenerator** ([src/cartoon_generator.py](src/cartoon_generator.py))
   - Uses Gemini 2.0-flash-exp for concept generation
   - Creates 5 ranked cartoon concepts per news topic
   - Each concept has: title, premise, why_funny (≤15 words)
   - Validates structure and auto-fixes malformed responses
   - Returns winner as first-ranked concept

4. **ImageGenerator** ([src/image_generator.py](src/image_generator.py))
   - Two-stage process: comic strip scripting → image generation
   - Uses Gemini 2.0-flash for scripting (detailed panel descriptions)
   - Uses Gemini 2.5-flash-image for actual image creation
   - Mark Knight style influence: expressive caricatures, exaggerated features
   - Saves images as PNG to `data/cartoons/`
   - Alternative: `image_generator_openrouter.py` uses Claude 3.5 Sonnet for scripting via OpenRouter API

### State Management

Streamlit session state manages the application flow:
- `location_data`: GPS coordinates and location metadata
- `address_data`: Human-readable address from reverse geocoding
- `news_data`: Headlines, topic, and date
- `cartoon_data`: Generated concepts with ranking
- `image_path`: Path to saved cartoon image

State persists across reruns enabling multi-step workflow without re-fetching data.

### Data Flow

```
User Location → Detect Location → Fetch News → Generate Concepts → Create Image
     ↓               ↓                 ↓              ↓                ↓
Browser GPS    3-tier fallback   Google News    Gemini 2.0    Comic scripting
                                   (GNews)                     + Gemini 2.5 Image
```

All generated data is saved to `data/cartoons/` with naming pattern:
`{location}_{date}.json` and `{location}_{date}.png`

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
- Automatically fetches real-time local news for any location
- Falls back to fictional news if no results found
- No authentication or rate limits to worry about

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

### Error Handling Pattern

All main classes follow consistent error handling:
1. Try API call
2. On failure, use fallback response
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

## Common Development Tasks

### Adding New Gemini Models

When Gemini releases new models:
1. Update model name in class `__init__` method
2. Check API compatibility with existing prompts
3. Test generation quality with `pytest tests/test_{module}.py`
4. Update README.md if cost/capabilities change

### Modifying Cartoon Generation Prompts

Prompts are in `_build_generation_prompt()` methods:
- CartoonGenerator: Concept generation rules
- ImageGenerator: Visual style and structure
- Keep prompts detailed and explicit
- Always specify output format (JSON structure)
- Test changes don't break validation

### Extending Location Detection

LocationDetector has 3 detection methods (priority order):
1. `get_browser_location()` - GPS from browser
2. Manual entry via Streamlit text input
3. `get_ip_location()` - Fallback using geocoder

Add new methods to the fallback chain in [app.py](app.py) location detection flow.

## Deployment Notes

### Streamlit Cloud
- Push to GitHub
- Connect at [share.streamlit.io](https://share.streamlit.io/)
- Add `GOOGLE_API_KEY` to Streamlit secrets
- Optionally add `NEWSAPI_KEY` for real news
- HTTPS is automatic (required for browser geolocation)

### Environment Variables
Development: Use `.env` file (loaded by python-dotenv)
Production: Use `.streamlit/secrets.toml` (Streamlit Secrets)

### Cost Considerations
- Gemini 2.0-flash-exp: ~$0.05-0.10 per cartoon concept generation
- Gemini 2.5-flash-image: ~$0.039 per image
- NewsAPI: Free tier available (100 requests/day)
- Estimated: $0.12-0.17 per complete cartoon generation
