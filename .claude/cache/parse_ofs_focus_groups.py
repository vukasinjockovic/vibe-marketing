#!/usr/bin/env python3
"""Parse Our Forever Stories focus groups document into JSON."""
import json
import re
import sys

INPUT_FILE = "/var/www/vibe-marketing/projects/our-forever-stories/Our_Forever_Stories_Focus_Groups_Marketing_Intelligence.md"
OUTPUT_FILE = "/var/www/vibe-marketing/.claude/cache/parsed-focus-groups-ofs.json"

# Category mapping by focus group number
CATEGORY_MAP = {
    1: "Wedding Life Stage",
    2: "Wedding Life Stage",
    3: "Wedding Life Stage",
    4: "Wedding Life Stage",
    5: "Wedding Life Stage",
    6: "Honeymoon & Travel Memories",
    7: "Honeymoon & Travel Memories",
    8: "Baby & Growing Family",
    9: "Baby & Growing Family",
    10: "Baby & Growing Family",
    11: "Baby & Growing Family",
    12: "Emotional & Psychological",
    13: "Emotional & Psychological",
    14: "Emotional & Psychological",
    15: "Emotional & Psychological",
    16: "Emotional & Psychological",
    17: "Gifting & Occasions",
    18: "Gifting & Occasions",
    19: "Gifting & Occasions",
    20: "Gifting & Occasions",
    21: "Home & Lifestyle",
    22: "Home & Lifestyle",
    23: "Home & Lifestyle",
    24: "Demographic & Regional",
    25: "Demographic & Regional",
    26: "Demographic & Regional",
    27: "Demographic & Regional",
    28: "Demographic & Regional",
}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting characters."""
    text = text.strip()
    # Remove bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic markers (only full wraps, not partial)
    text = re.sub(r'^\*(.+)\*$', r'\1', text)
    # Also handle inline italic markers
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    # Remove leading special characters
    text = re.sub(r'^[✓✗⚠→★]\s*', '', text)
    # Remove leading dash/bullet
    text = re.sub(r'^[-•]\s*', '', text)
    # Remove leading number + dot
    text = re.sub(r'^\d+\.\s*', '', text)
    # Remove surrounding quotes only if both sides match
    text = re.sub(r'^"(.+)"$', r'\1', text)
    text = re.sub(r'^\u201c(.+)\u201d$', r'\1', text)
    return text.strip()


def parse_table(lines: list[str]) -> dict[str, str]:
    """Parse a markdown table into a dict."""
    result = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('|---') or line.startswith('| Field'):
            continue
        if '|' not in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        # Filter empty parts from leading/trailing pipes
        parts = [p for p in parts if p]
        if len(parts) >= 2:
            key = strip_markdown(parts[0]).lower()
            value = strip_markdown(parts[1])
            result[key] = value
    return result


def parse_bullet_list(lines: list[str], prefix_pattern: str = None) -> list[str]:
    """Parse a bullet list, stripping prefix characters."""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cleaned = strip_markdown(line)
        if cleaned:
            items.append(cleaned)
    return items


def split_into_focus_groups(content: str) -> list[str]:
    """Split the document into individual focus group sections."""
    # Split on "FOCUS GROUP #N" headers
    pattern = r'\*\*FOCUS GROUP #\d+\*\*'
    parts = re.split(pattern, content)
    numbers = re.findall(r'\*\*FOCUS GROUP #(\d+)\*\*', content)

    if len(parts) < 2:
        print(f"ERROR: Found {len(parts)} parts, expected 29+")
        sys.exit(1)

    # First part is the preamble, skip it
    groups = []
    for i, num in enumerate(numbers):
        groups.append((int(num), parts[i + 1]))

    return groups


def find_section(text: str, header: str) -> str:
    """Find content between a section header and the next header."""
    # Escape special regex chars in header
    escaped_header = re.escape(header)
    # Try matching with ** bold markers
    pattern = rf'\*\*{escaped_header}\*\*\s*\n(.*?)(?=\n\*\*[A-Z]|\Z)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def parse_focus_group(number: int, text: str) -> dict:
    """Parse a single focus group section into structured data."""
    result = {
        "number": number,
        "category": CATEGORY_MAP.get(number, "Unknown"),
    }

    # Extract name (first bold line)
    name_match = re.search(r'^\*\*(.+?)\*\*', text.strip(), re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip()
    else:
        result["name"] = f"Focus Group {number}"

    # Extract nickname (italic line with quotes)
    nick_match = re.search(r'^\*"(.+?)"\*', text, re.MULTILINE)
    if nick_match:
        result["nickname"] = nick_match.group(1).strip()
    else:
        result["nickname"] = ""

    # Split into sections by ** headers
    sections = {}
    current_header = None
    current_lines = []

    for line in text.split('\n'):
        header_match = re.match(r'^\*\*([A-Z][A-Z &\'()]+(?:\s*\([^)]+\))?)\*\*\s*$', line.strip())
        if header_match:
            if current_header:
                sections[current_header] = current_lines
            current_header = header_match.group(1).strip()
            current_lines = []
        elif current_header:
            current_lines.append(line)

    if current_header:
        sections[current_header] = current_lines

    # Parse OVERVIEW
    overview_text = ""
    for key in sections:
        if 'OVERVIEW' in key:
            overview_text = '\n'.join(sections[key]).strip()
            # Remove any markdown
            overview_text = re.sub(r'\*\*(.+?)\*\*', r'\1', overview_text)
            overview_text = re.sub(r'\*(.+?)\*', r'\1', overview_text)
            break
    result["overview"] = overview_text

    # Parse DEMOGRAPHICS table
    demographics = {"ageRange": "", "gender": "", "income": "", "lifestyle": "", "triggers": []}
    for key in sections:
        if 'DEMOGRAPHICS' in key:
            table = parse_table(sections[key])
            demographics["ageRange"] = table.get("age", "")
            demographics["gender"] = table.get("gender", "")
            demographics["income"] = table.get("income", "")
            demographics["lifestyle"] = table.get("lifestyle", "")
            triggers_raw = table.get("triggers", "")
            if triggers_raw:
                # Split by comma, but be careful with commas inside phrases
                demographics["triggers"] = [t.strip() for t in re.split(r',\s*(?=[A-Za-z])', triggers_raw) if t.strip()]
            if table.get("location", ""):
                demographics["location"] = table.get("location", "")
            break
    result["demographics"] = demographics

    # Parse PSYCHOGRAPHICS table
    psychographics = {"values": [], "beliefs": [], "lifestyle": "", "identity": ""}
    for key in sections:
        if 'PSYCHOGRAPHICS' in key:
            table = parse_table(sections[key])
            values_raw = table.get("values", "")
            if values_raw:
                psychographics["values"] = [v.strip() for v in values_raw.split(',') if v.strip()]
            beliefs_raw = table.get("beliefs", "")
            if beliefs_raw:
                psychographics["beliefs"] = [b.strip() for b in re.split(r',\s*(?=[A-Za-z])', beliefs_raw) if b.strip()]
            psychographics["lifestyle"] = table.get("lifestyle", "")
            psychographics["identity"] = table.get("identity", "")
            break
    result["psychographics"] = psychographics

    # Parse CORE DESIRES
    result["coreDesires"] = []
    for key in sections:
        if 'CORE DESIRES' in key:
            result["coreDesires"] = parse_bullet_list(sections[key])
            break

    # Parse PAIN POINTS
    result["painPoints"] = []
    for key in sections:
        if 'PAIN POINTS' in key:
            result["painPoints"] = parse_bullet_list(sections[key])
            break

    # Parse FEARS & ANXIETIES
    result["fears"] = []
    for key in sections:
        if 'FEARS' in key:
            result["fears"] = parse_bullet_list(sections[key])
            break

    # Parse BELIEFS & WORLDVIEW
    result["beliefs"] = []
    for key in sections:
        if 'BELIEFS' in key and 'WORLDVIEW' in key:
            result["beliefs"] = parse_bullet_list(sections[key])
            break

    # Parse COMMON OBJECTIONS
    result["objections"] = []
    for key in sections:
        if 'OBJECTIONS' in key or 'COMMON OBJECTIONS' in key:
            result["objections"] = parse_bullet_list(sections[key])
            break

    # Parse EMOTIONAL TRIGGERS
    result["emotionalTriggers"] = []
    for key in sections:
        if 'EMOTIONAL TRIGGERS' in key:
            result["emotionalTriggers"] = parse_bullet_list(sections[key])
            break

    # Parse LANGUAGE PATTERNS
    result["languagePatterns"] = []
    for key in sections:
        if 'LANGUAGE PATTERNS' in key:
            result["languagePatterns"] = parse_bullet_list(sections[key])
            break

    # Parse CONTENT ANGLES (-> ebookAngles)
    result["ebookAngles"] = []
    for key in sections:
        if 'CONTENT ANGLES' in key:
            result["ebookAngles"] = parse_bullet_list(sections[key])
            break

    # Parse MARKETING HOOKS & HEADLINES
    result["marketingHooks"] = []
    for key in sections:
        if 'MARKETING HOOKS' in key:
            result["marketingHooks"] = parse_bullet_list(sections[key])
            break

    # Parse TRANSFORMATION PROMISE
    result["transformationPromise"] = ""
    for key in sections:
        if 'TRANSFORMATION PROMISE' in key:
            # Filter out --- separator lines and empty lines at end
            filtered_lines = [l for l in sections[key] if l.strip() and l.strip() != '---']
            raw = '\n'.join(filtered_lines).strip()
            # Remove bold markers
            raw = re.sub(r'\*\*(.+?)\*\*', r'\1', raw, flags=re.DOTALL)
            raw = re.sub(r'\*(.+?)\*', r'\1', raw, flags=re.DOTALL)
            # Clean up the arrow
            raw = raw.replace('\u2192', '->').replace('→', '->')
            result["transformationPromise"] = raw.strip()
            break

    return result


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    groups = split_into_focus_groups(content)
    print(f"Found {len(groups)} focus groups")

    parsed = []
    for number, text in groups:
        fg = parse_focus_group(number, text)
        parsed.append(fg)
        print(f"  #{number}: {fg['name']} ({fg['category']}) - "
              f"desires={len(fg['coreDesires'])}, pain={len(fg['painPoints'])}, "
              f"hooks={len(fg['marketingHooks'])}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(parsed)} focus groups to {OUTPUT_FILE}")

    # Validation
    if len(parsed) != 28:
        print(f"WARNING: Expected 28 focus groups, got {len(parsed)}")

    # Check for empty fields
    issues = []
    for fg in parsed:
        if not fg.get("name"):
            issues.append(f"#{fg['number']}: missing name")
        if not fg.get("overview"):
            issues.append(f"#{fg['number']}: missing overview")
        if not fg.get("coreDesires"):
            issues.append(f"#{fg['number']}: missing coreDesires")
        if not fg.get("painPoints"):
            issues.append(f"#{fg['number']}: missing painPoints")
        if not fg.get("marketingHooks"):
            issues.append(f"#{fg['number']}: missing marketingHooks")
        if not fg.get("transformationPromise"):
            issues.append(f"#{fg['number']}: missing transformationPromise")

    if issues:
        print(f"\nIssues found ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nAll focus groups validated - no missing required fields!")


if __name__ == '__main__':
    main()
