"""Plotly chart builders. Each function returns a styled ``go.Figure``.

Charts derive every value from the supplied dataframes. Styling relies on the
registered ``hireiq`` template, so these builders contain no duplicated theme
constants beyond chart-specific accents.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dashboard.config import THEME

_P = THEME.palette


def _base(fig: go.Figure, height: int = 340) -> go.Figure:
    """Apply shared layout sizing to a figure."""
    fig.update_layout(height=height, showlegend=False)
    return fig


def score_histogram(scores: pd.Series) -> go.Figure:
    """Histogram of candidate scores with an automatic bin count."""
    values = pd.to_numeric(scores, errors="coerce").dropna()
    bins = max(10, min(40, int(np.sqrt(values.size)) * 2))
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=bins,
            marker=dict(
                color=_P.purple,
                line=dict(color="rgba(255,255,255,0.12)", width=1),
            ),
            hovertemplate="Score %{x:.0f}<br>%{y} candidates<extra></extra>",
        )
    )
    fig.update_layout(bargap=0.06)
    fig.update_xaxes(title="Score")
    fig.update_yaxes(title="Candidates")
    return _base(fig)


def score_rank_curve(frame: pd.DataFrame) -> go.Figure:
    """Line + gradient-fill curve showing how score decays with rank."""
    ordered = frame.sort_values("rank")
    fig = go.Figure(
        go.Scatter(
            x=ordered["rank"],
            y=ordered["score"],
            mode="lines",
            line=dict(color=_P.orange, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(251,146,60,0.12)",
            hovertemplate="Rank %{x}<br>Score %{y:.1f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Rank")
    fig.update_yaxes(title="Score")
    return _base(fig)


def score_box(scores: pd.Series) -> go.Figure:
    """Box plot of the score distribution including outliers."""
    values = pd.to_numeric(scores, errors="coerce").dropna()
    fig = go.Figure(
        go.Box(
            x=values,
            boxpoints="outliers",
            marker=dict(color=_P.cyan),
            line=dict(color=_P.cyan),
            fillcolor="rgba(6,182,212,0.16)",
            hovertemplate="%{x:.1f}<extra></extra>",
            name="",
        )
    )
    fig.update_xaxes(title="Score")
    return _base(fig, height=240)


def top_candidates_bar(frame: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Horizontal bar chart of the highest-scoring candidates."""
    subset = frame.sort_values("score", ascending=False).head(top_n).iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=subset["score"],
            y=subset["candidate_id"],
            orientation="h",
            marker=dict(
                color=subset["score"],
                colorscale=[[0, _P.blue], [1, _P.purple]],
                line=dict(color="rgba(255,255,255,0.10)", width=1),
            ),
            hovertemplate="%{y}<br>Score %{x:.1f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Score")
    fig.update_layout(height=max(360, top_n * 22))
    return fig


def title_bar(distribution: pd.DataFrame) -> go.Figure:
    """Descending bar chart of role/title counts."""
    ordered = distribution.sort_values("count", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=ordered["count"],
            y=ordered["title"],
            orientation="h",
            marker=dict(
                color=ordered["count"],
                colorscale=[[0, _P.pink], [1, _P.purple]],
                line=dict(color="rgba(255,255,255,0.10)", width=1),
            ),
            hovertemplate="%{y}<br>%{x} candidates<extra></extra>",
        )
    )
    fig.update_xaxes(title="Candidates")
    fig.update_layout(height=max(360, len(ordered) * 26))
    return fig


def title_donut(distribution: pd.DataFrame) -> go.Figure:
    """Modern donut chart of role share."""
    fig = go.Figure(
        go.Pie(
            labels=distribution["title"],
            values=distribution["count"],
            hole=0.6,
            sort=True,
            direction="clockwise",
            marker=dict(line=dict(color="rgba(9,9,11,0.8)", width=2)),
            hovertemplate="%{label}<br>%{value} (%{percent})<extra></extra>",
            textposition="outside",
            textinfo="label",
        )
    )
    fig.update_layout(height=420, showlegend=False)
    return fig
