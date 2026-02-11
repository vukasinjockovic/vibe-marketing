# Enrichment Protocol

Validation rules, confidence criteria, and operational guardrails for the vibe-audience-enricher agent.

---

## Core Rules

1. **Never overwrite non-null fields in heartbeat mode.** Production records may have human-reviewed data. Only fill empty/null fields unless explicitly told to force-update.

2. **Always include reasoning for every inference.** Every call to `focusGroups:enrich` must include a non-empty `reasoning` string explaining what data was used and why this classification was chosen.

3. **Confidence levels must be earned, not assumed.** Default to "low" and upgrade only when signal thresholds are met.

4. **Log everything to the enrichments[] audit trail.** The `focusGroups:enrich` mutation handles this automatically. Never use `focusGroups:update` for enrichment fields.

5. **Skip fields where inference would be pure guesswork.** If there is no data to infer from, leave the field null. A null field is better than a wrong field.

---

## Confidence Thresholds

| Level | Criteria | When to Use |
|-------|----------|-------------|
| **high** | 3+ matching indicators from different data sources | Strong signal convergence across beliefs, objections, language, pain points |
| **medium** | 2 matching indicators, or 3+ from same source | Reasonable signal but not fully corroborated |
| **low** | 1 matching indicator, or weak/ambiguous signals | Use only when some signal exists; otherwise skip |

---

## Field-Level Inference Prerequisites

Each enrichment field has minimum data requirements before inference is attempted:

| Enrichment Field | Required Input Fields | Inference Script |
|-----------------|----------------------|-----------------|
| awarenessStage | beliefs OR objections (ideally both + languagePatterns) | `infer_awareness.py` |
| sophisticationLevel | marketingHooks (required) + languagePatterns (optional) | `infer_sophistication.py` |
| purchaseBehavior | demographics (required for priceRange) + objections (for history) | `infer_purchase_behavior.py` |
| contentPreferences | psychographics.identity + psychographics.lifestyle | LLM inference only |
| communicationStyle | languagePatterns + psychographics | LLM inference only |
| competitorContext | painPoints + objections + beliefs | LLM inference only |
| influenceSources | psychographics + demographics.lifestyle | LLM inference only |
| seasonalContext | demographics.triggers + psychographics.lifestyle | LLM inference only |
| negativeTriggers | objections + fears + beliefs | LLM inference only |
| awarenessSignals | Derived automatically with awarenessStage | `infer_awareness.py` |

---

## Pipeline Mode vs Heartbeat Mode

### Pipeline Mode (staging records)
- May overwrite any field (staging data is draft)
- Runs after document parse or research step
- Operates on `focusGroupStaging` records
- Uses `focusGroupStaging:updateFields` to update

### Heartbeat Mode (production records)
- Never overwrite non-null fields
- Runs weekly via cron/heartbeat
- Operates on `focusGroups` records
- Uses `focusGroups:enrich` which maintains audit trail
- Check `focusGroups:getEnrichmentProgress` first to see what is missing

---

## Error Handling

1. If a script fails, log the error and continue to next field/group
2. Never mark a pipeline step as complete if zero enrichments were made
3. If all groups already fully enriched, complete step with note "all groups current"
4. Timeout: 30 seconds per Convex call, 5 minutes per group enrichment cycle
