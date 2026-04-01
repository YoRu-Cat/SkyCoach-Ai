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
    BG_DARK = "#0b1020"
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "rgba(226, 232, 240, 0.72)"
    GLASS_BG = "rgba(15, 23, 42, 0.72)"
    GLASS_BORDER = "rgba(148, 163, 184, 0.16)"


def inject_global_styles():
    """Inject global CSS styles."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

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

        * {{ box-sizing: border-box; }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(168, 85, 247, 0.10), transparent 24%),
                linear-gradient(180deg, #0b1020 0%, #0f172a 100%);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: var(--text-primary);
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        .main .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 1.4rem;
            max-width: 1180px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_component_styles():
    """Inject all component-specific CSS."""
    st.markdown(
        """
        <style>
        .ui-card, .glass-card {
            background: rgba(15, 23, 42, 0.72);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 1.05rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 1px 0 rgba(255, 255, 255, 0.03), 0 18px 40px rgba(0, 0, 0, 0.24);
            animation: fadeInUp 0.45s ease-out forwards;
        }

        .ui-card-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }

        .ui-card-title, .ui-section-title {
            font-family: 'Space Grotesk', sans-serif;
            color: #f8fafc;
            font-size: 1.02rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .ui-card-subtitle, .ui-section-description {
            margin-top: 0.25rem;
            color: rgba(226, 232, 240, 0.68);
            font-size: 0.88rem;
            line-height: 1.4;
        }

        .ui-separator {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.22), transparent);
            margin: 0.75rem 0;
        }

        .ui-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.32rem 0.65rem;
            font-size: 0.76rem;
            font-weight: 600;
            line-height: 1;
            border: 1px solid rgba(148, 163, 184, 0.18);
            color: #e2e8f0;
            background: rgba(30, 41, 59, 0.72);
        }

        .ui-badge-default { background: rgba(30, 41, 59, 0.72); }
        .ui-badge-success { background: rgba(6, 95, 70, 0.25); color: #86efac; }
        .ui-badge-warning { background: rgba(120, 53, 15, 0.25); color: #fde68a; }
        .ui-badge-danger { background: rgba(127, 29, 29, 0.25); color: #fca5a5; }
        .ui-badge-primary { background: rgba(30, 64, 175, 0.25); color: #bfdbfe; }

        .ui-metric {
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.58);
            border-radius: 16px;
            padding: 0.82rem 0.9rem;
            margin-top: 0.6rem;
        }

        .ui-metric-label {
            color: rgba(226, 232, 240, 0.62);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .ui-metric-value {
            color: #f8fafc;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 0.2rem;
        }

        .ui-metric-hint {
            color: rgba(226, 232, 240, 0.6);
            font-size: 0.82rem;
            margin-top: 0.15rem;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #e2e8f0 0%, #c4b5fd 40%, #67e8f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 0.5rem;
        }

        .hero-subtitle {
            font-size: 1.04rem;
            color: rgba(226, 232, 240, 0.72);
            text-align: center;
            margin-bottom: 2rem;
        }

        .score-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1.5rem;
        }

        .score-circle {
            position: relative;
            width: 184px;
            height: 184px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: pulse 3.2s ease-in-out infinite;
        }

        .score-inner {
            width: 144px;
            height: 144px;
            border-radius: 50%;
            background: rgba(2, 6, 23, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: inset 0 0 24px rgba(255, 255, 255, 0.03);
        }

        .score-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            color: #f8fafc;
            line-height: 1;
        }

        .score-label {
            font-size: 0.85rem;
            color: rgba(226, 232, 240, 0.68);
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .weather-card { background: linear-gradient(180deg, rgba(15, 23, 42, 0.72) 0%, rgba(15, 23, 42, 0.52) 100%); }

        .weather-temp {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.6rem;
            font-weight: 600;
            color: #f8fafc;
        }

        .weather-condition {
            font-size: 1.02rem;
            color: rgba(226, 232, 240, 0.72);
        }

        .weather-emoji {
            font-size: 3.25rem;
            animation: bounce 2.7s ease-in-out infinite;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 100px;
            font-weight: 500;
            font-size: 0.9rem;
            border: 1px solid rgba(148, 163, 184, 0.16);
        }

        .status-outdoor {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .status-indoor {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
        }

        .factor-card {
            background: rgba(15, 23, 42, 0.55);
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(148, 163, 184, 0.12);
            transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
        }

        .factor-card:hover {
            transform: translateY(-1px);
            border-color: rgba(125, 211, 252, 0.28);
            background: rgba(15, 23, 42, 0.68);
        }

        .bonus-card { border-color: rgba(34, 197, 94, 0.18); }
        .penalty-card { border-color: rgba(248, 113, 113, 0.18); }

        .stTextArea textarea {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 14px !important;
            color: #f8fafc !important;
            font-size: 0.98rem !important;
            padding: 0.85rem !important;
        }

        .stTextArea textarea:focus {
            border-color: rgba(125, 211, 252, 0.8) !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.14) !important;
        }

        .stTextInput input {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
        }

        .stButton > button {
            background: #e2e8f0 !important;
            color: #0f172a !important;
            border: 1px solid rgba(226, 232, 240, 0.85) !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.25rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18) !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px) !important;
            background: #f8fafc !important;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.2) !important;
        }

        [data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.92) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        .history-item {
            background: rgba(15, 23, 42, 0.55);
            border-radius: 14px;
            padding: 0.8rem 0.95rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(148, 163, 184, 0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
        }

        .history-item:hover {
            background: rgba(15, 23, 42, 0.72);
            transform: translateY(-1px);
        }

        .alt-activity {
            background: rgba(15, 23, 42, 0.55);
            border-radius: 14px;
            padding: 0.95rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(148, 163, 184, 0.12);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .alt-activity:hover {
            border-color: rgba(125, 211, 252, 0.3);
            transform: translateY(-1px);
        }

        .forecast-item {
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 14px;
            padding: 0.75rem;
            text-align: center;
            min-width: 80px;
        }

        .ui-inline-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(24px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
