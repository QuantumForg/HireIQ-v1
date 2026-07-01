import json
import os
from collections import Counter

DATA_PATH = "data/candidates.jsonl"

# JD ke basis pe — ye titles strong signal hain
AI_TITLES = [
    "ml engineer", "machine learning engineer", "ai engineer",
    "senior ai engineer", "lead ai engineer", "applied ml engineer",
    "nlp engineer", "search engineer", "recommendation systems engineer",
    "ai research engineer", "data scientist", "senior data scientist",
    "research engineer", "applied scientist", "mlops engineer",
    "information retrieval engineer", "ranking engineer"
]

def is_ai_title(title: str) -> bool:
    title_lower = title.lower()
    return any(ai_title in title_lower for ai_title in AI_TITLES)

def explore_titles():
    candidates = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    print(f"Total candidates: {len(candidates)}")

    # All titles
    all_titles = [c["profile"]["current_title"] for c in candidates]
    title_counts = Counter(all_titles)

    # AI titles
    ai_candidates = [c for c in candidates if is_ai_title(
        c["profile"]["current_title"])]

    print(f"\nAI-titled candidates: {len(ai_candidates)}")
    print(f"Percentage: {len(ai_candidates)/len(candidates)*100:.1f}%")

    # AI title breakdown
    ai_titles = [c["profile"]["current_title"] for c in ai_candidates]
    ai_title_counts = Counter(ai_titles)

    print(f"\nAI Title Breakdown:")
    for title, count in ai_title_counts.most_common(20):
        print(f"  {count:4d} | {title}")

    # Experience of AI candidates
    ai_exp = [c["profile"]["years_of_experience"] for c in ai_candidates]
    if ai_exp:
        print(f"\nAI Candidates Experience:")
        print(f"  Average: {sum(ai_exp)/len(ai_exp):.1f} years")
        print(f"  5-9 yrs: {sum(1 for e in ai_exp if 5 <= e <= 9)}")
        print(f"  4-10 yrs: {sum(1 for e in ai_exp if 4 <= e <= 10)}")

    # Education tier of AI candidates
    ai_tiers = []
    for c in ai_candidates:
        for edu in c.get("education", []):
            ai_tiers.append(edu.get("tier", "unknown"))
    tier_counts = Counter(ai_tiers)
    print(f"\nAI Candidates Education Tiers:")
    for tier, count in tier_counts.most_common():
        print(f"  {tier}: {count}")

    # Sample 3 AI candidates
    print(f"\n--- SAMPLE AI CANDIDATES ---")
    for c in ai_candidates[:3]:
        p = c["profile"]
        skills = [s["name"] for s in c.get("skills", [])
                 if s.get("proficiency") in ["advanced", "expert"]]
        print(f"\nID: {c['candidate_id']}")
        print(f"Title: {p['current_title']} | Exp: {p['years_of_experience']}yrs")
        print(f"Company: {p['current_company']} ({p['current_company_size']})")
        print(f"Advanced Skills: {', '.join(skills[:8])}")
        signals = c["redrob_signals"]
        print(f"Active: {signals['last_active_date']} | "
              f"Response: {signals['recruiter_response_rate']:.0%} | "
              f"GitHub: {signals['github_activity_score']}")

if __name__ == "__main__":
    explore_titles()
    print("\n✅ Title exploration complete!")