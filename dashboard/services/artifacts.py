"""Discovery of downloadable artifacts in the outputs directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from dashboard import config
from dashboard.utils import file_extension, format_bytes, format_relative_time

_MIME_BY_EXTENSION: dict[str, str] = {
    "csv": "text/csv",
    "txt": "text/plain",
    "json": "application/json",
    "yaml": "application/x-yaml",
    "yml": "application/x-yaml",
}


@dataclass(frozen=True)
class Artifact:
    """Metadata describing a single output file."""

    name: str
    path: Path
    extension: str
    size_bytes: int
    modified: float

    @property
    def size_label(self) -> str:
        return format_bytes(self.size_bytes)

    @property
    def modified_label(self) -> str:
        return format_relative_time(self.modified)

    @property
    def mime(self) -> str:
        return _MIME_BY_EXTENSION.get(self.extension, "application/octet-stream")


def discover_artifacts() -> list[Artifact]:
    """Scan the outputs directory and return artifact metadata.

    Returns:
        Artifacts sorted by most-recently modified. Empty if the directory is
        absent.
    """
    return _discover_cached(str(config.OUTPUTS_DIR), _directory_signature())


def _directory_signature() -> tuple[tuple[str, float, int], ...]:
    """Return a cache signature reflecting the directory's current contents."""
    if not config.OUTPUTS_DIR.exists():
        return ()
    entries = []
    for path in sorted(config.OUTPUTS_DIR.iterdir()):
        if path.is_file():
            stat = path.stat()
            entries.append((path.name, stat.st_mtime, stat.st_size))
    return tuple(entries)


@st.cache_data(show_spinner=False)
def _discover_cached(
    directory_str: str,
    _signature: tuple[tuple[str, float, int], ...],
) -> list[Artifact]:
    """Cached directory scan keyed on the directory signature."""
    directory = Path(directory_str)
    if not directory.exists():
        return []

    artifacts: list[Artifact] = []
    for path in directory.iterdir():
        if not path.is_file():
            continue
        stat = path.stat()
        artifacts.append(
            Artifact(
                name=path.name,
                path=path,
                extension=file_extension(path),
                size_bytes=stat.st_size,
                modified=stat.st_mtime,
            )
        )

    artifacts.sort(key=lambda item: item.modified, reverse=True)
    return artifacts
