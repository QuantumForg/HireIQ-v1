"""Explainability section: per-candidate score reasoning explorer."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from dashboard.components import ui
from dashboard.sections.context import DashboardContext

_PAGE_SIZE = 9


def render(context: DashboardContext) -> None:
    """Render the explainability section."""
    ui.section_title(
        "Explainability", "Why Candidates Rank", "Transparent reasoning behind every score."
    )

    df = context.submission_df
    if df is None or "reasoning" not in df:
        ui.empty_state(
            "No reasoning available",
            "A submission containing a reasoning column is required.",
            "💡",
        )
        return

    query = st.text_input(
        "Search reasoning",
        placeholder="Search candidate ID...",
        label_visibility="collapsed",
    ).strip().lower()

    view = df.sort_values("rank")
    if query:
        view = view[view["candidate_id"].astype(str).str.lower().str.contains(query, na=False)]

    if view.empty:
        ui.empty_state("No matches", "No candidates match your search.", "🔍")
        return

    _render_cards(view.head(_PAGE_SIZE))
    if len(view) > _PAGE_SIZE:
        st.caption(f"Showing top {_PAGE_SIZE} of {len(view)} matching candidates.")


def _render_cards(view: pd.DataFrame) -> None:
    """Render candidate reasoning cards in a three-column grid."""
    records = view.to_dict("records")
    for start in range(0, len(records), 3):
        row = records[start : start + 3]
        cols = st.columns(len(row), gap="medium")
        for col, record in zip(cols, row):
            col.markdown(_card_html(record), unsafe_allow_html=True)


def _card_html(record: dict) -> str:
    """Build the HTML for a single explainability card."""
    rank = escape(str(record.get("rank", "—")))
    cid = escape(str(record.get("candidate_id", "Unknown")))
    score = record.get("score")
    score_label = f"{float(score):,.1f}" if pd.notna(score) else "—"
    reasoning = escape(str(record.get("reasoning", "No reasoning provided.")))
    return f"""
    <div class="hq-card hq-animate" style="margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="hq-trend neutral">#{rank}</span>
            <span style="font-weight:800;font-size:18px;color:#c4b5fd;">{score_label}</span>
        </div>
        <div style="font-weight:700;font-size:15px;margin:12px 0 8px 0;">{cid}</div>
        <div style="font-size:13px;color:var(--text-secondary);line-height:1.6;">{reasoning}</div>
    </div>
    """
