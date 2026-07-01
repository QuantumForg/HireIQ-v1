from src.utils.constants import (
    VECTOR_DB_SKILLS,
    RETRIEVAL_SKILLS,
    LLM_SKILLS,
    ML_CORE_SKILLS,
    CV_ONLY_SKILLS,
    SPEECH_ONLY_SKILLS
)

def safe_skills(candidate):
    return [
        s.get("name", "").strip()
        for s in candidate.get("skills", [])
        if s.get("name")
    ]

def count_overlap(skills, target):
    return sum(1 for s in skills if s in target)

def score_vector_databases(skills):
    return count_overlap(skills, VECTOR_DB_SKILLS)

def score_retrieval(skills):
    return count_overlap(skills, RETRIEVAL_SKILLS)

def score_llm(skills):
    return count_overlap(skills, LLM_SKILLS)

def score_ml_core(skills):
    return count_overlap(skills, ML_CORE_SKILLS)

def score_cv_only(skills):
    return count_overlap(skills, CV_ONLY_SKILLS)

def score_speech_only(skills):
    return count_overlap(skills, SPEECH_ONLY_SKILLS)

def score_python(skills):
    return 1 if "Python" in skills else 0

def score_rag(skills):
    score = 0

    if "RAG" in skills:
        score += 1

    if "LlamaIndex" in skills:
        score += 1

    if "LangChain" in skills:
        score += 1

    return score

def score_embedding_stack(skills):

    embedding_related = {
        "Embeddings",
        "Sentence Transformers",
        "Semantic Search",
        "Vector Search",
        "Information Retrieval",
        "Hugging Face Transformers"
    }

    return count_overlap(skills, embedding_related)

def score_ranking_stack(skills):

    ranking_related = {
        "BM25",
        "Learning to Rank",
        "Recommendation Systems"
    }

    return count_overlap(skills, ranking_related)

def score_finetuning(skills):

    finetune = {
        "LoRA",
        "QLoRA",
        "PEFT",
        "Fine-tuning LLMs"
    }

    return count_overlap(skills, finetune)

def score_infra(skills):

    infra = {
        "Docker",
        "Kubernetes",
        "MLOps",
        "Kubeflow",
        "MLflow"
    }

    return count_overlap(skills, infra)

def skill_profile(candidate):

    skills = safe_skills(candidate)

    profile = {}

    profile["vector_db_score"] = score_vector_databases(skills)

    profile["retrieval_score"] = score_retrieval(skills)

    profile["embedding_score"] = score_embedding_stack(skills)

    profile["ranking_score"] = score_ranking_stack(skills)

    profile["llm_score"] = score_llm(skills)

    profile["finetune_score"] = score_finetuning(skills)

    profile["ml_core_score"] = score_ml_core(skills)

    profile["infra_score"] = score_infra(skills)

    profile["python_score"] = score_python(skills)

    profile["rag_score"] = score_rag(skills)

    profile["cv_score"] = score_cv_only(skills)

    profile["speech_score"] = score_speech_only(skills)

    profile["total_ai_skill_score"] = (
        profile["vector_db_score"] * 4
        + profile["retrieval_score"] * 5
        + profile["embedding_score"] * 5
        + profile["ranking_score"] * 6
        + profile["llm_score"] * 2
        + profile["finetune_score"] * 3
        + profile["ml_core_score"] * 3
        + profile["infra_score"] * 2
        + profile["python_score"] * 4
    )

    return profile