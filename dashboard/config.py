"""Central configuration: paths, theme tokens, and constants.

This module is the single source of truth for every visual and structural
constant used across the dashboard. No colors, paths, sizes, or filenames
should be hardcoded anywhere else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
DATA_DIR: Path = PROJECT_ROOT / "data"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
VALIDATOR_PATH: Path = DATA_DIR / "validate_submission.py"
LOGO_PATH: Path = ASSETS_DIR / "logo.png"

# --------------------------------------------------------------------------- #
# Known output artifacts
# --------------------------------------------------------------------------- #

SUBMISSION_FILE: str = "submission.csv"
TOP100_FILE: str = "top100.csv"
FEATURES_FILE: str = "features.csv"
RANKING_REPORT_FILE: str = "ranking_report.txt"
TITLE_DISTRIBUTION_FILE: str = "title_distribution.csv"
VALIDATION_RESULT_FILE: str = "validation_result.txt"

SUBMISSION_REQUIRED_COLUMNS: tuple[str, ...] = (
    "candidate_id",
    "rank",
    "score",
    "reasoning",
)


# --------------------------------------------------------------------------- #
# Application metadata
# --------------------------------------------------------------------------- #

APP_NAME: str = "HireIQ V1"
APP_TAGLINE: str = "AI-Powered Candidate Ranking System"
APP_VERSION: str = "1.0.0"
HACKATHON: str = "Redrob AI Hackathon"
GITHUB_URL: str = "https://github.com"


# --------------------------------------------------------------------------- #
# Theme tokens
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Palette:
    """Color tokens for the dark enterprise theme."""

    bg: str = "#09090B"
    bg_secondary: str = "#111827"
    card: str = "rgba(20, 20, 25, 0.75)"
    text: str = "#FFFFFF"
    text_secondary: str = "#B4B7C5"
    text_muted: str = "#7D8597"
    border: str = "rgba(255, 255, 255, 0.08)"
    border_glass: str = "rgba(255, 255, 255, 0.12)"

    success: str = "#22C55E"
    warning: str = "#FACC15"
    danger: str = "#EF4444"
    info: str = "#3B82F6"

    purple: str = "#7C3AED"
    pink: str = "#EC4899"
    orange: str = "#FB923C"
    blue: str = "#3B82F6"
    cyan: str = "#06B6D4"


@dataclass(frozen=True)
class Gradients:
    """Reusable gradient definitions."""

    hero: str = "linear-gradient(135deg, #7C3AED 0%, #EC4899 50%, #FB923C 100%)"
    metric: str = "linear-gradient(135deg, #3B82F6 0%, #7C3AED 100%)"
    button: str = "linear-gradient(135deg, #7C3AED 0%, #FB923C 100%)"


@dataclass(frozen=True)
class Radius:
    card: str = "24px"
    button: str = "16px"
    input: str = "16px"
    chart: str = "24px"
    table: str = "20px"
    sidebar: str = "28px"


@dataclass(frozen=True)
class Theme:
    """Aggregate theme exposed to the rest of the application."""

    palette: Palette = field(default_factory=Palette)
    gradients: Gradients = field(default_factory=Gradients)
    radius: Radius = field(default_factory=Radius)
    font_family: str = (
        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    )


THEME: Theme = Theme()


# --------------------------------------------------------------------------- #
# Navigation
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class NavItem:
    """A single sidebar navigation entry."""

    key: str
    label: str
    icon: str  # Material Symbols icon name (rendered via Streamlit's icon API)


NAVIGATION: tuple[NavItem, ...] = (
    NavItem("overview", "Overview", "space_dashboard"),
    NavItem("analytics", "Analytics", "monitoring"),
    NavItem("leaderboard", "Leaderboard", "leaderboard"),
    NavItem("explain", "Explainability", "lightbulb"),
    NavItem("reports", "Reports", "description"),
    NavItem("validation", "Validation", "verified"),
    NavItem("artifacts", "Artifacts", "inventory_2"),
    NavItem("about", "About", "info"),
)
