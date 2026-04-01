import streamlit as st
from models.data_classes import HistoryEntry
from typing import List, Optional


def render_sidebar(
    initial_openai_key: str = "",
    initial_weather_key: str = "",
    initial_city: str = "New York",
    initial_demo_mode: bool = True,
    history: Optional[List[HistoryEntry]] = None
):
    """Render sidebar with settings and history."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: white;">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Keys
        st.markdown("### 🔑 API Keys")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=initial_openai_key,
            help="Get your key at platform.openai.com"
        )
        
        weather_key = st.text_input(
            "OpenWeatherMap Key",
            type="password",
            value=initial_weather_key,
            help="Get your free key at openweathermap.org"
        )
        
        st.session_state.openai_api_key = openai_key
        st.session_state.openweather_api_key = weather_key
        
        st.markdown("---")
        
        # Location
        st.markdown("### 📍 Location")
        city = st.text_input("City", value=initial_city, help="Enter city name")
        st.session_state.city = city
        
        st.markdown("---")
        
        # Demo mode
        demo_mode = st.toggle(
            "🎮 Demo Mode",
            value=initial_demo_mode,
            help="Use demo data (no API keys needed)"
        )
        st.session_state.demo_mode = demo_mode
        
        if demo_mode:
            st.info("Demo mode enabled. Using simulated data.")
        
        st.markdown("---")
        
        # About
        st.markdown("""
        <div style="padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 12px; margin-top: 1rem;">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">ℹ️ About</h4>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 0;">
                SkyCoach AI uses GPT-4 to understand your activities and real-time weather data to calculate the perfect SkyScore.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📜 Recent History")
        
        if history:
            for entry in history[-5:][::-1]:
                score_color = "#10b981" if entry.score >= 70 else "#f59e0b" if entry.score >= 40 else "#ef4444"
                st.markdown(f"""
                <div class="history-item">
                    <div>
                        <div style="color: white; font-weight: 500;">{entry.activity}</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{entry.timestamp}</div>
                    </div>
                    <div style="color: {score_color}; font-weight: 600;">{entry.score}%</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: rgba(255,255,255,0.4); font-size: 0.85rem; text-align: center; padding: 1rem;">
                No history yet. Analyze an activity to get started!
            </div>
            """, unsafe_allow_html=True)
        
        return openai_key, weather_key, city, demo_mode
