#!/usr/bin/env python3
"""Fuzzy match focus group names against existing groups.

Usage:
    python fuzzy_match.py --parsed-name "Fat Loss Seekers" --parsed-nickname "The Scale Watchers" --existing-json existing_groups.json

Output: JSON with matchStatus, matchedId, confidence, reason

Match priority:
    1. Exact name match (case-insensitive) -> enrich_existing (confidence 1.0)
    2. Exact nickname match (case-insensitive) -> enrich_existing (confidence 0.95)
    3. Name substring match -> possible_match (confidence 0.85)
    4. Levenshtein similarity >= 0.8 -> possible_match
    5. Nickname-to-name cross-match >= 0.8 -> possible_match
    6. No match -> create_new (confidence 0.0)
"""
import json
import sys
import argparse


def levenshtein(s1: str, s2: str) -> int:
    """Compute the Levenshtein (edit) distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def match_focus_group(parsed_name: str, parsed_nickname: str, existing_groups: list) -> dict:
    """Match a parsed focus group against a list of existing groups.

    Args:
        parsed_name: The name extracted from the document.
        parsed_nickname: The nickname extracted from the document (may be empty).
        existing_groups: List of dicts with at least '_id' and 'name' keys.
            Optional 'nickname' key.

    Returns:
        Dict with keys: matchStatus, matchedId, confidence, reason.
    """
    parsed_name_lower = parsed_name.strip().lower()
    parsed_nickname_lower = (parsed_nickname or "").strip().lower()

    for existing in existing_groups:
        existing_name_lower = existing["name"].strip().lower()
        existing_nickname_lower = (existing.get("nickname") or "").strip().lower()

        # Priority 1: Exact name match
        if parsed_name_lower == existing_name_lower:
            return {
                "matchStatus": "enrich_existing",
                "matchedId": existing["_id"],
                "confidence": 1.0,
                "reason": "exact_name",
            }

        # Priority 2: Exact nickname match
        if parsed_nickname_lower and parsed_nickname_lower == existing_nickname_lower:
            return {
                "matchStatus": "enrich_existing",
                "matchedId": existing["_id"],
                "confidence": 0.95,
                "reason": "exact_nickname",
            }

        # Priority 3: Name substring
        if parsed_name_lower in existing_name_lower or existing_name_lower in parsed_name_lower:
            return {
                "matchStatus": "possible_match",
                "matchedId": existing["_id"],
                "confidence": 0.85,
                "reason": "name_substring",
            }

        # Priority 4: Levenshtein similarity on names
        max_len = max(len(parsed_name_lower), len(existing_name_lower))
        if max_len > 0:
            similarity = 1.0 - (levenshtein(parsed_name_lower, existing_name_lower) / max_len)
            if similarity >= 0.8:
                return {
                    "matchStatus": "possible_match",
                    "matchedId": existing["_id"],
                    "confidence": round(similarity, 2),
                    "reason": f"fuzzy_{similarity:.2f}",
                }

        # Priority 5: Nickname-to-name cross-match
        if parsed_nickname_lower and existing_name_lower:
            max_len_cross = max(len(parsed_nickname_lower), len(existing_name_lower))
            if max_len_cross > 0:
                nick_sim = 1.0 - (levenshtein(parsed_nickname_lower, existing_name_lower) / max_len_cross)
                if nick_sim >= 0.8:
                    return {
                        "matchStatus": "possible_match",
                        "matchedId": existing["_id"],
                        "confidence": round(nick_sim, 2),
                        "reason": f"nick_to_name_{nick_sim:.2f}",
                    }

    return {
        "matchStatus": "create_new",
        "matchedId": None,
        "confidence": 0.0,
        "reason": "no_match",
    }


def main():
    parser = argparse.ArgumentParser(description="Fuzzy match focus group names")
    parser.add_argument("--parsed-name", required=True, help="Name from parsed document")
    parser.add_argument("--parsed-nickname", default="", help="Nickname from parsed document")
    parser.add_argument("--existing-json", required=True, help="Path to JSON file with existing groups")
    args = parser.parse_args()

    with open(args.existing_json) as f:
        existing = json.load(f)

    result = match_focus_group(args.parsed_name, args.parsed_nickname, existing)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
