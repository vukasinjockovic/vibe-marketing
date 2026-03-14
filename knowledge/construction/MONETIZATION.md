# FatStud Monetization Strategy

Last updated: 2026-03-11

## Data Assets Summary

| Data Type | Records | States | Notes |
|-----------|---------|--------|-------|
| Contractors (businesses) | 1,890,387 | 37+ states | Name, address, phone, entity type |
| Licenses | 2,090,873 | 12 states deep | License #, type, status, classifications, dates |
| Tradespersons (individuals) | 1,198,198 | 8 states | Individual qualifiers with certifications |
| Officers/Principals | 1,079,908 | WA + CA | Who runs each company |
| Categories/Classifications | 1,700,488 | 11 sources | What type of work they do |
| Insurance/WC | 521,555 | WA, CA, OR, TX, FL | Carrier, policy #, expiration dates |
| Bonds | 469,215 | WA, CA, OR | Bond company, amount, dates |
| Projects (WA only) | 2,407,738 | WA | Intent-to-pay + affidavit filings |
| OSHA (federal) | 18.7M | All US | Inspections, violations, accidents, penalties |
| **TOTAL** | **~28M+ records** | | |

**Planned additions:** Google Maps profiles, BBB, Angi/HomeAdvisor, EPA RRP

## Core Value Proposition

The most valuable thing isn't the raw data — it's the **CROSS-REFERENCING**. Anyone can look up a CA license on CSLB. Nobody else can show: "This contractor has a CSLB license, their bond expires in 60 days, they have 3 OSHA violations totaling $45K in penalties, and their WC carrier is Technology Insurance Company." That consolidated view is what's worth paying for.

## Revenue Streams

### Stream 1: B2B Data Subscriptions / API Access

**Tier 1 — High willingness to pay, clear ROI:**

| Buyer | What They Want | Why They'd Pay | Price Range |
|-------|---------------|----------------|-------------|
| WC Insurance brokers/agents | X-date lists (policy expiration + contractor contact) | Each lead = $50-200 commission on renewal | $500-2K per county list |
| Surety bond companies | Contractors whose bonds expire soon + license status | They need to find contractors needing bonds | $1K-5K/year |
| Construction lenders | Contractor license verification + insurance status | Due diligence on borrowers | $2K-10K/year |
| General contractors (large) | Subcontractor vetting — license + insurance + OSHA + bond | Risk management for hiring subs | $500-2K/year |

**Tier 2 — Moderate willingness to pay:**

| Buyer | What They Want | Why They'd Pay |
|-------|---------------|----------------|
| Material suppliers | Active contractor lists by trade + location | Sales prospecting |
| Construction software companies | Contractor contact lists for outreach | Lead gen for SaaS |
| Staffing agencies (construction) | Tradesperson lists with certifications | Recruiting pipeline |
| Real estate developers | Contractor vetting before hiring | Risk reduction |

**Pricing guidance:** $100/year is leaving money on the table. Insurance x-date lists alone sell for $500-2K. Price by value, not by cost:
- Free tier: Homeowners (ad-supported, basic lookups)
- Pro tier: $200-500/month for B2B API/dashboard access
- Enterprise: Custom pricing for bulk data exports, x-date lists

### Stream 2: Insurance Lead Sales (Highest $/lead)

**The x-date play:** We have WC policy expiration dates for 6,000+ FL construction contractors (and growing with more states). Insurance agents pay $50-200 per qualified lead.

**Current FL data (year 2026):**
- 251,250 WC policy records across all 69 counties
- 7,570 matched to construction contractors
- 6,061 unique contractors with WC insurance data
- Massive renewal wave in January 2027 (~4,000 contractors)

**Lead profile includes:** Business name, phone, city/zip, current carrier (competitive intel), policy number, exact expiration date, NCCI class code

**Pricing model options:**
- Per-lead: $25-75 per contractor contact with expiring WC policy
- Per-list: $500-2K per county x-date list
- Subscription: $2K-5K/year for rolling access to expiration alerts

**States with WC data:** WA, CA, OR, TX, FL (more coming)

### Stream 3: Ad Revenue (Raptive/Mediavine)

**Traffic strategy — lead with tools, not directory:**
- 167+ construction/home calculators = strongest SEO asset
- "Is my contractor licensed?" verification tools = high-intent queries
- State-specific guides ("Florida Contractor Licensing After HB 735")
- OSHA violation lookups = unique data nobody else surfaces

**Revenue math:**
- Target: 50K monthly visitors
- RPM: $10-20 (home/construction niche pays well)
- Monthly: $500-1,000/month
- Annual: $6K-12K/year

**Key insight:** Calculator pages convert well, have clear search intent, and Google treats them as tools (not thin content). Sites like calculator.net and omnicalculator.com built real traffic this way.

### Stream 4: Facebook Content → Site Traffic

**Strategy:**
1. Create niche Facebook pages per trade/region (e.g., "Florida Roofing Pros", "Texas Electrical Contractors")
2. Feed content from data: "Did you know 874 FL roofing contractors have WC policies expiring in January?"
3. Drive to fatstud for full lookup ("Check if YOUR contractor is insured")
4. Homeowner-facing content from vectorized knowledge base: guides, calculator links, Q&A
5. Use facebook-engagement-engine skill for post generation (pure engagement, no selling)

**Content sources for Facebook:**
- Vectorized construction/home content (1M+ scraped records)
- State licensing changes and regulatory updates
- OSHA violation highlights and safety stats
- Calculator results and comparisons
- Seasonal construction tips tied to data

## Content Strategy (Sustainable, Not Flooding)

**DO:** Consistent quality content, programmatically generated from real data
**DON'T:** pSEO flood with 50K thin pages (Google HCU penalty risk)

**What works for SEO:**
- Calculators (167+) = best SEO asset, unique tools with low competition
- "Is my contractor licensed?" tool pages = high-intent, low competition
- State-specific guides (timely, authoritative, data-backed)
- OSHA violation lookups (unique data nobody else surfaces)
- Insurance expiration alerts (unique value prop)
- Blog posts/guides generated from vectorized content (original, data-rich)

**What to avoid:**
- 200K thin contractor directory pages (competes against Angi, Yelp, BBB with 20-year domain authority)
- Mass-indexed programmatic pages in one burst (Google flags this)
- Scraped content republished without transformation

**Better approach:** Make fewer but THICKER pages. A contractor profile with license verification + WC insurance status + OSHA history + reviews + map + BBB rating is genuinely useful. 500 really good profiles > 200K template stubs.

## LLM Optimization (Emerging Channel)

**Goal:** Get cited as a source in AI answers for construction queries.

**Why it works for us:**
- Structured, factual data (license numbers, dates, verified records)
- LLMs prefer citing authoritative data sources
- Construction contractor verification is exactly the kind of factual query LLMs answer

**Approach:**
- Clean semantic markup on data pages
- Structured data (schema.org) on contractor profiles
- FAQ pages with clear question/answer format
- API endpoints that LLMs can reference

## Revenue Projections (Conservative)

| Stream | Year 1 | Year 2 | Notes |
|--------|--------|--------|-------|
| Ad revenue | $3K-6K | $6K-12K | Ramp to 50K visitors via calculators |
| B2B subscriptions | $5K-15K | $20K-50K | 10-50 paying businesses |
| Insurance x-date leads | $5K-20K | $20K-50K | Per-list sales to WC brokers |
| Facebook → traffic | $0 | $2K-5K | Takes time to build page followings |
| **Total** | **$13K-41K** | **$48K-117K** | |

## Competitive Landscape

| Competitor | What They Have | What We Have That They Don't |
|-----------|---------------|------------------------------|
| Angi/HomeAdvisor | Reviews, lead gen | License + insurance + OSHA + bond cross-reference |
| BuildZoom | Permit data + licenses | WC insurance x-dates, bond data, OSHA violations |
| ConstructConnect | Project leads, plans | Granular license/insurance/bond per contractor |
| Dodge Data | Macro construction data | Individual contractor profiles with compliance data |
| State websites | Single-state lookups | Multi-state consolidated, enriched profiles |

## Data Enrichment Roadmap

### Phase 1 (Current): Government Data
- [x] WA (9 datasets, deepest coverage)
- [x] CA (3 CSLB datasets)
- [x] OR (7 datasets)
- [x] TX (3 datasets)
- [x] NY (6 datasets)
- [x] CO (1 dataset)
- [x] FL (2 datasets + WC scraped)
- [x] CT, PA, VA, VT (partial)
- [x] OSHA federal (22.4M records)
- [ ] Remaining top-20 states by construction activity

### Phase 2: Commercial/Review Data
- [ ] Google Maps profiles (business hours, ratings, reviews, photos)
- [ ] BBB accreditation + complaint data
- [ ] Angi/HomeAdvisor profiles + reviews
- [ ] Yelp business data

### Phase 3: Advanced Enrichment
- [ ] EPA RRP (lead paint certifications)
- [ ] Secretary of State business filings (cross-reference)
- [ ] Court records / liens
- [ ] Building permit data (municipal level)

### Phase 4: Real-time Monitoring
- [ ] Daily OSHA sync + contractor matching
- [ ] Insurance expiration alerts
- [ ] License status change notifications
- [ ] New contractor registration alerts
