"""Generate the final ranked submission CSV.

Produces ``submission.csv`` with per-candidate reasoning derived from their
feature breakdown. Accepts a pre-ranked DataFrame to avoid recomputing scores.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger("hireiq.pipeline")

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

SUBMISSION_FILE = OUTPUT_DIR / "submission.csv"


def _build_reasoning(row: pd.Series) -> str:
    """Generate a human-readable reasoning string for a single candidate.

    Derives the explanation from the candidate's feature values so each row
    has a unique, informative description.
    """
    title = row.get("current_title", "Unknown")
    exp = row.get("years_of_experience", 0)
    retrieval = row.get("retrieval_score", 0)
    ranking = row.get("ranking_score", 0)
    production = row.get("production_ai_score", 0)
    ai_title = row.get("ai_title_score", 0)
    career = row.get("career_validation_score", 0)

    parts = [f"{title} with {exp}yr exp"]

    if retrieval > 0:
        parts.append(f"retrieval={retrieval}")
    if ranking > 0:
        parts.append(f"ranking={ranking}")
    if production > 0:
        parts.append(f"production_ai={production}")
    if ai_title > 0:
        parts.append("AI-titled role")
    if career > 0:
        parts.append(f"career_quality={career}")

    return " | ".join(parts)


def generate_submission(ranked: pd.DataFrame | None = None) -> pd.DataFrame:
    """Generate the submission CSV from a pre-ranked DataFrame.

    Args:
        ranked: A sorted DataFrame with candidate features and ``final_score``.
                If ``None``, scores are computed fresh via ``rank_candidates()``.

    Returns:
        The submission DataFrame (100 rows).
    """
    if ranked is None:
        from src.scoring.rank_candidates import rank_candidates
        ranked = rank_candidates()

    top100 = ranked.head(100).copy()
    top100 = top100.reset_index(drop=True)

    reasonings = [_build_reasoning(row) for _, row in top100.iterrows()]

    submission = pd.DataFrame({
        "candidate_id": top100["candidate_id"],
        "rank": range(1, len(top100) + 1),
        "score": top100["final_score"].round(4),
        "reasoning": reasonings,
    })

    submission.to_csv(SUBMISSION_FILE, index=False)

    logger.info("Submission generated: %s (%d rows)", SUBMISSION_FILE.relative_to(BASE_DIR).as_posix(), len(submission))
    return submission


if __name__ == "__main__":
    generate_submission()
