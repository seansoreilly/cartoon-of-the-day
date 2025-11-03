"""Tests for news fetching functionality."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from src.news_fetcher import NewsFetcher, fetch_news_for_location


class TestNewsFetcher:
    """Tests for NewsFetcher class."""

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_init_with_api_key(self, mock_configure, mock_get_key):
        """Test NewsFetcher initialization with API key."""
        fetcher = NewsFetcher(api_key="test-key")
        assert fetcher.api_key == "test-key"
        mock_configure.assert_called_once_with(api_key="test-key")

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_init_without_api_key(self, mock_configure, mock_get_key):
        """Test NewsFetcher initialization without API key."""
        mock_get_key.return_value = "fetched-key"
        fetcher = NewsFetcher()
        assert fetcher.api_key == "fetched-key"
        mock_configure.assert_called_once_with(api_key="fetched-key")

    @patch('src.news_fetcher.genai.GenerativeModel')
    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_fetch_local_news_success(self, mock_configure, mock_get_key, mock_model_class):
        """Test successful news fetching."""
        mock_get_key.return_value = "test-key"

        # Mock the model and response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "location": "Melbourne, Australia",
            "date": "2025-11-03",
            "headlines": [
                {"title": "Local Event", "summary": "Something happened"},
                {"title": "City News", "summary": "More news"}
            ],
            "dominant_topic": "Local Events"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        fetcher = NewsFetcher()
        result = fetcher.fetch_local_news("Melbourne", "Australia", "2025-11-03")

        assert result['location'] == "Melbourne, Australia"
        assert result['date'] == "2025-11-03"
        assert len(result['headlines']) == 2
        assert result['dominant_topic'] == "Local Events"

    @patch('src.news_fetcher.genai.GenerativeModel')
    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_fetch_local_news_with_default_date(
        self,
        mock_configure,
        mock_get_key,
        mock_model_class
    ):
        """Test news fetching with default date."""
        mock_get_key.return_value = "test-key"

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"location": "Paris, France", "date": "2025-11-03", "headlines": [], "dominant_topic": "News"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        fetcher = NewsFetcher()
        result = fetcher.fetch_local_news("Paris", "France")

        # Should use current date
        assert 'date' in result
        assert result['date'] == datetime.now().strftime("%Y-%m-%d")

    @patch('src.news_fetcher.genai.GenerativeModel')
    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_fetch_local_news_error(self, mock_configure, mock_get_key, mock_model_class):
        """Test news fetching with error."""
        mock_get_key.return_value = "test-key"

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        fetcher = NewsFetcher()
        result = fetcher.fetch_local_news("Melbourne", "Australia")

        assert 'error' in result
        assert result['dominant_topic'] == "Error"

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_get_news_summary_with_headlines(self, mock_configure, mock_get_key):
        """Test news summary generation with headlines."""
        mock_get_key.return_value = "test-key"

        news_data = {
            'headlines': [
                {'title': 'Headline 1', 'summary': 'Summary 1'},
                {'title': 'Headline 2', 'summary': 'Summary 2'},
                {'title': 'Headline 3', 'summary': 'Summary 3'}
            ]
        }

        fetcher = NewsFetcher()
        summary = fetcher.get_news_summary(news_data)

        assert "1. Headline 1" in summary
        assert "2. Headline 2" in summary
        assert "3. Headline 3" in summary

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_get_news_summary_empty(self, mock_configure, mock_get_key):
        """Test news summary with no headlines."""
        mock_get_key.return_value = "test-key"

        news_data = {'headlines': []}

        fetcher = NewsFetcher()
        summary = fetcher.get_news_summary(news_data)

        assert summary == "No news available"

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_select_dominant_topic_from_data(self, mock_configure, mock_get_key):
        """Test selecting dominant topic from news data."""
        mock_get_key.return_value = "test-key"

        news_data = {
            'dominant_topic': 'Local Politics',
            'headlines': [
                {'title': 'Political News', 'summary': 'Summary'}
            ]
        }

        fetcher = NewsFetcher()
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'Local Politics'

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_select_dominant_topic_fallback_to_headline(self, mock_configure, mock_get_key):
        """Test selecting dominant topic falls back to first headline."""
        mock_get_key.return_value = "test-key"

        news_data = {
            'headlines': [
                {'title': 'First Headline', 'summary': 'Summary'}
            ]
        }

        fetcher = NewsFetcher()
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'First Headline'

    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_select_dominant_topic_default(self, mock_configure, mock_get_key):
        """Test selecting dominant topic with no data."""
        mock_get_key.return_value = "test-key"

        news_data = {}

        fetcher = NewsFetcher()
        topic = fetcher.select_dominant_topic(news_data)

        assert topic == 'General News'

    @patch.object(NewsFetcher, 'fetch_local_news')
    @patch.object(NewsFetcher, 'select_dominant_topic')
    @patch.object(NewsFetcher, 'get_news_summary')
    @patch('src.news_fetcher.get_api_key')
    @patch('src.news_fetcher.genai.configure')
    def test_fetch_and_summarize(
        self,
        mock_configure,
        mock_get_key,
        mock_summary,
        mock_topic,
        mock_fetch
    ):
        """Test fetch_and_summarize combines all data."""
        mock_get_key.return_value = "test-key"

        news_data = {
            'location': 'Melbourne, Australia',
            'date': '2025-11-03',
            'headlines': []
        }

        mock_fetch.return_value = news_data
        mock_topic.return_value = 'Local News'
        mock_summary.return_value = 'News summary'

        fetcher = NewsFetcher()
        result = fetcher.fetch_and_summarize("Melbourne", "Australia", "2025-11-03")

        assert result['news_data'] == news_data
        assert result['dominant_topic'] == 'Local News'
        assert result['summary'] == 'News summary'
        assert result['location'] == 'Melbourne, Australia'
        assert result['date'] == '2025-11-03'


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch('src.news_fetcher.NewsFetcher')
    def test_fetch_news_for_location(self, mock_fetcher_class):
        """Test fetch_news_for_location convenience function."""
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_and_summarize.return_value = {
            'news_data': {},
            'dominant_topic': 'Test Topic',
            'summary': 'Test summary',
            'location': 'Test City, Test Country',
            'date': '2025-11-03'
        }
        mock_fetcher_class.return_value = mock_fetcher

        result = fetch_news_for_location(
            "Test City",
            "Test Country",
            "2025-11-03",
            "test-api-key"
        )

        assert result['dominant_topic'] == 'Test Topic'
        assert result['location'] == 'Test City, Test Country'
        mock_fetcher_class.assert_called_once_with(api_key="test-api-key")

    @patch('src.news_fetcher.NewsFetcher')
    def test_fetch_news_for_location_without_date(self, mock_fetcher_class):
        """Test fetch_news_for_location without date."""
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_and_summarize.return_value = {
            'news_data': {},
            'dominant_topic': 'Test Topic',
            'summary': 'Test summary',
            'location': 'Test City, Test Country',
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        mock_fetcher_class.return_value = mock_fetcher

        result = fetch_news_for_location("Test City", "Test Country")

        assert 'date' in result
        mock_fetcher.fetch_and_summarize.assert_called_once()
