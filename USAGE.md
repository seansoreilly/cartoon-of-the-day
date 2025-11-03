# 📖 Usage Guide

## Getting Started

### First Time Setup

1. **Get Your API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Click "Get API Key"
   - Copy your API key

2. **Configure the App**
   - Local: Add key to `.env` or `.streamlit/secrets.toml`
   - Cloud: Add key to Streamlit Cloud secrets

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

## Using the App

### Step 1: Set Your Location

You have three options:

#### Option A: Auto-Detect (Recommended)
1. Click **"🌍 Detect My Location"**
2. Allow browser location access when prompted
3. Your city will be displayed automatically

#### Option B: Manual Entry
1. Type your location in the text field
   - Example: "Paris, France"
   - Example: "New York, USA"
   - Example: "Tokyo, Japan"
2. Click **"📍 Use This Location"**

#### Option C: IP-Based (Automatic Fallback)
- If browser detection fails, the app automatically uses IP geolocation
- Less accurate but works without browser permissions

### Step 2: Generate Your Cartoon

1. Click **"✨ Generate Cartoon"**
2. Wait while the app:
   - 📰 Fetches local news from your area
   - 💭 Creates 5 comedy concepts
   - 🎨 Generates the cartoon image
3. View your results!

### Step 3: Explore Results

#### Winner Card (Top)
- See the **winning cartoon concept**
- View the **generated image**
- Read the premise and why it's funny

#### All Concepts (Ranked)
- Click on any concept to expand
- See all 5 concepts ranked by humor
- Trophy emoji (🏆) marks the winner

### Step 4: Take Action

Three action buttons at the bottom:

- **🔄 New Cartoon**: Generate a different cartoon for the same location
- **📍 Change Location**: Start over with a new location
- **💾 Download Image**: Save the cartoon image to your device

## Features Explained

### Location Detection

The app uses a 3-tier fallback system:

1. **Browser Geolocation** (Most accurate)
   - Uses your device's GPS or Wi-Fi positioning
   - Requires HTTPS (works on deployed site)
   - Most accurate results

2. **Manual Entry** (Override)
   - Enter any city in the world
   - Useful for exploring different locations
   - Format: "City, Country"

3. **IP-Based** (Automatic fallback)
   - Uses your IP address to estimate location
   - Less accurate (~city level)
   - Works without browser permissions

### News Fetching

- Fetches 5 current news headlines from your location
- Uses Google Gemini with web grounding
- Focuses on local stories specific to your area
- Identifies the dominant news topic automatically

### Cartoon Generation

The AI creates 5 unique cartoon concepts:

- **Original ideas** based on current news
- **Local context** specific to your city
- **Ranked by humor** from funniest to least funny
- **Explained** - why each concept is funny

### Image Generation

- Creates a placeholder image with:
  - Cartoon title and premise
  - Professional layout
  - "Coming Soon" message
- Future: Will use Gemini image API when available

## Tips for Best Results

### Location Tips

✅ **Do**:
- Use specific city names: "Melbourne" not "Australia"
- Include country for clarity: "London, UK" vs "London, Canada"
- Try major cities for better news coverage

❌ **Avoid**:
- Very small towns (limited news coverage)
- Vague locations like "Europe" or "Asia"
- Misspelled city names

### Understanding Results

**Ranking System**:
- #1 = Funniest (Winner)
- #5 = Least funny (still funny!)
- AI ranks based on:
  - Cleverness of wordplay
  - Relevance to news
  - Visual comedy potential
  - Universal appeal

**Quality Factors**:
- Recent news = better concepts
- Interesting news = funnier cartoons
- Major cities = more news options

## Common Workflows

### Daily Cartoon Ritual

1. Open app in morning
2. Auto-detect location
3. Generate cartoon
4. Read concepts while having coffee
5. Download winner image
6. Share with friends!

### Location Comparison

1. Enter "New York, USA"
2. Generate cartoon
3. Click "Change Location"
4. Enter "London, UK"
5. Generate cartoon
6. Compare humor styles!

### Concept Exploration

1. Generate cartoon
2. Read all 5 ranked concepts
3. Click "New Cartoon" for more ideas
4. Find your favorite concept
5. Download the image

## Troubleshooting

### "Location not detected"

**Try**:
1. Enable location services in browser
2. Refresh page and try again
3. Use manual entry instead
4. Check HTTPS connection

### "No news available"

**Possible causes**:
- Very small town with limited news
- API rate limit reached
- Temporary service issue

**Solutions**:
- Try a major nearby city
- Wait a few minutes
- Check API key is valid

### "Generation taking too long"

**Normal duration**:
- News fetching: 5-10 seconds
- Cartoon generation: 10-15 seconds
- Image creation: 2-5 seconds
- **Total: 20-30 seconds**

If longer:
- Check internet connection
- Verify API key is valid
- Try refreshing the page

### "Concepts aren't funny"

Remember:
- Humor is subjective
- AI learns from patterns
- Try generating again (different concepts)
- Different locations = different humor styles

## Advanced Usage

### Keyboard Shortcuts

When focused on text input:
- **Enter**: Submit location
- **Esc**: Clear input

### Browser Compatibility

✅ Fully supported:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

⚠️ Limited support:
- Internet Explorer (not recommended)
- Very old browsers

### Mobile Usage

The app works on mobile devices:
- Responsive layout adjusts automatically
- Location detection works with GPS
- Touch-friendly buttons
- Download images to photo library

### Accessibility

- Keyboard navigation supported
- Screen reader friendly
- High contrast colors
- Large, clear text

## Data & Privacy

### What Gets Saved

**Locally**:
- Generated cartoon images (in `data/cartoons/`)
- Cartoon data JSON files

**In Browser Session**:
- Current location
- Generated cartoon data
- UI state

**Not Saved**:
- Your API key (secure)
- Personal information
- Browsing history
- Location history

### Data Retention

- Session data: Cleared on browser close
- Local files: Kept until manually deleted
- Cloud deployment: No persistent storage

### Sharing

When you share:
- Only the image is shared
- No personal data included
- No tracking or analytics

## Best Practices

### Daily Use

- Generate one cartoon per day
- Explore different locations
- Save your favorites
- Share with friends

### Cost Management

- Each generation costs ~$0.12-0.17
- Daily use: ~$3-4/month
- Use responsibly to manage costs
- Consider API usage limits

### Quality Results

- Use major cities for better news
- Generate during local daytime hours
- Try multiple times for variety
- Explore different locations

## Getting Help

### Documentation

- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- This file - Usage instructions

### Support

- Check documentation first
- Review troubleshooting section
- Report issues on GitHub
- Ask in Streamlit community

### Feedback

We'd love to hear from you:
- Found a bug? Report it
- Have a suggestion? Share it
- Made something cool? Show us!

## FAQ

**Q: How often can I generate cartoons?**
A: As often as you like, subject to API rate limits.

**Q: Can I use this commercially?**
A: Check Google Gemini API terms and MIT license.

**Q: Will my cartoons be saved?**
A: Yes, locally in the `data/cartoons/` folder.

**Q: Can I edit the generated concepts?**
A: Currently no, but you can generate new ones.

**Q: Does this work offline?**
A: No, requires internet for API calls.

**Q: Can I change the art style?**
A: Not yet, but this feature may be added.

**Q: How accurate is the location detection?**
A: Browser geolocation is very accurate; IP-based is approximate.

**Q: Can I see cartoons from other dates?**
A: Currently shows today's news only.

## Updates

Stay tuned for future features:
- Real image generation (when API available)
- Multiple art styles
- Cartoon history/archive
- Social sharing features
- Voting on concepts
- Custom topics

---

**Enjoy creating cartoons! 🎨**
