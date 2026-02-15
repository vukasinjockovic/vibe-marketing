---
name: youtube-research
displayName: YouTube Research
description: Search YouTube, extract video transcripts and comments for audience voice data. Free via yt-dlp. Identifies emotional language, common themes, and content gaps from the audience's own words. Used in research phases for copy mining and content ideation.
category: research
type: tool
---

# YouTube Research Skill

Extract audience voice data from YouTube videos -- transcripts, comments, and engagement metadata. This skill uses `yt-dlp` (free, no API key required) to search YouTube, download subtitles, and mine comments for real audience language.

---

## When to Use This Skill

### Audience Voice Mining
YouTube comments are an unfiltered source of real audience language. Unlike reviews or forum posts, commenters react emotionally and immediately. This makes them ideal for:
- Discovering the exact words your audience uses to describe their feelings
- Identifying emotional triggers (what makes people cry, laugh, share)
- Finding objections and hesitations in their own language
- Mapping identity markers ("as a grandparent, I...")

### Content Gap Analysis
By analyzing what exists on YouTube for a topic, you can identify:
- What angles are overdone vs. underserved
- What video lengths dominate (opportunity in the opposite)
- Which sub-topics get the most engagement
- What the audience is asking for in comments but nobody is creating

### Emotional Language Extraction
Comments on emotional content (reunions, surprises, tributes) contain raw emotional vocabulary that feeds directly into:
- Email subject lines that trigger opens
- Social media hooks that stop the scroll
- Landing page headlines that connect emotionally
- Ad copy that resonates at an identity level

### Competitor Content Analysis
See what content your competitors (or adjacent channels) produce, how it performs, and what their audience says about it.

---

## How to Use

### CLI Interface

```bash
# Search YouTube and extract everything (transcripts + comments + metadata)
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "grandparent reunion surprise" \
    --max-videos 5 \
    --output json

# Extract only metadata (fast, no downloads)
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "baby gender reveal reaction" \
    --max-videos 10 \
    --extract metadata \
    --output json

# Process specific video URLs
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --video-urls "https://youtube.com/watch?v=abc" "https://youtube.com/watch?v=def" \
    --extract transcripts,comments \
    --output markdown

# Get transcripts in a different language
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "sorpresa abuela" \
    --language es \
    --max-videos 3
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--search` | One of search/video-urls | -- | YouTube search query |
| `--video-urls` | One of search/video-urls | -- | Direct YouTube URLs |
| `--max-videos` | No | 5 | Max videos to process |
| `--extract` | No | transcripts,comments,metadata | Comma-separated extraction targets |
| `--output` | No | json | Output format: json or markdown |
| `--language` | No | en | Subtitle language code |

### Output

- **JSON mode**: Structured data to stdout. Includes per-video metadata, transcript excerpts, top comments, comment themes, and aggregate insights.
- **Markdown mode**: Human-readable report with quotes and analysis. Suitable for direct inclusion in research documents.
- **Progress**: Printed to stderr so it does not interfere with JSON output.
- **Transcripts**: Full transcripts saved to `/tmp/yt_transcripts/{video_id}.txt` for agent follow-up.

---

## Practical Examples by Niche

### Wedding / Event Content
```bash
# Find emotional wedding moments for copy mining
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "surprise wedding first look reaction" \
    --max-videos 5 --extract comments --output json

# Mine father-daughter dance videos for tribute product copy
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "father daughter wedding dance tribute" \
    --max-videos 5 --output markdown
```

**What you get:** Comments like "I wish my dad was still here for this" and "I'm not crying you're crying" -- real emotional language that powers tribute product marketing.

### Grandparent / Legacy Content
```bash
# Reunion and surprise content
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "grandparent meets grandchild first time" \
    --max-videos 5

# Memorial and tribute content
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "grandparent tribute video memorial" \
    --max-videos 5 --extract comments
```

**What you get:** Pain points around loss ("I lost my grandmother before she met my kids"), desire language ("I wish I had recorded more of our conversations"), and identity markers ("as a grandchild who was raised by my grandparents...").

### Baby / Family Milestone Content
```bash
python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "baby reveal to grandparents reaction" \
    --max-videos 5

python .claude/skills/youtube-research/scripts/youtube_research.py \
    --search "first grandchild announcement compilation" \
    --max-videos 3 --extract comments --output markdown
```

**What you get:** High-engagement comments showing exactly how families describe these moments, what they wish they had captured, and what products/services they mention.

---

## How This Feeds Other Skills

### Content Writing Procedures
Transcript excerpts and audience voice samples feed directly into content creation. Instead of inventing marketing language, writers use the actual vocabulary from YouTube comments:
- Pain point language -> Headlines and hooks
- Emotional phrases -> Email subject lines
- Identity markers -> Audience segmentation copy
- Desire language -> CTA and offer framing

### Focus Group Enrichment
Comment themes and emotional language from YouTube supplement focus group profiles:
- `languagePatterns`: Populated with real quotes from comments
- `emotionalTriggers`: Derived from comment themes analysis
- `painPoints`: Extracted from frustration/loss/grief comments
- `coreDesires`: Derived from aspiration/wish comments

### Google Trends Research (Synergy)
Use Google Trends to find trending topics, then use YouTube Research to mine audience voice for those topics:
1. Run google-suggest-research to find trending queries
2. Feed top queries into `--search` for YouTube Research
3. Extract comment-level audience language for the trending topic
4. Use language patterns in time-sensitive content creation

### Audience Research Procedures
This tool complements `scrape_reddit.py` and `scrape_reviews.py` as a third source of audience voice data. YouTube comments tend to be more emotional and reactive than Reddit posts or product reviews, providing a complementary signal.

---

## Dependencies

- **yt-dlp**: `pip install yt-dlp` (free, no API key)
- **Python 3.10+**: Standard library only (no external packages beyond yt-dlp)
- **Network access**: Needs to reach youtube.com

No API keys, no paid services, no rate limit concerns for normal usage.

---

## Limitations

- **Comment availability**: Some videos have comments disabled. The tool handles this gracefully.
- **Transcript availability**: Not all videos have subtitles. Auto-generated subtitles are tried as fallback.
- **Rate limiting**: Processing many videos quickly may trigger YouTube rate limits. Keep `--max-videos` reasonable (5-10 per run).
- **Comment depth**: yt-dlp retrieves top-level comments sorted by relevance. Reply threads are not deeply traversed.
- **Language**: Comment analysis keyword lists are English-focused. Use `--language` for subtitle language only.

---

## Error Handling

The tool is designed for resilience:
- Individual video failures do not crash the batch
- Missing transcripts are reported but processing continues
- Missing comments are reported but processing continues
- Network timeouts have reasonable defaults (60-120 seconds per operation)
- Progress is reported to stderr so agents can monitor long runs
- Empty results return valid JSON with an error message
