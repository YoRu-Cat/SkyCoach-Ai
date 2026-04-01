import folium
from streamlit_folium import st_folium
import streamlit as st
from models.data_classes import WeatherData


def render_map(lat: float, lon: float, city: str, weather: WeatherData) -> folium.Map:
    """Render interactive Folium map with weather overlay."""
    
    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles="CartoDB dark_matter"
    )
    
    # Weather popup with HTML
    popup_html = f"""
    <div style="font-family: 'Inter', sans-serif; padding: 10px;">
        <h4 style="margin: 0 0 10px 0;">{weather.get_emoji()} {city}</h4>
        <p style="margin: 5px 0;"><b>Temperature:</b> {weather.temperature:.1f}{weather.temp_unit}</p>
        <p style="margin: 5px 0;"><b>Condition:</b> {weather.description.title()}</p>
        <p style="margin: 5px 0;"><b>Wind:</b> {weather.wind_mph:.1f} mph</p>
        <p style="margin: 5px 0;"><b>Humidity:</b> {weather.humidity}%</p>
    </div>
    """
    
    # Icon color based on weather
    if weather.is_raining:
        icon_color = "blue"
    elif weather.condition == "Clear":
        icon_color = "orange"
    else:
        icon_color = "gray"
    
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{city}: {weather.temperature:.1f}{weather.temp_unit}",
        icon=folium.Icon(color=icon_color, icon="cloud", prefix="fa")
    ).add_to(m)
    
    # Visual circle
    folium.Circle(
        [lat, lon],
        radius=5000,
        color="#6366f1",
        fill=True,
        fill_opacity=0.2
    ).add_to(m)
    
    return m


def display_map_section(weather: WeatherData):
    """Display map in a glass-card container."""
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">🗺️ Weather Map</h3>
    </div>
    """, unsafe_allow_html=True)
    
    weather_map = render_map(weather.latitude, weather.longitude, weather.city, weather)
    st_folium(weather_map, width=None, height=350, use_container_width=True)
