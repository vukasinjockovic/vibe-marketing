#!/usr/bin/env bash
# seed-agent-skills.sh — Wire staticSkillIds on agents in the live DB
# One-time script. Safe to re-run (skips agents that already have skills).
set -euo pipefail

CONVEX_URL="http://localhost:3210"

# Agent → skill slugs mapping
declare -A AGENT_SKILLS=(
  ["vibe-content-writer"]="content-writing-procedures mbook-schwarz-awareness humanizer writing-clearly-and-concisely"
  ["vibe-email-writer"]="email-sequence mbook-schwarz-awareness humanizer writing-clearly-and-concisely"
  ["vibe-social-writer"]="social-content mbook-schwarz-awareness humanizer writing-clearly-and-concisely"
  ["vibe-ad-writer"]="paid-ads mbook-schwarz-awareness"
  ["vibe-landing-page-writer"]="page-cro"
  ["vibe-content-reviewer"]="content-review-procedures writing-clearly-and-concisely"
  ["vibe-humanizer"]="humanizer writing-clearly-and-concisely"
  ["vibe-content-repurposer"]="content-writing-procedures"
  ["vibe-audience-parser"]="audience-analysis-procedures"
  ["vibe-audience-researcher"]="audience-research-procedures google-trends-research google-suggest-research youtube-research amazon-reviews-research pinterest-research etsy-research quora-research"
  ["vibe-audience-enricher"]="audience-enrichment-procedures"
  ["vibe-keyword-researcher"]="content-writing-procedures google-trends-research google-suggest-research youtube-research amazon-reviews-research"
  ["vibe-serp-analyzer"]="content-writing-procedures google-trends-research google-suggest-research"
  ["vibe-engagement-trend-researcher"]="google-trends-research google-suggest-research youtube-research quora-research pinterest-research"
  ["vibe-image-director"]="image-prompt-engineering"
  ["vibe-image-generator"]="image-generation-procedures"
  ["vibe-script-writer"]="video-script-guide"
  ["vibe-ebook-writer"]="ebook-procedures"
)

echo "=== Seeding agent-skill relations ==="

wired=0
skipped=0
errors=0

for agent_name in "${!AGENT_SKILLS[@]}"; do
  # Get agent ID
  agent_json=$(npx convex run agents:getByName "{\"name\":\"$agent_name\"}" --url "$CONVEX_URL" 2>/dev/null)
  agent_id=$(echo "$agent_json" | python3 -c "import sys,json; print(json.load(sys.stdin)['_id'])" 2>/dev/null)

  if [ -z "$agent_id" ]; then
    echo "  SKIP $agent_name — not found in DB"
    skipped=$((skipped + 1))
    continue
  fi

  # Check if already has skills
  existing_count=$(echo "$agent_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('staticSkillIds',[])))" 2>/dev/null)
  if [ "$existing_count" -gt 0 ]; then
    echo "  SKIP $agent_name — already has $existing_count skills"
    skipped=$((skipped + 1))
    continue
  fi

  # Resolve skill slugs to IDs
  skill_ids="["
  first=true
  for slug in ${AGENT_SKILLS[$agent_name]}; do
    skill_json=$(npx convex run skills:getBySlug "{\"slug\":\"$slug\"}" --url "$CONVEX_URL" 2>/dev/null)
    skill_id=$(echo "$skill_json" | python3 -c "import sys,json; print(json.load(sys.stdin)['_id'])" 2>/dev/null)
    if [ -z "$skill_id" ]; then
      echo "  WARN $agent_name — skill '$slug' not found"
      errors=$((errors + 1))
      continue
    fi
    if [ "$first" = true ]; then
      skill_ids+="\"$skill_id\""
      first=false
    else
      skill_ids+=",\"$skill_id\""
    fi
  done
  skill_ids+="]"

  # Update agent
  npx convex run agents:updateSkills "{\"id\":\"$agent_id\",\"staticSkillIds\":$skill_ids}" --url "$CONVEX_URL" 2>/dev/null
  echo "  OK   $agent_name — wired ${AGENT_SKILLS[$agent_name]}"
  wired=$((wired + 1))
done

echo ""
echo "=== Done: $wired wired, $skipped skipped, $errors errors ==="
