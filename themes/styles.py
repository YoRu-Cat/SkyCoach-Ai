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
    GLASS_BG = "rgba(10, 15, 30, 0.58)"
    GLASS_BORDER = "rgba(125, 211, 252, 0.18)"
    GLASS_GLOW = "rgba(6, 182, 212, 0.08)"


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
            position: relative;
            isolation: isolate;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}

        .main .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 1.4rem;
            max-width: 1180px;
            position: relative;
            z-index: 2;
        }}

        [data-testid="stSidebar"] {{
            position: relative;
            z-index: 3;
            background: rgba(3, 7, 18, 0.34) !important;
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-right: 1px solid rgba(125, 211, 252, 0.12) !important;
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
            background: rgba(10, 15, 30, 0.48);
            backdrop-filter: blur(32px) saturate(180%);
            -webkit-backdrop-filter: blur(32px) saturate(180%);
            border: 1px solid rgba(125, 211, 252, 0.18);
            border-radius: 20px;
            padding: 1.05rem;
            margin-bottom: 0.9rem;
            box-shadow: 
                inset 0 1px 0 rgba(255, 255, 255, 0.08),
                0 1px 0 rgba(255, 255, 255, 0.04),
                0 18px 48px rgba(0, 0, 0, 0.28),
                0 0 1px rgba(6, 182, 212, 0.12);
            position: relative;
            animation: fadeInUp 0.45s ease-out forwards;
            overflow: hidden;
        }

        .ui-card::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 20% 50%, rgba(6, 182, 212, 0.06), transparent 50%);
            pointer-events: none;
            border-radius: 20px;
        }

        .ui-card:hover, .glass-card:hover {
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 
                inset 0 1px 0 rgba(255, 255, 255, 0.12),
                0 1px 0 rgba(255, 255, 255, 0.06),
                0 24px 64px rgba(0, 0, 0, 0.32),
                0 0 32px rgba(6, 182, 212, 0.18);
            transform: translateY(-2px);
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
            background: linear-gradient(90deg, transparent 0%, rgba(125, 211, 252, 0.28) 20%, rgba(125, 211, 252, 0.28) 80%, transparent 100%);
            margin: 0.75rem 0;
            box-shadow: 0 0 8px rgba(6, 182, 212, 0.12);
        }

        .ui-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.32rem 0.65rem;
            font-size: 0.76rem;
            font-weight: 600;
            line-height: 1;
            border: 1px solid rgba(125, 211, 252, 0.22);
            color: #e2e8f0;
            background: rgba(6, 15, 30, 0.52);
            backdrop-filter: blur(16px);
            box-shadow: 0 0 12px rgba(6, 182, 212, 0.06);
        }

        .ui-badge-default { 
            background: rgba(6, 15, 30, 0.52); 
            border-color: rgba(125, 211, 252, 0.18);
        }
        .ui-badge-success { 
            background: rgba(6, 95, 70, 0.32); 
            color: #86efac;
            border-color: rgba(16, 185, 129, 0.24);
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.12);
        }
        .ui-badge-warning { 
            background: rgba(120, 53, 15, 0.32); 
            color: #fde68a;
            border-color: rgba(245, 158, 11, 0.24);
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.12);
        }
        .ui-badge-danger { 
            background: rgba(127, 29, 29, 0.32); 
            color: #fca5a5;
            border-color: rgba(239, 68, 68, 0.24);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.12);
        }
        .ui-badge-primary { 
            background: rgba(30, 64, 175, 0.32); 
            color: #bfdbfe;
            border-color: rgba(99, 102, 241, 0.24);
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.12);
        }

        .ui-metric {
            border: 1px solid rgba(125, 211, 252, 0.16);
            background: rgba(6, 15, 30, 0.42);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 0.82rem 0.9rem;
            margin-top: 0.6rem;
            box-shadow: 0 0 8px rgba(6, 182, 212, 0.08);
            transition: all 0.2s ease;
        }

        .ui-metric:hover {
            border-color: rgba(6, 182, 212, 0.32);
            box-shadow: 0 0 16px rgba(6, 182, 212, 0.16);
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

        .weather-card { 
            background: linear-gradient(180deg, rgba(10, 15, 30, 0.52) 0%, rgba(8, 12, 28, 0.48) 100%);
            backdrop-filter: blur(28px);
            border: 1px solid rgba(125, 211, 252, 0.18);
        }

        .weather-card:hover {
            border-color: rgba(6, 182, 212, 0.36);
            box-shadow: 0 0 24px rgba(6, 182, 212, 0.14);
        }

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
            background: rgba(8, 12, 28, 0.48);
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(125, 211, 252, 0.12);
            transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
            backdrop-filter: blur(16px);
        }

        .factor-card:hover {
            transform: translateY(-2px);
            border-color: rgba(125, 211, 252, 0.36);
            background: rgba(8, 12, 28, 0.62);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12);
        }

        .bonus-card { 
            border-color: rgba(16, 185, 129, 0.18);
        }
        .bonus-card:hover { 
            border-color: rgba(16, 185, 129, 0.32);
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.14);
        }
        
        .penalty-card { 
            border-color: rgba(239, 68, 68, 0.18);
        }
        .penalty-card:hover { 
            border-color: rgba(239, 68, 68, 0.32);
            box-shadow: 0 8px 24px rgba(239, 68, 68, 0.14);
        }

        .stTextArea textarea {
            background: rgba(10, 15, 30, 0.52) !important;
            border: 1px solid rgba(125, 211, 252, 0.18) !important;
            border-radius: 14px !important;
            color: #f8fafc !important;
            font-size: 0.98rem !important;
            padding: 0.85rem !important;
            backdrop-filter: blur(16px) !important;
            transition: all 0.15s ease !important;
        }

        .stTextArea textarea:focus {
            border-color: rgba(6, 182, 212, 0.64) !important;
            box-shadow: 
                0 0 0 4px rgba(6, 182, 212, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        }

        .stTextInput input {
            background: rgba(10, 15, 30, 0.52) !important;
            border: 1px solid rgba(125, 211, 252, 0.18) !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
            backdrop-filter: blur(16px) !important;
            transition: all 0.15s ease !important;
        }

        .stTextInput input:focus {
            border-color: rgba(6, 182, 212, 0.64) !important;
            box-shadow: 
                0 0 0 4px rgba(6, 182, 212, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
            color: #0f172a !important;
            border: 1px solid rgba(226, 232, 240, 0.85) !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.25rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease !important;
            box-shadow: 
                0 8px 24px rgba(6, 182, 212, 0.18),
                inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%) !important;
            box-shadow: 
                0 12px 32px rgba(6, 182, 212, 0.24),
                inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        }

        [data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.92) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(125, 211, 252, 0.12) !important;
        }

        .history-item {
            background: rgba(8, 12, 28, 0.44);
            border-radius: 14px;
            padding: 0.8rem 0.95rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(125, 211, 252, 0.12);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
            backdrop-filter: blur(16px);
        }

        .history-item:hover {
            background: rgba(8, 12, 28, 0.62);
            transform: translateY(-1px);
            border-color: rgba(6, 182, 212, 0.28);
            box-shadow: 0 8px 20px rgba(6, 182, 212, 0.1);
        }

        .alt-activity {
            background: rgba(8, 12, 28, 0.44);
            border-radius: 14px;
            padding: 0.95rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(125, 211, 252, 0.12);
            cursor: pointer;
            transition: all 0.2s ease;
            backdrop-filter: blur(16px);
        }

        .alt-activity:hover {
            border-color: rgba(6, 182, 212, 0.36);
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(6, 182, 212, 0.12);
        }

        .forecast-item {
            background: rgba(8, 12, 28, 0.48);
            border: 1px solid rgba(125, 211, 252, 0.12);
            border-radius: 14px;
            padding: 0.75rem;
            text-align: center;
            min-width: 80px;
            backdrop-filter: blur(16px);
            transition: all 0.15s ease;
        }

        .forecast-item:hover {
            border-color: rgba(6, 182, 212, 0.32);
            box-shadow: 0 6px 16px rgba(6, 182, 212, 0.1);
        }

        .ui-inline-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }

        @keyframes fadeInUp {
            from { 
                opacity: 0; 
                transform: translateY(28px);
                filter: blur(4px);
            }
            to { 
                opacity: 1; 
                transform: translateY(0);
                filter: blur(0);
            }
        }

        @keyframes pulse {
            0%, 100% { 
                transform: scale(1);
                filter: drop-shadow(0 0 0 rgba(6, 182, 212, 0));
            }
            50% { 
                transform: scale(1.025);
                filter: drop-shadow(0 0 12px rgba(6, 182, 212, 0.2));
            }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        @keyframes glowPulse {
            0%, 100% { 
                box-shadow: 0 0 12px rgba(6, 182, 212, 0.1);
            }
            50% { 
                box-shadow: 0 0 24px rgba(6, 182, 212, 0.24);
            }
        }

        @keyframes parallaxShift {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) translateX(0px); }
            25% { transform: translateY(-12px) translateX(4px); }
            50% { transform: translateY(-4px) translateX(-8px); }
            75% { transform: translateY(-14px) translateX(6px); }
        }

        /* Responsive Grid & Layout Transitions */
        html[data-breakpoint="mobile"] .hero-title {
            font-size: 2.2rem !important;
        }

        html[data-breakpoint="tablet"] .hero-title {
            font-size: 2.6rem !important;
        }

        html[data-breakpoint="desktop"] .hero-title {
            font-size: 3.15rem !important;
        }

        [data-testid="column"] {
            animation: slideInColumn 0.38s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
            opacity: 0;
            transform: translateY(16px);
        }

        @keyframes slideInColumn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .stColumns > div:nth-child(1) { animation-delay: 0ms; }
        .stColumns > div:nth-child(2) { animation-delay: 85ms; }
        .stColumns > div:nth-child(3) { animation-delay: 170ms; }

        /* Mobile-first responsive adjustments */
        @media (max-width: 639px) {
            .main .block-container {
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
                max-width: 100% !important;
            }

            .stColumns > div {
                gap: 0.6rem !important;
            }

            .hero-subtitle {
                font-size: 0.88rem !important;
            }

            .ui-card, .glass-card {
                padding: 0.75rem !important;
                border-radius: 14px !important;
            }

            .score-circle {
                width: 140px !important;
                height: 140px !important;
            }

            .score-inner {
                width: 110px !important;
                height: 110px !important;
            }

            .score-value {
                font-size: 2.4rem !important;
            }

            .weather-temp {
                font-size: 2rem !important;
            }

            .weather-emoji {
                font-size: 2.8rem !important;
            }

            .ui-metric {
                padding: 0.65rem 0.75rem !important;
                font-size: 0.9rem !important;
            }

            .ui-card-title {
                font-size: 0.95rem !important;
            }

            .status-pill {
                padding: 0.4rem 0.8rem !important;
                font-size: 0.8rem !important;
            }
        }

        /* Tablet (640px - 1023px) */
        @media (min-width: 640px) and (max-width: 1023px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 100% !important;
            }

            .stColumns > div {
                gap: 0.75rem !important;
            }

            .hero-title {
                font-size: 2.6rem !important;
            }

            .hero-subtitle {
                font-size: 0.94rem !important;
            }

            .ui-card, .glass-card {
                padding: 0.9rem !important;
            }

            .score-circle {
                width: 160px !important;
                height: 160px !important;
            }

            .score-inner {
                width: 125px !important;
                height: 125px !important;
            }

            .score-value {
                font-size: 2.6rem !important;
            }

            .weather-temp {
                font-size: 2.2rem !important;
            }

            .weather-emoji {
                font-size: 3rem !important;
            }

            .ui-metric {
                padding: 0.75rem 0.85rem !important;
            }
        }

        /* Desktop (1024px+) */
        @media (min-width: 1024px) {
            .main .block-container {
                padding-top: 1.4rem;
                padding-bottom: 1.4rem;
                max-width: 1180px;
            }
        }

        /* Smooth transitions for layout shifts */
        * {
            transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        [data-testid="stSidebar"] {
            transition: transform 0.3s ease, opacity 0.3s ease;
        }

        /* Stagger animations for multiple cards */
        .ui-card:nth-child(1) {
            animation-delay: 0ms;
        }

        .ui-card:nth-child(2) {
            animation-delay: 50ms;
        }

        .ui-card:nth-child(3) {
            animation-delay: 100ms;
        }

        .ui-card:nth-child(4) {
            animation-delay: 150ms;
        }

        .ui-card:nth-child(5) {
            animation-delay: 200ms;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
