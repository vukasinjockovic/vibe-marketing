"""Tests for extract_pdf_text.py — PDF text extraction."""
import sys
import os
import tempfile
import pytest

SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", ".claude", "skills",
    "audience-analysis-procedures", "scripts"
)
sys.path.insert(0, SCRIPTS_DIR)


class TestExtractPdfFunctions:
    """Test the PDF extraction utility functions."""

    def test_module_imports(self):
        """The module should import without error."""
        import extract_pdf_text
        assert hasattr(extract_pdf_text, "extract_text")

    def test_extract_text_nonexistent_file(self):
        """Should raise an error for nonexistent files."""
        from extract_pdf_text import extract_text
        with pytest.raises((FileNotFoundError, Exception)):
            extract_text("/nonexistent/file.pdf")

    def test_output_path_default(self):
        """Output path should default to .md extension."""
        from extract_pdf_text import get_output_path
        assert get_output_path("input.pdf") == "input.md"
        assert get_output_path("/path/to/file.pdf") == "/path/to/file.md"

    def test_output_path_explicit(self):
        """Explicit output path should be used as-is."""
        from extract_pdf_text import get_output_path
        assert get_output_path("input.pdf", "custom.md") == "custom.md"
