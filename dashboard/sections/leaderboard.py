"""Leaderboard section: searchable, filterable ranked candidate table."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components import ui
from dashboard.sections.context import DashboardContext

_TOP_N_OPTIONS = (10, 25, 50, 100)


def render(context: DashboardContext) -> None:
    """Render the leaderboard section."""
    ui.section_title(
        "Leaderboard", "Top Ranked Candidates", "Search, filter, and export the ranking."
    )

    df = context.submission_df
    if df is None:
        ui.error_card(
            "Submission unavailable",
            context.submission.error or "submission.csv could not be loaded.",
        )
        return

    query, top_n = _render_controls(df)
    view = _filter(df, query, top_n)

    if view.empty:
        ui.empty_state("No matches", "No candidates match your search.", "🔍")
        return

    score_min, score_max = _progress_range(df.get("score"))

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", width="small", format="%d"),
            "candidate_id": st.column_config.TextColumn("Candidate ID", width="medium"),
            "score": st.column_config.ProgressColumn(
                "Score",
                format="%.1f",
                min_value=score_min,
                max_value=score_max,
            ),
            "reasoning": st.column_config.TextColumn("Reasoning", width="large"),
        },
    )

    st.download_button(
        "Download submission.csv",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="submission.csv",
        mime="text/csv",
    )


def _progress_range(scores: "pd.Series | None") -> tuple[float, float]:
    """Return a safe ``(min, max)`` range for the score progress column.

    Streamlit's ``ProgressColumn`` requires a strictly positive span, so a
    degenerate range (single row, identical scores, or missing data) is
    widened to keep the bar renderable.

    Args:
        scores: The full submission score series, or ``None``.

    Returns:
        A ``(minimum, maximum)`` tuple where ``maximum > minimum``.
    """
    if scores is None:
        return 0.0, 1.0

    numeric = pd.to_numeric(scores, errors="coerce").dropna()
    if numeric.empty:
        return 0.0, 1.0

    minimum = float(numeric.min())
    maximum = float(numeric.max())
    if maximum <= minimum:
        maximum = minimum + 1.0
    return minimum, maximum


def _render_controls(df: pd.DataFrame) -> tuple[str, int]:
    """Render the search box and top-N selector."""
    search_col, filter_col = st.columns([3, 1], gap="medium")
    query = search_col.text_input(
        "Search", placeholder="Search candidate ID or reasoning...", label_visibility="collapsed"
    )
    top_n = filter_col.selectbox(
        "Show", _TOP_N_OPTIONS, index=len(_TOP_N_OPTIONS) - 1, label_visibility="collapsed"
    )
    return query.strip(), int(top_n)


def _filter(df: pd.DataFrame, query: str, top_n: int) -> pd.DataFrame:
    """Apply rank limit and free-text search."""
    view = df.sort_values("rank").head(top_n)
    if not query:
        return view

    lowered = query.lower()
    mask = pd.Series(False, index=view.index)
    for column in ("candidate_id", "reasoning"):
        if column in view.columns:
            mask |= view[column].astype(str).str.lower().str.contains(lowered, na=False, regex=False)
    return view[mask]
