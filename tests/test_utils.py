"""Tests for utility functions."""

import pytest
from datetime import datetime
from pathlib import Path
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from src.utils import (
    save_cartoon_data,
    get_local_time,
    format_date_for_location,
    sanitize_filename,
    validate_location_data,
    validate_cartoon_data
)


class TestSaveCartoonData:
    """Tests for save_cartoon_data function."""

    def test_save_cartoon_data_creates_file(self, tmp_path):
        """Test that cartoon data is saved to a JSON file."""
        # Setup
        with patch('src.utils.Path', return_value=tmp_path):
            cartoon_data = {
                "topic": "Local Politics",
                "location": "Melbourne",
                "ideas": [
                    {
                        "title": "Test Cartoon",
                        "premise": "A funny premise",
                        "why_funny": "It's hilarious"
                    }
                ],
                "ranking": ["Test Cartoon"],
                "winner": "Test Cartoon"
            }

            # Execute
            with patch('src.utils.Path.mkdir'):
                output_path = save_cartoon_data("Melbourne", cartoon_data)

            # Verify
            assert output_path is not None

    def test_save_cartoon_data_includes_metadata(self):
        """Test that saved data includes metadata."""
        cartoon_data = {
            "topic": "Local Politics",
            "location": "Melbourne",
            "ideas": [],
            "ranking": [],
            "winner": "Test"
        }

        with patch('src.utils.Path.mkdir'), \
             patch('builtins.open', MagicMock()):
            save_cartoon_data("Melbourne", cartoon_data)

            # Verify metadata was added
            assert "metadata" in cartoon_data
            assert "location" in cartoon_data["metadata"]
            assert "generated_at" in cartoon_data["metadata"]


class TestGetLocalTime:
    """Tests for get_local_time function."""

    def test_get_local_time_returns_datetime(self):
        """Test that get_local_time returns a datetime object."""
        # Melbourne coordinates
        result = get_local_time(-37.8136, 144.9631)
        assert isinstance(result, datetime)

    def test_get_local_time_with_invalid_coords(self):
        """Test get_local_time with invalid coordinates."""
        # Should fallback to UTC
        result = get_local_time(999, 999)
        assert isinstance(result, datetime)


class TestFormatDateForLocation:
    """Tests for format_date_for_location function."""

    def test_format_date_returns_string(self):
        """Test that format returns a string."""
        result = format_date_for_location(-37.8136, 144.9631)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_date_contains_date_elements(self):
        """Test that formatted string contains expected elements."""
        result = format_date_for_location(-37.8136, 144.9631)
        # Should contain a day name and month
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert any(day in result for day in days)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_sanitize_removes_invalid_chars(self):
        """Test that invalid characters are removed."""
        result = sanitize_filename("test/file:name*?.txt")
        assert "/" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result

    def test_sanitize_replaces_spaces(self):
        """Test that spaces are replaced with underscores."""
        result = sanitize_filename("test file name")
        assert " " not in result
        assert "_" in result

    def test_sanitize_preserves_valid_chars(self):
        """Test that valid characters are preserved."""
        result = sanitize_filename("test-file_name.txt")
        assert result == "test-file_name.txt"


class TestValidateLocationData:
    """Tests for validate_location_data function."""

    def test_validate_with_valid_data(self):
        """Test validation with valid location data."""
        data = {"latitude": -37.8136, "longitude": 144.9631}
        assert validate_location_data(data) is True

    def test_validate_with_missing_latitude(self):
        """Test validation fails with missing latitude."""
        data = {"longitude": 144.9631}
        assert validate_location_data(data) is False

    def test_validate_with_missing_longitude(self):
        """Test validation fails with missing longitude."""
        data = {"latitude": -37.8136}
        assert validate_location_data(data) is False

    def test_validate_with_empty_dict(self):
        """Test validation fails with empty dictionary."""
        assert validate_location_data({}) is False


class TestValidateCartoonData:
    """Tests for validate_cartoon_data function."""

    def test_validate_with_valid_data(self):
        """Test validation with complete valid data."""
        data = {
            "topic": "Local Politics",
            "location": "Melbourne",
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
        assert validate_cartoon_data(data) is True

    def test_validate_with_missing_field(self):
        """Test validation fails with missing required field."""
        data = {
            "topic": "Local Politics",
            "location": "Melbourne",
            "ideas": [],
            "ranking": []
            # Missing 'winner'
        }
        assert validate_cartoon_data(data) is False

    def test_validate_with_wrong_number_of_ideas(self):
        """Test validation fails with wrong number of ideas."""
        data = {
            "topic": "Local Politics",
            "location": "Melbourne",
            "ideas": [
                {"title": "Cartoon 1", "premise": "Premise 1", "why_funny": "Funny 1"}
            ],
            "ranking": ["Cartoon 1"],
            "winner": "Cartoon 1"
        }
        assert validate_cartoon_data(data) is False

    def test_validate_with_invalid_idea_structure(self):
        """Test validation fails with invalid idea structure."""
        data = {
            "topic": "Local Politics",
            "location": "Melbourne",
            "ideas": [
                {"title": "Cartoon 1"},  # Missing premise and why_funny
                {"title": "Cartoon 2", "premise": "Premise 2"},
                {"title": "Cartoon 3", "premise": "Premise 3", "why_funny": "Funny 3"},
                {"title": "Cartoon 4", "premise": "Premise 4", "why_funny": "Funny 4"},
                {"title": "Cartoon 5", "premise": "Premise 5", "why_funny": "Funny 5"}
            ],
            "ranking": ["Cartoon 1", "Cartoon 2", "Cartoon 3", "Cartoon 4", "Cartoon 5"],
            "winner": "Cartoon 1"
        }
        assert validate_cartoon_data(data) is False

    def test_validate_with_invalid_ranking_length(self):
        """Test validation fails with wrong ranking length."""
        data = {
            "topic": "Local Politics",
            "location": "Melbourne",
            "ideas": [
                {"title": "Cartoon 1", "premise": "Premise 1", "why_funny": "Funny 1"},
                {"title": "Cartoon 2", "premise": "Premise 2", "why_funny": "Funny 2"},
                {"title": "Cartoon 3", "premise": "Premise 3", "why_funny": "Funny 3"},
                {"title": "Cartoon 4", "premise": "Premise 4", "why_funny": "Funny 4"},
                {"title": "Cartoon 5", "premise": "Premise 5", "why_funny": "Funny 5"}
            ],
            "ranking": ["Cartoon 1", "Cartoon 2"],  # Wrong length
            "winner": "Cartoon 1"
        }
        assert validate_cartoon_data(data) is False
