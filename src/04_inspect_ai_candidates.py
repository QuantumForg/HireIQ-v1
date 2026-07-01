import json
from datetime import datetime, date
from collections import Counter

DATA_PATH = "data/candidates.jsonl"

AI_TITLES = [
    "ml engineer", "machine learning engineer", "ai engineer",
    "senior ai engineer", "lead ai engineer", "applied ml engineer",
    "nlp engineer", "search engineer", "recommendation systems engineer",
    "ai research engineer", "data scientist", "senior data scientist",
    "research engineer", "applied scientist", "mlops engineer",
    "junior ml engineer"
]

JD_TIER1_SKILLS = [
    "embeddings", "vector search", "information retrieval",
    "semantic search", "faiss", "pinecone", "qdrant", "weaviate",
    "milvus", "pgvector", "opensearch", "elasticsearch",
    "sentence transformers", "bm25", "learning to rank",
    "recommendation systems", "ranking", "hybrid search"
]

# Honeypot detection rules
def detect_honeypot(candidate):
    reasons = []
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    career = candidate.get("career_history", [])

    exp = profile["years_of_experience"]

    # Rule 1: Company founded after candidate's start date
    for job in career:
        company = job.get("company", "")
        start = job.get("start_date", "")
        duration = job.get("duration_months", 0)
        if duration > 0 and exp > 0:
            # Impossible experience
            if duration > exp * 12 + 6:
                reasons.append(f"Duration {duration}mo > total exp {exp}yr")

    # Rule 2: Expert in 10+ skills with very low endorsements
    skills = candidate.get("skills", [])
    expert_skills = [s for s in skills if s.get("proficiency") == "expert"]
    if len(expert_skills) > 8:
        avg_endorse = sum(s.get("endorsements", 0) for s in expert_skills) / len(expert_skills)
        if avg_endorse < 2:
            reasons.append(f"Expert in {len(expert_skills)} skills, avg {avg_endorse:.1f} endorsements")

    # Rule 3: salary min > max (impossible range)
    salary = signals.get("expected_salary_range_inr_lpa", {})
    sal_min = salary.get("min", 0)
    sal_max = salary.get("max", 0)
    if sal_min > sal_max and sal_max > 0:
        reasons.append(f"Salary min ({sal_min}) > max ({sal_max})")

    # Rule 4: Very high experience but very low profile completeness
    if exp > 10 and signals.get("profile_completeness_score", 100) < 20:
        reasons.append(f"High exp {exp}yr but completeness {signals['profile_completeness_score']}")

    # Rule 5: offer_acceptance_rate impossible
    oar = signals.get("offer_acceptance_rate", 0)
    if oar > 1.0:
        reasons.append(f"Impossible offer_acceptance_rate: {oar}")

    return reasons

def days_since_active(last_active_str):
    try:
        last = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        today = date(2026, 6, 16)
        return (today - last).days
    except:
        return 999

def inspect_candidates():
    candidates = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    ai_candidates = [c for c in candidates
                    if any(t in c["profile"]["current_title"].lower()
                           for t in AI_TITLES)]

    print(f"AI candidates: {len(ai_candidates)}")

    # Honeypot detection
    honeypots = []
    clean = []
    for c in ai_candidates:
        reasons = detect_honeypot(c)
        if reasons:
            honeypots.append((c, reasons))
        else:
            clean.append(c)

    print(f"\nHoneypots detected: {len(honeypots)}")
    print(f"Clean candidates: {len(clean)}")

    if honeypots:
        print(f"\n--- HONEYPOT EXAMPLES ---")
        for c, reasons in honeypots[:5]:
            print(f"\n{c['candidate_id']} | {c['profile']['current_title']}")
            for r in reasons:
                print(f"  ⚠️  {r}")

    # Career history analysis on clean candidates
    print(f"\n--- CAREER HISTORY PATTERNS ---")
    product_cos = ["flipkart", "amazon", "google", "microsoft", "netflix",
                   "swiggy", "zomato", "paytm", "razorpay", "phonepe",
                   "meesho", "ola", "uber", "myntra", "nykaa", "cred",
                   "dream11", "upstox", "zepto", "blinkit", "sarvam",
                   "krutrim", "openai", "anthropic", "hugging face",
                   "cohere", "mistral", "together ai", "groq"]

    product_exp_count = 0
    consulting_only = 0
    consulting_cos = ["tcs", "infosys", "wipro", "accenture",
                      "cognizant", "capgemini", "hcl", "tech mahindra",
                      "mphasis", "hexaware"]

    for c in clean:
        companies_lower = [job["company"].lower()
                          for job in c.get("career_history", [])]
        has_product = any(any(p in co for p in product_cos)
                         for co in companies_lower)
        all_consulting = all(any(cons in co for cons in consulting_cos)
                            for co in companies_lower)
        if has_product:
            product_exp_count += 1
        if all_consulting:
            consulting_only += 1

    print(f"Has product company exp: {product_exp_count}/{len(clean)}")
    print(f"Pure consulting career: {consulting_only}/{len(clean)}")

    # Top candidates full profile
    print(f"\n--- FULL PROFILE: TOP 5 CANDIDATES ---")

    # Score them
    scored = []
    for c in clean:
        skills_lower = {s["name"].lower() for s in c.get("skills", [])}
        t1 = sum(1 for s in JD_TIER1_SKILLS if s in skills_lower)
        exp = c["profile"]["years_of_experience"]
        sig = c["redrob_signals"]
        days_inactive = days_since_active(sig["last_active_date"])

        score = t1 * 3 + exp * 0.3
        score += sig["recruiter_response_rate"] * 2
        if days_inactive <= 30: score += 1.5
        elif days_inactive <= 90: score += 0.7
        if sig["open_to_work_flag"]: score += 0.5

        scored.append((score, c, t1))

    scored.sort(key=lambda x: x[0], reverse=True)

    for score, c, t1 in scored[:5]:
        p = c["profile"]
        sig = c["redrob_signals"]
        skills = [s["name"] for s in c.get("skills", [])
                 if s.get("proficiency") in ["advanced", "expert"]]
        print(f"\n{'='*45}")
        print(f"ID: {c['candidate_id']}")
        print(f"Title: {p['current_title']}")
        print(f"Exp: {p['years_of_experience']}yr | "
              f"Company: {p['current_company']} ({p['current_company_size']})")
        print(f"Location: {p['location']}, {p['country']}")
        print(f"Tier1 Skills: {t1} | Score: {score:.2f}")
        print(f"Advanced Skills: {', '.join(skills[:10])}")
        print(f"Response Rate: {sig['recruiter_response_rate']:.0%}")
        print(f"Last Active: {sig['last_active_date']}")
        print(f"GitHub: {sig['github_activity_score']}")
        print(f"Open to Work: {sig['open_to_work_flag']}")
        print(f"Notice: {sig['notice_period_days']} days")

        # Career history
        print(f"Career:")
        for job in c.get("career_history", [])[:3]:
            print(f"  {job['title']} @ {job['company']} "
                  f"({job['duration_months']}mo)")

if __name__ == "__main__":
    inspect_candidates()
    print("\n✅ Inspection complete!")