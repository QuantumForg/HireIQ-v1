"""Stateless presentational components rendered as themed HTML.

Each helper returns an HTML string (``*_html``) or renders directly via
Streamlit. Keeping markup generation pure makes the components easy to compose
and test.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

import streamlit as st

from dashboard.utils import hex_to_rgba


def _svg(path_data: str, size: int = 20, color: str = "currentColor") -> str:
    """Return an inline Lucide-style stroked SVG icon.

    Args:
        path_data: The ``d`` attribute geometry for the icon path.
        size: Square pixel size of the icon.
        color: Stroke color (any CSS color value).
    """
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round"><path d="{path_data}"/></svg>'
    )


def section_title(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Render a consistent section heading block."""
    sub = f'<div class="sub">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="hq-section hq-animate">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <h2>{escape(title)}</h2>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )


@dataclass(frozen=True)
class Metric:
    """Configuration for a single metric card."""

    label: str
    value: str
    description: str
    icon: str
    trend_text: str = ""
    trend_kind: str = "neutral"  # up | neutral | muted
    accent: str = "#7C3AED"  # icon tile accent color


def metric_card_html(metric: Metric) -> str:
    """Return HTML for a single premium metric card."""
    trend = ""
    if metric.trend_text:
        trend = (
            f'<div class="hq-trend {escape(metric.trend_kind)}">'
            f"{escape(metric.trend_text)}</div>"
        )
    icon_style = (
        f"background:{hex_to_rgba(metric.accent, 0.16)};"
        f"border-color:{hex_to_rgba(metric.accent, 0.45)};"
        f"box-shadow:0 8px 22px {hex_to_rgba(metric.accent, 0.28)};"
    )
    return f"""
    <div class="hq-card hq-metric hq-animate">
        <div class="icon" style="{icon_style}">{_svg(metric.icon, 21, metric.accent)}</div>
        <div class="label">{escape(metric.label)}</div>
        <div class="value">{escape(metric.value)}</div>
        <div class="desc">{escape(metric.description)}</div>
        {trend}
    </div>
    """


def render_metric_grid(metrics: list[Metric], columns: int = 3) -> None:
    """Render metric cards in an aligned responsive grid."""
    for start in range(0, len(metrics), columns):
        row = metrics[start : start + columns]
        cols = st.columns(len(row), gap="medium")
        for col, metric in zip(cols, row):
            col.markdown(metric_card_html(metric), unsafe_allow_html=True)


def empty_state(title: str, message: str, glyph: str = "📭") -> None:
    """Render a friendly empty state instead of a blank area."""
    st.markdown(
        f"""
        <div class="hq-empty hq-animate">
            <div class="glyph">{glyph}</div>
            <h4>{escape(title)}</h4>
            <p>{escape(message)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def error_card(title: str, message: str) -> None:
    """Render a non-technical error card with recovery guidance."""
    st.markdown(
        f"""
        <div class="hq-error hq-animate">
            <div class="t">{escape(title)}</div>
            <div class="m">{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_pill(label: str, value: str) -> str:
    """Return HTML for a compact statistic pill."""
    return f"""
    <div class="hq-stat hq-animate">
        <div class="k">{escape(label)}</div>
        <div class="v">{escape(value)}</div>
    </div>
    """


def render_stat_row(pairs: list[tuple[str, str]], columns: int = 4) -> None:
    """Render a row of statistic pills."""
    cols = st.columns(columns, gap="medium")
    for index, (label, value) in enumerate(pairs):
        cols[index % columns].markdown(stat_pill(label, value), unsafe_allow_html=True)


def file_card_html(title: str, meta: str, icon: str = "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z") -> str:
    """Return HTML for a file/artifact descriptor card (without the button)."""
    return f"""
    <div class="hq-card hq-animate" style="margin-bottom:10px;">
        <div class="hq-file">
            <div class="ficon">{_svg(icon, 22, "#93c5fd")}</div>
            <div>
                <div class="fname">{escape(title)}</div>
                <div class="fmeta">{escape(meta)}</div>
            </div>
        </div>
    </div>
    """


def render_hero(badge: str, title: str, subtitle: str, description: str) -> None:
    """Render the primary hero banner."""
    st.markdown(
        f"""
        <div class="hq-hero hq-animate">
            <div class="hq-hero-orb one"></div>
            <div class="hq-hero-orb two"></div>
            <div class="hq-badge"><span class="dot"></span>{escape(badge)}</div>
            <h1>{escape(title)}</h1>
            <div class="subtitle">{escape(subtitle)}</div>
            <div class="desc">{escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pipeline(stages: list[tuple[str, bool]]) -> None:
    """Render the horizontal pipeline timeline.

    Args:
        stages: Ordered ``(label, completed)`` pairs.
    """
    check = _svg("M20 6 9 17l-5-5", 18, "#22C55E")
    pieces: list[str] = []
    for index, (label, done) in enumerate(stages):
        node_class = "hq-pipe-node done" if done else "hq-pipe-node"
        inner = check if done else str(index + 1)
        pieces.append(
            f'<div class="hq-pipe-stage"><div class="{node_class}">{inner}</div>'
            f'<div class="hq-pipe-label">{escape(label)}</div></div>'
        )
        if index < len(stages) - 1:
            pieces.append('<div class="hq-pipe-conn"></div>')

    st.markdown(
        f'<div class="hq-card hq-animate"><div class="hq-pipe">{"".join(pieces)}</div></div>',
        unsafe_allow_html=True,
    )


def code_block(content: str) -> None:
    """Render preformatted text while preserving exact line formatting.

    Uses ``st.text`` rather than ``st.markdown``/``st.code`` so newlines and
    column alignment are preserved verbatim, with no dependency on the
    front-end syntax-highlighter asset.
    """
    st.text(content)


def render_footer(app_name: str, version: str, hackathon: str) -> None:
    st.markdown(
        f"""
        <div class="hq-footer">
            <div><b>{escape(app_name)}</b> · v{escape(version)}</div>
            <div>Built for {escape(hackathon)} · INDIA.RUNS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
