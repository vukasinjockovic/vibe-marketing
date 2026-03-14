# Plan: FatStud Vector Knowledge Pipeline (Qdrant + RAG)

**Status:** DEFERRED — execute after scraping phase is complete
**Depends on:** Content scrapers (Phase 1) finishing, millions of markdown files in `knowledge/construction/blogs/`

## Context

We're scraping content from 50+ construction sites into markdown files with YAML frontmatter.
Once we have a critical mass of content (100K+ articles), we need to:
1. Chunk and embed that content into a vector database
2. Build a RAG pipeline so Claude can query relevant knowledge
3. Generate thousands of original FatStud articles from multi-source synthesis

**Output is 100% original FatStud content.** Source tracking is internal-only for QA — no external citations in published articles.

## Architecture

```
Scraped Markdown (filesystem)
    ↓
chunk-and-embed.py (split on headings, overlapping windows)
    ↓
Qdrant (Docker, self-hosted, free)
    ↓
generate-article.py (RAG: query Qdrant → feed chunks to Claude → original article)
    ↓
BusinessPress CMS (PostgreSQL — only final published articles)
```

### Why Qdrant (not PG, not Elasticsearch)

- **Not PG**: App database shouldn't hold millions of knowledge chunks. Separation of concerns.
- **Not Elasticsearch**: Heavier to run, overkill for vector-first search. ES is better when you need complex full-text queries with facets.
- **Qdrant**: Purpose-built for vectors, self-hosted Docker, handles 10M+ vectors on single machine, REST API, metadata filtering, hybrid search (vector + keyword). Free.

## Component 1: Qdrant Setup

```bash
# Add to docker-compose.services.yml
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"   # REST API
    - "6334:6334"   # gRPC
  volumes:
    - qdrant_data:/qdrant/storage
  restart: unless-stopped
```

Collection schema:
```json
{
  "collection_name": "construction_knowledge",
  "vectors": {
    "size": 1024,
    "distance": "Cosine"
  },
  "payload_schema": {
    "domain": "keyword",
    "category": "keyword",
    "content_type": "keyword",
    "source_url": "keyword",
    "article_title": "text",
    "section_heading": "text",
    "chunk_index": "integer",
    "total_chunks": "integer",
    "word_count": "integer",
    "scraped_at": "datetime"
  }
}
```

## Component 2: Chunking Strategy

**Smart chunking — NOT blind token splitting:**

1. **Primary split: headings** — each `## Section` or `### Subsection` becomes a natural chunk
2. **Secondary split: paragraph boundaries** — if a section is still >600 tokens, split at paragraph breaks
3. **Overlapping window** — 50-100 token overlap between consecutive chunks so no context is lost at boundaries
4. **Metadata per chunk:**
   - `source_url` — where it came from
   - `article_title` — the full article title
   - `section_heading` — the heading this chunk falls under
   - `chunk_index` / `total_chunks` — position in article (so adjacent chunks can be retrieved)
   - `domain`, `category`, `content_type` — from YAML frontmatter

**Embedding model options:**
- BGE-large-en-v1.5 (1024-dim) — already used in our memory system, self-hosted via sentence-transformers
- OpenAI text-embedding-3-small (1536-dim) — better quality, costs ~$0.02/1M tokens
- Nomic Embed v1.5 (768-dim) — open source, good quality/speed tradeoff

Recommendation: **BGE-large** for consistency with existing memory system + zero cost.

### Script: `chunk-and-embed.py`

```
python3 scripts/scraping/chunk-and-embed.py                        # Process all unembedded articles
python3 scripts/scraping/chunk-and-embed.py --domain fixr.com      # Single domain
python3 scripts/scraping/chunk-and-embed.py --status               # Show embedding progress
python3 scripts/scraping/chunk-and-embed.py --reembed              # Re-embed all (model change)
```

Flow per article:
1. Read markdown file + parse YAML frontmatter
2. Split into chunks (heading-aware, overlapping)
3. Generate embeddings via BGE-large (batch of 32)
4. Upsert into Qdrant with full metadata payload
5. Track in SQLite (url_inventory.db: `embed_status` column)

## Component 3: RAG Generation Pipeline

### Script: `generate-article.py`

```
python3 scripts/scraping/generate-article.py \
  --topic "how much does a concrete slab cost" \
  --category concrete \
  --target-words 2500 \
  --style cost_guide
```

Flow:
1. Embed the topic query
2. Query Qdrant: top 30 chunks filtered by category, from 3+ different domains
3. Deduplicate overlapping chunks (same article, adjacent positions)
4. Build Claude prompt:
   - System: "You are a FatStud construction expert. Write 100% original content."
   - Context: 30 knowledge chunks with internal source tracking
   - Instructions: target word count, content type, SEO structure
5. Claude generates original article
6. Post-process: add schema markup, internal links, FAQ section
7. Save to BusinessPress CMS (Calculator/Post CPT)

### Internal Source Tracking

Each generated article stores (in a metadata JSON column, not shown to users):
```json
{
  "knowledge_sources": [
    {"url": "https://fixr.com/costs/concrete-slab", "chunks_used": [3, 4, 7]},
    {"url": "https://inspectapedia.com/...", "chunks_used": [1, 2]},
    {"url": "https://costhelper.com/...", "chunks_used": [5]}
  ],
  "generation_model": "claude-sonnet-4-6",
  "generated_at": "2026-03-15T..."
}
```

This is for internal QA only. Published articles show zero attribution to source sites.

## Component 4: Enrichment Before Vectorizing

Before embedding, each article chunk should be enriched with:
- **Category** (already have from scraper)
- **Subcategory** (more granular, e.g. "concrete > stamped concrete")
- **Entity extraction** (materials, tools, measurements, costs mentioned)
- **Difficulty level** (DIY vs pro)
- **Content freshness** (year mentioned, if any)
- **Geographic relevance** (national vs regional pricing)

This enrichment can be done by a lightweight Claude pass (haiku) during the chunking phase, adding metadata that makes Qdrant filtering more powerful.

## Component 5: Near-Duplicate Detection

**Problem:** Multiple sites publish nearly identical tutorials (e.g., 5 versions of "How to Pour a Concrete Slab" that are 85% identical). Without dedup, RAG produces Frankenstein articles mixing incompatible instructions.

**Layer 1: Dedup at scrape/embed time**
- Compute SimHash or MinHash fingerprint per article during chunking
- If two articles from different domains have >80% similarity, keep the longer/more detailed one, mark other as `duplicate`
- Store similarity fingerprint in Qdrant payload for later querying
- Script: `dedup-knowledge.py` — runs after embedding, flags duplicates in batch

**Layer 2: Diverse retrieval (MMR)**
- Use Qdrant's MMR (Maximal Marginal Relevance) instead of plain nearest-neighbor
- MMR returns chunks that are similar to query BUT diverse from each other
- Automatically avoids returning 5 versions of the same paragraph

**Layer 3: Source diversity constraints in generation prompt**
- Enforce: "use chunks from at least 3 different domains"
- Enforce: "max 5 chunks from any single source"
- Forces cross-referencing, prevents single-source regurgitation

## Execution Order

1. ~~Build scrapers~~ ✅ DONE
2. Run scrapers across all 15 domains (days/weeks)
3. Set up Qdrant Docker container
4. Build `chunk-and-embed.py`
5. Build `dedup-knowledge.py` (near-duplicate detection)
6. Build enrichment pass (optional, can add later)
6. Embed all scraped content into Qdrant
7. Build `generate-article.py` (RAG pipeline)
8. Test: generate 10 articles, review quality
9. Scale: batch generate thousands of articles
10. Import into BusinessPress CMS

## Volume Estimates

| Metric | Estimate |
|--------|----------|
| Scraped articles | 100K-500K |
| Avg chunks per article | 5-8 |
| Total chunks in Qdrant | 500K-4M |
| Embedding size (BGE-1024, float32) | ~2-16 GB |
| Qdrant RAM needed | 4-16 GB |
| Generation target | 20K+ original articles |

## Open Questions

- [ ] Which embedding model? (BGE-large vs OpenAI vs Nomic)
- [ ] Enrichment: do it during chunking or as separate pass?
- [ ] How to handle duplicate/near-duplicate content across domains?
- [ ] Rate limiting for Claude generation at scale (batch API?)
- [ ] Quality review pipeline before publishing (automated or manual spot-check?)
