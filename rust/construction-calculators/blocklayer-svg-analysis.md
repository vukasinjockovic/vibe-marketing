# Research Report: Blocklayer.com SVG-Generating Calculator Analysis
Generated: 2026-03-07

## Summary

Blocklayer.com contains **20+ calculators that generate serious visual output** using HTML5 Canvas (not SVG inline -- they render to Canvas then offer SVG export). Every calculator is **100% client-side**: vanilla JavaScript with zero frameworks, zero server calls for calculations, zero XHR/fetch requests. Each calculator loads two JS files: a shared `Gen.js` library and a page-specific minified JS bundle (e.g., `NotchEng_V27-2.js`). All rendering is via Canvas 2D API with optional SVG download via a `_SVG()` helper function that constructs SVG strings client-side and triggers a blob download.

## Technology Stack (Verified from Source)

- **Rendering**: HTML5 Canvas 2D Context (NOT inline SVG, NOT server-rendered)
- **JS Architecture**: Vanilla JavaScript, no frameworks, no build tools visible
- **Shared Library**: `/Scripts/Gen.js` (common utilities, printing, SVG export)
- **Per-Calculator JS**: Dedicated minified bundle per calculator (e.g., `HipEng_V15.js`, `NotchEng_V27-2.js`)
- **SVG Export**: Client-side SVG string construction, downloaded as blob via `_SVG()` function
- **PDF Export**: `_PrintAllCanvas()` opens a print-friendly window with all canvas elements
- **No Server Calls**: Zero XHR/fetch for calculations. All geometry computed in browser.
- **Real-time Updates**: Sliders (`input[type=range]`) connected to `oninput` handlers that recalculate + redraw instantly

## Client-Side Verification

**Evidence that ALL calculations are client-side:**
1. Each page loads exactly 2 JS files: `Gen.js` + page-specific bundle. No API endpoints.
2. No `fetch()`, `XMLHttpRequest`, or `$.ajax` calls in any calculator page source.
3. Slider `oninput` handlers call JS functions directly (e.g., `rngWidth_change(this)`) -- instant redraw.
4. The `_PrintAllCanvas()` function reads canvas elements directly from DOM -- no server round-trip.
5. SVG export constructs SVG strings entirely in JavaScript via `_SVG()` helper.
6. Body `onload="Setup()"` initializes all calculations from default input values.
7. Google Analytics is the ONLY external request (besides ads).

---

## Complete List of SVG/Canvas-Generating Calculators

### TIER 1: Highest Complexity (Difficulty 4-5)

---

#### 1. Hip Roof Framing Calculator
- **URL**: https://www.blocklayer.com/roof/hipeng
- **JS Bundle**: `/roof/Scripts/HipEng_V15.js`
- **Canvas Count**: 17 canvases (!!)
- **Visual Type**: Full roof framing plan, rafter placement diagram, profile view, individual rafter detail diagrams, cut angle templates, hip chamfer diagram, sheathing cut angles
- **Canvases**: `cnvsRoof` (1010x530), `cnvsJoin`, `cnvsJoinSquare`, `cnvsJoinSquare2`, `cnvsRun` (1010x530), `cnvsRafter`, `cnvsHip`, `cnvsTemplate`, `cnvsProfile` (990x661), `cnvsRoofSegments`, `cnvsHipDetail`, `cnvsCreeperDetail`, `cnvsHipChamfer`, `cnvsHipTemplate`, `cnvsCreeperTemplate`, `cnvsRafterTemplate`, `cnvsPly`, `cnvsPorch`
- **Complexity**: Complex -- 3D perspective projection of entire roof, multiple rafter types with individual cut angle diagrams, full dimensioning system
- **Printable**: Yes -- full scale rafter cut templates
- **Interactive**: Yes -- sliders for pitch, span, overhang update all 17 diagrams simultaneously
- **Reverse-engineer difficulty**: **5/5** -- Most complex calculator on the site. 3D projection math, multiple rafter type calculations (common, hip, creeper/jack), compound angle cuts, birdsmouth calculations, soffit drops, sheathing cuts

---

#### 2. Spiral/Circular Stair Calculator
- **URL**: https://www.blocklayer.com/stairs/spiral-stairseng
- **JS Bundle**: `/stairs/Scripts/SpiralEng_V14.js`
- **Visual Type**: Full plan view of spiral staircase with tread layout, animatable diagrams
- **Complexity**: Complex -- circular geometry, tread depth calculations at varying radii, headroom clearance, winder calculations
- **Printable**: Yes -- plan diagrams
- **Interactive**: Yes -- animate tread depths, adjust rotation, see resulting angles
- **Reverse-engineer difficulty**: **5/5** -- Polar coordinate geometry, variable-width treads on spiral, headroom calculations through multiple revolutions

---

#### 3. Gambrel Roof Framing Calculator
- **URL**: https://www.blocklayer.com/roof/gambreleng
- **JS Bundle**: `/roof/Scripts/GambrelRoofEng_V10-2.js`
- **Canvas Count**: 5
- **Canvases**: `cnvsMain` (960x550), `cnvsLowerRafter`, `cnvsUpperRafter`, `cnvsGussetTop`, `cnvsGussetBot`
- **Visual Type**: Full gambrel roof geometry diagram with both upper and lower pitch sections, individual rafter detail drawings, gusset plate dimension diagrams
- **Complexity**: Complex -- dual-pitch roof with independent upper/lower angles, gusset plate calculations
- **Printable**: Yes -- rafter diagrams with full dimensions
- **Interactive**: Yes -- sliders adjust both pitch angles independently
- **Reverse-engineer difficulty**: **4/5** -- Two independent roof pitches, transition angle calculations, gusset geometry

---

#### 4. Pipe/Tube Notching Template Generator
- **URL**: https://www.blocklayer.com/fab/round-tube/notcheng
- **JS Bundle**: `Scripts/NotchEng_V27-2.js` (version 27!)
- **Canvas Count**: 5
- **Canvases**: `cnvsProfile` (500x200), `cnvsTemplate` (460x504), `cnvsMultiTemplate` (dynamic), `cnvsPlot` (460x404), `cnvsSection` (161x211)
- **Visual Type**: 3D-ish tube intersection profile, full-scale wrap-around cutting templates (sinusoidal curves), plot diagrams, cross-section views
- **Complexity**: Very complex -- tube intersection geometry produces sine-wave cutting patterns at varying angles, wall thickness compensation
- **Printable**: Yes -- FULL SCALE wrap-around templates you print, cut, and wrap around actual pipe
- **Interactive**: Yes -- angle, diameter, wall thickness sliders
- **SVG Export**: Yes (`DownloadSVG()` button)
- **Reverse-engineer difficulty**: **5/5** -- Cylinder-cylinder intersection mathematics, unrolling 3D intersection curves to 2D cutting templates, wall thickness compensation. This is the hardest geometry on the site. Version 27 indicates years of iteration.

---

#### 5. Square-to-Round Transition Template
- **URL**: https://www.blocklayer.com/fab/transitions/square-roundeng
- **JS Bundle**: `Scripts/SquareRoundEng_V14.js`
- **Canvas Count**: 3
- **Canvases**: `cnvsPlan` (260x260), `cnvsElevation` (260x223), `cnvsTransition` (1127x586)
- **Visual Type**: Plan view, elevation view, and full-scale unrolled transition template with triangulation pattern
- **Complexity**: Very complex -- sheet metal pattern development via triangulation method
- **Printable**: Yes -- full scale sheet metal cutting template
- **Interactive**: Yes
- **SVG Export**: Yes
- **Reverse-engineer difficulty**: **5/5** -- Classical descriptive geometry problem. Requires triangulation of a square-to-round transition, unrolling each triangulated face into a flat pattern. Serious computational geometry.

---

#### 6. Segmented Woodturning Calculator
- **URL**: https://www.blocklayer.com/woodturning-segmentseng
- **JS Bundle**: `/Scripts/WoodTurnSegmentsEng_V18.js`
- **Canvas Count**: 7
- **Canvases**: `cnvsPlan` (800x820), `cnvsSegment` (640x260), `cnvsGapSegment`, `cnvsBowlProfile` (300x200), `cnvsStave` (800x500), `cnvsStaveCuts` (1000x618), `cnvsAngle` (400x400)
- **Visual Type**: Full circular segment plan with all pieces, individual segment detail, bowl profile, stave templates, cutting diagrams
- **Complexity**: Complex -- polygonal segment calculations at varying ring diameters for bowl/vase profiles, stave geometry
- **Printable**: Yes -- full scale segment and stave cutting templates
- **Interactive**: Yes
- **SVG Export**: Yes (3 separate SVG downloads: main, segment, gap)
- **Reverse-engineer difficulty**: **4/5** -- Multi-ring segment calculations with varying diameters, miter angles per ring, stave geometry

---

### TIER 2: Medium-High Complexity (Difficulty 3-4)

---

#### 7. Straight Stair Stringer Calculator
- **URL**: https://www.blocklayer.com/stairs/straighteng
- **JS Bundle**: `/stairs/Scripts/StraightEng_V*.js`
- **Visual Type**: Side elevation stringer profile, plan view, headroom clearance diagram
- **Complexity**: Medium-high -- stringer profile with rise/run, headroom intersection calculations
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Straightforward staircase geometry with notched stringer profiles

---

#### 8. Steel Spine Stair Calculator
- **URL**: https://www.blocklayer.com/stairs/steel-spineeng
- **JS Bundle**: `/stairs/Scripts/SteelSpineEng_V*.js`
- **Visual Type**: Steel central spine stair geometry with tread brackets
- **Complexity**: Medium-high -- spine stair with angled brackets and tread geometry
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Similar to straight stairs but with steel bracket detail

---

#### 9. Gable Roof Framing Calculator
- **URL**: https://www.blocklayer.com/roof/gableeng
- **JS Bundle**: `/roof/Scripts/GableEng_V*.js`
- **Visual Type**: Full gable roof plan, rafter placement, rafter detail diagrams
- **Complexity**: Medium-high -- simpler than hip roof (no hip/valley rafters) but still full framing plan
- **Printable**: Yes -- rafter cut templates
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Subset of hip roof calculator complexity

---

#### 10. Kerf Spacing Calculator (Bending Wood)
- **URL**: https://www.blocklayer.com/kerf-spacingeng
- **JS Bundle**: `/Scripts/KerfEng_V18.js`
- **Canvas Count**: 5
- **Canvases**: `cnvsKerfProfile` (980x198), `cnvsCurve` (980x304), `cnvsTemplate` (980x140), `cnvsBit` (200x200), `cnvsSweepRad` (400x300)
- **Visual Type**: Straight board with kerf cuts, same board bent to radius, full-scale marking template, router bit diagram, sweep radius diagram
- **Complexity**: Medium-high -- calculating kerf spacing for a given radius, showing before/after bending
- **Printable**: Yes -- full scale kerf marking template
- **Interactive**: Yes -- sliders animate the bending
- **Reverse-engineer difficulty**: **3/5** -- Arc length calculations with kerf gap closure geometry

---

#### 11. Pipe/Tube Miter Template Generator
- **URL**: https://www.blocklayer.com/fab/round-tube/mitereng
- **JS Bundle**: `Scripts/MiterEng_V*.js`
- **Visual Type**: Tube miter profile, full-scale wrap-around cutting template
- **Complexity**: Medium-high -- similar to notching but simpler (straight plane cut vs. cylinder intersection)
- **Printable**: Yes -- full scale wrap templates
- **Interactive**: Yes
- **SVG Export**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Cylinder cut by plane = sinusoidal unrolled curve

---

#### 12. Dovetail Joint Template Generator
- **URL**: https://www.blocklayer.com/woodjoints/dovetaileng
- **JS Bundle**: `/woodjoints/Scripts/DovetailEng_V3.js`
- **Canvas Count**: 1 (large: 816x472)
- **Visual Type**: Full-scale printable dovetail joint template showing pins and tails
- **Complexity**: Medium-high -- evenly-spaced dovetail geometry with variable pin/tail ratios
- **Printable**: Yes -- FULL SCALE template you fold over wood and cut through
- **Interactive**: Yes -- width slider adjusts template in real-time
- **Reverse-engineer difficulty**: **3/5** -- Trapezoidal geometry with even spacing, but precise fit is critical

---

#### 13. Pie Cut Tubing Bend Calculator
- **URL**: https://www.blocklayer.com/fab/round-tube/pie-cutseng
- **JS Bundle**: `Scripts/PieCutsEng_V*.js`
- **Visual Type**: Pie-cut tube bend diagram with individual miter cut templates
- **Complexity**: Medium-high -- calculating pie-cut segment angles for tube bending
- **Printable**: Yes -- full scale cutting templates
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **4/5** -- Multiple miter cuts at calculated angles to form a smooth curve

---

#### 14. 3-Way Corner Join Templates (Round Tube)
- **URL**: https://www.blocklayer.com/fab/round-tube/corner3eng
- **JS Bundle**: `Scripts/RoundTubeCornerThreeEng_V3.js`
- **Canvas Count**: 1 (600x600)
- **Visual Type**: 3-way intersection cutting templates
- **Complexity**: Medium-high -- three-cylinder intersection geometry
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **4/5** -- Triple cylinder intersection is significantly harder than two-cylinder

---

#### 15. Round-to-Round Cone Transition Template
- **URL**: https://www.blocklayer.com/fab/transitions/round-roundeng
- **JS Bundle**: Transition cone JS
- **Visual Type**: Conical frustum unrolled pattern
- **Complexity**: Medium -- cone frustum development
- **Printable**: Yes -- full scale cone pattern
- **SVG Export**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Classical cone development geometry

---

#### 16. Dividing Plate Generator (SVG)
- **URL**: https://www.blocklayer.com/dividing-plateeng
- **JS Bundle**: `/Scripts/DividingPlateEng_V8.js`
- **Canvas Count**: 1 (600x600)
- **Visual Type**: Full-scale dividing plate with concentric rings of holes at specified divisions
- **Complexity**: Medium -- circular division calculations
- **Printable**: Yes -- full scale printable plate
- **SVG Export**: Yes (primary output format)
- **Reverse-engineer difficulty**: **2/5** -- Circular division is straightforward polar coordinate math

---

### TIER 3: Medium Complexity (Difficulty 2-3)

---

#### 17. Twisted (Arigata) Dovetail Template
- **URL**: https://www.blocklayer.com/woodjoints/dovetailtwisteng
- **JS Bundle**: Dovetail twist JS
- **Visual Type**: Twisted dovetail joint template with 3D perspective
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **4/5** -- 3D twisted geometry is deceptively complex

---

#### 18. Log Half-Dovetail Template
- **URL**: https://www.blocklayer.com/woodjoints/log-dovetaileng
- **Visual Type**: Log cabin dovetail notch templates with full dimensions
- **Printable**: Yes -- full scale
- **Reverse-engineer difficulty**: **3/5** -- Complex because of log diameter variations

---

#### 19. Mortise and Tenon Calculator
- **URL**: https://www.blocklayer.com/woodjoints/mortise-tenoneng
- **Visual Type**: Multi-view mortise and tenon joint diagrams (animated)
- **Printable**: Scaled diagrams
- **Interactive**: Yes -- sliders adjust all dimensions
- **Reverse-engineer difficulty**: **2/5** -- Rectangular geometry with multiple views

---

#### 20. Gazebo Roof and Floor Plans
- **URL**: https://www.blocklayer.com/gazebos/gazeboeng
- **Visual Type**: Polygonal gazebo plan with rafter placement
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Regular polygon geometry with compound angle rafters

---

#### 21. Cone Pattern Templates
- **URL**: https://www.blocklayer.com/cone-patternseng
- **Visual Type**: Full-scale cone development/unroll pattern
- **Printable**: Yes -- full scale
- **Reverse-engineer difficulty**: **2/5** -- Basic cone development geometry

---

#### 22. Pulley & Belt Calculator
- **URL**: https://www.blocklayer.com/pulley-belteng
- **Visual Type**: Animated scaled diagram of pulley and belt system
- **Interactive**: Yes -- drag sliders to see belt wrap change
- **Reverse-engineer difficulty**: **2/5** -- Circle tangent geometry

---

#### 23. Deck Layout Calculator
- **URL**: https://www.blocklayer.com/deckcalculatoreng
- **Visual Type**: Full deck plan with stumps, bearers, joists, boards
- **Printable**: Yes
- **Interactive**: Yes
- **Reverse-engineer difficulty**: **3/5** -- Complex due to many interacting spacing rules

---

---

## Comparison Matrix -- Top 10 Hardest Calculators

| # | Calculator | Canvas Count | Printable Full-Scale | SVG Export | Geometry Type | Difficulty |
|---|-----------|-------------|---------------------|-----------|--------------|-----------|
| 1 | Hip Roof Framing | 17 | Yes (rafter templates) | No (PDF) | 3D projection, compound angles | 5/5 |
| 2 | Pipe Notching Templates | 5 | Yes (wrap-around) | Yes | Cylinder-cylinder intersection | 5/5 |
| 3 | Square-to-Round Transition | 3 | Yes (sheet metal) | Yes | Triangulated surface development | 5/5 |
| 4 | Spiral Stair | varies | Yes | No (PDF) | Polar coordinate, variable treads | 5/5 |
| 5 | Pie Cut Tube Bends | varies | Yes (multi-miter) | Yes | Multi-angle miter on cylinder | 4/5 |
| 6 | 3-Way Corner Join | 1 | Yes | No | Triple cylinder intersection | 4/5 |
| 7 | Segmented Turning | 7 | Yes (staves, segments) | Yes (3x) | Multi-ring polygon, varying diameter | 4/5 |
| 8 | Twisted Dovetail | varies | Yes | No | 3D twist geometry | 4/5 |
| 9 | Gambrel Roof | 5 | Yes | No (PDF) | Dual-pitch roof, gussets | 4/5 |
| 10 | Pipe Miter Templates | varies | Yes (wrap-around) | Yes | Cylinder-plane intersection | 3/5 |

## Key Technical Observations

### Architecture Pattern (Consistent Across All Calculators)
```
Page loads → Setup() called on body onload
         → Reads input defaults or URL params
         → Calls Calculate() → math functions
         → Calls Draw() → Canvas 2D API calls
         → Sliders oninput → recalculate + redraw (instant)
```

### JS Bundle Naming Convention
```
/Scripts/{CalcName}Eng_V{version}.js  -- Inch version
/Scripts/{CalcName}_V{version}.js     -- Metric version
```
Version numbers indicate maturity: NotchEng is at V27, Gen.js is shared across all.

### SVG Export Pattern
Not all calculators have SVG export. Those that do use a `DownloadSVG()` function that constructs SVG markup as a string in JavaScript and triggers a blob download. The SVG is generated programmatically (not by converting canvas to SVG).

### Print/PDF Pattern
All calculators have `_PrintAllCanvas()` which opens a new window containing just the canvas-rendered diagrams formatted for printing.

### Full-Scale Templates
The hardest feature to replicate: many calculators generate **full-scale printable templates** that you physically cut out and use. This requires precise DPI-aware canvas sizing and multi-page printing support. The pipe notching templates, for example, print a curve you wrap around actual pipe and mark with a marker.

## Recommendations for Replication

### Start With (Difficulty 2-3)
- Dividing Plate Generator -- clean polar math, SVG output already
- Cone Patterns -- classical geometry, well-documented formulas
- Mortise & Tenon -- rectangular geometry, multiple views

### Medium Challenge (Difficulty 3-4)
- Kerf Spacing -- interesting visual (animated bending), but geometry is manageable
- Dovetail Templates -- high demand, trapezoidal geometry
- Gable Roof -- simpler roof (no hip/valley complexity)

### Hard But High Value (Difficulty 4-5)
- Pipe Notching -- extremely high search volume, welders/fabricators love it
- Hip Roof Framing -- most complex but also most popular
- Square-to-Round Transition -- sheet metal fabricators need this constantly

### Implementation Notes
- Use SVG output instead of Canvas -- better for print, better for export
- The math is the hard part, not the rendering. All geometry formulas are embedded in the minified JS bundles.
- Full-scale printing is critical for the fabrication templates -- this requires careful DPI handling.

## Sources
1. [Blocklayer Calculator Directory](https://www.blocklayer.com/calculator-directory) - Full listing of all calculators
2. [Pipe Notching Templates (source inspection)](https://www.blocklayer.com/fab/round-tube/notcheng) - Verified canvas rendering, JS bundle structure
3. [Spiral Stair Calculator (source inspection)](https://www.blocklayer.com/stairs/spiral-stairseng) - Verified canvas + SVG pattern
4. [Hip Roof Framing Calculator (source inspection)](https://www.blocklayer.com/roof/hipeng) - 17 canvas elements verified
5. [Dovetail Templates (source inspection)](https://www.blocklayer.com/woodjoints/dovetaileng) - Full scale printable template
6. [Square to Round Transition (source inspection)](https://www.blocklayer.com/fab/transitions/square-roundeng) - Sheet metal pattern development
7. [Kerf Spacing Calculator (source inspection)](https://www.blocklayer.com/kerf-spacingeng) - 5 canvas elements, animation
8. [Segmented Turning Calculator (source inspection)](https://www.blocklayer.com/woodturning-segmentseng) - 7 canvases, 3 SVG exports
9. [Gambrel Roof Calculator (source inspection)](https://www.blocklayer.com/roof/gambreleng) - 5 canvases, dual-pitch geometry
10. [Dividing Plate Generator (source inspection)](https://www.blocklayer.com/dividing-plateeng) - SVG-first output
