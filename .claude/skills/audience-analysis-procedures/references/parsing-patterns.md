# Parsing Patterns

Common document structures the parser recognizes when extracting focus group profiles.

## Format 1: Markdown Heading with Quoted Name and Parenthesized Nickname

```
## Group N: "Group Name" (The Nickname)
**Category:** Category Name
**Overview:** Brief description...
### Demographics
- **Age Range:** 25-55
- **Gender:** 60% female, 40% male
...
### Core Desires
- Desire one
- Desire two
```

**Detection:** Regex `^#{1,3}\s+Group\s+\d+\s*:` at line start.

## Format 2: Bold Focus Group Header (Fitness Doc Format)

```
**FOCUS GROUP #N**

**Group Name**

*"The Nickname"*

**OVERVIEW**

Description text...

**DEMOGRAPHICS**

  ------------------ ---------
  **Age**            25-55
  **Gender**         60% female
  ...

**CORE DESIRES (What They Want)**

- Desire one
- Desire two
```

**Detection:** Regex `^\*\*FOCUS\s+GROUP\s+#\d+\*\*` at line start.
**Notes:**
- Name appears on the next non-empty bold line after the header
- Nickname appears as italic quoted text: `*"Nickname"*`
- May use escaped quotes: `*\"Nickname\"*`
- Demographics may use pandoc table format with `---` separator lines
- Section headings may include subtitles in parentheses: `**CORE DESIRES (What They Want)**`

## Format 3: Numbered Heading with Dash-Separated Nickname

```
# 1. Group Name - "The Nickname"
Category: Category Name
Overview: Description...
## Demographics
- Age Range: 25-55
...
```

**Detection:** Regex `^#{1,2}\s+\d+\.\s+\S` at line start.

## Section Heading Patterns

The parser recognizes these section headings (case-insensitive):

| Section | Alternate Names |
|---------|----------------|
| Demographics | DEMOGRAPHICS |
| Psychographics | PSYCHOGRAPHICS |
| Core Desires | CORE DESIRES, Core Desires (What They Want) |
| Pain Points | PAIN POINTS, Pain Points (What Frustrates Them) |
| Fears | Fears & Anxieties, FEARS & ANXIETIES |
| Beliefs | Beliefs & Worldview, BELIEFS & WORLDVIEW |
| Objections | Common Objections, COMMON OBJECTIONS (Why They Hesitate) |
| Emotional Triggers | EMOTIONAL TRIGGERS (What Activates Buying) |
| Language Patterns | LANGUAGE PATTERNS (Exact Phrases They Use) |
| Ebook Angles | Ebook Positioning Angles, EBOOK POSITIONING ANGLES |
| Marketing Hooks | Marketing Hooks & Headlines, MARKETING HOOKS & HEADLINES |
| Transformation Promise | TRANSFORMATION PROMISE |

## Bullet Item Formats

Items within sections may use these markers:
- Standard markdown: `- Item text` or `* Item text`
- Checkmark: `- Item text`
- Cross mark: `- Item text`
- Warning: `- Item text`
- Arrow: `-> Item text`
- Star: `* Item text`
- Italic quoted: `*"Quoted text"*`
- Bold numbered: `**1. "Title text"**`

The parser strips all marker prefixes and quote formatting to extract clean text.

## Table-Style Demographics

Some documents use pandoc-style tables for structured data:

```
  -------------------- --------------------------------------------------
  **Field Name**       Value text that may span
                       multiple lines
  -------------------- --------------------------------------------------
```

The parser detects `**FieldName**` followed by value text and joins multi-line values.
