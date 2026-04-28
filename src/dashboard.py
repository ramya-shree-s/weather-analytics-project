# ============================================================
#  src/dashboard.py  —  Streamlit Weather Analytics Dashboard
# ============================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys, os

# ── path setup ───────────────────────────────────────────────
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from config.config   import DEFAULT_CITY, UNITS_LABEL, WIND_LABEL, CITIES_FILE
from src.fetch_data  import get_current_weather, get_forecast

from src.analyze_data import (
    plot_temperature_trend, plot_humidity, plot_pressure,
    plot_wind, plot_daily_summary, plot_condition_pie,
    plot_correlation_heatmap, compute_statistics
)


# ════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════

st.set_page_config(
    page_title = "Weather Analytics",
    page_icon  = "🌦️",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)


# ════════════════════════════════════════════════════════════
#  CUSTOM CSS  (dark, modern card style)
# ════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ── global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0E1117;
    color: #E0E0E0;
    font-family: 'Segoe UI', sans-serif;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #161B27 !important;
    border-right: 1px solid #2A2D3E;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stDateInput label {
    color: #9BA3AF !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── metric cards ── */
[data-testid="stMetric"] {
    background: #1E2130;
    border: 1px solid #2A2D3E;
    border-radius: 12px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"]  { color: #9BA3AF !important; font-size: 0.78rem; }
[data-testid="stMetricValue"]  { color: #FFFFFF !important; font-size: 1.6rem; }
[data-testid="stMetricDelta"]  { font-size: 0.82rem; }

/* ── section headers ── */
h2, h3 { color: #FFFFFF; }

/* ── chart container ── */
.chart-box {
    background: #1E2130;
    border: 1px solid #2A2D3E;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 18px;
}

/* ── info banner ── */
.banner {
    background: linear-gradient(135deg, #1E3A5F, #0E2040);
    border-left: 4px solid #4ECDC4;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 16px;
    color: #D0E8F5;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def cached_current(city):
    return get_current_weather(city)

@st.cache_data(ttl=600)
def cached_forecast(city, days):
    return get_forecast(city, days)

def load_cities():
    try:
        with open(os.path.join(ROOT, CITIES_FILE)) as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return [DEFAULT_CITY]

def weather_emoji(desc: str) -> str:
    desc = desc.lower()
    if "thunder" in desc: return "⛈️"
    if "rain"    in desc: return "🌧️"
    if "drizzle" in desc: return "🌦️"
    if "snow"    in desc: return "❄️"
    if "mist" in desc or "fog" in desc: return "🌫️"
    if "clear"   in desc: return "☀️"
    if "cloud"   in desc: return "☁️"
    return "🌡️"

def wind_direction(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]


# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🌦️ Weather Analytics")
    st.markdown("---")

    # ── city selection ───────────────────────────────────────
    cities = load_cities()
    st.markdown("#### 📍 Location")
    city_choice = st.radio("", ["Select from list", "Type manually"], label_visibility="collapsed")

    if city_choice == "Select from list":
        city = st.selectbox("City", cities, index=cities.index(DEFAULT_CITY) if DEFAULT_CITY in cities else 0)
    else:
        city = st.text_input("Enter city name", value=DEFAULT_CITY).strip()

    # ── forecast days ────────────────────────────────────────
    st.markdown("#### 📅 Forecast Period")
    forecast_days = st.slider("Days ahead", min_value=1, max_value=5, value=3)

    # ── date filter for stored data ──────────────────────────
    st.markdown("#### 🗓️ Historical Date Range")
    col1, col2 = st.columns(2)
    date_from = col1.date_input("From", value=date.today() - timedelta(days=7))
    date_to   = col2.date_input("To",   value=date.today())

    # ── chart selection ──────────────────────────────────────
    st.markdown("#### 📊 Charts to Display")
    show_temp     = st.checkbox("Temperature Trend",   value=True)
    show_humidity = st.checkbox("Humidity",            value=True)
    show_pressure = st.checkbox("Pressure",            value=True)
    show_wind     = st.checkbox("Wind Speed",          value=True)
    show_daily    = st.checkbox("Daily Summary",       value=True)
    show_pie      = st.checkbox("Condition Pie Chart", value=True)
    show_heatmap  = st.checkbox("Correlation Heatmap", value=False)

    st.markdown("---")

    # ── action buttons ───────────────────────────────────────
    fetch_btn  = st.button("🔄  Fetch & Save Data",  use_container_width=True, type="primary")
    clear_btn  = st.button("🗑️  Clear Stored Data", use_container_width=True)

    if clear_btn:
        clear_store()
        st.success("Stored data cleared.")
        st.cache_data.clear()


# ════════════════════════════════════════════════════════════
#  FETCH & SAVE (triggered by sidebar button)
# ════════════════════════════════════════════════════════════

if fetch_btn:
    with st.spinner(f"Fetching weather data for **{city}** …"):
        cur  = get_current_weather(city)
        fore = get_forecast(city, forecast_days)
        if cur:
            save_current(cur)
            st.cache_data.clear()
            st.success(f"✅  Live data saved for **{city}**")
        else:
            st.error("❌  Could not fetch current weather. Check city name & API key.")
        if fore:
            save_forecast(fore)


# ════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ════════════════════════════════════════════════════════════

st.title(f"🌦️  Weather Analytics Dashboard")
st.markdown(f"<div class='banner'>📍 Showing data for <strong>{city}</strong> &nbsp;|&nbsp; Forecast: next <strong>{forecast_days} day(s)</strong> &nbsp;|&nbsp; Historical range: <strong>{date_from}</strong> → <strong>{date_to}</strong></div>", unsafe_allow_html=True)


# ── CURRENT WEATHER CARD ─────────────────────────────────────
st.subheader("🌤️ Current Conditions")

cur = cached_current(city)

if cur:
    emoji = weather_emoji(cur["description"])
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric(f"{emoji} Temperature",  f"{cur['temperature']}{UNITS_LABEL}", f"Feels {cur['feels_like']}{UNITS_LABEL}")
    c2.metric("💧 Humidity",           f"{cur['humidity']} %")
    c3.metric("🔵 Pressure",           f"{cur['pressure']} hPa")
    c4.metric(f"💨 Wind",              f"{cur['wind_speed']} {WIND_LABEL}", wind_direction(cur['wind_deg']))
    c5.metric("👁️ Visibility",         f"{cur['visibility']:.1f} km")
    c6.metric("☁️ Cloud Cover",        f"{cur['clouds']} %")

    st.markdown(f"<p style='color:#9BA3AF; font-size:0.9rem;'>🌍 {cur['city']}, {cur['country']} &nbsp;·&nbsp; {cur['description']}</p>", unsafe_allow_html=True)
else:
    st.info("No current weather loaded yet. Press **Fetch & Save Data** in the sidebar.")


st.markdown("---")


# ── FORECAST CHARTS ──────────────────────────────────────────
st.subheader("📈 Forecast Charts")

fore_records = cached_forecast(city, forecast_days)

if fore_records:
    df_fore = pd.DataFrame(fore_records)
    df_fore["datetime"] = pd.to_datetime(df_fore["datetime"])

    # optional date filter
    df_fore = df_fore[
        (df_fore["datetime"].dt.date >= date_from) &
        (df_fore["datetime"].dt.date <= date_to)
    ]

    if df_fore.empty:
        st.warning("No forecast data in the selected date range.")
    else:
        left, right = st.columns(2)

        if show_temp:
            with left:
                st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                st.pyplot(plot_temperature_trend(df_fore, city))
                st.markdown("</div>", unsafe_allow_html=True)

        if show_humidity:
            with right:
                st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                st.pyplot(plot_humidity(df_fore, city))
                st.markdown("</div>", unsafe_allow_html=True)

        if show_pressure:
            with left:
                st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                st.pyplot(plot_pressure(df_fore, city))
                st.markdown("</div>", unsafe_allow_html=True)

        if show_wind:
            with right:
                st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                st.pyplot(plot_wind(df_fore, city))
                st.markdown("</div>", unsafe_allow_html=True)

        if show_daily:
            st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
            st.pyplot(plot_daily_summary(df_fore, city))
            st.markdown("</div>", unsafe_allow_html=True)

        pie_col, heat_col = st.columns(2)

        if show_pie:
            fig_pie = plot_condition_pie(df_fore, city)
            if fig_pie:
                with pie_col:
                    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                    st.pyplot(fig_pie)
                    st.markdown("</div>", unsafe_allow_html=True)

        if show_heatmap:
            fig_heat = plot_correlation_heatmap(df_fore, city)
            if fig_heat:
                with heat_col:
                    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
                    st.pyplot(fig_heat)
                    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No forecast data available. Press **Fetch & Save Data** in the sidebar.")


# ── STATISTICS TABLE ─────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Statistics Summary")

df_stored = pd.read_csv("data/weather_data.csv")

if not df_stored.empty:
    mask = df_stored["city"].str.lower() == city.lower()
    df_city = df_stored[mask].copy()

    if "datetime" in df_city.columns:
        df_city["datetime"] = pd.to_datetime(df_city["datetime"], errors="coerce")
        df_city = df_city[
            (df_city["datetime"].dt.date >= date_from) &
            (df_city["datetime"].dt.date <= date_to)
        ]

    if not df_city.empty:
        stats = compute_statistics(df_city)
        stat_df = pd.DataFrame(stats).T
        stat_df.columns = ["Min", "Max", "Mean", "Std Dev"]
        stat_df.index.name = "Metric"
        st.dataframe(stat_df.style
                     .format("{:.1f}")
                     .background_gradient(cmap="Blues", subset=["Mean"]),
                     use_container_width=True)
    else:
        st.info("No stored data for selected city / date range.")
else:
    st.info("No stored data yet. Fetch some data first.")


# ── RAW DATA EXPANDER ─────────────────────────────────────────
st.markdown("---")
with st.expander("🗃️  View Raw Stored Data"):
    if not df_stored.empty:
        city_filter = st.selectbox("Filter by city", ["All"] + sorted(df_stored["city"].dropna().unique().tolist()))
        display_df  = df_stored if city_filter == "All" else df_stored[df_stored["city"] == city_filter]
        st.dataframe(display_df.reset_index(drop=True), use_container_width=True)
        csv = display_df.to_csv(index=False).encode()
        st.download_button("⬇️  Download CSV", csv, "weather_data.csv", "text/csv")
    else:
        st.write("No data stored yet.")


# ── FOOTER ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center; color:#555; font-size:0.8rem;'>Weather Analytics Dashboard · Data by OpenWeatherMap · Built with Streamlit 🌦️</p>", unsafe_allow_html=True)