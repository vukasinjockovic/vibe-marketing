#!/usr/bin/env python3
"""Infer market sophistication level from focus group fields.

Input: JSON focus group data on stdin or as file arg
Output: JSON {sophisticationLevel, confidence, reasoning}

Market sophistication stages (Schwartz/Schwarz model):
  - stage1: "First to market" -- simple, direct claims work
  - stage2: "Expanded claim" -- bigger, better claims needed
  - stage3: "Unique mechanism" -- HOW it works matters
  - stage4: "Expanded mechanism" -- better mechanism + more proof
  - stage5: "Identification" -- prospect buys based on brand/identity
"""
import json
import sys

SOPHISTICATION_RULES = {
    "stage1": {
        "description": "First to market - simple direct claims work",
        "hook_keywords": [
            "lose", "get", "fast", "#1", "best", "easy", "simple",
            "guaranteed", "free",
        ],
        "language_keywords": [
            "never tried", "first time", "new to", "just starting",
            "simple solution",
        ],
        "beliefs_keywords": [
            "just need", "simple", "one thing", "quick fix",
        ],
        "objections_keywords": [],
    },
    "stage2": {
        "description": "Expanded claims - bigger, better claims needed",
        "hook_keywords": [
            "more effective", "faster", "clinically proven", "leading",
            "results", "powerful", "advanced",
        ],
        "language_keywords": [
            "more effective", "faster results", "need proof",
            "want something better",
        ],
        "beliefs_keywords": [
            "seen claims", "more powerful", "need something better",
            "heard this before",
        ],
        "objections_keywords": [
            "heard this before", "prove it", "skeptical", "doubt",
        ],
    },
    "stage3": {
        "description": "Unique mechanism - HOW it works matters",
        "hook_keywords": [
            "patented", "proprietary", "unique", "formula", "process",
            "method", "mechanism", "technology", "system",
        ],
        "language_keywords": [
            "how does it work", "what's the science", "what makes this different",
            "mechanism", "explain how",
        ],
        "beliefs_keywords": [
            "method matters", "understand", "mechanism", "science",
            "how it works",
        ],
        "objections_keywords": [
            "what's different", "how exactly", "explain", "science",
        ],
    },
    "stage4": {
        "description": "Expanded mechanism - better mechanism + more proof",
        "hook_keywords": [
            "double-blind", "peer-reviewed", "bioavailable", "clinical",
            "study", "research", "evidence", "published",
        ],
        "language_keywords": [
            "show me the research", "studies say", "clinical data",
            "evidence-based", "peer-reviewed",
        ],
        "beliefs_keywords": [
            "tried unique mechanisms", "real proof", "data",
            "evidence-based", "only trust",
        ],
        "objections_keywords": [
            "other products claimed", "peer-reviewed", "evidence",
            "where's the proof", "clinical",
        ],
    },
    "stage5": {
        "description": "Identification - prospect buys based on brand/identity",
        "hook_keywords": [
            "join", "movement", "community", "tribe", "built by",
            "for lifters", "brand", "elite", "represent",
        ],
        "language_keywords": [
            "identify as", "part of", "community", "brand represents",
            "who I am", "my people",
        ],
        "beliefs_keywords": [
            "align with", "values", "community matters", "I am what",
            "identity", "represent",
        ],
        "objections_keywords": [
            "represent me", "who else uses", "community", "belong",
        ],
    },
}


def infer_sophistication(fg_data: dict) -> dict:
    """Classify a focus group into one of 5 market sophistication stages.

    Args:
        fg_data: Focus group data dict with optional keys:
            marketingHooks, languagePatterns, beliefs, objections

    Returns:
        Dict with sophisticationLevel, confidence, and reasoning.
    """
    hooks = [h.lower() for h in (fg_data.get("marketingHooks") or [])]
    language = [lp.lower() for lp in (fg_data.get("languagePatterns") or [])]
    beliefs = [b.lower() for b in (fg_data.get("beliefs") or [])]
    objections = [o.lower() for o in (fg_data.get("objections") or [])]

    hooks_text = " ".join(hooks)
    language_text = " ".join(language)
    beliefs_text = " ".join(beliefs)
    objections_text = " ".join(objections)

    scores = {}
    match_details = {}

    for stage, rules in SOPHISTICATION_RULES.items():
        score = 0
        matches = []

        for kw in rules["hook_keywords"]:
            if kw in hooks_text:
                score += 2  # Hooks are strong signal
                matches.append(f"hook contains '{kw}'")

        for kw in rules["language_keywords"]:
            if kw in language_text:
                score += 1
                matches.append(f"language contains '{kw}'")

        for kw in rules["beliefs_keywords"]:
            if kw in beliefs_text:
                score += 1
                matches.append(f"belief contains '{kw}'")

        for kw in rules["objections_keywords"]:
            if kw in objections_text:
                score += 1
                matches.append(f"objection contains '{kw}'")

        scores[stage] = score
        match_details[stage] = matches

    best_stage = max(scores, key=scores.get)
    best_score = scores[best_stage]

    confidence = "high" if best_score >= 4 else "medium" if best_score >= 2 else "low"

    match_summary = "; ".join(match_details[best_stage][:4]) if match_details[best_stage] else "no strong indicators"

    return {
        "sophisticationLevel": best_stage,
        "confidence": confidence,
        "reasoning": f"Matched {best_score} weighted indicators for {best_stage}: {match_summary}",
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    result = infer_sophistication(data)
    print(json.dumps(result, indent=2))
