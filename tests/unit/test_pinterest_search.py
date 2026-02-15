"""Tests for pinterest_search.py -- Pinterest pin search via Playwright.

Tests cover:
- CLI argument parsing
- URL construction from query
- Pin data extraction from mock HTML
- JSON output structure
- Error handling (empty results, timeouts)
- Stealth measures (user agent rotation, delays)
"""

import json
import sys
import os
import argparse
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "pinterest-research", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


class TestBuildSearchUrl:
    """Tests for building Pinterest search URLs."""

    def test_basic_query(self):
        from pinterest_search import build_search_url
        url = build_search_url("grandparent gifts")
        assert "pinterest.com/search/pins/" in url
        assert "q=" in url
        assert "grandparent" in url

    def test_query_encoding(self):
        from pinterest_search import build_search_url
        url = build_search_url("wedding & party ideas")
        assert "pinterest.com/search/pins/" in url
        # Special chars should be URL-encoded
        assert "+" in url or "%20" in url or "%26" in url

    def test_empty_query(self):
        from pinterest_search import build_search_url
        url = build_search_url("")
        assert "pinterest.com/search/pins/" in url


class TestParsePin:
    """Tests for extracting pin data from DOM-like structures."""

    def test_parse_pin_full_data(self):
        from pinterest_search import parse_pin_element
        mock_element = MagicMock()
        mock_element.query_selector.side_effect = lambda sel: {
            '[data-test-id="pinDescription"], [title]': _mock_el("Beautiful sunset painting"),
            'a[href*="/pin/"]': _mock_el(href="/pin/12345/"),
            'img[src]': _mock_el(src="https://i.pinimg.com/test.jpg"),
            '[data-test-id="pin-repin-count"], [aria-label*="repin"], [aria-label*="save"]': None,
            '[data-test-id="pinner-name"]': _mock_el("ArtLover99"),
        }.get(sel)

        result = parse_pin_element(mock_element)
        assert result["description"] == "Beautiful sunset painting"
        assert result["pin_url"] == "https://www.pinterest.com/pin/12345/"
        assert result["image_url"] == "https://i.pinimg.com/test.jpg"
        assert result["pinner_name"] == "ArtLover99"

    def test_parse_pin_missing_fields_returns_partial(self):
        from pinterest_search import parse_pin_element
        mock_element = MagicMock()
        mock_element.query_selector.return_value = None

        result = parse_pin_element(mock_element)
        assert result is not None
        assert result.get("description", "") == ""
        assert result.get("pin_url", "") == ""

    def test_parse_pin_repin_count_extraction(self):
        from pinterest_search import parse_repin_count
        assert parse_repin_count("1.2k saves") == 1200
        assert parse_repin_count("500 saves") == 500
        assert parse_repin_count("2.5M saves") == 2500000
        assert parse_repin_count("") == 0
        assert parse_repin_count(None) == 0


class TestUserAgents:
    """Tests for user agent rotation and stealth."""

    def test_user_agents_list_exists(self):
        from pinterest_search import USER_AGENTS
        assert isinstance(USER_AGENTS, list)
        assert len(USER_AGENTS) >= 3

    def test_user_agents_are_realistic(self):
        from pinterest_search import USER_AGENTS
        for ua in USER_AGENTS:
            assert "Mozilla" in ua
            assert len(ua) > 50


class TestOutputFormat:
    """Tests for output formatting."""

    def test_format_results_json_structure(self):
        from pinterest_search import format_results
        pins = [
            {
                "description": "Test pin",
                "pin_url": "https://www.pinterest.com/pin/123/",
                "image_url": "https://i.pinimg.com/test.jpg",
                "repin_count": 100,
                "pinner_name": "TestUser",
                "board_name": "",
            }
        ]
        result = format_results("test query", pins)
        assert result["query"] == "test query"
        assert "timestamp" in result
        assert result["total_pins"] == 1
        assert len(result["pins"]) == 1
        assert result["pins"][0]["description"] == "Test pin"

    def test_format_results_empty_pins(self):
        from pinterest_search import format_results
        result = format_results("empty query", [])
        assert result["total_pins"] == 0
        assert result["pins"] == []

    def test_format_results_sorts_by_repins(self):
        from pinterest_search import format_results
        pins = [
            {"description": "low", "pin_url": "", "image_url": "", "repin_count": 10, "pinner_name": "", "board_name": ""},
            {"description": "high", "pin_url": "", "image_url": "", "repin_count": 1000, "pinner_name": "", "board_name": ""},
            {"description": "mid", "pin_url": "", "image_url": "", "repin_count": 100, "pinner_name": "", "board_name": ""},
        ]
        result = format_results("test", pins)
        assert result["pins"][0]["description"] == "high"
        assert result["pins"][1]["description"] == "mid"
        assert result["pins"][2]["description"] == "low"


class TestCLIArgs:
    """Tests for argparse CLI argument parsing."""

    def test_required_query_argument(self):
        from pinterest_search import create_parser
        parser = create_parser()
        args = parser.parse_args(["--query", "wedding ideas"])
        assert args.query == "wedding ideas"

    def test_default_max_pins(self):
        from pinterest_search import create_parser
        parser = create_parser()
        args = parser.parse_args(["--query", "test"])
        assert args.max_pins == 20

    def test_custom_max_pins(self):
        from pinterest_search import create_parser
        parser = create_parser()
        args = parser.parse_args(["--query", "test", "--max-pins", "50"])
        assert args.max_pins == 50

    def test_output_format_default(self):
        from pinterest_search import create_parser
        parser = create_parser()
        args = parser.parse_args(["--query", "test"])
        assert args.output == "json"

    def test_output_format_markdown(self):
        from pinterest_search import create_parser
        parser = create_parser()
        args = parser.parse_args(["--query", "test", "--output", "markdown"])
        assert args.output == "markdown"


# Helper for creating mock elements
def _mock_el(text=None, href=None, src=None):
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
