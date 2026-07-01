"""Custom Plotly templates for consistent dark and light chart aesthetics."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

from dashboard.config import THEME

# Ordered categorical palette derived from theme accent colors (mode-agnostic).
COLORWAY: list[str] = [
    THEME.palette.purple,
    THEME.palette.blue,
    THEME.palette.pink,
    THEME.palette.cyan,
    THEME.palette.orange,
    THEME.palette.success,
    THEME.palette.warning,
    THEME.palette.info,
]

# Per-mode neutral colors for axes, gridlines, text, and hover labels.
_MODE_COLORS: dict[str, dict[str, str]] = {
    "dark": {
        "text": "#B4B7C5",
        "muted": "#7D8597",
        "grid": "rgba(255,255,255,0.06)",
        "zero": "rgba(255,255,255,0.08)",
        "line": "rgba(255,255,255,0.10)",
        "hover_bg": "rgba(17,24,39,0.95)",
        "hover_text": "#FFFFFF",
    },
    "light": {
        "text": "#475569",
        "muted": "#64748B",
        "grid": "rgba(15,23,42,0.08)",
        "zero": "rgba(15,23,42,0.12)",
        "line": "rgba(15,23,42,0.14)",
        "hover_bg": "rgba(255,255,255,0.97)",
        "hover_text": "#0F172A",
    },
}


def register_plotly_theme(mode: str = "dark") -> None:
    """Register (if needed) and activate the HireIQ Plotly template for ``mode``.

    Args:
        mode: ``"dark"`` or ``"light"``. Unknown values fall back to dark.
    """
    resolved = mode if mode in _MODE_COLORS else "dark"
    template_name = f"hireiq_{resolved}"

    if template_name not in pio.templates:
        pio.templates[template_name] = _build_template(_MODE_COLORS[resolved])

    pio.templates.default = template_name


def _build_template(colors: dict[str, str]) -> go.layout.Template:
    """Construct a Plotly template from a set of mode colors."""
    axis = dict(
        gridcolor=colors["grid"],
        zerolinecolor=colors["zero"],
        linecolor=colors["line"],
        tickcolor=colors["line"],
        tickfont=dict(color=colors["muted"], size=12),
        title=dict(font=dict(color=colors["text"], size=13)),
    )
    return go.layout.Template(
        layout=go.Layout(
            font=dict(family=THEME.font_family, color=colors["text"], size=13),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=COLORWAY,
            margin=dict(l=10, r=10, t=30, b=10),
            hoverlabel=dict(
                bgcolor=colors["hover_bg"],
                bordercolor="rgba(124,58,237,0.5)",
                font=dict(color=colors["hover_text"], family=THEME.font_family, size=13),
            ),
            xaxis=axis,
            yaxis=axis,
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=colors["text"], size=12),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                x=0,
            ),
            transition=dict(duration=500, easing="cubic-in-out"),
        )
    )
