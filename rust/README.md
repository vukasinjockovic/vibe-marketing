# Rust/WASM Tool Portfolio

Ad-monetized, client-side web tools built with Rust/WASM. Zero server costs, privacy-first positioning.

## Model
- **Inspiration**: Photopea ($2.8M/yr, 1 developer, $700/yr hosting, 100% client-side)
- **Monetization**: Display ads (Mediavine/Raptive at 50K sessions/mo) + freemium
- **Distribution**: Programmatic SEO (thousands of long-tail pages) + Reddit/HN seeding
- **Moat**: SEO + domain authority over time (not the code)

## Projects (Priority Order)

| # | Project | RPM | pSEO Scale | Status |
|---|---------|-----|-----------|--------|
| 1 | [resume-builder](./resume-builder/) | $30-50 | 5,000+ pages | Planning |
| 2 | [pdf-tools](./pdf-tools/) | $8-15 | 10,000+ pages | Planning |
| 3 | [construction-calculators](./construction-calculators/) | $25-40 | 10,000+ pages | Planning |
| 4 | [video-tools](./video-tools/) | $8-12 | 500+ pages | Planning |
| 5 | [3d-file-tools](./3d-file-tools/) | $10-15 | 200+ pages | Planning |
| 6 | [audio-tools](./audio-tools/) | $8-12 | 300+ pages | Planning |

## Shared Tech Stack
- **Core**: Rust compiled to WASM (wasm-pack + wasm-bindgen)
- **Frontend**: Minimal JS/TS shell (Leptos or vanilla)
- **Hosting**: Static files only (Cloudflare Pages / Vercel — free tier)
- **Key crates**: pdf-rs, image, symphonia, three-d, nalgebra

## Key Principle
Files never leave the browser. All processing is client-side WASM.
