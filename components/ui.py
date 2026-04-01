import streamlit as st
from typing import Iterable, Optional


def card_start(title: str, subtitle: Optional[str] = None, emoji: str = "") -> None:
    """Start a shadcn-style card."""
    st.markdown(
        f"""
        <div class="ui-card">
          <div class="ui-card-header">
            <div>
              <div class="ui-card-title">{emoji} {title}</div>
              {f'<div class="ui-card-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
          </div>
        """,
        unsafe_allow_html=True,
    )


def card_end() -> None:
    """Close a shadcn-style card."""
    st.markdown("</div>", unsafe_allow_html=True)


def badge(text: str, variant: str = "default") -> None:
    """Render a small badge."""
    st.markdown(f'<span class="ui-badge ui-badge-{variant}">{text}</span>', unsafe_allow_html=True)


def metric(label: str, value: str, hint: str = "") -> None:
    """Render a compact metric tile."""
    st.markdown(
        f"""
        <div class="ui-metric">
          <div class="ui-metric-label">{label}</div>
          <div class="ui-metric-value">{value}</div>
          {f'<div class="ui-metric-hint">{hint}</div>' if hint else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, description: Optional[str] = None) -> None:
    """Render a section title."""
    st.markdown(
        f"""
        <div class="ui-section-title">{title}</div>
        {f'<div class="ui-section-description">{description}</div>' if description else ''}
        """,
        unsafe_allow_html=True,
    )


def separator() -> None:
    st.markdown('<div class="ui-separator"></div>', unsafe_allow_html=True)
