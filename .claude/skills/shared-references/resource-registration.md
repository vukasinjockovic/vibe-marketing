# Resource Registration Protocol

All agents that produce files MUST register them as resources before calling `pipeline:completeStep` or `pipeline:completeBranch`.

## Creator Agent Pattern

After writing your output file(s):

```bash
# 1. Compute content hash
HASH=$(sha256sum "<filePath>" | cut -d' ' -f1)

# 2. Register the resource (returns resource ID)
RESOURCE_ID=$(npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "<TYPE>",
  "title": "<descriptive title>",
  "campaignId": "<CAMPAIGN_ID or omit>",
  "contentBatchId": "<BATCH_ID or omit>",
  "taskId": "<TASK_ID>",
  "filePath": "<absolute path to file>",
  "contentHash": "'$HASH'",
  "content": "<text content for textual resources, omit for binary>",
  "status": "draft",
  "pipelineStage": "<research|briefs|drafts|reviewed|final>",
  "createdBy": "<your-agent-name>",
  "metadata": {
    <type-specific fields — see table below>
  }
}' --url http://localhost:3210)

# 3. Complete step with resource IDs (REQUIRED — will error without them)
npx convex run pipeline:completeStep '{
  "taskId": "<TASK_ID>",
  "agentName": "<your-agent-name>",
  "qualityScore": <1-10>,
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

## Reviewer / Humanizer Pattern

Agents that update existing resources (don't create new files):

```bash
# 1. Find existing resources for this task
RESOURCES=$(npx convex run resources:listByTask '{"taskId":"<TASK_ID>"}' --url http://localhost:3210)
RESOURCE_ID=$(echo $RESOURCES | jq -r '.[0]._id')

# 2. Update status
npx convex run resources:updateStatus '{
  "id": "'$RESOURCE_ID'",
  "status": "reviewed",
  "updatedBy": "<your-agent-name>",
  "qualityScore": <1-10>,
  "note": "<review notes>"
}' --url http://localhost:3210

# 3. Complete step with same resource IDs
npx convex run pipeline:completeStep '{
  "taskId": "<TASK_ID>",
  "agentName": "<your-agent-name>",
  "qualityScore": <1-10>,
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

## Branch Agent Pattern

For parallel branch agents (e.g., image director):

```bash
npx convex run pipeline:completeBranch '{
  "taskId": "<TASK_ID>",
  "branchLabel": "<branch-label>",
  "agentName": "<your-agent-name>",
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

## Resource Types

| Agent | resourceType |
|-------|-------------|
| vibe-researcher / vibe-trend-researcher | `research_material` |
| vibe-brief-writer | `brief` |
| vibe-copywriter | `article`, `social_post`, `email_excerpt` |
| vibe-ad-copywriter | `ad_copy` |
| vibe-email-marketer | `email_sequence` |
| vibe-landing-page-builder | `landing_page` |
| vibe-image-director | `image_prompt` |
| vibe-image-creator | `image` |
| vibe-video-scripter | `video_script` |
| vibe-lead-magnet-creator | `lead_magnet` |
| vibe-facebook-engine | `social_post` |
| vibe-analytics-reporter | `report` |
| vibe-ebook-writer | `article` or `lead_magnet` |

## Metadata Shape by Type

| Type | Key Fields |
|------|-----------|
| `article` | wordCount, targetKeyword, awarenessStage, readabilityScore, skillsUsed |
| `social_post` | platform, characterCount, hashtags, steppsScore, postType |
| `ad_copy` | platform, adType, headline, cta, targetAudience |
| `image` | provider, promptUsed, dimensions, generationCost, format |
| `image_prompt` | style, dimensions, provider, promptText |
| `email_sequence` | emailCount, sequenceType, subject, preheader |
| `email_excerpt` | sourceArticleSlug, excerptType, wordCount |
| `research_material` | topics, wordCount, sources |
| `brief` | targetWordCount, targetKeyword, contentAngle, awarenessStage |
| `report` | reportType, period, metrics |
| `brand_asset` | assetType, format, dimensions |

## Deduplication

Resources use upsert by `taskId + filePath`. If an agent retries and creates a resource with the same taskId + filePath, the existing record is updated instead of creating a duplicate.
