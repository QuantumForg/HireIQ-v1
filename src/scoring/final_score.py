# ============================================================
# HireIQ v2 — Final Composite Scorer
# ============================================================

from src.utils.constants import WEIGHTS

def compute_final_score(features: dict) -> dict:
    """
    Combines all feature scores into final composite score (0-1)
    """

    # ── Hard Disqualifiers ─────────────────────────────────
    if features.get("is_noise", False):
        return {
            "final_score": 0.0,
            "disqualified": True,
            "disqualify_reason": "noise_summary"
        }

    # ── Base Scores ────────────────────────────────────────
    title_score    = features.get("title_score", 0.0)
    skill_score    = features.get("skill_score", 0.0)
    exp_score      = features.get("exp_score", 0.0)
    career_score   = features.get("career_score", 0.0)
    edu_score      = features.get("edu_score", 0.0)
    behavioral     = features.get("behavioral_score", 0.0)
    tier1_weighted = features.get("tier1_weighted", 0.0)
    tier2_weighted = features.get("tier2_weighted", 0.0)

    # ── Non-AI Title Penalty ───────────────────────────────
    # Non-AI titles get heavy penalty — JD needs real AI engineers
    if not features.get("is_ai_title", False):
        title_score = title_score * 0.1
        skill_score = skill_score * 0.5

    # ── Weighted Composite ─────────────────────────────────
    composite = (
        title_score  * WEIGHTS["ai_title"]      +
        skill_score  * WEIGHTS["tier1_skills"]  +
        tier2_weighted * WEIGHTS["tier2_skills"] +
        exp_score    * WEIGHTS["experience"]    +
        behavioral   * WEIGHTS["behavioral"]    +
        edu_score    * WEIGHTS["education"]     +
        career_score * WEIGHTS["career_quality"]
    )

    # ── Bonus Multipliers ──────────────────────────────────

    # Tier1 skills bonus — if candidate has 7+ tier1 skills
    tier1_count = features.get("tier1_count", 0)
    if tier1_count >= 7:
        composite *= 1.15
    elif tier1_count >= 5:
        composite *= 1.08
    elif tier1_count >= 3:
        composite *= 1.03

    # GitHub activity bonus
    # (already in behavioral, small extra boost for high github)

    # ── Cap at 1.0 ─────────────────────────────────────────
    composite = round(min(1.0, max(0.0, composite)), 6)

    return {
        "final_score": composite,
        "disqualified": False,
        "disqualify_reason": None,
        "score_breakdown": {
            "title":    round(title_score * WEIGHTS["ai_title"], 4),
            "skills":   round(skill_score * WEIGHTS["tier1_skills"], 4),
            "tier2":    round(tier2_weighted * WEIGHTS["tier2_skills"], 4),
            "exp":      round(exp_score * WEIGHTS["experience"], 4),
            "behavior": round(behavioral * WEIGHTS["behavioral"], 4),
            "edu":      round(edu_score * WEIGHTS["education"], 4),
            "career":   round(career_score * WEIGHTS["career_quality"], 4),
        }
    }


if __name__ == "__main__":
    # Test with strong AI candidate
    strong = {
        "is_noise": False,
        "is_ai_title": True,
        "title_score": 1.0,
        "skill_score": 0.85,
        "tier1_weighted": 0.9,
        "tier2_weighted": 0.7,
        "tier1_count": 8,
        "tier2_count": 5,
        "exp_score": 1.0,
        "career_score": 0.9,
        "edu_score": 1.0,
        "behavioral_score": 0.85,
    }

    # Weak non-AI candidate
    weak = {
        "is_noise": False,
        "is_ai_title": False,
        "title_score": 0.0,
        "skill_score": 0.3,
        "tier1_weighted": 0.1,
        "tier2_weighted": 0.05,
        "tier1_count": 1,
        "tier2_count": 0,
        "exp_score": 0.5,
        "career_score": 0.2,
        "edu_score": 0.5,
        "behavioral_score": 0.4,
    }

    # Noise candidate
    noise = {
        "is_noise": True,
        "is_ai_title": False,
        "title_score": 0.0,
        "skill_score": 0.8,  # Keyword stuffer
        "tier1_count": 10,
        "behavioral_score": 0.6,
    }

    print("=== FINAL SCORE TEST ===\n")

    result = compute_final_score(strong)
    print(f"Strong AI Candidate: {result['final_score']}")
    print(f"  Breakdown: {result['score_breakdown']}")

    result = compute_final_score(weak)
    print(f"\nWeak Non-AI Candidate: {result['final_score']}")
    print(f"  Breakdown: {result['score_breakdown']}")

    result = compute_final_score(noise)
    print(f"\nNoise Candidate: {result['final_score']}")
    print(f"  Disqualified: {result['disqualified']} — {result['disqualify_reason']}")