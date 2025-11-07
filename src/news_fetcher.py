"""News fetching using NewsAPI.org for real-time news."""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import streamlit as st
import os


class NewsFetcher:
    """Fetches local news using NewsAPI.org."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the news fetcher.

        Args:
            api_key: NewsAPI key (will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        self.base_url = "https://newsapi.org/v2"
        if not self.api_key:
            st.warning("⚠️ NEWSAPI_KEY not configured. Using fallback fictional news.")

    def fetch_local_news(
        self,
        city: str,
        country: str,
        date: Optional[str] = None,
        num_headlines: int = 5,
        sort_by: str = "relevancy"
    ) -> Dict[str, Any]:
        """
        Fetch local news headlines for a specific location using NewsAPI.

        Args:
            city: City name
            country: Country name
            date: Date string (defaults to today)
            num_headlines: Number of headlines to fetch
            sort_by: Sorting method - "relevancy" (default), "popularity", or "publishedAt"
                     relevancy: Most relevant to location (best for cartoons)
                     popularity: Trending/viral stories
                     publishedAt: Most recent stories

        Returns:
            Dictionary with news data including headlines and summary
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Validate sort_by parameter
        valid_sorts = ["relevancy", "popularity", "publishedAt"]
        if sort_by not in valid_sorts:
            st.warning(f"⚠️ Invalid sort_by '{sort_by}'. Using 'relevancy' instead.")
            sort_by = "relevancy"

        # If no API key, fall back to fictional news
        if not self.api_key:
            return self._get_fictional_news(city, country, date, num_headlines)

        try:
            # Try to fetch real news from NewsAPI
            headlines_data = self._fetch_from_newsapi(city, country, date, num_headlines, sort_by)

            if headlines_data:
                return headlines_data
            else:
                # Fallback to fictional if API returns empty
                return self._get_fictional_news(city, country, date, num_headlines)

        except Exception as e:
            st.warning(f"⚠️ Could not fetch real news: {e}. Using fictional news instead.")
            return self._get_fictional_news(city, country, date, num_headlines)

    def _fetch_from_newsapi(
        self,
        city: str,
        country: str,
        date: str,
        num_headlines: int,
        sort_by: str = "relevancy"
    ) -> Optional[Dict[str, Any]]:
        """Fetch headlines from NewsAPI with location filtering and sorting options.

        Args:
            city: City name
            country: Country name
            date: Date string
            num_headlines: Number of headlines to return
            sort_by: Sorting method - "relevancy", "popularity", or "publishedAt"
        """
        try:
            # Country code mapping for NewsAPI
            country_codes = {
                "USA": "us", "United States": "us",
                "UK": "gb", "United Kingdom": "gb",
                "Australia": "au",
                "Japan": "jp",
                "France": "fr",
                "Germany": "de",
                "Canada": "ca",
                "India": "in",
                "Brazil": "br"
            }

            # Get country code, default to searching by city+country
            country_code = country_codes.get(country.title())

            # Build search query with city and country name for accurate results
            query = f"{city} {country}"

            # Get news from past 24 hours
            from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            params = {
                "q": query,
                "sortBy": sort_by,  # Use configurable sorting (relevancy, popularity, or publishedAt)
                "language": "en",
                "from": from_date,
                "apiKey": self.api_key,
                "pageSize": num_headlines * 3  # Get more to filter location-relevant ones
            }

            response = requests.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()
            articles = data.get("articles", [])

            if not articles:
                return None

            # Filter articles to ensure they're about the location
            # Prioritize articles with city name in title (stronger signal)
            filtered_articles_title = []
            filtered_articles_desc = []

            location_str = city.lower()
            country_lower = country.lower()

            for article in articles:
                title = article.get("title", "").lower()
                description = article.get("description", "").lower() if article.get("description") else ""

                # Strongly prefer articles with city in title
                if location_str in title:
                    filtered_articles_title.append(article)
                # Secondary: city in description (but check it's not just a passing mention)
                elif location_str in description and len(description) > 100:
                    filtered_articles_desc.append(article)

            # Combine: prioritize title matches, fill with description matches
            filtered_articles = filtered_articles_title + filtered_articles_desc[:num_headlines]
            filtered_articles = filtered_articles[:num_headlines]

            # Extract headlines with URLs
            headlines = [
                {
                    "title": article.get("title", ""),
                    "summary": article.get("description", "")[:150],  # Limit summary length
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "")
                }
                for article in filtered_articles[:num_headlines]
                if article.get("title")
            ]

            # Determine dominant topic from titles
            dominant_topic = headlines[0]["title"].split(" - ")[0] if headlines else "News"

            return {
                "location": f"{city}, {country}",
                "date": date,
                "headlines": headlines,
                "dominant_topic": dominant_topic,
                "source": "NewsAPI"
            }

        except requests.exceptions.RequestException:
            return None

    def _get_fictional_news(
        self,
        city: str,
        country: str,
        date: str,
        num_headlines: int
    ) -> Dict[str, Any]:
        """Get fictional but realistic news as fallback."""
        return {
            "location": f"{city}, {country}",
            "date": date,
            "headlines": [
                {
                    "title": f"Local government discusses new infrastructure project in {city}",
                    "summary": "City council meets to discuss improvements"
                },
                {
                    "title": f"{city} sports team advances in regional championship",
                    "summary": "Recent victory keeps hopes alive for title"
                },
                {
                    "title": f"Community event draws large crowds to {city} center",
                    "summary": "Hundreds attend annual festival celebration"
                },
                {
                    "title": f"Local business expansion announced in {city}",
                    "summary": "New jobs coming to the area"
                },
                {
                    "title": f"{city} weather forecast: Clear skies ahead",
                    "summary": "Perfect conditions for outdoor activities"
                }
            ][:num_headlines],
            "dominant_topic": "Local News",
            "source": "Fictional (NEWSAPI_KEY not configured)"
        }

    def get_news_summary(self, news_data: Dict[str, Any]) -> str:
        """
        Generate a concise summary of the news.

        Args:
            news_data: News data dictionary from fetch_local_news

        Returns:
            Summary string
        """
        if not news_data.get('headlines'):
            return "No news available"

        headlines = news_data['headlines']
        summary_parts = []

        for i, headline in enumerate(headlines[:5], 1):
            title = headline.get('title', 'Unknown')
            summary_parts.append(f"{i}. {title}")

        return "\n".join(summary_parts)

    def select_dominant_topic(
        self,
        news_data: Dict[str, Any]
    ) -> str:
        """
        Select the dominant news topic from headlines.

        Args:
            news_data: News data dictionary

        Returns:
            Dominant topic string
        """
        # First try to use the dominant_topic from the API response
        if news_data.get('dominant_topic') and news_data['dominant_topic'] != "Error":
            return news_data['dominant_topic']

        # Fallback: use first headline if available
        if news_data.get('headlines') and len(news_data['headlines']) > 0:
            return news_data['headlines'][0].get('title', 'General News')

        return 'General News'

    def fetch_and_summarize(
        self,
        city: str,
        country: str,
        date: Optional[str] = None,
        sort_by: str = "relevancy"
    ) -> Dict[str, Any]:
        """
        Fetch news and prepare it for cartoon generation.

        Args:
            city: City name
            country: Country name
            date: Date string
            sort_by: Sorting method - "relevancy" (default), "popularity", or "publishedAt"

        Returns:
            Dictionary with news and dominant topic
        """
        news_data = self.fetch_local_news(city, country, date, sort_by=sort_by)
        dominant_topic = self.select_dominant_topic(news_data)

        return {
            'news_data': news_data,
            'dominant_topic': dominant_topic,
            'summary': self.get_news_summary(news_data),
            'location': f"{city}, {country}",
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'sort_by': sort_by
        }


def fetch_news_for_location(
    city: str,
    country: str,
    date: Optional[str] = None,
    api_key: Optional[str] = None,
    sort_by: str = "relevancy"
) -> Dict[str, Any]:
    """
    Convenience function to fetch news for a location.

    Args:
        city: City name
        country: Country name
        date: Date string
        api_key: NewsAPI key (optional)
        sort_by: Sorting method - "relevancy" (default), "popularity", or "publishedAt"

    Returns:
        Dictionary with news and dominant topic
    """
    fetcher = NewsFetcher(api_key=api_key)
    return fetcher.fetch_and_summarize(city, country, date, sort_by=sort_by)
