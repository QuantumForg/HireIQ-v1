"""Overview section: hero, executive metrics, and the pipeline timeline."""

from __future__ import annotations

import pandas as pd

from dashboard import config
from dashboard.components import ui
from dashboard.components.ui import Metric
from dashboard.sections.context import DashboardContext
from dashboard.utils import compact_number

# Lucide icon path data used by metric cards.
_ICON_USERS = "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"
_ICON_DB = "M12 3c4.4 0 8 1.3 8 3s-3.6 3-8 3-8-1.3-8-3 3.6-3 8-3zM4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"
_ICON_TROPHY = "M8 21h8M12 17v4M7 4h10v4a5 5 0 0 1-10 0V4zM5 9a2 2 0 0 1-2-2V6h4M19 9a2 2 0 0 0 2-2V6h-4"
_ICON_LAYERS = "M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
_ICON_FILE = "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6"
_ICON_SHIELD = "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"


def render(context: DashboardContext) -> None:
    """Render the overview section."""
    ui.render_hero(
        badge=f"Built for {config.HACKATHON}",
        title=config.APP_NAME,
        subtitle=config.APP_TAGLINE,
        description=(
            "An explainable, production-grade ranking engine that scores and "
            "orders candidates against the role. Every metric on this dashboard "
            "is read directly from verified pipeline outputs."
        ),
    )

    _render_metrics(context)

    ui.section_title(
        "Pipeline", "Processing Stages", "End-to-end flow from dataset to validated submission."
    )
    ui.render_pipeline(_pipeline_stages(context))


def _render_metrics(context: DashboardContext) -> None:
    """Compose and render the six executive metric cards."""
    ui.render_metric_grid(
        [
            _candidates_ranked(context),
            _candidate_pool(context),
            _top_score(context),
            _roles_metric(context),
            _reports_metric(),
            _validation_metric(context),
        ],
        columns=3,
    )


def _candidates_ranked(context: DashboardContext) -> Metric:
    count = len(context.submission_df) if context.submission_df is not None else 0
    return Metric(
        label="Candidates Ranked",
        value=compact_number(count) if count else "—",
        description="Final ordered submission",
        icon=_ICON_USERS,
        trend_text="Submission ready" if count else "Pending",
        trend_kind="up" if count else "muted",
        accent="#3B82F6",
    )


def _candidate_pool(context: DashboardContext) -> Metric:
    if context.features.ok:
        rows = context.features.data["rows"]
        return Metric(
            label="Candidate Pool",
            value=compact_number(rows),
            description="Profiles evaluated by the engine",
            icon=_ICON_DB,
            trend_text="Full corpus",
            trend_kind="neutral",
            accent="#06B6D4",
        )
    return Metric("Candidate Pool", "—", "features.csv unavailable", _ICON_DB, "Pending", "muted", "#06B6D4")


def _top_score(context: DashboardContext) -> Metric:
    df = context.submission_df
    if df is not None and "score" in df:
        top = pd.to_numeric(df["score"], errors="coerce").max()
        return Metric(
            label="Top Score",
            value=f"{top:,.1f}",
            description="Highest candidate score",
            icon=_ICON_TROPHY,
            trend_text="Rank #1",
            trend_kind="up",
            accent="#FB923C",
        )
    return Metric("Top Score", "—", "No scores available", _ICON_TROPHY, "Pending", "muted", "#FB923C")


def _roles_metric(context: DashboardContext) -> Metric:
    if context.title_df is not None:
        roles = len(context.title_df)
        return Metric(
            label="Roles Represented",
            value=str(roles),
            description="Distinct titles in the top 100",
            icon=_ICON_LAYERS,
            trend_text="Diverse pool",
            trend_kind="neutral",
            accent="#7C3AED",
        )
    return Metric("Roles Represented", "—", "Distribution unavailable", _ICON_LAYERS, "Pending", "muted", "#7C3AED")


def _reports_metric() -> Metric:
    report_files = (
        config.RANKING_REPORT_FILE,
        config.TOP100_FILE,
        config.TITLE_DISTRIBUTION_FILE,
    )
    present = sum(1 for name in report_files if (config.OUTPUTS_DIR / name).exists())
    return Metric(
        label="Reports Generated",
        value=f"{present}/{len(report_files)}",
        description="Analytical artifacts available",
        icon=_ICON_FILE,
        trend_text="Complete" if present == len(report_files) else "Partial",
        trend_kind="up" if present == len(report_files) else "muted",
        accent="#EC4899",
    )


def _validation_metric(context: DashboardContext) -> Metric:
    status = context.validation
    if status.is_valid:
        return Metric("Validation", "Passed", "Official validator", _ICON_SHIELD, "✓ Valid", "up", "#22C55E")
    if status.is_failed:
        return Metric("Validation", "Issues", "Official validator", _ICON_SHIELD, "Review", "muted", "#FACC15")
    return Metric("Validation", "Pending", "Not yet executed", _ICON_SHIELD, "Unknown", "muted", "#7D8597")


def _pipeline_stages(context: DashboardContext) -> list[tuple[str, bool]]:
    """Derive completion of each pipeline stage from available artifacts."""
    has_submission = context.submission.ok
    return [
        ("Dataset", context.features.ok),
        ("Features", context.features.ok),
        ("Ranking", context.top100.ok),
        ("Submission", has_submission),
        ("Reports", context.ranking_report.ok),
        ("Validation", context.validation.is_valid),
        ("Completed", has_submission and context.validation.is_valid),
    ]
