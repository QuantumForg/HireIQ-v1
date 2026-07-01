import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FEATURES_FILE = BASE_DIR / "outputs" / "features.csv"


def compute_score(df):
    return (
        df["retrieval_score"] * 25
        + df["ranking_score"] * 25
        + df["search_system_score"] * 25
        + df["retrieval_depth_score"] * 20
        + df["embedding_score"] * 18
        + df["production_ai_score"] * 25
        + df["production_ml_score"] * 20
        + df["career_validation_score"] * 2.0
        + df["recommendation_bonus"] * 20
        + df["product_company_score"] * 12
        + df["total_ai_skill_score"] * 0.5
        + df["response_score"] * 1.0
        + df["activity_score"] * 1.0
        + df["profile_score"] * 0.5
        + df["open_to_work_score"] * 12
        + df["verification_score"] * 5
        + df["response_speed_score"] * 2
        - df["consulting_penalty"] * 40
        - df["research_penalty"] * 40
        - df["framework_tourist_penalty"] * 20
        - df["fake_ai_penalty"] * 30
        - df["non_ai_title_penalty"] * 50
        - df["cv_penalty"] * 40
        - df["speech_penalty"] * 40
        - df["job_hop_score"] * 10
        - df["notice_penalty"] * 5
    )


def experience_fit(exp):
    if 5 <= exp <= 9:
        return 75
    if 4 <= exp < 5:
        return 25
    if 9 < exp <= 11:
        return 10
    if 11 < exp <= 13:
        return -100
    return -250


def jd_alignment_bonus(title):
    """
    JD-based title alignment bonus/penalty.

    JD explicitly says:
      - Pure research without production deployment → not moving forward
      - Computer Vision without NLP/IR exposure → not preferred
      - Recommendation/Search/Applied ML → strong fit
    """
    if title == "Recommendation Systems Engineer":
        return 75
    if title == "Search Engineer":
        return 60
    if title == "Applied ML Engineer":
        return 40
    if title == "AI Research Engineer":
        return -20
    if title == "Computer Vision Engineer":
        return -40
    return 0


def rank_candidates():
    df = pd.read_csv(FEATURES_FILE)

    df = df[
        (df["years_of_experience"] >= 4)
        & (df["years_of_experience"] <= 13)
    ].copy()

    df["experience_fit"] = (
        df["years_of_experience"]
        .apply(experience_fit)
    )

    df["jd_alignment_bonus"] = (
        df["current_title"]
        .apply(jd_alignment_bonus)
    )

    df["final_score"] = (
        compute_score(df)
        + df["experience_fit"]
        + df["jd_alignment_bonus"]
    )

    df = df.sort_values(
        by=[
            "final_score",
            "candidate_id"
        ],
        ascending=[
            False,
            True
       ]
    )

    return df


if __name__ == "__main__":
    ranked = rank_candidates()

    print("\nTOP 30\n")
    print(
        ranked[
            [
                "candidate_id",
                "current_title",
                "years_of_experience",
                "final_score",
                "jd_alignment_bonus",
            ]
        ].head(30)
    )

    print("\nTITLE DISTRIBUTION IN TOP 100\n")
    print(
        ranked.head(100)["current_title"]
        .value_counts()
        .head(15)
    )