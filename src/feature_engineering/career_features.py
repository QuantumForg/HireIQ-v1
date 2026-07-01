CONSULTING_COMPANIES = {
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Cognizant",
    "Capgemini",
    "HCL",
    "Tech Mahindra",
    "LTIMindtree"
}

PRODUCT_INDUSTRIES = {
    "AI/ML",
    "Software",
    "SaaS",
    "E-commerce",
    "Fintech",
    "HealthTech",
    "Food Delivery",
    "Transportation",
    "Gaming",
    "EdTech"
}

SEARCH_KEYWORDS = {
    "search",
    "retrieval",
    "ranking",
    "recommendation",
    "recommend",
    "matching",
    "relevance",
    "candidate matching"
}

PRODUCTION_KEYWORDS = {
    "production",
    "deployed",
    "deployment",
    "real users",
    "scale",
    "online",
    "serving",
    "latency",
    "inference",
    "monitoring",
    "evaluation",
    "a/b",
    "ab test",
    "pipeline"
}

RESEARCH_KEYWORDS = {
    "research",
    "paper",
    "publication",
    "academic",
    "thesis",
    "scientist"
}

CV_KEYWORDS = {
    "computer vision",
    "object detection",
    "image classification",
    "opencv",
    "yolo",
    "cnn"
}

SPEECH_KEYWORDS = {
    "speech",
    "tts",
    "asr",
    "voice",
    "speech recognition"
}


def safe_text(value):

    if value is None:
        return ""

    return str(value).lower()


def count_keywords(text, keywords):

    score = 0

    for kw in keywords:
        if kw in text:
            score += 1

    return score


def get_career_history(candidate):

    return candidate.get("career_history", [])


def product_company_score(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        industry = job.get("industry", "")

        if industry in PRODUCT_INDUSTRIES:
            score += 1

    return score


def consulting_penalty(candidate):

    history = get_career_history(candidate)

    total = len(history)

    if total == 0:
        return 0

    consulting_count = 0

    for job in history:

        company = job.get("company", "")

        if company in CONSULTING_COMPANIES:
            consulting_count += 1

    ratio = consulting_count / total

    if ratio >= 1.0:
        return 1

    if ratio >= 0.75:
        return 0.75

    if ratio >= 0.5:
        return 0.5

    return 0


def search_recommendation_score(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        title = safe_text(job.get("title"))

        description = safe_text(job.get("description"))

        combined = title + " " + description

        score += count_keywords(
            combined,
            SEARCH_KEYWORDS
        )

    return score


def production_ml_score(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        description = safe_text(
            job.get("description")
        )

        score += count_keywords(
            description,
            PRODUCTION_KEYWORDS
        )

    return score


def research_penalty(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        description = safe_text(
            job.get("description")
        )

        score += count_keywords(
            description,
            RESEARCH_KEYWORDS
        )

    return score


def cv_penalty(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        text = (
            safe_text(job.get("title"))
            + " "
            + safe_text(job.get("description"))
        )

        score += count_keywords(
            text,
            CV_KEYWORDS
        )

    return score


def speech_penalty(candidate):

    score = 0

    history = get_career_history(candidate)

    for job in history:

        text = (
            safe_text(job.get("title"))
            + " "
            + safe_text(job.get("description"))
        )

        score += count_keywords(
            text,
            SPEECH_KEYWORDS
        )

    return score


def job_hop_score(candidate):

    history = get_career_history(candidate)

    if len(history) == 0:
        return 0

    short_roles = 0

    for role in history:

        months = role.get(
            "duration_months",
            0
        )

        if months <= 18:
            short_roles += 1

    return short_roles


def seniority_score(candidate):

    exp = candidate["profile"].get(
        "years_of_experience",
        0
    )

    if 5 <= exp <= 9:
        return 10

    if 4 <= exp <= 10:
        return 7

    if 3 <= exp <= 12:
        return 4

    return 0


def career_profile(candidate):

    profile = {}

    profile["product_company_score"] = (
        product_company_score(candidate)
    )

    profile["consulting_penalty"] = (
        consulting_penalty(candidate)
    )

    profile["search_system_score"] = (
        search_recommendation_score(candidate)
    )

    profile["production_ml_score"] = (
        production_ml_score(candidate)
    )

    profile["research_penalty"] = (
        research_penalty(candidate)
    )

    profile["cv_penalty"] = (
        cv_penalty(candidate)
    )

    profile["speech_penalty"] = (
        speech_penalty(candidate)
    )

    profile["job_hop_score"] = (
        job_hop_score(candidate)
    )

    profile["seniority_score"] = (
        seniority_score(candidate)
    )

    return profile