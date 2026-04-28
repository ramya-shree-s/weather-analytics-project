
# ============================================================
#  config/config.py  —  Central configuration for the project
# ============================================================

# ── OpenWeatherMap ──────────────────────────────────────────
# Get your free API key at: https://openweathermap.org/api
API_KEY = "5e4c3463e0afc45bf20d755fa336c2d9"   # ← Replace this

# Base URLs
CURRENT_WEATHER_URL  = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL         = "https://api.openweathermap.org/data/2.5/forecast"
HISTORY_URL          = "https://api.openweathermap.org/data/2.5/onecall/timemachine"
GEO_URL              = "http://api.openweathermap.org/geo/1.0/direct"

# ── Data storage ────────────────────────────────────────────
DATA_FILE = "data/weather_data.csv"
CITIES_FILE = "data/cities.txt"

# ── App settings ────────────────────────────────────────────
DEFAULT_CITY  = "Bengaluru"
UNITS         = "metric"          # "metric" → °C  |  "imperial" → °F
UNITS_LABEL   = "°C"
WIND_LABEL    = "m/s"

# ── Colour palette used in charts ───────────────────────────
CHART_COLORS = {
    "temperature" : "#FF6B6B",
    "humidity"    : "#4ECDC4",
    "pressure"    : "#45B7D1",
    "wind"        : "#96CEB4",
    "feels_like"  : "#FFEAA7",
    "background"  : "#0E1117",
    "surface"     : "#1E2130",
}