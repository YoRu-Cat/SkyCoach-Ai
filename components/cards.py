import streamlit as st
from typing import List, Tuple
from models.data_classes import WeatherData, TaskAnalysis, SkyScoreResult
from themes.styles import Colors


def render_glass_card_header(title: str, emoji: str = ""):
    """Render a glass card header."""
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">{emoji} {title}</h3>
    """, unsafe_allow_html=True)


def close_glass_card():
    """Close a glass card div."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_weather_card(weather: WeatherData):
    """Render weather information card."""
    st.markdown(f"""
    <div class="glass-card weather-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="weather-temp">{weather.temperature:.1f}{weather.temp_unit}</div>
                <div class="weather-condition">{weather.description.title()}</div>
                <div style="color: rgba(255,255,255,0.5); margin-top: 0.5rem;">
                    📍 {weather.city}, {weather.country}
                </div>
            </div>
            <div class="weather-emoji">{weather.get_emoji()}</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; text-align: center;">
            <div>
                <div style="font-size: 1.5rem;">💨</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.wind_mph:.1f} mph</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Wind</div>
            </div>
            <div>
                <div style="font-size: 1.5rem;">💧</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.humidity}%</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Humidity</div>
            </div>
            <div>
                <div style="font-size: 1.5rem;">🌧️</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.rain_1h:.1f} mm</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Rain</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_analysis_card(task: TaskAnalysis):
    """Render task analysis card."""
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">🧠 Activity Analysis</h3>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">ORIGINAL INPUT</div>
            <div style="color: white;">"{task.original_text}"</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">CLEANED & UNDERSTOOD</div>
            <div style="color: white;">"{task.cleaned_text}"</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">IDENTIFIED ACTIVITY</div>
            <div style="color: white; font-weight: 600;">{task.activity}</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">CLASSIFICATION ({task.confidence*100:.0f}% confidence)</div>
            <div style="color: white;">{task.reasoning}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_factors_card(result: SkyScoreResult):
    """Render scoring factors card."""
    factors_html = ""
    
    # Weather factors
    for factor in result.weather_factors:
        factors_html += f'''
        <div class="factor-card">
            <div style="color: white;">{factor}</div>
        </div>
        '''
    
    # Bonuses
    for name, value, desc in result.bonuses:
        factors_html += f'''
        <div class="factor-card bonus-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: white;">✅ {name}</div>
                <div style="color: #10b981; font-weight: 600;">+{value}%</div>
            </div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{desc}</div>
        </div>
        '''
    
    # Penalties
    for name, value, desc in result.penalties:
        factors_html += f'''
        <div class="factor-card penalty-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: white;">❌ {name}</div>
                <div style="color: #ef4444; font-weight: 600;">{value}%</div>
            </div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{desc}</div>
        </div>
        '''
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">📊 Scoring Factors</h3>
        {factors_html}
        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99, 102, 241, 0.2); border-radius: 12px; text-align: center;">
            <div style="color: white; font-size: 1.1rem;">{result.recommendation}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mini_forecast(city: str):
    """Render weather forecast preview."""
    import hashlib
    
    hours = ["Now", "+3h", "+6h", "+9h", "+12h"]
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)
    conditions = [("☀️", "Clear"), ("⛅", "Partly Cloudy"), ("☁️", "Cloudy"), ("🌧️", "Rain")]
    
    forecast_html = '<div style="display: flex; gap: 0.75rem; justify-content: space-between;">'
    
    for i, hour in enumerate(hours):
        idx = (city_hash + i) % len(conditions)
        emoji, _ = conditions[idx]
        temp = 20 + ((city_hash + i * 3) % 15)
        forecast_html += f'''
        <div class="forecast-item">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{hour}</div>
            <div style="font-size: 1.5rem; margin: 0.25rem 0;">{emoji}</div>
            <div style="color: white; font-weight: 500;">{temp}°</div>
        </div>
        '''
    
    forecast_html += '</div>'
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">🕐 Upcoming Weather</h3>
        {forecast_html}
    </div>
    """, unsafe_allow_html=True)


def render_alternatives(classification: str, weather: WeatherData, alternatives: List[Tuple[str, str]]):
    """Render alternative activity suggestions."""
    if not alternatives:
        return
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">💡 Alternative Ideas</h3>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (activity, description) in enumerate(alternatives):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="alt-activity">
                <div style="font-size: 1.2rem; margin-bottom: 0.25rem;">{activity}</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
