"""Tests for infer_awareness.py -- Schwartz awareness stage inference from focus group data."""
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


class TestInferAwareness:
    """Unit tests for the infer_awareness function."""

    def test_returns_required_fields(self):
        """Output must contain awarenessStage, awarenessConfidence, awarenessStageSource, awarenessSignals, reasoning."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["I'm struggling to lose weight"],
            "objections": ["Nothing works for me"],
            "languagePatterns": ["frustrated with diets"],
            "painPoints": ["can't stick to a plan"],
        })
        assert "awarenessStage" in result
        assert "awarenessConfidence" in result
        assert "awarenessStageSource" in result
        assert "awarenessSignals" in result
        assert "reasoning" in result

    def test_awareness_stage_is_valid_value(self):
        """Stage must be one of the 5 Schwartz stages."""
        from infer_awareness import infer_awareness
        valid_stages = {"unaware", "problem_aware", "solution_aware", "product_aware", "most_aware"}
        result = infer_awareness({
            "beliefs": ["I need a better protein powder"],
            "objections": ["price is too high"],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessStage"] in valid_stages

    def test_confidence_is_valid_value(self):
        """Confidence must be high, medium, or low."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["struggling"],
            "objections": [],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessConfidence"] in {"high", "medium", "low"}

    def test_source_is_auto(self):
        """Source should always be 'auto' for inferred results."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["test"],
            "objections": [],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessStageSource"] == "auto"

    def test_problem_aware_detection(self):
        """Focus group with frustration/stuck language -> problem_aware."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "I'm struggling with my weight",
                "I can't figure out what to eat",
                "I feel stuck and frustrated",
            ],
            "objections": [
                "Nothing works for me",
                "I've tried everything already",
            ],
            "languagePatterns": [
                "why can't I lose weight",
                "so frustrated with diets",
            ],
            "painPoints": [
                "stuck at a plateau",
                "frustrated with lack of progress",
            ],
        })
        assert result["awarenessStage"] == "problem_aware"

    def test_most_aware_detection(self):
        """Focus group comparing products/prices -> most_aware."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "This is the best protein on the market",
                "I compared to Optimum Nutrition",
                "Worth it if there's a coupon",
            ],
            "objections": [
                "The price is higher than alternatives",
                "Is it cheaper on Amazon?",
                "Too costly compared to other brands",
            ],
            "languagePatterns": [
                "deal seeker",
                "compares ingredients",
            ],
            "painPoints": [],
        })
        assert result["awarenessStage"] == "most_aware"

    def test_solution_aware_detection(self):
        """Focus group researching options -> solution_aware."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "I know I should start lifting",
                "I need to figure out the right program",
                "I've heard about starting strength",
            ],
            "objections": [
                "It seems too complicated to start",
                "I'm overwhelmed by all the options",
                "Takes too much time",
            ],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessStage"] == "solution_aware"

    def test_product_aware_detection(self):
        """Focus group that has tried similar products -> product_aware."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "I tried MyFitnessPal but it didn't work",
                "Looking for a better option than Noom",
                "Need something different from what's out there",
            ],
            "objections": [
                "How is this different from what I've tried",
                "Can I trust this brand",
                "Is there a guarantee",
            ],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessStage"] == "product_aware"

    def test_unaware_detection(self):
        """Focus group content/no urgency -> unaware."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "My health is fine for now",
                "Fitness doesn't matter that much",
                "I'll worry about it someday",
            ],
            "objections": [
                "I don't need a gym membership",
                "I'm happy with how things are",
            ],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessStage"] == "unaware"

    def test_high_confidence_with_many_signals(self):
        """3+ matching indicators should yield high confidence."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": [
                "I'm struggling so much",
                "I can't lose weight",
                "I feel stuck in a rut",
            ],
            "objections": [
                "Nothing works at all",
                "I've tried everything possible",
                "It's probably genetics",
            ],
            "languagePatterns": [
                "why is this so hard",
                "frustrated beyond belief",
            ],
            "painPoints": [
                "stuck",
                "frustrated",
            ],
        })
        assert result["awarenessConfidence"] == "high"

    def test_low_confidence_with_few_signals(self):
        """Only 1 matching indicator should yield low confidence."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["something generic"],
            "objections": ["later"],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert result["awarenessConfidence"] == "low"

    def test_empty_input_does_not_crash(self):
        """Empty/missing fields should produce a result without error."""
        from infer_awareness import infer_awareness
        result = infer_awareness({})
        assert "awarenessStage" in result
        assert result["awarenessConfidence"] in {"high", "medium", "low"}

    def test_missing_fields_gracefully_handled(self):
        """None values for fields should be handled gracefully."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": None,
            "objections": None,
            "languagePatterns": None,
            "painPoints": None,
        })
        assert "awarenessStage" in result

    def test_signals_structure(self):
        """awarenessSignals should have beliefsSignal, objectionsSignal, languageSignal keys."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["struggling to keep up"],
            "objections": ["nothing works"],
            "languagePatterns": ["frustrated with everything"],
            "painPoints": ["stuck in a rut"],
        })
        signals = result["awarenessSignals"]
        assert "beliefsSignal" in signals
        assert "objectionsSignal" in signals
        assert "languageSignal" in signals

    def test_reasoning_is_nonempty_string(self):
        """Reasoning should explain the classification."""
        from infer_awareness import infer_awareness
        result = infer_awareness({
            "beliefs": ["I'm stuck"],
            "objections": ["nothing works"],
            "languagePatterns": [],
            "painPoints": [],
        })
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0
