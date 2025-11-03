"""Tests for location detection functionality."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from src.location_detector import LocationDetector, get_current_location


class TestLocationDetector:
    """Tests for LocationDetector class."""

    def test_init(self):
        """Test LocationDetector initialization."""
        detector = LocationDetector()
        assert detector.geolocator is not None

    @patch('streamlit_js_eval.get_geolocation')
    def test_get_browser_location_success(self, mock_geolocation):
        """Test successful browser location retrieval."""
        mock_geolocation.return_value = {
            'coords': {
                'latitude': -37.8136,
                'longitude': 144.9631,
                'accuracy': 100
            }
        }

        detector = LocationDetector()
        result = detector.get_browser_location()

        assert result is not None
        assert result['latitude'] == -37.8136
        assert result['longitude'] == 144.9631
        assert result['source'] == 'browser'

    @patch('streamlit_js_eval.get_geolocation')
    def test_get_browser_location_failure(self, mock_geolocation):
        """Test browser location retrieval failure."""
        mock_geolocation.return_value = None

        detector = LocationDetector()
        result = detector.get_browser_location()

        assert result is None

    @patch('src.location_detector.geocoder')
    def test_get_ip_location_success(self, mock_geocoder):
        """Test successful IP-based location retrieval."""
        mock_location = MagicMock()
        mock_location.ok = True
        mock_location.latlng = [-37.8136, 144.9631]
        mock_location.city = "Melbourne"
        mock_location.country = "Australia"
        mock_geocoder.ip.return_value = mock_location

        detector = LocationDetector()
        result = detector.get_ip_location()

        assert result is not None
        assert result['latitude'] == -37.8136
        assert result['longitude'] == 144.9631
        assert result['city'] == "Melbourne"
        assert result['country'] == "Australia"
        assert result['source'] == 'ip'

    @patch('src.location_detector.geocoder')
    def test_get_ip_location_failure(self, mock_geocoder):
        """Test IP location retrieval failure."""
        mock_location = MagicMock()
        mock_location.ok = False
        mock_geocoder.ip.return_value = mock_location

        detector = LocationDetector()
        result = detector.get_ip_location()

        assert result is None

    def test_reverse_geocode_success(self):
        """Test successful reverse geocoding."""
        detector = LocationDetector()

        mock_location = MagicMock()
        mock_location.address = "Melbourne, Victoria, Australia"
        mock_location.raw = {
            'address': {
                'city': 'Melbourne',
                'state': 'Victoria',
                'country': 'Australia',
                'country_code': 'au'
            }
        }

        with patch.object(detector.geolocator, 'reverse', return_value=mock_location):
            result = detector.reverse_geocode(-37.8136, 144.9631)

            assert result is not None
            assert result['city'] == 'Melbourne'
            assert result['state'] == 'Victoria'
            assert result['country'] == 'Australia'
            assert result['country_code'] == 'AU'

    def test_reverse_geocode_with_town(self):
        """Test reverse geocoding returns town when city not available."""
        detector = LocationDetector()

        mock_location = MagicMock()
        mock_location.address = "Small Town, Victoria, Australia"
        mock_location.raw = {
            'address': {
                'town': 'Small Town',
                'state': 'Victoria',
                'country': 'Australia',
                'country_code': 'au'
            }
        }

        with patch.object(detector.geolocator, 'reverse', return_value=mock_location):
            result = detector.reverse_geocode(-37.8136, 144.9631)

            assert result is not None
            assert result['city'] == 'Small Town'

    def test_reverse_geocode_failure(self):
        """Test reverse geocoding failure."""
        detector = LocationDetector()

        with patch.object(detector.geolocator, 'reverse', side_effect=Exception("Error")):
            result = detector.reverse_geocode(-37.8136, 144.9631)

            assert result is None

    def test_parse_manual_location_success(self):
        """Test successful manual location parsing."""
        detector = LocationDetector()

        mock_location = MagicMock()
        mock_location.latitude = 48.8566
        mock_location.longitude = 2.3522
        mock_location.address = "Paris, France"

        with patch.object(detector.geolocator, 'geocode', return_value=mock_location):
            result = detector.parse_manual_location("Paris, France")

            assert result is not None
            assert result['latitude'] == 48.8566
            assert result['longitude'] == 2.3522
            assert result['source'] == 'manual'

    def test_parse_manual_location_failure(self):
        """Test manual location parsing failure."""
        detector = LocationDetector()

        with patch.object(detector.geolocator, 'geocode', return_value=None):
            result = detector.parse_manual_location("Invalid Location XYZ123")

            assert result is None

    def test_format_location_display_full(self):
        """Test location formatting with all components."""
        detector = LocationDetector()

        address = {
            'city': 'Melbourne',
            'state': 'Victoria',
            'country': 'Australia'
        }

        result = detector.format_location_display(address)
        assert result == 'Melbourne, Victoria, Australia'

    def test_format_location_display_partial(self):
        """Test location formatting with missing components."""
        detector = LocationDetector()

        address = {
            'city': 'Melbourne',
            'country': 'Australia'
        }

        result = detector.format_location_display(address)
        assert result == 'Melbourne, Australia'

    def test_format_location_display_empty(self):
        """Test location formatting with empty address."""
        detector = LocationDetector()

        address = {}

        result = detector.format_location_display(address)
        assert result == 'Unknown Location'

    @patch.object(LocationDetector, 'parse_manual_location')
    @patch.object(LocationDetector, 'reverse_geocode')
    def test_get_location_with_fallback_manual(
        self,
        mock_reverse,
        mock_parse
    ):
        """Test location fallback with manual entry."""
        mock_parse.return_value = {
            'latitude': 48.8566,
            'longitude': 2.3522,
            'source': 'manual'
        }
        mock_reverse.return_value = {
            'city': 'Paris',
            'country': 'France'
        }

        detector = LocationDetector()
        result = detector.get_location_with_fallback("Paris, France")

        assert result is not None
        coords, address = result
        assert coords['latitude'] == 48.8566
        assert address['city'] == 'Paris'

    @patch.object(LocationDetector, 'get_browser_location')
    @patch.object(LocationDetector, 'reverse_geocode')
    def test_get_location_with_fallback_browser(
        self,
        mock_reverse,
        mock_browser
    ):
        """Test location fallback with browser geolocation."""
        mock_browser.return_value = {
            'latitude': -37.8136,
            'longitude': 144.9631,
            'source': 'browser'
        }
        mock_reverse.return_value = {
            'city': 'Melbourne',
            'country': 'Australia'
        }

        detector = LocationDetector()
        result = detector.get_location_with_fallback()

        assert result is not None
        coords, address = result
        assert coords['latitude'] == -37.8136
        assert address['city'] == 'Melbourne'

    @patch.object(LocationDetector, 'get_browser_location')
    @patch.object(LocationDetector, 'get_ip_location')
    @patch.object(LocationDetector, 'reverse_geocode')
    def test_get_location_with_fallback_ip(
        self,
        mock_reverse,
        mock_ip,
        mock_browser
    ):
        """Test location fallback with IP geolocation."""
        mock_browser.return_value = None
        mock_ip.return_value = {
            'latitude': -37.8136,
            'longitude': 144.9631,
            'city': 'Melbourne',
            'country': 'Australia',
            'source': 'ip'
        }
        mock_reverse.return_value = None  # Not needed for IP with city

        detector = LocationDetector()
        result = detector.get_location_with_fallback()

        assert result is not None
        coords, address = result
        assert address['city'] == 'Melbourne'

    @patch.object(LocationDetector, 'get_browser_location')
    @patch.object(LocationDetector, 'get_ip_location')
    def test_get_location_with_fallback_all_fail(
        self,
        mock_ip,
        mock_browser
    ):
        """Test location fallback when all methods fail."""
        mock_browser.return_value = None
        mock_ip.return_value = None

        detector = LocationDetector()
        result = detector.get_location_with_fallback()

        assert result is None


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch('src.location_detector.LocationDetector')
    def test_get_current_location(self, mock_detector_class):
        """Test get_current_location convenience function."""
        mock_detector = MagicMock()
        mock_detector.get_location_with_fallback.return_value = (
            {'latitude': -37.8136, 'longitude': 144.9631},
            {'city': 'Melbourne', 'country': 'Australia'}
        )
        mock_detector_class.return_value = mock_detector

        result = get_current_location()

        assert result is not None
        coords, address = result
        assert coords['latitude'] == -37.8136
        assert address['city'] == 'Melbourne'
