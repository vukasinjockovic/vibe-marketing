# Research Report: Image Generation Services — Ideogram & DALL-E/OpenAI (Feb 2026)
Generated: 2026-02-11

## Summary

Ideogram remains at version 3.0 (with incremental upgrades) and now HAS an MCP server. OpenAI has deprecated DALL-E 3 (shutdown May 12, 2026) and replaced it with the GPT Image model family (gpt-image-1, gpt-image-1.5). The registry entry for "DALL-E 3" is now outdated and should be updated to reference gpt-image-1.5 as the current OpenAI image model. Pricing has shifted significantly for both services, and both now have viable MCP integrations.

---

## Questions Answered

### Q1: Ideogram — Latest Version?
**Answer:** Still Ideogram 3.0. Released March 26, 2025, with a "major upgrade" in early 2026 adding enhanced realism, improved prompt following, greater diversity, and Magic Fill/Extend in Canvas. No 3.5 or 4.0 has been announced. The registry's "Ideogram 3.0" designation is still correct.
**Source:** https://ideogram.ai/features/3.0, https://x.com/ideogram_ai/status/1917985285679530232
**Confidence:** High

### Q2: Ideogram — Current Pricing?
**Answer:** Plans have changed from what's in the registry ($7-20/mo):
- **Free:** 10 slow credits/day, public only
- **Basic:** $8/mo (was $7) — 400 priority credits/mo + 100 slow/day
- **Plus:** $20/mo — 1,000 priority credits/mo + unlimited slow
- **Pro:** $60/mo (NEW tier) — 3,000 priority credits/mo + unlimited slow + batch generation
- **Team:** $20/user/mo
- **Top-up packs:** $4 each (100-250 credits depending on plan)
**Source:** https://ideogram.ai/pricing, https://docs.ideogram.ai/plans-and-pricing/available-plans
**Confidence:** High

### Q3: Ideogram — API Availability and Per-Image Pricing?
**Answer:** Ideogram has a fully available API with endpoints for Generate, Edit, Remix, Upscale, and Describe. Per-image pricing is approximately:
- Ideogram 2a model: ~$0.04/image (~$0.025 for 2a turbo)
- Ideogram V3 via third-party providers (Replicate, fal.ai): from ~$0.05/image
- Direct API: flat fee per output image (exact V3 rate not publicly documented — requires API signup to see)
**Source:** https://ideogram.ai/features/api-pricing, https://docs.ideogram.ai/plans-and-pricing/ideogram-api
**Confidence:** Medium (V3 direct API rate not published transparently)

### Q4: Ideogram — Still Best for Text-in-Image?
**Answer:** Yes, still the leader for typography/text-in-image. V3.0 improved text rendering further with multi-language support (Chinese, Arabic, non-Latin scripts). However, OpenAI's GPT Image models have significantly closed the gap — GPT-4o image generation "excels at accurately rendering text" and can handle 10-20 objects with text. Ideogram still leads for complex typographic designs, but the gap has narrowed.
**Source:** https://openai.com/index/introducing-4o-image-generation/, https://tech-now.io/en/blogs/ideogram-3-0-review-2025-the-ultimate-ai-image-generator-for-text-style-control
**Confidence:** High

### Q5: Ideogram — MCP Server Available?
**Answer:** YES — this is a significant change from "No MCP" in the registry. Multiple MCP implementations exist:
- **Primary:** `@sunwood-ai-labs/ideagram-mcp-server` (npm package, TypeScript, Ideogram V3 compatible)
  - Features: generate, style reference, magic prompt, aspect ratio, model selection, blur mask
  - Install: `npx @sunwood-ai-labs/ideagram-mcp-server`
  - Last released: May 2025, actively maintained
- **Alternative:** `flowluap/ideogram-mcp-server` (GitHub)
- **Alternative:** `PierrunoYT/replicate-ideogram-v3-mcp-server` (via Replicate)
**Source:** https://github.com/Sunwood-ai-labs/ideagram-mcp-server, https://glama.ai/mcp/servers/@Sunwood-ai-labs/ideagram-mcp-server
**Confidence:** High

### Q6: DALL-E / OpenAI — Latest Version?
**Answer:** DALL-E 3 is DEPRECATED (shutdown date: May 12, 2026). OpenAI has replaced it with the GPT Image model family:
- **gpt-image-1** — First generation GPT Image model (launched April 2025)
- **gpt-image-1.5** — Current latest (launched late 2025), 4x faster, 20% cheaper, better instruction following
- **gpt-image-1-mini** — Budget option for high-volume
- **chatgpt-image-latest** — Points to latest in ChatGPT
There is NO "DALL-E 4". The branding has shifted entirely to "GPT Image".
**Source:** https://platform.openai.com/docs/models/gpt-image-1.5, https://openai.com/index/image-generation-api/
**Confidence:** High

### Q7: OpenAI Image — Current Pricing?
**Answer:** Token-based pricing (replaces flat per-image):
| Model | Text Input | Image Input | Image Output | ~Cost per 1024x1024 (low/med/high) |
|-------|-----------|-------------|-------------|-------------------------------------|
| gpt-image-1 | $5/1M tokens | $10/1M tokens | $40/1M tokens | ~$0.011 / $0.04 / $0.17 |
| gpt-image-1.5 | (unclear exact) | $8/1M tokens | $32/1M tokens | ~$0.009 / $0.04 / $0.13 |
| gpt-image-1-mini | — | — | — | ~$0.005-$0.05 |

Registry had "$0.04-0.08/img" for DALL-E 3. New pricing is $0.009-$0.17 depending on quality tier, with most production use at medium quality (~$0.04) being comparable.
**Source:** https://platform.openai.com/docs/pricing, https://costgoat.com/pricing/openai-images
**Confidence:** High

### Q8: OpenAI Image — MCP Server?
**Answer:** `spartanz51/imagegen-mcp` now supports gpt-image-1 and gpt-image-1.5 (not just DALL-E 3), so it's still viable but there are now BETTER options:
- **`SureScaleAI/openai-gpt-image-mcp`** — Purpose-built for GPT Image models, supports create-image + edit-image (inpainting/outpainting/compositing), file output to disk, up to 10 images at once
- **`spartanz51/imagegen-mcp`** — Still works, supports gpt-image-1/1.5, text-to-image + image-to-image with mask
- **`PierrunoYT/gpt-image-1-mcp-server`** — Focused on gpt-image-1
- No OFFICIAL OpenAI MCP server exists, but OpenAI's Responses API natively supports MCP protocol for remote servers
**Source:** https://github.com/SureScaleAI/openai-gpt-image-mcp, https://github.com/spartanz51/imagegen-mcp
**Confidence:** High

### Q9: OpenAI Image — New Capabilities?
**Answer:** Massive capability upgrade over DALL-E 3:
- **Inpainting:** Mask-based editing (paint over areas to change)
- **Outpainting/Extend:** Expand images beyond borders
- **Compositing:** Multiple input images combined
- **Multi-turn editing:** Iterative refinement with conversation context
- **Streaming previews:** Watch image generate in real-time via API
- **Instruction-aware editing:** "Change X but keep Y" with high fidelity
- **Text rendering:** Dramatically improved (10-20 objects with text)
- **Image-to-image:** Transform uploaded images
**Source:** https://platform.openai.com/docs/guides/image-generation, https://openai.com/index/introducing-4o-image-generation/
**Confidence:** High

### Q10: OpenAI Image — Resolution Options?
**Answer:** gpt-image-1.5 supports: 1024x1024, 1024x1536, 1536x1024 (same as DALL-E 3). Three quality tiers: low, medium, high. No change in actual resolution options.
**Source:** https://platform.openai.com/docs/models/gpt-image-1.5
**Confidence:** High

### Q11: Ideogram Acquired?
**Answer:** No. Ideogram remains an independent private company, headquartered in Toronto, Canada (founded 2022). Raised $96.5M total ($80M Series A from a16z + Index Ventures, Feb 2024). Hit $7M revenue as of September 2025 with ~50 employees.
**Source:** https://pitchbook.com/profiles/company/534515-68, https://getlatka.com/companies/ideogram.ai
**Confidence:** High

---

## Comparison: Registry (CURRENT) vs Reality (VERIFIED)

### Ideogram

| Field | Registry Has | Verified Current | Action Needed |
|-------|-------------|-----------------|---------------|
| Version | Ideogram 3.0 | Ideogram 3.0 (with 2026 upgrade) | No change (still 3.0) |
| Cost | $7-20/mo | $8-60/mo (Basic $8, Plus $20, Pro $60) | UPDATE: pricing has shifted |
| API per-image | Not listed | ~$0.04-0.05/img | ADD: API pricing |
| Free Tier? | No | Free plan exists (10 slow/day, public) | UPDATE: limited free tier exists |
| MCP? | No | YES: `@sunwood-ai-labs/ideagram-mcp-server` | UPDATE: MCP now available |
| Integration | Script | Both (Script + MCP) | UPDATE |
| Install Method | HTTP API (no install) | `npx @sunwood-ai-labs/ideagram-mcp-server` (MCP) or HTTP API | UPDATE |
| Best For | Text-in-images, infographics, social graphics | Same + multi-language text, style references | Minor update |

### DALL-E / OpenAI Image

| Field | Registry Has | Verified Current | Action Needed |
|-------|-------------|-----------------|---------------|
| Model name | DALL-E 3 | **gpt-image-1.5** (DALL-E 3 deprecated May 2026) | CRITICAL UPDATE |
| Cost | $0.04-0.08/img | $0.009-0.17/img (quality-tiered) | UPDATE: more granular pricing |
| MCP | `spartanz51/imagegen-mcp` | Same + `SureScaleAI/openai-gpt-image-mcp` (better) | UPDATE: recommend SureScaleAI |
| Capabilities | General purpose | General purpose + inpainting + outpainting + multi-turn editing + streaming + text rendering | UPDATE: major capability expansion |
| Resolution | (not listed) | 1024x1024, 1024x1536, 1536x1024 | ADD |
| Best For | General purpose | General purpose, editing, text-in-image (improved), multi-turn refinement | UPDATE |

---

## Recommended Registry Updates

### Line 279 (Ideogram entry) — REPLACE WITH:
```
| 3 | **Ideogram 3.0** | API: ~$0.04-0.05/img; Plans: $8-60/mo | Yes (10 slow/day, public) | No | Both | Community (`@sunwood-ai-labs/ideagram-mcp-server` npm) | `npx @sunwood-ai-labs/ideagram-mcp-server` | Text-in-images, infographics, multi-language text, social graphics |
```

### Line 280 (DALL-E entry) — REPLACE WITH:
```
| 4 | **GPT Image 1.5** (OpenAI) | $0.009-0.17/img (low/med/high quality) | No | No | Both | Community (`SureScaleAI/openai-gpt-image-mcp`) | `npm install openai-gpt-image-mcp` | General purpose, editing/inpainting, text rendering |
```

### Line 287 (Recommendation) — UPDATE TO:
```
**Recommendation:** FLUX Pro (via fal.ai MCP) as primary -- best quality/cost ratio. FLUX Schnell for drafts. Ideogram 3.0 for text-heavy designs and infographics (now with MCP). GPT Image 1.5 for general purpose + editing/inpainting workflows (replaces DALL-E 3, deprecated May 2026). Google Imagen 4 for photorealistic shots. Midjourney/Leonardo only for specialized brand work.
```

### API Keys line 290 — No change needed (IDEOGRAM_API_KEY and OPENAI_API_KEY still correct)

### .mcp.json — ADD new entries:
```json
{
  "ideogram": {
    "command": "npx",
    "args": ["-y", "@sunwood-ai-labs/ideagram-mcp-server"],
    "env": {
      "IDEOGRAM_API_KEY": "${IDEOGRAM_API_KEY}"
    }
  }
}
```
(OpenAI MCP: `spartanz51/imagegen-mcp` already in .mcp.json, but consider switching to `SureScaleAI/openai-gpt-image-mcp` for gpt-image-1.5 native support)

---

## Open Questions

- Ideogram V3 direct API per-image rate is not transparently published (requires signup to see exact rate). The ~$0.04-0.05 figure comes from third-party providers and older model pricing.
- Whether `@sunwood-ai-labs/ideagram-mcp-server` supports all V3 endpoints (Magic Fill, Extend) or only Generate. The README mentions generate + style reference but Canvas-exclusive features may not be available.
- OpenAI's exact token-to-cost mapping for gpt-image-1.5 at non-square resolutions needs verification from their pricing page.

---

## Sources

1. [Ideogram 3.0 Features](https://ideogram.ai/features/3.0) — Official V3 feature page
2. [Ideogram Pricing](https://ideogram.ai/pricing) — Current subscription plans
3. [Ideogram API Pricing](https://ideogram.ai/features/api-pricing) — API cost structure
4. [Ideogram API Docs](https://docs.ideogram.ai/plans-and-pricing/ideogram-api) — API plans and pricing docs
5. [Ideogram Available Plans](https://docs.ideogram.ai/plans-and-pricing/available-plans) — Plan details
6. [Ideogram 3.0 2026 Upgrade (X post)](https://x.com/ideogram_ai/status/1917985285679530232) — Enhanced realism update
7. [Introducing 4o Image Generation (OpenAI)](https://openai.com/index/introducing-4o-image-generation/) — GPT-4o native image gen
8. [OpenAI Image Generation API](https://openai.com/index/image-generation-api/) — gpt-image-1 launch
9. [GPT Image 1.5 Model (OpenAI)](https://platform.openai.com/docs/models/gpt-image-1.5) — Latest model docs
10. [OpenAI API Pricing](https://platform.openai.com/docs/pricing) — Current pricing
11. [OpenAI Image Generation Guide](https://platform.openai.com/docs/guides/image-generation) — API guide with capabilities
12. [OpenAI Deprecations](https://platform.openai.com/docs/deprecations) — DALL-E 3 deprecation notice
13. [Sunwood-ai-labs ideagram-mcp-server (GitHub)](https://github.com/Sunwood-ai-labs/ideagram-mcp-server) — Ideogram MCP
14. [SureScaleAI openai-gpt-image-mcp (GitHub)](https://github.com/SureScaleAI/openai-gpt-image-mcp) — OpenAI GPT Image MCP
15. [spartanz51/imagegen-mcp (GitHub)](https://github.com/spartanz51/imagegen-mcp) — Original OpenAI image MCP
16. [OpenAI DALL-E & GPT Image Pricing Calculator](https://costgoat.com/pricing/openai-images) — Feb 2026 pricing calculator
17. [Ideogram Wikipedia](https://en.wikipedia.org/wiki/Ideogram_(text-to-image_model)) — Company info
18. [Ideogram Funding (PitchBook)](https://pitchbook.com/profiles/company/534515-68) — $96.5M total funding
