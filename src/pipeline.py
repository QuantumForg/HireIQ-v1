"""HireIQ V1 — main pipeline orchestrator.

Runs feature engineering, scoring, submission generation, and report
generation in sequence. Scoring is computed exactly once and passed to both
the submission and report generators.
"""

import logging
import time
from pathlib import Path

from src.build_features import build_features
from src.generate_submission import generate_submission
from src.reporting.generate_report import generate_report
from src.scoring.rank_candidates import rank_candidates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("hireiq.pipeline")

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
FEATURES_FILE = OUTPUT_DIR / "features.csv"
SUBMISSION_FILE = OUTPUT_DIR / "submission.csv"
REPORT_FILE = OUTPUT_DIR / "ranking_report.txt"


def banner():
    print()
    print("=" * 100)
    print("HIREIQ V1")
    print("REDROB AI HACKATHON PIPELINE")
    print("=" * 100)


def validate_artifacts():
    checks = [
        FEATURES_FILE,
        SUBMISSION_FILE,
        REPORT_FILE,
        OUTPUT_DIR / "top100.csv",
        OUTPUT_DIR / "title_distribution.csv",
    ]

    print()
    print("[VALIDATION]")

    for file in checks:
        if file.exists():
            size_bytes = file.stat().st_size
            if size_bytes >= 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{size_bytes / 1024:.2f} KB"
            
            logger.info("Artifact OK: %s (%s)", file.name, size_str)
            print(f"✓ {file.name:<23}{size_str:>8}")
        else:
            raise FileNotFoundError(f"Missing artifact: {file}")


def run_pipeline():
    start = time.time()

    banner()

    print()
    print("[1/5] Feature Engineering")
    processed = build_features()

    print()
    print("[2/5] Scoring & Ranking")
    ranked = rank_candidates()
    logger.info("Ranked %d candidates (score range: %.2f to %.2f)",
                len(ranked), ranked["final_score"].min(), ranked["final_score"].max())

    print()
    print("[3/5] Submission Generation")
    submission = generate_submission(ranked)

    print()
    print("[4/5] Report Generation")
    generate_report(ranked)

    print()
    print("[5/5] Artifact Validation")
    validate_artifacts()

    runtime = time.time() - start

    print()
    print("==========================================================")
    print("PIPELINE SUCCESSFULLY COMPLETED")
    print("===============================")
    print()
    print("==========================================================")
    print("EXECUTION SUMMARY")
    print("=================")
    print()
    print(f"Candidates Processed : {processed:,}")
    print(f"Candidates Ranked    : {len(ranked):,}")
    print(f"Top Candidates       : {len(submission)}")
    print(f"Reports Generated    : 3")
    print(f"Validation           : PASSED")
    print(f"Pipeline Status      : SUCCESS")
    print(f"Runtime              : {runtime:.2f} sec")
    print()
    print("==========================================================")

    print()
    print("Generated Artifacts")
    print()
    print(f"• {FEATURES_FILE.relative_to(BASE_DIR).as_posix()}")
    print(f"• {SUBMISSION_FILE.relative_to(BASE_DIR).as_posix()}")
    print(f"• {REPORT_FILE.relative_to(BASE_DIR).as_posix()}")
    print(f"• {(OUTPUT_DIR / 'top100.csv').relative_to(BASE_DIR).as_posix()}")
    print(f"• {(OUTPUT_DIR / 'title_distribution.csv').relative_to(BASE_DIR).as_posix()}")


if __name__ == "__main__":
    run_pipeline()
