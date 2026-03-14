# Audio Tools

Client-side audio processing — vocal removal, noise reduction, format conversion.

## Why This Wins
- **AI-driven demand wave**: vocal removal exploding with AI music creation
- **"remove vocals from song free"** — high autocomplete demand
- **Podcaster/creator market**: noise removal for recordings
- **No dominant free client-side player**
- **Rust/WASM advantage**: ML inference + audio DSP at near-native speed

## Revenue Model
- **Primary**: Display ads ($8-12 RPM)
- **Secondary**: Premium features (batch processing, higher quality output)

## Tools to Build
1. Remove vocals from song (AI-powered, client-side)
2. Remove background noise
3. Audio format converter (MP3/WAV/OGG/FLAC/AAC)
4. MP3 cutter/trimmer
5. Audio compressor (reduce file size)
6. Change tempo/pitch
7. Audio to text (speech-to-text, client-side)
8. Merge audio files
9. Audio equalizer
10. Voice changer

## Programmatic SEO
- "remove vocals from [song name]" — though copyright issues
- "convert [format] to [format] free online"
- "mp3 cutter online free"
- "remove background noise from [recording/video/podcast]"
- "voice changer [girl/deep/robot/anime]"

## Autocomplete Signals (Confirmed Demand)
- "remove vocals from song free" / "ai" / "from audio"
- "noise removal online free" / "from video"
- "mp3 cutter online free"
- "audio to text free" / "ai"
- "voice changer online free" / "girl" / "live"

## Tech Stack
- Rust WASM for audio DSP (symphonia crate for decoding)
- ONNX Runtime WASM for ML models (vocal separation)
- Web Audio API for playback/preview
- Web Workers for processing
- Static hosting

## Challenges
- ML models for vocal separation are large (50-200MB)
- Quality of client-side vocal separation vs server-side (Demucs)
- Browser memory limits for long audio files
- ONNX Runtime WASM is still maturing
