# API Integration Guide

This document describes the external APIs used by the Cartoon of the Day application.

## Overview

The application integrates with Google services for news fetching and AI-powered content generation:

1. **Google News** - Fetching local news articles
2. **Google Gemini API** - Generating cartoon concepts and images

## Google Gemini API

### Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key"
3. Create a new API key
4. Add the key to your `.env.local`:
```
VITE_GEMINI_API_KEY=your_api_key_here
```

### Rate Limits

- Free tier: 60 requests per minute
- Standard: 1,000,000 tokens per minute
- The app implements local rate limiting (2 image generations per minute)

### Cartoon Generation

**Service**: `src/services/geminiService.ts`

**Function**: `generateCartoonConcepts(articles: NewsArticle[])`

Generates 5 cartoon concept variations based on news articles using the Gemini 2.0-flash model.

**Request:**
```typescript
{
  topic: "News Topic",
  headlines: ["Headline 1", "Headline 2"],
  location: "City, Country"
}
```

**Response:**
```typescript
{
  topic: string;
  location: string;
  ideas: Array<{
    title: string;
    premise: string;
    why_funny: string;
  }>;
  ranking: string[];
  winner: string;
  generatedAt: number;
}
```

### Image Generation

**Function**: `generateCartoonImage(concept: CartoonConcept)`

Creates a cartoon image based on selected concept using Gemini Vision API.

**Process:**
1. Generate detailed comic panel script from concept
2. Create image from script description
3. Apply Mark Knight newspaper cartoon style

**Style Details:**
- Expressive caricatures with exaggerated features
- Bold pen and ink with selective watercolor
- Clear visual metaphors and symbolism
- Professional newspaper comic format

### API Costs

**Estimated costs per cartoon generation:**
- Concept generation (2.0-flash): ~$0.05-0.10
- Image generation (2.5-flash-image): ~$0.039
- **Total**: ~$0.10-0.15 per cartoon

**Daily usage (10 cartoons):** ~$1.00-1.50
**Monthly usage (300 cartoons):** ~$30-45

Monitor usage in [Google AI Studio Console](https://console.cloud.google.com/).

## Google News API

### Overview

The application uses the **GNews library** to fetch news articles from Google News.

**Key Features:**
- No API key required (uses public Google News)
- Real-time news updates
- Location-based filtering
- Multiple language support

### News Fetching

**Service**: `src/services/newsService.ts`

**Function**: `fetchNewsByLocation(location: string)`

Fetches top news articles for a specific location.

**Request Parameters:**
- `location` (string): City, region, or country
- `limit` (number): Maximum articles to return (default: 10)

**Response:**
```typescript
{
  articles: Array<{
    title: string;
    description: string;
    url: string;
    source: {
      name: string;
      url: string;
    };
    publishedAt: string;
    content?: string;
    image?: string;
    author?: string;
  }>;
  totalArticles: number;
  topic?: string;
  location?: string;
  timestamp?: number;
}
```

### Limitations

- News articles limited to English language
- May be region-specific availability
- Updates with Google News frequency (~real-time)
- No authentication needed

## Service Integration

### Location Service

**File**: `src/services/locationService.ts`

Provides location detection using:
1. Browser Geolocation API (GPS)
2. Manual user input
3. IP-based geolocation (fallback)

**Functions:**
- `getLocationFromGPS()`: Browser GPS
- `getLocationFromIP()`: IP-based fallback
- `getLocationName()`: Reverse geocoding (OpenStreetMap)

### Storage Service

**File**: `src/services/storageService.ts`

Manages local storage of:
- User location
- News articles
- Generated cartoons
- User preferences
- History

## Error Handling

All API calls include error handling:

```typescript
try {
  const result = await apiCall();
  return result;
} catch (error) {
  console.error('API Error:', error);
  // Fallback behavior
  return fallbackData;
}
```

**Fallback Strategies:**
- News API: Returns last cached articles or fictional news
- Image API: Returns placeholder image with error message
- Concept API: Returns default concept examples

## Rate Limiting

**Implementation**: `src/utils/rateLimiter.ts`

Local rate limiting for image generation:
- **Limit**: 2 images per minute per session
- **Storage**: In-memory (per browser tab)
- **Implementation**: Token bucket algorithm

**Usage:**
```typescript
const rateLimiter = new ImageGenerationRateLimiter();

if (rateLimiter.canGenerate()) {
  // Generate image
  rateLimiter.recordGeneration();
} else {
  // Show "Please wait" message
  const timeRemaining = rateLimiter.getTimeUntilNextGeneration();
}
```

## Testing API Integrations

### Mock Services

Tests use mocked API responses:

```typescript
vi.mock('../services/geminiService', () => ({
  generateCartoonConcepts: vi.fn(() => 
    Promise.resolve([mockConcept])
  )
}));
```

### Test Data

Mock responses are in `src/test/fixtures/`:
- `geminiResponses.ts` - Gemini API responses
- `newsResponses.ts` - Google News responses
- `locationResponses.ts` - Location data

## Troubleshooting

### API Key Issues

**Problem**: "Invalid API key"
**Solution**: 
- Verify key in [Google AI Studio](https://aistudio.google.com/)
- Check key is set in `.env.local` correctly
- Ensure no extra spaces or quotes

### Rate Limit Exceeded

**Problem**: "Rate limit exceeded"
**Solution**:
- Wait for rate limit window to reset
- Check free tier limits (60 req/min)
- Consider upgrading to paid tier

### Network Errors

**Problem**: "Failed to fetch"
**Solution**:
- Check internet connection
- Verify API endpoints are reachable
- Check CORS configuration
- Try again in a few moments

### Empty Results

**Problem**: No news articles or concepts returned
**Solution**:
- Verify location name is correct
- Check Google News is available in region
- Ensure Gemini API has quota remaining
- Review error logs in browser console

## Future Enhancements

1. **Multiple AI Providers**
   - OpenAI GPT-4
   - Claude AI
   - Open-source models

2. **News Sources**
   - RSS feeds
   - Traditional news APIs
   - Social media integration

3. **Caching**
   - Cache API responses
   - Offline mode support
   - Service worker integration

4. **Analytics**
   - Track popular concepts
   - Monitor API usage
   - User behavior insights
