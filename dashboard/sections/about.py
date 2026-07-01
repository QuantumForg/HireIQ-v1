"""About section: project summary, technology stack, and architecture notes."""

from __future__ import annotations

import streamlit as st

from dashboard import config
from dashboard.components import ui
from dashboard.sections.context import DashboardContext


def render(context: DashboardContext) -> None:
    """Render the about section."""
    ui.section_title("About", "HireIQ V1", "An explainable candidate ranking platform.")

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(_overview_html(), unsafe_allow_html=True)
    with right:
        st.markdown(_stack_html(), unsafe_allow_html=True)

    _render_features_card(context)


def _overview_html() -> str:
    """Return the project overview card."""
    return f"""
    <div class="hq-card hq-animate">
        <div style="font-weight:700;font-size:18px;margin-bottom:10px;">Overview</div>
        <p style="color:var(--text-secondary);line-height:1.7;font-size:14.5px;">
            {config.APP_NAME} ranks candidates against a role using a transparent,
            feature-driven scoring engine. The pipeline transforms raw profiles into
            engineered features, scores and orders them, then emits a validated
            submission alongside analytical reports.
        </p>
        <p style="color:var(--text-secondary);line-height:1.7;font-size:14.5px;">
            This dashboard is a read-only visualization layer. It never recomputes
            rankings or mutates outputs &mdash; every figure is sourced from verified
            pipeline artifacts.
        </p>
    </div>
    """


def _stack_html() -> str:
    """Return the technology stack card."""
    chips = ["Python", "Pandas", "NumPy", "Plotly", "Streamlit"]
    rendered = "".join(
        f'<span class="hq-badge" style="margin:4px 6px 4px 0;">{chip}</span>' for chip in chips
    )
    return f"""
    <div class="hq-card hq-animate">
        <div style="font-weight:700;font-size:18px;margin-bottom:14px;">Technology</div>
        <div style="display:flex;flex-wrap:wrap;">{rendered}</div>
        <div style="margin-top:18px;font-size:13px;color:var(--text-muted);">
            Built for the {config.HACKATHON}. Version {config.APP_VERSION}.
        </div>
    </div>
    """


def _render_features_card(context: DashboardContext) -> None:
    """Render a summary of the features dataset, never the full dataframe."""
    if not context.features.ok:
        return
    summary = context.features.data
    ui.section_title("", "Feature Dataset", "Summary of the engineered feature matrix.")
    ui.render_stat_row(
        [
            ("Profiles", f"{summary['rows']:,}"),
            ("Features", f"{summary['columns']:,}"),
            ("Numeric Features", f"{summary['numeric_columns']:,}"),
            ("Missing Values", f"{summary['missing_values']:,}"),
        ],
        columns=4,
    )
