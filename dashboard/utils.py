"""Pure formatting and helper utilities with no Streamlit dependencies."""

from __future__ import annotations

import base64
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("hireiq.dashboard")


def format_bytes(num_bytes: int) -> str:
    """Render a byte count as a human-readable string.

    Args:
        num_bytes: Size in bytes.

    Returns:
        A compact string such as ``"1.20 MB"`` or ``"512 B"``.
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    size = float(num_bytes)
    for unit in ("KB", "MB", "GB", "TB"):
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.2f} {unit}"
    return f"{size:.2f} PB"


def format_relative_time(timestamp: float, *, now: datetime | None = None) -> str:
    """Convert a POSIX timestamp into a human-readable relative time.

    Args:
        timestamp: POSIX modification time.
        now: Reference time, primarily for testing. Defaults to ``datetime.now``.

    Returns:
        A phrase such as ``"2 minutes ago"`` or ``"Yesterday"``.
    """
    reference = now or datetime.now()
    delta_seconds = (reference - datetime.fromtimestamp(timestamp)).total_seconds()

    if delta_seconds < 0:
        return "just now"
    if delta_seconds < 60:
        return "just now"

    minutes = delta_seconds / 60
    if minutes < 60:
        value = int(minutes)
        return f"{value} minute{_plural(value)} ago"

    hours = minutes / 60
    if hours < 24:
        value = int(hours)
        return f"{value} hour{_plural(value)} ago"

    days = hours / 24
    if days < 2:
        return "Yesterday"
    if days < 30:
        value = int(days)
        return f"{value} days ago"

    return datetime.fromtimestamp(timestamp).strftime("%b %d, %Y")


def _plural(value: int) -> str:
    """Return an ``"s"`` suffix for non-singular counts."""
    return "" if value == 1 else "s"


def file_extension(path: Path) -> str:
    """Return a lowercase file extension without the leading dot."""
    return path.suffix.lower().lstrip(".")


def compact_number(value: float) -> str:
    """Format a number compactly with thousands separators.

    Integers are rendered without decimals; floats keep two decimals.
    """
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.2f}"
    return f"{int(value):,}"


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a ``#RRGGBB`` color into an ``rgba(...)`` string.

    Args:
        hex_color: A hex color, with or without a leading ``#``.
        alpha: Opacity in the range ``0.0``–``1.0``.

    Returns:
        A CSS ``rgba(r, g, b, a)`` string. Falls back to a neutral purple tint
        if the input cannot be parsed.
    """
    cleaned = hex_color.lstrip("#")
    if len(cleaned) != 6:
        return f"rgba(124, 58, 237, {alpha})"
    try:
        red, green, blue = (int(cleaned[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return f"rgba(124, 58, 237, {alpha})"
    return f"rgba({red}, {green}, {blue}, {alpha})"


def image_data_uri(path: Path) -> str | None:
    """Return a base64 ``data:`` URI for an image file, or ``None`` if missing.

    Args:
        path: Path to the image file.

    Returns:
        A data URI suitable for embedding in an ``<img src>`` attribute, or
        ``None`` when the file does not exist or cannot be read.
    """
    if not path.exists():
        return None
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(file_extension(path), "image/png")
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return None
    return f"data:{mime};base64,{encoded}"
