"""
SkyCoach AI runtime entrypoint.
This file contains the refactored app logic while app.py becomes a thin launcher.
"""

import time
from datetime import datetime

import streamlit as st

from components.animations import render_motion_stage
from components.cards import (
    render_weather_card,
    render_analysis_card,
    render_factors_card,
    render_mini_forecast,
    render_alternatives,
)
from components.gauges import render_hero, render_input_section, render_score_gauge
from components.layout import render_sidebar
from core.pipeline import PluginPipeline
from core.scoring_engine import calculate_sky_score, get_alternative_activities
from models.data_classes import Config, HistoryEntry
from plugins.registry import get_default_plugins
from services.ai_engine import (
    analyze_task_fallback,
    analyze_task_openai,
    get_demo_weather,
    get_weather_by_city,
)
from services.maps import display_map_section
from themes.styles import inject_component_styles, inject_global_styles


def init_session_state() -> None:
    """Initialize Streamlit session state."""
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = True
    if "history" not in st.session_state:
        st.session_state.history = []


def configure_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="SkyCoach AI",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """Main application entry point."""
    configure_page()
    init_session_state()
    inject_global_styles()
    inject_component_styles()
    pipeline = PluginPipeline(get_default_plugins())

    openai_key, weather_key, city, demo_mode = render_sidebar(
        initial_openai_key=st.session_state.get("openai_api_key", ""),
        initial_weather_key=st.session_state.get("openweather_api_key", ""),
        initial_city=st.session_state.get("city", "New York"),
        initial_demo_mode=st.session_state.get("demo_mode", True),
        history=st.session_state.get("history", []),
    )

    render_motion_stage()
    render_hero()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_input, analyze_btn = render_input_section()

    if analyze_btn and user_input:
        with st.spinner("🔮 Analyzing your activity..."):
            config = Config()
            normalized_input = pipeline.process_task_text(user_input)
            normalized_city = pipeline.process_city(city)

            if demo_mode or not openai_key:
                task = analyze_task_fallback(normalized_input)
            else:
                try:
                    task = analyze_task_openai(normalized_input, openai_key)
                except Exception as exc:
                    st.warning(f"OpenAI error, using fallback: {str(exc)[:80]}")
                    task = analyze_task_fallback(normalized_input)

            task = pipeline.process_task(task)

            time.sleep(0.35)

            if demo_mode or not weather_key:
                weather = get_demo_weather(normalized_city)
            else:
                try:
                    weather = get_weather_by_city(normalized_city, weather_key)
                except Exception as exc:
                    st.warning(f"Weather API error, using demo: {str(exc)[:80]}")
                    weather = get_demo_weather(normalized_city)

            weather = pipeline.process_weather(weather)

            time.sleep(0.2)

            result = calculate_sky_score(task, weather, config)
            result = pipeline.process_score(result)

            history_entry = HistoryEntry(
                timestamp=datetime.now().strftime("%H:%M"),
                activity=task.activity[:20],
                classification=task.classification,
                score=result.score,
                city=weather.city,
                weather_condition=weather.condition,
            )
            st.session_state.history.append(history_entry)
            if len(st.session_state.history) > 10:
                st.session_state.history = st.session_state.history[-10:]

            st.session_state.task = task
            st.session_state.weather = weather
            st.session_state.result = result
            st.session_state.analyzed = True

    if st.session_state.get("analyzed"):
        task = st.session_state.task
        weather = st.session_state.weather
        result = st.session_state.result

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            render_score_gauge(result.score, result.classification)
            render_weather_card(weather)

        with col2:
            render_analysis_card(task)
            render_factors_card(result)

        st.markdown("<br>", unsafe_allow_html=True)

        map_col, forecast_col = st.columns([2, 1])
        with map_col:
            display_map_section(weather)

        with forecast_col:
            render_mini_forecast(city)
            st.markdown("<br>", unsafe_allow_html=True)
            alternatives = get_alternative_activities(result.classification, weather)
            render_alternatives(result.classification, weather, alternatives)


if __name__ == "__main__":
    main()
