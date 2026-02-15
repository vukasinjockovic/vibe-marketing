# Kraken: Resource Management -- Campaigns & Content Batches

## Checkpoints
<!-- Resumable state for kraken agent -->
**Task:** Implement 5-phase resource management for campaigns and content batches
**Started:** 2026-02-15T19:55:00Z
**Last Updated:** 2026-02-15T20:01:00Z

### Phase Status
- Phase 1 (Single-Task Campaign): VALIDATED (Convex deploys, single task pattern replaces N-task loop)
- Phase 2 (Production Manifest Schema): VALIDATED (schema + campaigns.ts create/update + CampaignForm.vue)
- Phase 3 (Resource Tree Linking): VALIDATED (listByTaskAndType, listTree, campaignProgress queries + retryStep + SKILL.md updates)
- Phase 4 (Typed Progress Tracking): VALIDATED (resourceProgress on tasks, completeStep updates counts, retryStep safeguards)
- Phase 5 (Dashboard Visualization): VALIDATED (CampaignProgress.vue, ResourceTree.vue, integrated into campaign detail)

### Validation State
```json
{
  "convex_deploy": "success",
  "files_modified": [
    "convex/orchestrator.ts",
    "convex/schema.ts",
    "convex/campaigns.ts",
    "convex/resources.ts",
    "convex/pipeline.ts",
    "dashboard/components/CampaignForm.vue",
    "dashboard/components/CampaignProgress.vue",
    "dashboard/components/ResourceTree.vue",
    "dashboard/pages/projects/[slug]/campaigns/[id].vue",
    ".claude/skills/shared-references/resource-registration.md",
    ".claude/skills/content-writing-procedures/SKILL.md",
    ".claude/skills/content-review-procedures/SKILL.md",
    ".claude/skills/image-prompt-engineering/SKILL.md"
  ],
  "last_test_command": "npx convex dev --once --url http://localhost:3210",
  "last_test_exit_code": 0
}
```

### Resume Context
- All 5 phases completed
- No blockers
