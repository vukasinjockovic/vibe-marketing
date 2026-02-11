#!/usr/bin/env python3
"""Infer purchase behavior from focus group demographics, psychographics, and pain points.

Input: JSON focus group data on stdin or as file arg
Output: JSON {purchaseBehavior: {buyingTriggers, priceRange, decisionProcess, objectionHistory}, confidence, reasoning}

Inference rules:
  - buyingTriggers: derived from emotionalTriggers + painPoints + demographics.triggers
  - priceRange: derived from demographics.income
  - decisionProcess: derived from psychographics (analytical vs impulsive vs social)
  - objectionHistory: derived from objections array
"""
import json
import sys

# Income -> price range mapping
INCOME_PRICE_MAP = {
    # Keywords found in income string -> price range label
    "under": "budget/value-conscious",
    "student": "budget/value-conscious",
    "<25": "budget/value-conscious",
    "<$25": "budget/value-conscious",
    "25k": "budget/value-conscious",
    "30k": "low-to-mid range",
    "35k": "low-to-mid range",
    "40k": "mid-range",
    "45k": "mid-range",
    "50k": "mid-range",
    "60k": "mid-to-premium",
    "75k": "mid-to-premium",
    "80k": "mid-to-premium",
    "90k": "premium",
    "100k": "premium/high-end",
    "150k": "premium/high-end",
    "200k": "premium/high-end",
}

# Psychographic keywords -> decision process type
DECISION_PATTERNS = {
    "research": [
        "evidence", "research", "data", "analytical", "methodical",
        "rational", "data-driven", "studies", "proof",
    ],
    "impulsive": [
        "spontaneous", "impulse", "quick", "instant", "now",
        "act fast", "fomo", "limited time",
    ],
    "social": [
        "community", "friends", "family", "peers", "reviews",
        "recommendations", "word of mouth", "influencer",
    ],
    "deliberate": [
        "careful", "thorough", "compare", "weigh", "consider",
        "deliberate", "cautious", "risk-averse",
    ],
}


def _infer_price_range(demographics: dict | None) -> str:
    """Infer price sensitivity from income level."""
    if not demographics:
        return "unknown"

    income = (demographics.get("income") or "").lower()

    if not income:
        return "unknown"

    # Check for high-end indicators first (order matters for overlapping patterns)
    for keyword in ["200k", "150k", "100k"]:
        if keyword in income:
            return "premium/high-end"
    for keyword in ["90k"]:
        if keyword in income:
            return "premium"
    for keyword in ["75k", "80k", "60k"]:
        if keyword in income:
            return "mid-to-premium"
    for keyword in ["50k", "45k", "40k"]:
        if keyword in income:
            return "mid-range"
    for keyword in ["35k", "30k"]:
        if keyword in income:
            return "low-to-mid range"
    for keyword in ["under", "student", "<25", "<$25", "25k"]:
        if keyword in income:
            return "budget/value-conscious"

    # Fallback heuristics
    if "+" in income:
        # e.g. "$100k+" -> premium
        return "premium/high-end"

    return "mid-range"


def _infer_decision_process(psychographics: dict | None, objections: list[str]) -> str:
    """Infer decision-making style from psychographics and objections."""
    if not psychographics and not objections:
        return "unknown"

    # Gather all text from psychographics
    psych_text = ""
    if psychographics:
        values = psychographics.get("values") or []
        beliefs_list = psychographics.get("beliefs") or []
        lifestyle = psychographics.get("lifestyle") or ""
        identity = psychographics.get("identity") or ""
        psych_text = " ".join(
            [v.lower() for v in values]
            + [b.lower() for b in beliefs_list]
            + [lifestyle.lower(), identity.lower()]
        )

    objections_text = " ".join(o.lower() for o in objections)
    all_text = f"{psych_text} {objections_text}"

    scores = {}
    for process_type, keywords in DECISION_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in all_text)
        scores[process_type] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "mixed/unknown"

    labels = {
        "research": "research-heavy/analytical",
        "impulsive": "impulsive/emotional",
        "social": "socially-influenced",
        "deliberate": "deliberate/methodical",
    }
    return labels.get(best, best)


def _infer_buying_triggers(
    emotional_triggers: list[str],
    pain_points: list[str],
    demographics: dict | None,
) -> list[str]:
    """Combine emotional triggers, pain points, and demographic triggers."""
    triggers = []

    for et in emotional_triggers:
        triggers.append(et)

    for pp in pain_points:
        triggers.append(f"pain point: {pp}")

    if demographics:
        for dt in demographics.get("triggers") or []:
            triggers.append(f"life event: {dt}")

    return triggers if triggers else ["no triggers identified"]


def infer_purchase_behavior(fg_data: dict) -> dict:
    """Infer purchase behavior from focus group demographics, psychographics, pain points.

    Args:
        fg_data: Focus group data dict with optional keys:
            demographics, painPoints, objections, emotionalTriggers, psychographics

    Returns:
        Dict with purchaseBehavior object, confidence, and reasoning.
    """
    demographics = fg_data.get("demographics")
    pain_points = fg_data.get("painPoints") or []
    objections = fg_data.get("objections") or []
    emotional_triggers = fg_data.get("emotionalTriggers") or []
    psychographics = fg_data.get("psychographics")

    price_range = _infer_price_range(demographics)
    decision_process = _infer_decision_process(psychographics, objections)
    buying_triggers = _infer_buying_triggers(emotional_triggers, pain_points, demographics)
    objection_history = list(objections) if objections else ["none recorded"]

    # Calculate confidence based on how much data was available
    data_points = 0
    if demographics:
        data_points += 1
    if pain_points:
        data_points += 1
    if objections:
        data_points += 1
    if emotional_triggers:
        data_points += 1
    if psychographics:
        data_points += 1

    confidence = "high" if data_points >= 4 else "medium" if data_points >= 2 else "low"

    sources = []
    if demographics:
        sources.append("demographics")
    if pain_points:
        sources.append("painPoints")
    if objections:
        sources.append("objections")
    if emotional_triggers:
        sources.append("emotionalTriggers")
    if psychographics:
        sources.append("psychographics")

    reasoning = f"Inferred from {data_points} data sources ({', '.join(sources) if sources else 'none'}). Price range from income: {price_range}. Decision process: {decision_process}."

    return {
        "purchaseBehavior": {
            "buyingTriggers": buying_triggers,
            "priceRange": price_range,
            "decisionProcess": decision_process,
            "objectionHistory": objection_history,
        },
        "confidence": confidence,
        "reasoning": reasoning,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    result = infer_purchase_behavior(data)
    print(json.dumps(result, indent=2))
