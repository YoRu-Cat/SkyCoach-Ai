import streamlit as st


def render_score_gauge(score: int, classification: str):
    """Render animated SkyScore gauge."""
    
    # Determine color based on score
    if score >= 80:
        color = "#10b981"  # Green
    elif score >= 60:
        color = "#06b6d4"  # Cyan
    elif score >= 40:
        color = "#f59e0b"  # Yellow
    elif score >= 20:
        color = "#f97316"  # Orange
    else:
        color = "#ef4444"  # Red
    
    st.markdown(f"""
    <div class="glass-card">
        <div class="score-container">
            <div class="score-circle" style="background: conic-gradient({color} {score * 3.6}deg, rgba(255,255,255,0.1) 0deg);">
                <div class="score-inner">
                    <span class="score-value">{score}</span>
                    <span class="score-label">SkyScore</span>
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="status-pill status-{classification.lower()}">{classification} Activity</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero():
    """Render hero section."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 class="hero-title">🌤️ SkyCoach AI</h1>
        <p class="hero-subtitle">Your intelligent weather-based activity advisor</p>
    </div>
    """, unsafe_allow_html=True)


def render_input_section():
    """Render activity input section."""
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem; margin-top: 0;">💭 What do you want to do?</h3>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "Activity",
        placeholder="e.g., 'washing my car' or 'gonna do some gardening today'",
        height=100,
        label_visibility="collapsed"
    )
    
    analyze_btn = st.button("🚀 Analyze Activity", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return user_input, analyze_btn
