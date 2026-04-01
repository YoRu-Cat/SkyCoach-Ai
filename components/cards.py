import streamlit as st
from typing import List, Tuple
from models.data_classes import WeatherData, TaskAnalysis, SkyScoreResult
from components.ui import badge, card_start, card_end, metric, separator


def render_weather_card(weather: WeatherData):
    """Render weather information card."""
    card_start("Current Weather", f"{weather.city}, {weather.country}", weather.get_emoji())
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; justify-content:space-between; gap:1rem;">
          <div>
            <div class="weather-temp">{weather.temperature:.1f}{weather.temp_unit}</div>
            <div class="weather-condition">{weather.description.title()}</div>
          </div>
          <div class="weather-emoji">{weather.get_emoji()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    separator()
    st.markdown('<div class="ui-inline-row">', unsafe_allow_html=True)
    badge(f"Wind {weather.wind_mph:.1f} mph", "primary")
    badge(f"Humidity {weather.humidity}%", "default")
    badge(f"Rain {weather.rain_1h:.1f} mm", "default")
    st.markdown("</div>", unsafe_allow_html=True)
    card_end()


def render_analysis_card(task: TaskAnalysis):
    """Render task analysis card."""
    card_start("Activity Analysis", "Clean output from the language engine", "🧠")
    metric("Original input", f'"{task.original_text}"')
    metric("Cleaned text", f'"{task.cleaned_text}"')
    metric("Identified activity", task.activity)
    metric("Confidence", f"{task.confidence*100:.0f}%", task.reasoning)
    card_end()


def render_factors_card(result: SkyScoreResult):
    """Render scoring factors card."""
    card_start("Scoring Factors", "What influenced the final recommendation", "📊")
    for factor in result.weather_factors:
        metric("Weather", factor)
    for name, value, desc in result.bonuses:
        metric(f"Bonus +{value}%", name, desc)
    for name, value, desc in result.penalties:
        metric(f"Penalty {value}%", name, desc)
    st.markdown(f'<div class="ui-card" style="margin-top:1rem; background: rgba(2, 6, 23, 0.72);"><div class="ui-card-title">Recommendation</div><div class="ui-card-subtitle" style="margin-top:0.4rem; color:#f8fafc;">{result.recommendation}</div></div>', unsafe_allow_html=True)
    card_end()


def render_mini_forecast(city: str):
    """Render weather forecast preview."""
    import hashlib
    
    hours = ["Now", "+3h", "+6h", "+9h", "+12h"]
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)
    conditions = [("☀️", "Clear"), ("⛅", "Partly Cloudy"), ("☁️", "Cloudy"), ("🌧️", "Rain")]

    card_start("Upcoming Weather", "A compact outlook for the next few hours", "🕐")
    st.markdown('<div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.6rem;">', unsafe_allow_html=True)

    for i, hour in enumerate(hours):
        idx = (city_hash + i) % len(conditions)
        emoji, _ = conditions[idx]
        temp = 20 + ((city_hash + i * 3) % 15)
        st.markdown(
            f'''
            <div class="forecast-item">
                <div style="color: rgba(226,232,240,0.6); font-size: 0.75rem;">{hour}</div>
                <div style="font-size: 1.4rem; margin: 0.2rem 0;">{emoji}</div>
                <div style="color: #f8fafc; font-weight: 600;">{temp}°</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
    card_end()


def render_alternatives(classification: str, weather: WeatherData, alternatives: List[Tuple[str, str]]):
    """Render alternative activity suggestions."""
    if not alternatives:
        return
    card_start("Alternative Ideas", "Shadcn-style quick suggestions", "💡")
    cols = st.columns(2)
    for i, (activity, description) in enumerate(alternatives):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="alt-activity">
                <div style="font-size: 1.2rem; margin-bottom: 0.25rem;">{activity}</div>
                <div style="color: rgba(226,232,240,0.68); font-size: 0.85rem;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
    card_end()
