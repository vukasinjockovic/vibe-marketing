"""Tests for infer_sophistication.py -- Market sophistication level inference from focus group data."""
import json
import sys
import os
import pytest

# Add scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "audience-enrichment-procedures", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


class TestInferSophistication:
    """Unit tests for the infer_sophistication function."""

    def test_returns_required_fields(self):
        """Output must contain sophisticationLevel, confidence, reasoning."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": ["Get fit fast"],
            "languagePatterns": ["simple and direct"],
            "beliefs": ["I want results"],
            "objections": [],
        })
        assert "sophisticationLevel" in result
        assert "confidence" in result
        assert "reasoning" in result

    def test_sophistication_level_is_valid(self):
        """Level must be one of stage1-stage5."""
        from infer_sophistication import infer_sophistication
        valid_levels = {"stage1", "stage2", "stage3", "stage4", "stage5"}
        result = infer_sophistication({
            "marketingHooks": ["Best product ever"],
            "languagePatterns": [],
            "beliefs": [],
            "objections": [],
        })
        assert result["sophisticationLevel"] in valid_levels

    def test_confidence_is_valid(self):
        """Confidence must be high, medium, or low."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": ["test"],
            "languagePatterns": [],
            "beliefs": [],
            "objections": [],
        })
        assert result["confidence"] in {"high", "medium", "low"}

    def test_stage1_simple_claims(self):
        """Market hearing claims for first time -> stage1."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": [
                "Lose 10 pounds in 30 days",
                "Get ripped fast",
                "The #1 supplement",
            ],
            "languagePatterns": [
                "never tried supplements before",
                "first time looking into this",
            ],
            "beliefs": [
                "I just need to find the right product",
                "There must be a simple solution",
            ],
            "objections": [],
        })
        assert result["sophisticationLevel"] == "stage1"

    def test_stage2_expanded_claims(self):
        """Market needs bigger/better claims -> stage2."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": [
                "Lose 20 pounds faster than ever",
                "More effective than leading brands",
                "Clinically proven results",
            ],
            "languagePatterns": [
                "looking for something more effective",
                "want faster results",
                "need proof it works",
            ],
            "beliefs": [
                "I've seen claims before",
                "Need something more powerful",
            ],
            "objections": ["heard this before", "prove it"],
        })
        assert result["sophisticationLevel"] == "stage2"

    def test_stage3_unique_mechanism(self):
        """Market wants to know HOW -> stage3."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": [
                "Our patented formula uses thermogenic cycling",
                "Proprietary blend targets stubborn fat",
                "How our unique process works differently",
            ],
            "languagePatterns": [
                "how does it work",
                "what's the science behind it",
                "what makes this different",
            ],
            "beliefs": [
                "The method matters more than the promise",
                "I want to understand the mechanism",
            ],
            "objections": ["what's different about this", "how exactly does it work"],
        })
        assert result["sophisticationLevel"] == "stage3"

    def test_stage4_expanded_mechanism(self):
        """Market needs better mechanism + proof -> stage4."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": [
                "Double-blind study proves our mechanism",
                "3x more bioavailable than standard",
                "Peer-reviewed research backs every ingredient",
            ],
            "languagePatterns": [
                "show me the research",
                "what do the studies say",
                "I need to see clinical data",
            ],
            "beliefs": [
                "I've tried unique mechanisms before",
                "Need to see real proof and data",
                "Only trust evidence-based approaches",
            ],
            "objections": [
                "other products claimed unique mechanisms too",
                "where's the peer-reviewed evidence",
            ],
        })
        assert result["sophisticationLevel"] == "stage4"

    def test_stage5_identification(self):
        """Market buys based on identity/brand -> stage5."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": [
                "Join the movement of conscious athletes",
                "Built by lifters, for lifters",
                "The brand elite athletes trust",
            ],
            "languagePatterns": [
                "I identify as a serious athlete",
                "part of the community",
                "this brand represents who I am",
            ],
            "beliefs": [
                "I buy brands that align with my values",
                "Community matters more than features",
                "I am what I consume",
            ],
            "objections": [
                "does this brand represent me",
                "who else uses this",
            ],
        })
        assert result["sophisticationLevel"] == "stage5"

    def test_empty_input_does_not_crash(self):
        """Empty input should return a valid result."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({})
        assert "sophisticationLevel" in result
        assert result["confidence"] in {"high", "medium", "low"}

    def test_none_fields_handled(self):
        """None values for fields should not crash."""
        from infer_sophistication import infer_sophistication
        result = infer_sophistication({
            "marketingHooks": None,
            "languagePatterns": None,
            "beliefs": None,
            "objections": None,
        })
        assert "sophisticationLevel" in result
