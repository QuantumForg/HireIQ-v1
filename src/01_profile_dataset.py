import json
import gzip
import os
from collections import Counter

DATA_PATH = "data/candidates.jsonl"
GZ_PATH = "data/candidates.jsonl.gz"

def load_candidates(path):
    candidates = []
    
    # Check if gz or plain jsonl
    if path.endswith(".gz"):
        opener = gzip.open(path, "rt", encoding="utf-8")
    else:
        opener = open(path, "r", encoding="utf-8")
    
    print(f"Loading candidates from {path}...")
    with opener as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    candidates.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            if (i + 1) % 10000 == 0:
                print(f"  Loaded {i+1} candidates...")
    
    return candidates

def profile_dataset(candidates):
    print(f"\n{'='*50}")
    print(f"DATASET PROFILE")
    print(f"{'='*50}")
    
    total = len(candidates)
    print(f"Total candidates: {total}")
    
    # Experience distribution
    experiences = [c["profile"]["years_of_experience"] for c in candidates]
    print(f"\nExperience:")
    print(f"  Average : {sum(experiences)/len(experiences):.1f} years")
    print(f"  Min     : {min(experiences)} years")
    print(f"  Max     : {max(experiences)} years")
    
    # Title distribution
    titles = [c["profile"]["current_title"] for c in candidates]
    title_counts = Counter(titles)
    print(f"\nTop 15 Current Titles:")
    for title, count in title_counts.most_common(15):
        print(f"  {count:5d} | {title}")
    
    # Industry distribution
    industries = [c["profile"]["current_industry"] for c in candidates]
    industry_counts = Counter(industries)
    print(f"\nTop 10 Industries:")
    for ind, count in industry_counts.most_common(10):
        print(f"  {count:5d} | {ind}")
    
    # Country distribution
    countries = [c["profile"]["country"] for c in candidates]
    country_counts = Counter(countries)
    print(f"\nTop 5 Countries:")
    for country, count in country_counts.most_common(5):
        print(f"  {count:5d} | {country}")
    
    # open_to_work
    open_to_work = sum(1 for c in candidates 
                      if c["redrob_signals"]["open_to_work_flag"])
    print(f"\nOpen to Work: {open_to_work} ({open_to_work/total*100:.1f}%)")
    
    # Skills overview
    all_skills = []
    for c in candidates:
        all_skills.extend([s["name"] for s in c.get("skills", [])])
    skill_counts = Counter(all_skills)
    print(f"\nTop 20 Skills:")
    for skill, count in skill_counts.most_common(20):
        print(f"  {count:5d} | {skill}")
    
    # Education tier
    tiers = []
    for c in candidates:
        for edu in c.get("education", []):
            tiers.append(edu.get("tier", "unknown"))
    tier_counts = Counter(tiers)
    print(f"\nEducation Tiers:")
    for tier, count in tier_counts.most_common():
        print(f"  {count:5d} | {tier}")

if __name__ == "__main__":
    # Load data
    if os.path.exists(DATA_PATH):
        candidates = load_candidates(DATA_PATH)
    elif os.path.exists(GZ_PATH):
        candidates = load_candidates(GZ_PATH)
    else:
        print("ERROR: candidates.jsonl not found in data/ folder!")
        exit(1)
    
    # Profile
    profile_dataset(candidates)
    
    print(f"\n✅ Day 1 complete — {len(candidates)} candidates loaded!")