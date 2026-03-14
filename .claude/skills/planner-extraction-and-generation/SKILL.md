# Planner Extraction & Generation

## 1. Overview

This skill covers the full pipeline for creating interactive digital planners sold under the **Our Forever Stories** brand (our-forever-stories.com). The process takes a source PDF planner (typically purchased as a reference/inspiration), extracts its structure, and rebuilds it as a fully original, interactive digital planner optimized for GoodNotes, Notability, and tablet use.

### Pipeline Summary

```
Source PDF  -->  Render pages to PNGs  -->  Analyze structure  -->  Write structure doc
     |
     v
Design System (colors, fonts, spacing)  -->  HTML + UnoCSS build  -->  Add interactivity
     |
     v
Puppeteer PDF generation  -->  Final interactive PDF (3-5 MB, 130+ pages)
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Markup | Single HTML file per planner |
| Styling | UnoCSS (Tailwind-like utility classes) + inline `<style>` for complex layouts |
| Fonts | Google Fonts via UnoCSS preset (Cormorant Garamond + Inter) |
| Build | Vite (auto-discovers `planners/*/index.html`) |
| PDF | Puppeteer (headless Chrome) |
| Shared styles | `shared/styles/print-base.css` |
| Config | `uno.config.ts` (palette + shortcuts), `vite.config.ts` (multi-entry build) |

---

## 2. Phase 1: PDF Analysis & Structure Extraction

### 2.1 Render PDF Pages to PNGs

```bash
# Create output directory
mkdir -p /tmp/planner-pages

# Render all pages as PNGs, downscaled to max 1200px wide
pdftoppm -png -scale-to 1200 input.pdf /tmp/planner-pages/page
```

**Why downscale:** The Claude API has a 2000px limit for multi-image requests. Source PDFs are often 2048x2732px. Always downscale to max 1200px to stay well within limits and allow batch analysis.

### 2.2 Extract Text for Section Mapping

```bash
pdftotext input.pdf output.txt
```

This gives a rough text dump for identifying section titles, page labels, and content groupings.

### 2.3 Analyze Pages Visually

Send batches of 10-20 PNG pages at a time to Claude for analysis. For each page, identify:

- **Page number and title**
- **Layout type** (cover, section divider, form, table, checklist, etc.)
- **Content category** (budget, guests, vendors, etc.)
- **Navigation elements** (tab colors, sub-nav items, home icon placement)
- **Unique vs. repetitive** (daily/weekly planner pages repeat hundreds of times)

### 2.4 Identify Unique vs. Repetitive Pages

Most planners have far fewer unique layouts than total pages. The wedding planner source had:
- **652 total pages** but only **~160 unique layouts**
- The remaining ~490 pages were repetitive weekly planners (72 pages) and daily planners (365 pages)

Focus on cataloguing the unique layout types -- repetitive pages follow the same template.

### 2.5 Create the Structure Document

Write a comprehensive structure doc following this format (reference: `WEDDING-PLANNER-STRUCTURE.md`):

```markdown
# Digital [Type] Planner - Full Structure Analysis

**Source:** [filename]
**Pages:** [count] | **Size:** [MB] | **Original:** [dimensions] | **Rendered:** [dimensions]
**Rendered images:** [path to PNGs]

---

## Design System
- Background, text color, fonts, table styling
- Tab colors for each section
- Top nav bar elements
- Footer style

---

## Page Map

### [Section Name] (Pages X-Y)
| Page | Title | Layout Type |
|------|-------|-------------|
| 1 | Cover | Full-page title, gradient background |
| 2 | Index | 3-column TOC with section links |
...

## Unique Layout Types (Templates to Recreate)
1. Cover
2. Section Divider
3. Form Page
...

## Content Sections Summary
| Section | Tab Color | Unique Pages | Key Templates |
...
```

---

## 3. Phase 2: Content Enrichment

The source PDF provides structural inspiration — section layout, page types, navigation patterns. But the actual content (labels, checklist items, form fields, categories) must be original and genuinely useful to the planner's target user. This phase decides **what to keep, what to rewrite, and what to add** — only where it meaningfully improves the planner.

### 3.1 The Rule: Enrich Only Where It Helps

Not every page needs enrichment. A blank "Notes" page is fine as-is. A budget table with 8 generic rows? That needs work. Apply this filter:

| Page Type | Enrichment Needed? | Why |
|-----------|-------------------|-----|
| Blank/lined/grid note pages | No | They're blank by design |
| Photo placement pages | No | Structure is the value |
| Section dividers | Light | Only tagline + page list |
| Form pages (write-in fields) | Medium | Better labels, more relevant fields |
| Checklists | Yes | Pre-filled items are the main value-add |
| Budget/comparison tables | Yes | Relevant row items save users real time |
| Schedules/timelines | Yes | Pre-filled time blocks and countdown tasks |

**The test:** Would a real user planning this event look at the page and think *"oh good, they already listed the things I need to track"*? If yes, enrich. If the page is meant to be filled in freely, leave it alone.

### 3.2 Three Types of Enrichment

#### Type A: Rewrite labels and headings (always do this)
Every heading, label, and field name must be in our own words. Never copy verbatim from the source.

- Source says "Photo & Video" → We write "Photography & Videography"
- Source says "Contact" → We write "Primary Contact Name"
- Source has no taglines → We add one per section divider (*"Every detail, side by side"*)

This is lightweight and applies to every page.

#### Type B: Pre-fill with domain-specific items (checklists, tables, timelines)
This is where the real value lives. Research what actual users track, then pre-fill.

**Do research first.** Before writing checklist items for a wedding emergency kit, look up what wedding planners actually recommend. Use Perplexity/web search for:
- "wedding emergency kit checklist" (real items people forget)
- "wedding budget breakdown categories" (industry-standard line items)
- "wedding planning timeline" (month-by-month tasks)

**Be specific, not generic:**

| Weak (generic) | Strong (domain-specific) |
|----------------|--------------------------|
| "Item 1, Item 2..." | "Bobby Pins, Clear Nail Polish, Stain Remover Pen..." |
| "Photographer Fee" | "Lead Photographer (8hr package)" |
| "3 months before" | "3 Months Before: Book florist, schedule cake tasting, order invitations" |

#### Type C: Add new pages (only if there's a clear gap)
Don't add pages just to pad the count. Add a page only if:
1. Real users commonly track this thing
2. The source PDF missed it
3. It fits naturally within an existing section

**Examples of justified additions:**
- Wedding planner missing a "Shot List" page → photographers and couples actually use these
- Travel planner missing "Visa & Documents" → travelers genuinely need this
- Baby planner missing "Feeding Log" → new parents track this daily

**Examples of unjustified additions (don't do these):**
- Adding a "Digital Backup" page to a printable planner → wrong medium
- Adding "Weather Contingency" as its own page → a single note line on the venue page suffices
- Adding "QR Code Tracker" → too niche, most users won't use it

### 3.3 Content Document

After enrichment, create `planners/{NAME}-CONTENT.md` containing:
- Rewritten section headings and taglines
- Complete pre-filled checklist items (every single one — the builder copies these directly)
- All form field labels
- Pre-filled table row items
- Any new pages being added, with justification

This document is the single source of truth for the HTML building phase. The builder should never need to refer back to the source PDF for content.

---

## 4. Phase 3: Design System Definition

The design system is defined across `uno.config.ts` and `shared/styles/print-base.css`. Every planner in the Our Forever Stories brand shares these foundations, with color variants per product line.

### 8.1 Fonts (from uno.config.ts)

```typescript
fonts: {
  heading: {
    name: 'Cormorant Garamond',
    weights: [400, 500, 600, 700],
    italic: true,
  },
  body: {
    name: 'Inter',
    weights: [300, 400, 500, 600],
  },
},
```

Usage:
- **Headings:** `font-heading` -- always uppercase, tracking-wide
- **Body/Labels:** `font-body` -- clean, readable at small sizes
- Use `font-heading italic` for taglines/subtitles

### 8.2 Color Palette (from uno.config.ts)

#### Wedding / Default Rose Palette

| Name | Key Shades | Usage |
|------|-----------|-------|
| prussian | `#0a1929` (900), `#eaf2fa` (50) | Primary text color |
| slate | `#617e9e` (500), `#a0b2c5` (300), `#27333f` (800) | Secondary text, labels, nav inactive |
| thistle | `#d8c0c8` (200), `#c4a1ac` (300), `#f5eff1` (50), `#ebe0e3` (100) | Borders, fills, subtle backgrounds |
| rose | `#c56d7d` (400), `#d3929e` (300), `#f8edef` (50), `#f0dbdf` (100) | Accent color, checkboxes, active nav, decorative elements |

#### Variant Palettes

| Product Line | Primary Accent | Border/Fill |
|-------------|---------------|-------------|
| Honeymoon / Travel | sage (`#6a9b56` to `#a5c399`) | fern (`#c7d4c3`, `#abbea5`) |
| Baby Boy | baby-blue (`#8BB5DB`, `#A7C7E7`) | `#B4D0E8`, `#D1E3F3` |
| Baby Girl | baby-pink (`#D9A0A6`, `#E8B4B8`) | `#E0BFC2`, `#F0D5D7` |
| Milestones / Baptism | milestone gold (`#C4A265`) | `#D4C4A0`, `#E8D5B0` |

### 8.3 Shared CSS Classes (from print-base.css)

```css
/* Checkbox -- Cotton Rose 300 border */
.checkbox {
  width: 16px;
  height: 16px;
  border: 1.5px solid #d3929e;
  border-radius: 2px;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Blank checkbox -- Thistle 300 border (more subtle) */
.checkbox-blank {
  width: 16px;
  height: 16px;
  border: 1.5px solid #c4a1ac;
  border-radius: 2px;
  flex-shrink: 0;
  margin-top: 1px;
}

/* Decorative gradient line below headers */
.section-line {
  height: 1.5px;
  background: linear-gradient(90deg, #c56d7d 0%, #d8c0c8 40%, transparent 100%);
}

/* Fill-in line for write-in fields */
.fill-line {
  border-bottom: 1px solid #c4a1ac;
  min-width: 200px;
  height: 1.1em;
}

/* Corner flourish L-shapes on content pages */
.corner-flourish { position: relative; }
.corner-flourish::before,
.corner-flourish::after {
  content: '';
  position: absolute;
  width: 30px;
  height: 30px;
  border-color: #d8c0c8;
  opacity: 0.4;
}
.corner-flourish::before {
  top: 0; left: 0;
  border-top: 1.5px solid;
  border-left: 1.5px solid;
}
.corner-flourish::after {
  top: 0; right: 0;
  border-top: 1.5px solid;
  border-right: 1.5px solid;
}
```

**Variant classes** follow the same pattern with suffix: `.checkbox-sage`, `.section-line-sage`, `.fill-line-sage`, `.corner-flourish-sage` (and similarly for `-baby-blue`, `-baby-pink`, `-milestone`).

### 8.4 UnoCSS Shortcuts (from uno.config.ts)

```typescript
shortcuts: {
  'print-page': 'w-full max-w-210mm mx-auto bg-white',
  'section-title': 'font-heading text-base font-600 tracking-wide uppercase',
  'check-item': 'flex items-start gap-2.5 py-0.75',
  'check-label': 'font-body text-13px text-prussian-900 leading-snug',
  'check-note': 'font-body text-11px text-slate-500 italic leading-snug',
  'page-header': 'text-center mb-4',
  'page-footer': 'text-center mt-4 pt-3 border-t border-thistle-100',
},
```

### 8.5 Typography Rules

| Element | Size | Weight | Extra |
|---------|------|--------|-------|
| Minimum text | 8px | -- | Only for calendar cells, legends |
| Labels | 9-10px | 500-600 | uppercase, tracking |
| Body text | 10-11px | 400-500 | -- |
| Checklist labels | 10px | 400 | text-slate-600 |
| Sub-nav tabs | 8px | 500 | uppercase, tracking-[0.06em] |
| Page titles (h1) | text-2xl (~20px) | 600 | uppercase, tracking-[0.08em], font-heading |
| Section divider titles | text-4xl (~36px) | 600 | uppercase, tracking-[0.15em], font-heading |
| Cover title | text-5xl (~48px) | 600 | uppercase, tracking-[0.2em], font-heading |
| Footer brand | 10px | 400 | text-rose-400, tracking-[0.2em], uppercase |
| Footer URL | 9px | 400 | text-slate-400 |

---

## 5. Phase 4: HTML Page Templates

Every page in the planner is a `<div>` with the `print-page` class and supporting utilities. Below are the exact HTML patterns for every page type.

### 8.a Cover Page

Centered vertically, gradient background, no sub-nav, no page-break (first page).

```html
<div id="cover" class="print-page min-h-297mm px-14mm py-8mm box-border relative corner-flourish flex flex-col items-center justify-center"
     style="background: linear-gradient(180deg, #fff 0%, #fdf8f9 40%, #f8edef 100%);">

  <div class="text-center">
    <p class="font-body text-10px tracking-[0.4em] uppercase text-rose-400 mb-6">Our Forever Stories</p>

    <h1 class="font-heading text-5xl font-600 text-prussian-900 leading-tight tracking-[0.15em] uppercase mb-3"
        style="letter-spacing: 0.2em;">Wedding</h1>
    <h1 class="font-heading text-5xl font-600 text-prussian-900 leading-tight tracking-[0.15em] uppercase mb-8"
        style="letter-spacing: 0.2em;">Planner</h1>

    <div class="w-20 h-0.5 bg-rose-400 mx-auto mb-8"></div>

    <p class="font-heading text-base italic text-slate-500 mb-6">
      Every detail, beautifully planned
    </p>

    <!-- Couple info fields -->
    <div class="flex flex-col items-center gap-3 mt-8 font-body text-12px text-slate-600">
      <div class="flex items-center gap-2">
        <span class="text-rose-400 font-500">Couple:</span>
        <span class="fill-line inline-block w-60"></span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-rose-400 font-500">Wedding Date:</span>
        <span class="fill-line inline-block w-52"></span>
      </div>
    </div>
  </div>

  <footer class="text-center mt-auto pt-4">
    <p class="font-body text-9px text-slate-400">our-forever-stories.com</p>
  </footer>
</div>
```

### 8.b Section Divider Page

Centered vertically with brand name, section title, decorative line, sub-nav tabs, and clickable section page links. Footer is just the URL (no brand name line).

```html
<div id="section-vendors" class="print-page min-h-297mm px-14mm py-8mm box-border page-break relative corner-flourish flex flex-col items-center justify-center">

  <div class="text-center">
    <p class="font-body text-10px tracking-[0.3em] uppercase text-rose-400 mb-4">Our Forever Stories</p>

    <h1 class="font-heading text-4xl font-600 text-prussian-900 leading-tight tracking-[0.15em] uppercase mb-3">Wedding Vendors</h1>

    <div class="w-16 h-0.5 bg-rose-400 mx-auto mb-8"></div>

    <div class="sub-nav mb-8" style="justify-content: center;">
      <a href="#page-79"><span class="active">Quote</span></a>
      <a href="#page-80"><span>Venue</span></a>
      <a href="#page-81"><span>Photo</span></a>
      <!-- ... more tabs -->
    </div>

    <div class="flex flex-col gap-3 items-center">
      <a href="#page-79" class="divider-link font-heading font-500 text-slate-400">Vendor Quote Comparison</a>
      <a href="#page-80" class="divider-link font-heading font-500 text-slate-400">Wedding Venue Comparison</a>
      <!-- ... more links -->
    </div>
  </div>

  <footer class="text-center mt-auto pt-4">
    <p class="font-body text-9px text-slate-400">our-forever-stories.com</p>
  </footer>
</div>
```

Key CSS for divider links and sub-nav (in `<head>` `<style>`):

```css
.divider-link {
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #a0b2c5;
  padding: 8px 0;
}

.sub-nav {
  display: flex;
  gap: 3px;
  justify-content: center;
  margin-bottom: 8px;
  flex-wrap: nowrap;
}
.sub-nav span {
  font-size: 8px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  border: 1px solid #ebe0e3;
  border-radius: 2px;
  color: #a0b2c5;
  white-space: nowrap;
}
.sub-nav span.active {
  background: #f8edef;
  color: #c56d7d;
  border-color: #e2b6be;
}
```

### 8.c Index / Table of Contents Page

Multi-column layout with grouped section links.

```html
<div id="index" class="print-page min-h-297mm px-14mm py-8mm box-border page-break relative corner-flourish flex flex-col">

  <header class="text-center pt-1 mb-4">
    <p class="font-body text-10px tracking-[0.3em] uppercase text-rose-400 mb-1">Our Forever Stories</p>
    <h1 class="font-heading text-3xl font-600 text-prussian-900 leading-tight tracking-[0.12em] uppercase mb-1">Index</h1>
    <div class="w-12 h-0.5 bg-rose-400 mx-auto mt-1.5 mb-1"></div>
    <p class="font-body text-11px text-slate-500">Everything you need, all in one place</p>
  </header>

  <div class="flex gap-3 flex-1">
    <!-- Column 1 -->
    <div class="flex-1 flex flex-col gap-1.5">
      <div class="toc-section">
        <a href="#section-overview"><h3>Year at a Glance</h3></a>
        <a href="#page-4" class="toc-item">Yearly Calendar</a>
        <a href="#page-5" class="toc-item">Year Overview</a>
        <!-- ... more items -->
      </div>
      <!-- More toc-sections -->
    </div>

    <!-- Column 2 -->
    <div class="flex-1 flex flex-col gap-1.5">
      <!-- toc-sections -->
    </div>

    <!-- Column 3 -->
    <div class="flex-1 flex flex-col gap-1.5">
      <!-- toc-sections -->
    </div>
  </div>

  <footer class="text-center mt-3 pt-2 border-t border-thistle-100">
    <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
    <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
  </footer>
</div>
```

TOC CSS (in `<head>` `<style>`):

```css
.toc-section {
  border: 1px solid #ebe0e3;
  border-radius: 2px;
  padding: 6px 8px;
  margin-bottom: 6px;
}
.toc-section h3 {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #c56d7d;
  margin: 0 0 3px 0;
  padding-bottom: 3px;
  border-bottom: 1px solid #f0dbdf;
}
.toc-item {
  font-size: 10px;
  padding: 2px 0;
  color: #27333f;
  display: flex;
  align-items: center;
  gap: 4px;
}
.toc-item::before {
  content: '';
  width: 4px;
  height: 4px;
  background: #d3929e;
  border-radius: 50%;
  flex-shrink: 0;
}
```

### 8.d Content Page with Table (Budget / Comparison)

Standard content page with header + sub-nav on the same baseline row, section line, optional header fields, and a table.

```html
<div id="page-79" class="print-page min-h-297mm px-14mm py-7mm box-border page-break relative corner-flourish flex flex-col">

  <!-- Header -->
  <div class="flex items-baseline justify-between mb-2">
    <h1 class="font-heading text-2xl font-600 text-prussian-900 tracking-[0.08em] uppercase">Vendor Quote Comparison</h1>
    <div class="sub-nav">
      <a href="#page-79"><span class="active">Quote</span></a>
      <a href="#page-80"><span>Venue</span></a>
      <!-- ... more tabs -->
    </div>
  </div>
  <div class="section-line mb-3"></div>

  <!-- Optional header fields (inline grid) -->
  <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 8px;">
    <div class="flex items-center gap-2">
      <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Overall Budget</span>
      <div class="fill-line" style="flex: 1;"></div>
    </div>
    <div class="flex items-center gap-2">
      <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Budget For</span>
      <div class="fill-line" style="flex: 1;"></div>
    </div>
    <div class="flex items-center gap-2">
      <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Priority</span>
      <div class="fill-line" style="flex: 1;"></div>
    </div>
  </div>

  <!-- Table -->
  <table class="budget-table" style="flex: 1;">
    <thead>
      <tr>
        <th style="width: 28%;">Details</th>
        <th style="width: 24%;">Vendor 1</th>
        <th style="width: 24%;">Vendor 2</th>
        <th style="width: 24%;">Vendor 3</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Company Name</td><td></td><td></td><td></td></tr>
      <tr><td>Contact Person</td><td></td><td></td><td></td></tr>
      <!-- ... more rows -->
    </tbody>
  </table>

  <footer class="text-center mt-2 pt-2 border-t border-thistle-100">
    <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
    <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
  </footer>
</div>
```

Budget table CSS (MUST be in `<head>` `<style>` -- not in print-base.css):

```css
.budget-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #ebe0e3;
}
.budget-table th {
  background: #f8edef;
  padding: 5px 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid #ebe0e3;
  text-align: center;
  color: #27333f;
}
.budget-table td {
  padding: 5px 6px;
  font-size: 10px;
  border: 1px solid #ebe0e3;
  text-align: center;
  height: 22px;
  color: #27333f;
}
.budget-table td:first-child {
  text-align: left;
  padding-left: 10px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.budget-table tr:nth-child(even) td {
  background: #fdf8f9;
}
.budget-table tr.budget-total td {
  background: #f8edef;
  font-weight: 600;
  border-top: 2px solid #d3929e;
}
.budget-table .paid-check {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 1.5px solid #d3929e;
  border-radius: 2px;
  vertical-align: middle;
}
```

### 8.e Content Page with Form Fields

Label + fill-line pairs for write-in information.

```html
<div id="page-12" class="print-page min-h-297mm px-14mm py-7mm box-border page-break relative corner-flourish flex flex-col">

  <div class="flex items-baseline justify-between mb-2">
    <h1 class="font-heading text-2xl font-600 text-prussian-900 tracking-[0.08em] uppercase">Wedding Details</h1>
    <div class="sub-nav">
      <a href="#page-12"><span class="active">Details</span></a>
      <a href="#page-13"><span>Our Story</span></a>
      <!-- ... -->
    </div>
  </div>
  <div class="section-line mb-4"></div>

  <p class="font-heading text-base italic text-slate-500 mb-4 text-center">The essential details for your special day</p>

  <!-- Form fields -->
  <div class="flex flex-col gap-4 mb-4">
    <div class="flex items-center gap-3">
      <span class="font-body text-11px font-600 text-prussian-900 uppercase tracking-wide" style="width: 130px; flex-shrink: 0;">Wedding Date</span>
      <div class="fill-line" style="flex: 1; min-width: 0;"></div>
    </div>
    <div class="flex items-center gap-3">
      <span class="font-body text-11px font-600 text-prussian-900 uppercase tracking-wide" style="width: 130px; flex-shrink: 0;">Ceremony Time</span>
      <div class="fill-line" style="flex: 1; min-width: 0;"></div>
    </div>
    <!-- ... more fields -->
  </div>

  <!-- Prompt boxes (label + lines) -->
  <div class="flex gap-3 mb-4">
    <div class="flex-1">
      <div class="prompt-label">Officiant</div>
      <div class="prompt-lines">
        <div class="space-y-2">
          <div class="fill-line w-full"></div>
          <div class="fill-line w-full"></div>
        </div>
      </div>
    </div>
    <div class="flex-1">
      <div class="prompt-label">Wedding Coordinator</div>
      <div class="prompt-lines">
        <div class="space-y-2">
          <div class="fill-line w-full"></div>
          <div class="fill-line w-full"></div>
        </div>
      </div>
    </div>
  </div>

  <footer class="text-center mt-auto pt-2 border-t border-thistle-100">
    <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
    <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
  </footer>
</div>
```

Prompt CSS (in `<head>` `<style>`):

```css
.prompt-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #27333f;
  background: #f8edef;
  padding: 4px 10px;
  border: 1px solid #ebe0e3;
  border-bottom: none;
}
.prompt-lines {
  border: 1px solid #ebe0e3;
  padding: 6px 10px;
}
```

### 8.f Checklist Page (3-Column Grid)

Pre-filled checkbox items organized in columns, often with a category header.

```html
<div id="page-76" class="print-page min-h-297mm px-14mm py-7mm box-border page-break relative corner-flourish flex flex-col">

  <div class="flex items-baseline justify-between mb-2">
    <h1 class="font-heading text-2xl font-600 text-prussian-900 tracking-[0.08em] uppercase">Decoration Checklist 1</h1>
    <div class="sub-nav">
      <!-- tabs -->
    </div>
  </div>
  <div class="section-line mb-3"></div>

  <!-- Category header -->
  <p class="font-body text-10px font-600 uppercase tracking-[0.08em] text-rose-400 mb-2 text-center">Ceremony</p>

  <!-- 3-column checkbox grid -->
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; flex: 1;">

    <!-- Column 1 -->
    <div style="border: 1px solid #ebe0e3;">
      <div class="flex items-center gap-2" style="padding: 4px 6px; border-bottom: 1px solid #f5eff1;">
        <div class="checkbox"></div>
        <span class="font-body text-10px text-slate-600">Arch / Arbour</span>
      </div>
      <div class="flex items-center gap-2" style="padding: 4px 6px; border-bottom: 1px solid #f5eff1;">
        <div class="checkbox"></div>
        <span class="font-body text-10px text-slate-600">Aisle Runner</span>
      </div>
      <!-- ... more items -->
      <div class="flex items-center gap-2" style="padding: 4px 6px;">
        <div class="checkbox"></div>
        <span class="font-body text-10px text-slate-600">Entrance Sign</span>
      </div>
    </div>

    <!-- Column 2 -->
    <div style="border: 1px solid #ebe0e3;">
      <!-- same pattern -->
    </div>

    <!-- Column 3 -->
    <div style="border: 1px solid #ebe0e3;">
      <!-- same pattern -->
    </div>

  </div>

  <!-- Notes box -->
  <div class="budget-notes mt-3">
    <div class="budget-notes-header"><h3>Notes</h3></div>
    <div class="budget-notes-body">
      <div class="fill-line w-full mt-2"></div>
      <div class="fill-line w-full mt-2"></div>
      <div class="fill-line w-full mt-2"></div>
    </div>
  </div>

  <footer class="text-center mt-2 pt-2 border-t border-thistle-100">
    <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
    <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
  </footer>
</div>
```

Note: The last item in each column omits `border-bottom` from its inline style.

### 8.g Contact Cards (2-Column Grid)

Cards with a colored header and labeled fill-line rows. Typically 8-12 cards per page.

```html
<!-- Contact Cards Grid -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; flex: 1;">

  <!-- Card -->
  <div style="border: 1px solid #ebe0e3; padding: 0;">
    <div style="background: #f8edef; padding: 3px 8px; border-bottom: 1px solid #ebe0e3;">
      <span class="font-body text-9px font-600 uppercase tracking-[0.06em]" style="color: #c56d7d;">Wedding Planner</span>
    </div>
    <div style="padding: 3px 8px;">
      <div class="flex items-center gap-2" style="padding: 2px 0; border-bottom: 1px solid #f5eff1;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Company</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
      <div class="flex items-center gap-2" style="padding: 2px 0; border-bottom: 1px solid #f5eff1;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Contact</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
      <div class="flex items-center gap-2" style="padding: 2px 0; border-bottom: 1px solid #f5eff1;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Phone</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
      <div class="flex items-center gap-2" style="padding: 2px 0; border-bottom: 1px solid #f5eff1;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Email</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
      <div class="flex items-center gap-2" style="padding: 2px 0; border-bottom: 1px solid #f5eff1;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Contract</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
      <div class="flex items-center gap-2" style="padding: 2px 0;">
        <span class="font-body text-9px text-slate-500" style="width: 55px; flex-shrink: 0;">Deposit</span>
        <div class="fill-line" style="flex: 1;"></div>
      </div>
    </div>
  </div>

  <!-- More cards... -->
</div>
```

### 8.h Note Papers

Five varieties, all sharing the same header pattern with Title + Date fields.

**Common header (all note types):**

```html
<div class="flex items-center gap-2 mb-3">
  <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Title</span>
  <div class="fill-line" style="flex: 1;"></div>
  <span class="font-body text-10px font-600 uppercase tracking-[0.04em] ml-4" style="white-space: nowrap;">Date</span>
  <div class="fill-line" style="width: 100px;"></div>
</div>
```

#### Dotted Grid

```html
<div style="flex: 1; background-image: radial-gradient(circle, #d8c0c8 0.7px, transparent 0.7px); background-size: 14px 14px; background-position: 7px 7px; border: 1px solid #f5eff1;"></div>
```

#### Lined

```html
<div style="flex: 1; border: 1px solid #f5eff1;">
  <div class="fill-line w-full" style="margin-top: 18px;"></div>
  <div class="fill-line w-full" style="margin-top: 18px;"></div>
  <!-- repeat ~25 times to fill the page -->
</div>
```

#### Small Grid

```html
<div style="flex: 1; background-image: linear-gradient(#ebe0e3 1px, transparent 1px), linear-gradient(90deg, #ebe0e3 1px, transparent 1px); background-size: 14px 14px; border: 1px solid #ebe0e3;"></div>
```

#### Blank

```html
<div style="flex: 1; border: 1px solid #f5eff1;"></div>
```

#### Cornell Notes

```html
<!-- Cornell layout: cue column + notes column -->
<div style="display: grid; grid-template-columns: 100px 1fr; flex: 1; border: 1px solid #ebe0e3;">

  <!-- Cue Column -->
  <div style="border-right: 1px solid #ebe0e3; padding: 8px;">
    <p class="font-body text-9px font-600 uppercase tracking-widest text-rose-300 mb-2">Cues</p>
    <div class="fill-line w-full mt-3"></div>
    <div class="fill-line w-full mt-3"></div>
    <!-- repeat ~18 times -->
  </div>

  <!-- Notes Column -->
  <div style="padding: 8px;">
    <p class="font-body text-9px font-600 uppercase tracking-widest text-rose-300 mb-2">Notes</p>
    <div class="fill-line w-full mt-3"></div>
    <div class="fill-line w-full mt-3"></div>
    <!-- repeat ~18 times -->
  </div>

</div>

<!-- Summary Section -->
<div style="border: 1px solid #ebe0e3; border-top: none; padding: 8px;">
  <p class="font-body text-9px font-600 uppercase tracking-widest text-rose-300 mb-2">Summary</p>
  <div class="fill-line w-full mt-2"></div>
  <div class="fill-line w-full mt-2"></div>
  <div class="fill-line w-full mt-2"></div>
</div>
```

### 8.i Photo Placement Page

Dashed border boxes with placeholder text and caption line.

```html
<!-- 6 photo placeholders in 2x3 grid -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; flex: 1;">
  <div style="border: 1.5px dashed #d8c0c8; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 120px;">
    <span class="font-body text-10px text-thistle-300 uppercase tracking-widest mb-1">Place a Photo Here</span>
    <div class="fill-line" style="width: 80px;"></div>
    <span class="font-body text-9px text-thistle-200 mt-1">Caption</span>
  </div>
  <!-- repeat 5 more times -->
</div>
```

### 8.j Venue Layout / Floor Plan Page

Dot grid for sketching with corner labels and a legend row.

```html
<!-- Venue info fields -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px;">
  <div class="flex items-center gap-2">
    <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Venue Name</span>
    <div class="fill-line" style="flex: 1;"></div>
  </div>
  <div class="flex items-center gap-2">
    <span class="font-body text-10px font-600 uppercase tracking-[0.04em]" style="white-space: nowrap;">Capacity</span>
    <div class="fill-line" style="flex: 1;"></div>
  </div>
</div>

<!-- Large dot grid area -->
<div style="flex: 1; border: 1px solid #ebe0e3; position: relative; background-image: radial-gradient(circle, #d8c0c8 0.8px, transparent 0.8px); background-size: 16px 16px; background-position: 8px 8px;">
  <span class="font-body text-8px text-thistle-300 uppercase" style="position: absolute; top: 6px; left: 8px;">Stage / Altar</span>
  <span class="font-body text-8px text-thistle-300 uppercase" style="position: absolute; top: 6px; right: 8px;">Entrance</span>
  <span class="font-body text-8px text-thistle-300 uppercase" style="position: absolute; bottom: 6px; left: 8px;">Bar / Catering</span>
  <span class="font-body text-8px text-thistle-300 uppercase" style="position: absolute; bottom: 6px; right: 8px;">Dance Floor</span>
</div>

<!-- Legend -->
<div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; margin-top: 6px; border: 1px solid #ebe0e3; padding: 5px 8px;">
  <div class="flex items-center gap-1">
    <div style="width: 10px; height: 10px; border-radius: 50%; border: 1px solid #c56d7d;"></div>
    <span class="font-body text-8px text-slate-500">Round Table</span>
  </div>
  <div class="flex items-center gap-1">
    <div style="width: 12px; height: 6px; border: 1px solid #c56d7d;"></div>
    <span class="font-body text-8px text-slate-500">Long Table</span>
  </div>
  <!-- more legend items -->
</div>
```

---

## 6. Phase 5: Building Process

### 8.1 File Location

Every planner lives at:
```
starter-kit/planners/{planner-name}/index.html
```

The Vite config auto-discovers planners via the glob pattern `planners/**/index.html`.

### 8.2 HTML Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>[Planner Name] -- Our Forever Stories</title>
  <link rel="stylesheet" href="../../shared/styles/print-base.css" />
  <script type="module" src="../../shared/main.ts"></script>
  <style>
    /* ══ All inline styles for this planner ══ */
    /* Budget tables, sub-nav, TOC, divider links, etc. */
    /* These are NOT in print-base.css */

    /* Link reset for interactive PDF */
    a { color: inherit; text-decoration: none; }
    a:visited { color: inherit; }
    .sub-nav a { color: inherit; text-decoration: none; }
    .sub-nav a:visited { color: inherit; }
    .sub-nav a span { color: inherit; }
  </style>
</head>
<body class="font-body bg-white text-prussian-900 m-0 p-0">

  <!-- Pages go here -->

</body>
</html>
```

The `shared/main.ts` provides UnoCSS and Tailwind reset:
```typescript
import 'virtual:uno.css'
import '@unocss/reset/tailwind.css'
```

### 8.3 Building in Batches

Build pages in batches of 3-5 pages per edit to avoid output token limits. Insert new pages before `</body>`.

### 8.4 Page Structure

Every page (except the cover) uses this wrapper:

```html
<!-- ════════════════════════════════════════════════════════════════
     PAGE XX: PAGE TITLE
     ════════════════════════════════════════════════════════════════ -->
<div id="page-XX" class="print-page min-h-297mm px-14mm py-7mm box-border page-break relative corner-flourish flex flex-col">

  <!-- Content here -->

  <footer class="text-center mt-2 pt-2 border-t border-thistle-100">
    <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
    <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
  </footer>
</div>
```

Key differences by page type:
- **Content pages:** `py-7mm`, standard flex-col
- **Section dividers:** `py-8mm`, add `items-center justify-center`
- **Cover:** `py-8mm`, add `items-center justify-center`, no `page-break`, has gradient background

### 8.5 Sub-Nav on Every Content Page

Every content page (non-divider) has a sub-nav in the header row. The current page's tab gets `class="active"`:

```html
<div class="flex items-baseline justify-between mb-2">
  <h1 class="font-heading text-2xl font-600 text-prussian-900 tracking-[0.08em] uppercase">Page Title</h1>
  <div class="sub-nav">
    <a href="#page-79"><span class="active">Current</span></a>
    <a href="#page-80"><span>Other</span></a>
    <!-- ... -->
  </div>
</div>
<div class="section-line mb-3"></div>
```

### 8.6 Footer Variants

**Standard content page footer:**
```html
<footer class="text-center mt-2 pt-2 border-t border-thistle-100">
  <p class="font-body text-10px text-rose-400 tracking-[0.2em] uppercase">Our Forever Stories</p>
  <p class="font-body text-9px text-slate-400 mt-0.5">our-forever-stories.com</p>
</footer>
```

**Section divider footer (URL only):**
```html
<footer class="text-center mt-auto pt-4">
  <p class="font-body text-9px text-slate-400">our-forever-stories.com</p>
</footer>
```

**Cover footer (URL only, mt-auto):**
```html
<footer class="text-center mt-auto pt-4">
  <p class="font-body text-9px text-slate-400">our-forever-stories.com</p>
</footer>
```

### 8.7 Page Comment Blocks

Every page is preceded by a comment block for easy navigation:

```html
<!-- ════════════════════════════════════════════════════════════════
     PAGE XX: PAGE TITLE
     ════════════════════════════════════════════════════════════════ -->
```

### 8.8 Build Command

```bash
cd /var/www/vibe-marketing/projects/our-forever-stories/starter-kit
npx vite build
```

Or using pnpm:
```bash
pnpm build
```

### 8.9 Build Verification

```bash
# Check built output exists
ls -la dist/planners/wedding-planner/index.html

# Count pages (page-break divs = total pages minus 1)
grep -c "page-break" planners/wedding-planner/index.html

# Check file size (source HTML is typically 400-800KB)
wc -l planners/wedding-planner/index.html
```

---

## 7. Phase 6: Making It Interactive

### 8.1 Add ID Attributes

Every page `<div>` needs a unique `id`:
- Cover: `id="cover"`
- Index: `id="index"`
- Section dividers: `id="section-{name}"` (e.g., `section-budget`, `section-vendors`)
- Content pages: `id="page-{number}"` (e.g., `page-79`, `page-80`)

### 8.2 Convert Nav to Links

**Sub-nav tabs:** Wrap each `<span>` in an `<a>`:
```html
<!-- Before -->
<span class="active">Quote</span>
<span>Venue</span>

<!-- After -->
<a href="#page-79"><span class="active">Quote</span></a>
<a href="#page-80"><span>Venue</span></a>
```

**Divider page links:** Convert `<p>` to `<a>`:
```html
<!-- Before -->
<p class="divider-link ...">Vendor Quote Comparison</p>

<!-- After -->
<a href="#page-79" class="divider-link ...">Vendor Quote Comparison</a>
```

**TOC entries:** Wrap in `<a>`:
```html
<a href="#page-42" class="toc-item">Photo & Video</a>
```

### 8.3 Link CSS Reset

Add to `<head>` `<style>` to prevent blue underlined links:

```css
a { color: inherit; text-decoration: none; }
a:visited { color: inherit; }
.sub-nav a { color: inherit; text-decoration: none; }
.sub-nav a:visited { color: inherit; }
.sub-nav a span { color: inherit; }
```

---

## 8. Phase 7: PDF Generation

### 8.1 Puppeteer Script

Create `planners/{planner-name}/generate-pdf.mjs`:

```javascript
/**
 * Generate interactive PDF from the planner HTML.
 *
 * Usage:
 *   cd /var/www/vibe-marketing/projects/our-forever-stories/starter-kit
 *   pnpm build
 *   node planners/{planner-name}/generate-pdf.mjs
 *
 * Or all-in-one (builds first):
 *   node planners/{planner-name}/generate-pdf.mjs --build
 */

import { execSync } from 'node:child_process'
import { resolve, join } from 'node:path'
import { existsSync, readFileSync } from 'node:fs'
import { createServer } from 'node:http'
import puppeteer from 'puppeteer'

const ROOT = resolve(import.meta.dirname, '..', '..')
const DIST = join(ROOT, 'dist')
const OUTPUT = join(import.meta.dirname, '{planner-name}.pdf')

const shouldBuild = process.argv.includes('--build')

function startServer(port = 4790) {
  return new Promise((res) => {
    const server = createServer((req, resp) => {
      let filePath = join(DIST, req.url === '/' ? 'index.html' : req.url)

      if (existsSync(filePath) && !filePath.includes('.')) {
        filePath = join(filePath, 'index.html')
      }

      if (!existsSync(filePath)) {
        resp.writeHead(404)
        resp.end('Not found')
        return
      }

      const ext = filePath.split('.').pop()
      const types = {
        html: 'text/html',
        css: 'text/css',
        js: 'application/javascript',
        json: 'application/json',
        png: 'image/png',
        jpg: 'image/jpeg',
        svg: 'image/svg+xml',
        woff2: 'font/woff2',
        woff: 'font/woff',
        ttf: 'font/ttf',
      }

      resp.writeHead(200, {
        'Content-Type': types[ext] || 'application/octet-stream',
        'Access-Control-Allow-Origin': '*',
      })
      resp.end(readFileSync(filePath))
    })

    server.listen(port, () => {
      console.log(`  Static server on http://localhost:${port}`)
      res(server)
    })
  })
}

async function main() {
  if (shouldBuild) {
    console.log('Building templates...')
    execSync('pnpm build', { cwd: ROOT, stdio: 'inherit' })
  }

  const htmlPath = join(DIST, 'planners', '{planner-name}', 'index.html')
  if (!existsSync(htmlPath)) {
    console.error('Built HTML not found. Run with --build flag or run `pnpm build` first.')
    process.exit(1)
  }

  const port = 4790
  const server = await startServer(port)

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
  })

  try {
    const page = await browser.newPage()

    const url = `http://localhost:${port}/planners/{planner-name}/`
    console.log(`  Loading ${url}...`)
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 })

    // Wait for web fonts
    await page.evaluateHandle('document.fonts.ready')

    // Extra wait for font rendering
    await new Promise(r => setTimeout(r, 1000))

    console.log('  Generating PDF...')
    await page.pdf({
      path: OUTPUT,
      format: 'A4',
      printBackground: true,
      margin: { top: '0mm', right: '0mm', bottom: '0mm', left: '0mm' },
      displayHeaderFooter: false,
      preferCSSPageSize: true,
    })

    console.log(`  Generated: ${OUTPUT}`)
    await page.close()
  } finally {
    await browser.close()
    server.close()
  }

  console.log('Done!')
}

main().catch(console.error)
```

### 8.2 Key Puppeteer Settings

| Setting | Value | Why |
|---------|-------|-----|
| `headless` | `true` | No visible browser window |
| `--no-sandbox` | flag | Required on Linux servers |
| `--disable-setuid-sandbox` | flag | Required on Linux servers |
| `--font-render-hinting=none` | flag | Cleaner font rendering |
| `waitUntil` | `'networkidle0'` | Wait for all fonts/assets to load |
| `document.fonts.ready` | evaluated | Explicitly wait for web fonts |
| `setTimeout 1000ms` | extra delay | Safety margin for font rendering |
| `format` | `'A4'` | Standard planner page size |
| `printBackground` | `true` | Render all CSS backgrounds |
| `margin` | all `'0mm'` | No browser-added margins (handled in CSS) |
| `preferCSSPageSize` | `true` | Use CSS `@page` size rules |

### 8.3 Running the Generation

```bash
cd /var/www/vibe-marketing/projects/our-forever-stories/starter-kit

# Build first, then generate
pnpm build && node planners/wedding-planner/generate-pdf.mjs

# Or all-in-one
node planners/wedding-planner/generate-pdf.mjs --build
```

### 8.4 Expected Output

- **File size:** 3-5 MB for 130+ page planner (the wedding planner is 3.6 MB / 137 pages)
- **Links:** Puppeteer automatically preserves HTML anchor links (`<a href="#page-XX">`) as internal PDF links -- no special configuration needed
- **Fonts:** Google Fonts are embedded via the UnoCSS web fonts preset

---

## 9. Pitfalls & Lessons Learned

### PDF Analysis Phase

- **PDF image size limit:** Never try to read full-resolution PDF pages (2048x2732px) in multi-image Claude API requests. Always downscale to max 1200px using `pdftoppm -scale-to 1200`.
- **Batch page analysis:** Send 10-20 pages at a time for visual analysis, not all at once.

### HTML Building Phase

- **Content filtering:** Very large HTML outputs from subagents can trigger content filtering. Build pages directly in the file or in small 3-5 page chunks if that happens.
- **Batch size:** Keep batches to 3-5 pages per edit to avoid output token limits.
- **Generic content trap:** Never use generic "life planner" content. Every label, checklist item, and section must be specific to the planner type (wedding, baby, travel, etc.). Pre-filled checklists with real, relevant items add significant value.
- **Build config pattern:** The `vite.config.ts` uses `planners/**/index.html` glob -- planners must be at that path to be auto-discovered.

### Styling Pitfalls

- **Text overflow in nav tabs:** Always use `white-space: nowrap` on sub-nav tab text. Tabs must never wrap.
- **Spacing issues:** Ensure proper `mb-2` or `mb-3` after headers and section-lines. Headers too close to content look cramped.
- **Border padding:** Never let text touch page borders. The page wrapper uses `px-14mm` for horizontal padding and `py-7mm` (content) or `py-8mm` (dividers/cover) for vertical.
- **Table styling:** Budget tables require inline styles in the `<head>` `<style>` block -- they are NOT in print-base.css. Always copy the full `.budget-table` CSS block into any new planner.
- **Fill-line min-width:** The `.fill-line` class has `min-width: 200px` in print-base.css. When using in flex layouts where it should shrink, add `style="flex: 1; min-width: 0;"`.

### PDF Generation Phase

- **Font loading:** Must use `waitUntil: 'networkidle0'` AND `document.fonts.ready` or Google Fonts may not render in the PDF.
- **Link preservation:** Puppeteer automatically converts HTML anchor links to internal PDF links. No special `tagged: true` or other flag needed.
- **Static server required:** Puppeteer must load from an HTTP server (not a file:// URL) to properly resolve CSS imports and font URLs. The generate-pdf.mjs script includes a built-in static server.
- **Build before generate:** Always run `pnpm build` before generating the PDF. The script reads from `dist/`, not from the source HTML.

---

## 10. Upcoming Planners

Each follows the same pipeline: PDF analysis --> structure doc --> design system --> HTML build --> interactive links --> PDF generation.

| Planner | Color Variant | Status |
|---------|--------------|--------|
| Wedding Planner | Rose (default) | Complete (137 pages, 3.6 MB) |
| Travel Planner | Sage green | Planned |
| Baby / Pregnancy Planner | Baby blue or baby pink | Planned |
| Life / Goals Planner | TBD | Planned |
| Fitness / Wellness Planner | TBD | Planned |

When creating a new planner:
1. Identify which color variant to use (or define a new one in `uno.config.ts` and `print-base.css`)
2. Use the corresponding CSS class variants (`.checkbox-sage`, `.section-line-sage`, etc.)
3. Follow the wedding planner as the canonical reference for structure and styling patterns

---

## 11. File Structure Reference

```
starter-kit/
├── index.html                         # Root index (links to all products)
├── uno.config.ts                      # Color palette, fonts, UnoCSS shortcuts
├── vite.config.ts                     # Multi-entry build config (auto-discovers planners)
├── package.json                       # Dependencies (vite, unocss, puppeteer)
├── shared/
│   ├── main.ts                        # UnoCSS + Tailwind reset imports
│   └── styles/
│       └── print-base.css             # Shared: checkbox, fill-line, section-line, corner-flourish
├── planners/
│   ├── WEDDING-PLANNER-STRUCTURE.md   # Structure analysis document
│   └── wedding-planner/
│       ├── index.html                 # Source HTML (12,738 lines, 137 pages)
│       ├── generate-pdf.mjs           # Puppeteer PDF generation script
│       └── wedding-planner.pdf        # Output (3.6 MB, 137 pages, interactive)
└── dist/                              # Vite build output (generated)
    └── planners/
        └── wedding-planner/
            └── index.html             # Built HTML with inlined CSS/fonts
```

---

## 12. Quick-Start Checklist for a New Planner

1. [ ] Obtain source PDF for reference/inspiration
2. [ ] Render pages: `pdftoppm -png -scale-to 1200 source.pdf /tmp/pages/page`
3. [ ] Extract text: `pdftotext source.pdf source.txt`
4. [ ] Analyze pages in batches, create `planners/{NAME}-STRUCTURE.md`
5. [ ] **Content enrichment:** Research domain, rewrite labels, pre-fill checklists/tables, create `planners/{NAME}-CONTENT.md`
6. [ ] Identify color variant; add to `uno.config.ts` and `print-base.css` if new
7. [ ] Create `planners/{name}/index.html` with full `<head>` (copy from wedding planner)
8. [ ] Build cover page (no page-break, gradient background)
9. [ ] Build index/TOC page
10. [ ] Build section dividers (one per major section)
11. [ ] Build content pages in batches of 3-5 (using CONTENT.md as source, not the PDF)
12. [ ] Add `id` attributes to all page divs
13. [ ] Convert all nav/TOC text to `<a href="#id">` links
14. [ ] Add link CSS reset to `<style>`
15. [ ] Verify build: `cd starter-kit && npx vite build`
16. [ ] Count pages: `grep -c "page-break" planners/{name}/index.html` (should be total - 1)
17. [ ] Create `planners/{name}/generate-pdf.mjs` (copy from wedding planner, update paths)
18. [ ] Generate PDF: `node planners/{name}/generate-pdf.mjs --build`
19. [ ] Verify PDF: check file size (3-5 MB expected), open and test all links
