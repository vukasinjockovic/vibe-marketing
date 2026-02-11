#!/usr/bin/env python3
"""Parse audience research documents into structured focus group profiles.

Usage:
    python parse_audience_doc.py input.md [--output output.json]

Supports multiple document formats:
    - Markdown with ## Group N: "Name" (Nickname) headings
    - Bold heading format: **FOCUS GROUP #N** / **Name** / *"Nickname"*
    - Numbered heading format: # N. Name - "Nickname"
    - Table-style demographics (pandoc table separators)

Output: JSON array of structured focus group objects with completeness scores.
"""
import json
import re
import sys
import argparse
from typing import Optional


# ── Field weights for completeness scoring ──
# These weights determine how important each field is to the overall score.
FIELD_WEIGHTS = {
    "awarenessStage": 15,
    "sophisticationLevel": 10,
    "contentPreferences": 10,
    "influenceSources": 10,
    "purchaseBehavior": 15,
    "competitorContext": 10,
    "communicationStyle": 10,
    "seasonalContext": 5,
    "negativeTriggers": 10,
    "awarenessSignals": 5,
}

# Total possible weight
TOTAL_WEIGHT = sum(FIELD_WEIGHTS.values())


# ═══════════════════════════════════════════
# SECTION SPLITTING
# ═══════════════════════════════════════════

# Patterns that indicate the start of a new focus group section
GROUP_START_PATTERNS = [
    # ## Group N: "Name" (Nickname)
    re.compile(r'^#{1,3}\s+Group\s+\d+\s*:', re.MULTILINE),
    # **FOCUS GROUP #N**
    re.compile(r'^\*\*FOCUS\s+GROUP\s+#\d+\*\*', re.MULTILINE),
    # # N. Name - "Nickname"
    re.compile(r'^#{1,2}\s+\d+\.\s+\S', re.MULTILINE),
]


def split_into_groups(text: str) -> list[str]:
    """Split a document into individual focus group text blocks.

    Identifies section boundaries using heading patterns and returns
    the text of each group section.

    Args:
        text: The full document text.

    Returns:
        List of text blocks, one per focus group found.
    """
    if not text or not text.strip():
        return []

    # Collect all match positions across all patterns
    boundaries = []
    for pattern in GROUP_START_PATTERNS:
        for match in pattern.finditer(text):
            boundaries.append(match.start())

    # Also detect the bold-name format used in the actual fitness doc:
    # **FOCUS GROUP #N** followed by **Name** on a subsequent line
    focus_group_header = re.compile(
        r'^\*\*FOCUS\s+GROUP\s+#(\d+)\*\*',
        re.MULTILINE,
    )
    for match in focus_group_header.finditer(text):
        pos = match.start()
        if pos not in boundaries:
            boundaries.append(pos)

    if not boundaries:
        return []

    boundaries = sorted(set(boundaries))

    # Extract text blocks between boundaries
    groups = []
    for i, start in enumerate(boundaries):
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(text)
        block = text[start:end].strip()
        if block:
            groups.append(block)

    return groups


# ═══════════════════════════════════════════
# NAME / NICKNAME EXTRACTION
# ═══════════════════════════════════════════

def extract_name_and_nickname(
    heading: str,
    subheading: str = None,
) -> tuple[str, Optional[str]]:
    """Extract focus group name and nickname from heading text.

    Handles multiple formats:
        - ## Group N: "Name" (Nickname)
        - **Name** with *"Nickname"* on next line
        - # N. Name - "Nickname"
        - ## Name

    Args:
        heading: The primary heading line.
        subheading: Optional second line (for bold-name format).

    Returns:
        Tuple of (name, nickname). Nickname may be None.
    """
    name = ""
    nickname = None

    # Strip markdown formatting
    clean = heading.strip()
    clean = re.sub(r'^#{1,6}\s*', '', clean)  # Remove heading markers
    clean = re.sub(r'^\*\*', '', clean)        # Remove leading bold
    clean = re.sub(r'\*\*$', '', clean)        # Remove trailing bold

    # Format: Group N: "Name" (Nickname)
    m = re.match(
        r'(?:Group\s+\d+\s*:\s*)?["\u201c]([^"\u201d]+)["\u201d]\s*\(([^)]+)\)',
        clean,
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Format: N. Name - "Nickname"
    m = re.match(
        r'\d+\.\s+(.+?)\s*[-\u2013]\s*["\u201c]([^"\u201d]+)["\u201d]',
        clean,
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Format: **Name** with *"Nickname"* subheading
    if subheading:
        name = re.sub(r'\*+', '', clean).strip()
        # Handle escaped quotes (\"...\") and normal quotes ("..." or smart quotes)
        cleaned_sub = subheading.replace('\\', '')
        nick_match = re.search(r'["\u201c]([^"\u201d]+)["\u201d]', cleaned_sub)
        if nick_match:
            nickname = nick_match.group(1).strip()
        return name, nickname

    # Format: Group N: "Name" (no nickname)
    m = re.match(r'Group\s+\d+\s*:\s*["\u201c]([^"\u201d]+)["\u201d]', clean)
    if m:
        return m.group(1).strip(), None

    # Fallback: just clean the heading
    name = re.sub(r'\*+', '', clean).strip()
    # Try to extract nickname from parentheses
    paren_match = re.search(r'\(([^)]+)\)', name)
    if paren_match:
        nickname = paren_match.group(1).strip()
        name = name[:paren_match.start()].strip()

    return name, nickname


# ═══════════════════════════════════════════
# FIELD EXTRACTION HELPERS
# ═══════════════════════════════════════════

def extract_bullet_list(text: str, section_name: str) -> list[str]:
    """Extract bullet items from a named section.

    Looks for section headers like '### Section Name' or '**SECTION NAME**'
    and collects bullet items until the next section.

    Args:
        text: The group text block.
        section_name: The section to look for (case-insensitive).

    Returns:
        List of extracted items (stripped of bullet markers).
    """
    # Build patterns for section header detection
    patterns = [
        # ### Section Name or ### Section Name (subtitle)
        re.compile(
            r'(?:^|\n)#{2,4}\s+' + re.escape(section_name) + r'[^\n]*\n',
            re.IGNORECASE,
        ),
        # **SECTION NAME** or **SECTION NAME (subtitle)**
        re.compile(
            r'(?:^|\n)\*\*' + re.escape(section_name).replace(r'\ ', r'\s+') + r'[^*]*\*\*\s*\n',
            re.IGNORECASE,
        ),
    ]

    section_text = None
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            start = match.end()
            # Find the next section header
            next_header = re.search(
                r'\n(?:#{2,4}\s|\*\*[A-Z])',
                text[start:],
            )
            end = start + next_header.start() if next_header else len(text)
            section_text = text[start:end]
            break

    if section_text is None:
        return []

    items = []
    for line in section_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Remove bullet markers and unicode markers
        cleaned = re.sub(r'^[-*\u2022\u2713\u2717\u26a0\u2192\u2605]\s*', '', line)
        # Remove italic markers around quotes
        cleaned = re.sub(r'^\*+', '', cleaned)
        cleaned = re.sub(r'\*+$', '', cleaned)
        # Remove leading/trailing quotes
        cleaned = re.sub(r'^["\u201c]', '', cleaned)
        cleaned = re.sub(r'["\u201d]$', '', cleaned)
        # Remove bold numbered items like **1. "Title"**
        cleaned = re.sub(r'^\*\*\d+\.\s*', '', cleaned)
        cleaned = re.sub(r'\*\*$', '', cleaned)
        cleaned = cleaned.strip()
        if cleaned and len(cleaned) > 2:
            items.append(cleaned)

    return items


def extract_labeled_value(text: str, label: str) -> Optional[str]:
    """Extract a single labeled value like '**Category:** Value' or 'Category: Value'.

    Args:
        text: The text to search in.
        label: The label to look for (case-insensitive).

    Returns:
        The extracted value, or None.
    """
    patterns = [
        re.compile(r'\*\*' + re.escape(label) + r'\*?\*?\s*:?\s*\*?\*?\s*(.+)', re.IGNORECASE),
        re.compile(r'(?:^|\n)\s*' + re.escape(label) + r'\s*:\s*(.+)', re.IGNORECASE),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            val = match.group(1).strip()
            # Clean trailing markdown
            val = re.sub(r'\*+$', '', val).strip()
            if val:
                return val
    return None


def extract_table_field(text: str, field_name: str) -> Optional[str]:
    """Extract a field value from pandoc-style table format.

    Handles:
        **Field**            Value text that may span
                             multiple lines

    Args:
        text: The text to search in.
        field_name: Field name (e.g., 'Age', 'Gender').

    Returns:
        The extracted value, or None.
    """
    pattern = re.compile(
        r'\*\*' + re.escape(field_name) + r'\*\*\s+(.+?)(?=\n\s*\n|\n\s*\*\*|\n\s*-{5,}|$)',
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    if match:
        val = match.group(1).strip()
        # Join multi-line values
        val = re.sub(r'\s*\n\s+', ' ', val)
        val = val.strip()
        if val:
            return val
    return None


def extract_demographics(text: str) -> Optional[dict]:
    """Extract demographics section with structured fields.

    Handles both bullet-list format and table format.
    """
    # Try bullet-list format first
    age = (
        extract_labeled_value(text, "Age Range")
        or extract_labeled_value(text, "Age")
        or extract_table_field(text, "Age")
    )
    gender = (
        extract_labeled_value(text, "Gender")
        or extract_table_field(text, "Gender")
    )
    income = (
        extract_labeled_value(text, "Income")
        or extract_table_field(text, "Income")
    )
    lifestyle_demo = (
        extract_labeled_value(text, "Lifestyle")
        or extract_table_field(text, "Lifestyle")
    )
    triggers_raw = (
        extract_labeled_value(text, "Triggers")
        or extract_table_field(text, "Triggers")
    )

    if not any([age, gender, income, lifestyle_demo]):
        return None

    triggers = []
    if triggers_raw:
        triggers = [t.strip() for t in re.split(r',\s*', triggers_raw) if t.strip()]

    return {
        "ageRange": age or "",
        "gender": gender or "",
        "income": income or "",
        "lifestyle": lifestyle_demo or "",
        "triggers": triggers,
    }


def extract_psychographics(text: str) -> Optional[dict]:
    """Extract psychographics section with structured fields."""
    # Look for values, beliefs, lifestyle, identity within the psychographics section
    psych_section = None
    psych_patterns = [
        re.compile(r'(?:^|\n)#{2,4}\s+Psychographics[^\n]*\n(.*?)(?=\n#{2,4}\s|\n\*\*[A-Z]|\Z)', re.IGNORECASE | re.DOTALL),
        re.compile(r'\*\*PSYCHOGRAPHICS\*\*\s*\n(.*?)(?=\n\*\*[A-Z]|\Z)', re.IGNORECASE | re.DOTALL),
    ]
    for p in psych_patterns:
        m = p.search(text)
        if m:
            psych_section = m.group(1)
            break

    if psych_section is None:
        return None

    values_raw = (
        extract_labeled_value(psych_section, "Values")
        or extract_table_field(psych_section, "Values")
    )
    beliefs_raw = (
        extract_labeled_value(psych_section, "Beliefs")
        or extract_table_field(psych_section, "Beliefs")
    )
    lifestyle_psych = (
        extract_labeled_value(psych_section, "Lifestyle")
        or extract_table_field(psych_section, "Lifestyle")
    )
    identity = (
        extract_labeled_value(psych_section, "Identity")
        or extract_table_field(psych_section, "Identity")
    )

    if not any([values_raw, beliefs_raw, lifestyle_psych, identity]):
        return None

    values_list = [v.strip() for v in re.split(r',\s*', values_raw)] if values_raw else []
    beliefs_list = [b.strip() for b in re.split(r',\s*', beliefs_raw)] if beliefs_raw else []

    return {
        "values": values_list,
        "beliefs": beliefs_list,
        "lifestyle": lifestyle_psych or "",
        "identity": identity or "",
    }


# ═══════════════════════════════════════════
# SINGLE GROUP PARSER
# ═══════════════════════════════════════════

def parse_single_group(text: str) -> dict:
    """Parse a single focus group text block into a structured dict.

    Args:
        text: The text block for one focus group.

    Returns:
        Dict with all extractable fields.
    """
    lines = text.split('\n')

    # Determine the heading format and extract name/nickname
    first_line = lines[0].strip() if lines else ""
    second_line = lines[1].strip() if len(lines) > 1 else ""
    third_line = lines[2].strip() if len(lines) > 2 else ""

    # Detect format
    name = ""
    nickname = None
    number = None

    # Format 1: ## Group N: "Name" (Nickname)
    group_num_match = re.match(r'(?:#{1,3}\s+)?Group\s+(\d+)', first_line)
    if group_num_match:
        number = int(group_num_match.group(1))
        name, nickname = extract_name_and_nickname(first_line)

    # Format 2: **FOCUS GROUP #N** -> **Name** -> *"Nickname"*
    elif re.match(r'\*\*FOCUS\s+GROUP\s+#(\d+)\*\*', first_line):
        num_match = re.match(r'\*\*FOCUS\s+GROUP\s+#(\d+)\*\*', first_line)
        number = int(num_match.group(1))
        # Name is on the next non-empty bold line
        name_line = ""
        nick_line = ""
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r'\*\*[^*]+\*\*$', stripped) and not name_line:
                name_line = stripped
            elif re.match(r'\*\\?["\u201c]', stripped) and name_line:
                nick_line = stripped
                break
            elif name_line:
                break
        if name_line:
            name, nickname = extract_name_and_nickname(name_line, nick_line)

    # Format 3: # N. Name - "Nickname"
    elif re.match(r'(?:#{1,2}\s+)?(\d+)\.\s+', first_line):
        num_match = re.match(r'(?:#{1,2}\s+)?(\d+)\.', first_line)
        number = int(num_match.group(1))
        name, nickname = extract_name_and_nickname(first_line)

    else:
        name, nickname = extract_name_and_nickname(first_line, second_line)

    # Extract all structured fields
    category = extract_labeled_value(text, "Category")
    overview = extract_labeled_value(text, "Overview")

    # If overview not found with label, check for **OVERVIEW** section
    if not overview:
        m = re.search(
            r'\*\*OVERVIEW\*\*\s*\n\n?(.*?)(?=\n\*\*|\n#{2,}|\Z)',
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if m:
            overview = m.group(1).strip()
            overview = re.sub(r'\s*\n\s*', ' ', overview)

    demographics = extract_demographics(text)
    psychographics = extract_psychographics(text)

    core_desires = extract_bullet_list(text, "Core Desires")
    pain_points = extract_bullet_list(text, "Pain Points")
    fears = extract_bullet_list(text, "Fears") or extract_bullet_list(text, "Fears & Anxieties")
    beliefs = extract_bullet_list(text, "Beliefs") or extract_bullet_list(text, "Beliefs & Worldview")
    objections = extract_bullet_list(text, "Objections") or extract_bullet_list(text, "Common Objections")
    emotional_triggers = extract_bullet_list(text, "Emotional Triggers")
    language_patterns = extract_bullet_list(text, "Language Patterns")
    ebook_angles = (
        extract_bullet_list(text, "Ebook Angles")
        or extract_bullet_list(text, "Ebook Positioning Angles")
    )
    marketing_hooks = (
        extract_bullet_list(text, "Marketing Hooks")
        or extract_bullet_list(text, "Marketing Hooks & Headlines")
    )

    # Transformation promise — try multiple heading formats
    transformation = extract_labeled_value(text, "Transformation Promise")
    if not transformation:
        # Try bold heading: **TRANSFORMATION PROMISE** or **Transformation Promise**
        m = re.search(
            r'\*\*(?:TRANSFORMATION\s+PROMISE|Transformation\s+Promise)\*\*\s*\n\n?(.*?)(?=\n\*\*|\n#{2,}|\Z)',
            text,
            re.DOTALL,
        )
        if m:
            transformation = m.group(1).strip()
            transformation = re.sub(r'\*+', '', transformation)
            transformation = re.sub(r'\s*\n\s*', ' ', transformation)
            transformation = transformation.strip()
    if not transformation:
        # Try markdown heading: ### Transformation Promise
        m = re.search(
            r'#{2,4}\s+Transformation\s+Promise[^\n]*\n\n?(.*?)(?=\n#{2,}|\n\*\*[A-Z]|\Z)',
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if m:
            transformation = m.group(1).strip()
            transformation = re.sub(r'\*+', '', transformation)
            transformation = re.sub(r'\s*\n\s*', ' ', transformation)
            transformation = transformation.strip()

    result = {
        "number": number,
        "name": name,
        "nickname": nickname,
        "category": category,
        "overview": overview,
        "demographics": demographics,
        "psychographics": psychographics,
        "coreDesires": core_desires,
        "painPoints": pain_points,
        "fears": fears,
        "beliefs": beliefs,
        "objections": objections,
        "emotionalTriggers": emotional_triggers,
        "languagePatterns": language_patterns,
        "ebookAngles": ebook_angles,
        "marketingHooks": marketing_hooks,
        "transformationPromise": transformation,
    }

    return result


# ═══════════════════════════════════════════
# COMPLETENESS SCORING
# ═══════════════════════════════════════════

def score_completeness(group: dict) -> tuple[float, list[str]]:
    """Score a parsed focus group for field completeness.

    Uses weighted scoring where enrichment-related fields carry more weight.

    Args:
        group: The parsed focus group dict.

    Returns:
        Tuple of (score_percentage, list_of_missing_field_names).
    """
    missing = []
    earned = 0

    for field, weight in FIELD_WEIGHTS.items():
        val = group.get(field)
        if val is None or val == "" or val == [] or val == {}:
            missing.append(field)
        else:
            earned += weight

    score = (earned / TOTAL_WEIGHT) * 100.0 if TOTAL_WEIGHT > 0 else 0.0
    return round(score, 1), missing


# ═══════════════════════════════════════════
# DOCUMENT-LEVEL PARSING
# ═══════════════════════════════════════════

def parse_document(text: str) -> list[dict]:
    """Parse a full document into a list of structured focus group profiles.

    Args:
        text: The full document text.

    Returns:
        List of dicts, each representing a focus group with completeness data.
    """
    if not text or not text.strip():
        return []

    blocks = split_into_groups(text)
    results = []

    for block in blocks:
        group = parse_single_group(block)
        if not group.get("name"):
            continue

        score, missing = score_completeness(group)
        group["completenessScore"] = score
        group["missingFields"] = missing

        results.append(group)

    return results


def parse_file(path: str) -> list[dict]:
    """Read a markdown file and parse it into focus group profiles.

    Args:
        path: Path to the markdown file.

    Returns:
        List of parsed focus group dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return parse_document(text)


import os


def main():
    parser = argparse.ArgumentParser(
        description="Parse audience research documents into structured focus group profiles"
    )
    parser.add_argument("input", help="Path to the markdown file")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    args = parser.parse_args()

    try:
        groups = parse_file(args.input)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(groups, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Parsed {len(groups)} focus groups -> {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
