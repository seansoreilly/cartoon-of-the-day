# 🎨 Cartoon of the Day

A Streamlit application that generates daily cartoon concepts based on local news from your location using Google Gemini AI.

[![Tests](https://img.shields.io/badge/tests-88%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-89%25-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## ✨ Features

### 🗺️ Smart Location Detection
- **Browser Geolocation**: Automatic detection using GPS/Wi-Fi
- **Manual Entry**: Enter any city worldwide
- **IP-Based Fallback**: Automatic fallback when browser detection fails

### 📰 Local News Integration
- Fetches 5 current headlines from your location
- Uses Google Gemini with web grounding
- Identifies dominant news topic automatically
- Real-time news updates

### 🎭 AI-Powered Comedy Generation
- Creates 5 unique cartoon concepts
- Each concept includes:
  - Creative title
  - One-sentence premise
  - Humor explanation (≤15 words)
- Ranked from funniest to least funny
- Context-aware local humor

### 🖼️ Image Generation
- Professional placeholder images
- Clean, branded design
- Ready for future Gemini image API integration
- Download capability

### 💎 Modern UI/UX
- Responsive design
- Custom CSS styling with gradients
- Smooth animations
- Mobile-friendly
- Loading progress indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google AI Studio API key ([Get yours free](https://aistudio.google.com/))
- Virtual environment tool (virtualenv or venv)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/cartoon-of-the-day.git
cd cartoon-of-the-day

# 2. Create virtual environment
virtualenv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your-key-here

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501` 🎉

### First-Time Setup

1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com/)
2. **Configure**: Add key to `.env` or `.streamlit/secrets.toml`
3. **Run**: Execute `streamlit run app.py`
4. **Generate**: Click "Detect My Location" → "Generate Cartoon"

See [USAGE.md](USAGE.md) for detailed instructions.

## 🧪 Testing & Quality

### Run Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Quick test run
pytest tests/ -v

# Specific test file
pytest tests/test_cartoon_generator.py -v
```

**Test Results**: ✅ 88/88 tests passing | 89% coverage

### Code Quality

```bash
# Linting (passes with no warnings)
pylint src/ --fail-under=8
flake8 src/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports

# Formatting
black src/ --check
```

All quality checks pass ✅

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

## 🛠️ Technology Stack

### Core Technologies
- **[Streamlit](https://streamlit.io/)** 1.32.0 - Web framework
- **[Google Gemini](https://ai.google.dev/)** 2.0-flash-exp - AI generation
- **Python** 3.10+ - Backend language

### Key Libraries
- **geopy** 2.4.1 - Reverse geocoding
- **geocoder** 1.38.1 - IP-based location
- **streamlit-js-eval** 0.1.5 - Browser geolocation
- **timezonefinder** 6.2.0 - Timezone detection
- **Pillow** 10.2.0 - Image processing
- **pytest** 8.0.0 - Testing framework

### Architecture
- **Location Detection**: 3-tier fallback system
- **News Fetching**: Gemini with web grounding
- **Cartoon Generation**: AI-powered ranking
- **Image Generation**: PIL-based placeholders
- **State Management**: Streamlit session state

## 💰 Cost Analysis

### Per Cartoon Generation
- News search (web grounding): ~$0.035
- Cartoon concept generation: ~$0.05-0.10
- Image generation: $0 (placeholder) / $0.039 (when API available)
- **Total**: ~$0.12-0.17 per cartoon

### Monthly Estimates
| Usage | Cost |
|-------|------|
| Light (5/day) | $3-4/month |
| Medium (20/day) | $12-15/month |
| Heavy (50/day) | $30-40/month |

**Free Tier**: Gemini offers generous quotas for testing

## 📦 Deployment

### Streamlit Cloud (Recommended)

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy cartoon app"
git push origin main

# 2. Deploy at https://share.streamlit.io/
# 3. Add GOOGLE_API_KEY to secrets
# 4. Your app is live! 🚀
```

**Detailed guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

### Local Development

```bash
# Activate environment
source venv/bin/activate

# Run app
streamlit run app.py

# Access at http://localhost:8501
```

## 📚 Documentation

- **[USAGE.md](USAGE.md)** - Complete user guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment instructions
- **[CARTOON_APP_PLAN.md](CARTOON_APP_PLAN.md)** - Original design document

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Maintain >85% code coverage
- Follow existing code style
- Update documentation
- Add type hints

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for powerful AI capabilities
- **Streamlit** for the amazing web framework
- **geopy** for location services
- All contributors and users

## 🐛 Known Issues

- Image generation uses placeholders (Gemini Image API integration pending)
- Browser geolocation requires HTTPS (works on deployed sites)
- Rate limits apply based on Google Gemini quotas

## 🗺️ Roadmap

### Coming Soon
- [ ] Real image generation via Gemini Image API
- [ ] Multiple art style options
- [ ] Cartoon history/archive
- [ ] Social sharing features
- [ ] User voting on concepts

### Future Ideas
- [ ] Animated cartoons
- [ ] Multi-panel comic strips
- [ ] Custom topic input
- [ ] Email delivery
- [ ] API access

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/cartoon-of-the-day/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/cartoon-of-the-day/discussions)
- **Email**: your-email@example.com

## ⭐ Show Your Support

If you like this project, please give it a ⭐ on GitHub!

---

**Made with ❤️ using Claude Code and Google Gemini**
