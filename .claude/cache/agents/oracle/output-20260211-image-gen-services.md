# Research Report: Image Generation Services — Current State (February 2026)
Generated: 2026-02-11

## Summary

The image generation API landscape has shifted significantly since our registry was last updated. Google Imagen 4 is REAL and now available beyond Vertex AI (via Gemini API). Replicate now has an OFFICIAL MCP server. Several major new services are missing from our registry entirely: GPT Image 1.5 (currently #1 ranked), Gemini 3 Pro Image (native multimodal), Flux 2 Pro (successor to Flux Pro), ByteDance Seedream 4.5/5.0, and Stability AI SD4. Our DALL-E 3 entry is outdated. Pricing data across the board needs updating.

---

## Part 1: Google Imagen — Answers

### Q1: Latest version? Is Imagen 4 real?
**Answer:** YES, Imagen 4 is real and shipping. Released May 20, 2025 at Google I/O 2025.
**Confidence:** HIGH (VERIFIED from Google official docs and blog)

Three variants exist:
| Variant | Price/Image | Best For |
|---------|-------------|----------|
| Imagen 4 Fast | $0.02 | Rapid generation, high-volume, drafts |
| Imagen 4 (Standard) | $0.04 | General purpose |
| Imagen 4 Ultra | $0.06 | Highest quality, up to 2K resolution |

Our registry listing of "Google Imagen 4" with "Vertex AI pricing" is directionally correct but incomplete on pricing.

### Q2: Current pricing on Vertex AI?
**Answer:** Updated pricing as of 2026:
- Imagen 4 Fast: **$0.02/image**
- Imagen 4 Standard: **$0.04/image**
- Imagen 4 Ultra: **$0.06/image**
- 4K resolution images (4096x4096): **$0.24/image** (2000 tokens)
- 1K/2K images: **$0.134/image** (1120 tokens) when billed by token

**Confidence:** HIGH
**Source:** [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing), [Imagen 4 Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate)

### Q3: MCP Status?
**Answer:** Our registry entry references `falahgs/imagen-3.0-generate-google-mcp-server` — this is OUTDATED (Imagen 3.0 era). However:
- Google announced **official MCP support for Google Cloud services** (Dec 2025), including MCP toolbox for Genmedia (Imagen + Veo). This is under public preview.
- The community `falahgs/imagen-3.0-generate-google-mcp-server` still exists but targets the older Imagen 3.0 model
- fal.ai route still works for accessing Imagen models

**ACTION NEEDED:** Update MCP reference. Watch for Google's official Genmedia MCP to go GA.

**Confidence:** MEDIUM (official MCP is preview, community one is stale)
**Source:** [Google MCP Announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)

### Q4: Quality for photorealistic faces — still best?
**Answer:** NO, not definitively the best anymore. The landscape has changed:
- Imagen 4 holds **#5 on Artificial Analysis Text-to-Image Leaderboard**
- **GPT Image 1.5 is currently #1** (LM Arena score 1264)
- Flux.1 Kontext and Recraft V3 also rank ahead of Imagen 4
- Multiple user reports of face quality issues with Imagen 4: "mangled faces, grainy textures" in some scenarios
- Still good at photorealism generally, but NO LONGER the undisputed leader for faces

**Our registry claim of "Photorealism, realistic faces" as Imagen's "Best For" needs nuancing.**

**Confidence:** HIGH
**Source:** [AllAboutAI Imagen 4 Review](https://www.allaboutai.com/ai-reviews/imagen/), [WaveSpeedAI Comparison](https://wavespeed.ai/blog/posts/best-ai-image-generators-2026/)

### Q5: Any new capabilities?
**Answer:** Yes, several since Imagen 3:
- **10x faster** generation with Fast mode
- **Better text rendering** (spelling accuracy, longer text strings, layout-sensitive)
- **Up to 4K resolution** (4096x4096)
- **Wider style range** (photorealism to abstract art, illustration, impressionism)
- **SynthID watermarking** built-in
- **Image editing** and **upscaling** (Imagen 4.0 Upscale Preview)

**Confidence:** HIGH
**Source:** [Kartaca Imagen 4 vs 3](https://kartaca.com/en/pushing-creative-boundaries-google-imagen-4-vs-imagen-3-in-real-world-use/)

### Q6: Availability — still Vertex AI only?
**Answer:** NO — major expansion. Imagen 4 is now available on:
1. **Vertex AI** (original channel)
2. **Gemini API** (GA as of August 15, 2025)
3. **Google AI Studio** (direct web UI access)
4. **Firebase AI Logic** (for mobile/web app integration)

This is a SIGNIFICANT change from our registry which implies Vertex-AI-only access.

**Confidence:** HIGH
**Source:** [Google Developers Blog - Imagen 4 in Gemini API](https://developers.googleblog.com/announcing-imagen-4-fast-and-imagen-4-family-generally-available-in-the-gemini-api/), [Imagen 4 in Gemini API and AI Studio](https://developers.googleblog.com/imagen-4-now-available-in-the-gemini-api-and-google-ai-studio/)

---

## Part 2: Replicate — Answers

### Q1: Current state of the platform?
**Answer:** Replicate remains a major multi-model inference platform. They host hundreds of image generation models including FLUX Pro, FLUX 2 Pro, Ideogram V3, Seedream 4.5, Recraft V3, and more. The platform has matured with official model designations and predictable per-image pricing for official models.

**Confidence:** HIGH
**Source:** [Replicate Official Models](https://replicate.com/docs/topics/models/official-models)

### Q2: Pricing model?
**Answer:** Still pay-as-you-go, but more nuanced now:
- **Official models**: Priced by predictable metrics (per image, per second of video, per token)
- **Community models**: Billed by compute time (per second on GPU)
- Typical image generation: **~$0.003-$0.055/image** depending on model
- Example: FLUX 2 Pro = ~$0.055/image, budget models = ~$0.003/image

Our registry's "Pay-per-use" is correct but should be more specific.

**Confidence:** HIGH
**Source:** [Replicate Pricing](https://replicate.com/pricing), [PricePerToken Comparison](https://pricepertoken.com/image)

### Q3: MCP Status?
**Answer:** MAJOR UPDATE — Replicate now has an **OFFICIAL MCP server**:
- **Hosted at:** `mcp.replicate.com` (remote MCP, runs on Cloudflare Workers)
- **Also available as:** public npm package for local running
- **OAuth-secured:** tokens stored in Cloudflare KV, never exposed to AI tools
- Works with Claude, Cursor, Codex, Gemini, VS Code

Our registry references `@gongrzhe/image-gen-server` — this is a community server and should be REPLACED or supplemented with the official one.

**Confidence:** HIGH
**Source:** [Replicate MCP Official](https://mcp.replicate.com/), [Replicate MCP Docs](https://replicate.com/docs/reference/mcp), [Replicate Blog Announcement](https://replicate.com/blog/remote-mcp-server)

### Q4: Most popular/best models on Replicate now?
**Answer:** Top image models on Replicate in Feb 2026:
1. **FLUX 2 Pro** (Black Forest Labs) — quality leader on the platform
2. **Ideogram V3** — best text rendering
3. **Recraft V3** — wide style range, long text, vector generation
4. **Seedream 4.5** (ByteDance) — excellent quality/price ratio
5. **FLUX Schnell** — fast/cheap drafts (still available)

**Confidence:** HIGH
**Source:** [Replicate Text-to-Image Collection](https://replicate.com/collections/text-to-image), [TeamDay Best Models 2026](https://www.teamday.ai/blog/best-ai-image-models-2026)

### Q5: Any official Replicate MCP?
**Answer:** YES — see Q3 above. Official hosted MCP at mcp.replicate.com.

---

## Part 3: NEW Services Missing from Registry

### 3A: GPT Image 1.5 (OpenAI) — SHOULD ADD, HIGH PRIORITY

**Status:** Released December 2025. Currently **#1 ranked** on LM Arena (score 1264).
**What it replaces:** Our DALL-E 3 entry (priority 4) is NOW OUTDATED.
**Pricing:**
| Quality | Price/Image (1024x1024) |
|---------|------------------------|
| Low | $0.01 |
| Medium | $0.04 |
| High | $0.17 |

**Key capabilities:**
- Best-in-class text rendering (typography, logos, signage)
- Superior instruction following
- Three resolutions: 1024x1024, 1024x1536, 1536x1024
- Available via OpenAI Images API (same `OPENAI_API_KEY`)

**MCP:** Existing community MCP servers for OpenAI image gen likely updated. Same API key as our existing DALL-E 3 integration.

**RECOMMENDATION:** Replace DALL-E 3 (priority 4) with GPT Image 1.5. Same API key, same vendor, strictly better model.

**Source:** [OpenAI GPT Image 1.5 Docs](https://platform.openai.com/docs/models/gpt-image-1.5), [OpenAI Pricing](https://platform.openai.com/docs/pricing)

### 3B: Gemini 3 Pro Image (Google) — SHOULD ADD

**Status:** Preview. Also called "Nano Banana Pro." Native multimodal model that generates images as part of text conversations.
**Pricing:** ~$0.134/image (1K/2K), uses token-based billing
**Key capabilities:**
- Native text+image output in single model call
- Advanced text rendering for infographics, menus, marketing
- **Google Search grounding** — can generate images based on real-time data
- "Thinking mode" for complex compositions
- 1K, 2K, 4K output

**Why it matters:** This is NOT a standalone image model — it's a multimodal LLM that generates images. Agents using Gemini for text tasks can get images in the same call. Unique capability.

**MCP:** Would use Google Gemini API MCP (separate from Imagen MCP)

**Source:** [Gemini 3 Pro Image Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image), [Google AI Developers](https://ai.google.dev/gemini-api/docs/image-generation)

### 3C: Flux 2 Pro (Black Forest Labs) — SHOULD UPDATE

**Status:** Flux 2 Pro is the successor to Flux Pro (which we have at priority 1).
**Pricing:**
- Via fal.ai: ~$0.03/image (1024x1024), $0.045 for 1920x1080
- Via Replicate: ~$0.055/image
- Via BFL direct API: similar range

**Key capabilities:**
- Successor to FLUX Pro with improved quality
- Zero-config text-to-image
- Image editing (FLUX 2 Dev Edit)
- Available on fal.ai, Replicate, BFL direct

**RECOMMENDATION:** Update our priority 1 entry from "FLUX Pro" to "FLUX 2 Pro" — same fal.ai integration path, just newer model.

**Source:** [fal.ai FLUX 2 Pro](https://fal.ai/models/fal-ai/flux-2-pro), [BFL Pricing](https://bfl.ai/pricing)

### 3D: ByteDance Seedream 4.5 / 5.0 — CONSIDER ADDING

**Status:** Seedream 5.0 launched early 2026. Available on Replicate, WaveSpeedAI, BytePlus.
**Pricing:** Very competitive (~$0.003/image on Replicate for Seedream 4)
**Key capabilities:**
- Real-time web search during generation (5.0)
- Excellent text rendering and dense text
- Multi-image editing with subject preservation
- 2K and 4K output
- Unified generation + editing architecture

**Why it matters:** Extremely cost-effective. Already on Replicate (so our Replicate integration covers it). Could be specifically called out as a budget option.

**Source:** [Seedream 5.0 on ByteDance](https://seed.bytedance.com/en/seedream4_5), [WaveSpeedAI Guide](https://wavespeed.ai/blog/posts/seedream-4-5-complete-guide-2026/)

### 3E: Stability AI / SD4 — CONSIDER ADDING

**Status:** SD4 and SDXL Turbo v2 exist. Stability AI has a developer platform at platform.stability.ai.
**Pricing:** Starts at $0.01/credit via their platform. Enterprise licensing for >$1M/year.
**Key capabilities:**
- Open-source heritage (self-hosting possible for older models)
- SD 3.5 Large fully open-weights
- SD4 available via API
- 3D and video capabilities expanding

**Why it matters:** Only option with truly open-source self-hosting path for image gen. Could serve as a fallback or for users wanting no cloud dependency.

**Source:** [Stability AI Platform](https://platform.stability.ai/pricing), [Stability AI](https://stability.ai/)

### 3F: Adobe Firefly API — PROBABLY SKIP

**Status:** Available but **enterprise-only**. Requires Adobe enterprise plan. Sales team contact required.
**Pricing:** Not publicly listed, enterprise negotiation only.
**Key capabilities:** Commercially safe (trained on licensed content), good for brand compliance.

**Why we should probably SKIP:** Enterprise-only gating makes it impractical for our target audience (indie/small business marketers). No self-serve API signup.

**Source:** [Adobe Firefly API Docs](https://developer.adobe.com/firefly-services/docs/firefly-api/)

### 3G: Amazon Titan Image Generator v2 — LOW PRIORITY

**Status:** Amazon Titan Image Generator G1 v2, available via Amazon Bedrock.
**Pricing:** Bedrock on-demand pricing (region-dependent).
**Key capabilities:** Image conditioning, color palette control, subject consistency, background removal, watermark detection.
**Availability:** US East and US West only.

**Why low priority:** Locked into AWS Bedrock ecosystem. Quality does not compete with top-tier models. Useful mainly for shops already deep in AWS.

**Source:** [Amazon Titan Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html)

---

## Part 4: WHAT WE HAVE vs WHAT'S CURRENT

### Registry Entries — Accuracy Audit

| # | Our Entry | Status | Action Needed |
|---|-----------|--------|---------------|
| 1 | FLUX Pro (via fal.ai) $0.05-0.10/img | OUTDATED | Update to **Flux 2 Pro**, price is now ~$0.03-0.055/img |
| 2 | FLUX Schnell (via fal.ai) $0.003/img | STILL CORRECT | Price still accurate, model still available |
| 3 | Ideogram 3.0 $7-20/mo | MOSTLY CORRECT | Ideogram V3 is current; API pricing is now per-image via credits, not just subscription |
| 4 | DALL-E 3 (OpenAI) $0.04-0.08/img | OUTDATED | Replace with **GPT Image 1.5** ($0.01-0.17/img) — same API key |
| 5 | Midjourney (via ImagineAPI) $10-30/mo | STILL CORRECT | Still no public API; ImagineAPI proxy route still valid |
| 6 | Leonardo.ai | STILL CORRECT | Still operational, niche use |
| 7 | Recraft V3 "API access" | NEEDS PRICING | Update to **$0.04/raster, $0.08/vector** per image |
| 8 | Google Imagen 4 "Vertex AI pricing" | NEEDS MAJOR UPDATE | Now $0.02-0.06/img (3 tiers), available on Gemini API + AI Studio (not just Vertex), MCP reference outdated |
| 9 | Replicate (multi-model) "Pay-per-use" | NEEDS MCP UPDATE | Official MCP at mcp.replicate.com replaces community `@gongrzhe/image-gen-server` |

### NEW Entries to Add

| Priority | Service | Cost | MCP? | Best For | Action |
|----------|---------|------|------|----------|--------|
| NEW (high) | **GPT Image 1.5** (OpenAI) | $0.01-0.17/img | Community (existing OpenAI MCPs) | Text rendering, highest overall quality (#1 ranked) | ADD — replace DALL-E 3 |
| NEW (medium) | **Gemini 3 Pro Image** | ~$0.134/img | Via Gemini API | Native multimodal image+text, search-grounded images | ADD — unique capability |
| NEW (low) | **Seedream 4.5/5.0** (ByteDance) | ~$0.003/img on Replicate | Via Replicate MCP | Budget option, good quality/price | CONSIDER — accessible via Replicate |
| NEW (low) | **Stability AI SD4** | $0.01+/credit | No official MCP | Self-hostable (older models), open-source ecosystem | CONSIDER — niche use |

---

## Part 5: Revised Priority Recommendation

Based on current 2026 landscape:

| Priority | Service | Cost/img | Best For | Why This Rank |
|----------|---------|----------|----------|---------------|
| 1 | **Flux 2 Pro** (via fal.ai) | $0.03-0.055 | Hero images, product shots, general high-quality | Best quality/cost, fast, great MCP support |
| 2 | **GPT Image 1.5** (OpenAI) | $0.04 (medium) | Text rendering, typography, logos, #1 overall quality | LM Arena #1, exceptional instruction following |
| 3 | **FLUX Schnell** (via fal.ai) | $0.003 | Quick drafts, thumbnails, bulk generation | Unbeatable for speed/cost |
| 4 | **Ideogram V3** | per-credit | Text-in-images, infographics, social graphics | Best text rendering specialist |
| 5 | **Google Imagen 4** (via Gemini API) | $0.02-0.06 | Photorealism, product photography, 4K output | Good photorealism, now accessible via Gemini API |
| 6 | **Recraft V3** | $0.04/$0.08 | Vector graphics, icons, SVG generation | Unique vector output capability |
| 7 | **Replicate** (multi-model) | varies | Access to any model (Seedream, etc.) | Official MCP, 600+ models, ultimate flexibility |
| 8 | **Gemini 3 Pro Image** | ~$0.134 | Multimodal text+image tasks, search-grounded visuals | Unique: generates images within LLM conversation |
| 9 | **Midjourney** (via ImagineAPI) | $10-30/mo | Artistic, brand imagery | Still strong for aesthetics, but no direct API |
| 10 | **Leonardo.ai** | $10+/mo | Character consistency | Niche use |

---

## Part 6: MCP Status Summary

| Service | Our Current MCP | Updated MCP Status |
|---------|----------------|-------------------|
| FLUX (fal.ai) | `mcp-fal-ai-image` npm | STILL VALID; also see fal.ai MCP servers from raveenb/Gravicity (600+ models) |
| DALL-E 3 / GPT Image 1.5 | `spartanz51/imagegen-mcp` | Should verify this supports GPT Image 1.5 endpoint; may need update |
| Google Imagen | `falahgs/imagen-3.0-generate-google-mcp-server` | OUTDATED (Imagen 3.0). Google official Genmedia MCP in preview. Watch for GA. |
| Replicate | `@gongrzhe/image-gen-server` npm | REPLACE with **official** `mcp.replicate.com` (hosted) or official npm package |
| Recraft V3 | None (Script only) | No official MCP found; fal.ai MCP can access Recraft V3 |
| Ideogram V3 | None (Script only) | No official MCP found |
| Gemini 3 Pro Image | N/A (not in registry) | Would use Google Gemini API; official Google MCP servers launching |

---

## Part 7: Key Pricing Changes

| Service | Our Listed Price | Actual Current Price | Delta |
|---------|-----------------|---------------------|-------|
| FLUX Pro/2 Pro (fal.ai) | $0.05-0.10/img | $0.03-0.055/img | CHEAPER |
| FLUX Schnell | $0.003/img | $0.003/img | Same |
| DALL-E 3 → GPT Image 1.5 | $0.04-0.08/img | $0.01-0.17/img (quality tiers) | Different model, wider range |
| Google Imagen 4 | "Vertex AI pricing" (vague) | $0.02-0.06/img (3 tiers) | Now specific |
| Recraft V3 | "API access" (vague) | $0.04 raster / $0.08 vector | Now specific |
| Replicate | "Pay-per-use" (vague) | $0.003-0.055/img depending on model | Now specific |

---

## Open Questions

1. **Google Genmedia MCP GA date?** — Currently in public preview. Could become the definitive Imagen MCP when it goes GA.
2. **Does the `spartanz51/imagegen-mcp` support GPT Image 1.5?** — Needs testing. If not, need a new community MCP or script wrapper.
3. **Flux 2 Pro vs Flux Pro on fal.ai** — Is Flux Pro still available or fully replaced? Need to verify the exact model IDs in the fal.ai MCP.
4. **Seedream 5.0 availability** — Just launched; API access may be limited. Monitor.
5. **Ideogram V3 per-image API pricing** — Credit system details unclear from public sources; may need to sign up to get exact $/image.

---

## Sources

1. [Google Imagen 4 Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate) — Official model documentation
2. [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) — Current pricing page
3. [Imagen 4 in Gemini API (Google Blog)](https://developers.googleblog.com/announcing-imagen-4-fast-and-imagen-4-family-generally-available-in-the-gemini-api/) — GA announcement
4. [Imagen 4 vs Imagen 3 (Kartaca)](https://kartaca.com/en/pushing-creative-boundaries-google-imagen-4-vs-imagen-3-in-real-world-use/) — Feature comparison
5. [Google Official MCP Announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services) — Official MCP servers including Genmedia
6. [Replicate Pricing](https://replicate.com/pricing) — Current pricing model
7. [Replicate Official MCP](https://mcp.replicate.com/) — Official hosted MCP server
8. [Replicate MCP Blog Post](https://replicate.com/blog/remote-mcp-server) — Remote MCP announcement
9. [OpenAI GPT Image 1.5 Docs](https://platform.openai.com/docs/models/gpt-image-1.5) — Model documentation
10. [OpenAI API Pricing](https://platform.openai.com/docs/pricing) — Current pricing
11. [Gemini 3 Pro Image Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image) — Multimodal image generation
12. [fal.ai FLUX 2 Pro](https://fal.ai/models/fal-ai/flux-2-pro) — Current FLUX 2 pricing
13. [BFL Pricing](https://bfl.ai/pricing) — Black Forest Labs direct pricing
14. [Recraft API Docs](https://www.recraft.ai/docs) — Recraft V3 pricing/features
15. [ByteDance Seedream](https://seed.bytedance.com/en/seedream4_5) — Seedream model page
16. [Adobe Firefly API](https://developer.adobe.com/firefly-services/docs/firefly-api/) — Enterprise-only API docs
17. [Amazon Titan Image Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-image-models.html) — Bedrock image gen
18. [Stability AI Platform](https://platform.stability.ai/pricing) — Developer platform pricing
19. [WaveSpeedAI 2026 Comparison](https://wavespeed.ai/blog/posts/best-ai-image-generators-2026/) — Cross-model benchmarks
20. [TeamDay Best Models 2026](https://www.teamday.ai/blog/best-ai-image-models-2026) — Flux 2 vs Recraft vs Ideogram tested
21. [AllAboutAI Imagen 4 Review](https://www.allaboutai.com/ai-reviews/imagen/) — Face quality issues documented
22. [PricePerToken Comparison](https://pricepertoken.com/image) — Cross-provider pricing comparison
