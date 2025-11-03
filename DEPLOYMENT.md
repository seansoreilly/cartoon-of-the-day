# 🚀 Deployment Guide

## Deploy to Streamlit Cloud

### Prerequisites

1. GitHub account
2. Google AI Studio API key ([Get one here](https://aistudio.google.com/))
3. Streamlit Cloud account (free) - Sign up at https://streamlit.io/cloud

### Step-by-Step Deployment

#### 1. Push to GitHub

```bash
# If you haven't already initialized git
git init
git add .
git commit -m "Initial commit: Cartoon of the Day app"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/cartoon-of-the-day.git
git branch -M main
git push -u origin main
```

#### 2. Connect to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository: `YOUR_USERNAME/cartoon-of-the-day`
4. Set Main file path: `app.py`
5. Click "Deploy"

#### 3. Configure Secrets

In Streamlit Cloud dashboard:

1. Go to your app settings (⚙️ icon)
2. Click "Secrets"
3. Add your API key:

```toml
GOOGLE_API_KEY = "your-api-key-here"
```

4. Click "Save"

#### 4. Verify Deployment

Your app will be available at:
```
https://YOUR_USERNAME-cartoon-of-the-day-app-xyz123.streamlit.app
```

## Local Development

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/cartoon-of-the-day.git
cd cartoon-of-the-day

# Create virtual environment
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

The app will open at http://localhost:8501

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Environment Variables

### Required

- `GOOGLE_API_KEY`: Your Google AI Studio API key

### Optional

No optional environment variables currently

## Configuration Files

### `.streamlit/config.toml`

Streamlit configuration (colors, theme, server settings)

### `.streamlit/secrets.toml` (Local only, gitignored)

Local secrets for development:
```toml
GOOGLE_API_KEY = "your-key-here"
```

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution**: Ensure you've added the API key to:
- Streamlit Cloud: App Settings → Secrets
- Local: `.streamlit/secrets.toml` or `.env` file

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Location detection not working

**Solution**:
- Browser geolocation requires HTTPS (works on Streamlit Cloud)
- Use manual location entry as fallback
- IP-based detection works as secondary fallback

### Issue: "Rate limit exceeded"

**Solution**:
- Google Gemini has rate limits
- Wait a few minutes before retrying
- Consider upgrading to a paid API plan

## Performance Optimization

### Caching

The app automatically caches responses using Streamlit's session state to avoid redundant API calls.

### Resource Usage

- **Memory**: ~200-300MB (Streamlit + dependencies)
- **API Calls per generation**:
  - 1 call for news fetching
  - 1 call for cartoon generation
  - Total: 2 API calls

### Cost Estimation

Based on Google Gemini pricing:

- **News Fetching**: ~$0.035 per call
- **Cartoon Generation**: ~$0.05-0.10 per call
- **Total per cartoon**: ~$0.12-0.17

**Monthly estimates**:
- Light use (5/day): ~$3-4/month
- Medium use (20/day): ~$12-15/month
- Heavy use (50/day): ~$30-40/month

## Security Best Practices

### API Key Protection

✅ **Do**:
- Use Streamlit secrets for deployment
- Use `.env` file for local development
- Add `.env` and `.streamlit/secrets.toml` to `.gitignore`

❌ **Don't**:
- Commit API keys to git
- Share API keys publicly
- Hardcode keys in source files

### Data Privacy

- No user data is stored permanently
- Session data is cleared on browser close
- Generated cartoons are saved locally only

## Monitoring

### Streamlit Cloud

View app metrics in Streamlit Cloud dashboard:
- App uptime
- Viewer count
- Resource usage
- Error logs

### Logs

Check logs for debugging:
1. Streamlit Cloud: App → "..." → "Logs"
2. Local: Console output

## Updates & Maintenance

### Updating the App

```bash
# Pull latest changes
git pull origin main

# Streamlit Cloud will auto-deploy
# Or manually: Settings → Reboot app
```

### Dependency Updates

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update requirements.txt
pip freeze > requirements.txt
```

### Database Maintenance

No database maintenance required - app uses file-based storage only.

## Backup & Recovery

### Backup

Generated cartoons are saved in `data/cartoons/`:
```bash
# Backup cartoons
tar -czf cartoons-backup-$(date +%Y%m%d).tar.gz data/cartoons/
```

### Recovery

```bash
# Restore from backup
tar -xzf cartoons-backup-YYYYMMDD.tar.gz
```

## Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Google Gemini API**: https://ai.google.dev/docs
- **GitHub Issues**: Report bugs on your repository
- **Streamlit Community**: https://discuss.streamlit.io/

## Production Checklist

Before deploying to production:

- [ ] All tests passing (88/88)
- [ ] Code coverage >85%
- [ ] API key configured in Streamlit secrets
- [ ] `.gitignore` includes sensitive files
- [ ] README updated with deployment URL
- [ ] Error handling tested
- [ ] Browser compatibility tested
- [ ] Mobile responsiveness checked
- [ ] Performance tested with API rate limits

## License

MIT License - See LICENSE file for details
