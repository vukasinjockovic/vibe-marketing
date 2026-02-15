"""Tests for pinterest_boards.py -- Pinterest board analysis via Playwright.

Tests cover:
- CLI argument parsing (URL mode vs search mode)
- Board metadata extraction
- Theme identification from pin descriptions
- JSON output structure
- Error handling
"""

import json
import sys
import os
import pytest
from unittest.mock import MagicMock

# Add scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "pinterest-research", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


class TestCLIArgs:
    """Tests for argparse CLI argument parsing."""

    def test_url_mode(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://www.pinterest.com/user/board/"])
        assert args.url == "https://www.pinterest.com/user/board/"
        assert args.search is None

    def test_search_mode(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--search", "wedding planning boards"])
        assert args.search == "wedding planning boards"
        assert args.url is None

    def test_default_max_pins(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://pinterest.com/u/b/"])
        assert args.max_pins == 30

    def test_custom_max_boards(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--search", "test", "--max-boards", "10"])
        assert args.max_boards == 10

    def test_default_max_boards(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--search", "test"])
        assert args.max_boards == 5

    def test_output_format_default(self):
        from pinterest_boards import create_parser
        parser = create_parser()
        args = parser.parse_args(["--url", "https://pinterest.com/u/b/"])
        assert args.output == "json"


class TestExtractBoardMeta:
    """Tests for extracting board metadata."""

    def test_extract_board_info(self):
        from pinterest_boards import extract_board_info
        mock_page = MagicMock()
        mock_page.query_selector.side_effect = lambda sel: {
            'h1, [data-test-id="board-header"] h1': _mock_el("Wedding Inspiration"),
            '[data-test-id="board-description"], meta[name="description"]': _mock_el("My dream wedding ideas"),
            '[data-test-id="board-pin-count"], [data-test-id="pin-count"]': _mock_el("245 Pins"),
            '[data-test-id="board-follower-count"]': _mock_el("1.2k followers"),
            '[data-test-id="board-creator"], [data-test-id="creator-name"]': _mock_el("WeddingPlanner"),
        }.get(sel)

        result = extract_board_info(mock_page)
        assert result["name"] == "Wedding Inspiration"
        assert result["description"] == "My dream wedding ideas"
        assert result["pin_count_text"] == "245 Pins"
        assert result["creator"] == "WeddingPlanner"

    def test_extract_board_info_missing_fields(self):
        from pinterest_boards import extract_board_info
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None

        result = extract_board_info(mock_page)
        assert result["name"] == ""
        assert result["description"] == ""


class TestIdentifyThemes:
    """Tests for theme identification from pin descriptions."""

    def test_identify_themes_basic(self):
        from pinterest_boards import identify_themes
        pins = [
            {"description": "rustic barn wedding decor ideas"},
            {"description": "outdoor rustic wedding centerpieces"},
            {"description": "rustic wedding cake designs"},
            {"description": "bohemian wedding dress inspiration"},
            {"description": "outdoor garden wedding setup"},
        ]
        themes = identify_themes(pins)
        assert isinstance(themes, list)
        assert len(themes) > 0
        # "rustic" and "wedding" should be top themes
        theme_words = [t["word"] for t in themes]
        assert "wedding" in theme_words or "rustic" in theme_words

    def test_identify_themes_empty_pins(self):
        from pinterest_boards import identify_themes
        themes = identify_themes([])
        assert themes == []

    def test_identify_themes_no_descriptions(self):
        from pinterest_boards import identify_themes
        pins = [{"description": ""}, {"description": ""}]
        themes = identify_themes(pins)
        assert isinstance(themes, list)


class TestFormatBoardResults:
    """Tests for board result formatting."""

    def test_format_single_board(self):
        from pinterest_boards import format_board_results
        boards = [
            {
                "name": "Test Board",
                "description": "A test board",
                "url": "https://pinterest.com/user/test/",
                "pin_count_text": "100 Pins",
                "follower_count_text": "50 followers",
                "creator": "TestUser",
                "pins": [{"description": "pin 1"}],
                "themes": [{"word": "test", "count": 5}],
            }
        ]
        result = format_board_results(boards, "test boards")
        assert result["query"] == "test boards"
        assert result["total_boards"] == 1
        assert "timestamp" in result
        assert result["boards"][0]["name"] == "Test Board"

    def test_format_empty_boards(self):
        from pinterest_boards import format_board_results
        result = format_board_results([], "empty search")
        assert result["total_boards"] == 0
        assert result["boards"] == []


# Helper for creating mock elements
def _mock_el(text=None):
    el = MagicMock()
    if text is not None:
        el.inner_text.return_value = text
        el.get_attribute.return_value = text
    else:
        el.inner_text.return_value = ""
        el.get_attribute.return_value = ""
    return el
