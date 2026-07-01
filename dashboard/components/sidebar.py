"""Floating glass sidebar with section navigation and a live status card."""

from __future__ import annotations

from html import escape

import streamlit as st

from dashboard import config
from dashboard.config import APP_NAME, APP_VERSION, NAVIGATION
from dashboard.services.validation import ValidationStatus
from dashboard.utils import image_data_uri

_STATE_KEY = "active_section"
_ANIMATIONS_KEY = "animations_enabled"


def current_section() -> str:
    """Return the currently selected section key."""
    return st.session_state.get(_STATE_KEY, NAVIGATION[0].key)


def animations_enabled() -> bool:
    """Return whether UI animations are currently enabled."""
    return st.session_state.get(_ANIMATIONS_KEY, True)


def render_sidebar(validation: ValidationStatus) -> str:
    """Render the sidebar and return the active section key.

    Args:
        validation: Resolved validation status for the footer status card.

    Returns:
        The key of the section the user has selected.
    """
    if _STATE_KEY not in st.session_state:
        st.session_state[_STATE_KEY] = NAVIGATION[0].key

    active_key = st.session_state[_STATE_KEY]

    with st.sidebar:
        st.markdown(_brand_html(), unsafe_allow_html=True)

        # Group navigation into sections
        groups = {
            "MAIN": ["overview", "analytics", "leaderboard", "explain"],
            "REPORTS": ["reports", "validation", "artifacts"],
            "ABOUT": ["about"]
        }

        for group_name, item_keys in groups.items():
            st.markdown(f'<div class="hq-menu-label">{group_name}</div>', unsafe_allow_html=True)
            for key in item_keys:
                item = next((x for x in NAVIGATION if x.key == key), None)
                if not item:
                    continue
                is_active = (active_key == item.key)
                
                clicked = st.button(
                    item.label,
                    key=f"nav_{item.key}",
                    use_container_width=True,
                    icon=f":material/{item.icon}:",
                    type="primary" if is_active else "secondary",
                )
                if clicked:
                    st.session_state[_STATE_KEY] = item.key
                    st.rerun()

        _render_controls()
        
        # Submission status section and card
        st.markdown('<div class="hq-menu-label">Submission</div>', unsafe_allow_html=True)
        st.markdown(_status_html(validation), unsafe_allow_html=True)

    return st.session_state[_STATE_KEY]


def _render_controls() -> None:
    """Render the data-refresh button and animations toggle inside a controls card container."""
    st.markdown('<div class="hq-menu-label">Controls</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Trigger stable selector in CSS via sibling match
        st.markdown('<div class="hq-refresh"></div>', unsafe_allow_html=True)
        if st.button(
            "Refresh data",
            key="refresh_data",
            use_container_width=True,
            icon=":material/sync:",
            type="secondary",
        ):
            st.cache_data.clear()
            st.toast("Data refreshed from outputs.", icon="✅")
            st.rerun()

        st.toggle(
            "Animations",
            value=st.session_state.get(_ANIMATIONS_KEY, True),
            key=_ANIMATIONS_KEY,
            help="Disable motion for a calmer, reduced-motion experience.",
        )


def _brand_html() -> str:
    """Return the brand lockup markup.

    Renders the custom logo image from ``assets/logo.png`` when available,
    otherwise falls back to the built-in "HQ" gradient mark.
    """
    logo = image_data_uri(config.LOGO_PATH)
    if logo:
        return f"""
        <div class="hq-brand hq-brand-logo">
            <img src="{logo}" alt="{escape(APP_NAME)} logo" />
        </div>
        """
    return f"""
    <div class="hq-brand">
        <div class="hq-brand-mark">HQ</div>
        <div>
            <div class="hq-brand-name">{escape(APP_NAME)}</div>
            <div class="hq-brand-sub">AI Recruitment Intelligence</div>
        </div>
    </div>
    """


def _status_html(validation: ValidationStatus) -> str:
    """Return the bottom status card reflecting validation state."""
    if validation.is_valid:
        return """
        <div class="hq-side-status success">
            <div class="hq-side-status-icon">✔</div>
            <div class="hq-side-status-content">
                <div class="hq-side-status-title">Submission Ready</div>
                <div class="hq-side-status-desc">Validator Passed</div>
            </div>
        </div>
        """
    if validation.is_failed:
        return """
        <div class="hq-side-status error">
            <div class="hq-side-status-icon">✗</div>
            <div class="hq-side-status-content">
                <div class="hq-side-status-title">Issues Detected</div>
                <div class="hq-side-status-desc">Validator Failed</div>
            </div>
        </div>
        """
    return """
    <div class="hq-side-status pending">
        <div class="hq-side-status-icon">⟳</div>
        <div class="hq-side-status-content">
            <div class="hq-side-status-title">Status Pending</div>
            <div class="hq-side-status-desc">Awaiting validation</div>
        </div>
    </div>
    """
