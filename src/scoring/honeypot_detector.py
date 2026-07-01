# ============================================================
# HireIQ v2 — Honeypot Detector
# ============================================================

def detect_honeypot(candidate) -> tuple[bool, list[str]]:
    """
    Returns (is_honeypot, reasons)
    """
    reasons = []
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])
    exp = profile["years_of_experience"]

    # ── Rule 1: Salary min > max ───────────────────────────
    salary = signals.get("expected_salary_range_inr_lpa", {})
    sal_min = salary.get("min", 0)
    sal_max = salary.get("max", 0)
    if sal_max > 0 and sal_min > sal_max:
        reasons.append(f"salary_inverted: min={sal_min} > max={sal_max}")

    # ── Rule 2: Job duration > total experience ────────────
    for job in career:
        duration = job.get("duration_months", 0)
        if duration > (exp * 12) + 6:
            reasons.append(
                f"impossible_duration: {job['company']} "
                f"{duration}mo > exp {exp}yr"
            )

    # ── Rule 3: Expert in many skills, near-zero endorsements
    expert_skills = [s for s in skills
                    if s.get("proficiency") in ["expert", "advanced"]
                    and s.get("endorsements", 0) == 0]
    if len(expert_skills) >= 6:
        reasons.append(
            f"expert_no_endorse: {len(expert_skills)} "
            f"advanced/expert skills with 0 endorsements"
        )

    # ── Rule 4: Profile completeness impossibly low ────────
    completeness = signals.get("profile_completeness_score", 100)
    if exp > 8 and completeness < 15:
        reasons.append(
            f"low_completeness: {exp}yr exp but "
            f"completeness={completeness}"
        )

    # ── Rule 5: Offer acceptance rate > 1 ─────────────────
    oar = signals.get("offer_acceptance_rate", 0)
    if oar > 1.0:
        reasons.append(f"impossible_oar: {oar}")

    # ── Rule 6: Signup date after last active date ─────────
    try:
        from datetime import datetime
        signup = datetime.strptime(
            signals.get("signup_date", "2020-01-01"), "%Y-%m-%d")
        last_active = datetime.strptime(
            signals.get("last_active_date", "2020-01-01"), "%Y-%m-%d")
        if signup > last_active:
            reasons.append(
                f"signup_after_active: "
                f"signup={signals['signup_date']} > "
                f"active={signals['last_active_date']}"
            )
    except (ValueError, TypeError):
        pass  # Malformed date strings cannot be compared.

    # ── Rule 7: Too many career hops with no AI work ───────
    if len(career) >= 6:
        avg_duration = sum(
            j.get("duration_months", 12) for j in career
        ) / len(career)
        if avg_duration < 8:
            reasons.append(
                f"excessive_hopping: {len(career)} jobs, "
                f"avg {avg_duration:.1f}mo"
            )

    is_honeypot = len(reasons) > 0
    return is_honeypot, reasons


if __name__ == "__main__":
    # Test on known honeypot pattern
    honeypot_test = {
        "candidate_id": "HONEYPOT_TEST",
        "profile": {"years_of_experience": 5.0,
                    "current_title": "ML Engineer"},
        "career_history": [{
            "company": "FakeCompany",
            "title": "ML Engineer",
            "duration_months": 72,  # > 5yr total exp!
            "is_current": True
        }],
        "skills": [
            {"name": f"Skill{i}", "proficiency": "expert",
             "endorsements": 0, "duration_months": 10}
            for i in range(8)
        ],
        "redrob_signals": {
            "expected_salary_range_inr_lpa": {"min": 50, "max": 30},
            "profile_completeness_score": 80,
            "offer_acceptance_rate": 0.5,
            "signup_date": "2025-01-01",
            "last_active_date": "2025-06-01"
        }
    }

    clean_test = {
        "candidate_id": "CLEAN_TEST",
        "profile": {"years_of_experience": 7.0,
                    "current_title": "Senior AI Engineer"},
        "career_history": [{
            "company": "Razorpay",
            "title": "Senior AI Engineer",
            "duration_months": 24,
            "is_current": True
        }],
        "skills": [
            {"name": "FAISS", "proficiency": "advanced",
             "endorsements": 10, "duration_months": 24}
        ],
        "redrob_signals": {
            "expected_salary_range_inr_lpa": {"min": 25, "max": 45},
            "profile_completeness_score": 85,
            "offer_acceptance_rate": 0.7,
            "signup_date": "2023-01-01",
            "last_active_date": "2026-05-01"
        }
    }

    print("=== HONEYPOT DETECTOR TEST ===\n")

    is_hp, reasons = detect_honeypot(honeypot_test)
    print(f"HONEYPOT_TEST: is_honeypot={is_hp}")
    for r in reasons:
        print(f"  ⚠️  {r}")

    is_hp, reasons = detect_honeypot(clean_test)
    print(f"\nCLEAN_TEST: is_honeypot={is_hp}")
    if not reasons:
        print("  ✅ Clean candidate!")