from src.utils.constants import AI_TITLES, NON_AI_TITLES

RETRIEVAL_SKILLS = {
    "Embeddings",
    "Sentence Transformers",
    "Semantic Search",
    "Vector Search",
    "Information Retrieval",
    "BM25",
    "Learning to Rank",
    "Recommendation Systems",
    "FAISS",
    "Milvus",
    "Pinecone",
    "Qdrant",
    "Weaviate",
    "pgvector",
    "OpenSearch",
    "Elasticsearch"
}

FRAMEWORK_TOURIST = {
    "LangChain",
    "LlamaIndex",
    "Prompt Engineering",
    "RAG"
}

PRODUCTION_AI_SKILLS = {
    "MLOps",
    "MLflow",
    "Kubeflow",
    "BentoML",
    "Feature Engineering",
    "Python",
    "scikit-learn",
    "PyTorch",
    "TensorFlow"
}


def get_title(candidate):

    return candidate["profile"].get(
        "current_title",
        ""
    )


def get_skills(candidate):

    return [
        s.get("name", "")
        for s in candidate.get("skills", [])
    ]


def ai_title_score(candidate):

    title = get_title(candidate)

    if title in AI_TITLES:
        return 20

    return 0


def non_ai_title_penalty(candidate):

    title = get_title(candidate)

    if title in NON_AI_TITLES:
        return 20

    return 0


def retrieval_depth_score(candidate):

    skills = get_skills(candidate)

    count = 0

    for s in skills:

        if s in RETRIEVAL_SKILLS:
            count += 1

    return count


def production_ai_score(candidate):

    skills = get_skills(candidate)

    count = 0

    for s in skills:

        if s in PRODUCTION_AI_SKILLS:
            count += 1

    return count


def framework_tourist_penalty(candidate):

    skills = get_skills(candidate)

    framework_count = 0

    retrieval_count = 0

    for s in skills:

        if s in FRAMEWORK_TOURIST:
            framework_count += 1

        if s in RETRIEVAL_SKILLS:
            retrieval_count += 1

    if framework_count >= 3 and retrieval_count == 0:
        return 20

    if framework_count >= 2 and retrieval_count <= 1:
        return 12

    return 0


def fake_ai_penalty(candidate):

    title = get_title(candidate)

    skills = get_skills(candidate)

    ai_skill_count = 0

    for s in skills:

        if (
            s in RETRIEVAL_SKILLS
            or s in PRODUCTION_AI_SKILLS
        ):
            ai_skill_count += 1

    if (
        title in NON_AI_TITLES
        and ai_skill_count >= 8
    ):
        return 25

    return 0


def recommendation_bonus(candidate):

    history = candidate.get(
        "career_history",
        []
    )

    score = 0

    for role in history:

        title = (
            role.get("title", "")
            .lower()
        )

        if "recommendation" in title:
            score += 20

        if "search" in title:
            score += 20

        if "retrieval" in title:
            score += 20

        if "ranking" in title:
            score += 20

    return score


def ai_signal_profile(candidate):

    profile = {}

    profile["ai_title_score"] = (
        ai_title_score(candidate)
    )

    profile["retrieval_depth_score"] = (
        retrieval_depth_score(candidate)
    )

    profile["production_ai_score"] = (
        production_ai_score(candidate)
    )

    profile["recommendation_bonus"] = (
        recommendation_bonus(candidate)
    )

    profile["framework_tourist_penalty"] = (
        framework_tourist_penalty(candidate)
    )

    profile["fake_ai_penalty"] = (
        fake_ai_penalty(candidate)
    )

    profile["non_ai_title_penalty"] = (
        non_ai_title_penalty(candidate)
    )

    return profile