import json
from collections import Counter
from datetime import datetime, date

DATA_PATH = "data/candidates.jsonl"

AI_TITLES = [
    "ml engineer", "machine learning engineer", "ai engineer",
    "senior ai engineer", "lead ai engineer", "applied ml engineer",
    "nlp engineer", "search engineer", "recommendation systems engineer",
    "ai research engineer", "data scientist", "senior data scientist",
    "research engineer", "applied scientist", "mlops engineer",
    "information retrieval engineer", "ranking engineer",
    "junior ml engineer"
]

# JD ke basis pe — ye skills directly relevant hain
JD_SKILLS = {
    "tier1": [  # Must-have skills (highest weight)
        "embeddings", "vector search", "information retrieval",
        "semantic search", "faiss", "pinecone", "qdrant", "weaviate",
        "milvus", "pgvector", "opensearch", "elasticsearch",
        "sentence transformers", "bm25", "learning to rank",
        "recommendation systems", "ranking", "hybrid search"
    ],
    "tier2": [  # Strong signals
        "rag", "llms", "fine-tuning llms", "lora", "qlora", "peft",
        "hugging face transformers", "mlflow", "kubeflow", "mlops",
        "pytorch", "tensorflow", "langchain", "llamaindex",
        "weights & biases", "feature engineering", "ndcg", "map"
    ],
    "tier3": [  # Nice to have
        "python", "nlp", "machine learning", "deep learning",
        "transformers", "bert", "gpt", "llama", "mistral",
        "spark", "kafka", "airflow", "docker", "kubernetes",
        "aws", "gcp", "azure", "fastapi", "redis"
    ]
}

# Negative career signals
NOISE_SUMMARIES = [
    "curious about ai tools",
    "experimented with chatgpt",
    "i think the space is exciting",
    "apply my domain expertise alongside emerging ai",
    "online courses on rag",
    "side projects",
    "haven't done it in a professional capacity"
]

def is_ai_title(title):
    return any(t in title.lower() for t in AI_TITLES)

def score_skills(skills):
    skill_names_lower = {s["name"].lower() for s in skills}
    t1 = sum(1 for s in JD_SKILLS["tier1"] if s in skill_names_lower)
    t2 = sum(1 for s in JD_SKILLS["tier2"] if s in skill_names_lower)
    t3 = sum(1 for s in JD_SKILLS["tier3"] if s in skill_names_lower)
    return t1, t2, t3

def is_noise_candidate(candidate):
    summary = candidate["profile"].get("summary", "").lower()
    return any(noise in summary for noise in NOISE_SUMMARIES)

def days_since_active(last_active_str):
    try:
        last = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        today = date(2026, 6, 16)
        return (today - last).days
    except:
        return 999

def analyze_ai_candidates():
    candidates = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    ai_candidates = [c for c in candidates
                    if is_ai_title(c["profile"]["current_title"])]

    print(f"AI candidates: {len(ai_candidates)}")

    # Noise detection
    noise = [c for c in ai_candidates if is_noise_candidate(c)]
    real_ai = [c for c in ai_candidates if not is_noise_candidate(c)]
    print(f"Noise AI candidates: {len(noise)}")
    print(f"Real AI candidates: {len(real_ai)}")

    # Skill scoring
    print(f"\n--- SKILL DISTRIBUTION (Real AI candidates) ---")
    t1_counts, t2_counts, t3_counts = [], [], []
    for c in real_ai:
        t1, t2, t3 = score_skills(c.get("skills", []))
        t1_counts.append(t1)
        t2_counts.append(t2)
        t3_counts.append(t3)

    print(f"Avg Tier-1 skills (retrieval/embedding): {sum(t1_counts)/len(t1_counts):.2f}")
    print(f"Avg Tier-2 skills (LLM/MLOps):          {sum(t2_counts)/len(t2_counts):.2f}")
    print(f"Avg Tier-3 skills (general ML):          {sum(t3_counts)/len(t3_counts):.2f}")
    print(f"Candidates with 3+ Tier-1 skills: {sum(1 for t in t1_counts if t >= 3)}")
    print(f"Candidates with 5+ Tier-1 skills: {sum(1 for t in t1_counts if t >= 5)}")

    # Activity analysis
    print(f"\n--- ACTIVITY ANALYSIS ---")
    active_30d = sum(1 for c in real_ai
                    if days_since_active(
                        c["redrob_signals"]["last_active_date"]) <= 30)
    active_90d = sum(1 for c in real_ai
                    if days_since_active(
                        c["redrob_signals"]["last_active_date"]) <= 90)
    open_work = sum(1 for c in real_ai
                   if c["redrob_signals"]["open_to_work_flag"])

    print(f"Active last 30 days: {active_30d}")
    print(f"Active last 90 days: {active_90d}")
    print(f"Open to work: {open_work}")

    # Company size analysis
    print(f"\n--- COMPANY SIZE ---")
    sizes = [c["profile"]["current_company_size"] for c in real_ai]
    size_counts = Counter(sizes)
    for size, count in size_counts.most_common():
        print(f"  {size}: {count}")

    # Top candidates preview
    print(f"\n--- TOP 10 CANDIDATES (by Tier-1 skills) ---")
    scored = []
    for c in real_ai:
        t1, t2, t3 = score_skills(c.get("skills", []))
        exp = c["profile"]["years_of_experience"]
        signals = c["redrob_signals"]
        days_inactive = days_since_active(signals["last_active_date"])

        # Simple score
        score = (t1 * 3) + (t2 * 1.5) + (t3 * 0.5)
        score += min(exp, 9) * 0.3
        score += signals["recruiter_response_rate"] * 2
        if days_inactive <= 30:
            score += 1.0
        elif days_inactive <= 90:
            score += 0.5

        scored.append((score, c, t1, t2))

    scored.sort(key=lambda x: x[0], reverse=True)

    for score, c, t1, t2 in scored[:10]:
        p = c["profile"]
        sig = c["redrob_signals"]
        print(f"\n{c['candidate_id']} | {p['current_title']}")
        print(f"  Exp: {p['years_of_experience']}yr | "
              f"Company: {p['current_company']} ({p['current_company_size']})")
        print(f"  Tier1: {t1} | Tier2: {t2} | Score: {score:.2f}")
        print(f"  Response: {sig['recruiter_response_rate']:.0%} | "
              f"Active: {sig['last_active_date']} | "
              f"GitHub: {sig['github_activity_score']}")

if __name__ == "__main__":
    analyze_ai_candidates()
    print("\n✅ AI candidate analysis complete!")