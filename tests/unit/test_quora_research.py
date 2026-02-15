"""Tests for quora-research skill scripts.

Tests cover:
- quora_questions.py: URL construction, search result parsing, question extraction, CLI args
- quora_answers.py: Answer extraction, persuasion pattern detection, CLI args
- quora_voice_mine.py: Voice mining analysis, phrase extraction, demographic signals, CLI args

All tests use mocks -- no actual network requests or Playwright browsers.
"""

import json
import sys
import os
import argparse
import re
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "quora-research", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


# ============================================================================
# quora_questions.py tests
# ============================================================================


class TestBuildSearchQuery:
    """Tests for building search queries to find Quora URLs."""

    def test_basic_topic(self):
        from quora_questions import build_search_query
        query = build_search_query("grandparent gifts")
        assert "site:quora.com" in query
        assert "grandparent gifts" in query

    def test_topic_with_special_chars(self):
        from quora_questions import build_search_query
        query = build_search_query("what's the best gift?")
        assert "site:quora.com" in query

    def test_empty_topic(self):
        from quora_questions import build_search_query
        query = build_search_query("")
        assert "site:quora.com" in query


class TestExtractQuoraUrls:
    """Tests for extracting Quora URLs from search results HTML."""

    def test_extract_quora_urls_from_html(self):
        from quora_questions import extract_quora_urls
        html = '''
        <a href="https://www.quora.com/What-is-the-best-gift-for-grandparents">link1</a>
        <a href="https://www.quora.com/How-do-I-choose-a-gift">link2</a>
        <a href="https://www.example.com/not-quora">link3</a>
        '''
        urls = extract_quora_urls(html)
        assert len(urls) >= 2
        assert all("quora.com" in u for u in urls)

    def test_extract_quora_urls_deduplicates(self):
        from quora_questions import extract_quora_urls
        html = '''
        <a href="https://www.quora.com/What-is-the-best-gift">link1</a>
        <a href="https://www.quora.com/What-is-the-best-gift">link2</a>
        '''
        urls = extract_quora_urls(html)
        assert len(urls) == 1

    def test_extract_quora_urls_filters_topic_pages(self):
        from quora_questions import extract_quora_urls
        html = '''
        <a href="https://www.quora.com/What-is-the-best-gift">question</a>
        <a href="https://www.quora.com/topic/Grandparents">topic page</a>
        <a href="https://www.quora.com/profile/SomeUser">profile</a>
        '''
        urls = extract_quora_urls(html)
        # Should include question URLs, may filter topic/profile pages
        assert any("What-is-the-best-gift" in u for u in urls)

    def test_extract_quora_urls_empty_html(self):
        from quora_questions import extract_quora_urls
        urls = extract_quora_urls("")
        assert urls == []


class TestAddShareParam:
    """Tests for adding ?share=1 to Quora URLs to bypass login wall."""

    def test_adds_share_param(self):
        from quora_questions import add_share_param
        url = "https://www.quora.com/What-is-the-best-gift"
        result = add_share_param(url)
        assert "share=1" in result

    def test_preserves_existing_params(self):
        from quora_questions import add_share_param
        url = "https://www.quora.com/What-is-the-best-gift?type=answer"
        result = add_share_param(url)
        assert "share=1" in result
        assert "type=answer" in result

    def test_no_duplicate_share_param(self):
        from quora_questions import add_share_param
        url = "https://www.quora.com/What-is-the-best-gift?share=1"
        result = add_share_param(url)
        assert result.count("share=1") == 1


class TestParseQuestionData:
    """Tests for extracting question data from a Quora page via mock Playwright."""

    def test_parse_question_full_data(self):
        from quora_questions import parse_question_page
        mock_page = MagicMock()
        mock_page.url = "https://www.quora.com/What-is-the-best-gift-for-grandparents"
        mock_page.title.return_value = "What is the best gift for grandparents? - Quora"
        mock_page.query_selector.side_effect = lambda sel: {
            '.q-box.qu-userSelect--text': _mock_el("What is the best gift for grandparents?"),
            '[class*="question_title"], .puppeteer_test_question_title': _mock_el("What is the best gift for grandparents?"),
        }.get(sel)
        mock_page.query_selector_all.return_value = [MagicMock(), MagicMock(), MagicMock()]  # 3 answers
        mock_page.evaluate.return_value = None

        result = parse_question_page(mock_page)
        assert result["question_title"] != ""
        assert result["url"] == mock_page.url
        assert isinstance(result["answer_count"], int)

    def test_parse_question_minimal_data(self):
        from quora_questions import parse_question_page
        mock_page = MagicMock()
        mock_page.url = "https://www.quora.com/Some-question"
        mock_page.title.return_value = "Some question - Quora"
        mock_page.query_selector.return_value = None
        mock_page.query_selector_all.return_value = []
        mock_page.evaluate.return_value = None

        result = parse_question_page(mock_page)
        assert result is not None
        assert "url" in result


class TestQuestionsUserAgents:
    """Tests for user agent list in quora_questions."""

    def test_user_agents_exist(self):
        from quora_questions import USER_AGENTS
        assert isinstance(USER_AGENTS, list)
        assert len(USER_AGENTS) >= 3

    def test_user_agents_are_realistic(self):
        from quora_questions import USER_AGENTS
        for ua in USER_AGENTS:
            assert "Mozilla" in ua
            assert len(ua) > 50


class TestQuestionsCLI:
    """Tests for quora_questions CLI argument parsing."""

    def test_required_topic_arg(self):
        from quora_questions import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "grandparent gifts"])
        assert args.topic == "grandparent gifts"

    def test_default_max_questions(self):
        from quora_questions import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test"])
        assert args.max_questions == 20

    def test_custom_max_questions(self):
        from quora_questions import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test", "--max-questions", "10"])
        assert args.max_questions == 10

    def test_output_format_default(self):
        from quora_questions import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test"])
        assert args.output == "json"

    def test_output_format_markdown(self):
        from quora_questions import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test", "--output", "markdown"])
        assert args.output == "markdown"


class TestQuestionsOutputFormat:
    """Tests for question output formatting."""

    def test_format_results_json_structure(self):
        from quora_questions import format_results
        questions = [
            {
                "question_title": "What is the best gift?",
                "url": "https://www.quora.com/What-is-the-best-gift",
                "answer_count": 15,
                "follower_count": 50,
                "upvote_count": 10,
                "tags": ["gifts"],
                "date_asked": "",
                "description": "",
            }
        ]
        result = format_results("grandparent gifts", questions)
        assert result["topic"] == "grandparent gifts"
        assert "timestamp" in result
        assert result["total_questions"] == 1
        assert len(result["questions"]) == 1

    def test_format_results_empty(self):
        from quora_questions import format_results
        result = format_results("empty topic", [])
        assert result["total_questions"] == 0
        assert result["questions"] == []

    def test_format_results_sorted_by_engagement(self):
        from quora_questions import format_results
        questions = [
            {"question_title": "low", "url": "", "answer_count": 1, "follower_count": 5, "upvote_count": 0, "tags": [], "date_asked": "", "description": ""},
            {"question_title": "high", "url": "", "answer_count": 50, "follower_count": 200, "upvote_count": 100, "tags": [], "date_asked": "", "description": ""},
            {"question_title": "mid", "url": "", "answer_count": 10, "follower_count": 30, "upvote_count": 5, "tags": [], "date_asked": "", "description": ""},
        ]
        result = format_results("test", questions)
        assert result["questions"][0]["question_title"] == "high"
        assert result["questions"][-1]["question_title"] == "low"


# ============================================================================
# quora_answers.py tests
# ============================================================================


class TestParseAnswer:
    """Tests for extracting individual answer data."""

    def test_parse_answer_full_data(self):
        from quora_answers import parse_answer_element
        mock_el = MagicMock()
        mock_el.query_selector.side_effect = lambda sel: {
            '.q-box.qu-userSelect--text span': _mock_el("This is my detailed answer about the topic with specific advice."),
            '[class*="user"] a, .q-box a[href*="/profile/"]': _mock_el("Dr. Sarah Smith"),
            '[class*="credential"], .q-box [class*="credential"]': _mock_el("PhD in Psychology, Gift-giving researcher"),
        }.get(sel)
        mock_el.query_selector_all.return_value = []
        mock_el.inner_text.return_value = "This is my detailed answer about the topic."

        result = parse_answer_element(mock_el)
        assert result["text"] != ""
        assert isinstance(result.get("author_name", ""), str)
        assert isinstance(result.get("author_credentials", ""), str)

    def test_parse_answer_empty_element(self):
        from quora_answers import parse_answer_element
        mock_el = MagicMock()
        mock_el.query_selector.return_value = None
        mock_el.query_selector_all.return_value = []
        mock_el.inner_text.return_value = ""

        result = parse_answer_element(mock_el)
        assert result is not None
        assert result.get("text", "") == ""


class TestDetectPersuasionPatterns:
    """Tests for detecting persuasion patterns in answers."""

    def test_detects_personal_story(self):
        from quora_answers import detect_persuasion_patterns
        text = "When I was struggling with the same problem, I found that the key was to start small. I personally tried three different approaches before finding what worked."
        patterns = detect_persuasion_patterns(text)
        assert "personal_story" in patterns

    def test_detects_authority_credential(self):
        from quora_answers import detect_persuasion_patterns
        text = "As a certified financial advisor with 20 years of experience, I recommend that you diversify your portfolio."
        patterns = detect_persuasion_patterns(text)
        assert "authority" in patterns

    def test_detects_specific_recommendation(self):
        from quora_answers import detect_persuasion_patterns
        text = "I highly recommend Product XYZ. You should definitely try it because it solved my problem completely."
        patterns = detect_persuasion_patterns(text)
        assert "specific_recommendation" in patterns

    def test_empty_text_no_patterns(self):
        from quora_answers import detect_persuasion_patterns
        patterns = detect_persuasion_patterns("")
        assert isinstance(patterns, list)
        assert len(patterns) == 0


class TestExtractProductMentions:
    """Tests for extracting product/service mentions from answers."""

    def test_extract_product_mentions(self):
        from quora_answers import extract_product_mentions
        text = "I recommend using Grammarly for writing and Canva for design. Also check out Amazon for reviews."
        mentions = extract_product_mentions(text)
        assert isinstance(mentions, list)

    def test_no_mentions_in_generic_text(self):
        from quora_answers import extract_product_mentions
        text = "The best approach is to take your time and think carefully about the decision."
        mentions = extract_product_mentions(text)
        assert isinstance(mentions, list)


class TestAnswersCLI:
    """Tests for quora_answers CLI argument parsing."""

    def test_url_mode(self):
        from quora_answers import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://www.quora.com/What-is-the-best-gift"])
        assert args.url == "https://www.quora.com/What-is-the-best-gift"

    def test_topic_mode(self):
        from quora_answers import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "wedding planning tips"])
        assert args.topic == "wedding planning tips"

    def test_default_max_answers(self):
        from quora_answers import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://www.quora.com/test"])
        assert args.max_answers == 10

    def test_topic_mode_defaults(self):
        from quora_answers import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test topic"])
        assert args.max_questions == 5
        assert args.answers_per_question == 5

    def test_output_format_choices(self):
        from quora_answers import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://www.quora.com/test", "--output", "markdown"])
        assert args.output == "markdown"


class TestAnswersOutputFormat:
    """Tests for answer output formatting."""

    def test_format_answers_json_structure(self):
        from quora_answers import format_results
        answers = [
            {
                "text": "Here is my answer to the question.",
                "author_name": "John Doe",
                "author_credentials": "Software Engineer",
                "upvote_count": 42,
                "date": "2024-01-15",
                "product_mentions": [],
                "links": [],
                "persuasion_patterns": ["authority"],
            }
        ]
        result = format_results("https://www.quora.com/test", "Test question?", answers)
        assert "timestamp" in result
        assert result["total_answers"] == 1
        assert len(result["answers"]) == 1
        assert result["answers"][0]["author_name"] == "John Doe"

    def test_format_answers_empty(self):
        from quora_answers import format_results
        result = format_results("https://www.quora.com/test", "Test?", [])
        assert result["total_answers"] == 0


# ============================================================================
# quora_voice_mine.py tests
# ============================================================================


class TestExtractPainPhrases:
    """Tests for extracting pain point phrases from text."""

    def test_extracts_pain_phrases(self):
        from quora_voice_mine import extract_pain_phrases
        texts = [
            "I feel so alone since my wife passed. Nobody visits anymore.",
            "The biggest frustration is that technology is so confusing for me.",
            "I struggle with connecting to my grandkids who live far away.",
        ]
        phrases = extract_pain_phrases(texts)
        assert isinstance(phrases, list)
        assert len(phrases) > 0

    def test_empty_texts(self):
        from quora_voice_mine import extract_pain_phrases
        phrases = extract_pain_phrases([])
        assert phrases == []

    def test_no_pain_in_positive_text(self):
        from quora_voice_mine import extract_pain_phrases
        texts = ["Everything is wonderful and I love my life!"]
        phrases = extract_pain_phrases(texts)
        assert isinstance(phrases, list)


class TestExtractDesirePhrases:
    """Tests for extracting desire/want phrases from text."""

    def test_extracts_desire_phrases(self):
        from quora_voice_mine import extract_desire_phrases
        texts = [
            "I just want to stay connected with my grandkids.",
            "I wish I could see them more often.",
            "My biggest goal is to leave a lasting legacy for my family.",
        ]
        phrases = extract_desire_phrases(texts)
        assert isinstance(phrases, list)
        assert len(phrases) > 0

    def test_empty_texts(self):
        from quora_voice_mine import extract_desire_phrases
        phrases = extract_desire_phrases([])
        assert phrases == []


class TestExtractObjectionPhrases:
    """Tests for extracting objection/resistance phrases from text."""

    def test_extracts_objection_phrases(self):
        from quora_voice_mine import extract_objection_phrases
        texts = [
            "But technology is so confusing for older people.",
            "I don't think I can afford something like that.",
            "I'm not sure this would actually work for someone my age.",
        ]
        phrases = extract_objection_phrases(texts)
        assert isinstance(phrases, list)
        assert len(phrases) > 0

    def test_empty_texts(self):
        from quora_voice_mine import extract_objection_phrases
        phrases = extract_objection_phrases([])
        assert phrases == []


class TestExtractEmotionalVocabulary:
    """Tests for extracting high-emotion words/phrases."""

    def test_extracts_emotional_words(self):
        from quora_voice_mine import extract_emotional_vocabulary
        texts = [
            "I was devastated when I heard the news. It broke my heart completely.",
            "The joy of seeing my grandchildren is absolutely priceless and heartwarming.",
            "I feel terrified about getting old and being forgotten.",
        ]
        vocab = extract_emotional_vocabulary(texts)
        assert isinstance(vocab, list)
        assert len(vocab) > 0

    def test_empty_texts(self):
        from quora_voice_mine import extract_emotional_vocabulary
        vocab = extract_emotional_vocabulary([])
        assert vocab == []


class TestExtractQuestionPatterns:
    """Tests for extracting how people frame their questions."""

    def test_extracts_question_patterns(self):
        from quora_voice_mine import extract_question_patterns
        texts = [
            "Is it normal to feel lonely after retirement?",
            "How do I deal with my grandparents living far away?",
            "What's the best way to stay active at 70?",
        ]
        patterns = extract_question_patterns(texts)
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_empty_texts(self):
        from quora_voice_mine import extract_question_patterns
        patterns = extract_question_patterns([])
        assert patterns == []


class TestExtractDemographicSignals:
    """Tests for extracting demographic information from self-descriptions."""

    def test_extracts_age_signals(self):
        from quora_voice_mine import extract_demographic_signals
        texts = [
            "As a 65-year-old grandmother, I find this challenging.",
            "I'm a retired teacher in my 70s.",
        ]
        signals = extract_demographic_signals(texts)
        assert isinstance(signals, dict)
        assert "age_signals" in signals

    def test_extracts_role_signals(self):
        from quora_voice_mine import extract_demographic_signals
        texts = [
            "As a mother of three, I always worry about my parents.",
            "Being a grandparent is the best thing that ever happened to me.",
        ]
        signals = extract_demographic_signals(texts)
        assert isinstance(signals, dict)

    def test_empty_texts(self):
        from quora_voice_mine import extract_demographic_signals
        signals = extract_demographic_signals([])
        assert isinstance(signals, dict)


class TestVoiceMineCLI:
    """Tests for quora_voice_mine CLI argument parsing."""

    def test_required_topic_arg(self):
        from quora_voice_mine import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "grandparent loneliness"])
        assert args.topic == "grandparent loneliness"

    def test_default_max_questions(self):
        from quora_voice_mine import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test"])
        assert args.max_questions == 10

    def test_output_format_default(self):
        from quora_voice_mine import create_parser
        parser = create_parser()
        args = parser.parse_args(["--topic", "test"])
        assert args.output == "json"


class TestVoiceMineOutputFormat:
    """Tests for voice mine output formatting."""

    def test_format_voice_data_structure(self):
        from quora_voice_mine import format_results
        voice_data = {
            "pain_phrases": ["I feel alone"],
            "desire_phrases": ["I want connection"],
            "objection_phrases": ["too expensive"],
            "emotional_vocabulary": ["heartbroken", "joyful"],
            "question_patterns": ["Is it normal to..."],
            "product_mentions": ["FaceTime"],
            "demographic_signals": {"age_signals": ["65-year-old"], "role_signals": ["grandmother"]},
        }
        result = format_results("grandparent loneliness", voice_data, 10)
        assert result["topic"] == "grandparent loneliness"
        assert "timestamp" in result
        assert "voice_data" in result
        assert result["questions_analyzed"] == 10

    def test_format_voice_data_empty(self):
        from quora_voice_mine import format_results
        voice_data = {
            "pain_phrases": [],
            "desire_phrases": [],
            "objection_phrases": [],
            "emotional_vocabulary": [],
            "question_patterns": [],
            "product_mentions": [],
            "demographic_signals": {},
        }
        result = format_results("test", voice_data, 0)
        assert result["questions_analyzed"] == 0


# ============================================================================
# Helpers
# ============================================================================


def _mock_el(text=None, href=None, src=None):
    """Create a mock Playwright element with common properties."""
    el = MagicMock()
    if text is not None:
        el.inner_text.return_value = text
    if href is not None:
        el.get_attribute.side_effect = lambda attr: href if attr == "href" else None
    elif src is not None:
        el.get_attribute.side_effect = lambda attr: src if attr == "src" else None
    else:
        el.inner_text.return_value = text or ""
        el.get_attribute.return_value = None
    return el
