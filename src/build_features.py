"""Feature engineering: transforms raw candidate JSONL into a feature CSV.

Streams rows to the output file incrementally to avoid holding the full
dataset in memory. Only the first record is buffered to determine the
column schema.
"""

import json
import csv
import logging
from pathlib import Path

from src.feature_engineering.skill_taxonomy import skill_profile
from src.feature_engineering.career_features import career_profile
from src.feature_engineering.behavioral_features import behavioral_profile
from src.feature_engineering.ai_signals import ai_signal_profile
from src.scoring.career_validation import career_validation_score

logger = logging.getLogger("hireiq.pipeline")

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "candidates.jsonl"
OUTPUT_FILE = BASE_DIR / "outputs" / "features.csv"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def flatten_candidate(candidate):
    """Transform a raw candidate dict into a flat feature row."""
    row = {}

    row["candidate_id"] = candidate["candidate_id"]

    profile = candidate.get("profile", {})

    row["current_title"] = profile.get("current_title", "")
    row["years_of_experience"] = profile.get("years_of_experience", 0)

    row.update(skill_profile(candidate))
    row.update(career_profile(candidate))
    row.update(behavioral_profile(candidate))
    row.update(ai_signal_profile(candidate))

    row["career_validation_score"] = career_validation_score(candidate)

    return row


def build_features():
    """Read candidates from JSONL and stream features to CSV."""
    total = 0
    malformed = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line:
            first_candidate = json.loads(first_line)
            fieldnames = list(flatten_candidate(first_candidate).keys())

            with open(
                OUTPUT_FILE, "w", newline="", encoding="utf-8"
            ) as out:
                writer = csv.DictWriter(out, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(flatten_candidate(first_candidate))
                total = 1

                for idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        candidate = json.loads(line)
                        writer.writerow(flatten_candidate(candidate))
                        total += 1
                    except (json.JSONDecodeError, KeyError, TypeError) as exc:
                        malformed += 1
                        logger.warning("Skipping malformed record at line %d: %s", idx + 2, exc)

                    if total % 10000 == 0:
                        logger.info("Processed %d candidates...", total)
                        print(f"Processed {total:,}")

    if malformed > 0:
        logger.warning("%d malformed records skipped", malformed)

    print()
    print(f"Saved {total:,} candidates ({malformed} malformed skipped)")
    print(f"Output -> {OUTPUT_FILE.relative_to(BASE_DIR).as_posix()}")
    return total


if __name__ == "__main__":
    build_features()
