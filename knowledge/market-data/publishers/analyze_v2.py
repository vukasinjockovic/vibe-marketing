#!/usr/bin/env python3
"""
Refined publisher analysis v2 - reduces false positives dramatically.
Uses whole-word matching and domain-specific heuristics.
"""

import csv
import re
import json
from collections import defaultdict
from pathlib import Path

CSV_PATH = Path("/var/www/vibe-marketing/knowledge/market-data/publishers/all_publishers.csv")


def load_publishers():
    publishers = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            publishers.append({
                'domain': row['domain'].strip().strip('"'),
                'name': row['name'].strip().strip('"'),
                'network': row['network'].strip(),
            })
    return publishers


def tokenize_domain(domain):
    """Split domain into meaningful tokens, removing TLD."""
    # Remove TLD
    parts = domain.lower().split('.')
    # Common multi-part TLDs
    multi_tlds = {'co.uk', 'co.nz', 'co.za', 'com.au', 'com.br', 'org.uk'}
    if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in multi_tlds:
        base = '.'.join(parts[:-2])
    elif len(parts) >= 2:
        base = '.'.join(parts[:-1])
    else:
        base = domain.lower()

    # Split on hyphens and dots
    raw_tokens = re.split(r'[-.]', base)

    # Also try to split camelCase-ish patterns in each token
    all_tokens = []
    for t in raw_tokens:
        # Split long tokens on common word boundaries
        sub = re.findall(r'[a-z]+', t.lower())
        all_tokens.extend(sub)

    return all_tokens, base


def is_genuine_tool_site(domain, name):
    """
    Strict check: is this genuinely a tool/utility/calculator/generator site?
    Returns (is_tool, tool_type, confidence) or (False, None, None)
    """
    d = domain.lower()
    n = name.lower()
    tokens, base = tokenize_domain(domain)

    # ===== DEFINITE TOOL SITES (domain strongly indicates a tool) =====

    definite_patterns = [
        # Calculator sites
        (r'calculator\b', 'Calculator', 'High'),
        (r'\bcalc\b', 'Calculator', 'High'),
        (r'calculat[eo]', 'Calculator', 'High'),

        # Converter sites
        (r'\bconvert(?:er|ible)?\b', 'Converter', 'High'),
        (r'conversion', 'Converter', 'Medium'),

        # Generator sites - but NOT "generation" (blog names)
        (r'generator\b', 'Generator', 'High'),
        (r'\bgenerat(?:e|ing)\b', 'Generator', 'Medium'),

        # Online tools
        (r'onlinetools?', 'Online Tool', 'High'),
        (r'freetool', 'Free Tool', 'High'),
        (r'webtool', 'Web Tool', 'High'),

        # Specific tool types
        (r'pdfto|topdf|pdf[-_]?(?:convert|merg|split|edit|compress)', 'PDF Tool', 'High'),
        (r'imag(?:e[-_]?(?:resiz|compress|convert|optim|edit))', 'Image Tool', 'High'),
        (r'photo[-_]?(?:edit|resiz|compress|convert|enhanc)', 'Photo Tool', 'High'),
        (r'video[-_]?(?:convert|compress|edit|download|trim)', 'Video Tool', 'High'),
        (r'audio[-_]?(?:convert|compress|edit|trim|merg)', 'Audio Tool', 'High'),
        (r'color[-_]?pick', 'Color Picker', 'High'),
        (r'rgbcolor', 'Color Tool', 'High'),
        (r'colorpick', 'Color Picker', 'High'),
        (r'palette(?:generat|mak|creat)', 'Palette Generator', 'High'),
        (r'(?:strong|secure|random)?password[-_]?gen', 'Password Generator', 'High'),
        (r'qr[-_]?(?:code)?[-_]?(?:gen|mak|creat|scan)', 'QR Code Tool', 'High'),
        (r'barcode[-_]?(?:gen|mak|creat|scan)', 'Barcode Tool', 'High'),
        (r'(?:json|xml|csv|yaml|html|css)[-_]?(?:format|valid|beautif|minif|lint)', 'Code Formatter', 'High'),
        (r'json[-_]?(?:to|2)[-_]?(?:csv|xml|yaml)', 'Data Converter', 'High'),
        (r'(?:unit|measur)[-_]?convert', 'Unit Converter', 'High'),
        (r'(?:currency|money)[-_]?(?:convert|exchang)', 'Currency Converter', 'High'),
        (r'(?:time[-_]?zone|timezone)[-_]?convert', 'Timezone Converter', 'High'),
        (r'speed[-_]?test', 'Speed Test', 'High'),
        (r'typing[-_]?(?:test|game|speed|practic)', 'Typing Tool', 'High'),
        (r'(?:mic|microphone|webcam|camera)[-_]?test', 'Hardware Test', 'High'),
        (r'screen[-_]?(?:record|captur|shot)', 'Screen Tool', 'High'),
        (r'countdown[-_]?(?:timer|clock)', 'Timer', 'High'),
        (r'stopwatch', 'Stopwatch', 'High'),
        (r'(?:word|character|letter)[-_]?count', 'Word Counter', 'High'),
        (r'(?:word|text|name|team|color|meme|logo|avatar|nickname|username)[-_]?gen', 'Generator', 'High'),
        (r'(?:lorem|ipsum)[-_]?(?:gen|text)', 'Lorem Generator', 'High'),
        (r'(?:random[-_]?)?(?:number|name|word|quote|fact|joke)[-_]?gen', 'Random Generator', 'High'),
        (r'(?:invoice|receipt|resume|cv)[-_]?(?:gen|mak|creat|build|template)', 'Document Generator', 'High'),
        (r'(?:chart|graph|diagram|flowchart)[-_]?(?:mak|creat|build|gen)', 'Chart Maker', 'High'),
        (r'(?:meme|gif)[-_]?(?:mak|creat|gen)', 'Meme/GIF Maker', 'High'),
        (r'(?:collage|mosaic)[-_]?(?:mak|creat)', 'Collage Maker', 'High'),
        (r'(?:font|text)[-_]?(?:gen|mak|creat|identif|find)', 'Font Tool', 'High'),
        (r'text[-_]?to[-_]?(?:speech|voice|audio|image|video|pdf)', 'Text Converter', 'High'),
        (r'speech[-_]?to[-_]?text', 'Speech-to-Text', 'High'),
        (r'(?:ip|dns|whois)[-_]?(?:look|check|find|scan|tool)', 'Network Tool', 'High'),
        (r'(?:seo|keyword|rank|backlink)[-_]?(?:tool|check|analyz|track)', 'SEO Tool', 'High'),
        (r'(?:url|link)[-_]?(?:short|expand|check|valid)', 'URL Tool', 'High'),
        (r'(?:hash|md5|sha)[-_]?(?:gen|calc|check|tool)', 'Hash Tool', 'High'),
        (r'(?:base64|hex|binary|ascii|unicode)[-_]?(?:encod|decod|convert)', 'Encoding Tool', 'High'),
        (r'(?:regex|regexp)[-_]?(?:test|tool|build|check)', 'Regex Tool', 'High'),
        (r'(?:diff|compar)[-_]?(?:tool|check|text|file|code)', 'Diff Tool', 'High'),
        (r'(?:watermark|stamp)[-_]?(?:add|remov|tool)', 'Watermark Tool', 'High'),
        (r'(?:ocr|text[-_]?recogn)', 'OCR Tool', 'High'),
        (r'(?:crop|trim|cut)[-_]?(?:image|photo|video|audio)', 'Cropping Tool', 'High'),
        (r'(?:merge|combine|join)[-_]?(?:pdf|image|video|audio|file)', 'Merger Tool', 'High'),
        (r'(?:split|separate)[-_]?(?:pdf|image|video|audio|file)', 'Splitter Tool', 'High'),
        (r'(?:compress|optimi[zs]e|reduc)[-_]?(?:image|photo|pdf|video|file)', 'Compressor', 'High'),
        (r'(?:download|save|extract)[-_]?(?:video|audio|image|music)', 'Downloader', 'High'),
        (r'(?:translate|translation)[-_]?(?:tool|online|free)', 'Translation Tool', 'High'),
        (r'(?:grammar|spell)[-_]?(?:check|correct|tool)', 'Grammar Checker', 'High'),
        (r'(?:plagiarism|duplicate)[-_]?(?:check|detect|scan)', 'Plagiarism Checker', 'High'),
        (r'(?:readability|flesch)[-_]?(?:check|score|test)', 'Readability Tool', 'High'),
        (r'(?:case|title|upper|lower)[-_]?(?:convert)', 'Case Converter', 'High'),
        (r'(?:age|date|time|bmi|calorie|macro|tdee|body[-_]?fat|pregnancy|due[-_]?date|ovulation)[-_]?calc', 'Health Calculator', 'High'),
        (r'(?:mortgage|loan|interest|compound|tax|salary|pay|tip|discount|percent|margin|markup|roi|break[-_]?even)[-_]?calc', 'Finance Calculator', 'High'),
        (r'(?:gpa|grade|cgpa)[-_]?calc', 'Grade Calculator', 'High'),
        (r'(?:concrete|lumber|roofing|flooring|paint|tile|mulch|gravel|brick|fence|deck|drywall|insulation)[-_]?calc', 'Construction Calculator', 'High'),
        (r'(?:distance|area|volume|perimeter|circumference|radius|diameter|square[-_]?footage)[-_]?calc', 'Math Calculator', 'High'),
    ]

    for pattern, tool_type, confidence in definite_patterns:
        if re.search(pattern, base) or re.search(pattern, d.replace('.', '')):
            return True, tool_type, confidence

    # ===== LIKELY TOOL SITES (need second signal) =====

    # Check for strong tool-indicating whole words in domain
    tool_domain_words = {
        'tool', 'tools', 'utility', 'utilities', 'app', 'apps',
        'online', 'free', 'checker', 'tester', 'analyzer',
        'scanner', 'finder', 'viewer', 'player', 'reader',
        'writer', 'editor', 'maker', 'builder', 'creator',
        'designer', 'planner', 'tracker', 'manager', 'organizer',
        'simulator', 'emulator',
    }

    has_tool_word = bool(set(tokens) & tool_domain_words)

    # Name-based signals
    tool_name_patterns = [
        r'\btool', r'\bcalculator', r'\bconverter', r'\bgenerator',
        r'\bmaker', r'\bbuilder', r'\bcreator', r'\beditor',
        r'\bplanner', r'\btracker', r'\bonline\b.*\btool',
        r'\bfree\b.*\btool', r'\bweb\b.*\btool',
        r'\bapp\b', r'\bsoftware\b', r'\bplatform\b',
    ]

    name_is_tool = any(re.search(p, n) for p in tool_name_patterns)

    if has_tool_word and name_is_tool:
        return True, 'General Tool', 'Medium'

    # ===== SPECIFIC DOMAIN NAME PATTERNS =====

    # Sites ending in common tool patterns
    tool_suffix_patterns = [
        (r'(?:tools?|utils?|utilities)\.', 'Tool Site', 'Medium'),
        (r'\.tools?$', 'Tool Site', 'Medium'),
        (r'(?:online|web|free|my|the)(?:calc|convert|gen|tool|edit|check|test)', 'Online Tool', 'Medium'),
    ]

    for pattern, tool_type, confidence in tool_suffix_patterns:
        if re.search(pattern, d):
            return True, tool_type, confidence

    return False, None, None


def is_genuine_game_site(domain, name):
    """Check if site is genuinely a game/quiz/puzzle site."""
    d = domain.lower()
    n = name.lower()
    tokens, base = tokenize_domain(domain)

    game_patterns = [
        (r'\bgame(?:s)?\b', 'Browser Game', 'High'),
        (r'\bpuzzle(?:s)?\b', 'Puzzle Game', 'High'),
        (r'\bquiz(?:zes?)?\b', 'Quiz', 'High'),
        (r'\btrivia\b', 'Trivia', 'High'),
        (r'\bwordle\b', 'Word Game', 'High'),
        (r'\bcrossword\b', 'Crossword', 'High'),
        (r'\bsudoku\b', 'Sudoku', 'High'),
        (r'\bsolitaire\b', 'Solitaire', 'High'),
        (r'\bchess\b', 'Chess', 'High'),
        (r'\bmahjong\b', 'Mahjong', 'High'),
        (r'\barcade\b', 'Arcade Game', 'High'),
        (r'\bcoloring\b', 'Coloring', 'Medium'),
        (r'\bjigsaw\b', 'Jigsaw Puzzle', 'High'),
        (r'\bword[-_]?(?:game|search|find|scrambl)', 'Word Game', 'High'),
        (r'\bbrain[-_]?(?:game|teaser|train)', 'Brain Game', 'High'),
        (r'\btyping[-_]?game', 'Typing Game', 'High'),
        (r'\bmath[-_]?game', 'Math Game', 'High'),
        (r'\bmemory[-_]?game', 'Memory Game', 'High'),
        (r'\bcard[-_]?game', 'Card Game', 'High'),
        (r'\bboard[-_]?game', 'Board Game', 'Medium'),
        (r'\bplay(?:able|ground|er)?\b', 'Game', 'Low'),
        (r'\bidle[-_]?(?:game|click)', 'Idle Game', 'High'),
        (r'\b\.io\b', 'IO Game', 'Medium'),
    ]

    for pattern, game_type, confidence in game_patterns:
        if re.search(pattern, base):
            return True, game_type, confidence

    # Check name for game indicators
    name_game_patterns = [
        (r'\bgame', 'Game Site', 'Medium'),
        (r'\bpuzzle', 'Puzzle Site', 'Medium'),
        (r'\bquiz', 'Quiz Site', 'Medium'),
        (r'\bplay\b', 'Game Site', 'Low'),
    ]

    for pattern, game_type, confidence in name_game_patterns:
        if re.search(pattern, n):
            # Verify domain also hints at games (not just a name coincidence)
            if any(w in tokens for w in ['game', 'games', 'play', 'puzzle', 'quiz', 'trivia', 'word', 'brain']):
                return True, game_type, confidence

    return False, None, None


def is_genuine_calculator_site(domain, name):
    """Check specifically for calculator/finance tool sites."""
    d = domain.lower()
    n = name.lower()
    tokens, base = tokenize_domain(domain)

    calc_patterns = [
        # Pure calculator sites
        (r'calculator', 'Calculator Site', 'High'),
        (r'\bcalc\b', 'Calculator', 'High'),
        (r'calculate', 'Calculator', 'High'),

        # Finance-specific calculators
        (r'mortgage[-_]?calc', 'Mortgage Calculator', 'High'),
        (r'loan[-_]?calc', 'Loan Calculator', 'High'),
        (r'invest[-_]?(?:ment)?[-_]?calc', 'Investment Calculator', 'High'),
        (r'(?:compound[-_]?)?interest[-_]?calc', 'Interest Calculator', 'High'),
        (r'tax[-_]?calc', 'Tax Calculator', 'High'),
        (r'salary[-_]?calc', 'Salary Calculator', 'High'),
        (r'pay[-_]?calc', 'Pay Calculator', 'High'),
        (r'(?:retirement|pension|401k|ira)[-_]?calc', 'Retirement Calculator', 'High'),
        (r'budget[-_]?(?:calc|tool|planner|app)', 'Budget Tool', 'High'),

        # Health calculators
        (r'bmi[-_]?calc', 'BMI Calculator', 'High'),
        (r'calorie[-_]?calc', 'Calorie Calculator', 'High'),
        (r'tdee[-_]?calc', 'TDEE Calculator', 'High'),
        (r'macro[-_]?calc', 'Macro Calculator', 'High'),
        (r'(?:body[-_]?fat|bf)[-_]?calc', 'Body Fat Calculator', 'High'),
        (r'(?:due[-_]?date|pregnancy)[-_]?calc', 'Pregnancy Calculator', 'High'),
        (r'(?:ovulation|fertility)[-_]?calc', 'Ovulation Calculator', 'High'),
        (r'(?:puppy|dog|cat|pet)[-_]?(?:weight)?[-_]?calc', 'Pet Calculator', 'High'),

        # Construction/home calculators
        (r'(?:concrete|lumber|roof|floor|paint|tile|mulch|gravel|fence|deck|sq[-_]?ft|square[-_]?foot)[-_]?calc', 'Construction Calculator', 'High'),
        (r'(?:inch|cm|mm|feet|meter|yard|mile|km)[-_]?calc', 'Measurement Calculator', 'High'),

        # Academic calculators
        (r'(?:gpa|grade|cgpa|sat|act|gre|gmat)[-_]?calc', 'Academic Calculator', 'High'),

        # Fantasy/sports calculators
        (r'(?:fantasy|draft|trade)[-_]?calc', 'Fantasy Calculator', 'High'),
        (r'(?:point|score)[-_]?calc', 'Points Calculator', 'High'),
    ]

    for pattern, calc_type, confidence in calc_patterns:
        if re.search(pattern, base):
            return True, calc_type, confidence

    return False, None, None


def is_practice_test_site(domain, name):
    """Check if site is a practice test/exam prep site."""
    d = domain.lower()
    tokens, base = tokenize_domain(domain)

    test_patterns = [
        (r'practice[-_]?(?:test|exam|quiz)', 'Practice Test Site', 'High'),
        (r'(?:test|exam)[-_]?(?:prep|practic|review|study)', 'Test Prep Site', 'High'),
        (r'(?:free|online|sample)[-_]?(?:test|exam|quiz)', 'Test Site', 'High'),
        (r'(?:mock|sample|demo)[-_]?(?:test|exam)', 'Mock Test Site', 'High'),
        (r'(?:cna|rbt|pert|tsi|hesi|nclex|asvab|ged|hiset|aswb|pmp|ccma|ptcb|servsafe|az900|nremt|siepr|phlebotomy|accuplacer|workkeys|parapro).*(?:test|exam|practic)', 'Certification Test Prep', 'High'),
        (r'(?:test|exam).*(?:cna|rbt|pert|tsi|hesi|nclex|asvab|ged|hiset|aswb|pmp|ccma|ptcb|servsafe|az900|nremt)', 'Certification Test Prep', 'High'),
        (r'(?:career|aptitude|personality|iq|eq|ennea)[-_]?test', 'Assessment Test', 'High'),
        (r'(?:spirit[-_]?animal|color[-_]?personality|mbti|disc)[-_]?test', 'Personality Quiz', 'High'),
        (r'frame[-_]?rate[-_]?test', 'FPS Test', 'High'),
        (r'(?:mic|webcam|keyboard|mouse|monitor|speaker|headphone)[-_]?test', 'Hardware Test', 'High'),
    ]

    for pattern, test_type, confidence in test_patterns:
        if re.search(pattern, base):
            return True, test_type, confidence

    return False, None, None


def is_template_site(domain, name):
    """Check for template/printable sites."""
    d = domain.lower()
    tokens, base = tokenize_domain(domain)

    patterns = [
        (r'template', 'Template Site', 'High'),
        (r'printable', 'Printable Site', 'High'),
        (r'worksheet', 'Worksheet Site', 'High'),
        (r'(?:resume|cv)[-_]?(?:build|mak|creat|template)', 'Resume Builder', 'High'),
        (r'(?:invoice|receipt)[-_]?(?:gen|mak|creat|template)', 'Invoice Generator', 'High'),
        (r'(?:flashcard|flash[-_]?card)', 'Flashcard Tool', 'High'),
        (r'(?:svg|design|craft)[-_]?(?:file|cut|template)', 'SVG/Craft File Site', 'Medium'),
    ]

    for pattern, site_type, confidence in patterns:
        if re.search(pattern, base):
            return True, site_type, confidence

    return False, None, None


def is_converter_reference_site(domain, name):
    """Check for conversion/reference/lookup sites."""
    d = domain.lower()
    tokens, base = tokenize_domain(domain)

    patterns = [
        (r'convert[-_]?(?:binary|hex|ascii|unicode|unit|measur|currency|temp)', 'Converter', 'High'),
        (r'(?:binary|hex|ascii|unicode|unit|measur|currency|temp)[-_]?convert', 'Converter', 'High'),
        (r'(?:inch|cm|feet|meter|kg|lb|oz|ml|cup|gallon|liter|fahrenheit|celsius)[-_]?(?:to|2)[-_]?', 'Unit Converter', 'High'),
        (r'titlecase[-_]?convert', 'Text Converter', 'High'),
        (r'(?:case|text)[-_]?convert', 'Text Converter', 'High'),
        (r'(?:diffen|versus|compare)', 'Comparison Site', 'High'),
        (r'(?:travel|distance)[-_]?math', 'Travel Calculator', 'High'),
    ]

    for pattern, site_type, confidence in patterns:
        if re.search(pattern, base):
            return True, site_type, confidence

    return False, None, None


def is_svg_craft_site(domain, name):
    """Check for SVG/craft file sites (downloadable templates for Cricut etc.)."""
    d = domain.lower()
    tokens, base = tokenize_domain(domain)

    patterns = [
        (r'\bsvg\b', 'SVG File Site', 'High'),
        (r'freesvg', 'Free SVG Site', 'High'),
        (r'svgfile', 'SVG File Site', 'High'),
        (r'(?:cricut|silhouette)[-_]?(?:file|template|design|cut)', 'Craft File Site', 'High'),
        (r'(?:free[-_]?)?(?:font|fonts)\b', 'Font Site', 'Medium'),
    ]

    for pattern, site_type, confidence in patterns:
        if re.search(pattern, base):
            return True, site_type, confidence

    return False, None, None


def comprehensive_categorize(domain, name):
    """
    Multi-pass categorization that's more accurate.
    Returns primary category and any special tool/game designations.
    """
    d = domain.lower()
    n = name.lower()
    tokens, base = tokenize_domain(domain)
    combined = f"{base} {n}"

    # ===== NICHE CATEGORIZATION (broad) =====
    # Order matters - more specific first

    niche_rules = [
        # Food/Recipe - very common in ad networks
        ('Food/Recipe', [
            r'\b(?:recipe|cook|bake|kitchen|food|foodie|meal|dinner|lunch|breakfast|brunch|dessert|cake|cookie|bread|pasta|pizza|soup|salad|grill|bbq|barbecue|roast|chef|culinary|restaur|bistro|cafe|coffee|tea|wine|beer|cocktail|smoothie|chocolate|candy|spice|flavor|yummy|delicious|tasty|eat|eater|feast|dine)\b',
        ]),
        # Travel
        ('Travel', [
            r'\b(?:travel|trip|vacation|holiday|tour|tourism|destination|adventure|wander|nomad|backpack|hostel|hotel|resort|flight|airline|cruise|passport|expat|abroad)\b',
        ]),
        # Finance
        ('Finance/Calculators', [
            r'\b(?:mortgage|invest|stock|crypto|bitcoin|forex|trading|broker|bank|credit|tax|retirement|pension|401k|savings|compound|dividend|payroll|salary|debt|refinanc|insurance|budget|frugal|coupon|cashback|finance|financial|fintech|money|wealth|accounti|bookkeep)\b',
        ]),
        # Health/Fitness
        ('Health/Fitness', [
            r'\b(?:bmi|calorie|workout|exercise|fitness|gym|yoga|pilates|crossfit|cardio|strength|muscle|protein|macro|keto|paleo|diet|weight[-_]?loss|supplement|vitamin|nutrition|health|wellness|medical|doctor|nurse|symptom|therapy|mental|anxiety|depression|meditat|mindful|pregnancy|prenatal|fertility|ovulation|running|marathon)\b',
        ]),
        # Parenting
        ('Parenting/Family', [
            r'\b(?:parent|mom|mum|mama|mother|dad|papa|father|baby|infant|toddler|child|kid|teen|family|pregnant|newborn|nursery|diaper|breastfeed|milestone|daycare|nanny|playdate|toy)\b',
        ]),
        # Education
        ('Education/Learning', [
            r'\b(?:learn|teach|tutor|course|lesson|study|student|school|college|university|academy|education|edtech|certification|exam|grade|gpa|sat|act|gre|math|science|physics|chemistry|biology|history|geography|english|grammar|spelling|vocabulary|homework|essay|thesis|flashcard|worksheet|printable|stem|tutorial|homeschool|preschool|kindergarten)\b',
        ]),
        # DIY/Home/Garden
        ('DIY/Home', [
            r'\b(?:diy|craft|handmade|woodwork|furniture|decor|interior|remodel|renovate|repair|plumb|electric|roof|floor|wall|paint|tile|cabinet|bathroom|landscape|garden|plant|flower|lawn|seed|soil|homestead|farmhouse|cleaning|clean|organize|declutter|storage|sew|sewing|knit|crochet|quilt|embroider|yarn|fabric)\b',
        ]),
        # Fashion/Beauty
        ('Fashion/Beauty', [
            r'\b(?:fashion|style|clothing|outfit|dress|wardrobe|trend|designer|boutique|beauty|makeup|cosmetic|skincare|hair|nail|fragrance|perfume|jewelry|accessory|shoe|sneaker)\b',
        ]),
        # Tech/Programming
        ('Tech/Programming', [
            r'\b(?:tech|technology|software|hardware|computer|laptop|server|cloud|saas|api|database|python|javascript|typescript|react|vue|angular|node|rust|golang|java|kotlin|swift|php|laravel|wordpress|linux|windows|macos|ios|android|app|web|ai|machine[-_]?learning|deep[-_]?learning|neural|cybersecurity|gadget|device|iot|smart|developer|engineer|coder|programmer|startup)\b',
        ]),
        # Pets
        ('Pets/Animals', [
            r'\b(?:pet|dog|puppy|cat|kitten|bird|fish|reptile|hamster|rabbit|bunny|horse|aquarium|vet|veterinar|breed|adopt|rescue|paw|fur|bark|meow)\b',
        ]),
        # Automotive
        ('Automotive', [
            r'\b(?:car|auto(?!mat)|vehicle|truck|suv|motorcycle|bike|scooter|tesla|ford|toyota|honda|bmw|mercedes|mechanic|tire|brake|engine)\b',
        ]),
        # Sports
        ('Sports/Outdoors', [
            r'\b(?:sport|football|soccer|basketball|baseball|hockey|tennis|golf|swimming|cycling|boxing|mma|ufc|wrestling|volleyball|cricket|rugby|nfl|nba|mlb|nhl|athlete|fantasy[-_]?(?:sport|football|basketball|baseball)|hunting|fishing|hiking|climbing|skiing|snowboard|surf|skateboard)\b',
        ]),
        # Photography
        ('Photography', [
            r'\b(?:photograph|camera|lens|dslr|mirrorless|canon|nikon|lightroom|photoshop|portrait|landscape[-_]?photo)\b',
        ]),
        # Music
        ('Music/Audio', [
            r'\b(?:music|song|sing|guitar|piano|drum|violin|cello|chord|lyric|melody|band|concert|album|playlist|producer|dj|mixing|recording|podcast|radio)\b',
        ]),
        # Games/Entertainment
        ('Games/Entertainment', [
            r'\b(?:game|gaming|gamer|puzzle|quiz|trivia|wordle|crossword|sudoku|solitaire|chess|mahjong|arcade|play|esport|twitch|stream|anime|manga|comic|meme|humor|funny|entertainment)\b',
        ]),
    ]

    primary_niche = 'Other'
    max_matches = 0

    for niche, patterns in niche_rules:
        match_count = 0
        for p in patterns:
            matches = re.findall(p, combined)
            match_count += len(matches)
        if match_count > max_matches:
            max_matches = match_count
            primary_niche = niche

    return primary_niche


def rate_rust_advantage(tool_type):
    """Rate how much Rust/WASM would benefit this tool type."""
    high_rust = [
        'PDF Tool', 'Image Tool', 'Photo Tool', 'Video Tool', 'Audio Tool',
        'Compressor', 'Optimizer/Compressor', 'Resizer', 'Converter',
        'OCR Tool', 'Hash Tool', 'Encoding Tool', 'Encryption Tool',
        'QR Code Tool', 'Barcode Tool', 'SVG Tool', 'Data Converter',
        'Unit Converter', 'Currency Converter', 'Code Formatter',
        'Diff Tool', 'Merger Tool', 'Splitter Tool', 'Cropping Tool',
        'Watermark Tool', 'Collage Maker', 'Meme/GIF Maker',
        'Screen Tool', 'Text Converter', 'Speech-to-Text',
        'Speed Test', 'Password Generator', 'Random Generator',
        'Generator', 'Calculator', 'Calculator Site',
    ]

    medium_rust = [
        'Typing Tool', 'Typing Game', 'Color Picker', 'Color Tool',
        'Palette Generator', 'Font Tool', 'Chart Maker',
        'Document Generator', 'Resume Builder', 'Invoice Generator',
        'Template Site', 'Printable Site', 'Worksheet Site',
        'Grammar Checker', 'Plagiarism Checker', 'Readability Tool',
        'Case Converter', 'Text Converter', 'Word Counter',
        'Timer', 'Stopwatch', 'Browser Game', 'Puzzle Game',
        'Word Game', 'Math Game', 'Brain Game', 'Crossword',
        'Sudoku', 'Solitaire', 'Chess', 'Mahjong',
        'Finance Calculator', 'Mortgage Calculator', 'Loan Calculator',
        'Investment Calculator', 'Tax Calculator', 'Health Calculator',
        'BMI Calculator', 'Calorie Calculator', 'TDEE Calculator',
        'Construction Calculator', 'Academic Calculator',
        'Travel Calculator', 'Comparison Site',
        'Hardware Test', 'FPS Test',
    ]

    low_rust = [
        'Practice Test Site', 'Test Prep Site', 'Mock Test Site',
        'Certification Test Prep', 'Assessment Test', 'Personality Quiz',
        'SVG File Site', 'Free SVG Site', 'Craft File Site',
        'Font Site', 'Flashcard Tool', 'Quiz', 'Trivia',
        'Online Tool', 'Free Tool', 'Web Tool', 'General Tool',
        'Tool Site', 'Network Tool', 'SEO Tool', 'URL Tool',
        'Regex Tool', 'Downloader', 'Translation Tool',
    ]

    if tool_type in high_rust:
        return 'High'
    elif tool_type in medium_rust:
        return 'Medium'
    elif tool_type in low_rust:
        return 'Low'
    return 'Low'


def assess_domain_quality(domain):
    """Rate domain quality for SEO/branding."""
    d = domain.lower()
    score = 50  # baseline

    # Short domains are more valuable
    base = d.split('.')[0]
    if len(base) <= 6:
        score += 20
    elif len(base) <= 10:
        score += 10
    elif len(base) <= 15:
        score += 5
    elif len(base) > 25:
        score -= 10

    # .com is most valuable
    if d.endswith('.com'):
        score += 15
    elif d.endswith('.org') or d.endswith('.net'):
        score += 10
    elif d.endswith('.io') or d.endswith('.co'):
        score += 8
    elif d.endswith('.me') or d.endswith('.app') or d.endswith('.tools'):
        score += 5
    else:
        score += 0

    # Exact match domains (the domain IS the tool name)
    exact_match_patterns = [
        r'^(?:the)?(?:calc|convert|generat|compress|resize|optimi|format|merge|split|crop|hash|encode|decode)',
        r'calculator\.',
        r'converter\.',
        r'generator\.',
    ]
    for p in exact_match_patterns:
        if re.search(p, d):
            score += 15
            break

    # Penalize very complex/long domains
    if d.count('-') > 3:
        score -= 10
    if d.count('.') > 2:
        score -= 5

    return min(100, max(0, score))


def main():
    print("Loading publishers...")
    publishers = load_publishers()
    print(f"Loaded {len(publishers)} publishers")

    # Categorize all publishers
    niche_counts = defaultdict(lambda: {'total': 0, 'mediavine': 0, 'raptive': 0, 'domains': []})

    # Specialized site lists
    tool_sites = []
    game_sites = []
    calculator_sites = []
    test_prep_sites = []
    template_sites = []
    converter_sites = []
    svg_craft_sites = []
    programmatic_seo = []

    for pub in publishers:
        domain = pub['domain']
        name = pub['name']
        network = pub['network']

        # Broad niche
        niche = comprehensive_categorize(domain, name)
        niche_counts[niche]['total'] += 1
        niche_counts[niche][network] += 1
        niche_counts[niche]['domains'].append(domain)

        # Check for specific tool types
        is_tool, tool_type, tool_conf = is_genuine_tool_site(domain, name)
        is_game, game_type, game_conf = is_genuine_game_site(domain, name)
        is_calc, calc_type, calc_conf = is_genuine_calculator_site(domain, name)
        is_test, test_type, test_conf = is_practice_test_site(domain, name)
        is_tmpl, tmpl_type, tmpl_conf = is_template_site(domain, name)
        is_conv, conv_type, conv_conf = is_converter_reference_site(domain, name)
        is_svg, svg_type, svg_conf = is_svg_craft_site(domain, name)

        entry = {
            'domain': domain,
            'name': name,
            'network': network,
            'niche': niche,
        }

        if is_tool:
            rust_adv = rate_rust_advantage(tool_type)
            dom_quality = assess_domain_quality(domain)
            tool_sites.append({
                **entry,
                'tool_type': tool_type,
                'confidence': tool_conf,
                'rust_advantage': rust_adv,
                'domain_quality': dom_quality,
            })

        if is_game:
            rust_adv = rate_rust_advantage(game_type)
            dom_quality = assess_domain_quality(domain)
            game_sites.append({
                **entry,
                'game_type': game_type,
                'confidence': game_conf,
                'rust_advantage': rust_adv,
                'domain_quality': dom_quality,
            })

        if is_calc:
            rust_adv = rate_rust_advantage(calc_type)
            dom_quality = assess_domain_quality(domain)
            calculator_sites.append({
                **entry,
                'calc_type': calc_type,
                'confidence': calc_conf,
                'rust_advantage': rust_adv,
                'domain_quality': dom_quality,
            })

        if is_test:
            dom_quality = assess_domain_quality(domain)
            test_prep_sites.append({
                **entry,
                'test_type': test_type,
                'confidence': test_conf,
                'domain_quality': dom_quality,
            })

        if is_tmpl:
            dom_quality = assess_domain_quality(domain)
            template_sites.append({
                **entry,
                'template_type': tmpl_type,
                'confidence': tmpl_conf,
                'domain_quality': dom_quality,
            })

        if is_conv:
            rust_adv = rate_rust_advantage(conv_type)
            dom_quality = assess_domain_quality(domain)
            converter_sites.append({
                **entry,
                'converter_type': conv_type,
                'confidence': conv_conf,
                'rust_advantage': rust_adv,
                'domain_quality': dom_quality,
            })

        if is_svg:
            dom_quality = assess_domain_quality(domain)
            svg_craft_sites.append({
                **entry,
                'svg_type': svg_type,
                'confidence': svg_conf,
                'domain_quality': dom_quality,
            })

        # Programmatic SEO potential
        d_lower = domain.lower()
        _, base = tokenize_domain(domain)
        seo_signals = []

        seo_checks = [
            ('Template-based', r'(?:template|printable|worksheet|flashcard|resume|invoice|card|flyer|poster|banner|mockup|coloring[-_]?page)'),
            ('Location-based', r'(?:local|city|state|country|weather|zip|area|region|near[-_]?me|[a-z]+[-_]?(?:city|county|state))'),
            ('Calculator-based', r'(?:calc|comput|estima|formula|equation)'),
            ('Conversion-based', r'(?:convert|unit|measur|exchange|rate|currency|translat)'),
            ('Generator-based', r'(?:generat|creat|maker|builder|random)'),
            ('Comparison/Review', r'(?:compar|versus|vs|differ|review|best|top[-_]?\d|rank|rate|altern)'),
            ('Data/Reference', r'(?:stat|data|fact|number|census|average|median|diction|encyclopedia|wiki|glossary|reference|define|meaning|synonym)'),
            ('Practice Test', r'(?:practice[-_]?test|exam[-_]?prep|test[-_]?prep|mock[-_]?test|sample[-_]?test)'),
        ]

        for seo_type, pattern in seo_checks:
            if re.search(pattern, base):
                seo_signals.append(seo_type)

        if seo_signals:
            programmatic_seo.append({
                **entry,
                'seo_types': seo_signals,
            })

    # ===== OUTPUT =====

    results = {
        'total_publishers': len(publishers),
        'niche_breakdown': {},
        'tool_sites': tool_sites,
        'game_sites': game_sites,
        'calculator_sites': calculator_sites,
        'test_prep_sites': test_prep_sites,
        'template_sites': template_sites,
        'converter_sites': converter_sites,
        'svg_craft_sites': svg_craft_sites,
        'programmatic_seo': programmatic_seo,
    }

    # Niche breakdown
    for niche in sorted(niche_counts.keys(), key=lambda x: -niche_counts[x]['total']):
        info = niche_counts[niche]
        results['niche_breakdown'][niche] = {
            'total': info['total'],
            'mediavine': info['mediavine'],
            'raptive': info['raptive'],
            'sample_domains': info['domains'][:25],
        }

    # Print summary
    print("\n" + "="*80)
    print("REFINED PUBLISHER ANALYSIS")
    print("="*80)

    print(f"\nTotal: {len(publishers)} publishers")
    print(f"\n{'Category':<30s} {'Total':>6s} {'MV':>6s} {'RP':>6s}")
    print("-"*50)
    for niche in sorted(niche_counts.keys(), key=lambda x: -niche_counts[x]['total']):
        info = niche_counts[niche]
        print(f"{niche:<30s} {info['total']:>6d} {info['mediavine']:>6d} {info['raptive']:>6d}")

    print(f"\n{'='*80}")
    print(f"TOOL/UTILITY SITES: {len(tool_sites)}")
    print(f"{'='*80}")
    for s in sorted(tool_sites, key=lambda x: (-{'High':3,'Medium':2,'Low':1}.get(x['rust_advantage'],0), -x['domain_quality'])):
        print(f"  [{s['rust_advantage']:6s}] {s['domain']:45s} | {s['tool_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"CALCULATOR SITES: {len(calculator_sites)}")
    print(f"{'='*80}")
    for s in sorted(calculator_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['calc_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"GAME/QUIZ SITES: {len(game_sites)}")
    print(f"{'='*80}")
    for s in sorted(game_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['game_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"TEST PREP SITES: {len(test_prep_sites)}")
    print(f"{'='*80}")
    for s in sorted(test_prep_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['test_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"TEMPLATE/PRINTABLE SITES: {len(template_sites)}")
    print(f"{'='*80}")
    for s in sorted(template_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['template_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"CONVERTER SITES: {len(converter_sites)}")
    print(f"{'='*80}")
    for s in sorted(converter_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['converter_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"SVG/CRAFT FILE SITES: {len(svg_craft_sites)}")
    print(f"{'='*80}")
    for s in sorted(svg_craft_sites, key=lambda x: -x['domain_quality']):
        print(f"  {s['domain']:45s} | {s['svg_type']:25s} | {s['network']:10s} | DQ:{s['domain_quality']}")

    print(f"\n{'='*80}")
    print(f"PROGRAMMATIC SEO OPPORTUNITIES: {len(programmatic_seo)}")
    print(f"{'='*80}")
    for s in sorted(programmatic_seo, key=lambda x: -len(x['seo_types']))[:50]:
        print(f"  {s['domain']:45s} | {', '.join(s['seo_types'])}")

    # Save
    output_path = CSV_PATH.parent / 'analysis_v2_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return results


if __name__ == '__main__':
    main()
