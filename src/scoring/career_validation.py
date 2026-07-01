POSITIVE_TITLES = {
    "Recommendation Systems Engineer",
    "Search Engineer",
    "Applied ML Engineer",
    "ML Engineer",
    "Machine Learning Engineer",
    "AI Engineer",
    "NLP Engineer",
    "Senior NLP Engineer",
    "AI Research Engineer",
    "Data Scientist",
    "Senior Data Scientist",
    "Senior Machine Learning Engineer",
    "Senior Applied Scientist",
    "Lead AI Engineer",
    "Senior AI Engineer",
    "Analytics Engineer",
    "Data Engineer",
    "Backend Engineer",
    "Senior Data Engineer",
    "Senior Software Engineer"
}

NEGATIVE_TITLES = {
    "Marketing Manager",
    "HR Manager",
    "Graphic Designer",
    "Content Writer",
    "Customer Support",
    "Accountant",
    "Sales Executive",
    "Business Analyst",
    "Civil Engineer",
    "Mechanical Engineer",
    "Operations Manager"
}


POSITIVE_KEYWORDS = {
    "retrieval",
    "ranking",
    "recommendation",
    "search",
    "relevance",
    "matching",
    "embeddings",
    "vector",
    "semantic",
    "information retrieval",
    "learning to rank",
    "nlp",
    "rag",
    "llm",
    "transformers"
}


NEGATIVE_KEYWORDS = {
    "seo",
    "content marketing",
    "brand",
    "sales",
    "customer support",
    "recruitment",
    "hr",
    "graphic design",
    "accounting",
    "operations management"
}


def career_validation_score(candidate):

    score = 0

    history = candidate.get(
        "career_history",
        []
    )

    for job in history:

        title = job.get(
            "title",
            ""
        )

        desc = (
            job.get(
                "description",
                ""
            )
            .lower()
        )

        if title in POSITIVE_TITLES:
            score += 15

        if title in NEGATIVE_TITLES:
            score -= 20

        for kw in POSITIVE_KEYWORDS:

            if kw in desc:
                score += 5

        for kw in NEGATIVE_KEYWORDS:

            if kw in desc:
                score -= 5

    return score