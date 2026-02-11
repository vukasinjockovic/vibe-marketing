"""Tests for fuzzy_match.py — Levenshtein-based focus group matching."""
import json
import sys
import os
import pytest

# Add scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "audience-analysis-procedures", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


class TestLevenshtein:
    """Unit tests for the Levenshtein distance function."""

    def test_identical_strings(self):
        from fuzzy_match import levenshtein
        assert levenshtein("hello", "hello") == 0

    def test_empty_strings(self):
        from fuzzy_match import levenshtein
        assert levenshtein("", "") == 0

    def test_one_empty(self):
        from fuzzy_match import levenshtein
        assert levenshtein("abc", "") == 3
        assert levenshtein("", "abc") == 3

    def test_single_substitution(self):
        from fuzzy_match import levenshtein
        assert levenshtein("cat", "bat") == 1

    def test_single_insertion(self):
        from fuzzy_match import levenshtein
        assert levenshtein("cat", "cats") == 1

    def test_single_deletion(self):
        from fuzzy_match import levenshtein
        assert levenshtein("cats", "cat") == 1

    def test_completely_different(self):
        from fuzzy_match import levenshtein
        assert levenshtein("abc", "xyz") == 3

    def test_case_sensitive(self):
        from fuzzy_match import levenshtein
        assert levenshtein("Hello", "hello") == 1


class TestMatchFocusGroup:
    """Tests for the match_focus_group function."""

    @pytest.fixture
    def existing_groups(self):
        return [
            {"_id": "fg_001", "name": "Fat Loss Seekers", "nickname": "The Scale Watchers"},
            {"_id": "fg_002", "name": "Muscle Builders / Hardgainers", "nickname": "The Ectomorph Strugglers"},
            {"_id": "fg_003", "name": "Body Recomposition Seekers", "nickname": "The 'Both' Demanders"},
            {"_id": "fg_004", "name": "Time-Crunched Professionals", "nickname": "The Efficiency Optimizers"},
        ]

    def test_exact_name_match(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("Fat Loss Seekers", "", existing_groups)
        assert result["matchStatus"] == "enrich_existing"
        assert result["matchedId"] == "fg_001"
        assert result["confidence"] == 1.0
        assert result["reason"] == "exact_name"

    def test_exact_name_match_case_insensitive(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("fat loss seekers", "", existing_groups)
        assert result["matchStatus"] == "enrich_existing"
        assert result["matchedId"] == "fg_001"
        assert result["confidence"] == 1.0

    def test_exact_nickname_match(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("Unknown Group Name", "The Scale Watchers", existing_groups)
        assert result["matchStatus"] == "enrich_existing"
        assert result["matchedId"] == "fg_001"
        assert result["confidence"] == 0.95
        assert result["reason"] == "exact_nickname"

    def test_name_substring_match(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("Muscle Builders", "", existing_groups)
        assert result["matchStatus"] == "possible_match"
        assert result["matchedId"] == "fg_002"
        assert result["confidence"] == 0.85
        assert result["reason"] == "name_substring"

    def test_fuzzy_match_high_similarity(self, existing_groups):
        from fuzzy_match import match_focus_group
        # "Fat Loss Seeker" vs "Fat Loss Seekers" — 1 char difference
        result = match_focus_group("Fat Loss Seeker", "", existing_groups)
        # Could match as substring or fuzzy — either way should match fg_001
        assert result["matchedId"] == "fg_001"
        assert result["matchStatus"] in ("possible_match", "enrich_existing")

    def test_no_match_returns_create_new(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("Completely Unrelated Group", "", existing_groups)
        assert result["matchStatus"] == "create_new"
        assert result["matchedId"] is None
        assert result["confidence"] == 0.0
        assert result["reason"] == "no_match"

    def test_empty_existing_groups(self):
        from fuzzy_match import match_focus_group
        result = match_focus_group("Fat Loss Seekers", "The Scale Watchers", [])
        assert result["matchStatus"] == "create_new"
        assert result["matchedId"] is None

    def test_nickname_to_name_cross_match(self, existing_groups):
        from fuzzy_match import match_focus_group
        # Parsed nickname matches an existing name closely
        result = match_focus_group("Totally Different Name", "Fat Loss Seekers", existing_groups)
        # The nickname "Fat Loss Seekers" should match existing name "Fat Loss Seekers"
        assert result["matchedId"] == "fg_001"
        assert result["matchStatus"] in ("possible_match", "enrich_existing")

    def test_whitespace_handling(self, existing_groups):
        from fuzzy_match import match_focus_group
        result = match_focus_group("  Fat Loss Seekers  ", "", existing_groups)
        assert result["matchStatus"] == "enrich_existing"
        assert result["matchedId"] == "fg_001"

    def test_no_nickname_field_in_existing(self):
        from fuzzy_match import match_focus_group
        existing = [{"_id": "fg_099", "name": "Some Group"}]
        result = match_focus_group("Some Group", "", existing)
        assert result["matchStatus"] == "enrich_existing"
        assert result["matchedId"] == "fg_099"
