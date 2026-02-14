# audience-analysis-procedures

SOP for the vibe-audience-parser agent. Parses uploaded audience research documents into structured focus group profiles, runs fuzzy matching against existing groups, and stages results for human review.

## Trigger

Activated when:
- A task of type "document-import" is assigned to vibe-audience-parser
- The task metadata contains `uploadedFilePath` and `productId`
- The pipeline step is "parse-document"

## Prerequisites

- Python 3.12+ available
- pandoc installed (for .docx support)
- Convex backend running at localhost:3210

## Execution Steps

### Step 1: Read Task Metadata

```bash
# Get task details
npx convex run tasks:get '{"id":"<TASK_ID>"}' --url http://localhost:3210
```

Extract from task metadata:
- `uploadedFilePath` -- path to the uploaded document
- `productId` -- the product these focus groups belong to
- `projectId` -- the project context
- `sourceFormat` -- file format (md, txt, docx, pdf)

### Step 2: Acquire Pipeline Lock

```bash
npx convex run pipeline:acquireLock '{"taskId":"<TASK_ID>","agentName":"vibe-audience-parser"}' --url http://localhost:3210
```

If lock is not acquired, exit immediately. Another agent is already working on this task.

### Step 3: Convert File Format (if needed)

Based on `sourceFormat` or file extension:

**Markdown / Text (.md, .txt):**
No conversion needed. Read the file directly.

**Word Document (.docx):**
```bash
bash .claude/skills/audience-analysis-procedures/scripts/convert_docx.sh "INPUT_PATH" "/tmp/parsed_doc.md"
```

**PDF (.pdf):**
```bash
python3 .claude/skills/audience-analysis-procedures/scripts/extract_pdf_text.py "INPUT_PATH" "/tmp/parsed_doc.md"
```

After conversion, the working file is at `/tmp/parsed_doc.md` (or the original path for .md/.txt).

### Step 4: Parse the Document

```bash
python3 .claude/skills/audience-analysis-procedures/scripts/parse_audience_doc.py "WORKING_FILE" --output "/tmp/parsed_groups.json"
```

This script:
1. Splits the document into individual focus group sections
2. Extracts structured fields for each group (name, nickname, demographics, psychographics, desires, pain points, etc.)
3. Scores completeness based on weighted field presence
4. Outputs a JSON array of parsed groups

Review `/tmp/parsed_groups.json` to verify the output. Check:
- All expected groups were detected (compare to table of contents if present)
- Names and nicknames were extracted correctly
- Array fields (desires, pain points, etc.) have reasonable item counts

### Step 5: Fetch Existing Focus Groups

```bash
npx convex run focusGroups:listByProduct '{"productId":"<PRODUCT_ID>"}' --url http://localhost:3210 > /tmp/existing_groups.json
```

If this returns an empty array, all parsed groups will be `create_new`.

### Step 6: Run Fuzzy Matching

For each parsed group, run the matching script against existing groups:

```bash
python3 .claude/skills/audience-analysis-procedures/scripts/fuzzy_match.py \
  --parsed-name "Group Name" \
  --parsed-nickname "Nickname" \
  --existing-json /tmp/existing_groups.json
```

The script outputs JSON with:
- `matchStatus`: `create_new`, `enrich_existing`, or `possible_match`
- `matchedId`: The ID of the matched existing group (or null)
- `matchConfidence`: 0.0 to 1.0
- `matchReason`: Why this match was selected

**Match priorities:**
1. Exact name match (confidence 1.0) -> `enrich_existing`
2. Exact nickname match (confidence 0.95) -> `enrich_existing`
3. Name substring match (confidence 0.85) -> `possible_match`
4. Levenshtein similarity >= 0.8 -> `possible_match`
5. Nickname-to-name cross-match >= 0.8 -> `possible_match`
6. No match (confidence 0.0) -> `create_new`

### Step 7: Build Staging Records

For each parsed group, combine:
- The parsed fields from Step 4
- The match result from Step 6
- Staging metadata:
  - `taskId`: the current task ID
  - `productId`: from task metadata
  - `projectId`: from task metadata
  - `reviewStatus`: `"pending_review"`
  - `completenessScore`: from the parser output
  - `missingFields`: from the parser output
  - `needsEnrichment`: `true` if `completenessScore < 100` or any enrichment fields missing
  - `source`: `"uploaded"`

### Step 8: Write to Staging

```bash
npx convex run focusGroupStaging:createBatch '{"groups":[...]}' --url http://localhost:3210
```

The `createBatch` function accepts an array of group objects. Each object must include all required staging fields (taskId, productId, projectId, matchStatus, reviewStatus, completenessScore, missingFields, needsEnrichment, name) plus any optional fields that were extracted.

**Important:** Convex IDs must be valid. For `create_new` groups, omit `matchedFocusGroupId`. For `enrich_existing` or `possible_match`, include the `matchedFocusGroupId` from the match result.

### Step 9: Log Activity

```bash
npx convex run activities:log '{
  "type": "document_parsed",
  "agentName": "vibe-audience-parser",
  "taskId": "<TASK_ID>",
  "details": "Parsed N focus groups from FILENAME (X create_new, Y enrich_existing, Z possible_match). Average completeness: NN%."
}' --url http://localhost:3210
```

### Step 10: Register Resource + Complete Pipeline Step

Register the source document as a resource, then complete the step:

```bash
RESOURCE_ID=$(npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "research_material",
  "title": "Audience Parse: <source filename>",
  "taskId": "<TASK_ID>",
  "filePath": "<path to uploaded document>",
  "status": "draft",
  "pipelineStage": "research",
  "createdBy": "vibe-audience-parser",
  "metadata": {"focusGroupCount": N, "matchBreakdown": {"create_new": X, "enrich_existing": Y}}
}' --url http://localhost:3210)

npx convex run pipeline:completeStep '{
  "taskId": "<TASK_ID>",
  "agentName": "vibe-audience-parser",
  "qualityScore": 7,
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for full protocol.

NEVER update task status directly -- only through `pipeline:completeStep`.

## Completeness Scoring

The parser scores each group based on the presence of enrichment-related fields. These fields are typically NOT present in uploaded documents and will be filled by enrichment agents later.

**Weighted fields:**
| Field | Weight |
|-------|--------|
| awarenessStage | 15 |
| sophisticationLevel | 10 |
| contentPreferences | 10 |
| influenceSources | 10 |
| purchaseBehavior | 15 |
| competitorContext | 10 |
| communicationStyle | 10 |
| seasonalContext | 5 |
| negativeTriggers | 10 |
| awarenessSignals | 5 |
| **Total** | **100** |

A score of 0% is normal for raw document imports. Enrichment agents will raise this score.

## Error Handling

1. **File not found:** Log error, set task to "blocked" with notes, notify vibe-orchestrator
2. **Parse failure (0 groups):** Log warning, check if file format is supported, set task to "blocked"
3. **Convex write failure:** Retry once, then log error and set task to "blocked"
4. **pandoc not installed:** Log error with install instructions, set task to "blocked"
5. **Partial parse (some groups failed):** Continue with successfully parsed groups, note failures in activity log

## Reference Files

- `references/focus-group-schema.json` -- Complete field schema with types and descriptions
- `references/parsing-patterns.md` -- Document format patterns the parser recognizes
- `references/example-input-output.md` -- Worked example from raw text to JSON
- `references/known-formats.md` -- Documented formats we have tested against

## Scripts

- `scripts/parse_audience_doc.py` -- Main parser (regex + heuristics)
- `scripts/fuzzy_match.py` -- Levenshtein-based name matching
- `scripts/extract_pdf_text.py` -- PDF text extraction (pymupdf/pdfplumber)
- `scripts/convert_docx.sh` -- pandoc wrapper for .docx

## Post-Completion

After this agent completes:
1. The parsed groups are in `focusGroupStaging` with `reviewStatus: "pending_review"`
2. The dashboard shows the staging review UI
3. A human reviews, edits, approves, or rejects each group
4. Approved groups are imported to the `focusGroups` table by the import step
5. The enrichment agent (vibe-audience-enricher) fills missing fields on imported groups
