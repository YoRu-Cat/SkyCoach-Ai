import streamlit as st


class Colors:
    """Centralized color palette."""
    PRIMARY = "#6366f1"
    PRIMARY_DARK = "#4f46e5"
    SECONDARY = "#8b5cf6"
    ACCENT = "#06b6d4"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    BG_DARK = "#0f0f1a"
    BG_CARD = "rgba(255, 255, 255, 0.05)"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.7)"
    GLASS_BG = "rgba(255, 255, 255, 0.08)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.1)"


def inject_global_styles():
    """Inject global CSS styles."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {{
        --primary: {Colors.PRIMARY};
        --primary-dark: {Colors.PRIMARY_DARK};
        --secondary: {Colors.SECONDARY};
        --accent: {Colors.ACCENT};
        --success: {Colors.SUCCESS};
        --warning: {Colors.WARNING};
        --danger: {Colors.DANGER};
        --bg-dark: {Colors.BG_DARK};
        --text-primary: {Colors.TEXT_PRIMARY};
        --text-secondary: {Colors.TEXT_SECONDARY};
        --glass-bg: {Colors.GLASS_BG};
        --glass-border: {Colors.GLASS_BORDER};
    }}
    
    * {{
        box-sizing: border-box;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, {Colors.BG_DARK} 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }}
    
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    </style>
    """, unsafe_allow_html=True)


def inject_component_styles():
    """Inject all component-specific CSS."""
    st.markdown("""
    <style>
    /* Glass cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    /* Hero section */
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: gradientShift 3s ease infinite;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.7);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Score gauge */
    .score-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .score-circle {
        position: relative;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .score-inner {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: #0f0f1a;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.5);
    }
    
    .score-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        line-height: 1;
    }
    
    .score-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Weather card */
    .weather-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .weather-temp {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 600;
        color: white;
    }
    
    .weather-condition {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .weather-emoji {
        font-size: 4rem;
        animation: bounce 2s ease-in-out infinite;
    }
    
    /* Status pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .status-outdoor {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-indoor {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
    }
    
    /* Factor cards */
    .factor-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6366f1;
        transition: transform 0.2s ease;
    }
    
    .factor-card:hover {
        transform: translateX(5px);
    }
    
    .bonus-card {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .penalty-card {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 26, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* History item */
    .history-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6366f1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(5px);
    }
    
    /* Alternative activities */
    .alt-activity {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(6, 182, 212, 0.2);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .alt-activity:hover {
        border-color: #06b6d4;
        transform: scale(1.02);
    }
    
    /* Forecast item */
    .forecast-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        min-width: 80px;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes gradientShift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(15deg); }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .score-circle { width: 160px; height: 160px; }
        .score-inner { width: 130px; height: 130px; }
        .score-value { font-size: 2.5rem; }
    }
    </style>
    """, unsafe_allow_html=True)
