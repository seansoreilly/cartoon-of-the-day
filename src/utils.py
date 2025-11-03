"""Utility functions for the Cartoon of the Day application."""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pytz


def get_api_key() -> str:
    """
    Retrieve the Google API key from environment or Streamlit secrets.

    Returns:
        str: The API key

    Raises:
        ValueError: If API key is not found
    """
    import streamlit as st

    # Try Streamlit secrets first (for deployed app)
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

    # Try environment variable (for local development)
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key

    raise ValueError(
        "GOOGLE_API_KEY not found. Please set it in .env file or "
        ".streamlit/secrets.toml"
    )


def save_cartoon_data(
    location: str,
    cartoon_data: Dict[str, Any],
    image_path: Optional[str] = None
) -> Path:
    """
    Save cartoon data to JSON file.

    Args:
        location: Location name for the cartoon
        cartoon_data: Dictionary containing cartoon concepts and metadata
        image_path: Optional path to saved image

    Returns:
        Path: Path to saved JSON file
    """
    # Create data directory if it doesn't exist
    data_dir = Path("data/cartoons")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_location = "".join(c for c in location if c.isalnum() or c in (' ', '-', '_'))
    safe_location = safe_location.replace(' ', '_')
    filename = f"{safe_location}_{timestamp}.json"

    # Add metadata
    cartoon_data["metadata"] = {
        "location": location,
        "generated_at": datetime.now().isoformat(),
        "image_path": str(image_path) if image_path else None
    }

    # Save JSON
    output_path = data_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cartoon_data, f, indent=2, ensure_ascii=False)

    return output_path


def get_local_time(latitude: float, longitude: float) -> datetime:
    """
    Get current local time for given coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        datetime: Current local time with timezone
    """
    from timezonefinder import TimezoneFinder

    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            return datetime.now(local_tz)
    except (ValueError, Exception):
        # Invalid coordinates or other errors
        pass

    # Fallback to UTC
    return datetime.now(pytz.UTC)


def format_date_for_location(latitude: float, longitude: float) -> str:
    """
    Format current date for a location in a human-readable format.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        str: Formatted date string (e.g., "Monday, November 3, 2025")
    """
    local_time = get_local_time(latitude, longitude)
    return local_time.strftime("%A, %B %d, %Y")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    sanitized = ''.join(c for c in filename if c in valid_chars)
    return sanitized.replace(' ', '_')


def validate_location_data(location_data: Dict[str, Any]) -> bool:
    """
    Validate location data structure.

    Args:
        location_data: Dictionary containing location information

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['latitude', 'longitude']
    return all(field in location_data for field in required_fields)


def validate_cartoon_data(cartoon_data: Dict[str, Any]) -> bool:
    """
    Validate cartoon data structure.

    Args:
        cartoon_data: Dictionary containing cartoon concepts

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['topic', 'location', 'ideas', 'ranking', 'winner']

    if not all(field in cartoon_data for field in required_fields):
        return False

    # Validate ideas structure
    if not isinstance(cartoon_data['ideas'], list) or len(cartoon_data['ideas']) != 5:
        return False

    for idea in cartoon_data['ideas']:
        if not all(key in idea for key in ['title', 'premise', 'why_funny']):
            return False

    # Validate ranking
    if not isinstance(cartoon_data['ranking'], list) or len(cartoon_data['ranking']) != 5:
        return False

    return True
