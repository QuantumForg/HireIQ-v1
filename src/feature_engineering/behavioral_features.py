def normalize(value, max_value):

    if max_value <= 0:
        return 0

    return min(value / max_value, 1.0)


def response_score(signals):

    rate = signals.get(
        "recruiter_response_rate",
        0
    )

    return rate * 25


def profile_completeness_score(signals):

    score = signals.get(
        "profile_completeness_score",
        0
    )

    return score / 4


def activity_score(signals):

    views = signals.get(
        "profile_views_received_30d",
        0
    )

    applications = signals.get(
        "applications_submitted_30d",
        0
    )

    appearances = signals.get(
        "search_appearance_30d",
        0
    )

    score = (
        normalize(views, 100) * 8
        + normalize(applications, 20) * 6
        + normalize(appearances, 200) * 8
    )

    return score


def recruiter_interest_score(signals):

    saved = signals.get(
        "saved_by_recruiters_30d",
        0
    )

    return min(saved, 20)


def open_to_work_score(signals):

    if signals.get(
        "open_to_work_flag",
        False
    ):
        return 10

    return 0


def verification_score(signals):

    score = 0

    if signals.get("verified_email"):
        score += 3

    if signals.get("verified_phone"):
        score += 3

    if signals.get("linkedin_connected"):
        score += 4

    return score


def response_speed_score(signals):

    hours = signals.get(
        "avg_response_time_hours",
        9999
    )

    if hours <= 24:
        return 10

    if hours <= 48:
        return 8

    if hours <= 72:
        return 6

    if hours <= 120:
        return 4

    if hours <= 240:
        return 2

    return 0


def notice_period_penalty(signals):

    notice = signals.get(
        "notice_period_days",
        999
    )

    if notice <= 30:
        return 0

    if notice <= 60:
        return 3

    if notice <= 90:
        return 7

    if notice <= 120:
        return 12

    return 18


def behavioral_profile(candidate):

    signals = candidate.get(
        "redrob_signals",
        {}
    )

    profile = {}

    profile["response_score"] = (
        response_score(signals)
    )

    profile["profile_score"] = (
        profile_completeness_score(signals)
    )

    profile["activity_score"] = (
        activity_score(signals)
    )

    profile["recruiter_interest_score"] = (
        recruiter_interest_score(signals)
    )

    profile["open_to_work_score"] = (
        open_to_work_score(signals)
    )

    profile["verification_score"] = (
        verification_score(signals)
    )

    profile["response_speed_score"] = (
        response_speed_score(signals)
    )

    profile["notice_penalty"] = (
        notice_period_penalty(signals)
    )

    return profile