"""Dataset loading and JSON persistence utilities."""

import gzip
import json
import logging
import os

from src.utils.constants import DATA_PATH

logger = logging.getLogger("hireiq.io")

# Optional: gzipped fallback path (e.g. "data/candidates.jsonl.gz").
GZ_PATH = f"{DATA_PATH}.gz"


def load_candidates(path=None):
    """Load candidates from a JSONL file, transparently handling ``.gz``.

    Malformed lines are logged and skipped rather than silently dropped.
    """
    if path is None:
        path = DATA_PATH

    candidates = []
    gz_path = f"{path}.gz"

    if os.path.exists(path):
        opener = open(path, "r", encoding="utf-8")
    elif os.path.exists(gz_path):
        opener = gzip.open(gz_path, "rt", encoding="utf-8")
    else:
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info("Loading candidates from %s", path)
    skipped = 0
    with opener as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError as exc:
                skipped += 1
                logger.warning("Skipping malformed line %d: %s", i + 1, exc)
            if (i + 1) % 20000 == 0:
                logger.info("  %d loaded...", i + 1)

    if skipped:
        logger.warning("Skipped %d malformed lines while loading %s", skipped, path)
    logger.info("Total loaded: %d", len(candidates))
    return candidates


def save_json(data, path):
    """Persist ``data`` as pretty-printed JSON, creating parent dirs."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved: %s", path)


def load_json(path):
    """Load and return JSON from ``path``."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
