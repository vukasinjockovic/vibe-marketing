# PDF Tools

Privacy-first PDF suite. Everything iLovePDF does, but files never leave your browser.

## Why This Wins
- **iLovePDF gets 283M visits/mo** — proves absurd demand
- **Privacy differentiation**: iLovePDF uploads everything to their servers. We process 100% client-side.
- **Zero server costs**: iLovePDF burns compute for every operation. We burn $0.
- **GDPR/HIPAA angle**: Lawyers, doctors, accountants who CAN'T upload client documents to random servers

## Revenue Model (Photopea Model — NOT iLovePDF Model)
- **Everything is free**. No file limits. No daily caps. No signup. No upload.
- **Primary revenue**: Display ads (Mediavine/Raptive). More usage = more pageviews = more ad revenue.
- **Soft throttle**: Interstitial ads between operations for heavy usage (50+ files/session). Not a paywall — just more ads.
- **Premium tier**: "Remove ads" for $3-5/mo. No feature gates. Just ad-free experience.
- **Why this beats iLovePDF**: They throttle free users (fewer pageviews = less ad revenue). We encourage unlimited usage (more pageviews = more ad revenue). Client-side = $0 server costs regardless of usage.
- **Cost**: ~$0/mo (static file hosting only)

## Tools to Build (each = separate landing page)
1. Merge PDF
2. Split PDF
3. Compress PDF
4. PDF to Word
5. PDF to JPG/PNG
6. Word to PDF
7. Excel to PDF
8. Image to PDF
9. Rotate PDF
10. Add watermark
11. Remove password
12. Add page numbers
13. PDF to text (OCR — harder client-side)
14. Sign PDF
15. Redact PDF

## Programmatic SEO
Each tool × modifiers × formats = thousands of pages:
- "compress pdf to [100kb/200kb/500kb/1mb] online free no upload"
- "merge pdf files [2/3/4/5/10] online free"
- "convert [format] to [format] free no signup"
- "pdf editor free no sign up"
- "compress pdf without uploading"

## Autocomplete Signals (Confirmed Demand)
- "compress pdf no upload" — privacy demand confirmed
- "pdf editor free no sign up" — signup friction
- "pdf editor online free no sign up" — double confirmation
- "pdf merge no upload" — privacy for merge too

## Competitors
| Site | Monthly Visits | Weakness |
|------|---------------|----------|
| ilovepdf.com | 283M | Uploads to server, freemium limits |
| smallpdf.com | 50M | Uploads to server, paywall |
| sejda.com | 16M | Uploads to server |
| pdf2go.com | 7M | Uploads to server |

ALL competitors upload files. NONE are client-side. That's the gap.

## Tech Stack
- Rust WASM (pdf-rs, lopdf, or pdfium-render compiled to WASM)
- Web Workers for heavy operations (don't block UI)
- Drag-and-drop file handling (File API)
- Static hosting (Cloudflare Pages)

## Prior Art
- LocalPDF (localpdf.online) — exists but tiny (~12K users total)
- CleanPDF (cleanpdf.net) — marketing privacy angle
- Google's pdf.js — viewer only, not editor

## Open Questions
- PDF rendering fidelity (complex PDFs with fonts/images)
- OCR client-side feasibility (tesseract.js exists but slow)
- Max file size in browser memory (~2GB limit)
