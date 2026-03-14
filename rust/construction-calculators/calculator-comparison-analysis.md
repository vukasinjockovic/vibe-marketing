# Construction Calculator Comparison Analysis
## OmniCalculator vs InchCalculator vs Blocklayer

**Generated:** 2026-03-07
**Methodology:** Web scraping + search analysis of all three calculator directories
**Scope:** Non-cost/non-price calculators only (material quantity, measurement, engineering)

---

## Table of Contents

1. [Full Calculator Lists by Site](#1-full-calculator-lists-by-site)
2. [Overlap Matrix](#2-overlap-matrix)
3. [Blocklayer Unique Value](#3-blocklayer-unique-value)
4. [Reverse Engineering Feasibility](#4-reverse-engineering-feasibility)
5. [Priority Ranking](#5-priority-ranking)
6. [Total Counts](#6-total-counts)
7. [Can We Build All of Them?](#7-can-we-build-all-of-them)

---

## 1. Full Calculator Lists by Site

### 1A. OmniCalculator Construction (omnicalculator.com/construction)

**Total non-cost calculators found: ~75**

#### Concrete & Masonry

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 1 | Concrete Slab Calculator | /concrete-slab | L, W, depth | Cubic yards, bags needed | Simple (L×W×D) |
| 2 | Concrete Block Calculator | /concrete-block | Wall L, W, block size | Block count, mortar needed | Simple (area/block area) |
| 3 | Concrete Column Calculator | /concrete-column | Diameter/width, height, count | Cubic yards, bags | Simple (pi×r²×h) |
| 4 | Concrete Cylinder Calculator | /concrete-cylinder | Diameter, height | Volume, weight | Simple (pi×r²×h × density) |
| 5 | Concrete Stairs Calculator | /concrete-stairs | Rise, run, width, steps | Concrete volume | Moderate (step geometry) |
| 6 | Concrete Weight Calculator | /concrete-weight | Volume, mix type | Weight in lbs/kg | Lookup (density table) |
| 7 | Sonotube Calculator | /sonotube | Diameter, height, count | Concrete volume, bags | Simple (pi×r²×h) |
| 8 | Cement Calculator | /cement | Project type, dimensions | Bags of cement, sand, aggregate | Lookup (mix ratios) |
| 9 | Brick Calculator | /brick | Wall area, brick size, mortar joint | Brick count, mortar volume | Simple (area/unit) |
| 10 | Retaining Wall Calculator | /retaining-wall | Height, length, block size | Block count, backfill, gravel | Simple + lookup |
| 11 | Rebar Calculator | /rebar | Slab dimensions, spacing | Rebar count, total length, weight | Simple (grid spacing) |

#### Roofing

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 12 | Roofing Calculator | /roofing | Roof area, pitch | Squares, bundles, felt rolls | Moderate (pitch factor) |
| 13 | Roof Pitch Calculator | /roof-pitch | Rise, run (or angle) | Pitch ratio, degrees, slope % | Trig (arctan) |
| 14 | Roof Truss Calculator | /roof-truss | Span, pitch, spacing | Rafter length, truss count | Trig (pythagorean) |
| 15 | Rafter Length Calculator | /rafter-length | Span, pitch, overhang | Rafter length, ridge height | Trig (cos/sin) |
| 16 | Roof Shingle Calculator | /roof-shingle | Roof area, pitch | Bundles, squares | Simple + pitch factor |
| 17 | Gambrel Roof Calculator | /gambrel-roof | Width, upper/lower pitch | All rafter dims, angles | Moderate trig |
| 18 | Birdsmouth Cut Calculator | /birdsmouth | Rafter width, pitch | Seat cut, plumb cut, HAP | Trig (seat/plumb angles) |

#### Framing & Carpentry

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 19 | Framing Calculator | /framing | Wall length, stud spacing | Stud count, plate length | Simple (length/spacing + 1) |
| 20 | Board Foot Calculator | /board-foot | Thickness, width, length | Board feet | Simple (T×W×L/144) |
| 21 | Lumber Calculator | /lumber | Dimensions, board count | Total board feet, cost | Simple |
| 22 | Lumber Weight Calculator | /lumber-weight | Species, dimensions | Weight | Lookup (species density) |
| 23 | Plywood Calculator | /plywood | Area, sheet size | Sheet count | Simple (area/sheet area) |
| 24 | Stair Calculator | /stairs | Total rise, ideal rise/run | Steps, stringer length, angles | Moderate (geometry) |
| 25 | Spiral Staircase Calculator | /spiral-staircase | Height, radius, rotation | Tread dims, stringer length | Complex (helix geometry) |
| 26 | Baluster Calculator | /baluster | Railing length, spacing | Baluster count | Simple (length/spacing) |
| 27 | Decking Calculator | /decking | Deck L, W, board width | Board count, fasteners | Simple (area/board) |
| 28 | Wainscoting Calculator | /wainscoting | Wall dimensions, panel size | Panel count, rail length | Simple |
| 29 | Board and Batten Calculator | /board-and-batten | Wall dimensions, board/batten width | Board count, batten count | Simple (spacing) |
| 30 | Miter Angle Calculator | /miter-angle | Corner angle, sides | Miter saw angle | Simple (angle/2) |

#### Siding

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 31 | Siding Calculator | /siding | Wall area, openings | Squares of siding | Simple (area - openings) |
| 32 | Vinyl Siding Calculator | /vinyl-siding | Wall dimensions, panel size | Panel count, trim | Simple (area/panel) |

#### Interior Finishing

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 33 | Drywall Calculator | /drywall | Room dimensions | Sheet count, tape, compound | Simple (area/sheet) |
| 34 | Tile Calculator | /tile | Area, tile size, gap width | Tile count, grout | Simple (area/tile) + waste |
| 35 | Wallpaper Calculator | /wallpaper | Room dimensions, roll size | Roll count | Simple (area/roll coverage) |
| 36 | Flooring Calculator | /flooring | Room dimensions | Sq ft, material amount | Simple (L×W) |
| 37 | Carpet Calculator | /carpet | Room dimensions | Sq ft, sq yards | Simple (L×W conversion) |
| 38 | Stair Carpet Calculator | /stair-carpet | Steps, width, rise/run | Carpet needed | Moderate (step wrapping) |
| 39 | Grout Calculator | /grout | Area, tile size, gap width/depth | Grout volume, bags | Moderate (gap geometry) |
| 40 | Thinset Calculator | /thinset | Area, tile size | Thinset volume, bags | Lookup (coverage rates) |
| 41 | Epoxy Calculator | /epoxy | Area, thickness | Resin volume (2:1 ratio) | Simple (area × depth) |
| 42 | Sealant Calculator | /sealant | Gap width, depth, length | Sealant volume, tubes | Simple (W×D×L) |

#### Landscaping & Materials

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 43 | Gravel Calculator | /gravel | Area, depth | Cubic yards, tons | Simple + density lookup |
| 44 | Sand Calculator | /sand | Area, depth | Cubic yards, tons | Simple + density lookup |
| 45 | Crushed Stone Calculator | /crushed-stone | Area, depth | Volume, weight | Simple + density lookup |
| 46 | Limestone Calculator | /limestone | Area, depth | Volume, weight | Simple + density lookup |
| 47 | Tonnage Calculator | /tonnage | Volume, material | Weight in tons | Lookup (density table) |
| 48 | Asphalt Calculator | /asphalt | Area, thickness | Tons of asphalt | Simple + density lookup |
| 49 | Paver Calculator | /paver | Area, paver size | Paver count, sand base | Simple (area/paver) |
| 50 | French Drain Calculator | /french-drain | Length, width, depth | Gravel volume, pipe length | Simple (trench volume) |
| 51 | Fire Glass Calculator | /fire-glass | Firepit dimensions | Glass quantity | Simple (volume × fill) |
| 52 | Pool Calculator | /pool | Shape, dimensions | Gallons, volume | Shape formulas |
| 53 | Pond Calculator | /pond | Shape, dimensions | Volume, liner size | Shape formulas |

#### Weight Calculators

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 54 | Metal Weight Calculator | /metal-weight | Shape, dimensions, metal type | Weight | Lookup (metal densities) |
| 55 | Steel Weight Calculator | /steel-weight | Shape, dimensions | Weight | Shape × density |
| 56 | Steel Plate Weight Calculator | /steel-plate-weight | L, W, thickness | Weight | Simple (L×W×T × density) |
| 57 | Aluminum Weight Calculator | /aluminum-weight | Shape, dimensions | Weight | Shape × density |
| 58 | Pipe Weight Calculator | /pipe-weight | OD, wall thickness, length, material | Weight | Annular area × length × density |
| 59 | Plate Weight Calculator | /plate-weight | Area, thickness, density | Weight | Simple (A×T×D) |
| 60 | Glass Weight Calculator | /glass-weight | Area, thickness, glass type | Weight | Lookup (glass densities) |
| 61 | Stone Weight Calculator | /stone | Dimensions | Volume, weight | Shape × density |
| 62 | Concrete Weight Calculator | /concrete-weight | Volume | Weight | Volume × density |
| 63 | Log Weight Calculator | /log-weight | Diameter, length, species | Weight | Cylinder × green density |

#### HVAC / Airflow

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 64 | Air Changes per Hour (ACH) | /air-changes-per-hour | Room volume, ACH rate | CFM needed | Simple (V×ACH/60) |
| 65 | CFM Calculator | /cfm | Room dimensions, ACH | Cubic feet per minute | Simple (area×height×ACH/60) |
| 66 | AC Tonnage Calculator | /ac-tonnage | Room size, climate, insulation | Tonnage required | Moderate (Manual J approx) |

#### Measurement & Conversion

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 67 | Square Footage Calculator | /square-footage | Shape, dimensions | Square feet | Shape formulas |
| 68 | Square Meter Calculator | /square-meter | Shape, dimensions | Square meters | Shape formulas |
| 69 | Square Yards Calculator | /square-yards | Dimensions | Square yards | Simple (sqft/9) |
| 70 | Cubic Yard Calculator | /cubic-yard | L, W, D | Cubic yards | Simple (L×W×D/27) |
| 71 | Sq Ft to Cubic Yards | /ft2-yd3 | Sq ft, depth | Cubic yards | Simple (sqft×depth/27) |
| 72 | Gallons per Sq Ft | /gallons-per-square-foot | Gallons, area | Gal/sqft ratio | Simple division |
| 73 | Size to Weight (Box) | /size-to-weight | L, W, H, density | Weight | Simple (L×W×H×D) |
| 74 | Road Base Calculator | /road-base | Area, depth | Volume, tonnage | Simple + density |

---

### 1B. InchCalculator Construction (inchcalculator.com/construction-calculators/)

**Total non-cost calculators found: ~55**

#### Concrete & Masonry

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 1 | Concrete Calculator | /concrete-calculator/ | Shape, dimensions | Cubic yards, bags | Shape formulas |
| 2 | Concrete Block Calculator | /concrete-block-calculator/ | Wall L, H, block size | Block count, mortar | Simple (area/block) |
| 3 | Concrete Footing Calculator | /concrete-footing-calculator/ | Footing dims, count | Cubic yards, bags | Simple volume |
| 4 | Post Hole Concrete Calculator | /post-hole-concrete-calculator/ | Hole diameter, depth, count | Cubic yards, bags | Cylinder volume |
| 5 | Brick Calculator | /brick-calculator/ | Wall area, brick size, joint | Brick count, mortar bags | Simple + lookup |
| 6 | Retaining Wall Calculator | /retaining-wall-calculator/ | Height, length, block dims | Block count, cap blocks, backfill | Simple + lookup |

#### Roofing

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 7 | Roofing Material Calculator | /roofing-calculator/ | Roof area, pitch | Squares, bundles, felt | Moderate (pitch factor) |
| 8 | Metal Roofing Calculator | /metal-roofing-material-calculator/ | Roof area, panel size | Panel count, trim | Simple + pitch |
| 9 | Roof Sheathing Calculator | /roof-sheathing-calculator/ | Roof L, W, pitch | Plywood sheets | Simple + pitch factor |
| 10 | Rafter Length Calculator | /rafter-length-calculator/ | Span, pitch, overhang | Rafter length | Trig (cos/sin) |

#### Siding

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 11 | Siding Calculator | /siding-squares-calculator/ | Wall area, openings | Squares of siding | Simple (area - openings) |
| 12 | Vinyl Siding Calculator | /vinyl-siding-calculator/ | Wall dimensions, openings | Panel count, trim pieces | Simple (area/panel) |

#### Carpentry & Framing

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 13 | Framing Calculator | /framing-calculator/ | Wall length, OC spacing | Stud count, plates | Simple (L/spacing+1) |
| 14 | Board Foot Calculator | /board-footage-calculator/ | T, W, L | Board feet | Simple (T×W×L/144) |
| 15 | Lumber Weight Calculator | /lumber-weight-calculator/ | Species, dimensions | Weight | Lookup (species density) |
| 16 | Plywood Calculator | /plywood-calculator/ | Area to cover | Sheet count | Simple (area/32) |
| 17 | Trim and Molding Calculator | /trim-moulding-calculator/ | Room perimeter, openings | Linear feet of trim | Simple (perimeter - openings) |
| 18 | Wainscoting Layout Calculator | /wainscoting-layout-calculator/ | Wall dimensions, panel size | Panel count, rail length | Simple spacing |
| 19 | Board and Batten Calculator | /board-and-batten-layout-calculator/ | Wall dimensions, board/batten width | Board/batten count, spacing | Simple spacing |
| 20 | Deck Board Calculator | /deck-board-calculator/ | Deck area, board width | Board count | Simple (area/board) |
| 21 | Deck Stain Calculator | /deck-stain-calculator/ | Deck area | Gallons of stain | Simple (area/coverage) |

#### Fence

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 22 | Fence Calculator (Wood) | /fence-calculator/ | Length, height, post spacing | Posts, rails, pickets | Simple (L/spacing) |
| 23 | Vinyl Fence Calculator | /vinyl-fence-calculator/ | Length, panel width | Panels, posts, caps | Simple (L/panel) |
| 24 | Fence Stain Calculator | /fence-stain-calculator/ | Fence area | Gallons of stain | Simple (area/coverage) |

#### Flooring & Interior

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 25 | Flooring Calculator | /flooring-calculator/ | Room dimensions | Sq ft, material amount | Simple (L×W) |
| 26 | Tile Calculator | /tile-calculator/ | Area, tile size | Tile count + waste | Simple (area/tile + %) |
| 27 | Carpet Calculator | /carpet-calculator/ | Room dimensions | Sq ft, sq yards | Simple (L×W) |
| 28 | Drywall Calculator | /drywall-calculator/ | Room dimensions | Sheets, screws, tape, compound | Simple (area/sheet) |
| 29 | Paint Calculator | /paint-calculator/ | Room dimensions, doors/windows | Gallons needed | Simple (net area/coverage) |

#### Landscaping

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 30 | Gravel Calculator | /gravel-calculator/ | Area, depth | Cubic yards, tons | Simple + density |
| 31 | Sand Calculator | /sand-calculator/ | Area, depth | Cubic yards, tons | Simple + density |
| 32 | Mulch Calculator | /mulch-calculator/ | Area, depth | Cubic yards, bags | Simple (volume) |
| 33 | Soil/Topsoil Calculator | /soil-calculator/ | Area, depth | Cubic yards | Simple (volume) |
| 34 | Stone Calculator | /stone-calculator/ | Area, depth | Cubic yards, tons | Simple + density |
| 35 | Paver Calculator | /paver-calculator/ | Area, paver size | Paver count, sand/gravel base | Simple (area/paver) |
| 36 | Paver Base Calculator | /paver-base-calculator/ | Area, base depth | Gravel cubic yards, sand | Simple (volume) |
| 37 | Asphalt Calculator | /asphalt-calculator/ | Area, thickness | Tons of asphalt | Simple + density |

#### Measurement & Reference

| # | Calculator | URL Path | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 38 | Square Footage Calculator | (various pages) | Dimensions | Sq ft | Shape formulas |
| 39 | Actual Dimensional Lumber Sizes | (reference page) | Nominal size | Actual size | Lookup table |

---

### 1C. Blocklayer (blocklayer.com/calculator-directory)

**Total non-cost calculators found: ~65+ (each in metric AND inch = 130+ pages)**

> Note: Blocklayer offers EVERY calculator in both Metric and Imperial (Inch) versions as separate pages. Counts below are for unique calculators (not versions).

#### Stairs

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 1 | Stair Stringer Calculator | /stairs/straight | Total rise, run, width | Rise/run per step, stringer length, headroom, floor opening | Moderate (geometry + headroom) |
| 2 | Circular/Spiral Stair Calculator | /stairs/spiral-stairs | Height, inner/outer radius, rotation | Tread dimensions, stringer curves, plan view | Complex (helix/arc geometry) |
| 3 | Steel Spine Stair Calculator | /stairs/steel-spine | Height, radius, bracket dims | Bracket templates, stringer geometry | Complex (3D bracket geometry) |

#### Roof Framing

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 4 | Hip Roof Framing Calculator | /roof/hip | Span, pitch, eave overhang | All rafter dims, hip/jack rafters, cutting templates, rafter placement | Complex (3D roof geometry + cutting angles) |
| 5 | Gable Roof Framing Calculator | /roof/gable | Span, pitch, overhang | Rafter dims, placement, cut angles | Moderate trig |
| 6 | Skillion/Lean-to Roof Calculator | /roof/skillion | Span, pitch | Rafter dims, cut angles | Moderate trig |
| 7 | Gambrel Roof Calculator | /roof/gambrel | Width, upper/lower pitch | All rafter dims, angles | Moderate trig |
| 8 | Saltbox Roof Calculator | /roof/saltbox | Width, front/back pitch | Rafter dims, ridge height | Moderate trig |
| 9 | Rafter Calculator | /roof/rafter | Pitch, span, overhang | Rafter length, birdsmouth cut, plumb cut, tail cut | Trig (all cut angles) |
| 10 | Rafter Birdsmouth Cutting Templates | /roof/rafter-template | Rafter dimensions | Printable full-scale cutting templates | Template generation |
| 11 | Rise in Run / Pitch / Angle | /riserun | Rise, run | Pitch, angle, grade % | Trig (arctan) |
| 12 | Pitch to Angle Converter | /pitchangle | Pitch ratio | Degrees, radians | Trig |
| 13 | Roof Pitch Measurement Tool | /roof-pitch | Physical measurement | Pitch, angle | Trig |

#### Carpentry & Woodwork

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 14 | Wall Framing Calculator | /wallframing | Wall L, H, stud spacing | Stud placement, top/bottom plate | Simple (spacing) |
| 15 | Wall Framing for Openings | /wallframing-openings | Opening size, wall dims | Jack/king studs, header, cripple studs | Moderate (framing rules) |
| 16 | Centres/Spacing Calculator | /centers-spacing | Length, member count or spacing | Exact spacing, end member fit | Simple (division) |
| 17 | Centres and Lengths Raking Wall | /centers-angle | Gable wall dims, spacing | Stud lengths at angle, spacing | Trig (angle) |
| 18 | Baluster Spacing Calculator | /baluster-spacing | Rail length, baluster width, max gap | Baluster count, exact spacing | Simple (spacing) |
| 19 | Dovetail Template Generator | /dovetails | Board width, pin/tail ratio | Full-scale printable dovetail template | Template (ratio-based) |
| 20 | Double Twisted Dovetail Template | /dovetail-twisted | Board width, twist angle | Printable twisted dovetail template | Complex (3D geometry) |
| 21 | Mortise and Tenon Calculator | /woodjoints/mortise-tenon | Member dims, tenon size | Visual joint diagram, dimensions | Simple (proportional) |
| 22 | Kerf Spacing Calculator | /kerf-spacing | Bend radius, board thickness, kerf width | Kerf count, spacing | Moderate (bend math) |
| 23 | Crown Molding Angle Chart | /crown-molding | Spring angle, corner angle | Miter angle, bevel angle | Trig (compound angles) |
| 24 | Compound Miter Angle Calculator | /compoundmiter | Corner angle, tilt angle | Miter angle, bevel angle | Trig (compound angles) |
| 25 | Diagonal/Cross Bracing Calculator | /diagonal-bracing | Frame dimensions | Brace length, miter angles | Trig (pythagorean + angles) |
| 26 | Miter Angle Calculator | /miter-angles | Number of sides or angle | Miter saw angle | Simple (180/n) |

#### Decks

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 27 | Deck Layout Calculator | /deckcalculator | Deck L, W, joist spacing | Joist placement, beam layout, post positions | Moderate (structural layout) |
| 28 | Deck Floor Board Spacing | /deckboards | Deck width, board width, count/gap | Board spacing, gap size, board count | Simple (spacing) |

#### Fencing

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 29 | Fence Posts & Rails Calculator | /fencing | Length, post spacing, rail count | Post count, rail lengths, material | Simple (spacing) |
| 30 | Fence Panel Calculator | /fence-panels | Length, panel width | Panel count, post count | Simple (L/panel) |
| 31 | Arched Fence Paling Calculator | /fence/picket-arch | Fence dims, arch height | Paling lengths (varying), spacing | Moderate (arc geometry) |
| 32 | Glass Balustrade Calculator | /glass-balustrade | Length, panel size, gap | Panel count, post positions | Simple (spacing) |

#### Concrete

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 33 | Multi-Sided Concrete Slab Calculator | /concrete/volume | Slab sides, depth, footings | Volume, rebar, steel mesh | Moderate (polygon area) |
| 34 | Premix Concrete Bags Calculator | /concrete/premix | Volume needed, bag size | Bag count | Simple (volume/bag yield) |
| 35 | Rebar Spacing & Layout | /concrete/rebar-slab | Slab dims, rebar spacing | Rebar count, placement, weight | Simple (grid spacing) |
| 36 | Concrete Column/Footing Calculator | /concrete/columns | Column/footing dims | Volume per column, total volume | Cylinder/box volume |
| 37 | Concrete Cutting Calculator | /concrete/cutting | Block/slab dims, cut size | Number of cuts, piece weights | Simple (division) |
| 38 | Concrete Core Drilling (Angled) | /concrete/core-drilling | Floor thickness, drill angle, diameter | Entry/exit positions, drill depth | Trig (angle through slab) |
| 39 | Block Corner Miter Calculator | /concrete/block-miter | Block size, corner angle | Miter cut dimensions | Trig |

#### Metalwork & Fabrication

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 40 | Tube/Pipe Notching Templates | /pipe-notch | Tube OD, angle, intersect tube OD | Printable wrap-around cutting template | Complex (3D intersection) |
| 41 | Tube/Pipe Miter Templates | /pipe-miter | Tube OD, miter angle | Printable wrap-around cutting template | Moderate (unrolled cylinder) |
| 42 | Pie Cut Tube Bending | /fab/round-tube/pie-cuts | Tube OD, bend radius, angle | Pie cut dimensions, template | Complex (segmented bend) |
| 43 | Tube Wrap Perforator | /fab/round-tube/wrap | Tube OD, hole pattern | Printable hole layout template | Moderate (unrolled cylinder) |
| 44 | Round to Square Transition | /fab/transitions/round-square | Circle diameter, square dims | Printable transition template | Complex (surface development) |

#### Geometry & Trigonometry

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 45 | Polygon Calculator | /trig/polygons | Number of sides, dimension | All dimensions, angles, area | Trig (polygon formulas) |
| 46 | Circle Calculator | /trig/circles | Radius/diameter/circumference | All circle properties | Pi formulas |
| 47 | Circle Chord Calculator | /trig/circle-chords | Radius, chord length or angle | Arc, sagitta, sector area | Trig |
| 48 | Isosceles Triangle Calculator | /trig/angles | Side lengths or angles | All angles, sides, area | Trig |
| 49 | Arc Templates with Vernier | /arc-templates | Radius, arc angle | Printable full-scale arc template | Template generation |
| 50 | Polygon Templates | /polygon-templates | Sides, size | Printable polygon template | Template generation |
| 51 | Ellipse/Oval Layout Calculator | /oval | Major/minor axis | Set-out points, area | Ellipse formulas |
| 52 | Golden Ratio Calculator | /goldenratio | One dimension | Matching golden ratio dimensions | Phi constant (1.618) |
| 53 | Square/Rectangle Set-Out | /squarerectangle | Dimensions | Diagonal check, area | Pythagorean |
| 54 | Pyramid Calculator | /pyramid | Base, height | Slant height, face area, volume | 3D geometry |
| 55 | Floor Area (Multi-Sided) | /floor-area | Irregular polygon coords | Area | Shoelace formula |
| 56 | Column Design Calculator | /column-design | Load, material | Column dimensions | Engineering formulas |
| 57 | Diminishing Lengths at Angle | /diminishing | Spacing, angle | Progressive lengths at rake | Trig |

#### Gazebo & Structures

| # | Calculator | URL Slug | Inputs | Outputs | Math Type |
|---|-----------|----------|--------|---------|-----------|
| 58 | Gazebo Calculator | /gazebos/gazebo | Sides, span | Rafter layout, center bracket, framing plan | Complex (polygon + roof) |
| 59 | Gazebo Center Bracket Templates | /gazebos/bracket | Number of rafters, pitch | Full-scale bracket cutting template | Template generation |

---

## 2. Overlap Matrix

### Calculators Present on All 3 Sites

| Calculator Type | OmniCalc | InchCalc | Blocklayer |
|----------------|:--------:|:--------:|:----------:|
| Concrete Volume/Slab | Yes | Yes | Yes |
| Concrete Block/CMU | Yes | Yes | Yes (as part of multi-sided) |
| Brick | Yes | Yes | -- |
| Rebar/Reinforcement | Yes | -- | Yes |
| Retaining Wall | Yes | Yes | -- |
| Roofing Material | Yes | Yes | -- |
| Rafter Length | Yes | Yes | Yes |
| Roof Pitch | Yes | -- | Yes |
| Stair Calculator | Yes | -- | Yes |
| Framing/Stud | Yes | Yes | Yes |
| Baluster Spacing | Yes | -- | Yes |
| Board Foot | Yes | Yes | -- |
| Decking | Yes | Yes | Yes |
| Fence | -- | Yes | Yes |
| Drywall | Yes | Yes | -- |
| Tile | Yes | Yes | -- |
| Paint | Yes | Yes | -- |
| Gravel | Yes | Yes | -- |
| Sand | Yes | Yes | -- |
| Paver | Yes | Yes | -- |
| Siding | Yes | Yes | -- |
| Board & Batten | Yes | Yes | Yes (as centres/spacing) |
| Wainscoting | Yes | Yes | -- |
| Miter Angle | Yes | -- | Yes |
| Square Footage/Area | Yes | Yes | Yes (floor area) |

### On 2 of 3 Sites

| Calculator Type | Sites |
|----------------|-------|
| Concrete Footing/Column | Omni + Blocklayer |
| Gambrel Roof | Omni + Blocklayer |
| Lumber Weight | Omni + InchCalc |
| Plywood | Omni + InchCalc |
| Carpet | Omni + InchCalc |
| Flooring (general) | Omni + InchCalc |
| Mulch | Omni + InchCalc |
| Topsoil/Soil | Omni + InchCalc |
| Asphalt | Omni + InchCalc |
| Vinyl Siding | Omni + InchCalc |
| Vinyl Fence | -- + InchCalc + (Blocklayer has panel calc) |
| Metal Roofing | Omni + InchCalc |
| Roof Sheathing | Omni (as plywood) + InchCalc |
| Concrete Stairs | Omni + (Blocklayer in stair calc) |
| Deck Board Spacing | InchCalc + Blocklayer |
| Crown Molding Angles | Omni (miter) + Blocklayer |
| Gable Roof | Omni (as rafter) + Blocklayer |
| Skillion/Lean-to Roof | -- + Blocklayer only |

### Unique to ONE Site

#### Unique to OmniCalculator (~20)
- Spiral Staircase Calculator
- Stair Carpet Calculator
- Pool Volume Calculator
- Pond Calculator
- French Drain Calculator
- Fire Glass Calculator
- Grout Calculator
- Thinset Calculator
- Epoxy Calculator
- Sealant Calculator
- Wallpaper Calculator
- Sonotube Calculator
- Air Changes per Hour (ACH)
- CFM Calculator
- AC Tonnage Calculator
- Tonnage Calculator (material weight)
- Road Base Calculator
- Glass Weight Calculator
- Log Weight Calculator
- Gallons per Sq Ft Converter
- Size to Weight (Rectangular Box)

#### Unique to InchCalculator (~8)
- Post Hole Concrete Calculator
- Roof Sheathing Calculator (dedicated)
- Deck Stain Calculator
- Fence Stain Calculator
- Trim and Molding Calculator (baseboard, chair rail, crown, casing)
- Paver Base Calculator (separate from paver)
- Stone Calculator (dedicated)
- Actual Dimensional Lumber Sizes (reference)

#### Unique to Blocklayer (~25+)
- Hip Roof Framing (full cutting templates + rafter placement)
- Saltbox Roof Calculator
- Circular/Spiral Stair Calculator (with full geometry)
- Steel Spine Stair Calculator
- Dovetail Template Generator
- Double Twisted Dovetail Template
- Mortise and Tenon Calculator
- Kerf Spacing Calculator (wood bending)
- Compound Miter Angle Calculator
- Diagonal/Cross Bracing Calculator
- Wall Framing for Openings (jack/king studs)
- Centres and Lengths at Raking Angle
- Arched Fence Paling Calculator
- Glass Balustrade Calculator
- Concrete Core Drilling (angled)
- Concrete Cutting Calculator
- Block Corner Miter Calculator
- Multi-sided Concrete Slab (with footings/thickenings)
- All metalwork calculators (tube notching, miter, pie cuts, transitions, perforator)
- Gazebo Calculator + center bracket templates
- Arc Templates with Vernier
- Polygon Templates (printable)
- Ellipse/Oval Layout Calculator
- Pyramid Calculator
- Golden Ratio Calculator
- Column Design Calculator
- Diminishing Lengths at Angle

---

## 3. Blocklayer Unique Value

Blocklayer occupies a fundamentally different niche than OmniCalculator and InchCalculator. Here is what makes it unique:

### 3.1 Tradesman-Specific, Not Homeowner-Oriented

| Aspect | OmniCalc / InchCalc | Blocklayer |
|--------|---------------------|------------|
| **Target user** | Homeowner / DIYer | Builder / Carpenter / Fabricator |
| **Question answered** | "How much material do I need to buy?" | "How do I cut/build this precisely?" |
| **Output style** | Number + cost estimate | Visual diagram + cutting template |
| **Math complexity** | Mostly arithmetic | Trigonometry + 3D geometry |
| **Printable templates** | None | Full-scale templates for wrapping, cutting |

### 3.2 Categories Only Blocklayer Covers

1. **Printable Full-Scale Cutting Templates** -- This is Blocklayer's killer feature. Wrap a template around a tube to mark a notch. Print a dovetail template at 1:1 scale. Print rafter birdsmouth templates. No other site does this.

2. **Metalwork & Fabrication** -- Tube notching, tube miter, pie-cut bending, round-to-square transitions. These serve welders, metalworkers, and fabricators. Neither OmniCalc nor InchCalc touches this space.

3. **Advanced Woodworking Joints** -- Dovetails (including twisted), mortise and tenon. These are precision craft calculators.

4. **Full Roof Framing Plans** -- Blocklayer does not just calculate rafter length -- it produces complete framing plans with every rafter position, every cut angle, and birdsmouth templates for hip roofs, gable roofs, saltbox roofs, etc.

5. **Gazebo Construction** -- Full polygon-based gazebo framing with center bracket templates. Unique.

6. **Geometric Construction Tools** -- Polygon set-out, ellipse layout, arc templates, diminishing lengths. These are physical construction tools for layout work on job sites.

7. **Angled Concrete Core Drilling** -- Calculates entry/exit points when drilling through a concrete slab at an angle. Very niche, very valuable for plumbers/electricians.

### 3.3 Key Differentiator: "Geometric Only"

Blocklayer explicitly states all calculators are "geometric only" -- meaning they compute shapes, angles, and dimensions. They never estimate material quantities or costs. This is the inverse of OmniCalc/InchCalc, which are primarily material quantity estimators.

---

## 4. Reverse Engineering Feasibility

### Difficulty Rating Scale

| Rating | Description | Example |
|--------|-------------|---------|
| **1** | Simple arithmetic (L×W×D, area, volume) | Concrete slab, mulch, gravel |
| **2** | Simple with lookup tables (densities, coverage rates) | Sand tonnage, paint coverage, lumber weight |
| **3** | Trigonometry / moderate geometry | Roof pitch, rafter length, stair stringer |
| **4** | Complex geometry / 3D calculations + diagrams | Hip roof framing, spiral stairs, tube notching |
| **5** | Engineering formulas + interactive diagrams | AC tonnage (Manual J), structural column design |

### Full Feasibility Assessment

#### Difficulty 1 -- Simple Arithmetic (Easy to replicate, Alpine.js)

| Calculator | Formula | Notes |
|-----------|---------|-------|
| Square Footage | L × W (+ shape variants) | Support rectangle, triangle, circle, trapezoid |
| Cubic Yard | L × W × D / 27 | Add unit conversion |
| Concrete Slab | L × W × D = cu.yd | Add bags conversion |
| Concrete Block | (wall area - openings) / block face area | Standard block = 1.125 sq ft |
| Brick | wall area × bricks/sqft | Lookup: 6.75 bricks/sqft (modular) |
| Board Foot | T × W × L / 144 | Standard lumber formula |
| Drywall | (wall area + ceiling area) / sheet size | Standard sheet = 32 sq ft |
| Plywood | Area / sheet size | Standard = 32 sq ft |
| Framing/Studs | (wall length / spacing) + 1 | Add doubles for corners/openings |
| Mulch | Area × depth (convert to cu.yd) | |
| Topsoil | Area × depth (convert to cu.yd) | |
| Flooring | L × W + waste % | |
| Carpet | L × W (convert to sq.yd) | |
| Tile | Area / tile size + waste % | |
| Paint | Net wall area / coverage rate | 350 sqft/gal typical |
| Wallpaper | Net wall area / roll coverage | |
| Baluster | (railing length - baluster width) / (spacing + baluster width) | |
| Fence (linear) | Length / panel width or post spacing | |
| Siding | Wall area / square (100 sqft) | |
| Deck Board | Area / board width / board length | |
| Paver | Area / paver face area | |
| Grout | Joint volume = (L+W)×D×W_joint / (L×W) per tile | |
| Sealant | Gap width × depth × length | |
| Epoxy | Area × thickness | |
| Post Hole Concrete | pi × r² × depth × count | |
| Sonotube | pi × r² × height × count | |
| Sq Ft to Cu.Yd | sqft × depth / 27 | |
| Board & Batten | wall width / (board + batten width) | |

**Count: ~30 calculators. All buildable with basic Alpine.js in 1-2 hours each.**

#### Difficulty 2 -- Arithmetic + Lookup Tables

| Calculator | Formula | Data Needed |
|-----------|---------|-------------|
| Gravel (in tons) | Volume × density | Density table: gravel = 1.4 tons/cu.yd |
| Sand (in tons) | Volume × density | Sand = 1.35 tons/cu.yd |
| Crushed Stone | Volume × density | ~1.4 tons/cu.yd |
| Limestone | Volume × density | ~1.5 tons/cu.yd |
| Asphalt | Volume × density | 145 lbs/cu.ft |
| Tonnage | Volume × material density | Multi-material density table |
| Lumber Weight | Board feet × species density | Density table per wood species |
| Metal Weight | Volume × metal density | Steel=490, Aluminum=169 lbs/cu.ft |
| Steel Plate Weight | L × W × T × 490 lbs/cu.ft | |
| Pipe Weight | Annular area × L × density | Need OD/ID/wall tables for common pipes |
| Glass Weight | Area × thickness × 156 lbs/cu.ft | |
| Concrete Weight | Volume × 150 lbs/cu.ft | Variants: lightweight, heavyweight |
| Log Weight | pi × r² × L × green density | Green density per species |
| Stone Weight | Volume × density | Granite=168, Marble=169 lbs/cu.ft |
| Cement (mix ratios) | Volume × ratio | 1:2:3 or 1:2:4 mix ratios |
| Mortar | Joint area × mortar per unit | Lookup per brick type |
| Thinset | Area × coverage rate per tile size | Coverage table per trowel notch |
| Retaining Wall | Block count + backfill + drainage gravel | Block dims, backfill ratios |
| Concrete Bags | Volume / yield per bag | 60lb=0.45cuft, 80lb=0.6cuft |
| Rebar (weight) | Length × weight/ft | #3=0.376, #4=0.668, #5=1.043 lbs/ft |
| Roof Shingles | Roof area × pitch factor / 100 (squares) | Pitch factor table |
| Metal Roofing | Roof area × pitch factor / panel area | Panel size data |
| Concrete Stairs | Σ(step volume) = width × Σ(rise × run) | Stepped volume formula |
| AC Tonnage | Room sqft × factors | Climate zone, insulation, windows |

**Count: ~24 calculators. Need embedded lookup tables (JSON data). Still simple code, 2-4 hours each.**

#### Difficulty 3 -- Trigonometry / Moderate Geometry

| Calculator | Formula | Visualization Needed |
|-----------|---------|---------------------|
| Roof Pitch | arctan(rise/run) | Pitch triangle diagram |
| Rafter Length | run / cos(pitch_angle) + overhang | Rafter diagram |
| Roof Truss | Pythagorean + count | Truss shape diagram |
| Stair Stringer | √(total_rise² + total_run²) | Stringer profile diagram |
| Gambrel Roof | Upper + lower pitch geometry | Roof profile diagram |
| Birdsmouth Cut | seat = rafter_width × cos(pitch), plumb = rafter_width × sin(pitch) | Cut detail diagram |
| Miter Angle | angle/2 for simple, trig for compound | Angle diagram |
| Crown Molding Angles | miter = arctan(sin(spring) × tan(corner/2)), bevel = arcsin(cos(spring) × sin(corner/2)) | Saw setting diagram |
| Spiral Staircase | Helix geometry: arc length, tread angles | Plan view diagram |
| Concrete Core Drilling | exit_offset = thickness × tan(drill_angle) | Cross-section diagram |
| Kerf Spacing | spacing = 2 × thickness × sin(arccos(1 - thickness/radius)) | Bend diagram |
| Circle Chord/Arc | Standard chord/arc formulas | Circle diagram |
| Polygon (N-sided) | Interior angle = (n-2)×180/n, apothem, area | Polygon diagram |
| Ellipse Layout | Pin-and-string method: focus distance = √(a²-b²) | Ellipse diagram |
| Arched Fence Palings | Arc height interpolation per paling position | Fence elevation diagram |

**Count: ~15 calculators. Need SVG/Canvas diagrams. 4-8 hours each. Math is known and documented.**

#### Difficulty 4 -- Complex Geometry + Interactive Diagrams

| Calculator | Formula | Special Requirements |
|-----------|---------|---------------------|
| Hip Roof Framing | 3D hip/jack rafter geometry, compound angles | Full framing plan SVG, cutting template PDFs |
| Saltbox Roof | Asymmetric roof geometry | Framing plan diagram |
| Gable Roof Framing (full) | Complete rafter placement plan | Layout diagram with measurements |
| Deck Layout | Joist spacing, beam placement, post positions | Plan view diagram |
| Gazebo | N-sided polygon roof framing | Plan view + elevation diagram |
| Tube Notching | 3D cylinder intersection → flattened template | Wrap-around printable template |
| Tube Miter | Cylinder cut at angle → flattened template | Wrap-around printable template |
| Pie Cut Bending | Segmented bend geometry | Template with cut lines |
| Round-to-Square Transition | Surface development (sheet metal) | Printable flatten pattern |
| Wall Framing for Openings | Header, jack, king, cripple stud layout | Framing diagram |
| Dovetail Templates | Pin/tail ratio → full-scale template | Printable template |
| Mortise and Tenon | Joint proportions → visual design | Interactive joint diagram |

**Count: ~12 calculators. 8-20 hours each. SVG generation required. Some need PDF template generation.**

#### Difficulty 5 -- Engineering Formulas / External Data

| Calculator | Issue |
|-----------|-------|
| AC Tonnage (Manual J) | Needs climate zone database, insulation values, window factors. Complex but known formula. |
| Column Design | Structural engineering. Euler's formula, safety factors. Would need professional review. |
| Snow Load | Needs geographic snow load data (ASCE 7). |

**Count: 3 calculators. These can wait or be simplified versions.**

---

## 5. Priority Ranking

Ranked by: Search Volume Potential x Inverse Difficulty x Monetization Potential

| Rank | Calculator | Search Vol (est.) | Difficulty | RPM Potential | Sites Having It | Priority Score |
|:----:|-----------|:-----------------:|:----------:|:-------------:|:---------------:|:--------------:|
| 1 | Square Footage Calculator | 500K/mo | 1 | $25 | Omni, Inch | **CRITICAL** |
| 2 | Concrete Slab Calculator | 500K/mo | 1 | $35 | Omni, Inch, Block | **CRITICAL** |
| 3 | Concrete Block/CMU Calculator | 50K/mo | 1 | $35 | All 3 | **HIGH** |
| 4 | Gravel Calculator | 50K/mo | 2 | $25 | Omni, Inch | **HIGH** |
| 5 | Mulch Calculator | 50K/mo | 1 | $25 | Omni, Inch | **HIGH** |
| 6 | Paint Calculator | 50K/mo | 1 | $30 | Omni, Inch | **HIGH** |
| 7 | Tile Calculator | 50K/mo | 1 | $30 | Omni, Inch | **HIGH** |
| 8 | Topsoil Calculator | 50K/mo | 1 | $25 | Omni, Inch | **HIGH** |
| 9 | Drywall Calculator | 50K/mo | 1 | $30 | Omni, Inch | **HIGH** |
| 10 | Deck Calculator | 50K/mo | 1-2 | $35 | All 3 | **HIGH** |
| 11 | Fence Calculator | 50K/mo | 1-2 | $35 | Inch, Block | **HIGH** |
| 12 | Roofing Calculator | 50K/mo | 2 | $50 | Omni, Inch | **HIGH** |
| 13 | Board Foot Calculator | 50K/mo | 1 | $25 | Omni, Inch | **HIGH** |
| 14 | Cubic Yard Calculator | 50K/mo | 1 | $25 | Omni | **HIGH** |
| 15 | Roof Pitch Calculator | 50K/mo | 3 | $50 | Omni, Block | **HIGH** |
| 16 | Stair Calculator | 50K/mo | 3 | $35 | Omni, Block | **HIGH** |
| 17 | Carpet Calculator | 50K/mo | 1 | $30 | Omni, Inch | **MEDIUM** |
| 18 | Flooring Calculator | 50K/mo | 1 | $30 | Omni, Inch | **MEDIUM** |
| 19 | Brick Calculator | 10K/mo | 1 | $30 | Omni, Inch | **MEDIUM** |
| 20 | Sand Calculator | 10K/mo | 2 | $25 | Omni, Inch | **MEDIUM** |
| 21 | Rafter Length Calculator | 5K/mo | 3 | $35 | All 3 | **MEDIUM** |
| 22 | Concrete Footing Calculator | 5K/mo | 1 | $35 | Omni, Inch, Block | **MEDIUM** |
| 23 | Framing Calculator | 5K/mo | 1 | $30 | All 3 | **MEDIUM** |
| 24 | Retaining Wall Calculator | 5K/mo | 2 | $35 | Omni, Inch | **MEDIUM** |
| 25 | Metal Roofing Calculator | 5K/mo | 2 | $50 | Omni, Inch | **MEDIUM** |
| 26 | Paver Calculator | 5K/mo | 1 | $35 | Omni, Inch | **MEDIUM** |
| 27 | Vinyl Siding Calculator | 5K/mo | 1 | $35 | Omni, Inch | **MEDIUM** |
| 28 | Siding Calculator | 5K/mo | 1 | $30 | Omni, Inch | **MEDIUM** |
| 29 | Asphalt Calculator | 5K/mo | 2 | $35 | Omni, Inch | **MEDIUM** |
| 30 | Plywood Calculator | 5K/mo | 1 | $30 | Omni, Inch | **MEDIUM** |
| 31 | Baluster Calculator | 5K/mo | 1 | $30 | Omni, Block | **MEDIUM** |
| 32 | Grout Calculator | 5K/mo | 2 | $30 | Omni | **MEDIUM** |
| 33 | Post Hole Concrete | 5K/mo | 1 | $30 | Inch | **MEDIUM** |
| 34 | Wallpaper Calculator | 5K/mo | 1 | $25 | Omni | **MEDIUM** |
| 35 | Board & Batten Calculator | 2K/mo | 1 | $30 | Omni, Inch, Block | **LOW** |
| 36 | Wainscoting Calculator | 2K/mo | 1 | $25 | Omni, Inch | **LOW** |
| 37 | Concrete Column Calculator | 2K/mo | 1 | $30 | Omni, Block | **LOW** |
| 38 | Sonotube Calculator | 2K/mo | 1 | $30 | Omni | **LOW** |
| 39 | Rebar Calculator | 2K/mo | 2 | $30 | Omni, Block | **LOW** |
| 40 | Lumber Weight Calculator | 2K/mo | 2 | $25 | Omni, Inch | **LOW** |
| 41 | French Drain Calculator | 2K/mo | 1 | $30 | Omni | **LOW** |
| 42 | Thinset Calculator | 2K/mo | 2 | $30 | Omni | **LOW** |
| 43 | Epoxy Calculator | 1K/mo | 1 | $25 | Omni | **LOW** |
| 44 | Sealant Calculator | 1K/mo | 1 | $25 | Omni | **LOW** |
| 45 | Fire Glass Calculator | 1K/mo | 1 | $25 | Omni | **LOW** |
| 46 | Concrete Weight Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 47 | Tonnage Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 48 | Steel Weight Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 49 | Metal Weight Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 50 | Pipe Weight Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 51 | Glass Weight Calculator | 500/mo | 2 | $25 | Omni | **LOW** |
| 52 | Aluminum Weight Calculator | 500/mo | 2 | $25 | Omni | **LOW** |
| 53 | Steel Plate Weight Calc | 500/mo | 1 | $25 | Omni | **LOW** |
| 54 | Stone Weight Calculator | 500/mo | 2 | $25 | Omni | **LOW** |
| 55 | Log Weight Calculator | 500/mo | 2 | $20 | Omni | **LOW** |
| 56 | Pool Volume Calculator | 5K/mo | 2 | $25 | Omni | **LOW** |
| 57 | Pond Calculator | 1K/mo | 2 | $20 | Omni | **LOW** |
| 58 | Road Base Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 59 | Crushed Stone Calculator | 2K/mo | 2 | $25 | Omni | **LOW** |
| 60 | Limestone Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| 61 | CFM Calculator | 2K/mo | 1 | $25 | Omni | **LOW** |
| 62 | Air Changes/Hour | 1K/mo | 1 | $25 | Omni | **LOW** |
| 63 | AC Tonnage | 2K/mo | 5 | $35 | Omni | **LOW** |
| 64 | Trim/Molding Calculator | 2K/mo | 1 | $25 | Inch | **LOW** |
| 65 | Deck Stain Calculator | 1K/mo | 1 | $25 | Inch | **LOW** |
| 66 | Fence Stain Calculator | 500/mo | 1 | $25 | Inch | **LOW** |
| 67 | Roof Sheathing Calculator | 2K/mo | 2 | $30 | Inch | **LOW** |
| 68 | Paver Base Calculator | 1K/mo | 1 | $25 | Inch | **LOW** |
| 69 | Vinyl Fence Calculator | 2K/mo | 1 | $30 | Inch | **LOW** |
| 70 | Stair Carpet Calculator | 1K/mo | 2 | $25 | Omni | **LOW** |
| --- | --- Blocklayer Specialty --- | | | | | |
| 71 | Gambrel Roof Calculator | 1K/mo | 3 | $30 | Omni, Block | **LOW** |
| 72 | Birdsmouth Cut Calculator | 2K/mo | 3 | $30 | Omni, Block | **LOW** |
| 73 | Hip Roof Framing + Templates | 2K/mo | 4 | $35 | Block only | **LOW** |
| 74 | Gable Roof Framing Plan | 2K/mo | 3 | $30 | Block only | **LOW** |
| 75 | Saltbox Roof Calculator | 500/mo | 3 | $25 | Block only | **LOW** |
| 76 | Skillion/Lean-to Roof | 500/mo | 3 | $25 | Block only | **LOW** |
| 77 | Crown Molding Angle Chart | 2K/mo | 3 | $25 | Block only | **LOW** |
| 78 | Compound Miter Calculator | 1K/mo | 3 | $25 | Block only | **LOW** |
| 79 | Dovetail Template Generator | 1K/mo | 4 | $20 | Block only | **NICHE** |
| 80 | Mortise & Tenon Calculator | 500/mo | 2 | $20 | Block only | **NICHE** |
| 81 | Kerf Spacing Calculator | 500/mo | 3 | $20 | Block only | **NICHE** |
| 82 | Diagonal Bracing Calculator | 500/mo | 3 | $25 | Block only | **NICHE** |
| 83 | Tube Notching Templates | 1K/mo | 4 | $25 | Block only | **NICHE** |
| 84 | Tube Miter Templates | 500/mo | 4 | $25 | Block only | **NICHE** |
| 85 | Pie Cut Bend Calculator | 500/mo | 4 | $25 | Block only | **NICHE** |
| 86 | Round-to-Square Transition | 200/mo | 4 | $25 | Block only | **NICHE** |
| 87 | Spiral Stair Calculator (full) | 1K/mo | 4 | $30 | Block only | **NICHE** |
| 88 | Steel Spine Stair Calculator | 500/mo | 4 | $25 | Block only | **NICHE** |
| 89 | Gazebo Calculator | 1K/mo | 4 | $25 | Block only | **NICHE** |
| 90 | Polygon Calculator | 2K/mo | 3 | $15 | Block only | **NICHE** |
| 91 | Circle Calculator | 5K/mo | 1 | $15 | Block only | **NICHE** |
| 92 | Circle Chord/Arc Calculator | 1K/mo | 3 | $15 | Block only | **NICHE** |
| 93 | Ellipse/Oval Layout | 500/mo | 3 | $15 | Block only | **NICHE** |
| 94 | Golden Ratio Calculator | 2K/mo | 1 | $10 | Block only | **NICHE** |
| 95 | Pyramid Calculator | 1K/mo | 2 | $10 | Block only | **NICHE** |
| 96 | Floor Area (Multi-Sided) | 500/mo | 2 | $15 | Block only | **NICHE** |
| 97 | Arched Fence Palings | 200/mo | 3 | $25 | Block only | **NICHE** |
| 98 | Glass Balustrade | 500/mo | 1 | $30 | Block only | **NICHE** |
| 99 | Concrete Core Drilling | 200/mo | 3 | $30 | Block only | **NICHE** |
| 100 | Multi-Sided Concrete Slab | 500/mo | 3 | $30 | Block only | **NICHE** |
| 101 | Concrete Block Corner Miter | 200/mo | 3 | $25 | Block only | **NICHE** |
| 102 | Wall Framing for Openings | 1K/mo | 2 | $25 | Block only | **NICHE** |
| 103 | Deck Board Spacing | 1K/mo | 1 | $25 | Block only | **NICHE** |
| 104 | Rise in Run Calculator | 2K/mo | 3 | $20 | Block only | **NICHE** |

---

## 6. Total Counts

### Per-Site Counts (Non-Cost Calculators)

| Site | Unique Calculators | With Variants (material/size) | Total Pages |
|------|:-----------------:|:----------------------------:|:-----------:|
| **OmniCalculator** | ~74 | ~80 | ~80 |
| **InchCalculator** | ~39 | ~55+ (incl. sub-category pages) | ~55 |
| **Blocklayer** | ~65 | ~65 (but × 2 for metric/inch) | ~130 |

### Combined Unique Calculators Across All 3 Sites

| Category | Count |
|----------|:-----:|
| Concrete & Masonry | 15 |
| Roofing | 12 |
| Framing & Carpentry | 18 |
| Decks & Outdoor Structures | 6 |
| Fencing | 5 |
| Siding | 3 |
| Interior Finishing (drywall, tile, paint, carpet, flooring) | 14 |
| Landscaping & Materials | 12 |
| Weight Calculators | 12 |
| HVAC / Airflow | 3 |
| Measurement & Conversion | 8 |
| Metalwork & Fabrication | 5 |
| Geometry & Trig | 12 |
| **TOTAL UNIQUE** | **~125** |

After deduplication (same calculator on multiple sites), there are approximately **104 truly unique calculator types** across all three sites.

---

## 7. Can We Build ALL of Them?

### Realistic Assessment

**YES -- we can build all of them.** Here is the breakdown:

#### Tier A: Trivial to Build (1-2 hours each) -- 55 calculators

These are all simple arithmetic: L × W × D, area / unit area, volume × density. Pure Alpine.js with a form and computed output. No diagrams needed (though adding one helps SEO).

**Includes:** All material quantity calculators (concrete, gravel, mulch, sand, topsoil, paint, tile, carpet, flooring, drywall, siding, fence pickets, deck boards, plywood, baluster, brick, paver, post hole concrete, sonotube, board foot, wallpaper, sealant, epoxy, grout, thinset, fire glass, board & batten, wainscoting, trim, stain calculators, etc.)

**Effort:** ~110 hours total (2 hours × 55)

#### Tier B: Arithmetic + Lookup Data (2-4 hours each) -- 25 calculators

Same Alpine.js pattern but need embedded data tables for material densities, coverage rates, species data, mix ratios.

**Includes:** All weight calculators (steel, aluminum, metal, glass, stone, concrete, log, lumber, pipe, plate), tonnage, cement mix ratios, thinset coverage, roofing (pitch factors), asphalt, concrete bags, rebar weight, retaining wall materials.

**Effort:** ~75 hours total (3 hours × 25)

**Data needed (all publicly available):**
- Material density table: ~30 materials (steel, aluminum, copper, brass, concrete, granite, marble, glass, wood species, gravel, sand, etc.)
- Wood species density: ~20 common species
- Concrete mix ratios: 3-5 standard mixes
- Pipe dimensions: standard pipe schedule table
- Roofing pitch multipliers: 12 standard pitches

#### Tier C: Trig + Diagrams (4-8 hours each) -- 15 calculators

Need trigonometric formulas and SVG diagrams that update reactively.

**Includes:** Roof pitch, rafter length, stair stringer, gambrel roof, birdsmouth cut, spiral staircase, miter angles, crown molding angles, kerf spacing, circle/polygon calculations, ellipse layout.

**Effort:** ~90 hours total (6 hours × 15)

**Technical approach:** Alpine.js + inline SVG with reactive data bindings. All trig formulas are well-documented (Math.atan2, Math.cos, Math.sin). SVG paths update when inputs change.

#### Tier D: Complex Geometry + Templates (8-20 hours each) -- 12 calculators

These need sophisticated SVG generation, potentially PDF template output, and complex 3D geometry calculations.

**Includes:** Hip roof framing (full plan), gable/saltbox roof framing plans, tube notching/miter templates, pie cut bending, round-to-square transitions, dovetail templates, gazebo framing, steel spine stairs, deck full layout.

**Effort:** ~150 hours total (12 hours × 12)

**Technical approach:** 
- SVG generation with Alpine.js is doable but complex
- For printable templates: generate SVG at exact scale, use CSS @media print
- Tube notching: parametric unrolled cylinder intersection (known math, well-documented)
- Could use Canvas API for complex rendering if SVG becomes unwieldy

**These are the most differentiated calculators. Blocklayer's printable templates are its moat. Building these would be a strong competitive move.**

#### Tier E: Skip or Simplify -- 3 calculators

| Calculator | Issue | Recommendation |
|-----------|-------|----------------|
| AC Tonnage (Manual J) | Climate zone database, many factors | Build simplified version (sq ft × factor) |
| Column Design (structural) | Engineering liability concern | Skip or add strong disclaimers |
| Snow Load | Geographic data (ASCE 7 tables) | Skip or build simplified regional version |

### Total Build Effort Summary

| Tier | Calculators | Hours Each | Total Hours | Timeline (1 dev) |
|------|:-----------:|:----------:|:-----------:|:-----------------:|
| A (Simple) | 55 | 2 | 110 | 2 weeks |
| B (Lookup) | 25 | 3 | 75 | 1.5 weeks |
| C (Trig+SVG) | 15 | 6 | 90 | 2 weeks |
| D (Complex) | 12 | 12 | 150 | 3 weeks |
| E (Skip) | 3 | -- | -- | -- |
| **TOTAL** | **107** | -- | **425 hrs** | **~10 weeks** |

### Special Considerations

1. **Template System:** Build a reusable calculator shell (Alpine.js component) with standardized input types (length, area, volume, angle) and output formatting. This reduces per-calculator effort by 30-40%.

2. **SVG Diagram Library:** Create reusable SVG primitives (rectangle, triangle, circle, dimension lines, angle arcs) that can be composed into calculator-specific diagrams. Invest 20 hours upfront to save 5 hours per diagram calculator.

3. **Printable Template Engine:** Build a generic "print at scale" system (one investment of ~15 hours) that all template calculators can share.

4. **Unit Conversion Layer:** Build once: metric/imperial toggle that converts all inputs/outputs. Blocklayer duplicates every page for metric vs inch -- we can do this with one toggle.

5. **Responsive Design:** All calculators should be mobile-friendly. This is table stakes.

### Competitive Advantage Opportunities

| Advantage | Description |
|-----------|-------------|
| **Metric/Imperial toggle** | One page, not two. Better than Blocklayer. |
| **Better mobile UX** | Blocklayer's site is desktop-oriented. Modern responsive design wins. |
| **Visual output on ALL calcs** | OmniCalc/InchCalc are mostly text output. Add SVG diagrams to even simple calcs (concrete slab visualization, roof pitch triangle). |
| **Printable templates** | Match Blocklayer's killer feature but with better print CSS. |
| **Cross-linked material guides** | "You need 4.5 cu.yd of concrete" links to "How to mix concrete" and "Concrete delivery near you." |
| **Shareable results** | URL with parameters so users can share: fatstud.com/concrete-slab?l=20&w=12&d=4 |
| **Speed** | Static site (Rust WASM or pure Alpine.js) loads instantly vs OmniCalc's heavy React app. |

---

## Appendix A: Data Tables Needed

All data below is publicly available and commonly used in construction references.

### Material Densities (lbs per cubic foot)

| Material | Density |
|----------|--------:|
| Concrete (standard) | 150 |
| Concrete (lightweight) | 115 |
| Gravel | 105 |
| Sand (dry) | 100 |
| Sand (wet) | 120 |
| Topsoil | 75 |
| Mulch | 45 |
| Asphalt | 145 |
| Crushed stone | 100 |
| Limestone | 160 |
| Granite | 168 |
| Marble | 169 |
| Steel | 490 |
| Aluminum | 169 |
| Copper | 559 |
| Brass | 524 |
| Glass (standard) | 156 |
| Water | 62.4 |

### Wood Species Densities (lbs per cubic foot, air-dried)

| Species | Density |
|---------|--------:|
| Douglas Fir | 32 |
| Southern Yellow Pine | 36 |
| Spruce | 28 |
| Cedar (Western Red) | 23 |
| Oak (Red) | 44 |
| Oak (White) | 47 |
| Maple (Hard) | 44 |
| Cherry | 35 |
| Walnut | 38 |
| Poplar | 29 |
| Ash | 41 |
| Birch | 43 |
| Pine (White) | 25 |
| Redwood | 28 |
| Mahogany | 35 |
| Teak | 41 |
| Hickory | 51 |
| Balsa | 9 |
| IPE | 69 |
| Bamboo | 25 |

### Roof Pitch Multipliers

| Pitch | Multiplier | Angle (degrees) |
|-------|:----------:|:---------------:|
| 1/12 | 1.003 | 4.8 |
| 2/12 | 1.014 | 9.5 |
| 3/12 | 1.031 | 14.0 |
| 4/12 | 1.054 | 18.4 |
| 5/12 | 1.083 | 22.6 |
| 6/12 | 1.118 | 26.6 |
| 7/12 | 1.158 | 30.3 |
| 8/12 | 1.202 | 33.7 |
| 9/12 | 1.250 | 36.9 |
| 10/12 | 1.302 | 39.8 |
| 11/12 | 1.357 | 42.5 |
| 12/12 | 1.414 | 45.0 |

### Standard Rebar Sizes

| Size | Diameter (in) | Weight (lbs/ft) |
|------|:-------------:|:---------------:|
| #3 | 0.375 | 0.376 |
| #4 | 0.500 | 0.668 |
| #5 | 0.625 | 1.043 |
| #6 | 0.750 | 1.502 |
| #7 | 0.875 | 2.044 |
| #8 | 1.000 | 2.670 |

### Concrete Bag Yields

| Bag Size | Yield (cu ft) |
|----------|:-------------:|
| 40 lb | 0.30 |
| 50 lb | 0.375 |
| 60 lb | 0.45 |
| 80 lb | 0.60 |
| 90 lb | 0.67 |

---

## Appendix B: Sources

### Primary Sources (Scraped/Analyzed)
- [OmniCalculator Construction](https://www.omnicalculator.com/construction) - Full calculator directory
- [InchCalculator Construction](https://www.inchcalculator.com/construction-calculators/) - Construction & estimation tools hub
- [Blocklayer Calculator Directory](https://www.blocklayer.com/calculator-directory) - Builder calculator apps

### Additional References
- [InchCalculator Concrete & Masonry](https://www.inchcalculator.com/concrete-calculators/)
- [InchCalculator Carpentry](https://www.inchcalculator.com/carpentry-calculators/)
- [InchCalculator Flooring](https://www.inchcalculator.com/flooring-calculators/)
- [InchCalculator Fence](https://www.inchcalculator.com/fence-calculators/)
- [InchCalculator Landscaping](https://www.inchcalculator.com/lawn-landscaping-calculators/)
- [Awesome Construction Calculators (GitHub)](https://github.com/dicktracey909/awesome-construction-calculators)
- Keyword data from: /var/www/vibe-marketing/rust/construction-calculators/keyword-research/MASTER-SUMMARY.md

---

*Analysis complete. 104 unique calculators identified across 3 sites. All are buildable with Alpine.js + SVG. Estimated total effort: ~425 developer hours (~10 weeks). Recommended approach: template-based system to accelerate builds.*
