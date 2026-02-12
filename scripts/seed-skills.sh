#!/usr/bin/env bash
# Seed mbook skills into Convex skills table
# Usage: bash scripts/seed-skills.sh

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"

run() {
  npx convex run skills:upsertBySlug "$1" --url "$CONVEX_URL" 2>&1
}

echo "Seeding skills into Convex ($CONVEX_URL)..."

# ═══ L1: Audience Understanding (auto-active) ═══
run '{
  "slug": "mbook-schwarz-awareness",
  "name": "mbook-schwarz-awareness",
  "displayName": "Schwartz Awareness Levels",
  "description": "Routes copy via 5 Stages of Awareness × Market Sophistication matrix. Determines opening strategy based on where the reader is.",
  "category": "L1_audience",
  "type": "mbook",
  "isAutoActive": true,
  "isCampaignSelectable": false,
  "filePath": ".claude/skills/mbook-schwarz-awareness/SKILL.md",
  "tagline": "Know your reader before you write",
  "dashboardDescription": "Auto-applied. Routes content strategy through Awareness × Sophistication matrix."
}'
echo "  ✓ L1: Schwartz Awareness"

# ═══ L2: Offer Structure (selectable) ═══
run '{
  "slug": "mbook-hormozi-offers",
  "name": "mbook-hormozi-offers",
  "displayName": "Hormozi Value Equation",
  "description": "Structure irresistible offers using the Value Equation: Dream Outcome × Perceived Likelihood / Time Delay × Effort & Sacrifice.",
  "category": "L2_offer",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-hormozi-offers/SKILL.md",
  "tagline": "Make offers so good people feel stupid saying no",
  "dashboardDescription": "Value Equation framework for structuring offers. Best for landing pages, sales pages, ad copy."
}'
echo "  ✓ L2: Hormozi Offers"

run '{
  "slug": "mbook-hormozi-leads",
  "name": "mbook-hormozi-leads",
  "displayName": "Hormozi Lead Generation",
  "description": "Lead magnet frameworks, lead generation copy, outreach scripts, and audience-building funnels.",
  "category": "L2_offer",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-hormozi-leads/SKILL.md",
  "tagline": "Turn strangers into leads at scale",
  "dashboardDescription": "Lead generation frameworks. Best for lead magnets, outreach, audience building."
}'
echo "  ✓ L2: Hormozi Leads"

run '{
  "slug": "mbook-brunson-dotcom",
  "name": "mbook-brunson-dotcom",
  "displayName": "Brunson DotCom Funnels",
  "description": "Build sales funnels and email sequences using the Value Ladder, funnel types, and traffic strategies.",
  "category": "L2_offer",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-brunson-dotcom/SKILL.md",
  "tagline": "Every business is one funnel away",
  "dashboardDescription": "Sales funnel architecture. Best for funnel copy, email sequences, upsell flows."
}'
echo "  ✓ L2: Brunson DotCom"

run '{
  "slug": "mbook-brunson-expert",
  "name": "mbook-brunson-expert",
  "displayName": "Brunson Expert Secrets",
  "description": "Authority positioning, origin stories, the Epiphany Bridge, and mass movement frameworks.",
  "category": "L2_offer",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-brunson-expert/SKILL.md",
  "tagline": "Create a mass movement of people who pay",
  "dashboardDescription": "Expert positioning frameworks. Best for webinars, authority content, origin stories."
}'
echo "  ✓ L2: Brunson Expert"

# ═══ L3: Persuasion/Narrative (selectable, multi-select) ═══
run '{
  "slug": "mbook-cialdini-influence",
  "name": "mbook-cialdini-influence",
  "displayName": "Cialdini Influence Principles",
  "description": "Apply the 7 principles of persuasion: Reciprocity, Liking, Social Proof, Authority, Scarcity, Commitment/Consistency, Unity.",
  "category": "L3_persuasion",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "subSelections": [
    {"key": "reciprocity", "label": "Reciprocity", "description": "Give value first to create obligation"},
    {"key": "liking", "label": "Liking", "description": "Build rapport and similarity"},
    {"key": "social_proof", "label": "Social Proof", "description": "Show others doing the same thing"},
    {"key": "authority", "label": "Authority", "description": "Establish expertise and credibility"},
    {"key": "scarcity", "label": "Scarcity", "description": "Limited availability creates urgency"},
    {"key": "commitment", "label": "Commitment/Consistency", "description": "Small yeses lead to big yeses"},
    {"key": "unity", "label": "Unity", "description": "Shared identity and belonging"}
  ],
  "filePath": ".claude/skills/mbook-cialdini-influence/SKILL.md",
  "tagline": "The science of ethical persuasion",
  "dashboardDescription": "7 persuasion principles with sub-selections. Best for any persuasive content."
}'
echo "  ✓ L3: Cialdini Influence"

run '{
  "slug": "mbook-voss-negotiation",
  "name": "mbook-voss-negotiation",
  "displayName": "Voss Tactical Empathy",
  "description": "Apply tactical empathy, mirroring, labeling, and calibrated questions to marketing copy.",
  "category": "L3_persuasion",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-voss-negotiation/SKILL.md",
  "tagline": "Never split the difference with your reader",
  "dashboardDescription": "Tactical empathy for copy. Best for objection handling, email sequences, video scripts."
}'
echo "  ✓ L3: Voss Negotiation"

run '{
  "slug": "mbook-miller-storybrand",
  "name": "mbook-miller-storybrand",
  "displayName": "Miller StoryBrand",
  "description": "Structure marketing messages using the 7-part StoryBrand framework: Character, Problem, Guide, Plan, CTA, Failure, Success.",
  "category": "L3_persuasion",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-miller-storybrand/SKILL.md",
  "tagline": "Make the customer the hero",
  "dashboardDescription": "Narrative framework. Best for brand messaging, ebooks, video scripts, website copy."
}'
echo "  ✓ L3: Miller StoryBrand"

run '{
  "slug": "mbook-sugarman-copywriting",
  "name": "mbook-sugarman-copywriting",
  "displayName": "Sugarman Psychological Triggers",
  "description": "Apply the Slippery Slide framework and 31 Psychological Triggers for compelling copy.",
  "category": "L3_persuasion",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "subSelections": [
    {"key": "curiosity", "label": "Curiosity", "description": "Open loops that compel reading"},
    {"key": "storytelling", "label": "Storytelling", "description": "Narrative hooks and payoffs"},
    {"key": "specificity", "label": "Specificity", "description": "Concrete details build credibility"},
    {"key": "urgency", "label": "Urgency", "description": "Time pressure and deadlines"},
    {"key": "exclusivity", "label": "Exclusivity", "description": "Limited access creates desire"}
  ],
  "filePath": ".claude/skills/mbook-sugarman-copywriting/SKILL.md",
  "tagline": "Every sentence sells the next sentence",
  "dashboardDescription": "Psychological triggers with sub-selections. Best for email, social, short-form copy."
}'
echo "  ✓ L3: Sugarman Copywriting"

# ═══ L4: Craft/Style (selectable, radio — pick one primary) ═══
run '{
  "slug": "mbook-halbert-boron",
  "name": "mbook-halbert-boron",
  "displayName": "Halbert Direct Response",
  "description": "Direct response copywriting fundamentals: A-pile mail, headline formulas, urgency, personal tone.",
  "category": "L4_craft",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-halbert-boron/SKILL.md",
  "tagline": "Write like you are talking to one person",
  "dashboardDescription": "Direct response style. Best for sales letters, email, ad copy, landing pages."
}'
echo "  ✓ L4: Halbert Direct Response"

run '{
  "slug": "mbook-ogilvy-advertising",
  "name": "mbook-ogilvy-advertising",
  "displayName": "Ogilvy Advertising Craft",
  "description": "David Ogilvy advertising craft: headline rules, body copy techniques, research-driven advertising.",
  "category": "L4_craft",
  "type": "mbook",
  "isAutoActive": false,
  "isCampaignSelectable": true,
  "filePath": ".claude/skills/mbook-ogilvy-advertising/SKILL.md",
  "tagline": "The consumer is not a moron, she is your wife",
  "dashboardDescription": "Advertising craft style. Best for brand content, blog posts, authority articles."
}'
echo "  ✓ L4: Ogilvy Advertising"

echo ""
echo "Done! Seeded 11 skills (1 auto-active + 10 selectable)"
