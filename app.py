"""HireIQ V1 dashboard entry point.

Responsibilities are limited to application bootstrap: page configuration,
theme loading, navigation, and composition of section renderers. All business
logic lives in the ``dashboard`` package.

Run with::

    streamlit run app.py
"""

from __future__ import annotations

import logging

import streamlit as st

from dashboard import config
from dashboard.components import sidebar, ui
from dashboard.sections import (
    about,
    analytics,
    artifacts,
    explain,
    leaderboard,
    overview,
    reports,
    validation,
)
from dashboard.sections.context import DashboardContext, build_context
from dashboard.styles.plotly_theme import register_plotly_theme
from dashboard.styles.theme import inject_global_styles, inject_motion_preference

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s")

# Maps navigation keys to their section renderer.
_SECTION_RENDERERS = {
    "overview": overview.render,
    "analytics": analytics.render,
    "leaderboard": leaderboard.render,
    "explain": explain.render,
    "reports": reports.render,
    "validation": validation.render,
    "artifacts": artifacts.render,
    "about": about.render,
}


def _configure_page() -> None:
    """Apply Streamlit page configuration and global styling."""
    st.set_page_config(
        page_title=f"{config.APP_NAME} · Analytics",
        page_icon=str(config.LOGO_PATH) if config.LOGO_PATH.exists() else "◆",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Read the appearance toggle's widget state directly so the choice applies
    # within the same rerun it was changed.
    mode = "light" if st.session_state.get("theme_toggle", False) else "dark"
    inject_global_styles(mode)
    inject_motion_preference(st.session_state.get("animations_enabled", True))
    register_plotly_theme(mode)


def _render_active_section(section_key: str, context: DashboardContext) -> None:
    """Dispatch rendering to the selected section, falling back to overview."""
    renderer = _SECTION_RENDERERS.get(section_key, overview.render)
    renderer(context)


def main() -> None:
    """Compose and render the dashboard for the current rerun."""
    _configure_page()
    context = build_context()
    section_key = sidebar.render_sidebar(context.validation)
    _render_active_section(section_key, context)
    ui.render_footer(config.APP_NAME, config.APP_VERSION, config.HACKATHON)


if __name__ == "__main__":
    main()
