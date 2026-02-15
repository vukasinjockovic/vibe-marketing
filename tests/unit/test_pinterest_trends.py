"""Tests for pinterest_trends.py -- Pinterest trending topics scraper.

Tests cover:
- CLI argument parsing
- Category URL mapping
- Trend data extraction
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

    def test_default_category(self):
        from pinterest_trends import create_parser
        parser = create_parser()
        args = parser.parse_args([])
        assert args.category is None or args.category == ""

    def test_category_argument(self):
        from pinterest_trends import create_parser
        parser = create_parser()
        args = parser.parse_args(["--category", "weddings"])
        assert args.category == "weddings"

    def test_output_format_default(self):
        from pinterest_trends import create_parser
        parser = create_parser()
        args = parser.parse_args([])
        assert args.output == "json"

    def test_output_format_markdown(self):
        from pinterest_trends import create_parser
        parser = create_parser()
        args = parser.parse_args(["--output", "markdown"])
        assert args.output == "markdown"


class TestCategoryMapping:
    """Tests for category to URL mapping."""

    def test_known_categories(self):
        from pinterest_trends import get_trends_url
        url = get_trends_url("weddings")
        assert "trends.pinterest.com" in url

    def test_general_trends(self):
        from pinterest_trends import get_trends_url
        url = get_trends_url(None)
        assert "trends.pinterest.com" in url

    def test_all_supported_categories(self):
        from pinterest_trends import SUPPORTED_CATEGORIES
        expected = {"weddings", "home", "food", "diy", "fashion", "beauty", "travel"}
        assert expected.issubset(set(SUPPORTED_CATEGORIES))


class TestParseTrendItem:
    """Tests for parsing individual trend items."""

    def test_parse_trend_basic(self):
        from pinterest_trends import parse_trend_item
        mock_el = MagicMock()
        mock_el.inner_text.return_value = "Coastal grandmother aesthetic"
        mock_el.query_selector.return_value = None

        result = parse_trend_item(mock_el)
        assert result["term"] == "Coastal grandmother aesthetic"

    def test_parse_trend_with_growth(self):
        from pinterest_trends import parse_trend_item
        mock_el = MagicMock()
        mock_el.inner_text.return_value = "Dopamine decor"

        growth_el = MagicMock()
        growth_el.inner_text.return_value = "+150%"
        mock_el.query_selector.side_effect = lambda sel: growth_el if "growth" in sel.lower() or "change" in sel.lower() else None

        result = parse_trend_item(mock_el)
        assert result["term"] == "Dopamine decor"

    def test_parse_trend_empty(self):
        from pinterest_trends import parse_trend_item
        mock_el = MagicMock()
        mock_el.inner_text.return_value = ""
        mock_el.query_selector.return_value = None

        result = parse_trend_item(mock_el)
        assert result["term"] == ""


class TestFormatTrendsResults:
    """Tests for trend result formatting."""

    def test_format_with_trends(self):
        from pinterest_trends import format_trends_results
        trends = [
            {"term": "Coastal decor", "growth": "+200%"},
            {"term": "Quiet luxury", "growth": "+150%"},
        ]
        result = format_trends_results("home", trends)
        assert result["category"] == "home"
        assert result["total_trends"] == 2
        assert "timestamp" in result
        assert len(result["trends"]) == 2

    def test_format_empty_trends(self):
        from pinterest_trends import format_trends_results
        result = format_trends_results("weddings", [])
        assert result["total_trends"] == 0
        assert result["trends"] == []

    def test_format_no_category(self):
        from pinterest_trends import format_trends_results
        result = format_trends_results(None, [{"term": "trending"}])
        assert result["category"] is None or result["category"] == "general"
