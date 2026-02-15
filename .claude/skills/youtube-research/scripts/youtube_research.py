#!/usr/bin/env python3
"""YouTube Research Tool -- Extract audience voice data from YouTube.

Searches YouTube, downloads transcripts/subtitles, and extracts audience
insights from comments. Uses yt-dlp (free, no API key required).

Usage:
    python youtube_research.py --search "grandparent reunion surprise" \
        --max-videos 5 --extract transcripts,comments --output json

    python youtube_research.py --video-urls "https://youtube.com/watch?v=abc" \
        --extract metadata --output markdown

Returns JSON (default) or Markdown with video metadata, transcripts,
top comments, comment themes, and aggregate audience insights.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


TRANSCRIPT_DIR = "/tmp/yt_transcripts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_ytdlp():
    """Verify yt-dlp is installed and accessible."""
    if shutil.which("yt-dlp") is None:
        print("ERROR: yt-dlp is not installed. Install with: pip install yt-dlp",
              file=sys.stderr)
        sys.exit(1)


def run_ytdlp(args, timeout=120):
    """Run a yt-dlp command and return (stdout, stderr, returncode)."""
    cmd = ["yt-dlp"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        print(f"  yt-dlp timed out after {timeout}s: {' '.join(cmd[:6])}...",
              file=sys.stderr)
        return "", "timeout", 1
    except Exception as e:
        print(f"  yt-dlp error: {e}", file=sys.stderr)
        return "", str(e), 1


def parse_vtt(vtt_text):
    """Parse VTT subtitle content into plain text, removing timestamps and tags."""
    lines = []
    seen = set()
    for line in vtt_text.splitlines():
        line = line.strip()
        # Skip VTT headers, timestamps, position markers
        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if line.startswith("NOTE"):
            continue
        if re.match(r"^\d{2}:\d{2}", line):
            continue
        if re.match(r"^[\d\-]+$", line):
            continue
        if "align:" in line or "position:" in line:
            continue
        # Strip HTML-like tags
        clean = re.sub(r"<[^>]+>", "", line)
        clean = clean.strip()
        if clean and clean not in seen:
            seen.add(clean)
            lines.append(clean)
    return " ".join(lines)


def parse_srt(srt_text):
    """Parse SRT subtitle content into plain text."""
    lines = []
    seen = set()
    for line in srt_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"\d{2}:\d{2}:\d{2}", line):
            continue
        clean = re.sub(r"<[^>]+>", "", line)
        clean = clean.strip()
        if clean and clean not in seen:
            seen.add(clean)
            lines.append(clean)
    return " ".join(lines)


def format_number(n):
    """Format a number for display (e.g., 2500000 -> '2.5M')."""
    if n is None:
        return "N/A"
    if isinstance(n, str):
        try:
            n = int(n)
        except (ValueError, TypeError):
            return str(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def search_youtube(query, max_videos=5):
    """Search YouTube and return video metadata as list of dicts."""
    print(f"Searching YouTube for: {query}", file=sys.stderr)
    search_term = f"ytsearch{max_videos}:{query}"
    stdout, stderr, rc = run_ytdlp(
        [
            "--dump-json",
            "--no-download",
            "--flat-playlist",
            search_term,
        ],
        timeout=60,
    )

    if rc != 0:
        # flat-playlist may not work for search; try without it
        stdout, stderr, rc = run_ytdlp(
            [
                "--dump-json",
                "--no-download",
                search_term,
            ],
            timeout=90,
        )

    results = []
    if stdout:
        for line in stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                results.append(data)
            except json.JSONDecodeError:
                continue

    print(f"  Found {len(results)} videos", file=sys.stderr)
    return results


def get_video_metadata(video_url):
    """Get metadata for a single video URL."""
    print(f"Fetching metadata: {video_url}", file=sys.stderr)
    stdout, stderr, rc = run_ytdlp(
        [
            "--dump-json",
            "--no-download",
            video_url,
        ],
        timeout=60,
    )
    if rc != 0 or not stdout.strip():
        print(f"  Failed to get metadata for {video_url}", file=sys.stderr)
        return None
    try:
        return json.loads(stdout.strip().splitlines()[0])
    except (json.JSONDecodeError, IndexError):
        return None


def extract_metadata(info):
    """Extract structured metadata from yt-dlp info dict."""
    video_id = info.get("id", "unknown")
    duration = info.get("duration")
    duration_str = None
    if duration:
        hours = int(duration) // 3600
        minutes = (int(duration) % 3600) // 60
        seconds = int(duration) % 60
        if hours > 0:
            duration_str = f"PT{hours}H{minutes}M{seconds}S"
        else:
            duration_str = f"PT{minutes}M{seconds}S"

    upload_date = info.get("upload_date", "")
    published = None
    if upload_date and len(upload_date) == 8:
        published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

    return {
        "video_id": video_id,
        "title": info.get("title", ""),
        "url": info.get("webpage_url", f"https://youtube.com/watch?v={video_id}"),
        "channel": info.get("channel", info.get("uploader", "")),
        "channel_id": info.get("channel_id", ""),
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "comment_count": info.get("comment_count"),
        "published": published,
        "duration": duration_str,
        "duration_seconds": duration,
        "description": (info.get("description") or "")[:1000],
        "tags": info.get("tags", [])[:20],
        "categories": info.get("categories", []),
    }


def download_transcript(video_id, video_url, language="en"):
    """Download subtitles/transcript for a video. Returns transcript text or None."""
    print(f"  Downloading transcript for {video_id}...", file=sys.stderr)
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    # Clean up any previous files for this video
    for ext in [".vtt", ".srt", ".en.vtt", ".en.srt",
                f".{language}.vtt", f".{language}.srt"]:
        path = os.path.join(TRANSCRIPT_DIR, f"{video_id}{ext}")
        if os.path.exists(path):
            os.remove(path)

    # Try manual subtitles first, then auto-generated
    for sub_flag in ["--write-sub", "--write-auto-sub"]:
        stdout, stderr, rc = run_ytdlp(
            [
                sub_flag,
                "--sub-lang", language,
                "--sub-format", "vtt/srt/best",
                "--skip-download",
                "-o", os.path.join(TRANSCRIPT_DIR, "%(id)s"),
                video_url,
            ],
            timeout=60,
        )

        # Look for the generated subtitle file
        for ext in [f".{language}.vtt", ".en.vtt", f".{language}.srt", ".en.srt",
                     ".vtt", ".srt"]:
            candidate = os.path.join(TRANSCRIPT_DIR, f"{video_id}{ext}")
            if os.path.exists(candidate):
                with open(candidate, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if ".vtt" in ext:
                    text = parse_vtt(content)
                else:
                    text = parse_srt(content)
                if text and len(text) > 50:
                    # Save plain text version
                    txt_path = os.path.join(TRANSCRIPT_DIR, f"{video_id}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"    Transcript saved: {txt_path} ({len(text)} chars)",
                          file=sys.stderr)
                    return text

    print(f"    No transcript available for {video_id}", file=sys.stderr)
    return None


def download_comments(video_id, video_url, max_comments=100):
    """Download comments for a video. Returns list of comment dicts."""
    print(f"  Downloading comments for {video_id}...", file=sys.stderr)

    # Use a temp directory for the comment JSON
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s")
        stdout, stderr, rc = run_ytdlp(
            [
                "--write-comments",
                "--extractor-args",
                f"youtube:max_comments={max_comments},all,100,100",
                "--skip-download",
                "-o", output_template,
                video_url,
            ],
            timeout=90,
        )

        # yt-dlp writes comments into the info JSON
        info_file = os.path.join(tmpdir, f"{video_id}.info.json")
        if not os.path.exists(info_file):
            # Try without the video id
            for f in os.listdir(tmpdir):
                if f.endswith(".info.json"):
                    info_file = os.path.join(tmpdir, f)
                    break

        if os.path.exists(info_file):
            try:
                with open(info_file, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                raw_comments = data.get("comments", [])
                comments = []
                for c in raw_comments:
                    comments.append({
                        "text": c.get("text", ""),
                        "likes": c.get("like_count", 0),
                        "replies": c.get("reply_count", 0) if "reply_count" in c else 0,
                        "author": c.get("author", ""),
                        "is_pinned": c.get("is_pinned", False),
                        "is_hearted": c.get("is_favorited", False),
                    })
                # Sort by likes descending
                comments.sort(key=lambda x: x.get("likes", 0) or 0, reverse=True)
                print(f"    Got {len(comments)} comments", file=sys.stderr)
                return comments
            except (json.JSONDecodeError, KeyError) as e:
                print(f"    Error parsing comments: {e}", file=sys.stderr)

    print(f"    No comments retrieved for {video_id}", file=sys.stderr)
    return []


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

# Emotion/theme word lists for comment analysis
EMOTIONAL_PHRASES = [
    "made me cry", "i'm crying", "tears", "sobbing", "bawling",
    "broke my heart", "hits hard", "beautiful", "so touching",
    "i miss", "i wish", "i lost my", "passed away", "gone too soon",
    "treasure", "cherish", "grateful", "blessed", "thankful",
    "this is everything", "goosebumps", "chills", "pure joy",
    "love this", "so wholesome", "faith in humanity",
    "my heart", "can't stop watching", "watched this",
    "who's cutting onions", "onion ninjas", "not crying you're crying",
]

THEME_KEYWORDS = {
    "nostalgia": ["remember", "reminds me", "back when", "used to", "growing up",
                  "childhood", "those days", "miss the old", "takes me back"],
    "loss_grief": ["passed away", "lost my", "gone", "miss you", "rest in peace",
                   "rip", "heaven", "watching over", "angel", "no longer with us"],
    "family_connection": ["family", "grandma", "grandpa", "grandmother", "grandfather",
                          "mom", "dad", "mother", "father", "parents", "siblings",
                          "kids", "children", "son", "daughter", "baby"],
    "tears_of_joy": ["happy tears", "tears of joy", "crying happy", "joyful",
                     "made me smile", "so happy", "wonderful", "amazing moment"],
    "inspiration": ["inspired", "motivation", "dream", "never give up", "believe",
                    "strength", "courage", "brave", "hero", "goal"],
    "surprise_reaction": ["surprise", "shocked", "didn't expect", "omg", "oh my god",
                          "reaction", "priceless", "face was", "look on their face"],
    "relatability": ["same", "me too", "i relate", "my story", "going through",
                     "been there", "exactly", "literally me", "this is me"],
    "desire_aspiration": ["i want", "i wish", "one day", "hope to", "dream of",
                          "goals", "bucket list", "someday", "can't wait"],
    "frustration": ["frustrated", "annoyed", "tired of", "sick of", "hate",
                    "disappointed", "worst", "terrible", "awful"],
    "humor": ["lol", "lmao", "hilarious", "funny", "dead", "i can't",
              "comedy gold", "killed me", "rofl"],
}


def analyze_comments(comments):
    """Analyze comments to extract themes, emotional language, and patterns."""
    if not comments:
        return {
            "comment_themes": [],
            "emotional_language": [],
            "top_phrases": [],
            "sentiment_summary": "no_comments",
        }

    all_text = " ".join(c.get("text", "").lower() for c in comments)
    all_text_lines = [c.get("text", "") for c in comments if c.get("text")]

    # Detect themes
    theme_scores = {}
    for theme, keywords in THEME_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in all_text)
        if count > 0:
            theme_scores[theme] = count

    # Sort themes by score
    sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
    detected_themes = [t[0] for t in sorted_themes if t[1] >= 1]

    # Extract emotional phrases actually found
    found_emotional = []
    for phrase in EMOTIONAL_PHRASES:
        if phrase in all_text:
            found_emotional.append(phrase)

    # Also extract high-signal phrases from highly-liked comments
    high_signal_phrases = []
    for c in comments:
        likes = c.get("likes", 0) or 0
        text = c.get("text", "").strip()
        if likes >= 10 and len(text) > 20 and len(text) < 300:
            high_signal_phrases.append(text)
        if len(high_signal_phrases) >= 20:
            break

    # Detect overall sentiment
    positive_count = sum(1 for phrase in ["love", "beautiful", "amazing", "great",
                                           "wonderful", "best", "happy", "joy",
                                           "perfect", "incredible"]
                         if phrase in all_text)
    negative_count = sum(1 for phrase in ["hate", "terrible", "awful", "worst",
                                           "disappointing", "bad", "boring",
                                           "trash", "cringe"]
                         if phrase in all_text)

    if positive_count > negative_count * 2:
        sentiment = "overwhelmingly_positive"
    elif positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "mixed"

    return {
        "comment_themes": detected_themes[:10],
        "emotional_language": found_emotional[:15],
        "top_phrases": high_signal_phrases[:20],
        "sentiment_summary": sentiment,
    }


def compute_aggregate_insights(all_results):
    """Compute aggregate insights across all processed videos."""
    total_views = 0
    total_likes = 0
    all_themes = Counter()
    all_emotional = Counter()
    all_phrases = []
    channels = set()
    durations = []

    for r in all_results:
        views = r.get("views") or 0
        total_views += views
        total_likes += (r.get("likes") or 0)
        channels.add(r.get("channel", ""))

        if r.get("duration_seconds"):
            durations.append(r["duration_seconds"])

        analysis = r.get("_comment_analysis", {})
        for theme in analysis.get("comment_themes", []):
            all_themes[theme] += 1
        for phrase in analysis.get("emotional_language", []):
            all_emotional[phrase] += 1
        for phrase in analysis.get("top_phrases", []):
            all_phrases.append(phrase)

    # Most common themes across videos
    common_themes = [t for t, _ in all_themes.most_common(10)]

    # Most common emotional language
    emotional_lang = [e for e, _ in all_emotional.most_common(15)]

    # Deduplicate and pick top audience phrases
    seen_phrases = set()
    unique_phrases = []
    for p in all_phrases:
        normalized = p.lower().strip()
        if normalized not in seen_phrases:
            seen_phrases.add(normalized)
            unique_phrases.append(p)
        if len(unique_phrases) >= 30:
            break

    # Average duration
    avg_duration = None
    if durations:
        avg_duration = sum(durations) / len(durations)

    # Content gap analysis hint
    content_gaps = []
    if total_views > 0 and len(all_results) > 0:
        avg_views = total_views / len(all_results)
        if avg_views > 100000:
            content_gaps.append("High view counts indicate strong audience demand in this topic")
        if "loss_grief" in all_themes and "humor" not in all_themes:
            content_gaps.append("Emotional/grief content dominates -- lighter/humorous angles may be underserved")
        if "relatability" in all_themes:
            content_gaps.append("Strong relatability signals -- personal story content resonates")
        if avg_duration and avg_duration < 300:
            content_gaps.append("Most content is short-form (<5 min) -- longer deep-dive content may be a gap")
        elif avg_duration and avg_duration > 600:
            content_gaps.append("Content tends to be long-form -- short punchy compilations may be a gap")

    return {
        "total_views": total_views,
        "total_likes": total_likes,
        "unique_channels": len(channels - {""}),
        "avg_duration_seconds": int(avg_duration) if avg_duration else None,
        "common_comment_themes": common_themes,
        "emotional_language": emotional_lang,
        "audience_voice_samples": unique_phrases[:30],
        "content_gaps": content_gaps if content_gaps else ["Insufficient data for gap analysis"],
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_json_output(query, results, aggregate):
    """Format results as JSON."""
    # Remove internal analysis key from results
    clean_results = []
    for r in results:
        cr = {k: v for k, v in r.items() if not k.startswith("_")}
        clean_results.append(cr)

    output = {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "videos_processed": len(clean_results),
        "results": clean_results,
        "aggregate_insights": aggregate,
    }
    return json.dumps(output, indent=2, ensure_ascii=False, default=str)


def format_markdown_output(query, results, aggregate):
    """Format results as Markdown."""
    lines = []
    lines.append(f"# YouTube Research: {query}")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Videos processed:** {len(results)}")
    lines.append(f"**Total views:** {format_number(aggregate.get('total_views', 0))}")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    # Aggregate insights
    lines.append("## Aggregate Insights")
    lines.append("")
    if aggregate.get("common_comment_themes"):
        lines.append("### Common Themes")
        for theme in aggregate["common_comment_themes"]:
            lines.append(f"- {theme.replace('_', ' ').title()}")
        lines.append("")

    if aggregate.get("emotional_language"):
        lines.append("### Emotional Language Detected")
        for phrase in aggregate["emotional_language"]:
            lines.append(f'- "{phrase}"')
        lines.append("")

    if aggregate.get("audience_voice_samples"):
        lines.append("### Audience Voice Samples (from comments)")
        for phrase in aggregate["audience_voice_samples"][:15]:
            lines.append(f'> "{phrase}"')
            lines.append("")

    if aggregate.get("content_gaps"):
        lines.append("### Content Gap Analysis")
        for gap in aggregate["content_gaps"]:
            lines.append(f"- {gap}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Individual video results
    lines.append("## Video Results")
    lines.append("")

    for i, r in enumerate(results, 1):
        title = r.get("title", "Unknown")
        lines.append(f"### {i}. {title}")
        lines.append("")
        lines.append(f"- **URL:** {r.get('url', 'N/A')}")
        lines.append(f"- **Channel:** {r.get('channel', 'N/A')}")
        lines.append(f"- **Views:** {format_number(r.get('views'))}")
        lines.append(f"- **Likes:** {format_number(r.get('likes'))}")
        lines.append(f"- **Published:** {r.get('published', 'N/A')}")
        lines.append(f"- **Duration:** {r.get('duration', 'N/A')}")
        lines.append("")

        if r.get("transcript_excerpt"):
            lines.append("**Transcript Excerpt:**")
            lines.append(f"```")
            lines.append(r["transcript_excerpt"][:800])
            lines.append(f"```")
            lines.append("")

        if r.get("top_comments"):
            lines.append("**Top Comments:**")
            for c in r["top_comments"][:5]:
                likes = c.get("likes", 0) or 0
                lines.append(f'> "{c["text"]}" ({likes} likes)')
                lines.append("")

        if r.get("comment_themes"):
            themes_str = ", ".join(t.replace("_", " ") for t in r["comment_themes"])
            lines.append(f"**Comment Themes:** {themes_str}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_video(info, extract_types, language="en"):
    """Process a single video: extract metadata, transcript, comments."""
    meta = extract_metadata(info)
    video_id = meta["video_id"]
    video_url = meta["url"]

    result = dict(meta)
    result["transcript_excerpt"] = None
    result["full_transcript_path"] = None
    result["top_comments"] = []
    result["comment_themes"] = []

    # Transcript extraction
    if "transcripts" in extract_types:
        try:
            transcript = download_transcript(video_id, video_url, language)
            if transcript:
                result["transcript_excerpt"] = transcript[:500]
                result["full_transcript_path"] = os.path.join(
                    TRANSCRIPT_DIR, f"{video_id}.txt"
                )
        except Exception as e:
            print(f"  Transcript error for {video_id}: {e}", file=sys.stderr)

    # Comment extraction
    comment_analysis = {}
    if "comments" in extract_types:
        try:
            comments = download_comments(video_id, video_url)
            # Keep top 20 comments for output
            result["top_comments"] = [
                {"text": c["text"], "likes": c["likes"], "replies": c["replies"]}
                for c in comments[:20]
            ]
            comment_analysis = analyze_comments(comments)
            result["comment_themes"] = comment_analysis.get("comment_themes", [])
        except Exception as e:
            print(f"  Comment error for {video_id}: {e}", file=sys.stderr)

    # Store analysis internally for aggregation
    result["_comment_analysis"] = comment_analysis

    return result


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Research Tool -- extract audience voice data from YouTube",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search and extract everything
  python youtube_research.py --search "grandparent reunion surprise" --max-videos 5

  # Process specific URLs, metadata only
  python youtube_research.py --video-urls "https://youtube.com/watch?v=abc" --extract metadata

  # Search with markdown output
  python youtube_research.py --search "baby reveal reactions" --output markdown
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--search",
        type=str,
        help="YouTube search query",
    )
    group.add_argument(
        "--video-urls",
        nargs="+",
        help="Direct YouTube video URLs",
    )

    parser.add_argument(
        "--max-videos",
        type=int,
        default=5,
        help="Maximum videos to process (default: 5)",
    )
    parser.add_argument(
        "--extract",
        type=str,
        default="transcripts,comments,metadata",
        help='Comma-separated: "transcripts", "comments", "metadata" (default: all)',
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Subtitle language code (default: en)",
    )

    args = parser.parse_args()

    # Validate
    check_ytdlp()
    extract_types = [e.strip().lower() for e in args.extract.split(",")]
    valid_types = {"transcripts", "comments", "metadata"}
    for et in extract_types:
        if et not in valid_types:
            print(f"WARNING: Unknown extract type '{et}', ignoring", file=sys.stderr)
    extract_types = [et for et in extract_types if et in valid_types]
    if not extract_types:
        extract_types = ["metadata"]

    query = args.search or " ".join(args.video_urls)

    # Ensure transcript directory exists
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    # Step 1: Get video info dicts
    video_infos = []
    if args.search:
        video_infos = search_youtube(args.search, args.max_videos)
    else:
        for url in args.video_urls:
            info = get_video_metadata(url)
            if info:
                video_infos.append(info)
            if len(video_infos) >= args.max_videos:
                break

    if not video_infos:
        error_result = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "videos_processed": 0,
            "results": [],
            "aggregate_insights": {},
            "error": "No videos found for the given query/URLs",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(0)

    # Step 2: Process each video
    all_results = []
    for i, info in enumerate(video_infos):
        title = info.get("title", "unknown")
        print(f"\n[{i+1}/{len(video_infos)}] Processing: {title}", file=sys.stderr)
        try:
            result = process_video(info, extract_types, args.language)
            all_results.append(result)
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            # Still include partial metadata
            try:
                meta = extract_metadata(info)
                meta["error"] = str(e)
                all_results.append(meta)
            except Exception:
                pass

    # Step 3: Compute aggregate insights
    aggregate = compute_aggregate_insights(all_results)

    # Step 4: Format and output
    if args.output == "markdown":
        output = format_markdown_output(query, all_results, aggregate)
    else:
        output = format_json_output(query, all_results, aggregate)

    print(output)
    print(f"\nDone. Processed {len(all_results)} videos.", file=sys.stderr)


if __name__ == "__main__":
    main()
