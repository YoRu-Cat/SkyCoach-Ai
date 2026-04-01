"""
Responsive layout utilities for adaptive grid system.
Handles mobile, tablet, and desktop breakpoints with CSS-based transitions.
"""

import streamlit as st


class ResponsivePresets:
    """Common responsive layout configurations."""
    
    @staticmethod
    def two_column_equal():
        """Equal width columns: 1-1."""
        return [1, 1]
    
    @staticmethod
    def two_column_dominant():
        """Dominant left column: 2-1."""
        return [2, 1]
    
    @staticmethod
    def three_column_equal():
        """Equal three columns: 1-1-1."""
        return [1, 1, 1]
    
    @staticmethod
    def three_column_center():
        """Center-focused: 1-2-1."""
        return [1, 2, 1]
    
    @staticmethod
    def sidebar_main():
        """Sidebar + main content: 1-3."""
        return [1, 3]


class ResponsiveContainers:
    """Container utilities for responsive layouts."""
    
    @staticmethod
    def section(title: str = "", emoji: str = "", full_width: bool = False):
        """Create responsive section."""
        if title:
            st.markdown(
                f"""
                <div class="responsive-section" data-full-width="{str(full_width).lower()}">
                    <h3 style="margin:0 0 0.8rem 0; color:#f8fafc;">
                        {emoji} {title}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )


class BreakpointHelper:
    """Helper for breakpoint-aware logic."""
    
    @staticmethod
    def is_mobile() -> bool:
        """Check if viewport is mobile (<640px)."""
        return False
    
    @staticmethod
    def is_tablet() -> bool:
        """Check if viewport is tablet (640px-1023px)."""
        return False
    
    @staticmethod
    def is_desktop() -> bool:
        """Check if viewport is desktop (1024px+)."""
        return True
def get_responsive_columns(desktop: list, tablet: list, mobile: list) -> list:
    """
    Return appropriate column ratio based on screen size.
    
    Args:
        desktop: Column ratios for desktop (>1024px)
        tablet: Column ratios for tablet (641px-1024px)
        mobile: Column ratios for mobile (<640px)
    
    Returns:
        Column ratios to use with st.columns()
    """
    # Streamlit doesn't expose screen width directly, but we can use CSS injection
    # For now, return desktop by default - client-side JS will handle responsive adjustments
    return desktop


def render_responsive_grid(columns_config: dict) -> None:
    """
    Render a responsive grid container with mobile-first approach.
    
    Args:
        columns_config: Dict with 'desktop', 'tablet', 'mobile' layout specs
    """
    st.markdown(
        '<div class="responsive-grid-container" data-columns="responsive">',
        unsafe_allow_html=True,
    )


def end_responsive_grid() -> None:
    """Close responsive grid container."""
    st.markdown("</div>", unsafe_allow_html=True)


class ResponsiveLayout:
    """Manage responsive layout transitions and breakpoints."""
    
    BREAKPOINTS = {
        "mobile": 640,
        "tablet": 1024,
        "desktop": 1200,
    }
    
    @staticmethod
    def inject_responsive_css() -> None:
        """Inject responsive CSS and JavaScript for adaptive layouts."""
        st.markdown(
            """
            <style>
            /* Responsive Breakpoints */
            
            /* Mobile First (< 640px) */
            @media (max-width: 639px) {
                .main .block-container {
                    padding-left: 0.8rem !important;
                    padding-right: 0.8rem !important;
                    max-width: 100% !important;
                }
                
                .stColumns > div {
                    gap: 0.6rem !important;
                }
                
                [data-testid="column"] {
                    min-width: 100% !important;
                }
                
                .hero-title {
                    font-size: 2.2rem !important;
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
            }
            
            /* Desktop (1024px+) */
            @media (min-width: 1024px) {
                .main .block-container {
                    padding-top: 1.4rem;
                    padding-bottom: 1.4rem;
                    max-width: 1180px;
                }
                
                .hero-title {
                    font-size: 3.15rem;
                }
            }
            
            /* Layout transitions */
            [data-testid="column"] {
                animation: slideIn 0.35s ease-out forwards;
            }
            
            .ui-card, .glass-card {
                animation: slideIn 0.4s ease-out, fadeIn 0.4s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(16px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
            
            /* Stagger animation for columns */
            .stColumns > div:nth-child(1) {
                animation-delay: 0ms;
            }
            
            .stColumns > div:nth-child(2) {
                animation-delay: 80ms;
            }
            
            .stColumns > div:nth-child(3) {
                animation-delay: 160ms;
            }
            
            /* Smooth transitions for all interactive elements */
            .ui-card, .glass-card, .ui-badge, .ui-metric {
                transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            
            /* Viewport-specific adjustments */
            @supports (position: fixed) {
                [data-testid="stSidebar"] {
                    transition: transform 0.3s ease, width 0.3s ease;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    @staticmethod
    def inject_responsive_js() -> None:
        """Inject JavaScript for runtime responsive behavior."""
        st.markdown(
            """
            <script>
            (function() {
              const updateLayout = () => {
                const width = window.innerWidth;
                const html = document.documentElement;
                
                if (width < 640) {
                  html.setAttribute('data-breakpoint', 'mobile');
                  html.setAttribute('data-viewport-width', width);
                } else if (width < 1024) {
                  html.setAttribute('data-breakpoint', 'tablet');
                  html.setAttribute('data-viewport-width', width);
                } else {
                  html.setAttribute('data-breakpoint', 'desktop');
                  html.setAttribute('data-viewport-width', width);
                }
              };
              
              updateLayout();
              window.addEventListener('resize', updateLayout);
              
              // Detect layout changes and trigger animations
              const observer = new MutationObserver(() => {
                const cards = document.querySelectorAll('.ui-card, .glass-card');
                cards.forEach((card, index) => {
                  card.style.animationDelay = (index * 50) + 'ms';
                });
              });
              
              observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: false
              });
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )


def responsive_columns(*args, **kwargs) -> list:
    """
    Wrapper around st.columns() that returns column contexts.
    Can be extended for future responsive behavior.
    """
    return st.columns(*args, **kwargs)
