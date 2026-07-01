"""Generate ranking reports and supplementary CSV artifacts.

Produces ``ranking_report.txt``, ``top100.csv``, and ``title_distribution.csv``.
Accepts a pre-ranked DataFrame to avoid recomputing scores.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger("hireiq.pipeline")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

REPORT_FILE = OUTPUT_DIR / "ranking_report.txt"
TOP100_FILE = OUTPUT_DIR / "top100.csv"
TITLE_FILE = OUTPUT_DIR / "title_distribution.csv"


def generate_report(ranked: pd.DataFrame | None = None) -> None:
    """Generate all report artifacts from a pre-ranked DataFrame.

    Args:
        ranked: A sorted DataFrame with candidate features and ``final_score``.
                If ``None``, scores are computed fresh via ``rank_candidates()``.
    """
    if ranked is None:
        from src.scoring.rank_candidates import rank_candidates
        ranked = rank_candidates()

    top100 = ranked.head(100).copy()

    top100.to_csv(TOP100_FILE, index=False)
    logger.info("Saved %s (%d rows)", TOP100_FILE.relative_to(BASE_DIR).as_posix(), len(top100))

    title_dist = (
        top100["current_title"]
        .value_counts()
        .reset_index()
    )
    title_dist.columns = ["title", "count"]
    title_dist.to_csv(TITLE_FILE, index=False)
    logger.info("Saved %s", TITLE_FILE.relative_to(BASE_DIR).as_posix())

    exp_stats = top100["years_of_experience"].describe()

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("HIREIQ V1 RANKING REPORT\n")
        f.write("=" * 60)
        f.write("\n\n")

        f.write("TOP100 EXPERIENCE\n")
        f.write(str(exp_stats))
        f.write("\n\n")

        f.write("TITLE DISTRIBUTION\n")
        f.write(title_dist.to_string(index=False))
        f.write("\n\n")

        f.write("TOP 20 CANDIDATES\n")
        f.write(
            top100[
                [
                    "candidate_id",
                    "current_title",
                    "years_of_experience",
                    "final_score",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

    logger.info("Saved %s", REPORT_FILE.relative_to(BASE_DIR).as_posix())


if __name__ == "__main__":
    generate_report()
