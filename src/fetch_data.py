# ============================================================
#  src/fetch_data.py  —  All API calls to OpenWeatherMap
# ============================================================

import requests
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.config import (
    API_KEY, CURRENT_WEATHER_URL, FORECAST_URL,
    GEO_URL, UNITS
)


# ── helpers ──────────────────────────────────────────────────

def _get(url: str, params: dict) -> dict | None:
    """Thin wrapper around requests.get with basic error handling."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print("❌  No internet connection.")
    except requests.exceptions.Timeout:
        print("❌  Request timed out.")
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            print("❌  Invalid API key — check config/config.py.")
        elif code == 404:
            print(f"❌  City not found.")
        else:
            print(f"❌  HTTP {code}: {e}")
    except Exception as e:
        print(f"❌  Unexpected error: {e}")
    return None


# ── public functions ─────────────────────────────────────────

def get_current_weather(city: str) -> dict | None:
    """
    Fetch current weather for *city*.
    Returns a flat dict ready to be stored / displayed.
    """
    data = _get(CURRENT_WEATHER_URL, {
        "q"     : city,
        "appid" : API_KEY,
        "units" : UNITS,
    })
    if data is None:
        return None

    return {
        "city"        : data["name"],
        "country"     : data["sys"]["country"],
        "temperature" : data["main"]["temp"],
        "feels_like"  : data["main"]["feels_like"],
        "temp_min"    : data["main"]["temp_min"],
        "temp_max"    : data["main"]["temp_max"],
        "humidity"    : data["main"]["humidity"],
        "pressure"    : data["main"]["pressure"],
        "wind_speed"  : data["wind"]["speed"],
        "wind_deg"    : data["wind"].get("deg", 0),
        "visibility"  : data.get("visibility", 0) / 1000,   # → km
        "description" : data["weather"][0]["description"].title(),
        "icon"        : data["weather"][0]["icon"],
        "clouds"      : data["clouds"]["all"],
        "timestamp"   : data["dt"],
    }


def get_forecast(city: str, days: int = 5) -> list[dict] | None:
    """
    Fetch up to *days* days of 3-hourly forecast data for *city*.
    Returns a list of flat dicts (one per 3-hour slot).
    """
    data = _get(FORECAST_URL, {
        "q"     : city,
        "appid" : API_KEY,
        "units" : UNITS,
        "cnt"   : days * 8,          # 8 slots per day (3 h × 8 = 24 h)
    })
    if data is None:
        return None

    records = []
    for item in data["list"]:
        records.append({
            "city"        : data["city"]["name"],
            "country"     : data["city"]["country"],
            "datetime"    : item["dt_txt"],
            "temperature" : item["main"]["temp"],
            "feels_like"  : item["main"]["feels_like"],
            "temp_min"    : item["main"]["temp_min"],
            "temp_max"    : item["main"]["temp_max"],
            "humidity"    : item["main"]["humidity"],
            "pressure"    : item["main"]["pressure"],
            "wind_speed"  : item["wind"]["speed"],
            "wind_deg"    : item["wind"].get("deg", 0),
            "clouds"      : item["clouds"]["all"],
            "description" : item["weather"][0]["description"].title(),
            "icon"        : item["weather"][0]["icon"],
        })
    return records


def get_coordinates(city: str) -> tuple[float, float] | None:
    """Return (lat, lon) for *city* using the Geocoding API."""
    data = _get(GEO_URL, {
        "q"     : city,
        "limit" : 1,
        "appid" : API_KEY,
    })
    if data and len(data) > 0:
        return data[0]["lat"], data[0]["lon"]
    return None