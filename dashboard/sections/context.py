"""Shared dashboard data context assembled once per rerun.

Loaders are individually cached, so building the context is cheap. Bundling
the results keeps section renderers free of loading concerns.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from dashboard import config
from dashboard.services import data_loader
from dashboard.services.data_loader import LoadResult
from dashboard.services.validation import ValidationStatus, resolve_validation


@dataclass(frozen=True)
class DashboardContext:
    """Aggregated, ready-to-render pipeline data."""

    submission: LoadResult
    top100: LoadResult
    title_distribution: LoadResult
    ranking_report: LoadResult
    features: LoadResult
    validation: ValidationStatus

    @property
    def submission_df(self) -> pd.DataFrame | None:
        return self.submission.data if self.submission.ok else None

    @property
    def top100_df(self) -> pd.DataFrame | None:
        return self.top100.data if self.top100.ok else None

    @property
    def title_df(self) -> pd.DataFrame | None:
        return self.title_distribution.data if self.title_distribution.ok else None


def build_context() -> DashboardContext:
    """Load every artifact needed by the dashboard."""
    return DashboardContext(
        submission=data_loader.load_csv(
            config.SUBMISSION_FILE, config.SUBMISSION_REQUIRED_COLUMNS
        ),
        top100=data_loader.load_csv(config.TOP100_FILE),
        title_distribution=data_loader.load_csv(config.TITLE_DISTRIBUTION_FILE),
        ranking_report=data_loader.load_text(config.RANKING_REPORT_FILE),
        features=data_loader.features_summary(),
        validation=resolve_validation(),
    )
