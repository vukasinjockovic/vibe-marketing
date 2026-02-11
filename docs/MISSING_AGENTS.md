# Missing Agents — Not Yet Implemented

These agents are defined in `vibe-marketing-platform-v3.md` but not yet seeded or built.
The 18 currently seeded agents cover all pipeline steps. These are future additions.

## Intelligence Department (7 agents)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-competitor-analyst | sonnet | daily | Competitor intelligence gathering |
| vibe-brand-monitor | sonnet | */8h | Brand monitoring, social listening |
| vibe-reddit-scout | sonnet | */8h | Reddit opportunity scouting |
| vibe-twitter-scout | sonnet | */8h | X/Twitter opportunity scouting |
| vibe-linkedin-scout | sonnet | daily | LinkedIn opportunity scouting |
| vibe-trend-detector | sonnet | */12h | Trend detection across platforms |
| vibe-review-harvester | sonnet | weekly | Review mining and analysis |

## SEO Department (2 agents)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-keyword-deep-researcher | sonnet | on-demand | Deep keyword cluster research |
| vibe-seo-auditor | sonnet | weekly | Technical SEO audit |

## Content Department (1 agent)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-press-writer | opus | on-demand | PR and press releases |

## Quality Department (2 agents)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-fact-checker | sonnet | triggered | Product/claim accuracy verification |
| vibe-plagiarism-checker | haiku | triggered | Copyscape plagiarism checks |

## Visual Department (1 agent)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-video-generator | haiku | on-demand | AI video generation (Runway, etc.) |

## Distribution Department (3 agents)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-publisher | haiku | */3h | CMS publishing (WordPress, Ghost, Webflow) |
| vibe-social-distributor | haiku | */12h | Social platform auto-posting |
| vibe-email-distributor | haiku | on-demand | Email campaign dispatch |

## Analytics Department (4 agents)

| Agent | Model | Schedule | Purpose |
|-------|-------|----------|---------|
| vibe-analytics-reporter | sonnet | weekly | Performance analytics reports |
| vibe-rank-tracker | haiku | daily | Keyword position tracking |
| vibe-content-refresher | sonnet | weekly | Content decay detection and refresh |
| vibe-roi-calculator | sonnet | monthly | Cost and revenue analysis |

---

**Total missing: 20 agents**
**Total seeded: 18 agents**
**Total planned: 38 agents**

## To add these agents

1. Add the agent definition to `convex/seed.ts` in the agents array
2. Add service dependencies to the `deps` array in seed.ts
3. Create the skill directory: `.claude/skills/{agent-name}/SKILL.md`
4. Run: `npx convex run seed:clearAll && npx convex run seed:run`
5. Or register individually: `npx convex run agents:register '{...}'`
