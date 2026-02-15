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
| vibe-researcher / vibe-engagement-trend-researcher | `research_material` |
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

## Multi-Article Campaign Pattern

Campaigns now create a single task for N articles (instead of N tasks). Each agent processes ALL articles in one pass. The task description will say something like:

```
Campaign "Summer Sale" -- Produce 5 articles in a single pipeline run.
Enabled deliverables: Hero Image, Social Posts (facebook: 2, instagram: 1), Email Excerpt
Seed keywords: summer fitness, outdoor workout
Each agent processes ALL 5 articles in one pass.
Register each article as an individual resource.
```

### Resource Tree Shape

```
Campaign (container -- not a resource)
+-- research_material (shared, no parent -- campaign-level)
+-- brief (shared, no parent -- campaign-level)
+-- article #1 (parentResourceId = null, campaignId = campaign._id)
|   +-- social_post (facebook) (parentResourceId = article_1._id)
|   +-- social_post (instagram) (parentResourceId = article_1._id)
|   +-- image_prompt (parentResourceId = article_1._id)
|   +-- image (parentResourceId = image_prompt._id)
|   +-- email_excerpt (parentResourceId = article_1._id)
|   +-- video_script (parentResourceId = article_1._id)
+-- article #2 ...
+-- email_sequence (standalone, parentResourceId = null)
+-- lead_magnet (standalone, parentResourceId = null)
```

**Key rules:**
- Research and briefs are campaign-level (no parent). They cover ALL articles.
- Articles are root resources (parentResourceId = null, campaignId set).
- Social posts, image prompts, email excerpts, video scripts are CHILD resources linked to their parent article via `parentResourceId`.
- Images are children of their image_prompt (parentResourceId = image_prompt._id).
- Standalone deliverables (email_sequence, lead_magnet) have no parent.

### Step 1: Skip-Already-Done Pattern (Retry Safety)

**ALWAYS check before producing.** If the agent crashed mid-run and restarts, this prevents duplicating work:

```bash
# Check existing resources for this task and type
EXISTING=$(npx convex run resources:listByTaskAndType '{
  "taskId": "'$TASK_ID'",
  "resourceType": "article"
}' --url http://localhost:3210)
EXISTING_COUNT=$(echo "$EXISTING" | jq 'length')

# Only produce articles that don't exist yet
if [ "$EXISTING_COUNT" -ge "$ARTICLE_COUNT" ]; then
  echo "All articles already registered, skipping production"
else
  # Start from article EXISTING_COUNT+1
  START_INDEX=$((EXISTING_COUNT + 1))
fi
```

Every agent in the pipeline must run this check for its own resource type before starting work.

### Step 2: Create Root Article Resources

The copywriter creates N article resources, each as a root resource (no parent):

```bash
for i in $(seq 1 $ARTICLE_COUNT); do
  ARTICLE_ID=$(npx convex run resources:create '{
    "projectId": "'$PROJECT_ID'",
    "resourceType": "article",
    "title": "Article '$i' -- '$KEYWORD'",
    "campaignId": "'$CAMPAIGN_ID'",
    "taskId": "'$TASK_ID'",
    "filePath": "'$OUTPUT_DIR'/article-'$i'.md",
    "status": "draft",
    "createdBy": "'$AGENT_NAME'"
  }' --url http://localhost:3210)
  ARTICLE_IDS+=("$ARTICLE_ID")
done
```

### Step 3: Create Child Resources with parentResourceId

Branch agents (image, social, email) find parent articles first, then link children:

```bash
# 1. Find parent articles for this task
ARTICLES=$(npx convex run resources:listByTaskAndType '{
  "taskId": "'$TASK_ID'",
  "resourceType": "article"
}' --url http://localhost:3210)

# 2. For each article, create child resources
ARTICLE_ID=$(echo "$ARTICLES" | jq -r '.[0]._id')

IMAGE_ID=$(npx convex run resources:create '{
  "projectId": "'$PROJECT_ID'",
  "resourceType": "image_prompt",
  "title": "Hero image for Article 1",
  "campaignId": "'$CAMPAIGN_ID'",
  "taskId": "'$TASK_ID'",
  "parentResourceId": "'$ARTICLE_ID'",
  "filePath": "'$OUTPUT_DIR'/images/article-1-hero.md",
  "status": "draft",
  "createdBy": "'$AGENT_NAME'"
}' --url http://localhost:3210)
```

### Step 4: Batch Creation for Bulk Resources

For efficiency when registering many child resources at once, use `resources:batchCreate`:

```bash
npx convex run resources:batchCreate '{
  "resources": [
    { "projectId": "'$PID'", "resourceType": "social_post", "title": "Facebook post for Article 1", "taskId": "'$TID'", "parentResourceId": "'$AID1'", "status": "draft", "createdBy": "'$AGENT'" },
    { "projectId": "'$PID'", "resourceType": "social_post", "title": "Instagram post for Article 1", "taskId": "'$TID'", "parentResourceId": "'$AID1'", "status": "draft", "createdBy": "'$AGENT'" }
  ]
}' --url http://localhost:3210
```

### Step 5: Single completeStep Call

After ALL articles/resources are produced and registered, call completeStep ONCE:

```bash
# Collect ALL resource IDs produced in this pass
npx convex run pipeline:completeStep '{
  "taskId": "'$TASK_ID'",
  "agentName": "'$AGENT_NAME'",
  "resourceIds": ["id1", "id2", "id3"]
}' --url http://localhost:3210
```

**Never call completeStep per article.** One call at the end with all resource IDs.

### Agent Role Summary (Multi-Article)

| Agent | Resource Type | Parent | Count per Campaign |
|-------|-------------|--------|-------------------|
| vibe-researcher / vibe-keyword-researcher | `research_material` | null (campaign-level) | 1 shared resource |
| vibe-brief-writer | `brief` | null (campaign-level) | 1 shared resource or N briefs |
| vibe-content-writer | `article` | null (root) | N articles |
| vibe-content-reviewer | updates existing `article` status | -- | Reviews N articles |
| vibe-humanizer | updates existing `article` status | -- | Humanizes N articles |
| vibe-image-director | `image_prompt` | article._id | N prompts (child) |
| vibe-image-creator | `image` | image_prompt._id | N images (child of prompt) |
| vibe-social-writer | `social_post` | article._id | N x platforms (child) |
| vibe-ad-writer | `ad_copy` | article._id | N ad sets (child) |
| vibe-email-writer | `email_excerpt` | article._id | N excerpts (child) |
| vibe-script-writer | `video_script` | article._id | N scripts (child) |
