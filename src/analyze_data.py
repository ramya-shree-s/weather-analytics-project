# ============================================================
#  src/analyze_data.py  —  All chart / analysis functions
# ============================================================

import pandas as pd
import matplotlib
matplotlib.use("Agg")                    # headless — works inside Streamlit
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.config import CHART_COLORS, UNITS_LABEL, WIND_LABEL


# ── shared style ─────────────────────────────────────────────

BG   = CHART_COLORS["background"]
SURF = CHART_COLORS["surface"]

def _base_style(fig, ax_list=None):
    """Apply dark theme to figure and axes."""
    fig.patch.set_facecolor(BG)
    axes = ax_list or fig.get_axes()
    for ax in axes:
        ax.set_facecolor(SURF)
        ax.tick_params(colors="#AAAAAA", labelsize=9)
        ax.xaxis.label.set_color("#CCCCCC")
        ax.yaxis.label.set_color("#CCCCCC")
        ax.title.set_color("#FFFFFF")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333344")
    return fig


def _save_or_return(fig):
    """Tight-layout + return the figure (Streamlit will render it)."""
    fig.tight_layout(pad=2.0)
    return fig


# ── 1. Temperature trend ─────────────────────────────────────

def plot_temperature_trend(df: pd.DataFrame, city: str):
    """Line chart — temperature & feels-like vs. time."""
    df = df.sort_values("datetime").dropna(subset=["temperature"])

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(df["datetime"], df["temperature"],
            color=CHART_COLORS["temperature"], lw=2.5,
            marker="o", markersize=4, label=f"Temp ({UNITS_LABEL})")

    if "feels_like" in df.columns:
        ax.plot(df["datetime"], df["feels_like"],
                color=CHART_COLORS["feels_like"], lw=1.8,
                linestyle="--", alpha=0.85, label=f"Feels Like ({UNITS_LABEL})")

    ax.fill_between(df["datetime"], df["temperature"],
                    alpha=0.15, color=CHART_COLORS["temperature"])

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax.set_title(f"🌡️  Temperature Trend — {city}", fontsize=13, pad=10)
    ax.set_xlabel("Date / Time")
    ax.set_ylabel(f"Temperature ({UNITS_LABEL})")
    ax.legend(facecolor=SURF, edgecolor="#444", labelcolor="#CCCCCC")
    ax.grid(True, linestyle="--", alpha=0.25, color="#555")

    _base_style(fig)
    return _save_or_return(fig)


# ── 2. Humidity bar chart ─────────────────────────────────────

def plot_humidity(df: pd.DataFrame, city: str):
    """Bar chart — humidity % over time."""
    df = df.sort_values("datetime").dropna(subset=["humidity"])

    fig, ax = plt.subplots(figsize=(10, 4))

    bars = ax.bar(df["datetime"], df["humidity"],
                  color=CHART_COLORS["humidity"],
                  width=0.1, alpha=0.85)

    # colour bars by severity
    for bar, val in zip(bars, df["humidity"]):
        if val >= 80:
            bar.set_color("#FF6B6B")
        elif val >= 60:
            bar.set_color("#FFEAA7")
        else:
            bar.set_color(CHART_COLORS["humidity"])

    ax.axhline(60, color="#FFEAA7", lw=1.2, linestyle="--", alpha=0.7, label="60 % threshold")
    ax.axhline(80, color="#FF6B6B", lw=1.2, linestyle="--", alpha=0.7, label="80 % threshold")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_ylim(0, 105)
    ax.set_title(f"💧  Humidity (%) — {city}", fontsize=13, pad=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Humidity (%)")
    ax.legend(facecolor=SURF, edgecolor="#444", labelcolor="#CCCCCC")
    ax.grid(True, axis="y", linestyle="--", alpha=0.25, color="#555")

    _base_style(fig)
    return _save_or_return(fig)


# ── 3. Pressure line chart ───────────────────────────────────

def plot_pressure(df: pd.DataFrame, city: str):
    """Line chart — atmospheric pressure (hPa)."""
    df = df.sort_values("datetime").dropna(subset=["pressure"])

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(df["datetime"], df["pressure"],
            color=CHART_COLORS["pressure"], lw=2.2,
            marker="s", markersize=4)
    ax.fill_between(df["datetime"], df["pressure"],
                    df["pressure"].min() - 5,
                    alpha=0.15, color=CHART_COLORS["pressure"])

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax.set_title(f"🔵  Atmospheric Pressure (hPa) — {city}", fontsize=13, pad=10)
    ax.set_xlabel("Date / Time")
    ax.set_ylabel("Pressure (hPa)")
    ax.grid(True, linestyle="--", alpha=0.25, color="#555")

    _base_style(fig)
    return _save_or_return(fig)


# ── 4. Wind speed chart ──────────────────────────────────────

def plot_wind(df: pd.DataFrame, city: str):
    """Area chart — wind speed over time."""
    df = df.sort_values("datetime").dropna(subset=["wind_speed"])

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.fill_between(df["datetime"], df["wind_speed"],
                    color=CHART_COLORS["wind"], alpha=0.55)
    ax.plot(df["datetime"], df["wind_speed"],
            color=CHART_COLORS["wind"], lw=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax.set_title(f"💨  Wind Speed ({WIND_LABEL}) — {city}", fontsize=13, pad=10)
    ax.set_xlabel("Date / Time")
    ax.set_ylabel(f"Wind Speed ({WIND_LABEL})")
    ax.grid(True, linestyle="--", alpha=0.25, color="#555")

    _base_style(fig)
    return _save_or_return(fig)


# ── 5. Daily summary (min / max / avg) ───────────────────────

def plot_daily_summary(df: pd.DataFrame, city: str):
    """Grouped bar — daily min / max / avg temperature."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    daily = df.groupby("date")["temperature"].agg(["min", "max", "mean"]).reset_index()

    x   = np.arange(len(daily))
    w   = 0.28
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(x - w, daily["min"],  w, color="#4ECDC4", label="Min", alpha=0.9)
    ax.bar(x,     daily["mean"], w, color="#FFEAA7", label="Avg", alpha=0.9)
    ax.bar(x + w, daily["max"],  w, color="#FF6B6B", label="Max", alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in daily["date"]], rotation=30, ha="right")
    ax.set_title(f"📊  Daily Temp Summary ({UNITS_LABEL}) — {city}", fontsize=13, pad=10)
    ax.set_ylabel(f"Temperature ({UNITS_LABEL})")
    ax.legend(facecolor=SURF, edgecolor="#444", labelcolor="#CCCCCC")
    ax.grid(True, axis="y", linestyle="--", alpha=0.25, color="#555")

    _base_style(fig)
    return _save_or_return(fig)


# ── 6. Weather condition distribution (pie) ──────────────────

def plot_condition_pie(df: pd.DataFrame, city: str):
    """Pie chart — share of weather conditions in forecast."""
    if "description" not in df.columns:
        return None

    counts = df["description"].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(counts)))     # type: ignore

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.82,
        wedgeprops={"edgecolor": BG, "linewidth": 1.5},
    )
    for t in texts:
        t.set_color("#CCCCCC")
        t.set_fontsize(9)
    for at in autotexts:
        at.set_color("#FFFFFF")
        at.set_fontsize(8)

    ax.set_title(f"🌤️  Weather Conditions — {city}", fontsize=13, pad=10, color="#FFF")
    fig.patch.set_facecolor(BG)

    return _save_or_return(fig)


# ── 7. Correlation heatmap ───────────────────────────────────

def plot_correlation_heatmap(df: pd.DataFrame, city: str):
    """Heatmap of numeric column correlations."""
    num_cols = ["temperature", "feels_like", "humidity",
                "pressure", "wind_speed", "clouds"]
    available = [c for c in num_cols if c in df.columns]
    if len(available) < 2:
        return None

    corr = df[available].corr()
    fig, ax = plt.subplots(figsize=(7, 6))

    im = ax.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax, shrink=0.8)

    ax.set_xticks(range(len(available)))
    ax.set_yticks(range(len(available)))
    ax.set_xticklabels(available, rotation=45, ha="right", color="#CCC")
    ax.set_yticklabels(available, color="#CCC")

    for i in range(len(available)):
        for j in range(len(available)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}",
                    ha="center", va="center",
                    color="black" if abs(corr.iloc[i, j]) < 0.5 else "white",
                    fontsize=9)

    ax.set_title(f"🔗  Correlation Heatmap — {city}", fontsize=13, pad=10)
    _base_style(fig)
    return _save_or_return(fig)


# ── 8. Quick statistics ──────────────────────────────────────

def compute_statistics(df: pd.DataFrame) -> dict:
    """Return a dict of summary statistics for the dashboard."""
    stats = {}
    for col in ("temperature", "feels_like", "humidity",
                "pressure", "wind_speed"):
        if col in df.columns:
            stats[col] = {
                "min"  : round(df[col].min(), 1),
                "max"  : round(df[col].max(), 1),
                "mean" : round(df[col].mean(), 1),
                "std"  : round(df[col].std(), 1),
            }
    return stats