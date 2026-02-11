# Known Document Formats

## Format: Fitness Focus Groups (Primary)

**Source file:** `Fitness_Focus_Groups_Marketing_Intelligence.md`
**Groups:** 28 detailed audience profiles
**Product:** GymZilla / fitness content
**Status:** Fully supported by parser

### Structure

```
TABLE OF CONTENTS
  Category headings (bold, uppercase)
  Numbered list of groups with names and nicknames

Per-group sections:
  **FOCUS GROUP #N**
  **Group Name**
  *"The Nickname"*  (may use escaped quotes: *\"Nickname\"*)
  **OVERVIEW**
  Paragraph text
  **DEMOGRAPHICS**
  Pandoc table format (** Field ** Value)
  **PSYCHOGRAPHICS**
  Pandoc table format
  **CORE DESIRES (What They Want)**
  Bullet list with checkmark markers
  **PAIN POINTS (What Frustrates Them)**
  Bullet list with cross markers
  **FEARS & ANXIETIES**
  Bullet list with warning markers
  **BELIEFS & WORLDVIEW**
  Bullet list
  **COMMON OBJECTIONS (Why They Hesitate)**
  Italic quoted items
  **EMOTIONAL TRIGGERS (What Activates Buying)**
  Bullet list with arrow markers
  **LANGUAGE PATTERNS (Exact Phrases They Use)**
  Italic quoted items
  **EBOOK POSITIONING ANGLES**
  Bold numbered items
  **MARKETING HOOKS & HEADLINES**
  Bullet list with star markers
  **TRANSFORMATION PROMISE**
  Bold paragraph text
```

### Category Groups

1. PHYSICAL TRANSFORMATION DESIRES (Groups 1-5)
2. LIFESTYLE & CONVENIENCE DESIRES (Groups 6-9)
3. PSYCHOLOGICAL & EMOTIONAL DESIRES (Groups 10-13)
4. KNOWLEDGE & GUIDANCE DESIRES (Groups 14-17)
5. LIFE STAGE & GOAL-SPECIFIC DESIRES (Groups 18-20)
6. SOCIAL & EXTERNAL VALIDATION DESIRES (Groups 21-23)
7. FUNCTIONAL / ATHLETIC PERFORMANCE DESIRES (Groups 24-28)

### Parsing Notes

- Nickname line uses escaped quotes (`\"`) which need special handling
- Demographics use pandoc table separators (`------ ------`)
- Some bullet items use unicode markers (checkmark, cross, warning, arrow, star)
- Ebook angles are bold-numbered: `**1. "Title"**`
- Language patterns and objections are italic-quoted: `*"phrase"*`
- Transformation promise is bold text, may span multiple lines
- Category is NOT labeled within each group; it appears as a section heading above groups

### Extraction Quality (Verified)

From the real 4,762-line document:
- 28/28 groups detected and extracted
- 28/28 nicknames successfully extracted
- All array fields populated (5-9 items each)
- Demographics extracted from table format
- Psychographics extracted from table format
- Transformation promises extracted from bold sections
