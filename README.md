# 🎨 Cartoon of the Day

A Streamlit application that generates daily cartoon concepts based on local news from your location using Google Gemini AI.

## Features

- **Location Detection**: Automatically detect your city/region from browser
- **Local News Fetching**: Retrieves current news headlines from your location
- **Comedy Generation**: Creates 5 original cartoon concepts based on local news
- **Ranking System**: AI ranks concepts from funniest to least funny
- **Image Generation**: Creates a cartoon image for the winner
- **JSON Output**: Structured data output for all concepts

## Setup

### Prerequisites

- Python 3.10+
- Google AI Studio API key ([Get one here](https://aistudio.google.com/))

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd cartoon-of-the-day
```

2. Create and activate virtual environment:
```bash
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Configuration

Create `.streamlit/secrets.toml` for local development:
```toml
GOOGLE_API_KEY = "your-api-key-here"
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Development

### Running Tests

```bash
pytest tests/ -v --cov
```

### Code Quality

```bash
# Linting
pylint src/ --fail-under=8
flake8 src/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports

# Formatting
black src/ --check
```

## Project Structure

```
cartoon-of-the-day/
├── .streamlit/           # Streamlit configuration
├── src/                  # Source code
│   ├── location_detector.py
│   ├── news_fetcher.py
│   ├── cartoon_generator.py
│   ├── image_generator.py
│   └── utils.py
├── data/cartoons/        # Generated cartoons
├── tests/                # Unit tests
├── app.py                # Main application
└── requirements.txt      # Dependencies
```

## Technology Stack

- **Streamlit**: Web framework
- **Google Gemini 2.5 Pro**: Text generation with web grounding
- **Google Gemini 2.5 Flash Image**: Cartoon image generation
- **geopy**: Location services
- **timezonefinder**: Timezone detection

## Cost Estimates

- Per cartoon generation: ~$0.12-0.17
- Monthly (daily use): ~$6-9
- Includes Gemini free tier benefits

## Deployment

Deploy to Streamlit Cloud:

1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `GOOGLE_API_KEY` to Streamlit secrets
4. Deploy!

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
