import streamlit as st
from typing import List, Optional

from components.ui import card_start, card_end, separator
from models.data_classes import HistoryEntry


def render_sidebar(
    initial_openai_key: str = "",
    initial_weather_key: str = "",
    initial_city: str = "New York",
    initial_demo_mode: bool = True,
    history: Optional[List[HistoryEntry]] = None,
):
    """Render sidebar with settings and history."""
    with st.sidebar:
        st.markdown(
            "<div style='padding: 0.75rem 0 0.25rem 0;'><h2 style='color:#f8fafc; margin:0;'>SkyCoach</h2><div style='color:rgba(226,232,240,0.68); font-size:0.92rem;'>Activity guidance with weather context</div></div>",
            unsafe_allow_html=True,
        )

        separator()
        st.markdown("<div class='ui-section-title' style='margin-bottom:0.6rem;'>Settings</div>", unsafe_allow_html=True)

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=initial_openai_key,
            help="Get your key at platform.openai.com",
        )

        weather_key = st.text_input(
            "OpenWeatherMap Key",
            type="password",
            value=initial_weather_key,
            help="Get your free key at openweathermap.org",
        )

        st.session_state.openai_api_key = openai_key
        st.session_state.openweather_api_key = weather_key

        separator()
        st.markdown("<div class='ui-section-title' style='margin-bottom:0.6rem;'>Location</div>", unsafe_allow_html=True)

        city = st.text_input(
            "City",
            value=initial_city,
            help="Enter city name",
        )
        st.session_state.city = city

        separator()
        demo_mode = st.toggle(
            "Demo mode",
            value=initial_demo_mode,
            help="Use demo data (no API keys needed)",
        )
        st.session_state.demo_mode = demo_mode

        if demo_mode:
            st.info("Demo mode enabled. Using simulated data.")

        separator()
        card_start("About", "What this app does", "ℹ️")
        st.markdown(
            "<div style='color:rgba(226,232,240,0.72); font-size:0.88rem; line-height:1.5;'>SkyCoach AI understands your activity, checks weather conditions, and produces a simple recommendation.</div>",
            unsafe_allow_html=True,
        )
        card_end()

        separator()
        st.markdown("<div class='ui-section-title' style='margin-bottom:0.6rem;'>Recent History</div>", unsafe_allow_html=True)

        if history:
            for entry in history[-5:][::-1]:
                score_color = "#10b981" if entry.score >= 70 else "#f59e0b" if entry.score >= 40 else "#ef4444"
                st.markdown(
                    f"""
                    <div class="history-item">
                        <div>
                            <div style="color:#f8fafc; font-weight:600;">{entry.activity}</div>
                            <div style="color: rgba(226,232,240,0.62); font-size: 0.75rem;">{entry.timestamp} · {entry.city}</div>
                        </div>
                        <div style="color: {score_color}; font-weight: 700;">{entry.score}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div style="color: rgba(226,232,240,0.5); font-size: 0.85rem; text-align: center; padding: 1rem;">
                    No history yet. Analyze an activity to get started!
                </div>
                """,
                unsafe_allow_html=True,
            )

        return openai_key, weather_key, city, demo_mode
