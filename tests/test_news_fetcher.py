"""Tests for news fetching functionality."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from src.news_fetcher import NewsFetcher, fetch_news_for_location


class TestNewsFetcher:
    """Tests for NewsFetcher class."""

    def test_init_with_api_key(self):
        """Test NewsFetcher initialization with API key."""
        fetcher = NewsFetcher(api_key="test-key")
        assert fetcher.api_key == "test-key"
        assert fetcher.base_url == "https://newsapi.org/v2"

    @patch.dict('os.environ', {'NEWSAPI_KEY': 'env-key'})
    def test_init_without_api_key_uses_env(self):
        """Test NewsFetcher initialization without API key uses environment variable."""
        fetcher = NewsFetcher()
        assert fetcher.api_key == "env-key"

    def test_init_without_api_key_no_env(self):
        """Test NewsFetcher initialization without API key and no environment variable."""
        with patch.dict('os.environ', {}, clear=True):
            fetcher = NewsFetcher()
            assert fetcher.api_key is None

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_success(self, mock_get):
        """Test successful news fetching from NewsAPI."""
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Local Event in Melbourne",
                    "description": "Something happened in the city of Melbourne"
                },
                {
                    "title": "Melbourne City News - Government Announcement",
                    "description": "More news from the Melbourne municipality"
                },
                {
                    "title": "City News - Government Announcement",
                    "description": "Unrelated global news that should be filtered out"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", "2025-11-03", num_headlines=2)

        assert result['location'] == "Melbourne, Australia"
        assert result['date'] == "2025-11-03"
        assert len(result['headlines']) == 2  # Only Melbourne-related articles
        assert "Melbourne" in result['headlines'][0]['title']
        assert result['source'] == "NewsAPI"

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_with_default_date(self, mock_get):
        """Test news fetching with default date."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Paris News",
                    "description": "French capital news"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Paris", "France")

        # Should use current date
        assert 'date' in result
        assert result['date'] == datetime.now().strftime("%Y-%m-%d")

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_api_error(self, mock_get):
        """Test news fetching with API error falls back to fictional news."""
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia")

        # Should fall back to fictional news
        assert result['source'] == "Fictional (NEWSAPI_KEY not configured)" or "Fictional" in result['source']
        assert len(result['headlines']) > 0

    @patch.dict('os.environ', {'NEWSAPI_KEY': ''})
    def test_fetch_local_news_no_api_key(self):
        """Test news fetching without API key returns fictional news."""
        fetcher = NewsFetcher(api_key=None)
        result = fetcher.fetch_local_news("Melbourne", "Australia", "2025-11-03")

        # Should use fictional news
        assert result['source'] == "Fictional (NEWSAPI_KEY not configured)"
        assert len(result['headlines']) > 0
        assert result['location'] == "Melbourne, Australia"

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_empty_results(self, mock_get):
        """Test news fetching with empty results falls back to fictional news."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia")

        # Should fall back to fictional news
        assert len(result['headlines']) > 0

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_request_exception(self, mock_get):
        """Test news fetching with request exception falls back to fictional news."""
        mock_get.side_effect = Exception("Connection error")

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia")

        # Should fall back to fictional news
        assert len(result['headlines']) > 0

    def test_get_news_summary_with_headlines(self):
        """Test news summary generation with headlines."""
        news_data = {
            'headlines': [
                {'title': 'Headline 1', 'summary': 'Summary 1'},
                {'title': 'Headline 2', 'summary': 'Summary 2'},
                {'title': 'Headline 3', 'summary': 'Summary 3'}
            ]
        }

        fetcher = NewsFetcher(api_key="test-key")
        summary = fetcher.get_news_summary(news_data)

        assert "1. Headline 1" in summary
        assert "2. Headline 2" in summary
        assert "3. Headline 3" in summary

    def test_get_news_summary_empty(self):
        """Test news summary with no headlines."""
        news_data = {'headlines': []}

        fetcher = NewsFetcher(api_key="test-key")
        summary = fetcher.get_news_summary(news_data)

        assert summary == "No news available"

    def test_get_news_summary_no_headlines_key(self):
        """Test news summary with missing headlines key."""
        news_data = {}

        fetcher = NewsFetcher(api_key="test-key")
        summary = fetcher.get_news_summary(news_data)

        assert summary == "No news available"

    def test_select_dominant_topic_from_data(self):
        """Test selecting dominant topic from news data."""
        news_data = {
            'dominant_topic': 'Local Politics',
            'headlines': [
                {'title': 'Political News', 'summary': 'Summary'}
            ]
        }

        fetcher = NewsFetcher(api_key="test-key")
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'Local Politics'

    def test_select_dominant_topic_fallback_to_headline(self):
        """Test selecting dominant topic falls back to first headline."""
        news_data = {
            'headlines': [
                {'title': 'First Headline', 'summary': 'Summary'}
            ]
        }

        fetcher = NewsFetcher(api_key="test-key")
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'First Headline'

    def test_select_dominant_topic_default(self):
        """Test selecting dominant topic with no data."""
        news_data = {}

        fetcher = NewsFetcher(api_key="test-key")
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'General News'

    def test_select_dominant_topic_ignores_error_state(self):
        """Test selecting dominant topic ignores error state."""
        news_data = {
            'dominant_topic': 'Error',
            'headlines': [
                {'title': 'Real Headline', 'summary': 'Summary'}
            ]
        }

        fetcher = NewsFetcher(api_key="test-key")
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'Real Headline'

    @patch.object(NewsFetcher, 'fetch_local_news')
    @patch.object(NewsFetcher, 'select_dominant_topic')
    @patch.object(NewsFetcher, 'get_news_summary')
    def test_fetch_and_summarize(self, mock_summary, mock_topic, mock_fetch):
        """Test fetch_and_summarize combines all data."""
        news_data = {
            'location': 'Melbourne, Australia',
            'date': '2025-11-03',
            'headlines': []
        }

        mock_fetch.return_value = news_data
        mock_topic.return_value = 'Local News'
        mock_summary.return_value = 'News summary'

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_and_summarize("Melbourne", "Australia", "2025-11-03")

        assert result['news_data'] == news_data
        assert result['dominant_topic'] == 'Local News'
        assert result['summary'] == 'News summary'
        assert result['location'] == 'Melbourne, Australia'
        assert result['date'] == '2025-11-03'

    @patch.object(NewsFetcher, 'fetch_local_news')
    def test_fetch_and_summarize_without_date(self, mock_fetch):
        """Test fetch_and_summarize without explicit date."""
        news_data = {
            'location': 'Tokyo, Japan',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'headlines': []
        }

        mock_fetch.return_value = news_data

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_and_summarize("Tokyo", "Japan")

        assert result['date'] == datetime.now().strftime("%Y-%m-%d")


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch('src.news_fetcher.NewsFetcher.fetch_and_summarize')
    def test_fetch_news_for_location(self, mock_fetch_and_summarize):
        """Test fetch_news_for_location convenience function."""
        expected_result = {
            'news_data': {},
            'dominant_topic': 'Test Topic',
            'summary': 'Test summary',
            'location': 'Test City, Test Country',
            'date': '2025-11-03'
        }
        mock_fetch_and_summarize.return_value = expected_result

        result = fetch_news_for_location(
            "Test City",
            "Test Country",
            "2025-11-03",
            "test-api-key"
        )

        assert result['dominant_topic'] == 'Test Topic'
        assert result['location'] == 'Test City, Test Country'

    @patch('src.news_fetcher.NewsFetcher.fetch_and_summarize')
    def test_fetch_news_for_location_without_date(self, mock_fetch_and_summarize):
        """Test fetch_news_for_location without date."""
        expected_result = {
            'news_data': {},
            'dominant_topic': 'Test Topic',
            'summary': 'Test summary',
            'location': 'Test City, Test Country',
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        mock_fetch_and_summarize.return_value = expected_result

        result = fetch_news_for_location("Test City", "Test Country")

        assert 'date' in result
        assert result['dominant_topic'] == 'Test Topic'

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_with_sort_by_popularity(self, mock_get):
        """Test news fetching with sort_by='popularity' parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Melbourne trending story",
                    "description": "Trending news in Melbourne"
                },
                {
                    "title": "Melbourne recent story",
                    "description": "Recent news in Melbourne"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news(
            "Melbourne", "Australia", sort_by="popularity"
        )

        # Verify the API was called with popularity sorting
        call_args = mock_get.call_args
        assert call_args[1]['params']['sortBy'] == 'popularity'
        assert result['location'] == "Melbourne, Australia"

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_with_sort_by_publishedAt(self, mock_get):
        """Test news fetching with sort_by='publishedAt' parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Melbourne latest",
                    "description": "Latest news in Melbourne"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news(
            "Melbourne", "Australia", sort_by="publishedAt"
        )

        # Verify the API was called with publishedAt sorting
        call_args = mock_get.call_args
        assert call_args[1]['params']['sortBy'] == 'publishedAt'

    @patch('src.news_fetcher.requests.get')
    def test_fetch_local_news_with_invalid_sort_by(self, mock_get):
        """Test news fetching with invalid sort_by falls back to popularity."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Melbourne news",
                    "description": "News in Melbourne"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news(
            "Melbourne", "Australia", sort_by="invalid_sort"
        )

        # Should fall back to popularity
        call_args = mock_get.call_args
        assert call_args[1]['params']['sortBy'] == 'popularity'

    @patch.object(NewsFetcher, 'fetch_local_news')
    def test_fetch_and_summarize_with_sort_by(self, mock_fetch):
        """Test fetch_and_summarize passes sort_by parameter."""
        news_data = {
            'location': 'Melbourne, Australia',
            'date': '2025-11-03',
            'headlines': [{'title': 'Test', 'summary': 'Test'}]
        }
        mock_fetch.return_value = news_data

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_and_summarize(
            "Melbourne", "Australia", sort_by="popularity"
        )

        # Verify sort_by was passed and included in result
        mock_fetch.assert_called_once_with(
            "Melbourne", "Australia", None, sort_by="popularity"
        )
        assert result['sort_by'] == 'popularity'

    @patch('src.news_fetcher.NewsFetcher.fetch_and_summarize')
    def test_fetch_news_for_location_with_sort_by(self, mock_fetch_and_summarize):
        """Test fetch_news_for_location passes sort_by parameter."""
        expected_result = {
            'news_data': {},
            'dominant_topic': 'Test Topic',
            'summary': 'Test summary',
            'location': 'Test City, Test Country',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'sort_by': 'popularity'
        }
        mock_fetch_and_summarize.return_value = expected_result

        result = fetch_news_for_location(
            "Test City", "Test Country", sort_by="popularity"
        )

        assert result['sort_by'] == 'popularity'


class TestNewsStoriesRetrieval:
    """Tests demonstrating news stories being retrieved."""

    @patch('src.news_fetcher.requests.get')
    def test_news_stories_retrieved_with_details(self, mock_get):
        """Test that news stories are retrieved with complete details.

        This test demonstrates:
        - News articles are fetched from NewsAPI
        - Stories are filtered by location
        - Complete story details are preserved (title, summary, URL, source)
        """
        # Mock multiple news articles
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Melbourne heatwave causes traffic chaos on main roads",
                    "description": "Extreme temperatures in Melbourne caused significant traffic disruptions today",
                    "url": "https://news.example.com/melbourne-heat-1",
                    "source": {"name": "News Today"},
                    "urlToImage": "https://example.com/image1.jpg"
                },
                {
                    "title": "Melbourne startup raises funding milestone",
                    "description": "A Melbourne-based tech company announced record funding round",
                    "url": "https://news.example.com/melbourne-startup",
                    "source": {"name": "Tech News"},
                    "urlToImage": "https://example.com/image2.jpg"
                },
                {
                    "title": "Melbourne arts festival announces 2025 program",
                    "description": "The annual Melbourne arts festival has revealed its diverse lineup",
                    "url": "https://news.example.com/melbourne-arts",
                    "source": {"name": "Arts Weekly"},
                    "urlToImage": "https://example.com/image3.jpg"
                },
                {
                    "title": "New bike lanes open in Melbourne CBD",
                    "description": "City council completed expansion of bicycle infrastructure in Melbourne",
                    "url": "https://news.example.com/melbourne-bikes",
                    "source": {"name": "City News"},
                    "urlToImage": "https://example.com/image4.jpg"
                },
                {
                    "title": "Melbourne weather: Summer forecast looks intense",
                    "description": "Meteorologists predict Melbourne will experience hot and dry summer conditions",
                    "url": "https://news.example.com/melbourne-weather",
                    "source": {"name": "Weather Hub"},
                    "urlToImage": "https://example.com/image5.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", num_headlines=5)

        # Verify stories were retrieved
        assert result is not None
        assert 'headlines' in result
        headlines = result['headlines']

        # Verify we got the expected number of stories
        assert len(headlines) == 5, f"Expected 5 headlines, got {len(headlines)}"

        # Verify each story has complete details
        for i, headline in enumerate(headlines, 1):
            assert 'title' in headline, f"Story {i} missing title"
            assert 'summary' in headline, f"Story {i} missing summary"
            assert 'url' in headline, f"Story {i} missing url"
            assert 'source' in headline, f"Story {i} missing source"

            # Verify values are not empty
            assert headline['title'], f"Story {i} has empty title"
            assert headline['url'], f"Story {i} has empty url"
            assert headline['source'], f"Story {i} has empty source"

        # Verify story content
        story_titles = [h['title'] for h in headlines]
        assert "Melbourne heatwave causes traffic chaos on main roads" in story_titles
        assert "Melbourne startup raises funding milestone" in story_titles
        assert "Melbourne arts festival announces 2025 program" in story_titles

        # Verify location metadata
        assert result['location'] == "Melbourne, Australia"
        assert result['source'] == "NewsAPI"

    @patch('src.news_fetcher.requests.get')
    def test_news_stories_filtered_by_location(self, mock_get):
        """Test that news stories are properly filtered by location.

        Demonstrates:
        - Stories about the specific location are included
        - Non-location stories are filtered out
        - Location matching prioritizes title over description
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Tokyo launches new subway line",  # Not Melbourne
                    "description": "Japanese capital opens transportation",
                    "url": "https://news.example.com/tokyo-1",
                    "source": {"name": "News"},
                    "urlToImage": "https://example.com/img.jpg"
                },
                {
                    "title": "Melbourne weather update",  # Melbourne in title
                    "description": "Local conditions report",
                    "url": "https://news.example.com/melbourne-weather",
                    "source": {"name": "News"},
                    "urlToImage": "https://example.com/img.jpg"
                },
                {
                    "title": "Technology trends",  # Generic title
                    "description": "New developments in Melbourne technology sector",  # Melbourne in description
                    "url": "https://news.example.com/tech-1",
                    "source": {"name": "News"},
                    "urlToImage": "https://example.com/img.jpg"
                },
                {
                    "title": "Melbourne's famous landmarks attract tourists",  # Melbourne in title
                    "description": "Popular destinations worldwide",
                    "url": "https://news.example.com/landmarks",
                    "source": {"name": "News"},
                    "urlToImage": "https://example.com/img.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", num_headlines=5)

        headlines = result['headlines']

        # Verify filtering: should include Melbourne stories, exclude Tokyo story
        titles = [h['title'] for h in headlines]

        # Melbourne stories should be included
        assert any("Melbourne" in title for title in titles), \
            f"No Melbourne stories found. Got: {titles}"

        # Non-Melbourne stories should be filtered out
        assert not any("Tokyo" in title for title in titles), \
            "Tokyo story should have been filtered out"

    @patch('src.news_fetcher.requests.get')
    def test_news_stories_with_sorting_method(self, mock_get):
        """Test that news stories are retrieved with specified sorting.

        Demonstrates:
        - Default sorting is 'popularity' (trending stories)
        - API is called with correct sortBy parameter
        - Different sorting methods can be specified
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Trending story in Melbourne",
                    "description": "This is a viral story",
                    "url": "https://news.example.com/trending-1",
                    "source": {"name": "Popular News"},
                    "urlToImage": "https://example.com/img.jpg"
                },
                {
                    "title": "Another Melbourne story",
                    "description": "Also popular content",
                    "url": "https://news.example.com/trending-2",
                    "source": {"name": "Viral News"},
                    "urlToImage": "https://example.com/img.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")

        # Test default (popularity)
        result = fetcher.fetch_local_news("Melbourne", "Australia")
        call_args = mock_get.call_args
        assert call_args[1]['params']['sortBy'] == 'popularity', \
            "Default should be 'popularity'"
        assert len(result['headlines']) > 0, "Should retrieve stories with default sorting"

        # Test with explicit sorting
        mock_get.reset_mock()
        result = fetcher.fetch_local_news("Melbourne", "Australia", sort_by="publishedAt")
        call_args = mock_get.call_args
        assert call_args[1]['params']['sortBy'] == 'publishedAt', \
            "Should use specified sortBy parameter"

    @patch('src.news_fetcher.requests.get')
    def test_news_stories_summary_generation(self, mock_get):
        """Test that news story summaries are properly generated.

        Demonstrates:
        - Story summaries are created from full descriptions
        - Summaries are limited in length
        - Summary includes story title and context
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Melbourne traffic reaches record levels",
                    "description": "A very long description about traffic conditions in Melbourne that goes on and on with lots of details about the causes and effects of traffic congestion on roads throughout the city and surrounding suburbs",
                    "url": "https://news.example.com/traffic",
                    "source": {"name": "Traffic News"},
                    "urlToImage": "https://example.com/img.jpg"
                },
                {
                    "title": "New Melbourne restaurant opens to great reviews",
                    "description": "Short description",
                    "url": "https://news.example.com/restaurant",
                    "source": {"name": "Food News"},
                    "urlToImage": "https://example.com/img.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", num_headlines=2)

        headlines = result['headlines']
        assert len(headlines) == 2

        # Verify summaries exist and are properly formatted
        for headline in headlines:
            assert 'summary' in headline
            assert len(headline['summary']) > 0
            # Summaries should be capped at ~150 chars (based on code)
            assert len(headline['summary']) <= 160

    def test_news_stories_display_format(self):
        """Test that retrieved news stories can be displayed properly.

        Demonstrates the format of news data after retrieval:
        - Location and date information
        - List of headlines with summaries
        - Dominant topic extraction
        - Summary text generation
        """
        # Example of what fetched news looks like
        news_data = {
            "location": "Melbourne, Australia",
            "date": "2025-11-07",
            "headlines": [
                {
                    "title": "Melbourne startup wins innovation award",
                    "summary": "A Melbourne-based tech company was recognized for groundbreaking work",
                    "url": "https://news.example.com/award",
                    "source": "Tech Weekly"
                },
                {
                    "title": "New park opens in Melbourne's west",
                    "summary": "City council unveiled major green space development",
                    "url": "https://news.example.com/park",
                    "source": "City News"
                },
                {
                    "title": "Melbourne weather: sunny week ahead",
                    "summary": "Forecast shows good conditions for the week",
                    "url": "https://news.example.com/weather",
                    "source": "Weather Service"
                }
            ],
            "dominant_topic": "Melbourne Innovation",
            "source": "NewsAPI"
        }

        # Verify the structure
        assert news_data['location'] == "Melbourne, Australia"
        assert len(news_data['headlines']) == 3
        assert news_data['source'] == "NewsAPI"

        # Verify each headline can be displayed
        for headline in news_data['headlines']:
            assert headline['title']
            assert headline['summary']
            assert headline['url']
            assert headline['source']

        # Verify summary text generation
        fetcher = NewsFetcher(api_key="test-key")
        summary = fetcher.get_news_summary(news_data)

        assert "1. Melbourne startup wins innovation award" in summary
        assert "2. New park opens in Melbourne's west" in summary
        assert "3. Melbourne weather: sunny week ahead" in summary
