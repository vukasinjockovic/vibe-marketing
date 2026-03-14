#!/usr/bin/env python3
"""
Final extraction: Curated list of genuine tool/utility/calculator/game sites.
Removes false positives via exclusion lists.
"""

import csv
import re
import json
from collections import defaultdict
from pathlib import Path

CSV_PATH = Path("/var/www/vibe-marketing/knowledge/market-data/publishers/all_publishers.csv")


def load_publishers():
    publishers = []
    seen = set()
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row['domain'].strip().strip('"')
            if d not in seen:
                seen.add(d)
                publishers.append({
                    'domain': d,
                    'name': row['name'].strip().strip('"'),
                    'network': row['network'].strip(),
                })
    return publishers


# ===== FALSE POSITIVE EXCLUSIONS =====
# Domains that match tool patterns but aren't tool sites

FP_DOMAINS = {
    # "calc" in non-calculator contexts
    'thegeographicalcure.com',  # travel blog, "calc" in "geographical"
    'practicalcooks.com',  # recipe blog
    'magicalclan.com',  # gaming blog
    'practicalfamilyfinance.com', 'practicalperfectionut.com',
    'practicalself.com', 'practicalstepmom.com', 'practicalwanderlust.com',
    'practicalcookbook.com',

    # "hash" in hashtag/other
    'hashtagcoloradolife.com', 'hashtaginvesting.com', 'hashtagbasketball.com',
    'hashimashi.com', 'abroadwithash.com', 'natashashome.com',
    'athomewithashley.com', 'withashleyandco.com',

    # "ocr" in crochet/other
    'cococrochetlee.com', 'mediocrechef.com', 'motocrosshideout.com',
    'bellacococrochet.com', 'pinsandprocrastination.com',
    'makeanddocrew.com', 'hellocreativefamily.com', 'nocrumbsleft.net',
    'creamofthecropcrochet.com',

    # "convert" in non-tool contexts
    'truckconversion.net', 'safeconvertiblecarseats.com',
    'snailpacetransformations.com',
    'girlversusdough.com',  # vs/versus match but recipe

    # "diff" in non-tool contexts
    'differencebetween.net',  # could be a reference site but not a tool
    'everystarisdifferent.com', 'sesamebutdifferent.com',
    'differentiatedteaching.com', 'differentbydesignlearning.com',
    'ithinkdiff.com', 'differentiatedkindergarten.com',
    'allthedifferences.com', 'criticalhit.net',

    # "font" in name not font tools
    'emmafontanella.com', 'jacqui@jacquelinebellefontaine.co.uk',
    'dafontfile.org',  # this one might actually be a font site - keep investigating

    # "beautif" matching beautiful/beauty
    'beautifulmakeupsearch.com', 'beautifuleatsandthings.com',
    'eatbeautiful.net', 'beautifullybrokenjourney.com',
    'dwellbeautiful.com', 'homebeautifully.com', 'abeautifulplate.com',
    'nomadisbeautiful.com', 'beautifulwithbrains.com',
    'onebeautifulhomeblog.com', 'abeautifulmess.com',
    'ohsobeautifulpaper.com', 'diybeautify.com',

    # "lint" in non-linter contexts
    'girlinthegarage.net', 'afarmgirlinthemaking.com',
    'amazingribs.com', 'fluentin3months.com', 'onlinemictest.com',

    # "format" in information/other
    'mauiinformationguide.com', 'missinformationblog.com',
    'reformationacres.com', 'personalityclub.com', 'formatlibrary.com',

    # "palette" not a tool
    'thepalettemuse.com', 'stitchpalettes.com',

    # "audio" not tool sites
    'lovelyaudiobooks.info', 'blackghostaudio.com', 'audiocaptain.com',
    'audiobookaddicts.com', 'audiotips.com', 'audioassemble.com',

    # "video" not tool sites
    'wildwoodvideoarchive.com', 'diyvideostudio.com', 'videochums.com',
    'thatvideogameblog.com',

    # "image" not tool sites
    'imagelicious.com',

    # "app" matching in non-app names
    'qa-monk.com', 'qa-magenta.com', 'qa-turquoise.com',

    # "test" matching in blog names
    'thesweetestdigs.com', 'thesweetestoccasion.com', 'sweetestmenu.com',
    'triedtestedandtrue.com', 'familydaystriedandtested.com',
    'marystestkitchen.com', 'twintestedblog.com', 'mycrashtestlife.com',
    'cutest-baby-shower-ideas.com', 'theruntesters.com', 'greatestspeakers.com',
    'thetraveltester.com', 'testprepnerds.com', 'biketestreviews.com',
    'laurenslatest.com', 'hungrypaprikas.com', 'dk894953543.com',

    # "speed" not speed test
    'speedyrecipe.com', 'dsmtuners.com', 'turbospeedwifi.com',

    # "random" not random generator
    'ootrandomizer.com',  # Zelda randomizer game mod

    # "tool" in non-tool contexts
    'tantrumsandtools.com', 'viewsfromastepstool.com',
    'craftsmanprotools.com', 'batterytools.net', 'easyteachingtools.com',
    'thetoolscout.com', 'finepowertools.com', 'anysoftwaretools.com',

    # "online" in non-tool contexts
    'thegentlealbum.com', 'thegeneticchef.com', 'cookinginmygenes.com',

    # Misc false positives
    'aboutbritain.com', 'stable-diffusion-art.com', 'idownloadblog.com',
    'windowslatest.com', 'fairytaleshadows.com', 'raisinggenerationnourished.com',
    'lauraradniecki.com', 'recipemarker.com', 'effortlessconversations.com',
    'thegirlwithashovel.com', 'fattybuttsbbq.com', 'cnevpost.com',
    'lifeprettified.com', 'savoryspin.com', 'feistytapas.com',
    'postcardstoseattle.com', 'mrspinch.com', 'strandsgame.me',
    'hdontap.com', 'heysnickerdoodle.com', 'michaelscodingspot.com',
    'mythirtyspot.com', 'jenrylandllc.blogspot.com', 'emergencyprepguy.com',
    'generationacresfarm.com', 'botanicalinterests.com', 'mailboxlocate.com',
    'selfdecode.com', 'optimizedportfolio.com', 'kingshotoptimizer.com',
    'tabletpccomparison.net', 'collegefootball.gg', 'madden-school.com',
    'pelheat.com',

    # Test sites (not real)
    'site.com', 'test.com', 'test1sameemail.com', 'test2sameemail.com',
    'testsite.com', 'kinsta.cloud', 'justclickappliances.com.test',
}


def classify_domain(domain, name, network):
    """Classify a domain into specific tool categories. Returns list of classifications."""
    d = domain.lower()
    n = name.lower()

    # Remove TLD for pattern matching
    parts = d.split('.')
    if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in {'co.uk', 'co.nz', 'co.za', 'com.au'}:
        base = '.'.join(parts[:-2])
    elif len(parts) >= 2:
        base = '.'.join(parts[:-1])
    else:
        base = d

    results = []

    # ===== CALCULATORS =====
    calc_patterns = [
        (r'calculator', 'Calculator Site'),
        (r'\bcalc\b', 'Calculator'),
        (r'calculate', 'Calculator'),
        (r'fatcalc', 'Body Fat Calculator'),
    ]
    for pat, ctype in calc_patterns:
        if re.search(pat, base):
            results.append(('Calculator', ctype, 'High'))

    # ===== CONVERTERS =====
    conv_patterns = [
        (r'convert(?:er|binary)', 'Converter'),
        (r'titlecase', 'Case Converter'),
    ]
    for pat, ctype in conv_patterns:
        if re.search(pat, base):
            results.append(('Converter', ctype, 'High'))

    # ===== GENERATORS =====
    gen_patterns = [
        (r'(?:random|password|name|word|text|color|meme|logo|team)[-_]?gen', 'Generator'),
        (r'generator(?![-_]?(?:grid|s[-_]?farm))', 'Generator'),
        (r'strongpasswordgen', 'Password Generator'),
        (r'randomgen', 'Random Generator'),
    ]
    for pat, ctype in gen_patterns:
        if re.search(pat, base):
            results.append(('Generator', ctype, 'High'))

    # ===== GAMES =====
    game_patterns = [
        (r'\bgame\b', 'Browser Game'),
        (r'games\b', 'Game Site'),
        (r'puzzle', 'Puzzle'),
        (r'solitaire', 'Solitaire'),
        (r'crossword', 'Crossword'),
        (r'sudoku', 'Sudoku'),
        (r'chess\b', 'Chess'),
        (r'mahjong', 'Mahjong'),
        (r'wordle', 'Word Game'),
        (r'quiz\b', 'Quiz'),
        (r'trivia', 'Trivia'),
        (r'typing[-_]?game', 'Typing Game'),
        (r'coloring[-_]?page', 'Coloring Pages'),
    ]
    for pat, ctype in game_patterns:
        if re.search(pat, base):
            results.append(('Game', ctype, 'Medium'))

    # ===== TEST PREP =====
    test_patterns = [
        (r'practice[-_]?test', 'Practice Test'),
        (r'practice[-_]?exam', 'Practice Exam'),
        (r'test[-_]?prep', 'Test Prep'),
        (r'exam[-_]?prep', 'Exam Prep'),
        (r'(?:cna|rbt|pert|tsi|hesi|nclex|asvab|ged|hiset|aswb|pmp|ccma|ptcb|servsafe|az900|nremt|phlebotomy|accuplacer|workkeys|parapro)[-_]?(?:practice|test|exam)', 'Certification Test Prep'),
        (r'(?:career|aptitude|personality|spirit[-_]?animal)[-_]?test', 'Assessment/Personality Test'),
        (r'frame[-_]?rate[-_]?test', 'FPS Test'),
        (r'(?:mic|webcam|keyboard|mouse|monitor)[-_]?test', 'Hardware Test'),
        (r'speed[-_]?test', 'Internet Speed Test'),
    ]
    for pat, ctype in test_patterns:
        if re.search(pat, base):
            results.append(('Test/Quiz', ctype, 'Medium'))

    # ===== TEMPLATES/PRINTABLES =====
    tmpl_patterns = [
        (r'template', 'Template Site'),
        (r'printable', 'Printable Site'),
        (r'worksheet', 'Worksheet Site'),
        (r'flashcard', 'Flashcard Tool'),
    ]
    for pat, ctype in tmpl_patterns:
        if re.search(pat, base):
            results.append(('Template/Printable', ctype, 'Medium'))

    # ===== SVG/CRAFT FILES =====
    svg_patterns = [
        (r'\bsvg\b', 'SVG File Site'),
        (r'freesvg', 'Free SVG Site'),
        (r'(?:free)?[-_]?fonts?\b', 'Font Site'),
    ]
    for pat, ctype in svg_patterns:
        if re.search(pat, base):
            results.append(('SVG/Font/Craft', ctype, 'Medium'))

    # ===== COLOR TOOLS =====
    color_patterns = [
        (r'color[-_]?pick', 'Color Picker'),
        (r'rgb[-_]?color', 'Color Tool'),
        (r'palette[-_]?(?:gen|mak|creat)', 'Palette Generator'),
    ]
    for pat, ctype in color_patterns:
        if re.search(pat, base):
            results.append(('Color Tool', ctype, 'Medium'))

    # ===== TEXT TOOLS =====
    text_patterns = [
        (r'word[-_]?count', 'Word Counter'),
        (r'character[-_]?count', 'Character Counter'),
        (r'typing[-_]?(?:test|speed|game|practic)', 'Typing Tool'),
    ]
    for pat, ctype in text_patterns:
        if re.search(pat, base):
            results.append(('Text Tool', ctype, 'Medium'))

    # ===== COMPARISON/REFERENCE =====
    ref_patterns = [
        (r'\bdiffen\b', 'Comparison/Difference Site'),
        (r'comparebeforebuying', 'Product Comparison'),
        (r'howthingscompare', 'Comparison Site'),
        (r'travelmath', 'Travel Calculator'),
    ]
    for pat, ctype in ref_patterns:
        if re.search(pat, base):
            results.append(('Reference/Comparison', ctype, 'Medium'))

    # ===== SPECIFIC TOOL SITES =====
    specific_patterns = [
        (r'remote\.tools', 'Remote Work Tools Directory'),
        (r'wodtools', 'CrossFit/WOD Tools'),
        (r'kanji\.tools', 'Japanese Kanji Tool'),
        (r'pd2\.tools', 'Payday 2 Tools'),
        (r'generatorgrid', 'Generator Directory'),
        (r'onlinemictest', 'Online Mic Test'),
        (r'frameratetest', 'Frame Rate Test'),
    ]
    for pat, ctype in specific_patterns:
        if re.search(pat, base) or re.search(pat, d):
            results.append(('Specific Tool', ctype, 'Medium'))

    # ===== ONLINE/WEB TOOLS (when "online" + tool signal) =====
    if 'online' in base:
        if any(w in base for w in ['test', 'calc', 'convert', 'tool', 'check', 'scan', 'edit', 'play']):
            results.append(('Online Tool', 'Online Tool', 'Medium'))

    return results


def rate_domain_quality(domain):
    """Score domain quality for branding/SEO."""
    d = domain.lower()
    base = d.split('.')[0]
    score = 50

    # Length bonus
    if len(base) <= 8:
        score += 20
    elif len(base) <= 12:
        score += 10
    elif len(base) <= 16:
        score += 5
    elif len(base) > 25:
        score -= 10

    # TLD bonus
    if d.endswith('.com'):
        score += 15
    elif d.endswith('.org') or d.endswith('.net'):
        score += 10
    elif d.endswith('.me') or d.endswith('.io') or d.endswith('.co'):
        score += 8
    elif d.endswith('.academy') or d.endswith('.tools') or d.endswith('.zone'):
        score += 5

    # Exact-match domain bonus
    exact_patterns = [
        r'^calculator', r'^convert', r'^generat', r'^compress',
        r'^resize', r'^format', r'^merge', r'^split',
        r'^typing', r'^diffen', r'^fatcalc', r'^svg\.',
        r'^calcul',
    ]
    for p in exact_patterns:
        if re.search(p, d):
            score += 15
            break

    # Penalty for complexity
    if d.count('-') > 3:
        score -= 10

    return min(100, max(0, score))


def rate_rust_advantage(tool_type):
    """How much would Rust/WASM improve this tool type?"""
    high = {'Calculator', 'Converter', 'Generator', 'Password Generator',
            'Random Generator', 'Color Picker', 'Color Tool', 'Palette Generator',
            'Word Counter', 'Character Counter', 'Case Converter',
            'Body Fat Calculator', 'Calculator Site', 'FPS Test',
            'Internet Speed Test', 'Typing Tool'}
    medium = {'Browser Game', 'Puzzle', 'Solitaire', 'Crossword', 'Sudoku',
              'Chess', 'Mahjong', 'Word Game', 'Typing Game',
              'Online Mic Test', 'Frame Rate Test', 'Hardware Test',
              'SVG File Site', 'Free SVG Site', 'Font Site',
              'Travel Calculator', 'Comparison/Difference Site'}
    low = {'Quiz', 'Trivia', 'Practice Test', 'Practice Exam', 'Test Prep',
           'Exam Prep', 'Certification Test Prep', 'Assessment/Personality Test',
           'Template Site', 'Printable Site', 'Worksheet Site', 'Flashcard Tool',
           'Coloring Pages', 'Product Comparison', 'Comparison Site',
           'Remote Work Tools Directory', 'CrossFit/WOD Tools',
           'Japanese Kanji Tool', 'Payday 2 Tools', 'Generator Directory',
           'Online Tool', 'Game Site'}

    if tool_type in high:
        return 'High'
    elif tool_type in medium:
        return 'Medium'
    elif tool_type in low:
        return 'Low'
    return 'Low'


def main():
    publishers = load_publishers()
    print(f"Loaded {len(publishers)} unique publishers")

    # ===== BROAD NICHE CATEGORIZATION =====
    niche_counts = defaultdict(lambda: {'total': 0, 'mv': 0, 'rp': 0})

    niche_patterns = {
        'Food/Recipe': r'(?:recipe|cook|bake|kitchen|food|foodie|meal|chef|culinary|eat|eater|dinner|lunch|breakfast|dessert|cake|cookie|bread|pasta|pizza|soup|salad|grill|bbq|barbecue|chocolate|candy|spice|coffee|tea|wine|beer|cocktail|smoothie|vegan|vegetarian|paleo|keto)',
        'Travel': r'(?:travel|trip|vacation|holiday|tour|tourist|destination|wander|nomad|backpack|hotel|resort|flight|cruise|expat|abroad|passport)',
        'DIY/Home/Garden': r'(?:diy|craft|handmade|woodwork|furniture|decor|decorat|interior|remodel|renovat|garden|plant|flower|lawn|homestead|farmhouse|sew|sewing|knit|crochet|quilt|yarn|fabric|organize|declutter|cleaning)',
        'Parenting/Family': r'(?:parent|mom|mum|mama|mother|dad|papa|father|baby|infant|toddler|child|kid|teen|family|pregnant|newborn|nursery|daycare|nanny|toy|birthday)',
        'Health/Fitness': r'(?:fitness|workout|exercise|gym|yoga|pilates|crossfit|muscle|protein|supplement|vitamin|nutrition|health|wellness|medical|doctor|symptom|therapy|mental|anxiety|depression|meditat|mindful|pregnancy|running|marathon|weight[-_]?loss)',
        'Finance': r'(?:finance|financial|invest|stock|crypto|bitcoin|forex|trading|broker|bank|credit|tax|retirement|pension|savings|debt|insurance|budget|frugal|coupon|cashback|money|wealth|accounting)',
        'Education': r'(?:learn|teach|tutor|course|lesson|school|college|university|academy|education|homeschool|preschool|kindergarten|stem|homework|study|student|flashcard|worksheet)',
        'Tech/Programming': r'(?:tech|technology|software|hardware|computer|laptop|server|cloud|saas|api|database|python|javascript|react|vue|angular|node|rust|java|php|wordpress|linux|windows|android|ios|ai|machine[-_]?learning|cybersecurity|developer|programmer|startup|gadget)',
        'Fashion/Beauty': r'(?:fashion|style|clothing|outfit|dress|wardrobe|trend|designer|boutique|beauty|makeup|cosmetic|skincare|hair|nail|fragrance|jewelry|shoe|sneaker)',
        'Pets/Animals': r'(?:pet|dog|puppy|cat|kitten|bird|fish|reptile|rabbit|bunny|horse|aquarium|vet|breed|paw|bark)',
        'Automotive': r'(?:car|auto|vehicle|truck|motorcycle|bike|scooter|tesla|ford|toyota|honda|bmw|mechanic|tire|engine)',
        'Sports/Outdoors': r'(?:sport|football|soccer|basketball|baseball|hockey|tennis|golf|swimming|cycling|boxing|mma|ufc|nfl|nba|mlb|hunting|fishing|hiking|climbing|skiing|surf)',
        'Photography': r'(?:photograph|camera|lens|dslr|mirrorless|lightroom|photoshop)',
        'Music/Audio': r'(?:music|song|guitar|piano|drum|violin|chord|lyric|band|concert|album|playlist|producer|dj|podcast)',
        'Games/Entertainment': r'(?:game|gaming|gamer|esport|twitch|stream|anime|manga|comic|humor|funny|entertainment)',
    }

    for pub in publishers:
        d_base = re.sub(r'\.[a-z]{2,}$', '', pub['domain'].lower())
        combined = f"{d_base} {pub['name'].lower()}"
        best_niche = 'Other'
        best_count = 0

        for niche, pattern in niche_patterns.items():
            matches = re.findall(pattern, combined)
            if len(matches) > best_count:
                best_count = len(matches)
                best_niche = niche

        niche_counts[best_niche]['total'] += 1
        if pub['network'] == 'mediavine':
            niche_counts[best_niche]['mv'] += 1
        else:
            niche_counts[best_niche]['rp'] += 1

    # ===== TOOL SITE IDENTIFICATION =====
    all_tool_sites = []

    for pub in publishers:
        if pub['domain'] in FP_DOMAINS:
            continue

        classifications = classify_domain(pub['domain'], pub['name'], pub['network'])
        if classifications:
            dq = rate_domain_quality(pub['domain'])
            for category, tool_type, base_conf in classifications:
                rust_adv = rate_rust_advantage(tool_type)
                all_tool_sites.append({
                    'domain': pub['domain'],
                    'name': pub['name'],
                    'network': pub['network'],
                    'category': category,
                    'tool_type': tool_type,
                    'rust_advantage': rust_adv,
                    'domain_quality': dq,
                })

    # Deduplicate by domain (keep highest-priority classification)
    priority = {'High': 3, 'Medium': 2, 'Low': 1}
    best_per_domain = {}
    for site in all_tool_sites:
        d = site['domain']
        if d not in best_per_domain or priority.get(site['rust_advantage'], 0) > priority.get(best_per_domain[d]['rust_advantage'], 0):
            best_per_domain[d] = site

    tool_sites_deduped = sorted(best_per_domain.values(),
                                key=lambda x: (-priority.get(x['rust_advantage'], 0), -x['domain_quality']))

    # ===== OUTPUT =====
    print(f"\n{'='*80}")
    print(f"NICHE CATEGORIZATION (all {len(publishers)} unique publishers)")
    print(f"{'='*80}")
    print(f"\n{'Category':<25s} {'Total':>6s} {'MV':>6s} {'RP':>6s} {'%':>6s}")
    print('-'*55)
    for niche in sorted(niche_counts.keys(), key=lambda x: -niche_counts[x]['total']):
        info = niche_counts[niche]
        pct = info['total'] / len(publishers) * 100
        print(f"{niche:<25s} {info['total']:>6d} {info['mv']:>6d} {info['rp']:>6d} {pct:>5.1f}%")

    # Group tool sites by category
    by_category = defaultdict(list)
    for site in tool_sites_deduped:
        by_category[site['category']].append(site)

    print(f"\n{'='*80}")
    print(f"IDENTIFIED TOOL/UTILITY SITES: {len(tool_sites_deduped)} unique domains")
    print(f"{'='*80}")

    for cat in ['Calculator', 'Converter', 'Generator', 'Color Tool', 'Text Tool',
                'Game', 'Test/Quiz', 'Template/Printable', 'SVG/Font/Craft',
                'Reference/Comparison', 'Specific Tool', 'Online Tool']:
        sites = by_category.get(cat, [])
        if sites:
            print(f"\n--- {cat} ({len(sites)} sites) ---")
            for s in sorted(sites, key=lambda x: (-priority.get(x['rust_advantage'], 0), -x['domain_quality'])):
                print(f"  [{s['rust_advantage']:6s}] {s['domain']:45s} | {s['tool_type']:30s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    # Save results
    results = {
        'total_publishers': len(publishers),
        'niche_breakdown': {k: v for k, v in sorted(niche_counts.items(), key=lambda x: -x[1]['total'])},
        'tool_sites': tool_sites_deduped,
        'by_category': {k: v for k, v in by_category.items()},
    }

    output_path = CSV_PATH.parent / 'final_tool_sites.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()
