"""Validation section: premium pass/fail status card."""

from __future__ import annotations

from html import escape

import streamlit as st

from dashboard.components import ui
from dashboard.sections.context import DashboardContext


def render(context: DashboardContext) -> None:
    """Render the validation section."""
    ui.section_title(
        "Validation", "Submission Integrity", "Status from the official challenge validator."
    )

    status = context.validation
    if status.is_valid:
        _render_success(status.source)
    elif status.is_failed:
        _render_failure(status.issues, status.source)
    else:
        _render_unknown()


def _render_success(source: str) -> None:
    """Render the success state card."""
    st.markdown(
        f"""
        <div class="hq-validation ok hq-animate">
            <div class="ring">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
                     stroke="#22C55E" stroke-width="2.5" stroke-linecap="round"
                     stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            </div>
            <h3>Submission Valid</h3>
            <p>The official validator completed successfully against all rules.</p>
            <p style="font-size:12px;color:var(--text-muted);">Source: {escape(source)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_failure(issues: list[str], source: str) -> None:
    """Render the failure state card with collapsible issues."""
    st.markdown(
        f"""
        <div class="hq-validation fail hq-animate">
            <div class="ring">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
                     stroke="#EF4444" stroke-width="2.5" stroke-linecap="round"
                     stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </div>
            <h3>Validation Issues Found</h3>
            <p>{len(issues)} issue(s) reported. Review the details below.</p>
            <p style="font-size:12px;color:var(--text-muted);">Source: {escape(source)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("View reported issues", expanded=True):
        for issue in issues:
            st.markdown(f"- {issue}")


def _render_unknown() -> None:
    """Render the neutral pending state card."""
    st.markdown(
        """
        <div class="hq-validation unknown hq-animate">
            <div class="ring">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
                     stroke="#7D8597" stroke-width="2.5" stroke-linecap="round"
                     stroke-linejoin="round"><path d="M12 16v-4M12 8h.01"/>
                     <circle cx="12" cy="12" r="10"/></svg>
            </div>
            <h3>Validation Pending</h3>
            <p>Validation has not been executed for the current submission.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
