# Research Report: FLUX Image Generation Models & fal.ai (February 2026)
Generated: 2026-02-11

## Summary

The FLUX ecosystem has undergone a major generational shift. Black Forest Labs released **FLUX.2** (November 2025) with Pro, Flex, Dev, and Klein variants, superseding the FLUX.1 series. fal.ai has additionally released a **FLUX.2 [dev] Turbo** distilled model (January 2026) that is 10x cheaper than FLUX.2 Pro. The registry's current entries referencing "FLUX Pro" and "FLUX Schnell" at old pricing are now outdated and should be updated to reflect the FLUX.2 lineup.

---

## Questions Answered

### Q1: What is the latest version of FLUX Pro?
**Answer:** FLUX.2 [pro] — released November 25, 2025, by Black Forest Labs. The fal.ai endpoint is `fal-ai/flux-2-pro`. This supersedes FLUX.1 Pro and FLUX1.1 Pro.
**Source:** https://fal.ai/models/fal-ai/flux-2-pro
**Confidence:** High

### Q2: Is $0.05-0.10/img still accurate for FLUX Pro?
**Answer:** NO. FLUX.2 [pro] on fal.ai costs **$0.03 per megapixel**. A standard 1024x1024 image (1MP) costs $0.03. A 1920x1080 image costs $0.045. The old registry price of "$0.05-0.10/img" is outdated — it's now cheaper.
**Source:** https://fal.ai/models/fal-ai/flux-2-pro, https://fal.ai/pricing
**Confidence:** High

### Q3: What is the latest version of FLUX Schnell? Still $0.003/img?
**Answer:** FLUX Schnell (FLUX.1 generation) has been effectively replaced by two options:
- **FLUX.2 [dev] Turbo** (fal.ai distilled) — $0.008/MP (~$0.008 for 1024x1024). This is the new "fast cheap" option.
- **FLUX.2 [klein]** (BFL official, Jan 15, 2026) — 4B and 9B parameter models for real-time generation. Sub-second inference.

The old FLUX.1 Schnell endpoint likely still works on fal.ai but is no longer the recommended fast/cheap option.
**Source:** https://venturebeat.com/technology/new-years-ai-surprise-fal-releases-its-own-version-of-flux-2-image-generator, https://fal.ai/learn/biz/flux-2-turbo-vs-flux-2-which-model-should-you-choose
**Confidence:** High

### Q4: Does FLUX Dev still exist? Is it relevant?
**Answer:** Yes, reborn as **FLUX.2 [dev]** — a 32B open-weight model at $0.012/MP on fal.ai. It's the open-weight workhorse: supports LoRA, image editing, and multi-reference editing. Commercially licensed. Very relevant as the customizable mid-tier option.
**Source:** https://fal.ai/models/fal-ai/flux-2
**Confidence:** High

### Q5: Any new FLUX models released since mid-2025?
**Answer:** Yes, significant releases:

| Model | Release | Key Feature |
|-------|---------|-------------|
| **FLUX.1 Kontext** (pro/max/dev) | May 29, 2025 | In-context image editing with text+image input. Character consistency. |
| **FLUX.1 Krea Dev** | July 31, 2025 | BFL + Krea AI collab, better aesthetics/realism |
| **FLUX.2 [pro]** | Nov 25, 2025 | Zero-config, production-grade, best quality |
| **FLUX.2 [flex]** | Nov 25, 2025 | Adjustable steps/guidance, typography, $0.06/MP |
| **FLUX.2 [dev]** | Nov 25, 2025 | 32B open-weight, LoRA, editing, $0.012/MP |
| **FLUX.2 [klein] 4B/9B** | Jan 15, 2026 | Apache 2.0 (4B), real-time, sub-second |
| **FLUX.2 [dev] Turbo** | Jan 2026 | fal.ai distilled, 8-step, $0.008/MP, highest open-weight ELO |

**Source:** https://bfl.ai/, https://fal.ai/flux-2, https://en.wikipedia.org/wiki/Flux_(text-to-image_model)
**Confidence:** High

### Q6: Is `mcp-fal-ai-image` still the correct MCP server?
**Answer:** It still works but there is now a better alternative: **`fal-ai-mcp-server`** (npm, version 2.1.2). This newer package provides:
- Platform API v1 support
- Universal model discovery (search all 600+ fal.ai models)
- Pricing information built in
- File upload to fal.ai CDN
- Works with ALL fal.ai models (FLUX.2, Kontext, Ideogram, etc.), not just image generation

The `mcp-fal-ai-image` package is more limited — it generates images but lacks model discovery and the broader Platform API features.

There is no "official" fal.ai MCP server from fal.ai themselves; both are community packages.
**Source:** https://libraries.io/npm/fal-ai-mcp-server, https://www.npmjs.com/package/mcp-fal-ai-image
**Confidence:** Medium (community packages, not official fal.ai releases)

### Q7: fal.ai pricing changes since 2025?
**Answer:** fal.ai has moved to a **per-megapixel** pricing model (not flat per-image). Key current prices:

| Model | Price/MP | 1024x1024 Cost | Notes |
|-------|----------|----------------|-------|
| FLUX.2 [pro] | $0.030 | $0.030 | Best quality, zero-config |
| FLUX.2 [flex] | $0.060 | $0.060 | Adjustable params, typography |
| FLUX.2 [dev] | $0.012 | $0.012 | Open-weight, LoRA support |
| FLUX.2 [dev] Turbo | $0.008 | $0.008 | Fastest, cheapest quality option |
| FLUX1.1 [pro] (legacy) | $0.040 | $0.040 | Still available but superseded |
| FLUX.2 LoRA Realism | $0.021 | $0.021 | Specialized realism LoRA |

**Source:** https://fal.ai/pricing, https://docs.fal.ai/platform-apis/v1/models/pricing
**Confidence:** High

---

## Registry Comparison: CURRENT vs NEEDED

### image_generation Capability — What We Have vs What's Current

| Field | CURRENT (Registry) | SHOULD BE (Updated) |
|-------|-------------------|---------------------|
| **Priority 1 Name** | FLUX Pro (via fal.ai) | **FLUX.2 [pro]** (via fal.ai) |
| **Priority 1 Cost** | $0.05-0.10/img | **$0.03/MP** ($0.03 for 1024x1024) |
| **Priority 1 Best For** | Hero images, product shots | Hero images, product shots (unchanged) |
| **Priority 2 Name** | FLUX Schnell (via fal.ai) | **FLUX.2 [dev] Turbo** (via fal.ai) |
| **Priority 2 Cost** | $0.003/img | **$0.008/MP** ($0.008 for 1024x1024) |
| **Priority 2 Best For** | Quick drafts, thumbnails | Quick drafts, thumbnails, batch generation |
| **MCP Server** | `mcp-fal-ai-image` npm | **`fal-ai-mcp-server`** npm (v2.1.2) — universal model access |

### New Models to ADD to Registry

| Priority | Model | Cost/MP | fal.ai Endpoint | Best For |
|----------|-------|---------|-----------------|----------|
| NEW (3) | **FLUX.2 [dev]** | $0.012 | `fal-ai/flux-2` | LoRA fine-tuning, custom styles, editing |
| NEW (4) | **FLUX.2 [flex]** | $0.060 | `fal-ai/flux-2-flex` | Text-in-images, logos, controllable generation |
| NEW (5) | **FLUX.1 Kontext [pro]** | TBD | `fal-ai/flux-pro/kontext` | In-context editing, character consistency |

### MCP Config Update (.mcp.json)

Current:
```json
"fal-ai": {
  "command": "npx",
  "args": ["-y", "mcp-fal-ai-image"],
  "env": { "FAL_KEY": "${FAL_KEY}" }
}
```

Recommended:
```json
"fal-ai": {
  "command": "npx",
  "args": ["-y", "fal-ai-mcp-server"],
  "env": { "FAL_KEY": "${FAL_KEY}" }
}
```

### Free Minimum Path Update

Current:
> vibe-image-generator: FLUX Schnell via fal.ai ($0.003/img, near-free)

Should be:
> vibe-image-generator: FLUX.2 [dev] Turbo via fal.ai ($0.008/img, near-free) — ~$2.40/mo for 300 images

### Growth Tier Update

Current:
> Images: FLUX Pro (fal.ai) ~$5-10/mo

Should be:
> Images: FLUX.2 [pro] (fal.ai) ~$3-9/mo (cheaper per image, $0.03/img at 1MP)

---

## Complete FLUX.2 Model Lineup (February 2026)

### Black Forest Labs Official Models

| Model | Params | License | Available On | Key Differentiator |
|-------|--------|---------|-------------|-------------------|
| FLUX.2 [pro] | Proprietary | API only | fal.ai, Together AI, BFL API | Highest quality, zero-config |
| FLUX.2 [flex] | Proprietary | API only | fal.ai, BFL API | Adjustable steps/guidance, typography |
| FLUX.2 [dev] | 32B | Non-commercial | fal.ai, HuggingFace, local | Open-weight, LoRA, editing |
| FLUX.2 [klein] 4B | 4B | Apache 2.0 | HuggingFace, local | Real-time, fully open, commercial OK |
| FLUX.2 [klein] 9B | 9B | Non-commercial | HuggingFace, local | Higher quality real-time |

### fal.ai Exclusive Models

| Model | Based On | Key Feature | Price/MP |
|-------|----------|-------------|----------|
| FLUX.2 [dev] Turbo | FLUX.2 [dev] distilled | 8-step, fastest, highest open ELO | $0.008 |
| FLUX.2 LoRA Realism | FLUX.2 + LoRA | Photorealistic fine-tune | $0.021 |

### Still Available (Legacy FLUX.1)

| Model | Status | Notes |
|-------|--------|-------|
| FLUX.1 Pro | Available | Superseded by FLUX.2 [pro] |
| FLUX1.1 Pro | Available ($0.04/MP) | Superseded by FLUX.2 [pro] |
| FLUX.1 Schnell | Available | Superseded by FLUX.2 Turbo |
| FLUX.1 Dev | Available | Superseded by FLUX.2 [dev] |
| FLUX.1 Kontext (pro/max/dev) | Active | Still the editing model — no FLUX.2 Kontext yet |

---

## Recommendations

### For This Codebase (vibe-marketing registry)

1. **Update FLUX Pro to FLUX.2 [pro]** — better quality AND cheaper ($0.03 vs $0.05-0.10)
2. **Replace FLUX Schnell with FLUX.2 [dev] Turbo** — slightly more expensive ($0.008 vs $0.003) but massively better quality, and it's the recommended fast option now
3. **Add FLUX.2 [dev] as a mid-tier option** — $0.012/MP, supports LoRA customization for brand-consistent imagery
4. **Switch MCP server from `mcp-fal-ai-image` to `fal-ai-mcp-server`** — universal model access, pricing info, future-proof
5. **Consider adding FLUX.1 Kontext** — for image editing workflows (e.g., vibe-image-generator doing iterative edits on hero images)
6. **Update all pricing references** from flat per-image to per-megapixel

### Implementation Notes
- fal.ai pricing is per-megapixel, not per-image. For standard 1024x1024 (1MP), price = price/MP. For larger images, multiply by ceil(MP).
- The `fal-ai-mcp-server` v2.1.2 package name is different from the old `mcp-fal-ai-image` — it uses a different tool interface (model discovery + generation vs just generation)
- FLUX.2 [klein] 4B (Apache 2.0) could theoretically be self-hosted for $0/image on a GPU server, but requires an RTX GPU with decent VRAM
- FLUX.1 Kontext has no FLUX.2 equivalent yet — it remains the latest for context-aware editing

---

## Sources

1. [fal.ai FLUX.2 Pro model page](https://fal.ai/models/fal-ai/flux-2-pro) - Pricing, features, API docs
2. [fal.ai FLUX API landing page](https://fal.ai/flux) - All FLUX models on fal.ai
3. [fal.ai FLUX.2 landing page](https://fal.ai/flux-2) - FLUX.2 specific models
4. [fal.ai Pricing](https://fal.ai/pricing) - Current per-megapixel pricing
5. [fal.ai FLUX.2 Dev model page](https://fal.ai/models/fal-ai/flux-2) - Dev model specs
6. [VentureBeat: Fal releases Flux 2 Turbo](https://venturebeat.com/technology/new-years-ai-surprise-fal-releases-its-own-version-of-flux-2-image-generator) - Turbo announcement
7. [fal.ai Flux 2 Turbo vs Flux 2 comparison](https://fal.ai/learn/biz/flux-2-turbo-vs-flux-2-which-model-should-you-choose) - Turbo vs standard
8. [Black Forest Labs models page](https://bfl.ai/models) - Official BFL model list
9. [BFL FLUX.2 Klein announcement](https://bfl.ai/blog/flux2-klein-towards-interactive-visual-intelligence) - Klein model details
10. [NVIDIA blog: FLUX.2 on RTX](https://blogs.nvidia.com/blog/rtx-ai-garage-flux-2-comfyui/) - FLUX.2 release context
11. [fal.ai FLUX.1 Kontext](https://fal.ai/flux-kontext) - Kontext editing model
12. [fal-ai-mcp-server on npm](https://libraries.io/npm/fal-ai-mcp-server) - MCP server v2.1.2
13. [mcp-fal-ai-image on npm](https://www.npmjs.com/package/mcp-fal-ai-image) - Legacy MCP package
14. [Flux Wikipedia](https://en.wikipedia.org/wiki/Flux_(text-to-image_model)) - Model timeline
15. [AI CERTs: Fal.ai Flux 2 Turbo](https://www.aicerts.ai/news/fal-ai-flux-2-turbo-slashes-image-generation-costs/) - Turbo cost analysis

## Open Questions

- Exact pricing for FLUX.1 Kontext [pro] and [max] on fal.ai (not found in search results)
- Whether fal.ai plans an official MCP server (currently all are community)
- Whether FLUX.2 Kontext is in development (no announcements found)
- FLUX.2 [klein] pricing on fal.ai specifically (may need to check fal.ai directly)
