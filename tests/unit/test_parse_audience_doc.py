"""Tests for parse_audience_doc.py — document parsing and field extraction."""
import json
import sys
import os
import tempfile
import pytest

SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "audience-analysis-procedures", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


# ── Fixture: Minimal focus group markdown ──

SINGLE_GROUP_MD = """
## Group 1: "Fat Loss Seekers" (The Scale Watchers)
**Category:** Physical Transformation Desires
**Overview:** Individuals whose primary goal is reducing body fat.

### Demographics
- **Age Range:** 25-55, peaks at 35-45
- **Gender:** 60% female, 40% male
- **Income:** Middle to upper-middle class
- **Lifestyle:** Sedentary to moderately active
- **Triggers:** Photos of themselves, upcoming events

### Psychographics
- **Values:** Health, appearance, self-control, discipline
- **Beliefs:** Weight loss = willpower, calories in/out is simple math
- **Lifestyle:** Busy professionals, parents
- **Identity:** See themselves as someone who 'used to be fit'

### Core Desires
- See visible changes in the mirror and photos
- Fit into old clothes or buy smaller sizes
- Feel comfortable in a swimsuit

### Pain Points
- Scale won't budge despite 'eating healthy'
- Losing the same 10 pounds over and over
- Confused by conflicting diet advice

### Fears & Anxieties
- Being stuck at this weight forever
- Health complications from excess weight

### Beliefs & Worldview
- Some people are just naturally thin
- My metabolism is broken/slow
- I have no willpower around food

### Common Objections
- "I've tried everything already"
- "I don't have time to meal prep"
- "Healthy food is too expensive"

### Emotional Triggers
- Seeing unflattering photos of themselves
- Clothes feeling tight
- Comparing themselves to old photos

### Language Patterns
- "I want to lose X pounds"
- "Nothing I try works"

### Ebook Positioning Angles
- "The Last Fat Loss Guide You'll Ever Need"
- "Why Your Diet Isn't Working (And What Will)"

### Marketing Hooks & Headlines
- "Still counting calories and still not losing weight?"
- "What if everything you know about fat loss is wrong?"

### Transformation Promise
From frustrated dieter constantly battling the scale to confident individual who maintains their ideal weight effortlessly.
"""

TWO_GROUPS_MD = """
**PHYSICAL TRANSFORMATION DESIRES**

## Group 1: "Fat Loss Seekers" (The Scale Watchers)
**Category:** Physical Transformation Desires
**Overview:** Individuals whose primary goal is reducing body fat.

### Demographics
- **Age Range:** 25-55
- **Gender:** 60% female, 40% male
- **Income:** Middle class
- **Lifestyle:** Sedentary
- **Triggers:** Photos of themselves

### Core Desires
- See visible changes in the mirror
- Fit into old clothes

### Pain Points
- Scale won't budge
- Losing the same 10 pounds

### Transformation Promise
From frustrated dieter to confident individual.

## Group 2: "Muscle Builders / Hardgainers" (The Ectomorph Strugglers)
**Category:** Physical Transformation Desires
**Overview:** Individuals who struggle to gain muscle mass.

### Demographics
- **Age Range:** 18-35
- **Gender:** 85% male, 15% female
- **Income:** Entry-level to mid-career
- **Lifestyle:** Active, gym-goers
- **Triggers:** Being called skinny

### Core Desires
- Look like they actually lift weights
- Fill out shirts and clothes

### Pain Points
- Training for months with minimal visible gains
- Feeling small compared to others

### Transformation Promise
From frustrated skinny person to confident muscular individual.
"""

MINIMAL_GROUP_MD = """
## Group 5: "Plateau Breakers" (The Stuck Sufferers)
**Category:** Physical Transformation Desires
**Overview:** People stuck at a training plateau.

### Core Desires
- Break through their current plateau
"""

# Alternate format: numbered headings without quotes
ALT_FORMAT_MD = """
# 1. Fat Loss Seekers - "The Scale Watchers"
Category: Physical Transformation Desires
Overview: Individuals whose primary goal is reducing body fat.

## Demographics
- Age Range: 25-55
- Gender: 60% female

## Core Desires
- See visible changes in the mirror

## Pain Points
- Scale won't budge

## Transformation Promise
From frustrated dieter to confident individual.
"""

# Format with table-style demographics (like the actual fitness doc)
TABLE_FORMAT_MD = """
**FOCUS GROUP #1**

**Fat Loss Seekers**

*"The Scale Watchers"*

**OVERVIEW**

Individuals whose primary goal is reducing body fat and seeing lower
numbers on the scale.

**DEMOGRAPHICS**

  ------------------ ----------------------------------------------------
  **Age**            25-55, peaks at 35-45

  **Gender**         60% female, 40% male

  **Income**         Middle to upper-middle class

  **Lifestyle**      Sedentary to moderately active, often desk jobs

  **Triggers**       Photos of themselves, upcoming events, doctor
                     visits, clothes not fitting
  ------------------ ----------------------------------------------------

**PSYCHOGRAPHICS**

  ------------------ ----------------------------------------------------
  **Values**         Health, appearance, self-control, discipline

  **Beliefs**        Weight loss = willpower, calories in/out is simple
                     math, cardio burns fat

  **Lifestyle**      Busy professionals, parents, people who've 'let
                     themselves go'

  **Identity**       See themselves as someone who 'used to be fit' or
                     'has always struggled with weight'
  ------------------ ----------------------------------------------------

**CORE DESIRES (What They Want)**

- See visible changes in the mirror and photos

- Fit into old clothes or buy smaller sizes

**PAIN POINTS (What Frustrates Them)**

- Scale won't budge despite 'eating healthy'

- Losing the same 10 pounds over and over

**FEARS & ANXIETIES**

- Being stuck at this weight forever

**BELIEFS & WORLDVIEW**

- Some people are just naturally thin

- My metabolism is broken/slow

**COMMON OBJECTIONS (Why They Hesitate)**

*"I've tried everything already"*

*"I don't have time to meal prep"*

**EMOTIONAL TRIGGERS (What Activates Buying)**

- Seeing unflattering photos of themselves

**LANGUAGE PATTERNS (Exact Phrases They Use)**

*"I want to lose X pounds"*

*"Nothing I try works"*

**EBOOK POSITIONING ANGLES**

**1. "The Last Fat Loss Guide You'll Ever Need"**

**MARKETING HOOKS & HEADLINES**

- "Still counting calories and still not losing weight?"

**TRANSFORMATION PROMISE**

**From frustrated dieter constantly battling the scale -> confident
individual who understands their body**
"""


class TestSplitSections:
    """Test that the parser correctly identifies section boundaries."""

    def test_splits_two_groups(self):
        from parse_audience_doc import split_into_groups
        groups = split_into_groups(TWO_GROUPS_MD)
        assert len(groups) == 2

    def test_splits_single_group(self):
        from parse_audience_doc import split_into_groups
        groups = split_into_groups(SINGLE_GROUP_MD)
        assert len(groups) == 1

    def test_handles_table_format(self):
        from parse_audience_doc import split_into_groups
        groups = split_into_groups(TABLE_FORMAT_MD)
        assert len(groups) >= 1

    def test_empty_input(self):
        from parse_audience_doc import split_into_groups
        groups = split_into_groups("")
        assert len(groups) == 0

    def test_no_groups_in_text(self):
        from parse_audience_doc import split_into_groups
        groups = split_into_groups("Just some random text without focus groups.")
        assert len(groups) == 0


class TestExtractGroupName:
    """Test name extraction from various heading formats."""

    def test_extract_name_standard_format(self):
        from parse_audience_doc import extract_name_and_nickname
        name, nickname = extract_name_and_nickname(
            '## Group 1: "Fat Loss Seekers" (The Scale Watchers)'
        )
        assert name == "Fat Loss Seekers"
        assert nickname == "The Scale Watchers"

    def test_extract_name_focus_group_format(self):
        from parse_audience_doc import extract_name_and_nickname
        heading = '**Fat Loss Seekers**'
        subheading = '*"The Scale Watchers"*'
        name, nickname = extract_name_and_nickname(heading, subheading)
        assert name == "Fat Loss Seekers"
        assert nickname == "The Scale Watchers"

    def test_extract_name_without_nickname(self):
        from parse_audience_doc import extract_name_and_nickname
        name, nickname = extract_name_and_nickname("## Fat Loss Seekers")
        assert name == "Fat Loss Seekers"
        assert nickname is None or nickname == ""

    def test_extract_name_numbered_format(self):
        from parse_audience_doc import extract_name_and_nickname
        name, nickname = extract_name_and_nickname(
            '# 1. Fat Loss Seekers - "The Scale Watchers"'
        )
        assert name == "Fat Loss Seekers"
        assert "Scale Watchers" in (nickname or "")


class TestExtractFields:
    """Test that structured fields are correctly extracted from group text."""

    @pytest.fixture
    def parsed_group(self):
        from parse_audience_doc import parse_single_group
        return parse_single_group(SINGLE_GROUP_MD.strip())

    def test_name_extracted(self, parsed_group):
        assert parsed_group["name"] == "Fat Loss Seekers"

    def test_nickname_extracted(self, parsed_group):
        assert parsed_group["nickname"] == "The Scale Watchers"

    def test_category_extracted(self, parsed_group):
        assert parsed_group["category"] == "Physical Transformation Desires"

    def test_overview_extracted(self, parsed_group):
        assert "reducing body fat" in parsed_group["overview"]

    def test_demographics_extracted(self, parsed_group):
        demo = parsed_group["demographics"]
        assert demo is not None
        assert "25-55" in demo["ageRange"]
        assert "female" in demo["gender"].lower() or "male" in demo["gender"].lower()
        assert demo["income"] is not None
        assert demo["lifestyle"] is not None
        assert isinstance(demo["triggers"], list)
        assert len(demo["triggers"]) > 0

    def test_psychographics_extracted(self, parsed_group):
        psych = parsed_group["psychographics"]
        assert psych is not None
        assert isinstance(psych["values"], list)
        assert len(psych["values"]) > 0
        assert isinstance(psych["beliefs"], list)
        assert psych["lifestyle"] is not None
        assert psych["identity"] is not None

    def test_core_desires_extracted(self, parsed_group):
        assert isinstance(parsed_group["coreDesires"], list)
        assert len(parsed_group["coreDesires"]) >= 2

    def test_pain_points_extracted(self, parsed_group):
        assert isinstance(parsed_group["painPoints"], list)
        assert len(parsed_group["painPoints"]) >= 2

    def test_fears_extracted(self, parsed_group):
        assert isinstance(parsed_group["fears"], list)
        assert len(parsed_group["fears"]) >= 1

    def test_beliefs_extracted(self, parsed_group):
        assert isinstance(parsed_group["beliefs"], list)
        assert len(parsed_group["beliefs"]) >= 1

    def test_objections_extracted(self, parsed_group):
        assert isinstance(parsed_group["objections"], list)
        assert len(parsed_group["objections"]) >= 1

    def test_emotional_triggers_extracted(self, parsed_group):
        assert isinstance(parsed_group["emotionalTriggers"], list)
        assert len(parsed_group["emotionalTriggers"]) >= 1

    def test_language_patterns_extracted(self, parsed_group):
        assert isinstance(parsed_group["languagePatterns"], list)
        assert len(parsed_group["languagePatterns"]) >= 1

    def test_ebook_angles_extracted(self, parsed_group):
        assert isinstance(parsed_group["ebookAngles"], list)
        assert len(parsed_group["ebookAngles"]) >= 1

    def test_marketing_hooks_extracted(self, parsed_group):
        assert isinstance(parsed_group["marketingHooks"], list)
        assert len(parsed_group["marketingHooks"]) >= 1

    def test_transformation_promise_extracted(self, parsed_group):
        assert parsed_group["transformationPromise"] is not None
        assert len(parsed_group["transformationPromise"]) > 10


class TestCompletenessScoring:
    """Test the completeness scoring system."""

    def test_full_group_high_score(self):
        from parse_audience_doc import score_completeness
        full_group = {
            "name": "Test",
            "nickname": "Test Nick",
            "category": "Test Cat",
            "overview": "An overview",
            "demographics": {"ageRange": "25-35", "gender": "50/50", "income": "Mid", "lifestyle": "Active", "triggers": ["x"]},
            "psychographics": {"values": ["x"], "beliefs": ["x"], "lifestyle": "Active", "identity": "Fit"},
            "coreDesires": ["desire1"],
            "painPoints": ["pain1"],
            "fears": ["fear1"],
            "beliefs": ["belief1"],
            "objections": ["objection1"],
            "emotionalTriggers": ["trigger1"],
            "languagePatterns": ["pattern1"],
            "ebookAngles": ["angle1"],
            "marketingHooks": ["hook1"],
            "transformationPromise": "From X to Y",
            "awarenessStage": "problem_aware",
            "sophisticationLevel": "stage2",
            "contentPreferences": {"preferredFormats": ["blog"]},
            "influenceSources": {"trustedVoices": ["influencer1"]},
            "purchaseBehavior": {"buyingTriggers": ["trigger"]},
            "competitorContext": {"currentSolutions": ["solution"]},
            "communicationStyle": {"formalityLevel": "casual"},
            "seasonalContext": {"peakInterestPeriods": ["January"]},
            "negativeTriggers": {"dealBreakers": ["spam"]},
            "awarenessSignals": {"beliefsSignal": "signal"},
        }
        score, missing = score_completeness(full_group)
        assert score >= 90.0
        assert len(missing) == 0

    def test_minimal_group_low_score(self):
        from parse_audience_doc import score_completeness
        minimal_group = {
            "name": "Test",
            "coreDesires": ["desire1"],
        }
        score, missing = score_completeness(minimal_group)
        assert score < 50.0
        assert len(missing) > 5

    def test_missing_fields_listed(self):
        from parse_audience_doc import score_completeness
        group = {
            "name": "Test",
            "awarenessStage": "problem_aware",
        }
        score, missing = score_completeness(group)
        assert "sophisticationLevel" in missing
        assert "purchaseBehavior" in missing

    def test_score_is_percentage(self):
        from parse_audience_doc import score_completeness
        group = {"name": "Test"}
        score, _ = score_completeness(group)
        assert 0.0 <= score <= 100.0


class TestParseDocument:
    """Integration tests for full document parsing."""

    def test_parse_two_groups(self):
        from parse_audience_doc import parse_document
        result = parse_document(TWO_GROUPS_MD)
        assert len(result) == 2
        assert result[0]["name"] == "Fat Loss Seekers"
        assert result[1]["name"] == "Muscle Builders / Hardgainers"

    def test_parse_includes_completeness(self):
        from parse_audience_doc import parse_document
        result = parse_document(SINGLE_GROUP_MD)
        assert len(result) == 1
        group = result[0]
        assert "completenessScore" in group
        assert "missingFields" in group
        assert isinstance(group["completenessScore"], (int, float))
        assert isinstance(group["missingFields"], list)

    def test_parse_minimal_group(self):
        from parse_audience_doc import parse_document
        result = parse_document(MINIMAL_GROUP_MD)
        assert len(result) == 1
        assert result[0]["name"] == "Plateau Breakers"
        assert result[0]["completenessScore"] < 50.0

    def test_parse_empty_document(self):
        from parse_audience_doc import parse_document
        result = parse_document("")
        assert result == []

    def test_output_is_json_serializable(self):
        from parse_audience_doc import parse_document
        result = parse_document(SINGLE_GROUP_MD)
        # Should not raise
        json.dumps(result)

    def test_number_field_extracted(self):
        from parse_audience_doc import parse_document
        result = parse_document(SINGLE_GROUP_MD)
        assert result[0].get("number") == 1

    def test_parse_table_format(self):
        """Test parsing the actual fitness doc format with table-style demographics."""
        from parse_audience_doc import parse_document
        result = parse_document(TABLE_FORMAT_MD)
        assert len(result) >= 1
        group = result[0]
        assert group["name"] == "Fat Loss Seekers"
        assert group["nickname"] == "The Scale Watchers"


class TestFileIO:
    """Test that the script reads files and outputs JSON correctly."""

    def test_parse_file(self):
        from parse_audience_doc import parse_file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SINGLE_GROUP_MD)
            f.flush()
            result = parse_file(f.name)
        os.unlink(f.name)
        assert len(result) == 1
        assert result[0]["name"] == "Fat Loss Seekers"

    def test_parse_file_not_found(self):
        from parse_audience_doc import parse_file
        with pytest.raises(FileNotFoundError):
            parse_file("/nonexistent/file.md")
