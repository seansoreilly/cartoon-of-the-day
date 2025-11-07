#!/usr/bin/env python3
"""
Run news story retrieval tests and display the results in a readable format.

This script demonstrates how news stories are retrieved and formatted.
"""

import sys
from unittest.mock import MagicMock, patch
from src.news_fetcher import NewsFetcher


def display_news_stories():
    """Display example news stories retrieved from the news fetcher."""

    print("\n" + "=" * 80)
    print("  🌍 NEWS STORY RETRIEVAL DEMONSTRATION")
    print("=" * 80 + "\n")

    # Mock data simulating real NewsAPI response
    mock_articles = [
        {
            "title": "Melbourne heatwave causes traffic chaos on main roads",
            "description": "Extreme temperatures in Melbourne caused significant traffic disruptions today",
            "url": "https://news.example.com/melbourne-heat-1",
            "source": {"name": "News Today"},
        },
        {
            "title": "Melbourne startup raises funding milestone",
            "description": "A Melbourne-based tech company announced record funding round",
            "url": "https://news.example.com/melbourne-startup",
            "source": {"name": "Tech News"},
        },
        {
            "title": "Melbourne arts festival announces 2025 program",
            "description": "The annual Melbourne arts festival has revealed its diverse lineup",
            "url": "https://news.example.com/melbourne-arts",
            "source": {"name": "Arts Weekly"},
        },
        {
            "title": "New bike lanes open in Melbourne CBD",
            "description": "City council completed expansion of bicycle infrastructure in Melbourne",
            "url": "https://news.example.com/melbourne-bikes",
            "source": {"name": "City News"},
        },
        {
            "title": "Melbourne weather: Summer forecast looks intense",
            "description": "Meteorologists predict Melbourne will experience hot and dry summer conditions",
            "url": "https://news.example.com/melbourne-weather",
            "source": {"name": "Weather Hub"},
        },
    ]

    # Mock the requests.get call
    with patch('src.news_fetcher.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": mock_articles}
        mock_get.return_value = mock_response

        # Fetch news using the fetcher
        fetcher = NewsFetcher(api_key="demo-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", num_headlines=5)

    # Display the results
    print(f"📍 LOCATION: {result['location']}")
    print(f"📅 DATE: {result['date']}")
    print(f"🔄 SORT BY: {result.get('sort_by', 'popularity')} (trending stories)")
    print(f"📰 SOURCE: {result['source']}")
    print(f"📊 STORIES RETRIEVED: {len(result['headlines'])}\n")

    print("-" * 80)
    print("  RETRIEVED HEADLINES")
    print("-" * 80 + "\n")

    # Display each story
    for i, headline in enumerate(result['headlines'], 1):
        print(f"Story {i}:")
        print(f"  ✓ Title: {headline['title']}")
        print(f"  ✓ Summary: {headline['summary']}")
        print(f"  ✓ Source: {headline['source']}")
        print(f"  ✓ URL: {headline['url']}")
        print()

    # Display summary
    print("-" * 80)
    print("  NEWS SUMMARY (for cartoon generation)")
    print("-" * 80 + "\n")

    summary = fetcher.get_news_summary(result)
    print(summary)

    print("\n" + "-" * 80)
    print("  DOMINANT TOPIC (used for cartoon concept generation)")
    print("-" * 80 + "\n")

    dominant_topic = fetcher.select_dominant_topic(result)
    print(f"Topic: {dominant_topic}\n")

    print("=" * 80)
    print("✅ News retrieval test completed successfully!")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = display_news_stories()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error running news retrieval test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
