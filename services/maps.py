import folium
from folium.plugins import Fullscreen, MiniMap, MousePosition
from streamlit_folium import st_folium
import streamlit as st
from models.data_classes import WeatherData


def render_map(lat: float, lon: float, city: str, weather: WeatherData) -> folium.Map:
    """Render interactive Folium map with weather overlay."""

    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )

    # Base layers
    folium.TileLayer("CartoDB dark_matter", name="Dark", control=True).add_to(m)
    folium.TileLayer("CartoDB positron", name="Light", control=True).add_to(m)
    folium.TileLayer("OpenStreetMap", name="Street", control=True).add_to(m)

    # Map controls
    Fullscreen(position="topright", title="Fullscreen", title_cancel="Exit").add_to(m)
    MiniMap(toggle_display=True, position="bottomright").add_to(m)
    MousePosition(position="topright", separator=" | ", prefix="Coords").add_to(m)
    
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

    # Weather intensity ring radius
    intensity = min(1.0, (weather.rain_1h / 5.0) + (weather.wind_mph / 40.0))
    ring_radius = 2500 + int(intensity * 9000)
    ring_color = "#06b6d4" if not weather.is_raining else "#3b82f6"
    
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{city}: {weather.temperature:.1f}{weather.temp_unit}",
        icon=folium.Icon(color=icon_color, icon="cloud", prefix="fa")
    ).add_to(m)

    # Weather intensity ring
    folium.Circle(
        [lat, lon],
        radius=ring_radius,
        color=ring_color,
        fill=True,
        fill_opacity=0.18,
        weight=2,
        tooltip=f"Influence radius: {ring_radius/1000:.1f} km",
    ).add_to(m)

    # Inner focus ring
    folium.Circle(
        [lat, lon],
        radius=max(1000, ring_radius // 3),
        color="#8b5cf6",
        fill=False,
        weight=1,
        opacity=0.8,
    ).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    
    return m


def display_map_section(weather: WeatherData):
    """Display map in a glass-card container."""
    st.markdown(
        f"""
        <div class="glass-card">
            <h3 style="color: white; margin-bottom: 0.4rem; margin-top: 0;">🗺️ Weather Map</h3>
            <div style="color: rgba(226,232,240,0.7); font-size:0.9rem; margin-bottom:0.4rem;">
                Live focus: {weather.city} · {weather.description.title()} · {weather.temperature:.1f}{weather.temp_unit}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    weather_map = render_map(weather.latitude, weather.longitude, weather.city, weather)
    st_folium(weather_map, width=None, height=390, use_container_width=True)
