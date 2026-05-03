# 🌦️ Weather Analytics Dashboard

A mini-project that fetches live weather data from **OpenWeatherMap**, stores it locally as CSV, and visualises it through an interactive **Streamlit** dashboard with **Matplotlib** charts.

---

## 📁 Project Structure

```
weather-analytics-project/
│
├── config/
│   └── config.py          ← API key, URLs, chart colours
│
├── data/
│   ├── cities.txt         ← Pre-loaded city list
│   └── weather_data.csv   ← Auto-created when you fetch data
│
├── src/
│   ├── fetch_data.py      ← OpenWeatherMap API calls
│   ├── store_data.py      ← CSV read / write helpers
│   ├── analyze_data.py    ← All Matplotlib chart functions
│   └── dashboard.py       ← Streamlit UI (the whole app)
│
├── requirements.txt
├── run.py                 ← Entry point
└── README.md
```

---

## ⚡ Quick Start

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Add your API key
Edit `config/config.py` and replace:
```python
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
```
Get a **free** key at [openweathermap.org/api](https://openweathermap.org/api) (takes ~10 min to activate).

### 3 — Run the dashboard
```bash
python run.py
# or
streamlit run src/dashboard.py
```

Open **http://localhost:8501** in your browser.

---

## 🖥️ Dashboard Features

| Feature | Description |
|---|---|
| **Location selector** | Pick from the cities list or type any city name |
| **Forecast period** | Slider: 1–5 days ahead |
| **Date range filter** | Filter historical charts by custom date range |
| **Chart toggles** | Turn individual charts on/off from the sidebar |
| **Fetch & Save** | One-click fetch + auto-save to CSV |
| **Raw data viewer** | Expandable table with CSV download |

### 📊 Charts Included
- 🌡️ Temperature Trend (line + fill)
- 💧 Humidity (coloured bar chart)
- 🔵 Atmospheric Pressure (line)
- 💨 Wind Speed (area chart)
- 📊 Daily Min / Max / Avg Summary (grouped bars)
- 🌤️ Weather Condition Distribution (pie chart)
- 🔗 Correlation Heatmap (optional)

---

## 📦 Requirements

```
requests==2.31.0
pandas==2.1.4
matplotlib==3.8.2
streamlit==1.31.0
```

---

## 📝 Notes
- The free OpenWeatherMap plan gives current weather + 5-day/3h forecast.
- Data is appended to `data/weather_data.csv` each time you fetch.
- Use the **Clear Stored Data** button in the sidebar to reset.
