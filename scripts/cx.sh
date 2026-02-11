#!/bin/bash
# scripts/cx.sh — Convex CLI shortcut
# Usage: ./scripts/cx.sh tasks:listByAgent '{"agentName":"scout"}'
npx convex run "$1" "$2" --url http://localhost:3210 2>/dev/null
