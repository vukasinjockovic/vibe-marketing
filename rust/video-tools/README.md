# Video Tools

Client-side video processing. No upload, no watermark, instant.

## Why This Wins
- **Strongest frustration signals**: "trim video online free no watermark" — users hate current tools
- **Massive pain point**: uploading a 500MB video takes minutes. Client-side = instant start.
- **"compress video for discord"** — specific use case with huge gaming audience
- **FFmpeg.wasm exists** but nobody built a polished UI around it

## Revenue Model
- **Primary**: Display ads ($8-12 RPM)
- **Secondary**: None needed — pure ad play with volume

## Tools to Build
1. Trim/cut video
2. Compress video (target file size: "compress to 25MB for Discord")
3. Convert video (MP4/MOV/AVI/WebM)
4. Video to GIF
5. Video to MP3 (extract audio)
6. Merge videos
7. Add subtitles
8. Resize/crop video
9. Remove audio from video
10. Screen recorder (MediaRecorder API + WASM encoding)

## Programmatic SEO
- "compress video to [25mb/50mb/100mb] for [discord/email/whatsapp]"
- "convert [format] to [format] free online"
- "trim video online free no watermark"
- "video to gif [high quality/with sound/loop]"

## Autocomplete Signals (Confirmed Demand)
- "trim video online free no watermark" — peak frustration
- "compress video for discord" — specific use case
- "video to gif online" — high demand
- "merge videos online without watermark reddit" — Reddit frustration
- "screen recorder online free" / "without download"

## Competitors
| Site | Weakness |
|------|----------|
| Kapwing | Watermark on free tier |
| Clipchamp | Microsoft-owned, pushes Edge |
| EZGif | Works but ugly, slow, uploads |
| 123apps | Uploads to server |

## Tech Stack
- FFmpeg compiled to WASM (ffmpeg.wasm)
- Web Workers for processing (don't freeze UI)
- File System Access API for large files
- Progress indicators (FFmpeg progress callbacks)
- Static hosting

## Challenges
- Large video files stress browser memory
- FFmpeg.wasm is ~25MB download (needs lazy loading)
- Some codecs have licensing issues (H.265)
- Mobile browser support is limited for large files
