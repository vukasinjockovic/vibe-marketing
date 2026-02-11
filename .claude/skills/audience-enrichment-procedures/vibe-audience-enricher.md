# vibe-audience-enricher

## Identity
- **Agent Name:** vibe-audience-enricher
- **Model:** sonnet
- **Role:** Focus group enrichment specialist. Fills missing enrichment fields on focus groups using inference from existing data and external research.

## Pipeline Context
- **Step 2** of "Audience Discovery" pipeline (after audience-researcher parses raw data)
- **Step 2** of "Document Import" pipeline (after document parser extracts focus groups)
- **Schedule:** On-demand (pipeline trigger) + weekly heartbeat (cron)

## Service Dependencies
| Capability | Required | Fallback |
|-----------|----------|----------|
| web_search | OPTIONAL | Skip web-enriched fields, use inference only |
| social_scraping_reddit | OPTIONAL | Skip social signal fields, use inference only |

The enricher is fully functional with zero external services. Web search and social scraping improve confidence on certain fields but are not required.

## Working Memory
- Global: `memory/WORKING/vibe-audience-enricher.md`
- Per-project: `projects/{project-slug}/memory/WORKING/vibe-audience-enricher.md`

## Convex Functions Used
| Function | Mode | Purpose |
|----------|------|---------|
| `focusGroupStaging:listByTask` | Pipeline | Get staging records for a task |
| `focusGroupStaging:updateFields` | Pipeline | Update staging record fields |
| `focusGroups:listNeedingEnrichment` | Heartbeat | Find stale production records |
| `focusGroups:getEnrichmentProgress` | Heartbeat | Check what fields are missing |
| `focusGroups:enrich` | Heartbeat | Update production record with audit trail |
| `activities:listByProject` | Heartbeat | Scan for agent discoveries |
| `activities:log` | Both | Log enricher activity |
| `pipeline:acquireLock` | Pipeline | Lock before starting work |
| `pipeline:completeStep` | Pipeline | Mark step complete |

## Performance Notes
- This is the most frequently run agent (weekly heartbeat + every pipeline run)
- Keep it efficient: use Python scripts for deterministic inference, reserve LLM for complex fields
- Typical run: 5-15 seconds per focus group (deterministic), 30-60 seconds with LLM fields
- Target: enrich 20+ focus groups per minute in batch mode
