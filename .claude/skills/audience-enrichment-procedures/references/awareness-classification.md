# Awareness Stage Classification Guide

Based on Eugene Schwartz's "Breakthrough Advertising" -- the 5 Stages of Awareness model adapted for focus group enrichment.

---

## Stage Definitions

### 1. Unaware

**Definition:** The prospect does not recognize they have a problem. Content with status quo, no urgency.

**Key Indicators:**
- Beliefs: "I'm fine", "doesn't matter", "not a priority"
- Language: No problem-related vocabulary, future-oriented dismissals ("someday")
- Behavior: Not searching for solutions, no engagement with problem-related content
- Objections: "I don't need this", "I'm happy as I am"

**Example Focus Group:**
> "Casual Gym-Goer" -- goes to gym occasionally, thinks they're healthy enough, not tracking anything

**How to Distinguish from Problem Aware:** Unaware people genuinely don't see a problem. Problem-aware people feel pain but don't know solutions. If there's any frustration or dissatisfaction expressed, they're at least problem_aware.

---

### 2. Problem Aware

**Definition:** Recognizes the problem, feels the pain, but doesn't know solutions exist or what they look like.

**Key Indicators:**
- Beliefs: "I'm struggling", "I can't figure this out", "Something is wrong"
- Language: Frustration language, "stuck", "why can't I", emotional vocabulary
- Behavior: Venting in forums, not yet searching for products
- Objections: "Nothing works", "I've tried everything", "It's probably genetics"

**Example Focus Group:**
> "Frustrated Dieters" -- know they need to lose weight, feel stuck, haven't found a program

**How to Distinguish from Solution Aware:** Problem-aware people express frustration without mentioning solution categories. Solution-aware people talk about approaches they've heard of ("I know I should try keto" vs "I can't lose weight").

---

### 3. Solution Aware

**Definition:** Knows solutions exist in general terms, researching approaches, but hasn't committed to a specific product or method.

**Key Indicators:**
- Beliefs: "I know I should", "I need to figure out the right approach", "I've heard about X"
- Language: Research language, comparing approaches (not products), "which method is best"
- Behavior: Reading articles about approaches, not yet comparing specific products
- Objections: "It's too complicated", "I'm overwhelmed by options", "Takes too much time"

**Example Focus Group:**
> "Research-Phase Lifters" -- know they need to lift weights, comparing programs (SS, 5x5, PPL), haven't picked one

**How to Distinguish from Product Aware:** Solution-aware talks about methods/approaches ("should I do keto or paleo?"). Product-aware talks about specific products/brands ("is Noom better than MyFitnessPal?").

---

### 4. Product Aware

**Definition:** Knows your product (or category of products) exists. Has tried similar products. Comparing specific options.

**Key Indicators:**
- Beliefs: "I tried X but it didn't work", "Looking for something better", "Need a different option"
- Language: Brand names, feature comparisons, "which one is better"
- Behavior: Reading reviews, comparison shopping, has purchase history in category
- Objections: "How is this different?", "Can I trust this brand?", "Is there a guarantee?"

**Example Focus Group:**
> "Supplement Switchers" -- tried Optimum Nutrition, looking at other brands, comparing ingredients

**How to Distinguish from Most Aware:** Product-aware people are still deciding. Most-aware people have decided and are looking for the best deal. Product-aware asks "which one?" -- most-aware asks "what's the price?".

---

### 5. Most Aware

**Definition:** Knows the product, may have purchased before. Ready to buy, looking for the best deal/timing.

**Key Indicators:**
- Beliefs: "This is the best", "compared to X it's worth it", "waiting for a deal"
- Language: Price/deal vocabulary, coupon codes, "worth it", comparison language
- Behavior: Checking prices, waiting for sales, has purchased from category before
- Objections: "Price is too high", "Is it cheaper elsewhere?", "Any coupons?"

**Example Focus Group:**
> "Brand Loyalists" -- already use the product category, comparing prices, looking for deals

**How to Distinguish from Product Aware:** Most-aware objections are about price/deal, not about trust/differentiation. They know what they want; they're negotiating terms.

---

## Classification Algorithm

The `infer_awareness.py` script scores each stage by counting keyword matches across beliefs, objections, language patterns, and pain points. The stage with the highest score wins.

**Tie-breaking:** When scores are equal, the algorithm favors the first stage found in rule order (most_aware checked first, then product_aware, etc.). This is intentional -- if a group shows signals across multiple stages, they're likely at the higher stage.

**Confidence mapping:**
- 3+ matches = high confidence
- 2 matches = medium confidence
- 0-1 matches = low confidence
