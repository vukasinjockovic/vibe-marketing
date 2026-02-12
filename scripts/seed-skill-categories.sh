#!/usr/bin/env bash
# Seed skill categories into Convex skillCategories table
# Usage: bash scripts/seed-skill-categories.sh

CONVEX_URL="${CONVEX_URL:-http://localhost:3210}"

run() {
  npx convex run skillCategories:upsert "$1" --url "$CONVEX_URL" 2>&1
}

echo "Seeding skill categories into Convex ($CONVEX_URL)..."

run '{"key":"L1_audience","displayName":"Audience Understanding","description":"Know your reader before you write","sortOrder":1,"scope":"copy"}'
echo "  L1: Audience Understanding"

run '{"key":"L2_offer","displayName":"Offer Structure","description":"Structure irresistible offers","sortOrder":2,"scope":"copy"}'
echo "  L2: Offer Structure"

run '{"key":"L3_persuasion","displayName":"Persuasion & Narrative","description":"Influence and storytelling frameworks","sortOrder":3,"scope":"copy"}'
echo "  L3: Persuasion & Narrative"

run '{"key":"L4_craft","displayName":"Copywriting Craft","description":"Direct response and advertising craft","sortOrder":4,"scope":"copy"}'
echo "  L4: Copywriting Craft"

run '{"key":"L5_quality","displayName":"Writing Quality","description":"Clarity, style, and humanization","sortOrder":5,"scope":"quality"}'
echo "  L5: Writing Quality"

run '{"key":"research","displayName":"Research & Analysis","description":"Audience research and competitive analysis","sortOrder":6,"scope":"research"}'
echo "  Research & Analysis"

run '{"key":"content","displayName":"Content Production","description":"Content creation workflows and SOPs","sortOrder":7,"scope":"general"}'
echo "  Content Production"

run '{"key":"media","displayName":"Visual & Media","description":"Image generation and media production","sortOrder":8,"scope":"visual"}'
echo "  Visual & Media"

run '{"key":"marketing","displayName":"Marketing & CRO","description":"Conversion optimization, SEO, ads, and growth","sortOrder":9,"scope":"general"}'
echo "  Marketing & CRO"

echo ""
echo "Done! 9 skill categories seeded."
