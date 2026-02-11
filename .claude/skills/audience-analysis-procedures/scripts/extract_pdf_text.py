#!/usr/bin/env python3
"""Extract text from PDF files.

Usage:
    python extract_pdf_text.py input.pdf [output.md]

Tries pymupdf first, falls back to pdfplumber.
If neither is installed, exits with error and install instructions.
"""
import sys
import os


def get_output_path(input_path: str, output_path: str = None) -> str:
    """Determine the output file path.

    Args:
        input_path: Path to the input PDF file.
        output_path: Explicit output path, or None to derive from input.

    Returns:
        The output file path (replaces .pdf with .md if not specified).
    """
    if output_path:
        return output_path
    base, _ = os.path.splitext(input_path)
    return base + ".md"


def extract_with_pymupdf(path: str) -> str:
    """Extract text from PDF using pymupdf (fitz)."""
    import pymupdf
    doc = pymupdf.open(path)
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n\n".join(text)


def extract_with_pdfplumber(path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        text = []
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n\n".join(text)


def extract_text(path: str) -> str:
    """Extract text from a PDF file.

    Tries pymupdf first, then pdfplumber. Raises if neither is available
    or if the file does not exist.

    Args:
        path: Path to the PDF file.

    Returns:
        Extracted text as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ImportError: If neither pymupdf nor pdfplumber is installed.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        return extract_with_pymupdf(path)
    except ImportError:
        pass

    try:
        return extract_with_pdfplumber(path)
    except ImportError:
        pass

    raise ImportError(
        "No PDF extraction library available. "
        "Install one with: pip install pymupdf  (or: pip install pdfplumber)"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_pdf_text.py input.pdf [output.md]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = get_output_path(
        input_path,
        sys.argv[2] if len(sys.argv) > 2 else None,
    )

    try:
        text = extract_text(input_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w") as f:
        f.write(text)
    print(f"Extracted {len(text)} chars -> {output_path}")


if __name__ == "__main__":
    main()
