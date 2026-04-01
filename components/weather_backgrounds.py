"""
Dynamic weather atmosphere backgrounds.
Renders immersive sunny, cloudy, rainy, and storm visuals behind the UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from models.data_classes import WeatherData

WeatherMood = Literal["sunny", "cloudy", "rainy", "stormy", "foggy", "snowy", "default"]

VIDEO_SOURCES: dict[WeatherMood, str] = {
    "sunny": "https://videos.pexels.com/video-files/2365457/2365457-hd_1280_720_25fps.mp4",
    "cloudy": "https://videos.pexels.com/video-files/2728248/2728248-hd_1280_720_25fps.mp4",
    "rainy": "https://videos.pexels.com/video-files/3769153/3769153-hd_1280_720_25fps.mp4",
    "stormy": "https://videos.pexels.com/video-files/3769128/3769128-hd_1280_720_30fps.mp4",
    "foggy": "https://videos.pexels.com/video-files/2818034/2818034-hd_1280_720_25fps.mp4",
    "snowy": "https://videos.pexels.com/video-files/1448735/1448735-hd_1280_720_25fps.mp4",
    "default": "https://videos.pexels.com/video-files/2365457/2365457-hd_1280_720_25fps.mp4",
}


@dataclass
class BackgroundPalette:
    sky_top: str
    sky_bottom: str
    accent: str
    glow: str
    mist: str
    text: str


PALETTES: dict[WeatherMood, BackgroundPalette] = {
    "sunny": BackgroundPalette(
        sky_top="#2b6fff",
        sky_bottom="#8fd3ff",
        accent="#ffd166",
        glow="rgba(255, 209, 102, 0.42)",
        mist="rgba(255, 255, 255, 0.12)",
        text="rgba(255, 255, 255, 0.92)",
    ),
    "cloudy": BackgroundPalette(
        sky_top="#42506a",
        sky_bottom="#8c9bb7",
        accent="#dbe7ff",
        glow="rgba(203, 213, 225, 0.28)",
        mist="rgba(255, 255, 255, 0.10)",
        text="rgba(248, 250, 252, 0.88)",
    ),
    "rainy": BackgroundPalette(
        sky_top="#0f2744",
        sky_bottom="#203a63",
        accent="#67e8f9",
        glow="rgba(103, 232, 249, 0.26)",
        mist="rgba(96, 165, 250, 0.14)",
        text="rgba(241, 245, 249, 0.92)",
    ),
    "stormy": BackgroundPalette(
        sky_top="#0b1020",
        sky_bottom="#1e293b",
        accent="#a78bfa",
        glow="rgba(167, 139, 250, 0.26)",
        mist="rgba(148, 163, 184, 0.12)",
        text="rgba(248, 250, 252, 0.92)",
    ),
    "foggy": BackgroundPalette(
        sky_top="#5b6471",
        sky_bottom="#c7ced6",
        accent="#f8fafc",
        glow="rgba(255, 255, 255, 0.18)",
        mist="rgba(255, 255, 255, 0.24)",
        text="rgba(15, 23, 42, 0.9)",
    ),
    "snowy": BackgroundPalette(
        sky_top="#6ea8ff",
        sky_bottom="#eff8ff",
        accent="#ffffff",
        glow="rgba(255, 255, 255, 0.28)",
        mist="rgba(255, 255, 255, 0.22)",
        text="rgba(15, 23, 42, 0.88)",
    ),
    "default": BackgroundPalette(
        sky_top="#0b1020",
        sky_bottom="#172554",
        accent="#67e8f9",
        glow="rgba(103, 232, 249, 0.22)",
        mist="rgba(148, 163, 184, 0.10)",
        text="rgba(248, 250, 252, 0.92)",
    ),
}


def resolve_mood(weather: WeatherData | None) -> WeatherMood:
    """Map weather conditions to a visual mood."""
    if weather is None:
        return "default"

    condition = (weather.condition or "").lower()
    description = (weather.description or "").lower()

    if weather.is_raining or any(keyword in condition or keyword in description for keyword in ("rain", "drizzle", "shower")):
        if "thunder" in condition or "storm" in condition or "thunder" in description:
            return "stormy"
        return "rainy"

    if any(keyword in condition or keyword in description for keyword in ("cloud", "overcast", "partly cloudy", "mostly cloudy")):
        return "cloudy"

    if any(keyword in condition or keyword in description for keyword in ("fog", "mist", "haze")):
        return "foggy"

    if any(keyword in condition or keyword in description for keyword in ("snow", "sleet", "flurr")):
        return "snowy"

    return "sunny" if condition == "clear" or "sun" in description else "default"


def _weather_title(mood: WeatherMood) -> str:
    titles = {
        "sunny": "Sunny sky",
        "cloudy": "Cloud layers",
        "rainy": "Rain window",
        "stormy": "Storm atmosphere",
        "foggy": "Soft fog",
        "snowy": "Snowfall scene",
        "default": "Weather atmosphere",
    }
    return titles[mood]


def render_weather_background(weather: WeatherData | None) -> None:
    """Render the weather background layer behind the UI."""
    mood = resolve_mood(weather)
    palette = PALETTES[mood]
    video_url = VIDEO_SOURCES.get(mood, VIDEO_SOURCES["default"])

    rain_count = 30 if mood in {"rainy", "stormy"} else 0
    cloud_count = 5 if mood in {"cloudy", "stormy", "default"} else 2
    snow_count = 24 if mood == "snowy" else 0

    rain_streaks = "".join(
        f'<span class="weather-drop" style="left:{i * 3.2 % 100:.2f}%; animation-delay:{(i * 0.14) % 3:.2f}s; opacity:{0.35 + (i % 5) * 0.1:.2f}; height:{90 + (i % 6) * 20}px;"></span>'
        for i in range(rain_count)
    )
    cloud_blobs = "".join(
        f'<span class="weather-cloud cloud-{i % 3}" style="top:{10 + i * 11}% ; left:{8 + i * 18}% ; animation-delay:{i * 0.7:.2f}s;"></span>'
        for i in range(cloud_count)
    )
    snow_flakes = "".join(
        f'<span class="weather-snow" style="left:{i * 4.1 % 100:.2f}%; animation-delay:{(i * 0.13) % 4:.2f}s; transform: scale({0.6 + (i % 5) * 0.12:.2f});"></span>'
        for i in range(snow_count)
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: transparent !important;
            position: relative;
            isolation: isolate;
        }}

        .weather-atmosphere {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }}

        .weather-video {{
            position: absolute;
            top: 50%;
            left: 50%;
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            transform: translate(-50%, -50%);
            object-fit: cover;
            opacity: 0.95;
            z-index: 1;
        }}

        .weather-video-fallback {{
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 20% 15%, {palette.glow}, transparent 26%),
                radial-gradient(circle at 80% 12%, rgba(255, 255, 255, 0.14), transparent 22%),
                linear-gradient(180deg, {palette.sky_top} 0%, {palette.sky_bottom} 100%);
            z-index: 0;
        }}

        .weather-atmosphere::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), transparent 35%, rgba(0, 0, 0, 0.08));
            z-index: 2;
        }}

        .weather-atmosphere::after {{
            content: "";
            position: absolute;
            inset: auto 0 0 0;
            height: 24%;
            background: linear-gradient(180deg, transparent, rgba(2, 6, 23, 0.22));
            z-index: 2;
        }}

        .weather-sun {{
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            right: 8%;
            top: 7%;
            background: radial-gradient(circle, rgba(255,255,255,0.98) 0%, rgba(255, 230, 140, 0.94) 30%, rgba(255, 209, 102, 0.35) 55%, transparent 72%);
            filter: blur(0.4px) drop-shadow(0 0 45px rgba(255, 209, 102, 0.4));
            opacity: {1.0 if mood == 'sunny' else 0.22};
            animation: sunPulse 8s ease-in-out infinite;
            z-index: 3;
        }}

        .weather-ray {{
            position: absolute;
            right: calc(8% + 90px);
            top: calc(7% + 90px);
            width: 2px;
            height: 140px;
            background: linear-gradient(180deg, rgba(255, 239, 166, 0.96), transparent);
            transform-origin: bottom center;
            opacity: {0.9 if mood == 'sunny' else 0.18};
            filter: blur(0.3px);
            z-index: 3;
        }}

        .weather-ray.r1 {{ transform: rotate(15deg); }}
        .weather-ray.r2 {{ transform: rotate(45deg); }}
        .weather-ray.r3 {{ transform: rotate(75deg); }}
        .weather-ray.r4 {{ transform: rotate(105deg); }}
        .weather-ray.r5 {{ transform: rotate(135deg); }}
        .weather-ray.r6 {{ transform: rotate(165deg); }}

        .weather-cloud {{
            position: absolute;
            border-radius: 999px;
            background: linear-gradient(180deg, rgba(255,255,255,0.80), rgba(226,232,240,0.44));
            filter: blur(2px);
            box-shadow: 0 14px 40px rgba(15, 23, 42, 0.12);
            animation: cloudDrift 24s linear infinite;
            opacity: {0.88 if mood in {'cloudy', 'stormy'} else 0.18};
            z-index: 3;
        }}

        .weather-cloud::before,
        .weather-cloud::after {{
            content: "";
            position: absolute;
            border-radius: 999px;
            background: inherit;
        }}

        .cloud-0 {{ width: 160px; height: 54px; top: 12%; left: 6%; }}
        .cloud-0::before {{ width: 84px; height: 84px; top: -42px; left: 26px; }}
        .cloud-0::after {{ width: 96px; height: 96px; top: -50px; left: 74px; }}

        .cloud-1 {{ width: 210px; height: 66px; top: 24%; left: 36%; animation-duration: 30s; }}
        .cloud-1::before {{ width: 110px; height: 110px; top: -56px; left: 28px; }}
        .cloud-1::after {{ width: 124px; height: 124px; top: -64px; left: 98px; }}

        .cloud-2 {{ width: 190px; height: 58px; top: 8%; right: 10%; animation-duration: 28s; }}
        .cloud-2::before {{ width: 92px; height: 92px; top: -46px; left: 18px; }}
        .cloud-2::after {{ width: 110px; height: 110px; top: -54px; left: 90px; }}

        .weather-drop {{
            position: absolute;
            top: -14%;
            width: 2px;
            border-radius: 999px;
            background: linear-gradient(180deg, rgba(255,255,255,0), rgba(191, 219, 254, 0.95));
            animation: rainFall 1.15s linear infinite;
            filter: drop-shadow(0 0 8px rgba(96, 165, 250, 0.22));
            opacity: {1.0 if mood in {'rainy', 'stormy'} else 0.0};
            z-index: 3;
        }}

        .weather-drop::after {{
            content: "";
            position: absolute;
            left: -2px;
            bottom: -6px;
            width: 6px;
            height: 10px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(191, 219, 254, 0.62), transparent 70%);
            filter: blur(2px);
        }}

        .weather-snow {{
            position: absolute;
            top: -10%;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255,255,255,0.9);
            box-shadow: 0 0 14px rgba(255,255,255,0.22);
            animation: snowFall 10s linear infinite;
            opacity: {1.0 if mood == 'snowy' else 0.0};
            z-index: 3;
        }}

        .weather-mist {{
            position: absolute;
            inset: auto 0 0 0;
            height: 42%;
            background: linear-gradient(180deg, transparent, {palette.mist});
            filter: blur(18px);
            opacity: {0.92 if mood in {'foggy', 'cloudy'} else 0.18};
            z-index: 2;
        }}

        @keyframes rainFall {{
            0% {{ transform: translateY(-10vh) translateX(0); opacity: 0.0; }}
            10% {{ opacity: 1; }}
            100% {{ transform: translateY(120vh) translateX(-24px); opacity: 0; }}
        }}

        @keyframes cloudDrift {{
            0% {{ transform: translateX(-14px); }}
            50% {{ transform: translateX(16px); }}
            100% {{ transform: translateX(-14px); }}
        }}

        @keyframes sunPulse {{
            0%, 100% {{ transform: scale(1); filter: blur(0.4px) drop-shadow(0 0 45px rgba(255, 209, 102, 0.4)); }}
            50% {{ transform: scale(1.04); filter: blur(0.4px) drop-shadow(0 0 60px rgba(255, 209, 102, 0.58)); }}
        }}

        @keyframes snowFall {{
            0% {{ transform: translateY(-10vh) translateX(0); opacity: 0.0; }}
            10% {{ opacity: 0.9; }}
            100% {{ transform: translateY(115vh) translateX(36px); opacity: 0; }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .weather-atmosphere *, .weather-atmosphere {{ animation: none !important; }}
        }}
        </style>

        <div class="weather-atmosphere" aria-hidden="true">
            <div class="weather-video-fallback"></div>
            <video class="weather-video" autoplay muted loop playsinline preload="auto" onloadstart="this.style.display='block'" onerror="this.style.display='none'">
                <source src="{video_url}" type="video/mp4">
            </video>
            <div class="weather-sun"></div>
            <span class="weather-ray r1"></span>
            <span class="weather-ray r2"></span>
            <span class="weather-ray r3"></span>
            <span class="weather-ray r4"></span>
            <span class="weather-ray r5"></span>
            <span class="weather-ray r6"></span>
            {cloud_blobs}
            {rain_streaks}
            {snow_flakes}
            <div class="weather-mist"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if mood == "stormy":
        st.markdown(
            """
            <script>
            (function () {
              const flashes = 2 + Math.floor(Math.random() * 2);
              const app = document.querySelector('.stApp');
              if (!app) return;
              let count = 0;
              const flash = () => {
                app.style.filter = 'brightness(1.08) contrast(1.08)';
                setTimeout(() => {
                  app.style.filter = 'none';
                }, 110);
                count += 1;
                if (count < flashes) {
                  setTimeout(flash, 1800 + Math.random() * 1200);
                }
              };
              setTimeout(flash, 1400);
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )


def get_background_mood_label(weather: WeatherData | None) -> str:
    """Human readable mood label for the current background."""
    return _weather_title(resolve_mood(weather))
