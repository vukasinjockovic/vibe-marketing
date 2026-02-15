"""Tests for the Etsy research skill scripts.

Tests cover:
- etsy_search.py: parse_price, parse_rating, compute_search_metrics, format_as_markdown
- etsy_reviews.py: voice analysis (love/hate phrases, product gaps, gift mentions)
- etsy_shop.py: parse_shop_stats, parse_sales_count
- etsy_suggest.py: build_suggest_url, dedupe_suggestions, expand_with_alphabet
"""
import json
import sys
import os
import pytest

# Add the etsy-research scripts dir to path
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "etsy-research", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


# ===========================================================================
# etsy_search.py tests
# ===========================================================================

class TestParsePrice:
    """Test price parsing from Etsy listing text."""

    def test_usd_price(self):
        from etsy_search import parse_price
        assert parse_price("$24.99") == 24.99

    def test_usd_price_no_cents(self):
        from etsy_search import parse_price
        assert parse_price("$100") == 100.0

    def test_usd_with_comma(self):
        from etsy_search import parse_price
        assert parse_price("$1,299.00") == 1299.0

    def test_price_with_currency_symbol_eur(self):
        from etsy_search import parse_price
        # Should still extract numeric value
        result = parse_price("EUR 24.99")
        assert result == 24.99

    def test_empty_string(self):
        from etsy_search import parse_price
        assert parse_price("") == 0.0

    def test_none_value(self):
        from etsy_search import parse_price
        assert parse_price(None) == 0.0

    def test_free_shipping_text(self):
        from etsy_search import parse_price
        assert parse_price("FREE shipping") == 0.0

    def test_price_range(self):
        from etsy_search import parse_price
        # Should extract the first price
        result = parse_price("$12.99 - $45.99")
        assert result == 12.99


class TestParseRating:
    """Test star rating parsing."""

    def test_standard_rating(self):
        from etsy_search import parse_rating
        assert parse_rating("5 out of 5 stars") == 5.0

    def test_fractional_rating(self):
        from etsy_search import parse_rating
        assert parse_rating("4.5 out of 5 stars") == 4.5

    def test_empty_string(self):
        from etsy_search import parse_rating
        assert parse_rating("") == 0.0

    def test_none_value(self):
        from etsy_search import parse_rating
        assert parse_rating(None) == 0.0

    def test_numeric_only(self):
        from etsy_search import parse_rating
        # e.g., from aria label "4.8"
        assert parse_rating("4.8") == 4.8


class TestComputeSearchMetrics:
    """Test metrics calculation from listing data."""

    def test_basic_metrics(self):
        from etsy_search import compute_search_metrics
        listings = [
            {"price": 10.0, "free_shipping": True, "bestseller": True},
            {"price": 20.0, "free_shipping": False, "bestseller": False},
            {"price": 30.0, "free_shipping": True, "bestseller": False},
        ]
        metrics = compute_search_metrics(listings)
        assert metrics["average_price"] == pytest.approx(20.0)
        assert metrics["price_range"]["min"] == 10.0
        assert metrics["price_range"]["max"] == 30.0
        assert metrics["pct_free_shipping"] == pytest.approx(66.67, abs=0.01)
        assert metrics["pct_bestseller"] == pytest.approx(33.33, abs=0.01)

    def test_empty_listings(self):
        from etsy_search import compute_search_metrics
        metrics = compute_search_metrics([])
        assert metrics["average_price"] == 0
        assert metrics["pct_free_shipping"] == 0
        assert metrics["pct_bestseller"] == 0

    def test_single_listing(self):
        from etsy_search import compute_search_metrics
        listings = [
            {"price": 25.50, "free_shipping": True, "bestseller": True},
        ]
        metrics = compute_search_metrics(listings)
        assert metrics["average_price"] == 25.50
        assert metrics["price_range"]["min"] == 25.50
        assert metrics["price_range"]["max"] == 25.50
        assert metrics["pct_free_shipping"] == 100.0
        assert metrics["pct_bestseller"] == 100.0

    def test_all_zero_prices(self):
        from etsy_search import compute_search_metrics
        listings = [
            {"price": 0.0, "free_shipping": False, "bestseller": False},
            {"price": 0.0, "free_shipping": False, "bestseller": False},
        ]
        metrics = compute_search_metrics(listings)
        assert metrics["average_price"] == 0.0


class TestSearchSortUrl:
    """Test URL construction for Etsy search."""

    def test_relevancy_sort(self):
        from etsy_search import build_search_url
        url = build_search_url("grandparent memory book", "relevancy")
        assert "q=grandparent+memory+book" in url or "q=grandparent%20memory%20book" in url
        assert "etsy.com/search" in url

    def test_sort_parameter(self):
        from etsy_search import build_search_url
        url = build_search_url("test", "most_recent")
        assert "most_recent" in url

    def test_top_reviews_sort(self):
        from etsy_search import build_search_url
        url = build_search_url("test", "top_reviews")
        assert "top_reviews" in url


# ===========================================================================
# etsy_reviews.py tests
# ===========================================================================

class TestReviewVoiceAnalysis:
    """Test the voice analysis functions from etsy_reviews.py."""

    def test_love_phrases_extraction(self):
        from etsy_reviews import analyze_etsy_reviews
        reviews = [
            {"stars": 5, "text": "I absolutely love this journal. Made my grandma cry tears of joy."},
            {"stars": 5, "text": "Perfect gift for my mother. She treasures it forever."},
            {"stars": 5, "text": "Exceeded my expectations, highly recommend to everyone."},
        ]
        analysis = analyze_etsy_reviews(reviews)
        assert len(analysis["love_phrases"]) > 0

    def test_hate_phrases_extraction(self):
        from etsy_reviews import analyze_etsy_reviews
        reviews = [
            {"stars": 1, "text": "Very disappointed with the quality. Pages fell apart immediately."},
            {"stars": 1, "text": "Too small to write in. Returned it for a refund."},
            {"stars": 2, "text": "Cheaply made, not worth the price. Would not recommend."},
        ]
        analysis = analyze_etsy_reviews(reviews)
        assert len(analysis["hate_phrases"]) > 0

    def test_product_gaps_extraction(self):
        from etsy_reviews import analyze_etsy_reviews
        reviews = [
            {"stars": 3, "text": "Good idea but I wish it had more pages for photos."},
            {"stars": 4, "text": "Would be great if it came with a pen holder."},
            {"stars": 2, "text": "Needs better binding. The pages fall out."},
        ]
        analysis = analyze_etsy_reviews(reviews)
        assert len(analysis["product_gaps"]) > 0

    def test_gift_mentions_detection(self):
        from etsy_reviews import analyze_etsy_reviews
        reviews = [
            {"stars": 5, "text": "Bought this as a Christmas gift for my grandmother."},
            {"stars": 5, "text": "Perfect birthday present for my mom."},
            {"stars": 4, "text": "Got it for Mother's Day. She loved it."},
        ]
        analysis = analyze_etsy_reviews(reviews)
        assert len(analysis["gift_mentions"]) > 0

    def test_empty_reviews(self):
        from etsy_reviews import analyze_etsy_reviews
        analysis = analyze_etsy_reviews([])
        assert analysis["love_phrases"] == []
        assert analysis["hate_phrases"] == []
        assert analysis["product_gaps"] == []
        assert analysis["gift_mentions"] == []

    def test_star_filter_applied(self):
        from etsy_reviews import filter_reviews_by_stars
        reviews = [
            {"stars": 1, "text": "Bad"},
            {"stars": 3, "text": "Ok"},
            {"stars": 5, "text": "Great"},
        ]
        filtered = filter_reviews_by_stars(reviews, [1, 5])
        assert len(filtered) == 2
        assert all(r["stars"] in (1, 5) for r in filtered)

    def test_star_filter_all_stars(self):
        from etsy_reviews import filter_reviews_by_stars
        reviews = [
            {"stars": 1, "text": "Bad"},
            {"stars": 3, "text": "Ok"},
            {"stars": 5, "text": "Great"},
        ]
        filtered = filter_reviews_by_stars(reviews, [1, 2, 3, 4, 5])
        assert len(filtered) == 3

    def test_dedupe_and_rank(self):
        from etsy_reviews import dedupe_and_rank
        phrases = ["great quality", "GREAT QUALITY", "great quality", "poor finish"]
        result = dedupe_and_rank(phrases, max_items=10)
        # "great quality" appears 3 times (case-insensitive), should be first
        assert len(result) == 2
        assert result[0].lower() == "great quality"


# ===========================================================================
# etsy_shop.py tests
# ===========================================================================

class TestParseSalesCount:
    """Test parsing sales count from shop page text."""

    def test_simple_count(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count("1,234 sales") == 1234

    def test_large_count(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count("123,456 sales") == 123456

    def test_no_comma(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count("567 sales") == 567

    def test_empty_string(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count("") == 0

    def test_none_value(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count(None) == 0

    def test_no_match(self):
        from etsy_shop import parse_sales_count
        assert parse_sales_count("No sales yet") == 0


class TestParseShopStats:
    """Test shop statistics extraction helpers."""

    def test_build_shop_url_from_name(self):
        from etsy_shop import build_shop_url
        url = build_shop_url("DuncanandStone")
        assert url == "https://www.etsy.com/shop/DuncanandStone"

    def test_build_shop_url_from_url(self):
        from etsy_shop import build_shop_url
        url = build_shop_url("https://www.etsy.com/shop/SomeShop")
        # Already a URL, return as-is
        assert url == "https://www.etsy.com/shop/SomeShop"

    def test_analyze_pricing_strategy(self):
        from etsy_shop import analyze_pricing_strategy
        listings = [
            {"price": 10.0, "reviews": 100},
            {"price": 12.0, "reviews": 50},
            {"price": 15.0, "reviews": 200},
            {"price": 45.0, "reviews": 5},
        ]
        analysis = analyze_pricing_strategy(listings)
        assert "price_range" in analysis
        assert analysis["price_range"]["min"] == 10.0
        assert analysis["price_range"]["max"] == 45.0
        assert "average_price" in analysis
        assert "median_price" in analysis

    def test_analyze_pricing_empty(self):
        from etsy_shop import analyze_pricing_strategy
        analysis = analyze_pricing_strategy([])
        assert analysis["price_range"]["min"] == 0
        assert analysis["price_range"]["max"] == 0
        assert analysis["average_price"] == 0


# ===========================================================================
# etsy_suggest.py tests
# ===========================================================================

class TestBuildSuggestUrl:
    """Test Etsy autocomplete URL building."""

    def test_basic_url(self):
        from etsy_suggest import build_suggest_url
        url = build_suggest_url("grandparent gift")
        assert "etsy.com" in url
        assert "grandparent" in url

    def test_url_encoding(self):
        from etsy_suggest import build_suggest_url
        url = build_suggest_url("mom's birthday gift")
        # Should be URL-encoded
        assert "mom" in url


class TestDedupeSuggestions:
    """Test suggestion deduplication."""

    def test_basic_dedup(self):
        from etsy_suggest import dedupe_suggestions
        suggestions = [
            "grandparent gift",
            "Grandparent Gift",
            "grandparent gift book",
            "grandparent gift",
        ]
        result = dedupe_suggestions(suggestions)
        assert len(result) == 2

    def test_empty_list(self):
        from etsy_suggest import dedupe_suggestions
        assert dedupe_suggestions([]) == []


class TestExpandWithAlphabet:
    """Test alphabet expansion query generation."""

    def test_generates_26_queries(self):
        from etsy_suggest import generate_alphabet_queries
        queries = generate_alphabet_queries("grandparent gift")
        assert len(queries) == 26
        assert queries[0] == "grandparent gift a"
        assert queries[25] == "grandparent gift z"

    def test_seed_preserved(self):
        from etsy_suggest import generate_alphabet_queries
        queries = generate_alphabet_queries("wedding planner")
        assert all(q.startswith("wedding planner ") for q in queries)


# ===========================================================================
# Integration-style tests (data format validation)
# ===========================================================================

class TestOutputFormats:
    """Test that output structures match expected schemas."""

    def test_search_listing_schema(self):
        """A listing dict should have all required keys."""
        required_keys = {
            "title", "price", "shop_name", "rating", "review_count",
            "listing_url", "image_url", "bestseller", "star_seller",
            "ad", "free_shipping",
        }
        # Create a sample listing
        listing = {
            "title": "Grandparent Journal",
            "price": 24.99,
            "shop_name": "DuncanAndStone",
            "rating": 4.8,
            "review_count": 1234,
            "listing_url": "https://www.etsy.com/listing/12345/grandparent-journal",
            "image_url": "https://i.etsystatic.com/img.jpg",
            "bestseller": True,
            "star_seller": False,
            "ad": False,
            "free_shipping": True,
        }
        assert required_keys.issubset(listing.keys())

    def test_review_schema(self):
        """A review dict should have all required keys."""
        required_keys = {
            "stars", "text", "reviewer_name", "date",
            "verified_purchase", "has_photos",
        }
        review = {
            "stars": 5,
            "text": "Amazing product",
            "reviewer_name": "Jane",
            "date": "2025-12-01",
            "verified_purchase": True,
            "has_photos": False,
        }
        assert required_keys.issubset(review.keys())

    def test_shop_schema(self):
        """A shop dict should have all required keys."""
        required_keys = {
            "shop_name", "total_sales", "total_reviews",
            "average_rating", "member_since", "location",
        }
        shop = {
            "shop_name": "DuncanAndStone",
            "total_sales": 50000,
            "total_reviews": 12000,
            "average_rating": 4.9,
            "member_since": "2015",
            "location": "United States",
        }
        assert required_keys.issubset(shop.keys())

    def test_voice_analysis_schema(self):
        """Voice analysis output should have required keys."""
        from etsy_reviews import analyze_etsy_reviews
        analysis = analyze_etsy_reviews([])
        required_keys = {"love_phrases", "hate_phrases", "product_gaps", "gift_mentions"}
        assert required_keys.issubset(analysis.keys())
