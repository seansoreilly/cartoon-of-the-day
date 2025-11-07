"""Tests for cartoon generation functionality."""

import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from src.cartoon_generator import CartoonGenerator, generate_cartoons_from_news


class TestCartoonGenerator:
    """Tests for CartoonGenerator class."""

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_init_with_api_key(self, mock_model, mock_configure, mock_get_key):
        """Test CartoonGenerator initialization with API key."""
        generator = CartoonGenerator(api_key="test-key")
        assert generator.api_key == "test-key"
        mock_configure.assert_called_once_with(api_key="test-key")

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_init_without_api_key(self, mock_model, mock_configure, mock_get_key):
        """Test CartoonGenerator initialization without API key."""
        mock_get_key.return_value = "fetched-key"
        generator = CartoonGenerator()
        assert generator.api_key == "fetched-key"
        mock_configure.assert_called_once_with(api_key="fetched-key")

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_generate_concepts_success(self, mock_model_class, mock_configure, mock_get_key):
        """Test successful cartoon concept generation."""
        mock_get_key.return_value = "test-key"

        # Create valid cartoon data
        valid_response = {
            "topic": "Local Politics",
            "location": "Melbourne, Australia",
            "ideas": [
                {"title": "Cartoon 1", "premise": "Premise 1", "why_funny": "Funny 1"},
                {"title": "Cartoon 2", "premise": "Premise 2", "why_funny": "Funny 2"},
                {"title": "Cartoon 3", "premise": "Premise 3", "why_funny": "Funny 3"},
                {"title": "Cartoon 4", "premise": "Premise 4", "why_funny": "Funny 4"},
                {"title": "Cartoon 5", "premise": "Premise 5", "why_funny": "Funny 5"}
            ],
            "ranking": ["Cartoon 1", "Cartoon 2", "Cartoon 3", "Cartoon 4", "Cartoon 5"],
            "winner": "Cartoon 1"
        }

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(valid_response)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        generator = CartoonGenerator()
        result = generator.generate_concepts("Local Politics", "Melbourne, Australia")

        assert result['topic'] == "Local Politics"
        assert result['location'] == "Melbourne, Australia"
        assert len(result['ideas']) == 5
        assert len(result['ranking']) == 5
        assert result['winner'] == "Cartoon 1"

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_generate_concepts_with_markdown(self, mock_model_class, mock_configure, mock_get_key):
        """Test cartoon generation with markdown-wrapped JSON."""
        mock_get_key.return_value = "test-key"

        valid_response = {
            "topic": "Sports",
            "location": "Paris, France",
            "ideas": [
                {"title": "Cartoon 1", "premise": "Premise 1", "why_funny": "Funny 1"},
                {"title": "Cartoon 2", "premise": "Premise 2", "why_funny": "Funny 2"},
                {"title": "Cartoon 3", "premise": "Premise 3", "why_funny": "Funny 3"},
                {"title": "Cartoon 4", "premise": "Premise 4", "why_funny": "Funny 4"},
                {"title": "Cartoon 5", "premise": "Premise 5", "why_funny": "Funny 5"}
            ],
            "ranking": ["Cartoon 1", "Cartoon 2", "Cartoon 3", "Cartoon 4", "Cartoon 5"],
            "winner": "Cartoon 1"
        }

        mock_model = MagicMock()
        mock_response = MagicMock()
        # Wrap in markdown code block
        mock_response.text = f"```json\n{json.dumps(valid_response)}\n```"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        generator = CartoonGenerator()
        result = generator.generate_concepts("Sports", "Paris, France")

        assert result['topic'] == "Sports"
        assert len(result['ideas']) == 5

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_generate_concepts_error(self, mock_model_class, mock_configure, mock_get_key):
        """Test cartoon generation with error."""
        mock_get_key.return_value = "test-key"

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        generator = CartoonGenerator()
        result = generator.generate_concepts("Topic", "Location")

        assert 'error' in result
        assert len(result['ideas']) == 5  # Fallback response

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_build_generation_prompt(self, mock_model_class, mock_configure, mock_get_key):
        """Test prompt building."""
        mock_get_key.return_value = "test-key"

        generator = CartoonGenerator()
        prompt = generator._build_generation_prompt("Sports", "Paris, France", "News context")

        assert "Sports" in prompt
        assert "Paris, France" in prompt
        assert "News context" in prompt
        # Structured output handles JSON formatting, check for spelling emphasis instead
        assert "spell correctly" in prompt

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_parse_response_valid_json(self, mock_model_class, mock_configure, mock_get_key):
        """Test parsing valid JSON response."""
        mock_get_key.return_value = "test-key"

        valid_data = {
            "topic": "Test",
            "location": "Test Location",
            "ideas": [],
            "ranking": [],
            "winner": ""
        }

        generator = CartoonGenerator()
        result = generator._parse_response(json.dumps(valid_data), "Test", "Test Location")

        assert result['topic'] == "Test"
        assert result['location'] == "Test Location"

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_parse_response_invalid_json(self, mock_model_class, mock_configure, mock_get_key):
        """Test parsing invalid JSON response."""
        mock_get_key.return_value = "test-key"

        generator = CartoonGenerator()
        result = generator._parse_response("Not valid JSON", "Test", "Test Location")

        # Should return fallback response
        assert result['topic'] == "Test"
        assert result['location'] == "Test Location"
        assert len(result['ideas']) == 5

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_fix_cartoon_data(self, mock_model_class, mock_configure, mock_get_key):
        """Test fixing invalid cartoon data."""
        mock_get_key.return_value = "test-key"

        invalid_data = {
            "topic": "Test",
            "location": "Test Location",
            "ideas": [
                {"title": "Only One"}
            ],
            "ranking": []
        }

        generator = CartoonGenerator()
        result = generator._fix_cartoon_data(invalid_data, "Test", "Test Location")

        assert len(result['ideas']) == 5
        assert len(result['ranking']) == 5
        assert 'winner' in result

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_create_fallback_response(self, mock_model_class, mock_configure, mock_get_key):
        """Test creating fallback response."""
        mock_get_key.return_value = "test-key"

        generator = CartoonGenerator()
        result = generator._create_fallback_response("Test Topic", "Test Location", "Error")

        assert result['topic'] == "Test Topic"
        assert result['location'] == "Test Location"
        assert len(result['ideas']) == 5
        assert len(result['ranking']) == 5
        assert 'winner' in result
        assert 'error' in result

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_get_winner(self, mock_model_class, mock_configure, mock_get_key):
        """Test extracting winner from cartoon data."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            "topic": "Sports",
            "location": "Paris, France",
            "ideas": [
                {"title": "Winner Cartoon", "premise": "Winning premise", "why_funny": "Very funny"},
                {"title": "Other Cartoon", "premise": "Other premise", "why_funny": "Also funny"}
            ],
            "ranking": ["Winner Cartoon", "Other Cartoon"],
            "winner": "Winner Cartoon"
        }

        generator = CartoonGenerator()
        winner = generator.get_winner(cartoon_data)

        assert winner['title'] == "Winner Cartoon"
        assert winner['premise'] == "Winning premise"
        assert winner['why_funny'] == "Very funny"

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_get_winner_not_found(self, mock_model_class, mock_configure, mock_get_key):
        """Test getting winner when winner not in ideas."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            "ideas": [
                {"title": "First", "premise": "First premise", "why_funny": "Funny"}
            ],
            "winner": "Nonexistent"
        }

        generator = CartoonGenerator()
        winner = generator.get_winner(cartoon_data)

        # Should fall back to first idea
        assert winner['title'] == "First"

    @patch('src.cartoon_generator.get_api_key')
    @patch('src.cartoon_generator.genai.configure')
    @patch('src.cartoon_generator.genai.GenerativeModel')
    def test_rank_concepts(self, mock_model_class, mock_configure, mock_get_key):
        """Test ranking concepts in order."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            "ideas": [
                {"title": "Third", "premise": "3rd", "why_funny": "Funny"},
                {"title": "First", "premise": "1st", "why_funny": "Funny"},
                {"title": "Second", "premise": "2nd", "why_funny": "Funny"}
            ],
            "ranking": ["First", "Second", "Third"]
        }

        generator = CartoonGenerator()
        ranked = generator.rank_concepts(cartoon_data)

        assert ranked[0]['title'] == "First"
        assert ranked[1]['title'] == "Second"
        assert ranked[2]['title'] == "Third"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch('src.cartoon_generator.CartoonGenerator')
    def test_generate_cartoons_from_news(self, mock_generator_class):
        """Test generate_cartoons_from_news convenience function."""
        mock_generator = MagicMock()
        mock_generator.generate_concepts.return_value = {
            "topic": "Test Topic",
            "location": "Test Location",
            "ideas": [],
            "ranking": [],
            "winner": ""
        }
        mock_generator_class.return_value = mock_generator

        news_data = {
            'dominant_topic': 'Test Topic',
            'location': 'Test Location',
            'summary': 'Test summary'
        }

        result = generate_cartoons_from_news(news_data, "test-api-key")

        assert result['topic'] == "Test Topic"
        assert result['location'] == "Test Location"
        mock_generator_class.assert_called_once_with(api_key="test-api-key")
        mock_generator.generate_concepts.assert_called_once_with(
            'Test Topic',
            'Test Location',
            'Test summary',
            []
        )

    @patch('src.cartoon_generator.CartoonGenerator')
    def test_generate_cartoons_from_news_missing_data(self, mock_generator_class):
        """Test generating cartoons with missing news data."""
        mock_generator = MagicMock()
        mock_generator.generate_concepts.return_value = {
            "topic": "General News",
            "location": "Unknown",
            "ideas": [],
            "ranking": [],
            "winner": ""
        }
        mock_generator_class.return_value = mock_generator

        news_data = {}

        result = generate_cartoons_from_news(news_data)

        # Should use defaults
        mock_generator.generate_concepts.assert_called_once()
        call_args = mock_generator.generate_concepts.call_args[0]
        assert call_args[0] == 'General News'
        assert call_args[1] == 'Unknown'
