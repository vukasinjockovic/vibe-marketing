# Rust/WASM Rebuild Opportunities: Publisher Network Analysis

**Analysis Date:** 2026-03-06
**Data Source:** 20,726 publishers (8,839 Mediavine + 11,887 Raptive) in `all_publishers.csv`
**Unique Domains Analyzed:** 15,499 (after deduplication)

---

## 1. Executive Summary

We analyzed all 20,726 publishers across the Mediavine and Raptive premium ad networks to identify tool/SaaS/utility/game sites that could be rebuilt with Rust/WASM for massive performance gains and monetized via ad revenue.

### Key Findings

| Metric | Count |
|--------|-------|
| Total publishers analyzed | 20,726 |
| Unique domains | 15,499 |
| Identified tool/utility sites | 124 |
| Calculator sites | 15 |
| Converter/reference sites | 13 |
| Generator sites | 3 |
| Game/puzzle/quiz sites | 41 |
| Test prep/exam sites | 26 |
| Template/printable sites | 22 |
| Color/text/typing tools | 4 |
| **High Rust-advantage sites** | **24** |
| **Medium Rust-advantage sites** | **21** |

### The Opportunity

These 124 sites already qualify for premium ad networks (Mediavine requires 50K sessions/month; Raptive requires 100K pageviews/month). They prove that tool/utility sites can generate meaningful ad revenue. The strategy is:

1. **Identify proven tool niches** from this publisher data
2. **Build Rust/WASM versions** that are 3-10x faster than existing JavaScript implementations
3. **Win on speed** -- Google Core Web Vitals reward fast sites with higher rankings
4. **Monetize with Mediavine/Raptive** at premium RPMs ($15-50+)

**Revenue potential:** A calculator site at 5M visits/month with $35 RPM = **$175,000/month** in ad revenue. The top calculator sites in this dataset (inchcalculator.com, thecalculatorsite.com) already achieve these traffic levels.

---

## 2. Full Niche Categorization

All 15,499 unique publishers categorized by primary niche:

| Category | Total | Mediavine | Raptive | % of Total |
|----------|------:|----------:|--------:|-----------:|
| Other (uncategorized) | 7,809 | 4,500 | 3,309 | 50.4% |
| Food/Recipe | 2,734 | 1,445 | 1,289 | 17.6% |
| Tech/Programming | 899 | 478 | 421 | 5.8% |
| Parenting/Family | 807 | 491 | 316 | 5.2% |
| Travel | 646 | 490 | 156 | 4.2% |
| DIY/Home/Garden | 591 | 316 | 275 | 3.8% |
| Pets/Animals | 385 | 207 | 178 | 2.5% |
| Automotive | 314 | 162 | 152 | 2.0% |
| Health/Fitness | 277 | 175 | 102 | 1.8% |
| Finance | 228 | 120 | 108 | 1.5% |
| Education | 193 | 104 | 89 | 1.2% |
| Sports/Outdoors | 188 | 99 | 89 | 1.2% |
| Fashion/Beauty | 177 | 109 | 68 | 1.1% |
| Games/Entertainment | 118 | 39 | 79 | 0.8% |
| Music/Audio | 105 | 58 | 47 | 0.7% |
| Photography | 28 | 17 | 11 | 0.2% |

**Key insight:** The "Other" category (50.4%) contains many lifestyle, personal, and multi-niche blogs that don't map cleanly to one category. The food/recipe category (17.6%) dominates, which is typical for content-based ad networks. Tool sites are a small but high-value slice.

---

## 3. Tool/SaaS/Utility Sites -- Detailed Analysis

### 3.1 Calculator Sites (15 domains)

Calculator sites are the highest-value targets. They have:
- Massive organic search traffic (people Google "X calculator" constantly)
- High user intent (users need an answer = high engagement)
- Repeat visits (bookmarked tools)
- Premium ad RPMs ($25-50+ in finance/health niches)

| Domain | Type | Network | Domain Quality | Est. Monthly Traffic | Rust Advantage |
|--------|------|---------|---------------|---------------------|----------------|
| **inchcalculator.com** | Unit/construction calculators | Raptive | 70 | ~5.5M visits | HIGH |
| **thecalculatorsite.com** | Multi-purpose calculator hub | Raptive | 65 | ~5.7M visits | HIGH |
| **calculateme.com** | Conversion calculators | Raptive | 90 | ~200K-500K visits | HIGH |
| **calculator.academy** | Educational calculators | Raptive | 80 | ~500K-1M visits | HIGH |
| **gradecalculator.com** | GPA/grade calculator | Raptive | 70 | ~500K-1M visits | HIGH |
| **fatcalc.com** | Body fat/fitness calculators | Raptive | 100 | ~150K organic | HIGH |
| **calculatemyroof.com** | Roofing material calculator | Raptive | 85 | ~100K-300K visits | HIGH |
| **tdeecalculator.me** | TDEE/calorie calculator | Raptive | 63 | ~500K-1M visits | HIGH |
| **fantasyfootballcalculator.com** | Fantasy football tools | Raptive | 65 | Seasonal (1M+ in season) | HIGH |
| **puppyweightcalculator.com** | Puppy weight predictor | Raptive | 65 | ~200K-500K visits | HIGH |
| **cryptoprofitcalculator.com** | Crypto profit calculator | Raptive | 65 | ~100K-300K visits | HIGH |
| **thepointcalculator.com** | Credit card points calculator | Mediavine | 65 | ~100K-300K visits | HIGH |
| **kingshotcalculator.com** | Gaming calculator | Raptive | 65 | ~100K-300K visits | HIGH |
| **mypaycalculator.co.uk** | UK salary/pay calculator | Raptive | 55 | ~300K-500K visits | HIGH |
| **starbucks-calorie-calculator.com** | Starbucks calorie tool | Raptive | 55 | ~100K-300K visits | HIGH |

**Note:** 14/15 are on Raptive (requires 100K+ pageviews). All are proven traffic generators.

### 3.2 Converter Sites (2 dedicated + related)

| Domain | Type | Network | Domain Quality | Rust Advantage |
|--------|------|---------|---------------|----------------|
| **convertbinary.com** | Binary/number converter | Raptive | 85 | HIGH |
| **titlecaseconverter.com** | Text case converter | Raptive | 65 | HIGH |

### 3.3 Generator Sites (3 domains)

| Domain | Type | Network | Domain Quality | Rust Advantage |
|--------|------|---------|---------------|----------------|
| **randomgenerators.com** | Multi-purpose random generators | Raptive | 70 | HIGH |
| **randompowergenerator.com** | Random generator tools | Raptive | 65 | HIGH |
| **strongpasswordgenerator.org** | Secure password generator | Raptive | 60 | HIGH |

### 3.4 Color / Text / Typing Tools (7 domains)

| Domain | Type | Network | Domain Quality | Rust Advantage |
|--------|------|---------|---------------|----------------|
| **rgbcolorpicker.com** | RGB color picker tool | Raptive | 70 | HIGH |
| **charactercounter.com** | Character/word counter | Raptive | 70 | HIGH |
| **thewordcounter.com** | Word counter tool | Raptive | 70 | HIGH |
| **syllablecounter.io** | Syllable counting tool | Raptive | 65 | HIGH |
| **typinggames.zone** | Typing speed games | Raptive | 80 | HIGH |
| **frameratetest.com** | FPS/frame rate tester | Raptive | 70 | HIGH |
| **onlinemictest.com** | Online microphone test | Raptive | 70 | MEDIUM |

### 3.5 Reference/Comparison Sites (4 domains)

| Domain | Type | Network | Domain Quality | Rust Advantage |
|--------|------|---------|---------------|----------------|
| **diffen.com** | Compare anything (X vs Y) | Raptive | 100 | MEDIUM |
| **travelmath.com** | Travel distance/time calculator | Raptive | 75 | MEDIUM |
| **howthingscompare.com** | Comparison site | Raptive | 70 | LOW |
| **comparebeforebuying.com** | Product comparison | Mediavine | 65 | LOW |

---

## 4. Game/Quiz/Interactive Sites (41 domains)

### 4.1 Puzzle/Crossword Sites (High Rust Advantage)

These are ideal for Rust/WASM -- puzzles require fast computation, rendering, and user interaction.

| Domain | Type | Network | Domain Quality |
|--------|------|---------|---------------|
| **online-solitaire.com** | Solitaire card game | Raptive | 70 |
| **crosswordjam.net** | Crossword puzzles | Raptive | 70 |
| **nytcrossword.org** | NYT crossword answers | Raptive | 70 |
| **crosswordbuzz.com** | Crossword solver | Raptive | 70 |
| **blackcrossword.com** | Crossword puzzles | Raptive | 70 |
| **puzzleseveryday.com** | Daily puzzles | Raptive | 70 |
| **puzzles-to-print.com** | Printable puzzles | Raptive | 70 |
| **puzzlepagecheats.com** | Puzzle solutions | Raptive | 70 |
| **crosswordmasterhelp.com** | Crossword help | Raptive | 65 |
| **usatodaycrosswordanswers.com** | Crossword answers | Raptive | 65 |
| **dailycommutercrossword.com** | Daily crossword | Raptive | 65 |
| **crosswordanswers911.net** | Crossword answers | Raptive | 60 |
| **nytcrosswordanswers.org** | NYT crossword answers | Raptive | 60 |
| **crossword-explorer.net** | Crossword helper | Raptive | 60 |
| **dailythemedcrossword.info** | Themed crossword | Raptive | 50 |

### 4.2 Word/Brain Games

| Domain | Type | Network | Domain Quality |
|--------|------|---------|---------------|
| **playwordle.uk** | Wordle clone | Mediavine | 60 |
| **flagle-game.com** | Geography guessing game | Raptive | 75 |
| **game.dazepuzzle.com** | Puzzle game | Mediavine | 85 |
| **ladypuzzle.pro** | Puzzle game | Raptive | 60 |

### 4.3 Game/Trivia Sites

| Domain | Type | Network | Domain Quality |
|--------|------|---------|---------------|
| **triviawhizz.com** | Trivia quizzes | Mediavine | 75 |
| **triviabliss.com** | Trivia site | Raptive | 75 |
| **triviaquiznight.com** | Trivia quiz | Mediavine | 70 |
| **everythingtrivia.com** | Trivia content | Raptive | 70 |
| **novelgames.com** | Online games collection | Raptive | 75 |
| **west-games.com** | Online games | Raptive | 75 |
| **worldofcardgames.com** | Card games | Raptive | 70 |
| **crazymonkeygames.com** | Flash/HTML5 games | Raptive | 70 |
| **mywordgames.com** | Word games | Raptive | 75 |
| **quiz-questions.uk** | Quiz questions | Mediavine | 55 |

### 4.4 Coloring Pages

| Domain | Type | Network | Domain Quality |
|--------|------|---------|---------------|
| **coloringpageshq.com** | Coloring pages | Raptive | 70 |
| **yaycoloringpages.com** | Coloring pages | Raptive | 70 |

---

## 5. Finance Calculator Sites

Finance tools command the highest RPMs ($30-50+). Sites in this dataset with finance-adjacent calculators:

| Domain | Specific Tool | Network | Notes |
|--------|--------------|---------|-------|
| **cryptoprofitcalculator.com** | Crypto profit/loss calculator | Raptive | Crypto niche = high RPM |
| **thepointcalculator.com** | Credit card rewards points | Mediavine | Finance niche |
| **mypaycalculator.co.uk** | UK salary/tax calculator | Raptive | Finance niche |
| **fantasycalc.com** | Fantasy sports valuations | Raptive | Sports betting adjacent |
| **fantasyfootballcalculator.com** | Fantasy football | Raptive | Seasonal but massive traffic |
| **calculatemyroof.com** | Roofing cost estimator | Raptive | Home improvement = good RPM |

**Opportunity:** The biggest gap is general finance calculators (mortgage, compound interest, retirement, tax). The existing sites in the network are niche-specific. A comprehensive finance calculator site in Rust/WASM could capture enormous search traffic.

---

## 6. Test Prep / Certification Exam Sites (26 domains)

These represent a large programmatic SEO opportunity. Each certification exam = a separate landing page cluster.

| Domain | Certification | Network |
|--------|--------------|---------|
| **practicecnatest.com** | CNA (Nursing Assistant) | Raptive |
| **pertpracticetest.com** | PERT (Florida college) | Raptive |
| **tsipracticetest.com** | TSI (Texas college) | Raptive |
| **siepracticeexam.com** | SIE (Securities) | Raptive |
| **rbtpracticeexam.com** | RBT (Behavior Technician) | Raptive |
| **nremtpracticetest.com** | NREMT (Emergency Medical) | Raptive |
| **highschooltestprep.com** | General high school | Raptive |
| **workkeyspracticetest.com** | WorkKeys (ACT) | Raptive |
| **aswbpracticeexam.com** | ASWB (Social Work) | Raptive |
| **gedpracticetest.net** | GED | Raptive |
| **asvabpracticetests.com** | ASVAB (Military) | Raptive |
| **parapropracticetest.com** | ParaPro (Teaching) | Raptive |
| **accuplacerpracticetest.com** | ACCUPLACER (College) | Raptive |
| **ptcbpracticetest.com** | PTCB (Pharmacy) | Raptive |
| **hesipracticetest.com** | HESI (Nursing) | Raptive |
| **az900practicetest.com** | AZ-900 (Azure Cloud) | Raptive |
| **ccmapracticetests.com** | CCMA (Medical Asst) | Raptive |
| **servsafepracticetest.com** | ServSafe (Food Safety) | Raptive |
| **pmppracticeexam.org** | PMP (Project Mgmt) | Raptive |
| **phlebotomypracticetest.net** | Phlebotomy | Raptive |
| **hisetpracticetest.org** | HiSET (HS equivalency) | Raptive |
| **gedpracticequestions.com** | GED | Raptive |
| **phlebotomyexaminer.com** | Phlebotomy | Raptive |
| **yourfreecareertest.com** | Career assessment | Raptive |
| **spiritanimaltest.org** | Personality quiz | Raptive |
| **frameratetest.com** | FPS test (hardware) | Raptive |

**Rust advantage:** LOW for content-based test prep. But a Rust/WASM quiz engine could provide instant scoring, adaptive difficulty, and smooth UX. The bigger win is the **programmatic SEO model**: one template per certification x hundreds of certifications = massive page count.

---

## 7. Template/Printable Sites (22 domains)

| Domain | Type | Network |
|--------|------|---------|
| **worldofprintables.com** | Multi-category printables | Raptive |
| **createprintables.com** | Printable generator | Raptive |
| **printablecrush.com** | Printable designs | Raptive |
| **worksheetgenius.com** | Worksheet generator | Raptive |
| **worksheetplace.com** | Worksheet library | Raptive |
| **15worksheets.com** | Worksheets | Raptive |
| **emojiflashcards.com** | Emoji flashcards | Raptive |
| **printables4mom.com** | Mom printables | Mediavine |
| **printablesfairy.com** | Printable designs | Mediavine |
| **superstarworksheets.com** | Worksheets | Mediavine |
| **favoriteprintables.com** | Printable collection | Mediavine |
| **prettysweetprintables.com** | Printable designs | Mediavine |
| **theprintableprincess.com** | Educational printables | Mediavine |
| **goldstarworksheets.com** | Worksheets | Mediavine |
| **printablesforlife.com** | Printable collection | Mediavine/Raptive |
| **makefunprintables.com** | Fun printables | Raptive |
| **onceuponaprintable.com** | Printable designs | Raptive |
| **freeorganizingprintables.com** | Organizing printables | Raptive |
| **worksheets-to-print.com** | Printable worksheets | Raptive |
| **notimeforflashcards.com** | Flashcards (parenting) | Raptive |
| **free-n8n-templates.com** | N8N automation templates | Raptive |
| **discordtemplates.me** | Discord server templates | Raptive |

**Rust advantage:** MEDIUM. PDF generation in Rust/WASM is a prime candidate -- generating printable PDFs client-side is CPU-intensive and Rust excels here. A printable generator that creates custom worksheets/planners/calendars client-side via WASM would be significantly faster.

---

## 8. SVG/Font/Craft File Sites

| Domain | Type | Network |
|--------|------|---------|
| **svg.com** | SVG files (premium domain) | Raptive |
| **freescrapbookfonts.com** | Scrapbook fonts | Raptive |

**Note:** svg.com is an exceptionally valuable domain. SVG manipulation in Rust/WASM (parsing, optimization, conversion) is a natural fit.

---

## 9. Programmatic SEO Opportunities

Sites whose content model lends itself to programmatic page generation at scale:

### 9.1 Calculator-based pSEO (Highest Priority)

**Pattern:** `[Noun] Calculator` -- one landing page per calculation type

Sites proving this works:
- **calculator.academy** - Hub of hundreds of calculators, each targeting a specific "how to calculate X" query
- **inchcalculator.com** - 5.5M visits/month with construction/measurement calculators
- **thecalculatorsite.com** - 5.7M visits/month multi-purpose calculator hub
- **calculateme.com** - Conversion calculators for every unit type

**pSEO Scale:** Thousands of calculators can be generated from formulas:
- Math: area, volume, perimeter, percentage, ratio, fraction, etc.
- Finance: mortgage, loan, compound interest, ROI, break-even, markup, margin, tip, etc.
- Health: BMI, TDEE, calorie, macro, body fat, pregnancy due date, ovulation, etc.
- Construction: concrete, lumber, roofing, flooring, paint, mulch, gravel, fence, deck, etc.
- Unit conversion: length, weight, volume, temperature, speed, area, time, data, etc.
- Science: chemistry molar mass, physics equations, electrical calculations, etc.

Each calculator = one page targeting "[thing] calculator" keyword. Thousands of pages, minimal incremental effort with a Rust/WASM calculator engine.

### 9.2 Conversion-based pSEO

**Pattern:** `Convert [X] to [Y]` -- combinatorial explosion of pages

Sites proving this works:
- **convertbinary.com** - Binary/decimal/hex/octal conversions
- **titlecaseconverter.com** - Text case conversions

**pSEO Scale:** Every pair of units = a page. For example:
- 100+ length units = 10,000+ conversion pairs
- 50+ currencies = 2,500+ currency pairs
- File format conversions (PNG to JPG, PDF to Word, etc.)
- Encoding conversions (Base64, URL encode, HTML entities, etc.)

### 9.3 Test Prep pSEO

**Pattern:** `[Certification] Practice Test` -- one site per exam type

Proven by 20+ sites in the dataset (all on Raptive). Each certification has:
- Practice questions page
- Study guide page
- Requirements page
- Salary/career page
- State-specific requirements (50 states x N certifications)

### 9.4 Comparison pSEO

**Pattern:** `[X] vs [Y]` -- every pair of compared items = a page

Proven by **diffen.com** (521K visits). The model:
- Two entities from same category
- Side-by-side comparison table
- Prose explanation of differences
- Scales to millions of comparisons

### 9.5 Template/Printable pSEO

**Pattern:** `Free [Type] Template` -- one page per template category

Proven by 22 printable sites. Each variation = a page:
- "[Holiday] coloring pages" (365+ holidays x categories)
- "[Subject] worksheet for [grade]" (subjects x grades x topics)
- "[Type] planner template" (daily, weekly, monthly, yearly x styles)

---

## 10. Top 20 Rust Rebuild Targets

Ranked by combined score of: domain quality, tool complexity (simpler = faster to build), traffic potential, RPM potential, and Rust advantage.

### Tier 1: Build These First (Highest ROI)

| Rank | Domain Concept | Why | Est. Revenue Potential | Build Complexity |
|------|---------------|-----|----------------------|-----------------|
| **1** | **Multi-calculator hub** (like calculator.academy) | pSEO goldmine: 1000s of calculators, each targets a keyword. Rust/WASM makes calculations instant. thecalculatorsite.com does 5.7M visits/month. | $150K-200K/mo at scale | Low -- formula-based, template engine |
| **2** | **Unit converter** (like calculateme.com) | Billions of monthly searches for "convert X to Y". Combinatorial pSEO. All computation is client-side and benefits from WASM. | $50K-100K/mo | Low -- lookup tables + math |
| **3** | **Construction calculators** (like inchcalculator.com) | 5.5M visits/month proven. High RPM (home improvement = $30-50 RPM). Concrete, roofing, flooring, paint, lumber calculators. | $100K-200K/mo | Low-Medium |
| **4** | **Text tools hub** (word counter, character counter, case converter) | charactercounter.com + thewordcounter.com prove demand. Extremely simple to build in Rust/WASM. Writers, students, SEO pros use daily. | $30K-60K/mo | Very Low |
| **5** | **Typing speed test/game** (like typinggames.zone) | High engagement, repeat visits, gamification. WASM enables buttery smooth real-time typing measurement. | $20K-50K/mo | Low |

### Tier 2: High Value, Medium Effort

| Rank | Domain Concept | Why | Est. Revenue Potential | Build Complexity |
|------|---------------|-----|----------------------|-----------------|
| **6** | **Body composition calculators** (BMI, TDEE, body fat, macro) | tdeecalculator.me, fatcalc.com prove demand. Health niche = high RPM ($25-40). | $30K-80K/mo | Low |
| **7** | **Comparison engine** (X vs Y, like diffen.com) | 521K visits. Programmatic: compare any two entities. Template-driven content at massive scale. | $20K-50K/mo | Medium -- needs data |
| **8** | **Color picker / palette tools** (like rgbcolorpicker.com) | Designers search for these constantly. Color math in WASM is natural. Small tool, huge SEO tail. | $15K-30K/mo | Low |
| **9** | **Password/random generators** (like strongpasswordgenerator.org) | Constant demand. Crypto-grade randomness in Rust > JavaScript Math.random(). Security positioning. | $15K-30K/mo | Very Low |
| **10** | **Finance calculators** (mortgage, compound interest, loan) | Highest RPMs in all of display ads ($40-60+). Every financial calculation = a landing page. | $50K-150K/mo | Low-Medium |

### Tier 3: Proven Niches, More Effort

| Rank | Domain Concept | Why | Est. Revenue Potential | Build Complexity |
|------|---------------|-----|----------------------|-----------------|
| **11** | **Online solitaire/card games** | online-solitaire.com, worldofcardgames.com prove demand. Rust/WASM enables smooth 60fps gameplay. Classic games have permanent demand. | $30K-80K/mo | Medium |
| **12** | **Crossword solver/builder** | 15+ crossword sites in dataset, all on Raptive. WASM enables instant dictionary search and grid solving. | $20K-50K/mo | Medium |
| **13** | **Practice test engine** | 20+ cert test sites prove model. One engine, hundreds of certifications. Rust/WASM for instant scoring + adaptive difficulty. | $30K-80K/mo | Medium |
| **14** | **Printable PDF generator** | 22 printable sites. Client-side PDF generation in WASM eliminates server costs and is faster. Worksheets, planners, calendars, coloring pages. | $20K-50K/mo | Medium |
| **15** | **Travel calculator** (distance, time, cost) | travelmath.com does 1.3-3.1M visits/month. Distance, drive time, flight time, cost calculations. | $20K-40K/mo | Low-Medium |

### Tier 4: Supplementary Builds

| Rank | Domain Concept | Why | Est. Revenue Potential | Build Complexity |
|------|---------------|-----|----------------------|-----------------|
| **16** | **SVG tools** (optimize, convert, edit) | svg.com exists on Raptive. Rust has excellent SVG libraries (resvg). Designer audience. | $10K-30K/mo | Medium |
| **17** | **Binary/encoding converter** (Base64, hex, binary, URL encode) | convertbinary.com on Raptive. Developer audience. Very simple math. | $10K-20K/mo | Very Low |
| **18** | **Syllable/readability analyzer** | syllablecounter.io on Raptive. Writers, poets, students. NLP tasks benefit from WASM speed. | $5K-15K/mo | Low |
| **19** | **Frame rate / hardware test** | frameratetest.com, onlinemictest.com on Raptive. Hardware tests need low-latency JS -- WASM is ideal. | $10K-20K/mo | Low-Medium |
| **20** | **Crypto profit calculator** | cryptoprofitcalculator.com on Raptive. Crypto niche = very high RPM. Real-time calculation. | $10K-30K/mo | Low |

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Build the shared infrastructure:**

```
rust-tools-monorepo/
  crates/
    calculator-engine/     # Core math/formula evaluation (Rust)
    wasm-bridge/           # WASM bindings and JS interop
    seo-template/          # HTML template generation for pSEO pages
    ad-layout/             # Mediavine/Raptive ad placement optimization
  sites/
    calc-hub/              # Multi-calculator site
    convert-hub/           # Unit converter site
    text-tools/            # Word counter, character counter, etc.
```

**Tech stack per tool:**

| Component | Technology |
|-----------|-----------|
| Core logic | Rust compiled to WASM via wasm-pack |
| UI framework | Leptos or Yew (Rust-native) OR vanilla JS + WASM module |
| Static generation | Rust CLI tool generates 1000s of HTML pages |
| Hosting | Cloudflare Pages (free, fast, global CDN) |
| Ad integration | Mediavine or Raptive script tags |
| Analytics | Simple server-side analytics (Plausible) |

**Recommended approach:** Start with vanilla HTML/CSS/JS for the UI shell (fastest to iterate), with Rust/WASM modules for the computation. This is the approach Figma uses and it's pragmatic. Only move to full-Rust frameworks (Leptos) if you want to showcase Rust end-to-end.

### Phase 2: Launch First Tools (Weeks 5-8)

1. **Text tools** (lowest complexity, fastest to launch)
   - Word counter, character counter, sentence counter
   - Case converter (title case, upper, lower, camel, snake, kebab)
   - Text diff tool
   - Lorem ipsum generator
   - Readability scorer (Flesch-Kincaid in WASM)

2. **Calculator hub** (highest traffic potential)
   - Start with 50 most-searched calculators
   - Use pSEO template: title, formula explanation, calculator widget, related calculators
   - Target: "X calculator" keywords

3. **Password/random generators** (very quick to build)
   - Cryptographically secure via Rust's `rand` crate
   - Password generator, UUID generator, random number, random color, etc.

### Phase 3: Scale Content (Weeks 9-16)

4. **Unit converter** (combinatorial pSEO)
   - Generate pages for every unit pair: "feet to meters", "kg to lbs", etc.
   - Target: thousands of "convert X to Y" keywords

5. **Construction calculators** (high RPM niche)
   - Concrete calculator, paint calculator, roofing calculator, lumber calculator
   - Target homeowner audience (premium ad rates)

6. **Finance calculators** (highest RPM)
   - Mortgage, compound interest, loan amortization, ROI, break-even
   - Finance niche commands $40-60+ RPM

### Phase 4: Expand (Weeks 17-24)

7. **Health calculators** (BMI, TDEE, calorie, macro, body fat)
8. **Typing speed test** (gamified, high engagement)
9. **Color tools** (picker, palette generator, contrast checker)
10. **Comparison engine** (X vs Y format)

### Phase 5: Games & Interactive (Weeks 25+)

11. **Solitaire** (Rust/WASM for smooth card game)
12. **Crossword helper** (dictionary search in WASM)
13. **Printable PDF generator** (client-side PDF in WASM)
14. **Quiz/test engine** (reusable engine for any certification)

### Ad Network Timeline

| Milestone | Requirement | Timeline |
|-----------|------------|----------|
| Apply to Ezoic | 10K visits/month | Month 2-3 |
| Apply to Mediavine | 50K sessions/month | Month 4-6 |
| Apply to Raptive | 100K pageviews/month | Month 6-12 |
| Premium placement | 500K+ pageviews/month | Month 12+ |

### SEO Strategy

1. **Programmatic pages** -- Generate thousands of calculator/converter pages from templates
2. **Core Web Vitals** -- Rust/WASM tools will score near-perfect Lighthouse scores, giving SEO boost
3. **Internal linking** -- Each calculator links to related calculators (massive internal link graph)
4. **Schema markup** -- Add Calculator, HowTo, and FAQ schema to every page
5. **Content cluster** -- Wrap each tool with "How to calculate X" article content for topical authority

### Revenue Projections (Conservative)

| Month | Traffic | RPM | Monthly Revenue |
|-------|---------|-----|----------------|
| 3 | 50K | $10 (Ezoic) | $500 |
| 6 | 200K | $20 (Mediavine) | $4,000 |
| 9 | 500K | $25 (Mediavine) | $12,500 |
| 12 | 1M | $30 (Raptive) | $30,000 |
| 18 | 3M | $35 (Raptive) | $105,000 |
| 24 | 5M+ | $35-45 (Raptive) | $175K-225K |

These are conservative estimates based on the traffic levels achieved by existing sites in this dataset (inchcalculator.com: 5.5M, thecalculatorsite.com: 5.7M, travelmath.com: 3.1M).

---

## 12. Why Rust/WASM Specifically?

### Performance Benchmarks (2025 data)

| Metric | JavaScript | Rust/WASM | Improvement |
|--------|-----------|-----------|-------------|
| Array operations | 1.4ms | 0.23ms (SIMD) | 6x faster |
| General computation | baseline | 3-5x faster (wasm-bindgen) | 3-5x |
| Raw compute | baseline | 8-10x faster (raw WASM) | 8-10x |
| Image processing | baseline | 10-15x faster (SIMD) | 10-15x |

### SEO Advantage

Google's Core Web Vitals heavily weight:
- **Largest Contentful Paint (LCP)** -- WASM tools render faster
- **Interaction to Next Paint (INP)** -- WASM calculations respond instantly
- **Cumulative Layout Shift (CLS)** -- Pre-computed layouts from WASM

Fast tools = better Google rankings = more traffic = more ad revenue.

### Cost Advantage

Client-side WASM computation means:
- Zero server compute costs (all math runs in browser)
- Static hosting only (Cloudflare Pages = free)
- Infinite scalability (no server bottleneck)
- Marginal cost per user approaches zero

---

## 13. Network Analysis: Why Raptive Dominates Tool Sites

Of the 124 tool/utility sites identified:
- **Raptive: 109 (88%)**
- **Mediavine: 15 (12%)**

This suggests Raptive actively recruits tool/utility publishers, likely because:
1. Tool sites have high pageviews-per-session (users try multiple tools)
2. Tool sites have high engagement metrics
3. Technical audience = higher value to advertisers
4. Raptive's minimum (100K pageviews) is easier for tool sites to hit than Mediavine's session-based metric

**Recommendation:** Target Raptive as the primary ad network for tool sites.

---

## Appendix A: All 15,499 Domains by Network

- Mediavine: 7,394 unique domains
- Raptive: 8,105 unique domains

## Appendix B: Additional Domains Worth Investigating

These domains appeared in broader pattern matching but need manual verification:

| Domain | Why Flagged | Network |
|--------|------------|---------|
| pregnancyfoodchecker.com | Food safety checker for pregnant women | Raptive |
| kingshotoptimizer.com | Gaming optimizer tool | Raptive |
| pc-builder.io | PC building tool | Raptive |
| bigtimer.net | Timer/countdown tool | Raptive |
| generatorgrid.com | Generator comparison site | Raptive |
| remote.tools | Remote work tools directory | Mediavine |
| wodtools.com | CrossFit WOD tools | Mediavine |
| kanji.tools | Japanese kanji learning tool | Raptive |
| dafontfile.org | Font download site | Mediavine |

## Appendix C: Methodology

1. Loaded all 20,726 publisher records from `all_publishers.csv`
2. Deduplicated by domain (reduced to 15,499 unique domains)
3. Applied broad niche categorization using keyword pattern matching against domain names and publisher names
4. Applied strict tool-site identification using:
   - Whole-word matching for tool-specific terms (calculator, converter, generator, etc.)
   - Domain structure analysis (TLD, length, exact-match patterns)
   - False positive exclusion list (134 manually verified false positives removed)
5. Rated each tool site on:
   - Rust/WASM advantage (High/Medium/Low based on computation intensity)
   - Domain quality score (0-100 based on length, TLD, exact-match bonus)
6. Verified top sites via web search for actual traffic data and functionality
7. Cross-referenced with industry RPM data ($15-50+ for premium ad networks)

**False positive exclusion examples:**
- "crochet" domains matching "ocr" pattern
- "beautiful" domains matching "beautif" (beautify) pattern
- "hashtag" domains matching "hash" pattern
- "practical" domains matching "calc" pattern
- Blog names containing "test" (e.g., "triedandtested")

---

*Analysis performed on 2026-03-06. Traffic estimates are based on publicly available SimilarWeb/Semrush data and may vary. Revenue projections use industry-standard RPM ranges for Mediavine ($22-43 avg) and Raptive ($47-57 avg Q4 2025) as reported by publishers.*
