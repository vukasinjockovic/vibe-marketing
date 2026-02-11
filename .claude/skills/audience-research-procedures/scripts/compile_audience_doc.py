#!/usr/bin/env python3
"""Compile research data into a comprehensive audience intelligence document.

Usage:
    python compile_audience_doc.py \
        --product-name "GymZilla Training Program" \
        --project-slug "gymzilla" \
        --research-data /path/to/research.json \
        --output /path/to/output.md

Takes all research data as input (JSON from other scripts) and generates
a comprehensive markdown document following the focus-group-template.md format.
"""

import argparse
import json
import sys
import os
from datetime import datetime


def load_research_data(filepath):
    """Load research data from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading research data: {e}", file=sys.stderr)
        return None


def generate_table_of_contents(focus_groups):
    """Generate a table of contents organized by category."""
    categories = {}
    for i, group in enumerate(focus_groups, 1):
        category = group.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "number": i,
            "name": group.get("name", f"Group {i}"),
            "nickname": group.get("nickname", "")
        })

    lines = ["## TABLE OF CONTENTS\n"]
    for category, groups in categories.items():
        lines.append(f"**{category.upper()}**\n")
        for group in groups:
            nickname_str = f' - "{group["nickname"]}"' if group["nickname"] else ""
            lines.append(f'{group["number"]}. {group["name"]}{nickname_str}\n')
        lines.append("")

    return "\n".join(lines)


def format_focus_group(group, number):
    """Format a single focus group profile into markdown."""
    sections = []

    # Header
    name = group.get("name", f"Group {number}")
    nickname = group.get("nickname", "")
    category = group.get("category", "")

    sections.append(f"---\n")
    sections.append(f"## FOCUS GROUP #{number}\n")
    sections.append(f"**{name}**\n")
    if nickname:
        sections.append(f'*"{nickname}"*\n')

    # Overview
    overview = group.get("overview", "")
    if overview:
        sections.append(f"**OVERVIEW**\n")
        sections.append(f"{overview}\n")

    # Demographics
    demographics = group.get("demographics", {})
    if demographics:
        sections.append("**DEMOGRAPHICS**\n")
        sections.append("| Field | Value |")
        sections.append("| --- | --- |")
        if demographics.get("ageRange"):
            sections.append(f'| **Age** | {demographics["ageRange"]} |')
        if demographics.get("gender"):
            sections.append(f'| **Gender** | {demographics["gender"]} |')
        if demographics.get("income"):
            sections.append(f'| **Income** | {demographics["income"]} |')
        if demographics.get("lifestyle"):
            sections.append(f'| **Lifestyle** | {demographics["lifestyle"]} |')
        if demographics.get("triggers"):
            triggers = ", ".join(demographics["triggers"])
            sections.append(f'| **Triggers** | {triggers} |')
        sections.append("")

    # Psychographics
    psychographics = group.get("psychographics", {})
    if psychographics:
        sections.append("**PSYCHOGRAPHICS**\n")
        sections.append("| Field | Value |")
        sections.append("| --- | --- |")
        if psychographics.get("values"):
            values = ", ".join(psychographics["values"])
            sections.append(f'| **Values** | {values} |')
        if psychographics.get("beliefs"):
            beliefs = ", ".join(psychographics["beliefs"])
            sections.append(f'| **Beliefs** | {beliefs} |')
        if psychographics.get("lifestyle"):
            sections.append(f'| **Lifestyle** | {psychographics["lifestyle"]} |')
        if psychographics.get("identity"):
            sections.append(f'| **Identity** | {psychographics["identity"]} |')
        sections.append("")

    # List sections with custom markers
    list_fields = [
        ("coreDesires", "CORE DESIRES (What They Want)", "V"),
        ("painPoints", "PAIN POINTS (What Frustrates Them)", "X"),
        ("fears", "FEARS & ANXIETIES", "!"),
        ("beliefs", "BELIEFS & WORLDVIEW", "*"),
        ("objections", "COMMON OBJECTIONS (Why They Hesitate)", None),
        ("emotionalTriggers", "EMOTIONAL TRIGGERS (What Activates Buying)", ">"),
        ("languagePatterns", "LANGUAGE PATTERNS (Exact Phrases They Use)", None),
        ("ebookAngles", "EBOOK POSITIONING ANGLES", None),
        ("marketingHooks", "MARKETING HOOKS & HEADLINES", "*"),
    ]

    for field_key, heading, marker in list_fields:
        items = group.get(field_key, [])
        if items:
            sections.append(f"**{heading}**\n")
            for item in items:
                if field_key == "languagePatterns":
                    sections.append(f'*"{item}"*\n')
                elif field_key == "objections":
                    sections.append(f'*"{item}"*\n')
                elif field_key == "ebookAngles":
                    sections.append(f'**{item}**\n')
                elif marker:
                    sections.append(f'{marker} {item}\n')
                else:
                    sections.append(f'- {item}\n')
            sections.append("")

    # Transformation Promise
    promise = group.get("transformationPromise", "")
    if promise:
        sections.append("**TRANSFORMATION PROMISE**\n")
        sections.append(f"**{promise}**\n")

    # Awareness Stage
    awareness = group.get("awarenessStage", "")
    confidence = group.get("awarenessConfidence", "")
    signals = group.get("awarenessSignals", {})
    if awareness:
        sections.append("**AWARENESS STAGE**\n")
        sections.append(f"**Stage:** {awareness}")
        if confidence:
            sections.append(f"**Confidence:** {confidence}")
        if signals:
            signal_parts = []
            if signals.get("beliefsSignal"):
                signal_parts.append(f"Beliefs: {signals['beliefsSignal']}")
            if signals.get("objectionsSignal"):
                signal_parts.append(f"Objections: {signals['objectionsSignal']}")
            if signals.get("languageSignal"):
                signal_parts.append(f"Language: {signals['languageSignal']}")
            if signal_parts:
                sections.append(f"**Signals:** {'; '.join(signal_parts)}")
        sections.append("")

    return "\n".join(sections)


def compile_document(product_name, project_slug, focus_groups, research_metadata=None):
    """Compile the full audience intelligence document."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    group_count = len(focus_groups)

    # Count categories
    categories = list(dict.fromkeys(g.get("category", "Uncategorized") for g in focus_groups))

    doc_parts = []

    # Title and metadata
    doc_parts.append(f"# {product_name.upper()}\n")
    doc_parts.append("# AUDIENCE INTELLIGENCE DOCUMENT\n")
    doc_parts.append(f"**{group_count} Detailed Audience Profiles**\n")
    doc_parts.append(f"*Generated: {timestamp}*\n")
    doc_parts.append(f"*For: {product_name} Marketing Strategy*\n")

    # How to use
    doc_parts.append("## HOW TO USE THIS DOCUMENT\n")
    doc_parts.append(f"This document maps {group_count} distinct focus groups (audience segments) "
                     f"for {product_name}. Each profile includes:\n")
    doc_parts.append("- **Demographics & Psychographics** - Who they are and how they think")
    doc_parts.append("- **Core Desires** - What they deeply want (emotional drivers)")
    doc_parts.append("- **Pain Points** - What frustrates them (problems to solve)")
    doc_parts.append("- **Fears & Beliefs** - What they're afraid of and what they believe")
    doc_parts.append("- **Objections** - Why they hesitate to buy")
    doc_parts.append("- **Emotional Triggers** - What activates their buying desire")
    doc_parts.append("- **Language Patterns** - Exact phrases they use (for copy)")
    doc_parts.append("- **Ebook Angles** - Title/positioning ideas for this audience")
    doc_parts.append("- **Marketing Hooks** - Headlines and hooks that resonate")
    doc_parts.append("- **Transformation Promise** - The before->after journey")
    doc_parts.append("- **Awareness Stage** - Where they are in the buying journey\n")
    doc_parts.append("*Use for: Creating targeted ebooks, writing marketing copy, "
                     "developing ad campaigns, and positioning content for specific audiences.*\n")

    # Research metadata
    if research_metadata:
        doc_parts.append("## RESEARCH METHODOLOGY\n")
        sources = research_metadata.get("sources_used", [])
        if sources:
            doc_parts.append("**Data Sources Used:**")
            for source in sources:
                doc_parts.append(f"- {source}")
            doc_parts.append("")
        quality = research_metadata.get("research_quality", "")
        if quality:
            doc_parts.append(f"**Research Quality:** {quality}\n")

    # Table of contents
    doc_parts.append(generate_table_of_contents(focus_groups))

    # Focus group profiles
    for i, group in enumerate(focus_groups, 1):
        doc_parts.append(format_focus_group(group, i))

    return "\n".join(doc_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Compile research data into audience intelligence document"
    )
    parser.add_argument("--product-name", required=True,
                        help="Product name")
    parser.add_argument("--project-slug", required=True,
                        help="Project slug for file paths")
    parser.add_argument("--research-data", required=True,
                        help="Path to research data JSON file")
    parser.add_argument("--output", required=True,
                        help="Output markdown file path")

    args = parser.parse_args()

    # Load research data
    data = load_research_data(args.research_data)
    if not data:
        print("Failed to load research data", file=sys.stderr)
        sys.exit(1)

    focus_groups = data.get("focus_groups", [])
    if not focus_groups:
        print("No focus groups found in research data", file=sys.stderr)
        sys.exit(1)

    research_metadata = data.get("metadata", {})

    # Compile the document
    document = compile_document(
        product_name=args.product_name,
        project_slug=args.project_slug,
        focus_groups=focus_groups,
        research_metadata=research_metadata
    )

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write output
    with open(args.output, "w") as f:
        f.write(document)

    print(f"Document written to {args.output}", file=sys.stderr)
    print(f"Focus groups: {len(focus_groups)}", file=sys.stderr)
    print(f"Categories: {len(set(g.get('category', '') for g in focus_groups))}", file=sys.stderr)

    # Also output summary JSON to stdout for the agent to use
    summary = {
        "status": "success",
        "output_path": args.output,
        "focus_group_count": len(focus_groups),
        "categories": list(dict.fromkeys(g.get("category", "") for g in focus_groups)),
        "document_length": len(document)
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
