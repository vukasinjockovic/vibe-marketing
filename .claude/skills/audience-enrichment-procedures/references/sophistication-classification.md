# Market Sophistication Classification Guide

Based on Eugene Schwartz's market sophistication model from "Breakthrough Advertising," adapted for focus group enrichment.

---

## The 5 Stages of Market Sophistication

Market sophistication measures how many marketing claims the prospect has already been exposed to. It determines what TYPE of messaging will work.

### Stage 1: First to Market

**What works:** Simple, direct claims. "Lose 10 pounds." "Get fit fast."

**Audience signals:**
- Marketing hooks use simple declarative claims
- Language suggests first exposure to category: "never tried", "first time", "new to this"
- Beliefs reflect naive optimism: "just need to find the right thing", "there's a simple solution"
- Few or no objections (haven't been burned yet)

**Key insight:** These prospects haven't been exposed to marketing in this category. Direct claims feel new and exciting.

---

### Stage 2: Expanded Claims

**What works:** Bigger, bolder claims with some proof. "Lose 20 pounds in half the time."

**Audience signals:**
- Marketing hooks need qualifiers: "more effective", "faster", "clinically proven"
- Language expresses desire for improvement: "looking for something better", "need proof"
- Beliefs show prior exposure: "I've seen claims before", "need something more powerful"
- Objections include skepticism: "heard this before", "prove it"

**Key insight:** Simple claims no longer work. The market needs you to out-claim competitors.

---

### Stage 3: Unique Mechanism

**What works:** Explain HOW your product works differently. "Our thermogenic cycling process..."

**Audience signals:**
- Marketing hooks reference mechanisms: "patented", "proprietary", "unique formula"
- Language focuses on understanding: "how does it work", "what's the science", "what makes this different"
- Beliefs value methodology: "the method matters", "I want to understand the mechanism"
- Objections demand differentiation: "what's different about this", "how exactly does it work"

**Key insight:** Claims don't matter anymore. The market wants to know WHY your product works where others didn't.

---

### Stage 4: Expanded Mechanism

**What works:** Better mechanism with more proof. "Double-blind study proves our approach..."

**Audience signals:**
- Marketing hooks cite research: "peer-reviewed", "clinical study", "bioavailable"
- Language demands evidence: "show me the research", "what do the studies say"
- Beliefs reflect mechanism fatigue: "I've tried unique mechanisms before", "only trust evidence"
- Objections challenge proof: "where's the peer-reviewed evidence", "other products claimed unique mechanisms too"

**Key insight:** Unique mechanisms alone don't work. The market now needs PROOF that your mechanism is superior.

---

### Stage 5: Identification

**What works:** The prospect buys based on identity, community, and brand alignment. "Built by lifters, for lifters."

**Audience signals:**
- Marketing hooks emphasize belonging: "join the movement", "the brand athletes trust"
- Language reflects identity: "I identify as", "part of the community", "represents who I am"
- Beliefs tie consumption to self: "I buy brands that align with my values", "I am what I consume"
- Objections are identity-based: "does this brand represent me", "who else uses this"

**Key insight:** Features, mechanisms, and proof are irrelevant. The market buys because the brand IS them.

---

## How Sophistication Interacts with Awareness

These are orthogonal dimensions:

| | Unaware | Problem Aware | Solution Aware | Product Aware | Most Aware |
|---|---|---|---|---|---|
| **Stage 1** | Interrupt with simple claim | Name the pain + simple fix | Simple recommendation | Direct comparison | Price/deal |
| **Stage 3** | Educate via mechanism story | Mechanism explains the cause | Mechanism differentiates approach | Mechanism vs their current product | Mechanism justifies premium |
| **Stage 5** | Identity-first storytelling | "People like you struggle with..." | "The community chose this approach" | "Unlike Brand X, we're for YOUR tribe" | "You already know. Join us." |

---

## Classification Algorithm

The `infer_sophistication.py` script uses weighted keyword matching:
- Hook keywords: 2x weight (strongest signal of what messaging works)
- Language keywords: 1x weight
- Beliefs keywords: 1x weight
- Objections keywords: 1x weight

**Confidence mapping:**
- 4+ weighted score = high confidence
- 2-3 weighted score = medium confidence
- 0-1 weighted score = low confidence
