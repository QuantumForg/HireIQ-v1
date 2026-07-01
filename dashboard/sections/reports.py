"""Reports section: preview and download generated text/CSV reports."""

from __future__ import annotations

import streamlit as st

from dashboard import config
from dashboard.components import ui
from dashboard.sections.context import DashboardContext


def render(context: DashboardContext) -> None:
    """Render the reports section."""
    ui.section_title(
        "Reports", "Generated Artifacts", "Preview and export the pipeline's reports."
    )

    _render_ranking_report(context)
    _render_csv_report(
        "Title Distribution",
        config.TITLE_DISTRIBUTION_FILE,
        context.title_distribution,
    )
    _render_csv_report("Top 100 Candidates", config.TOP100_FILE, context.top100)


def _render_ranking_report(context: DashboardContext) -> None:
    """Render the ranking text report with a preview and download."""
    result = context.ranking_report
    if not result.ok:
        ui.error_card("Ranking report unavailable", result.error or "Report not found.")
        return

    content: str = result.data
    ui.section_title("", "Ranking Report", "")
    with st.expander("Preview ranking_report.txt", expanded=True):
        ui.code_block(content)

    st.download_button(
        "Download ranking_report.txt",
        data=content.encode("utf-8"),
        file_name=config.RANKING_REPORT_FILE,
        mime="text/plain",
    )
    st.write("")


def _render_csv_report(title: str, filename: str, result) -> None:
    """Render a CSV report preview and download control."""
    if not result.ok:
        ui.error_card(f"{title} unavailable", result.error or "File not found.")
        return

    df = result.data
    meta = f"{len(df):,} rows · {df.shape[1]} columns"
    st.markdown(ui.file_card_html(title, meta), unsafe_allow_html=True)

    with st.expander(f"Preview {filename}", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True, height=320)

    st.download_button(
        f"Download {filename}",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=f"dl_{filename}",
    )
    st.write("")
