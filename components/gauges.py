import streamlit as st
from components.ui import card_start, card_end, badge, separator


def render_score_gauge(score: int, classification: str):
    """Render animated SkyScore gauge."""

    # Determine color and status based on score
    if score >= 80:
        color = "#10b981"
        status = "Excellent"
    elif score >= 60:
        color = "#06b6d4"
        status = "Good"
    elif score >= 40:
        color = "#f59e0b"
        status = "Fair"
    elif score >= 20:
        color = "#f97316"
        status = "Poor"
    else:
        color = "#ef4444"
        status = "Risky"

    # Needle rotation for half-circle gauge face
    needle_rotation = -90 + (score * 1.8)

    card_start("SkyScore", "Advanced weather suitability index", "✨")
    st.markdown(f"""
        <div class="score-container">
            <div class="score-circle" style="background: conic-gradient(
                #ef4444 0deg 72deg,
                #f59e0b 72deg 144deg,
                #06b6d4 144deg 252deg,
                #10b981 252deg 360deg
            );">
                <div class="score-inner">
                    <span class="score-value">{score}</span>
                    <span class="score-label">SkyScore</span>
                </div>
                <div style="position:absolute; width:2px; height:72px; background:{color}; border-radius:999px; transform: rotate({needle_rotation}deg) translateY(-26px);"></div>
                <div style="position:absolute; width:10px; height:10px; border-radius:999px; background:{color}; box-shadow: 0 0 18px {color};"></div>
            </div>
        </div>
        <div style="display:flex; justify-content:center; gap:0.5rem; margin-top: 0.2rem; margin-bottom:0.7rem;">
            <span class="ui-badge ui-badge-primary">{status}</span>
            <span class="ui-badge ui-badge-default">{score}/100</span>
        </div>
        <div style="text-align: center; margin-top: 0.3rem;">
            <span class="status-pill status-{classification.lower()}">{classification} Activity</span>
        </div>
        <div style="margin-top:0.9rem; height:8px; background:rgba(148,163,184,0.2); border-radius:999px; overflow:hidden;">
            <div style="height:100%; width:{score}%; background:linear-gradient(90deg, #38bdf8, {color}); border-radius:999px;"></div>
        </div>
    """, unsafe_allow_html=True)
    card_end()


def render_hero():
    """Render hero section."""
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <h1 class="hero-title">🌤️ SkyCoach AI</h1>
            <p class="hero-subtitle">Less noise. More signal. Beautiful weather guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_section():
    """Render activity input section."""
    card_start("What do you want to do?", "Describe the activity in plain language", "💭")
    
    user_input = st.text_area(
        "Activity",
        placeholder="e.g., washing my car, going hiking, cooking dinner",
        height=100,
        label_visibility="collapsed"
    )
    
    separator()
    analyze_btn = st.button("Analyze activity", use_container_width=True)
    
    card_end()
    
    return user_input, analyze_btn
