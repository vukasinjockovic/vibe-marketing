# FatStud Content Factory — Master Source List

**Created:** 2026-03-07
**Purpose:** Complete inventory of all content sources for construction content mining. Referenced by [fatstud-content-factory-plan-v2.md](/var/www/vibe-marketing/thoughts/shared/plans/fatstud-content-factory-plan-v2.md).

**Priority Legend:**
- `★★★` = MUST SCRAPE — highest content volume, easiest access, most valuable data
- `★★` = HIGH VALUE — substantial content, worth the effort
- `★` = NICE TO HAVE — good supplementary data, lower priority
- `⊘` = SKIP — paywalled, gated, or too difficult for the return

**Scrapability Legend:**
- `EASY` = Clean HTML, server-rendered, robots.txt permissive
- `MEDIUM` = Some JS, or mixed free/gated content
- `HARD` = Heavy JS SPA, paywall, bot detection

---

## Summary Totals

| Category | Sources | Est. Total Articles | Priority Sources |
|----------|:-------:|:-------------------:|:----------------:|
| Construction/DIY Blog Sites | 55 | 85,000+ | 20 ★★★ |
| Cost Guide Sites | 11 | 8,000+ | 6 ★★★ |
| YouTube Channels | 45 | 8,000+ videos | 15 ★★★ |
| Forums / Q&A Sites | 17 | 2M+ threads | 6 ★★★ |
| Trade Publications | 15 | 25,000+ | 5 ★★ |
| Manufacturer Blogs | 12 | 2,000+ | 4 ★★ |
| Building Code / Reference | 5 | 15,000+ | 2 ★★★ |
| Yelp (construction reviews) | 1 | 200K+ reviews | 1 ★★★ |
| Retail How-To | 3 | 5,500+ | 2 ★★ |
| Real Estate / Reno Crossover | 4 | 2,300+ | 1 ★ |
| Tool / Equipment Review | 4 | 2,300+ | 1 ★ |
| **TOTALS** | **172** | **355,000+** | **63 priority** |

---

## 1. Construction / DIY Blog Sites (55 sites)

### ★★★ MUST SCRAPE (20 sites — ~52,000+ articles)

| # | Domain | Description | Est. Articles | Content Type | Scrape | Notes |
|:-:|--------|-------------|:-------------:|:------------:|:------:|-------|
| 1 | **inspectapedia.com** | Free online encyclopedia of building construction, inspection, repair. By Daniel Friedman. THE single richest free reference on the open web. | 10,000+ | Reference encyclopedia | EASY | Clean HTML. Covers every building system. |
| 2 | **thisoldhouse.com** | This Old House — 40+ year brand. Project walkthroughs, how-to guides, tool reviews. | 5,000+ | How-to, project guides | EASY | Clean article pages |
| 3 | **familyhandyman.com** | Reader's Digest brand. Huge DIY library covering all home improvement. | 5,000+ | DIY tutorials, tips | EASY | WordPress, clean HTML |
| 4 | **houzz.com** | Largest home design/renovation platform. Articles + absorbed GardenWeb archive (millions of forum posts). | 10,000+ articles + millions Q&A | Design, Q&A, product guides | MEDIUM | React SPA but indexable |
| 5 | **hgtv.com** | HGTV's content hub. 30+ years of content production. | 5,000+ | How-to, inspiration | MEDIUM | JS-heavy but articles render |
| 6 | **doityourself.com** | Long-running DIY site with articles AND decades of active forums. | 5,000+ articles + 50K+ forum | How-to + forum Q&A | EASY | Clean HTML, forum accessible |
| 7 | **thespruce.com** | Dotdash Meredith brand. Consumer-friendly home guides. | 5,000+ | Consumer home guides | EASY | Clean article pages |
| 8 | **bobvila.com** | Legendary brand. Home improvement guides across all categories. | 3,000+ | How-to guides | EASY | Clean HTML |
| 9 | **wikihow.com** (Home category) | Massive how-to encyclopedia. Step-by-step with illustrations. | 3,000+ (construction subset) | Step-by-step how-to | EASY | Very well-structured HTML |
| 10 | **bhg.com** | Better Homes & Gardens. Legacy publication, huge content library. | 5,000+ | How-to, design, seasonal | MEDIUM | Ad-heavy but readable |
| 11 | **instructables.com** (Workshop/Home) | Community DIY projects with detailed photo guides. | 2,000+ (construction) | Project guides | EASY | Clean HTML |
| 12 | **finehomebuilding.com** | Taunton Press. Professional-grade construction techniques. | 3,000+ | Pro techniques | EASY | Clean articles |
| 13 | **todayshomeowner.com** | Danny Lipford brand. TV companion site with articles + video. | 2,000+ | How-to, cost guides | EASY | WordPress, clean HTML |
| 14 | **concretenetwork.com** | Deep concrete-specific content. Design, techniques, contractors. | 2,000+ | Concrete how-to + design | EASY | Clean HTML |
| 15 | **apartmenttherapy.com** | Renovation guides, before/after, DIY projects. | 3,000+ | Before/after, how-to | EASY | Clean article pages |
| 16 | **forconstructionpros.com** | Houses Concrete Contractor, Equipment Today, Asphalt Contractor, Pavement magazines. | 5,000+ | Trade articles | EASY | Clean article pages |
| 17 | **hunker.com** | Home improvement basics, accessible tone. | 2,000+ | How-to basics | EASY | Clean HTML |
| 18 | **jlconline.com** | Journal of Light Construction. Residential construction pros. | 1,500+ | Pro techniques | EASY | Clean HTML |
| 19 | **diynetwork.com** | DIY Network content (merged into HGTV). Step-by-step projects. | 2,000+ | Step-by-step | MEDIUM | Same CMS as HGTV |
| 20 | **remodelista.com** | Design-forward renovation content. Material guides, sourcebook format. | 2,000+ | Design, material sourcing | EASY | Clean HTML |

### ★★ HIGH VALUE (15 sites — ~14,000+ articles)

| # | Domain | Description | Est. Articles | Content Type | Scrape | Notes |
|:-:|--------|-------------|:-------------:|:------------:|:------:|-------|
| 21 | **protoolreviews.com** | Pro contractor tool reviews and comparisons. | 1,000+ | Tool reviews | EASY | WordPress |
| 22 | **builderonline.com** | Builder Magazine. Industry insights for builders. | 1,000+ | Industry, techniques | EASY | Clean HTML |
| 23 | **houserepairtalk.com** | DIY forum with guides. Organized by trade. | 1,000+ articles + 50K forum | Forum Q&A, how-to | EASY | Forum software |
| 24 | **dwell.com** | Architecture and modern home design. Renovation stories. | 2,000+ | Design, renovation | MEDIUM | Some JS |
| 25 | **constructiondive.com** | Construction industry news and analysis. Clean writing. | 2,000+ | Industry analysis | EASY | Clean HTML |
| 26 | **probuilder.com** | Professional Builder magazine. Content for homebuilders. | 1,500+ | Industry, techniques | EASY | Clean HTML |
| 27 | **proremodeler.com** | Pro Remodeler. Business + technical for remodeling contractors. | 1,000+ | Business, techniques | EASY | Clean HTML |
| 28 | **qualifiedremodeler.com** | Qualified Remodeler magazine. Business content. | 1,000+ | Business, products | EASY | Clean HTML |
| 29 | **construction-today.com** | Construction Today digital magazine. | 500+ | Projects, products | EASY | Clean HTML |
| 30 | **constructionexec.com** | Construction Executive. Business management for contractors. | 2,000+ | Business management | EASY | Clean HTML |
| 31 | **constructionspecifier.com** | CSI's publication. Technical specs and materials. | 1,500+ | Technical specs | EASY | WordPress |
| 32 | **energyvanguard.com/blog** | Allison Bailes' building science blog. Energy, HVAC, envelope. | 500+ | Building science | EASY | WordPress |
| 33 | **houselogic.com** | NAR's consumer site. Home maintenance + value guides. | 500+ | Maintenance, value | EASY | Clean HTML |
| 34 | **roofonline.com** | Roofing reference library. Construction details, publications. | 500+ | Reference, technical | EASY | Clean HTML |
| 35 | **realtor.com/advice/home-improvement** | Renovation ROI, cost guides, home prep. | 1,000+ | Renovation ROI, costs | EASY | Clean HTML |

### ★ NICE TO HAVE (15 sites — ~7,000+ articles)

| # | Domain | Description | Est. Articles | Content Type | Scrape | Notes |
|:-:|--------|-------------|:-------------:|:------------:|:------:|-------|
| 36 | **realestate.usnews.com** | Home improvement trends, cost analysis. | 300+ | Trends, costs | EASY | |
| 37 | **zillow.com** (home improvement) | Market-informed renovation content. | 500+ | Cost guides | MEDIUM | React app |
| 38 | **toolboxbuzz.com** | Pro contractor tool reviews. Head-to-head comparisons. | 500+ | Tool reviews | EASY | WordPress |
| 39 | **toolsinaction.com** | Pro power tool guide. Reviews, news. | 500+ | Tool reviews | EASY | WordPress |
| 40 | **thetoolreview.com** | Independent power tool reviews. | 300+ | Tool reviews | EASY | WordPress |
| 41 | **constructionequipment.com** | Heavy equipment reviews, fleet management. | 1,000+ | Equipment reviews | EASY | |
| 42 | **menards.com** (How-To) | Midwest-focused project guides. | 500+ | How-to, buying guides | EASY | Simpler site |
| 43 | **paintmag.com** | Painting techniques, business, products. | 500+ | Painting trade | EASY | |
| 44 | **floorcoveringweekly.com** | Flooring industry news, installation. | 1,000+ | Flooring trade | EASY | |
| 45 | **structure.mag.org** | Structural engineering articles. | 1,000+ | Structural engineering | EASY | |
| 46 | **hearth.com** (articles) | Fireplace, woodstove, chimney content. | 500+ | Niche: heating | EASY | |
| 47 | **remodeling.hw.net** | Remodeling Magazine. Cost vs. Value Report. | 1,500+ | Cost data, business | MEDIUM | Some gating |
| 48 | **concretecontractor.com** | Concrete Contractor magazine (via forconstructionpros). | 1,000+ | Concrete techniques | EASY | |
| 49 | **pmmag.com** | Plumbing & Mechanical magazine. | 1,000+ | Plumbing trade | EASY | |
| 50 | **hpacmag.com** | HPAC Magazine (Canadian). Mechanical pros. | 500+ | HVAC/plumbing | EASY | |

### ⊘ SKIP (too difficult/paywalled for the return)

| # | Domain | Why Skip |
|:-:|--------|----------|
| 51 | **enr.com** | Paywalled, heavy JS. Industry bible but not accessible. |
| 52 | **csiresources.org** | Mostly member-gated. |
| 53 | **aci.int** | Mostly member-gated. Concrete standards. |
| 54 | **nari.org** | Member-gated remodeling content. |
| 55 | **nkba.org** | Member-gated kitchen/bath content. |

---

## 2. Cost Guide Sites (11 sites)

### ★★★ MUST SCRAPE — Critical for pricing data in city pages + cost guides

| # | Domain | Description | Est. Articles | Scrape | Notes |
|:-:|--------|-------------|:-------------:|:------:|-------|
| 1 | **fixr.com** | 600+ pure cost guides. Detailed metrics, material breakdowns, labor estimates. | 600+ | EASY | Clean article pages. Best structured cost data. |
| 2 | **homeguide.com/costs** | Proprietary cost database from millions of contractor estimates. Clean, detailed. | 1,500+ | EASY | Well-structured HTML. Very scrape-friendly. |
| 3 | **costhelper.com** | Crowdsourced cost data. Users report actual costs paid. Real-world data. | 1,000+ | EASY | Simple HTML. User-reported = authentic data. |
| 4 | **homewyse.com** | Cost calculators by ZIP code. Material + labor breakdowns. Data-driven. | 500+ | EASY | Clean HTML. ZIP-based = city page goldmine. |
| 5 | **inchcalculator.com** | Direct competitor. Construction calcs + cost guides. | 500+ | EASY | WordPress. Study their approach. |
| 6 | **remodelingcalculator.org** | Remodeling cost calculators and estimators by project. | 200+ | EASY | WordPress. |

### ★★ HIGH VALUE — Good supplementary cost data

| # | Domain | Description | Est. Articles | Scrape | Notes |
|:-:|--------|-------------|:-------------:|:------:|-------|
| 7 | **angi.com** | Huge cost guide library. Local pricing data. | 3,000+ | MEDIUM | JS but articles render. Formerly Angie's List. |
| 8 | **homeadvisor.com/cost/** | True Cost Guide. Detailed breakdowns with local data. | 2,000+ | MEDIUM | JS-heavy. Now part of Angi. |
| 9 | **modernize.com** | Cost guides by project type. Contractor matching. | 500+ | EASY | Clean HTML. |
| 10 | **porch.com** | Cost guides and project planning. | 500+ | MEDIUM | Some JS. |
| 11 | **thumbtack.com/costs** | Cost guides from actual marketplace quotes. | 500+ | MEDIUM | React app. |

---

## 3. YouTube Channels (45 channels)

### ★★★ MUST SCRAPE (15 channels — highest value transcripts)

| # | Channel | Focus | Subs | Videos | Notes |
|:-:|---------|-------|:----:|:------:|-------|
| 1 | **This Old House** | Full project walkthroughs. The gold standard. | 2M+ | 1,500+ | Covers everything. |
| 2 | **Essential Craftsman** | General construction, concrete, framing. Master class. | 1.25M | 300+ | Deep, expert-level content. |
| 3 | **Matt Risinger** | Building science, materials, techniques. | 1M+ | 500+ | Building science authority. |
| 4 | **Home RenoVision DIY** | DIY renovation tutorials. Step-by-step. | 1M+ | 400+ | Very detailed how-to. |
| 5 | **Sparky Channel** | Electrical tutorials, NEC code, wiring. | 500K+ | 200+ | Best electrical YT channel. |
| 6 | **Electrician U** | Electrical education, NEC code, apprenticeship content. | 500K+ | 300+ | Companion to Sparky Channel. |
| 7 | **Roger Wakefield** | Plumbing tutorials, drain cleaning, DIY plumbing. | 500K+ | 300+ | Best plumbing YT. |
| 8 | **Perkins Builder Brothers** | Custom home building, framing, finish work. | 700K+ | 200+ | Great framing content. |
| 9 | **See Jane Drill** | Beginner-friendly DIY, tool operation, home repair. | 936K | 300+ | Beginner audience = A1 segment. |
| 10 | **Apple Drains** | French drains, drainage, yard grading. Niche dominator. | 600K+ | 200+ | Landscaping niche goldmine. |
| 11 | **Modern Builds** | Woodworking, metalworking, concrete projects. | 1.7M | 200+ | Great project content. |
| 12 | **Roof It Right** | Roofing tutorials and techniques. | 100K+ | 100+ | Best roofing YT. |
| 13 | **Odell Complete Concrete** | Concrete finishing, flatwork, decorative. | 200K+ | 150+ | Concrete pro content. |
| 14 | **Mike Haduck** | Masonry, concrete, stone work, chimney repair. | 200K+ | 200+ | Old-school masonry. |
| 15 | **Word of Advice TV** | Plumbing how-to, drain cleaning, DIY plumbing. | 300K+ | 200+ | Supplements Roger Wakefield. |

### ★★ HIGH VALUE (15 channels)

| # | Channel | Focus | Subs | Videos |
|:-:|---------|-------|:----:|:------:|
| 16 | **Vancouver Carpenter** | Carpentry, framing, finishing. | 200K+ | 200+ |
| 17 | **Larry Haun** | Framing masterclass. Legacy content. | 100K+ | 100+ |
| 18 | **RR Buildings** | Pole barns, metal buildings. | 200K+ | 200+ |
| 19 | **HVAC School** | HVAC technician training, diagnostics. | 200K+ | 200+ |
| 20 | **The Honest Carpenter** | Carpentry techniques, tool reviews. | 300K+ | 200+ |
| 21 | **Insider Carpentry** | Finish carpentry, trim, molding. | 200K+ | 150+ |
| 22 | **Kirk Giordano Plastering** | Stucco, plastering, cement work. | 150K+ | 200+ |
| 23 | **Tile Coach** | Tile installation, waterproofing. | 100K+ | 100+ |
| 24 | **Sal DiBlasi** | Tile, bathroom remodeling, waterproofing. | 200K+ | 150+ |
| 25 | **Shannon from House Improvements** | General home improvement, renovation. | 300K+ | 200+ |
| 26 | **The Excellent Laborer** | Concrete work, construction labor. | 100K+ | 100+ |
| 27 | **Skill Builder** | UK-based. Tools, techniques, thorough testing. | 500K+ | 300+ |
| 28 | **Home Mender** | Quick home repair how-tos. Short-form. | 200K+ | 200+ |
| 29 | **AwesomeFramers** | Structural framing techniques. | 150K+ | 100+ |
| 30 | **AFT Construction** | Residential construction, framing. | 200K+ | 150+ |

### ★ NICE TO HAVE (15 channels)

| # | Channel | Focus | Subs |
|:-:|---------|-------|:----:|
| 31 | **The Funny Carpenter** | Finish carpentry with humor | 100K+ |
| 32 | **Contractor Evolution** | Business for contractors | 100K+ |
| 33 | **Belinda Carr** | Renovation, design, DIY. UK. | 400K+ |
| 34 | **Scott Brown Carpentry** | Fine carpentry, joinery. UK. | 150K+ |
| 35 | **Stumpy Nubs** | Woodworking, workshop | 300K+ |
| 36 | **Build Show Network** | Building techniques | 150K+ |
| 37 | **Dmitry Lipinskiy** | Roofing Insights | 100K+ |
| 38 | **BiggerPockets** | Real estate investing (construction overlap) | 1M+ |
| 39 | **Yard Mastery** | Lawn care, landscaping | 200K+ |
| 40 | **Myatt Landscaping** | Landscaping business + techniques | 100K+ |
| 41 | **ElectricianU** (additional content) | Already counted above | - |
| 42 | **The Build Show** | Matt Risinger's second channel | - |
| 43 | **Concrete Decor Show** | Decorative concrete techniques | 50K+ |
| 44 | **ProTradeCraft** | Builder techniques, details | 50K+ |
| 45 | **Build With Roman** | Residential building | 100K+ |

---

## 4. Forums / Q&A Sites (17 sites)

### ★★★ MUST SCRAPE — Richest Q&A sources for Q&A pages + voice data

| # | Forum | URL | Focus | Size | Scrape | Notes |
|:-:|-------|-----|-------|:----:|:------:|-------|
| 1 | **DIY Stack Exchange** | diy.stackexchange.com | All home improvement Q&A. Structured upvoted answers. | 200K+ questions | EASY | **HAS API.** Highest quality structured Q&A on the web. |
| 2 | **ContractorTalk** | contractortalk.com | Pro contractors across ALL trades. | 200K+ members, 1M+ posts | EASY | vBulletin. Massive archive. |
| 3 | **Mike Holt's Forum** | forums.mikeholt.com | THE electrical forum. NEC code, wiring, grounding. | 100K+ members | EASY | XenForo. Deep electrical. |
| 4 | **Terry Love Forum** | terrylove.com/forums | THE plumbing forum. 95K+ threads, 68K+ members. | 95K+ threads | EASY | vBulletin. Plumbing bible. |
| 5 | **DoItYourself.com Forums** | doityourself.com/forum | All home improvement. Decades of content. | Very large | EASY | Forum software. |
| 6 | **HVAC-Talk** | hvac-talk.com | THE HVAC forum. 150K+ members. | 150K+ members | EASY | vBulletin. |

### ★★ HIGH VALUE (7 forums)

| # | Forum | URL | Focus | Size | Scrape |
|:-:|-------|-----|-------|:----:|:------:|
| 7 | **DIY Chatroom** | diychatroom.com | All home improvement. Contractors + DIYers. | Large | EASY |
| 8 | **GardenWeb / Houzz Discussions** | houzz.com/discussions | Kitchen, bath, landscaping. Absorbed GardenWeb. | Millions of posts | MEDIUM |
| 9 | **The Building Code Forum** | thebuildingcodeforum.com | Code interpretation discussions. Inspectors + contractors. | Moderate | EASY |
| 10 | **Fine Homebuilding Breaktime** | finehomebuilding.com/breaktime | FHB's pro discussion forum. High quality. | Moderate | EASY |
| 11 | **JLC Online Forum** | forums.jlconline.com | Journal of Light Construction forum. Pro residential. | Moderate | EASY |
| 12 | **GreenBuildingAdvisor Q&A** | greenbuildingadvisor.com/qa | Building science Q&A. Expert answers. | Moderate | EASY |
| 13 | **Plumbing Zone** | plumbingzone.com | Pro plumbers only (verified). Technical. | Moderate | EASY |

### ★ NICE TO HAVE (4 forums)

| # | Forum | URL | Focus |
|:-:|-------|-----|-------|
| 14 | **Electrical-Online Forum** | electrical-online.com | Electrical how-to + wiring diagrams |
| 15 | **The Garage Journal** | garagejournal.com/forum | Garage building, workshop, tools |
| 16 | **Sawmill Creek** | sawmillcreek.org | Woodworking + construction |
| 17 | **Hearth.com Forums** | hearth.com | Fireplace, woodstove, chimney |

---

## 5. Reddit Subreddits (12 subreddits)

### ★★★ MUST SCRAPE

| # | Subreddit | Members | Content Value |
|:-:|-----------|:-------:|:-------------:|
| 1 | **r/HomeImprovement** | 5M+ | DIY questions, project results, material recs |
| 2 | **r/DIY** | 22M+ | Broad DIY including construction |
| 3 | **r/Construction** | 200K+ | Pro trade discussions, techniques |
| 4 | **r/Electricians** | 300K+ | Code questions, wiring help |
| 5 | **r/Concrete** | 30K+ | Mix ratios, finishing techniques |
| 6 | **r/Roofing** | 50K+ | Material comparisons, estimates |

### ★★ HIGH VALUE

| # | Subreddit | Members |
|:-:|-----------|:-------:|
| 7 | **r/Carpentry** | 200K+ |
| 8 | **r/Plumbing** | 200K+ |
| 9 | **r/Landscaping** | 300K+ |
| 10 | **r/Drywall** | 10K+ |
| 11 | **r/HVAC** | 200K+ |
| 12 | **r/Hardscaping** | 10K+ |

---

## 6. Trade Publications (15 sites)

### ★★ HIGH VALUE (trade-specific deep expertise)

| # | Domain | Trade | Est. Articles | Scrape |
|:-:|--------|-------|:-------------:|:------:|
| 1 | **roofingcontractor.com** | Roofing | 1,500+ | EASY |
| 2 | **roofingmagazine.com** | Roofing | 1,000+ | EASY |
| 3 | **professionalroofing.net** | Roofing (NRCA) | 1,500+ | EASY |
| 4 | **ecmag.com** | Electrical (NECA) | 2,000+ | EASY |
| 5 | **achrnews.com** | HVAC/R | 3,000+ | EASY |
| 6 | **contractormag.com** | Plumbing/HVAC | 1,500+ | EASY |

### ★ NICE TO HAVE

| # | Domain | Trade | Est. Articles |
|:-:|--------|-------|:-------------:|
| 7 | **pmmag.com** | Plumbing | 1,000+ |
| 8 | **paintmag.com** | Painting | 500+ |
| 9 | **floorcoveringweekly.com** | Flooring | 1,000+ |
| 10 | **structure.mag.org** | Structural engineering | 1,000+ |
| 11 | **concretecontractor.com** | Concrete (via forconstructionpros) | 1,000+ |
| 12 | **hpacmag.com** | HVAC (Canadian) | 500+ |
| 13 | **constructionequipment.com** | Heavy equipment | 1,000+ |
| 14 | **construction-today.com** | General | 500+ |
| 15 | **qualifiedremodeler.com** | Remodeling | 1,000+ |

---

## 7. Building Code / Reference Sites (5 sites)

### ★★★ MUST SCRAPE

| # | Domain | Description | Content | Scrape |
|:-:|--------|-------------|:-------:|:------:|
| 1 | **inspectapedia.com** | Already listed in blogs. 10,000+ articles. | 10,000+ | EASY |
| 2 | **diy.stackexchange.com** | Already listed in forums. 200K+ Q&A. | 200K+ | EASY |

### ★★ HIGH VALUE

| # | Domain | Description | Content | Scrape |
|:-:|--------|-------------|:-------:|:------:|
| 3 | **up.codes** | Building codes searchable by jurisdiction. Clean interface. | Full code database | MEDIUM |
| 4 | **greenbuildingadvisor.com** | Building science. 1,000+ construction details by climate zone. | 2,000+ | MEDIUM |
| 5 | **buildingscience.com** | BSC. Joseph Lstiburek. 450+ figures/tables. Deep technical. | 500+ | EASY |

### ⊘ SKIP

| Domain | Why |
|--------|-----|
| **codes.iccsafe.org** | Copyrighted code text. Legal risk. |

---

## 8. Manufacturer Blogs (12 sites)

### ★★ HIGH VALUE

| # | Domain | Products | Est. Articles | Scrape |
|:-:|--------|----------|:-------------:|:------:|
| 1 | **quikrete.com/diy** | Concrete, mortar, stucco | 100+ | EASY |
| 2 | **sakrete.com/blog** | Concrete, mortar | 100+ | EASY |
| 3 | **iko.com/na/blog** | Roofing | 300+ | EASY |
| 4 | **gaf.com** (resources) | Roofing | 200+ | MEDIUM |

### ★ NICE TO HAVE

| # | Domain | Products | Est. Articles |
|:-:|--------|----------|:-------------:|
| 5 | **owenscorning.com/roofing** | Roofing, insulation | 200+ |
| 6 | **jameshardie.com** (resources) | Fiber cement siding | 100+ |
| 7 | **trex.com/inspiration** | Composite decking | 100+ |
| 8 | **schluter.com** (resources) | Tile waterproofing | 100+ |
| 9 | **milwaukeetool.com/articles** | Tools | 200+ |
| 10 | **strongtie.com** | Connectors, fasteners | 100+ |
| 11 | **certainteed.com** | Roofing, siding | 100+ |
| 12 | **behr.com** (project ideas) | Paint | 100+ |

---

## 9. Retail How-To Libraries (3 sites)

### ★★ HIGH VALUE — Huge content, retailer perspective

| # | Domain | Description | Est. Articles | Scrape |
|:-:|--------|-------------|:-------------:|:------:|
| 1 | **homedepot.com/c/diy_projects_and_ideas** | Home Depot DIY hub. Buying guides + how-to. | 3,000+ | MEDIUM |
| 2 | **lowes.com/diy-projects-and-ideas** | Lowe's project guides with video. | 2,000+ | MEDIUM |
| 3 | **menards.com** (How-To) | Midwest-focused project guides. | 500+ | EASY |

---

## 10. Yelp (1 source, massive data)

### ★★★ MUST SCRAPE

| # | Domain | Description | Est. Data | Method |
|:-:|--------|-------------|:---------:|:------:|
| 1 | **yelp.com** | Construction contractor reviews. Customer voice, pricing data, city-specific info. | 200K+ reviews | Web archive mining (2020+) + Scrapling/DataImpulse |

---

## 11. Quora (1 source)

### ★★ HIGH VALUE

| # | Domain | Topics | Est. Q&A |
|:-:|--------|--------|:--------:|
| 1 | **quora.com** | Home Improvement, Construction, DIY, Roofing, Electrical, Concrete, Landscaping, Carpentry | 1,000+ |

---

## Scraping Priority Order

For maximum content acquisition efficiency, scrape in this order:

### Wave 1: Web Archive Mining (FREE, parallel, no rate limits)
Mine all ★★★ domains through Wayback/Common Crawl/GAU to build URL inventory.

### Wave 2: Highest-Yield Easy Scrapes
1. **inspectapedia.com** — 10,000 articles, easy HTML
2. **diy.stackexchange.com** — 200K Q&A, has API
3. **doityourself.com** — 5,000 articles + 50K forum threads
4. **fixr.com** — 600 cost guides, perfect for city pages
5. **homeguide.com** — 1,500 cost guides
6. **costhelper.com** — crowdsourced cost data
7. **instructables.com** — 2,000+ construction projects
8. **wikihow.com** (home) — 3,000+ how-to articles

### Wave 3: Major Content Sites
9. **thisoldhouse.com** — 5,000+ articles
10. **familyhandyman.com** — 5,000+ articles
11. **bobvila.com** — 3,000+ articles
12. **thespruce.com** — 5,000+ articles
13. **finehomebuilding.com** — 3,000+ articles
14. **todayshomeowner.com** — 2,000+ articles
15. **concretenetwork.com** — 2,000+ articles

### Wave 4: YouTube Transcripts (parallel)
All 15 ★★★ channels simultaneously via youtube_research.py

### Wave 5: Forums (Q&A extraction)
16. **ContractorTalk** — 1M+ posts
17. **Mike Holt** — electrical bible
18. **Terry Love** — plumbing bible
19. **HVAC-Talk** — HVAC bible
20. **DIY Chatroom** — all trades

### Wave 6: Reddit + Quora
All 12 subreddits + 8 Quora topics

### Wave 7: Yelp
Web archive mining + Scrapling targeted scraping

### Wave 8: Trade Pubs + Manufacturers + Retail
Everything ★★ and ★ that wasn't covered above

---

## Content Type Distribution After Full Mining

| Content Type | Est. Documents | Primary Sources |
|:------------:|:--------------:|:---------------:|
| How-to articles | 30,000+ | blogs, wikihow, instructables, retail |
| Cost guides | 5,000+ | fixr, homeguide, costhelper, angi, homewyse |
| Q&A threads | 500,000+ | diy.stackexchange, forums, reddit, quora |
| Video transcripts | 5,000+ | 45 YouTube channels |
| Review/voice data | 200,000+ | yelp, reddit, quora |
| Technical reference | 15,000+ | inspectapedia, building science, codes |
| Trade articles | 20,000+ | trade publications |
| Product/brand guides | 2,000+ | manufacturer blogs |
| **Total available** | **~777,000+** | |

Not all 777K documents will be scraped — the URL inventory lets us cherry-pick the most relevant ~10-15K documents based on keyword matching and content quality.

---

## Scraper Requirements by Source Type

| Source Type | Scraper Tool | Script Needed |
|-------------|:------------:|:-------------:|
| Blog articles (easy HTML) | Crawl4AI | `scrape-construction-content.py` |
| Blog articles (JS-heavy) | Firecrawl or Playwright | `scrape-js-content.py` |
| Forum threads | Crawl4AI | `scrape-forums.py` |
| Stack Exchange | SE API (free, 10K req/day) | `scrape-stackexchange.py` |
| YouTube transcripts | youtube_research.py | `scrape-youtube.py` |
| Reddit | Reddit MCP | `scrape-reddit.py` |
| Quora | quora_research.py | `scrape-quora.py` |
| Yelp reviews | Scrapling + DataImpulse | `scrape-yelp-reviews.py` |
| Cost calculators | Crawl4AI | `scrape-cost-data.py` |
| Web archives (URL discovery) | GAU + Wayback CDX + CC | `discover-construction-urls.sh` |
| Yelp archives (URL discovery) | GAU + Wayback CDX + CC | `discover-yelp-urls.sh` |
