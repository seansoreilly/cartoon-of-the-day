"""News fetching using Google Gemini with web grounding."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
import streamlit as st

from src.utils import get_api_key


class NewsFetcher:
    """Fetches local news using Gemini with web grounding."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the news fetcher.

        Args:
            api_key: Google API key (will use get_api_key() if not provided)
        """
        self.api_key = api_key or get_api_key()
        genai.configure(api_key=self.api_key)

    def fetch_local_news(
        self,
        city: str,
        country: str,
        date: Optional[str] = None,
        num_headlines: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch local news headlines for a specific location.

        Args:
            city: City name
            country: Country name
            date: Date string (defaults to today)
            num_headlines: Number of headlines to fetch

        Returns:
            Dictionary with news data including headlines and summary
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Create model with web grounding
            model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                tools='google_search'
            )

            prompt = f"""
            Find {num_headlines} major news headlines from {city}, {country}
            from today ({date}). Focus on local stories specific to this location.

            Return the response in this exact JSON format:
            {{
                "location": "{city}, {country}",
                "date": "{date}",
                "headlines": [
                    {{"title": "headline 1", "summary": "brief summary"}},
                    {{"title": "headline 2", "summary": "brief summary"}},
                    ...
                ],
                "dominant_topic": "the main theme across these headlines"
            }}

            Only return the JSON, no other text.
            """

            response = model.generate_content(prompt)

            # Parse the response
            import json
            import re

            # Extract JSON from response
            text = response.text.strip()

            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                news_data = json.loads(json_match.group())
                return news_data

            # Fallback: create structure from text
            return {
                "location": f"{city}, {country}",
                "date": date,
                "headlines": [],
                "dominant_topic": "Unable to fetch news",
                "raw_response": text
            }

        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return {
                "location": f"{city}, {country}",
                "date": date,
                "headlines": [],
                "dominant_topic": "Error",
                "error": str(e)
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
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch news and prepare it for cartoon generation.

        Args:
            city: City name
            country: Country name
            date: Date string

        Returns:
            Dictionary with news and dominant topic
        """
        news_data = self.fetch_local_news(city, country, date)
        dominant_topic = self.select_dominant_topic(news_data)

        return {
            'news_data': news_data,
            'dominant_topic': dominant_topic,
            'summary': self.get_news_summary(news_data),
            'location': f"{city}, {country}",
            'date': date or datetime.now().strftime("%Y-%m-%d")
        }


def fetch_news_for_location(
    city: str,
    country: str,
    date: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to fetch news for a location.

    Args:
        city: City name
        country: Country name
        date: Date string
        api_key: Google API key (optional)

    Returns:
        Dictionary with news and dominant topic
    """
    fetcher = NewsFetcher(api_key=api_key)
    return fetcher.fetch_and_summarize(city, country, date)
