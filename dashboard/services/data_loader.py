"""Cached, fault-tolerant loaders for pipeline output files.

Every loader returns a :class:`LoadResult` so the UI can render premium empty
or error states instead of crashing. Loading is cached on the file's
modification time so edits to outputs are picked up without a manual restart.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard import config
from dashboard.utils import logger


@dataclass(frozen=True)
class LoadResult:
    """Outcome of attempting to load a file.

    Attributes:
        ok: Whether usable data was produced.
        data: The loaded object (``DataFrame`` or ``str``) when ``ok`` is True.
        error: A human-readable explanation when ``ok`` is False.
        path: The resolved path that was targeted.
    """

    ok: bool
    data: object | None
    error: str | None
    path: Path


def _signature(path: Path) -> float:
    """Return the modification time used as a cache key, or ``-1`` if missing."""
    try:
        return path.stat().st_mtime
    except OSError:
        return -1.0


def load_csv(filename: str, required_columns: tuple[str, ...] = ()) -> LoadResult:
    """Load a CSV from the outputs directory with validation.

    Args:
        filename: Name of the file within ``outputs/``.
        required_columns: Columns that must be present for the file to be valid.

    Returns:
        A :class:`LoadResult` describing success or the precise failure reason.
    """
    path = config.OUTPUTS_DIR / filename
    return _load_csv_cached(str(path), _signature(path), required_columns)


@st.cache_data(show_spinner=False)
def _load_csv_cached(
    path_str: str,
    _signature_value: float,
    required_columns: tuple[str, ...],
) -> LoadResult:
    """Cached CSV reader keyed on path and modification time."""
    path = Path(path_str)

    if not path.exists():
        logger.info("CSV missing: %s", path.name)
        return LoadResult(False, None, f"{path.name} was not found.", path)

    try:
        frame = pd.read_csv(path)
    except UnicodeDecodeError:
        return LoadResult(False, None, f"{path.name} is not valid UTF-8.", path)
    except pd.errors.EmptyDataError:
        return LoadResult(False, None, f"{path.name} is empty.", path)
    except (OSError, pd.errors.ParserError) as exc:
        return LoadResult(False, None, f"Could not parse {path.name}: {exc}", path)

    frame.columns = [str(col).strip() for col in frame.columns]

    if frame.empty:
        return LoadResult(False, None, f"{path.name} contains no rows.", path)

    missing = [col for col in required_columns if col not in frame.columns]
    if missing:
        joined = ", ".join(missing)
        return LoadResult(False, None, f"{path.name} is missing column(s): {joined}.", path)

    logger.info("Loaded CSV %s (%d rows)", path.name, len(frame))
    return LoadResult(True, frame, None, path)


def load_text(filename: str) -> LoadResult:
    """Load a UTF-8 text file from the outputs directory."""
    path = config.OUTPUTS_DIR / filename
    return _load_text_cached(str(path), _signature(path))


@st.cache_data(show_spinner=False)
def _load_text_cached(path_str: str, _signature_value: float) -> LoadResult:
    """Cached text reader keyed on path and modification time."""
    path = Path(path_str)

    if not path.exists():
        return LoadResult(False, None, f"{path.name} was not found.", path)

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return LoadResult(False, None, f"{path.name} is not valid UTF-8.", path)
    except OSError as exc:
        return LoadResult(False, None, f"Could not read {path.name}: {exc}", path)

    logger.info("Loaded text %s (%d chars)", path.name, len(content))
    return LoadResult(True, content, None, path)


def features_summary() -> LoadResult:
    """Summarize ``features.csv`` without materializing the full dataframe.

    The features file can contain hundreds of thousands of rows, so only
    lightweight metadata (row/column counts, memory, missing values) is
    computed and cached.

    Returns:
        A :class:`LoadResult` whose ``data`` is a dict of summary statistics.
    """
    path = config.OUTPUTS_DIR / config.FEATURES_FILE
    return _features_summary_cached(str(path), _signature(path))


@st.cache_data(show_spinner=False)
def _features_summary_cached(path_str: str, _signature_value: float) -> LoadResult:
    """Cached summary computation for the features file utilizing chunked loading."""
    path = Path(path_str)

    if not path.exists():
        return LoadResult(False, None, f"{path.name} was not found.", path)

    try:
        chunksize = 10000
        reader = pd.read_csv(path, chunksize=chunksize)
        
        total_rows = 0
        total_missing = 0
        total_memory = 0
        column_names = None
        numeric_columns_set = set()
        
        for chunk in reader:
            if column_names is None:
                column_names = list(chunk.columns)
                for col in chunk.columns:
                    if pd.api.types.is_numeric_dtype(chunk[col]):
                        numeric_columns_set.add(col)
            
            total_rows += len(chunk)
            total_missing += int(chunk.isna().sum().sum())
            total_memory += int(chunk.memory_usage(deep=True).sum())
            
        summary = {
            "rows": total_rows,
            "columns": len(column_names) if column_names else 0,
            "numeric_columns": len(numeric_columns_set),
            "missing_values": total_missing,
            "memory_bytes": total_memory,
            "column_names": column_names if column_names else [],
        }
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        return LoadResult(False, None, f"Could not read {path.name}: {exc}", path)

    return LoadResult(True, summary, None, path)
