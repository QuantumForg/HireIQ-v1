"""Submission validation status resolution.

Validation status is resolved with the following precedence:

1. If ``outputs/validation_result.txt`` exists, its contents are trusted.
2. Otherwise the official validator (``data/validate_submission.py``) is
   imported and executed in-memory against ``submission.csv``. The validator
   only reads the file, so this is a safe, read-only operation.
3. If neither path can produce a result, the status is reported as unknown
   rather than fabricated.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st

from dashboard import config
from dashboard.utils import logger

_VALID_MARKER = "submission is valid"


@dataclass(frozen=True)
class ValidationStatus:
    """Resolved validation outcome.

    Attributes:
        state: One of ``"valid"``, ``"failed"``, or ``"unknown"``.
        issues: Human-readable issues when validation failed.
        source: Where the status came from (file or live validator).
    """

    state: str
    issues: list[str] = field(default_factory=list)
    source: str = "unknown"

    @property
    def is_valid(self) -> bool:
        return self.state == "valid"

    @property
    def is_failed(self) -> bool:
        return self.state == "failed"


def resolve_validation() -> ValidationStatus:
    """Resolve the current submission validation status."""
    submission_path = config.OUTPUTS_DIR / config.SUBMISSION_FILE
    result_path = config.OUTPUTS_DIR / config.VALIDATION_RESULT_FILE
    return _resolve_cached(
        str(submission_path),
        _mtime(submission_path),
        str(result_path),
        _mtime(result_path),
    )


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return -1.0


@st.cache_data(show_spinner=False)
def _resolve_cached(
    submission_str: str,
    _submission_sig: float,
    result_str: str,
    _result_sig: float,
) -> ValidationStatus:
    """Cached resolution keyed on submission and result-file timestamps."""
    result_path = Path(result_str)
    if result_path.exists():
        status = _read_result_file(result_path)
        if status is not None:
            return status

    return _run_official_validator(Path(submission_str))


def _read_result_file(path: Path) -> ValidationStatus | None:
    """Interpret an existing validation result file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if _VALID_MARKER in text.lower():
        return ValidationStatus("valid", source="validation_result.txt")

    issues = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return ValidationStatus("failed", issues=issues, source="validation_result.txt")


def _run_official_validator(submission_path: Path) -> ValidationStatus:
    """Execute the official validator in-memory against the submission."""
    if not submission_path.exists():
        return ValidationStatus("unknown", source="missing submission")

    validate = _load_validator()
    if validate is None:
        return ValidationStatus("unknown", source="validator unavailable")

    try:
        errors = validate(str(submission_path))
    except Exception as exc:  # noqa: BLE001 - surface as a neutral status, never crash
        logger.warning("Validator raised: %s", exc)
        return ValidationStatus("unknown", source="validator error")

    if errors:
        return ValidationStatus("failed", issues=list(errors), source="official validator")
    return ValidationStatus("valid", source="official validator")


def _load_validator():
    """Dynamically import ``validate_submission`` from the data directory.

    Returns:
        The ``validate_submission`` callable, or ``None`` if it cannot be loaded.
    """
    if not config.VALIDATOR_PATH.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            "hireiq_validator", config.VALIDATOR_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "validate_submission", None)
    except Exception as exc:  # noqa: BLE001 - never let import issues crash the UI
        logger.warning("Could not load validator: %s", exc)
        return None
