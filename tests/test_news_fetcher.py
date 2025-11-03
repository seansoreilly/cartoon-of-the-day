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
                    "description": "Something happened in the city"
                },
                {
                    "title": "City News - Government Announcement",
                    "description": "More news from the municipality"
                }
            ]
        }
        mock_get.return_value = mock_response

        fetcher = NewsFetcher(api_key="test-key")
        result = fetcher.fetch_local_news("Melbourne", "Australia", "2025-11-03")

        assert result['location'] == "Melbourne, Australia"
        assert result['date'] == "2025-11-03"
        assert len(result['headlines']) == 2
        assert result['headlines'][0]['title'] == "Local Event in Melbourne"
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
