"""Tests for infer_purchase_behavior.py -- Purchase behavior inference from focus group data."""
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


class TestInferPurchaseBehavior:
    """Unit tests for the infer_purchase_behavior function."""

    def test_returns_required_fields(self):
        """Output must contain purchaseBehavior with expected sub-fields."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "25-34",
                "gender": "male",
                "income": "$50k-$75k",
                "lifestyle": "active",
                "triggers": ["new year resolution"],
            },
            "painPoints": ["can't afford premium gyms"],
            "objections": ["too expensive"],
            "emotionalTriggers": ["fear of missing out"],
            "psychographics": {
                "values": ["health"],
                "beliefs": ["fitness is important"],
                "lifestyle": "active",
                "identity": "aspiring athlete",
            },
        })
        assert "purchaseBehavior" in result
        pb = result["purchaseBehavior"]
        assert "buyingTriggers" in pb
        assert "priceRange" in pb
        assert "decisionProcess" in pb
        assert "objectionHistory" in pb

    def test_confidence_is_valid(self):
        """Confidence must be high, medium, or low."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "25-34",
                "gender": "female",
                "income": "$75k-$100k",
                "lifestyle": "busy professional",
                "triggers": ["summer body"],
            },
            "painPoints": ["no time"],
            "objections": [],
            "emotionalTriggers": [],
            "psychographics": None,
        })
        assert result["confidence"] in {"high", "medium", "low"}

    def test_reasoning_present(self):
        """Reasoning string should be present and non-empty."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "35-44",
                "gender": "male",
                "income": "$100k+",
                "lifestyle": "executive",
                "triggers": ["health scare"],
            },
            "painPoints": ["declining energy"],
            "objections": ["skeptical of supplements"],
            "emotionalTriggers": ["fear of aging"],
            "psychographics": {
                "values": ["success", "performance"],
                "beliefs": ["you get what you pay for"],
                "lifestyle": "high-achiever",
                "identity": "executive",
            },
        })
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    def test_high_income_maps_to_premium_price_range(self):
        """High income demographics should infer premium/high price range."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "35-44",
                "gender": "male",
                "income": "$100k+",
                "lifestyle": "executive",
                "triggers": [],
            },
            "painPoints": [],
            "objections": [],
            "emotionalTriggers": [],
            "psychographics": None,
        })
        price = result["purchaseBehavior"]["priceRange"].lower()
        assert "premium" in price or "high" in price

    def test_low_income_maps_to_budget_price_range(self):
        """Low income demographics should infer budget/low price range."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "18-24",
                "gender": "any",
                "income": "under $25k",
                "lifestyle": "student",
                "triggers": [],
            },
            "painPoints": [],
            "objections": [],
            "emotionalTriggers": [],
            "psychographics": None,
        })
        price = result["purchaseBehavior"]["priceRange"].lower()
        assert "budget" in price or "low" in price or "value" in price

    def test_objections_become_objection_history(self):
        """Objections from input should map to objectionHistory."""
        from infer_purchase_behavior import infer_purchase_behavior
        input_objections = ["too expensive", "doesn't ship internationally", "bad reviews"]
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "25-34",
                "gender": "female",
                "income": "$50k-$75k",
                "lifestyle": "active",
                "triggers": [],
            },
            "painPoints": [],
            "objections": input_objections,
            "emotionalTriggers": [],
            "psychographics": None,
        })
        obj_history = result["purchaseBehavior"]["objectionHistory"]
        assert isinstance(obj_history, list)
        assert len(obj_history) > 0

    def test_emotional_triggers_become_buying_triggers(self):
        """Emotional triggers + pain points should map to buyingTriggers."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "30-40",
                "gender": "female",
                "income": "$50k-$75k",
                "lifestyle": "mom",
                "triggers": ["back to school"],
            },
            "painPoints": ["low energy", "post-pregnancy weight"],
            "objections": [],
            "emotionalTriggers": ["fear of judgment", "desire to be a role model"],
            "psychographics": {
                "values": ["family", "health"],
                "beliefs": ["moms should be strong"],
                "lifestyle": "busy parent",
                "identity": "dedicated mom",
            },
        })
        triggers = result["purchaseBehavior"]["buyingTriggers"]
        assert isinstance(triggers, list)
        assert len(triggers) > 0

    def test_research_heavy_psychographics_infer_research_decision(self):
        """Analytical/research psychographics -> research-heavy decision process."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": {
                "ageRange": "30-45",
                "gender": "male",
                "income": "$75k-$100k",
                "lifestyle": "analytical",
                "triggers": [],
            },
            "painPoints": [],
            "objections": ["need more data", "show me studies"],
            "emotionalTriggers": [],
            "psychographics": {
                "values": ["evidence", "research", "data"],
                "beliefs": ["decisions should be data-driven"],
                "lifestyle": "methodical",
                "identity": "rational thinker",
            },
        })
        decision = result["purchaseBehavior"]["decisionProcess"].lower()
        assert "research" in decision or "analytic" in decision or "deliberate" in decision

    def test_empty_input_does_not_crash(self):
        """Empty input should produce a valid result without error."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({})
        assert "purchaseBehavior" in result

    def test_none_fields_handled(self):
        """None values should not cause crashes."""
        from infer_purchase_behavior import infer_purchase_behavior
        result = infer_purchase_behavior({
            "demographics": None,
            "painPoints": None,
            "objections": None,
            "emotionalTriggers": None,
            "psychographics": None,
        })
        assert "purchaseBehavior" in result
