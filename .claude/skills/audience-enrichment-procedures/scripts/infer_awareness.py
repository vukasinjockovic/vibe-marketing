#!/usr/bin/env python3
"""Infer Schwartz awareness stage from focus group fields.

Input: JSON focus group data on stdin or as file arg
Output: JSON {awarenessStage, awarenessConfidence, awarenessStageSource, awarenessSignals, reasoning}

Uses keyword matching against beliefs, objections, language patterns, and pain points
to classify into one of 5 Schwartz awareness stages:
  - unaware: doesn't recognize the problem
  - problem_aware: recognizes the problem but doesn't know solutions
  - solution_aware: knows solutions exist but hasn't chosen
  - product_aware: knows specific products, has tried similar
  - most_aware: compares products, asks about pricing/deals
"""
import json
import sys

AWARENESS_RULES = {
    "most_aware": {
        "signals": [
            "mentions specific product by name",
            "compares features",
            "asks about pricing/deals",
            "knows competitors by name",
        ],
        "beliefs_keywords": ["best", "compared to", "deal", "coupon", "worth it"],
        "objections_keywords": ["price", "cost", "cheaper", "alternative"],
    },
    "product_aware": {
        "signals": [
            "knows solution category exists",
            "has tried similar products",
            "asks 'which one'",
        ],
        "beliefs_keywords": ["tried", "didn't work", "looking for", "better option"],
        "objections_keywords": ["different", "trust", "guarantee", "scam"],
    },
    "solution_aware": {
        "signals": [
            "knows solutions exist but hasn't chosen",
            "researching options",
            "comparing approaches",
        ],
        "beliefs_keywords": ["i know", "should", "need to", "heard about"],
        "objections_keywords": ["time", "effort", "complicated", "overwhelmed"],
    },
    "problem_aware": {
        "signals": [
            "recognizes the problem",
            "feels pain but doesn't know solutions",
            "frustrated",
        ],
        "beliefs_keywords": ["struggling", "can't", "frustrated", "why", "stuck"],
        "objections_keywords": ["nothing works", "tried everything", "genetics"],
    },
    "unaware": {
        "signals": [
            "doesn't recognize the problem",
            "content with status quo",
            "no urgency",
        ],
        "beliefs_keywords": ["fine", "doesn't matter", "someday", "not a priority"],
        "objections_keywords": ["don't need", "happy", "later"],
    },
}


def infer_awareness(fg_data: dict) -> dict:
    """Classify a focus group into one of 5 Schwartz awareness stages.

    Args:
        fg_data: Focus group data dict with optional keys:
            beliefs, objections, languagePatterns, painPoints

    Returns:
        Dict with awarenessStage, awarenessConfidence, awarenessStageSource,
        awarenessSignals, and reasoning.
    """
    beliefs = [b.lower() for b in (fg_data.get("beliefs") or [])]
    objections = [o.lower() for o in (fg_data.get("objections") or [])]
    language = [lp.lower() for lp in (fg_data.get("languagePatterns") or [])]
    pain_points = [p.lower() for p in (fg_data.get("painPoints") or [])]

    all_text = " ".join(beliefs + objections + language + pain_points)

    scores = {}
    reasoning = {}

    for stage, rules in AWARENESS_RULES.items():
        score = 0
        matches = []
        for kw in rules["beliefs_keywords"]:
            if kw in all_text:
                score += 1
                matches.append(f"beliefs/language contains '{kw}'")
        for kw in rules["objections_keywords"]:
            if any(kw in o for o in objections):
                score += 1
                matches.append(f"objection contains '{kw}'")
        scores[stage] = score
        reasoning[stage] = matches

    best_stage = max(scores, key=scores.get)
    best_score = scores[best_stage]

    confidence = "high" if best_score >= 3 else "medium" if best_score >= 2 else "low"

    # Build signals broken out by source type
    beliefs_signals = [r for r in reasoning[best_stage] if "beliefs/language" in r]
    objection_signals = [r for r in reasoning[best_stage] if "objection" in r]
    language_signals = [r for r in reasoning[best_stage] if "language" in r.lower() and "beliefs" not in r]

    signals = {
        "beliefsSignal": "; ".join(beliefs_signals[:3]) if beliefs_signals else None,
        "objectionsSignal": "; ".join(objection_signals[:2]) if objection_signals else None,
        "languageSignal": "; ".join(language_signals[:2]) if language_signals else None,
    }

    match_summary = "; ".join(reasoning[best_stage][:3]) if reasoning[best_stage] else "no strong indicators"

    return {
        "awarenessStage": best_stage,
        "awarenessConfidence": confidence,
        "awarenessStageSource": "auto",
        "awarenessSignals": signals,
        "reasoning": f"Matched {best_score} indicators for {best_stage}: {match_summary}",
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    result = infer_awareness(data)
    print(json.dumps(result, indent=2))
