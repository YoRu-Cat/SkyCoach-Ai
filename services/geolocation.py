"""
Geolocation service for SkyCoach AI.
Provides automatic location detection using:
  1. Browser Geolocation API (GPS/WiFi — most accurate, requires user permission)
  2. IP-based geolocation  (ip-api.com — free, no key, instant fallback)
"""

import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class GeoLocation:
    """Represents a detected geographic location."""
    city: str
    country: str
    latitude: float
    longitude: float
    source: str  # "gps", "ip", "manual", "default"
    accuracy: str  # "high", "medium", "low"

    @property
    def display_label(self) -> str:
        flag = {"high": "📍", "medium": "🌐", "low": "📌"}.get(self.accuracy, "📌")
        source_label = {
            "gps": "GPS",
            "ip": "IP Lookup",
            "manual": "Manual",
            "default": "Default",
        }.get(self.source, self.source)
        return f"{flag} {self.city}, {self.country}  ({source_label})"


# ── IP-based geolocation (free, no API key) ────────────────────────────────

def detect_location_by_ip() -> Optional[GeoLocation]:
    """
    Detect user location via IP address using ip-api.com.
    Free tier: 45 requests/minute, no API key needed.
    Returns None on failure.
    """
    try:
        resp = requests.get(
            "http://ip-api.com/json/?fields=status,city,country,lat,lon,query",
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "success":
            return None

        city = data.get("city", "")
        country = data.get("country", "")

        if not city:
            return None

        return GeoLocation(
            city=city,
            country=country,
            latitude=round(data["lat"], 4),
            longitude=round(data["lon"], 4),
            source="ip",
            accuracy="medium",
        )
    except Exception:
        return None


# ── Reverse geocode coordinates → city  ────────────────────────────────────

def reverse_geocode(lat: float, lon: float) -> Optional[GeoLocation]:
    """
    Convert GPS coordinates to a city name using geopy (Nominatim).
    Used when browser geolocation provides raw lat/lon.
    """
    try:
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="skycoach_auto_location", timeout=5)
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, language="en")

        if location is None:
            return None

        address = location.raw.get("address", {})
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
            or "Unknown"
        )
        country = address.get("country", "")

        return GeoLocation(
            city=city,
            country=country,
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            source="gps",
            accuracy="high",
        )
    except Exception:
        # If reverse geocode fails, still return a location with coords
        return GeoLocation(
            city=f"{lat:.2f}, {lon:.2f}",
            country="",
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            source="gps",
            accuracy="high",
        )


# ── Browser Geolocation JavaScript ─────────────────────────────────────────

BROWSER_GEO_JS = """
(async () => {
    try {
        const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 8000,
                maximumAge: 300000
            });
        });
        return JSON.stringify({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy
        });
    } catch (err) {
        return JSON.stringify({error: err.message || "denied"});
    }
})()
"""


def get_browser_location_js() -> str:
    """Return the JavaScript snippet for browser geolocation."""
    return BROWSER_GEO_JS


# ── Main auto-detect orchestrator ──────────────────────────────────────────

DEFAULT_LOCATION = GeoLocation(
    city="New York",
    country="US",
    latitude=40.7128,
    longitude=-74.006,
    source="default",
    accuracy="low",
)


def auto_detect_location() -> GeoLocation:
    """
    Auto-detect user location. Tries IP-based first.
    Browser GPS is handled separately via JS in the Streamlit UI.
    Falls back to New York as default.
    """
    ip_location = detect_location_by_ip()
    if ip_location:
        return ip_location

    return DEFAULT_LOCATION
