# Resume Builder

Client-side resume builder with instant PDF generation via Rust/WASM.

## Why This Wins
- **Privacy**: "Your resume never leaves your browser" — address, phone, work history stays local
- **Truly free PDF export**: Competitors (resume.io, Zety) charge $25/mo for PDF. We do it client-side for $0
- **Instant**: Rust generates PDFs in ~35ms (vs server round-trip of 2-5 seconds)
- **No signup required**: Biggest frustration signal in autocomplete

## Revenue Model
- **Primary**: Display ads ($30-50 RPM — career/employment niche is top-tier)
- **Secondary**: Premium templates ($10-25/mo subscription)
- **Bridge**: Same WASM PDF engine as pdf-tools project

## Programmatic SEO
"[job title] resume template free" × thousands of job titles:
- software engineer resume template
- nurse resume template
- teacher resume template
- project manager resume template
- graphic designer resume template
- ... (5,000+ variations)

Each job title gets its own landing page with a pre-filled template preview.

## Autocomplete Signals (Confirmed Demand)
- "resume builder free" → free download, free online, free ai, **free reddit**
- "resume builder free reddit" — people searching Reddit for alternatives = frustration

## Competitors
| Site | Model | Weakness |
|------|-------|----------|
| resume.io | Freemium ($25/mo for PDF) | Charges for basic feature |
| Canva | Freemium | Bloated, not resume-focused |
| Zety | Paywall after building | Bait-and-switch UX |
| NovoResume | Freemium | Limited free templates |

## Tech Stack
- Rust WASM for PDF generation (typst or printpdf crate)
- Minimal frontend (form → JSON → WASM → PDF blob → download)
- Template system: JSON schema per job category
- Static hosting (Cloudflare Pages)

## Open Questions
- Template design: need 20-30 polished templates at launch
- ATS compatibility: generated PDFs must pass ATS parsers
- How to handle multi-page resumes in WASM
