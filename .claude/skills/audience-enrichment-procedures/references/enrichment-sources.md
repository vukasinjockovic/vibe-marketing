# Enrichment Data Sources

Where enrichment data comes from, in priority order.

---

## 1. Inference from Existing Fields (Primary)

The main enrichment source. Uses the focus group's own data to infer missing enrichment fields.

**How it works:**
- Python scripts analyze beliefs, objections, language patterns, pain points, demographics, psychographics, marketing hooks
- Deterministic keyword matching (no LLM needed for core fields)
- LLM inference for complex fields (contentPreferences, communicationStyle, etc.)

**Scripts:**
| Script | Input Fields | Output Fields |
|--------|-------------|---------------|
| `infer_awareness.py` | beliefs, objections, languagePatterns, painPoints | awarenessStage, awarenessConfidence, awarenessStageSource, awarenessSignals |
| `infer_sophistication.py` | marketingHooks, languagePatterns, beliefs, objections | sophisticationLevel |
| `infer_purchase_behavior.py` | demographics, painPoints, objections, emotionalTriggers, psychographics | purchaseBehavior (buyingTriggers, priceRange, decisionProcess, objectionHistory) |

**When to use:** Always. This is the first pass on every enrichment run.

---

## 2. Agent Activity Discoveries (Secondary)

Other agents learn about the audience while doing their work. The enricher scans their activity logs for relevant discoveries.

**Sources:**
- `vibe-audience-researcher` -- discovers new audience insights during research
- `vibe-content-writer` -- learns about audience responses while writing
- `vibe-content-reviewer` -- notes awareness/sophistication mismatches during review
- `vibe-social-listener` -- discovers language patterns from social monitoring

**How it works:**
- `scan_recent_mentions.py` queries `activities:listByProject`
- Filters for enrichment-relevant keywords
- Agent reviews discoveries and decides if they warrant field updates

**When to use:** During heartbeat mode. Check for discoveries since last enrichment run.

---

## 3. Web Research (Triggered Enrichment)

Optional, requires web_search or social_scraping services.

**Sources:**
- Reddit threads mentioning the audience's pain points
- Forum discussions with language pattern discoveries
- Review sites showing objection patterns
- Social media showing content preferences

**How it works:**
- Only triggered when specific fields are missing AND existing data is insufficient
- Uses SERVICE_REGISTRY.md to find active web_search or social_scraping_reddit services
- Enricher reads research output and updates fields

**When to use:** Only when inference from existing fields produces low confidence AND the field is high-weight (awarenessStage, purchaseBehavior).

**Service dependencies:**
- `web_search` -- OPTIONAL, degrades gracefully
- `social_scraping_reddit` -- OPTIONAL, degrades gracefully

---

## 4. Manual Human Input (Dashboard Overrides)

Humans can override any enrichment field via the dashboard.

**How it works:**
- Dashboard calls `focusGroups:enrich` with `awarenessStageSource: "manual"`
- The enrichments[] audit trail records the human override
- In heartbeat mode, the enricher respects non-null fields (never overwrites human input)

**When to use:** When automated enrichment produces incorrect results. Humans correct via dashboard.

---

## Source Priority

When multiple sources provide conflicting data:

1. **Manual human input** -- highest priority, never overwritten by automation
2. **High-confidence inference** -- 3+ indicators from existing data
3. **Agent activity discoveries** -- corroborated by multiple agents
4. **Medium-confidence inference** -- 2 indicators
5. **Web research** -- external data
6. **Low-confidence inference** -- single indicator, use as placeholder only

The `awarenessStageSource` field tracks whether the value came from "auto" (inference/agent) or "manual" (human). In heartbeat mode, if source is "manual", the field is never touched.
