# Kraken: 7 Plumbing & HVAC Calculators for FatStud

## Checkpoints
<!-- Resumable state for kraken agent -->
**Task:** Build 7 plumbing and HVAC calculators (JS + Blade) for FatStud
**Started:** 2026-03-07T18:48:00Z
**Last Updated:** 2026-03-07T18:55:00Z

### Phase Status
- Phase 1 (Codebase Analysis): VALIDATED (patterns understood from existing calcs)
- Phase 2 (Plumbing JS): VALIDATED (4 files, node -c passes)
- Phase 3 (HVAC JS): VALIDATED (3 files, node -c passes)
- Phase 4 (Blade Templates): VALIDATED (7 blade files created)
- Phase 5 (Build): VALIDATED (npm run build success in 2.81s)

### Validation State
```json
{
  "files_created": [
    "resources/js/calculators/plumbing/drain-pipe-slope.js",
    "resources/js/calculators/plumbing/pipe-volume.js",
    "resources/js/calculators/plumbing/flow-rate.js",
    "resources/js/calculators/plumbing/water-heater-size.js",
    "resources/js/calculators/hvac/furnace-btu.js",
    "resources/js/calculators/hvac/heat-loss.js",
    "resources/js/calculators/hvac/insulation.js",
    "resources/views/components/calculators/drain-pipe-slope.blade.php",
    "resources/views/components/calculators/pipe-volume.blade.php",
    "resources/views/components/calculators/flow-rate.blade.php",
    "resources/views/components/calculators/water-heater-size.blade.php",
    "resources/views/components/calculators/furnace-btu.blade.php",
    "resources/views/components/calculators/heat-loss.blade.php",
    "resources/views/components/calculators/insulation.blade.php"
  ],
  "syntax_check": "all 7 JS files pass node -c",
  "build_success": true,
  "build_time": "2.81s",
  "index_js_modified": false
}
```

### Resume Context
- All phases complete
- index.js NOT modified per instructions -- calculators need registration there to be functional
- No blockers
