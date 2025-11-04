"""Location detection using browser geolocation and IP fallback."""

from typing import Optional, Dict, Any, Tuple
from geopy.geocoders import Nominatim
import geocoder
import streamlit as st


class LocationDetector:
    """Handles location detection from browser or IP address."""

    def __init__(self):
        """Initialize the location detector."""
        self.geolocator = Nominatim(user_agent="cartoon-of-the-day")

    def get_browser_location(self) -> Optional[Dict[str, Any]]:
        """
        Get location from browser geolocation API.

        Returns:
            Dictionary with location data or None if unavailable
        """
        try:
            from streamlit_js_eval import get_geolocation

            location = get_geolocation()

            if location and 'coords' in location:
                coords = location['coords']
                return {
                    'latitude': coords.get('latitude'),
                    'longitude': coords.get('longitude'),
                    'accuracy': coords.get('accuracy'),
                    'source': 'browser'
                }
            elif location is None:
                st.info("ℹ️ Browser location access not granted. Please allow location access or enter manually.")
                return None
            else:
                st.warning("⚠️ Browser location data incomplete.")
                return None
        except ModuleNotFoundError:
            st.error("❌ streamlit-js-eval not installed. Run: pip install streamlit-js-eval")
            return None
        except Exception as e:
            error_msg = str(e).lower()
            if 'https' in error_msg or 'secure' in error_msg:
                st.warning("🔒 Browser geolocation requires HTTPS. Using fallback location method.")
            elif 'permission' in error_msg or 'denied' in error_msg:
                st.info("ℹ️ Location permission denied. Please enable location access or enter manually.")
            else:
                st.warning(f"⚠️ Browser geolocation unavailable: {e}")
            return None

    def get_ip_location(self) -> Optional[Dict[str, Any]]:
        """
        Get location from IP address as fallback.

        Returns:
            Dictionary with location data or None if unavailable
        """
        try:
            location = geocoder.ip('me')

            if location.ok and location.latlng:
                return {
                    'latitude': location.latlng[0],
                    'longitude': location.latlng[1],
                    'city': location.city,
                    'country': location.country,
                    'source': 'ip'
                }
        except Exception as e:
            st.warning(f"IP geolocation unavailable: {e}")

        return None

    def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, str]]:
        """
        Convert coordinates to city/region names.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with address components or None if unavailable
        """
        try:
            location = self.geolocator.reverse(
                f"{latitude}, {longitude}",
                language='en',
                timeout=10
            )

            if location and location.raw:
                address = location.raw.get('address', {})

                return {
                    'city': address.get('city') or
                            address.get('town') or
                            address.get('village') or
                            address.get('municipality') or
                            'Unknown',
                    'state': address.get('state') or
                             address.get('region') or
                             address.get('province') or '',
                    'country': address.get('country', 'Unknown'),
                    'country_code': address.get('country_code', '').upper(),
                    'full_address': location.address
                }
        except Exception as e:
            st.error(f"Reverse geocoding failed: {e}")

        return None

    def parse_manual_location(self, location_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse manually entered location string.

        Args:
            location_str: Location string (e.g., "Paris, France")

        Returns:
            Dictionary with location data or None if unavailable
        """
        try:
            location = self.geolocator.geocode(location_str, timeout=10)

            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'display_name': location.address,
                    'source': 'manual'
                }
        except Exception as e:
            st.error(f"Location parsing failed: {e}")

        return None

    def get_location_with_fallback(
        self,
        manual_location: Optional[str] = None
    ) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
        """
        Get location with automatic fallback strategy.

        Priority:
        1. Manual location (if provided)
        2. Browser geolocation
        3. IP-based geolocation

        Args:
            manual_location: Optional manually entered location string

        Returns:
            Tuple of (coordinates_dict, address_dict) or None
        """
        coords = None
        address = None

        # Try manual location first
        if manual_location and manual_location.strip():
            coords = self.parse_manual_location(manual_location)
            if coords:
                address = self.reverse_geocode(
                    coords['latitude'],
                    coords['longitude']
                )
                if address:
                    return (coords, address)

        # Try browser geolocation
        coords = self.get_browser_location()
        if coords and coords.get('latitude') and coords.get('longitude'):
            address = self.reverse_geocode(
                coords['latitude'],
                coords['longitude']
            )
            if address:
                return (coords, address)

        # Fallback to IP geolocation
        coords = self.get_ip_location()
        if coords:
            # IP location might already have city info
            if 'city' in coords and 'country' in coords:
                address = {
                    'city': coords['city'],
                    'state': '',
                    'country': coords['country'],
                    'country_code': '',
                    'full_address': f"{coords['city']}, {coords['country']}"
                }
            else:
                address = self.reverse_geocode(
                    coords['latitude'],
                    coords['longitude']
                )

            if address:
                return (coords, address)

        return None

    def format_location_display(self, address: Dict[str, str]) -> str:
        """
        Format address for display.

        Args:
            address: Address dictionary from reverse_geocode

        Returns:
            Formatted location string
        """
        parts = []

        if address.get('city'):
            parts.append(address['city'])

        if address.get('state'):
            parts.append(address['state'])

        if address.get('country'):
            parts.append(address['country'])

        return ', '.join(parts) if parts else 'Unknown Location'


def get_current_location(
    manual_location: Optional[str] = None
) -> Optional[Tuple[Dict[str, Any], Dict[str, str]]]:
    """
    Convenience function to get current location.

    Args:
        manual_location: Optional manually entered location

    Returns:
        Tuple of (coordinates_dict, address_dict) or None
    """
    detector = LocationDetector()
    return detector.get_location_with_fallback(manual_location)
