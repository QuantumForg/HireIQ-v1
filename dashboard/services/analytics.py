"""Score analytics computed purely from pipeline outputs.

All statistics are derived from ``submission.csv`` / ``top100.csv``. Nothing is
hardcoded or fabricated; if a value cannot be computed it is reported as
``None`` so the UI can show a neutral placeholder.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ScoreStatistics:
    """Descriptive statistics for a candidate score column."""

    count: int
    mean: float
    median: float
    std: float
    minimum: float
    maximum: float
    p25: float
    p75: float

    @property
    def iqr(self) -> float:
        """Inter-quartile range (75th minus 25th percentile)."""
        return self.p75 - self.p25

    @property
    def score_range(self) -> float:
        """Difference between the maximum and minimum score."""
        return self.maximum - self.minimum


def compute_score_statistics(scores: pd.Series) -> ScoreStatistics | None:
    """Compute descriptive statistics from a numeric score series.

    Args:
        scores: A pandas Series of candidate scores.

    Returns:
        A :class:`ScoreStatistics` instance, or ``None`` if no valid numeric
        values are present.
    """
    clean = pd.to_numeric(scores, errors="coerce").dropna()
    if clean.empty:
        return None

    return ScoreStatistics(
        count=int(clean.size),
        mean=float(clean.mean()),
        median=float(clean.median()),
        std=float(clean.std(ddof=0)),
        minimum=float(clean.min()),
        maximum=float(clean.max()),
        p25=float(clean.quantile(0.25)),
        p75=float(clean.quantile(0.75)),
    )


def title_share(distribution: pd.DataFrame) -> pd.DataFrame:
    """Return the title distribution sorted descending with a share column.

    Args:
        distribution: DataFrame with ``title`` and ``count`` columns.

    Returns:
        A sorted copy with an added ``share`` (fraction of total) column.
    """
    ordered = distribution.sort_values("count", ascending=False).reset_index(drop=True)
    total = ordered["count"].sum()
    ordered["share"] = ordered["count"] / total if total else 0.0
    return ordered
