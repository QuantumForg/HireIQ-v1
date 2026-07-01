"""Analytics section: executive KPIs and interactive score/role charts."""

from __future__ import annotations

import streamlit as st

from dashboard.components import charts, ui
from dashboard.sections.context import DashboardContext
from dashboard.services import analytics
from dashboard.services.analytics import ScoreStatistics

_PLOTLY_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}


def render(context: DashboardContext) -> None:
    """Render the analytics section."""
    ui.section_title(
        "Analytics", "Score Intelligence", "Real insights derived from the ranking outputs."
    )

    df = context.submission_df
    if df is None or "score" not in df:
        ui.empty_state(
            "No analytics available",
            "A valid submission with scores is required to compute analytics.",
            "📊",
        )
        return

    stats = analytics.compute_score_statistics(df["score"])
    if stats is None:
        ui.empty_state("No numeric scores", "The score column could not be interpreted.", "📊")
        return

    _render_kpis(stats)
    _render_distribution_charts(context)
    _render_role_charts(context)
    _render_stats_panel(stats)


def _render_kpis(stats: ScoreStatistics) -> None:
    """Render the four headline KPI pills."""
    ui.render_stat_row(
        [
            ("Average Score", f"{stats.mean:,.1f}"),
            ("Median Score", f"{stats.median:,.1f}"),
            ("Highest Score", f"{stats.maximum:,.1f}"),
            ("Lowest Score", f"{stats.minimum:,.1f}"),
        ],
        columns=4,
    )
    st.write("")


def _render_distribution_charts(context: DashboardContext) -> None:
    """Render histogram, rank-decay curve, and box plot."""
    left, right = st.columns(2, gap="large")
    with left:
        st.caption("Score Distribution")
        st.plotly_chart(
            charts.score_histogram(context.submission_df["score"]),
            use_container_width=True,
            config=_PLOTLY_CONFIG,
        )
    with right:
        st.caption("Score by Rank")
        st.plotly_chart(
            charts.score_rank_curve(context.submission_df),
            use_container_width=True,
            config=_PLOTLY_CONFIG,
        )

    st.caption("Score Percentiles")
    st.plotly_chart(
        charts.score_box(context.submission_df["score"]),
        use_container_width=True,
        config=_PLOTLY_CONFIG,
    )


def _render_role_charts(context: DashboardContext) -> None:
    """Render role distribution as a bar chart and donut."""
    if context.title_df is None:
        return
    ordered = analytics.title_share(context.title_df)
    left, right = st.columns(2, gap="large")
    with left:
        st.caption("Role Distribution")
        st.plotly_chart(
            charts.title_bar(ordered), use_container_width=True, config=_PLOTLY_CONFIG
        )
    with right:
        st.caption("Role Share")
        st.plotly_chart(
            charts.title_donut(ordered), use_container_width=True, config=_PLOTLY_CONFIG
        )


def _render_stats_panel(stats: ScoreStatistics) -> None:
    """Render a detailed statistics panel."""
    ui.section_title("Statistics", "Full Score Breakdown", "Computed across the submission set.")
    ui.render_stat_row(
        [
            ("Std Deviation", f"{stats.std:,.2f}"),
            ("25th Percentile", f"{stats.p25:,.1f}"),
            ("75th Percentile", f"{stats.p75:,.1f}"),
            ("IQR", f"{stats.iqr:,.1f}"),
        ],
        columns=4,
    )
    st.write("")
    ui.render_stat_row(
        [
            ("Range", f"{stats.score_range:,.1f}"),
            ("Sample Size", f"{stats.count:,}"),
            ("Max", f"{stats.maximum:,.1f}"),
            ("Min", f"{stats.minimum:,.1f}"),
        ],
        columns=4,
    )
