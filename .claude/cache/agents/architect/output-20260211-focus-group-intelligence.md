# Architect Output: Focus Group Intelligence System
Created: 2026-02-11
Status: PLAN COMPLETE

## Summary

Designed the Focus Group Intelligence System with two primary flows:
- **Flow A (0-to-1)**: Research audiences from scratch using web search, competitor analysis, Reddit scraping
- **Flow B (0.5-to-1)**: Parse existing audience documents (.md/.docx/.pdf/.txt) into structured records

## Key Design Decisions

1. **Staging table pattern**: New `focusGroupStaging` table holds parsed/generated groups for human review before committing to production. Avoids polluting focusGroups with unreviewed data.
2. **Same pipeline infrastructure**: Focus group pipelines use the existing task/pipeline system. No separate pipeline engine needed. Tasks use `contentType: "audience_research"` and `metadata.productId` instead of `campaignId`.
3. **Three agents**: vibe-audience-parser (sonnet), vibe-audience-researcher (opus), vibe-audience-enricher (sonnet)
4. **Fuzzy matching**: 5-priority matching algorithm (exact name -> exact nickname -> substring -> Levenshtein -> cross-match) with human confirmation for anything below 0.95 confidence
5. **Enrichment audit trail**: Uses existing `enrichments[]` array in schema -- every change logged with timestamp, agent, field, old/new value, confidence, reasoning

## Files

- Full plan: `/var/www/vibe-marketing/thoughts/shared/plans/focus-group-intelligence-system.md`
- 45 new files, 5 modified files across 9 implementation phases
- Phase 1 (Convex foundation) has no dependencies and can start immediately

## Implementation Order

Phase 1: Convex Foundation (schema + functions) -- START HERE
Phase 2: Agent Skills - Parser
Phase 3: Agent Skills - Researcher  (can parallel with Phase 2)
Phase 4: Agent Skills - Enricher    (can parallel with Phase 2-3)
Phase 5: Dashboard - Enhanced Audiences Page (depends on Phase 1)
Phase 6: Dashboard - Staging Review Page (depends on Phase 5)
Phase 7: Dashboard - Detail & Enrichment History (depends on Phase 5)
Phase 8: Agent Registration (depends on Phases 2-4)
Phase 9: End-to-End Testing (depends on all)
