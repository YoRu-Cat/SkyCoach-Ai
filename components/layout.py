import json
import streamlit as st
from typing import List, Optional

from components.ui import card_start, card_end, separator
from models.data_classes import HistoryEntry
from services.geolocation import (
    auto_detect_location,
    reverse_geocode,
    get_browser_location_js,
    GeoLocation,
)


def _init_auto_location() -> None:
    """Auto-detect location on first load using IP geolocation."""
    if "auto_location" not in st.session_state:
        detected = auto_detect_location()
        st.session_state.auto_location = detected
        st.session_state.city = detected.city
        st.session_state.auto_location_lat = detected.latitude
        st.session_state.auto_location_lon = detected.longitude
        st.session_state.location_source = detected.source
        st.session_state.location_manual_override = False


def _render_location_section(initial_city: str) -> str:
    """Render the smart location section with auto-detect + manual override."""

    _init_auto_location()

    st.markdown(
        "<div class='ui-section-title' style='margin-bottom:0.6rem;'>📍 Location</div>",
        unsafe_allow_html=True,
    )

    auto_loc: GeoLocation = st.session_state.get("auto_location")

    # --- Show current detected location ---
    if auto_loc and not st.session_state.get("location_manual_override", False):
        source_badge = {
            "gps": ("🛰️", "GPS · High Accuracy", "#10b981"),
            "ip": ("🌐", "IP Lookup · Auto-detected", "#06b6d4"),
            "default": ("📌", "Default Location", "#f59e0b"),
        }.get(auto_loc.source, ("📌", auto_loc.source, "#94a3b8"))

        icon, label, color = source_badge
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.04);
                border: 1px solid {color}33;
                border-radius: 12px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.75rem;
            ">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <span style="color:#f8fafc; font-weight:600; font-size:1.05rem;">
                        {auto_loc.city}
                    </span>
                </div>
                <div style="color:{color}; font-size:0.78rem; font-weight:500;">
                    {label}
                </div>
                <div style="color:rgba(226,232,240,0.45); font-size:0.72rem; margin-top:0.2rem;">
                    {auto_loc.latitude:.4f}°, {auto_loc.longitude:.4f}°
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- GPS Precision Button ---
    if st.button("🛰️ Use Precise Location (GPS)", use_container_width=True, key="gps_btn"):
        try:
            from streamlit_js_eval import streamlit_js_eval

            raw = streamlit_js_eval(js_expressions=get_browser_location_js(), want_output=True, key="geo_js")
            if raw:
                geo_data = json.loads(raw) if isinstance(raw, str) else raw
                if "lat" in geo_data and "lon" in geo_data:
                    gps_loc = reverse_geocode(geo_data["lat"], geo_data["lon"])
                    if gps_loc:
                        st.session_state.auto_location = gps_loc
                        st.session_state.city = gps_loc.city
                        st.session_state.auto_location_lat = gps_loc.latitude
                        st.session_state.auto_location_lon = gps_loc.longitude
                        st.session_state.location_source = "gps"
                        st.session_state.location_manual_override = False
                        st.success(f"📍 Location updated: {gps_loc.city}")
                        st.rerun()
                    else:
                        st.warning("Could not resolve GPS coordinates to a city.")
                elif "error" in geo_data:
                    st.warning("Browser denied location access. Using auto-detected location.")
        except ImportError:
            st.info("GPS requires `streamlit-js-eval`. Using IP-based detection instead.")
        except Exception:
            st.warning("Could not get GPS location. Using auto-detected location.")

    # --- Re-detect via IP button ---
    if st.button("🔄 Re-detect Location", use_container_width=True, key="redetect_btn"):
        detected = auto_detect_location()
        st.session_state.auto_location = detected
        st.session_state.city = detected.city
        st.session_state.auto_location_lat = detected.latitude
        st.session_state.auto_location_lon = detected.longitude
        st.session_state.location_source = detected.source
        st.session_state.location_manual_override = False
        st.rerun()

    # --- Manual Override Toggle ---
    manual_override = st.toggle(
        "✏️ Enter city manually",
        value=st.session_state.get("location_manual_override", False),
        key="manual_loc_toggle",
    )
    st.session_state.location_manual_override = manual_override

    if manual_override:
        city = st.text_input(
            "City",
            value=st.session_state.get("city", initial_city),
            help="Type any city name to override auto-detection",
            key="manual_city_input",
        )
        st.session_state.city = city
        st.session_state.location_source = "manual"
    else:
        city = st.session_state.get("city", initial_city)

    return city


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

        # ── Smart Location Section ──
        city = _render_location_section(initial_city)

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
