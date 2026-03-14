#!/usr/bin/env python3
"""
Comprehensive publisher analysis for Rust rebuild opportunities.
Analyzes all 20,726 publishers from Mediavine + Raptive networks.
"""

import csv
import re
import json
from collections import defaultdict, Counter
from pathlib import Path

CSV_PATH = Path("/var/www/vibe-marketing/knowledge/market-data/publishers/all_publishers.csv")

# ─── Keyword patterns for categorization ───

TOOL_KEYWORDS = [
    'calc', 'calculator', 'converter', 'generator', 'maker', 'builder',
    'creator', 'editor', 'tool', 'app', 'online', 'pdf', 'image', 'photo',
    'video', 'audio', 'text', 'code', 'planner', 'tracker', 'timer',
    'counter', 'chart', 'graph', 'draw', 'design', 'template', 'resume',
    'invoice', 'budget', 'convert', 'translate', 'check', 'test', 'scan',
    'analyze', 'compare', 'resize', 'compress', 'merge', 'split', 'crop',
    'optimize', 'minify', 'format', 'encode', 'decode', 'hash', 'encrypt',
    'qr', 'barcode', 'color', 'picker', 'palette', 'font', 'icon',
    'emoji', 'meme', 'gif', 'svg', 'css', 'html', 'json', 'xml', 'csv',
    'markdown', 'regex', 'ip', 'dns', 'whois', 'speed', 'typing',
    'password', 'random', 'lorem', 'placeholder', 'mockup', 'wireframe',
    'flowchart', 'diagram', 'mindmap', 'sitemap', 'schema', 'validator',
    'lint', 'beautif', 'prettif', 'diff', 'snippet', 'embed', 'widget',
    'screensho', 'screen', 'webcam', 'record', 'capture', 'download',
    'extract', 'scrape', 'crawl', 'proxy', 'vpn', 'shortener', 'shorten',
    'unshorten', 'expand', 'tinyurl', 'bitly', 'utm', 'pixel',
    'watermark', 'stamp', 'signature', 'sign', 'esign', 'ocr',
    'transcri', 'subtitle', 'caption', 'speech', 'tts', 'stt',
    'voiceover', 'dictation', 'pronunci',
]

GAME_KEYWORDS = [
    'game', 'quiz', 'puzzle', 'trivia', 'word', 'sudoku', 'crossword',
    'solitaire', 'chess', 'checkers', 'mahjong', 'tetris', 'snake',
    'pacman', 'arcade', 'play', 'score', 'level', 'quest', 'adventure',
    'rpg', 'mmorpg', 'multiplayer', 'io-game', 'iogame', 'idle',
    'clicker', 'tap', 'swipe', 'match', 'bubble', 'shooter', 'tower',
    'defense', 'strategy', 'board', 'card', 'dice', 'spin', 'slot',
    'casino', 'poker', 'blackjack', 'roulette', 'bingo', 'lottery',
    'scratch', 'wordle', 'riddle', 'brain', 'memory', 'logic',
    'escape', 'hidden', 'findthe', 'spot', 'jigsaw', 'coloring',
    'painting', 'drawing', 'doodle', 'pixel-art',
]

FINANCE_KEYWORDS = [
    'mortgage', 'loan', 'invest', 'stock', 'crypto', 'bitcoin', 'forex',
    'trading', 'broker', 'bank', 'credit', 'debit', 'tax', 'irs',
    'retirement', 'pension', '401k', 'ira', 'roth', 'savings', 'interest',
    'compound', 'amortiz', 'annuit', 'dividend', 'yield', 'roi',
    'profit', 'revenue', 'expense', 'payroll', 'salary', 'wage',
    'income', 'net-worth', 'networth', 'debt', 'payoff', 'refinanc',
    'insurance', 'premium', 'deductible', 'copay', 'hsa', 'fsa',
    'budget', 'frugal', 'coupon', 'deal', 'discount', 'cashback',
    'rewards', 'points', 'miles', 'finance', 'financial', 'fintech',
    'money', 'wealth', 'rich', 'millionaire', 'billionaire',
    'accounti', 'bookkeep', 'quickbooks', 'invoice', 'billing',
    'payment', 'checkout', 'stripe', 'paypal', 'venmo', 'zelle',
]

HEALTH_FITNESS_KEYWORDS = [
    'bmi', 'calorie', 'workout', 'exercise', 'fitness', 'gym', 'yoga',
    'pilates', 'crossfit', 'hiit', 'cardio', 'strength', 'muscle',
    'protein', 'macro', 'keto', 'paleo', 'vegan', 'vegetarian',
    'diet', 'weight', 'fat', 'lean', 'bulk', 'cut', 'shred',
    'supplement', 'vitamin', 'mineral', 'nutrition', 'nutrient',
    'health', 'wellness', 'medical', 'doctor', 'nurse', 'hospital',
    'clinic', 'pharmacy', 'drug', 'medication', 'prescription',
    'symptom', 'diagnosis', 'treatment', 'therapy', 'rehab',
    'mental', 'anxiety', 'depression', 'stress', 'sleep', 'insomnia',
    'meditat', 'mindful', 'breathing', 'relax', 'calm',
    'pregnancy', 'prenatal', 'postnatal', 'fertility', 'ovulation',
    'period', 'menstrual', 'cycle', 'hormone', 'thyroid',
    'blood-pressure', 'bloodpressure', 'cholesterol', 'diabetes',
    'insulin', 'glucose', 'a1c', 'heart-rate', 'heartrate',
    'step-counter', 'pedometer', 'running', 'marathon', 'triathlon',
]

FOOD_RECIPE_KEYWORDS = [
    'recipe', 'cook', 'bake', 'kitchen', 'food', 'meal', 'dinner',
    'lunch', 'breakfast', 'brunch', 'snack', 'dessert', 'cake',
    'cookie', 'bread', 'pasta', 'pizza', 'soup', 'salad', 'grill',
    'bbq', 'barbecue', 'smoke', 'roast', 'fry', 'stir', 'saut',
    'boil', 'steam', 'slow-cook', 'instant-pot', 'airfryer', 'air-fryer',
    'crockpot', 'oven', 'microwave', 'blender', 'juicer', 'mixer',
    'foodie', 'chef', 'culinary', 'gastronom', 'restaur', 'bistro',
    'cafe', 'coffee', 'tea', 'wine', 'beer', 'cocktail', 'drink',
    'beverage', 'smoothie', 'juice', 'lemonade', 'chocolate',
    'candy', 'sugar', 'flour', 'butter', 'cream', 'cheese',
    'spice', 'herb', 'season', 'flavor', 'taste', 'yummy', 'delicious',
    'tasty', 'nom', 'eat', 'eater', 'eating', 'feast', 'dine',
]

EDUCATION_KEYWORDS = [
    'learn', 'teach', 'tutor', 'course', 'class', 'lesson', 'lecture',
    'study', 'student', 'school', 'college', 'university', 'academy',
    'institut', 'education', 'edtech', 'elearn', 'online-learning',
    'mooc', 'certification', 'diploma', 'degree', 'exam', 'test',
    'quiz', 'assessment', 'grade', 'gpa', 'sat', 'act', 'gre', 'gmat',
    'lsat', 'mcat', 'toefl', 'ielts', 'math', 'science', 'physics',
    'chemistry', 'biology', 'history', 'geography', 'english',
    'grammar', 'spelling', 'vocabulary', 'reading', 'writing',
    'homework', 'assignment', 'essay', 'thesis', 'research',
    'flashcard', 'note', 'summary', 'outline', 'cheatsheet',
    'worksheet', 'printable', 'activity', 'experiment', 'project',
    'stem', 'coding', 'programming', 'python', 'javascript',
    'tutorial', 'howto', 'how-to', 'guide', 'handbook', 'manual',
    'reference', 'encyclopedia', 'dictionary', 'glossary', 'wiki',
    'homeschool', 'preschool', 'kindergarten', 'elementary',
    'middle-school', 'high-school', 'k12',
]

DIY_HOME_KEYWORDS = [
    'diy', 'craft', 'handmade', 'homemade', 'woodwork', 'wood',
    'carpentry', 'furniture', 'decor', 'decorat', 'interior',
    'exterior', 'home', 'house', 'apartment', 'condo', 'property',
    'real-estate', 'realestate', 'remodel', 'renovate', 'repair',
    'fix', 'plumb', 'electric', 'hvac', 'roof', 'floor', 'wall',
    'paint', 'tile', 'cabinet', 'counter', 'bathroom', 'kitchen',
    'bedroom', 'living-room', 'garage', 'basement', 'attic',
    'patio', 'deck', 'fence', 'landscape', 'garden', 'plant',
    'flower', 'tree', 'shrub', 'lawn', 'mow', 'seed', 'soil',
    'compost', 'mulch', 'organic', 'permaculture', 'homestead',
    'farmhouse', 'cottage', 'cabin', 'tiny-house', 'van-life',
    'rv', 'camper', 'camping', 'outdoor', 'backyard', 'porch',
    'cleaning', 'clean', 'tidy', 'organize', 'declutter', 'minimal',
    'storage', 'closet', 'shelf', 'container', 'bin', 'basket',
    'laundry', 'stain', 'sew', 'sewing', 'knit', 'crochet',
    'quilt', 'embroider', 'needle', 'yarn', 'fabric', 'pattern',
]

TRAVEL_KEYWORDS = [
    'travel', 'trip', 'vacation', 'holiday', 'tour', 'tourism',
    'tourist', 'destination', 'adventure', 'explore', 'wander',
    'nomad', 'backpack', 'hostel', 'hotel', 'resort', 'airbnb',
    'flight', 'airline', 'airport', 'cruise', 'sail', 'boat',
    'train', 'bus', 'roadtrip', 'road-trip', 'drive', 'highway',
    'route', 'itinerary', 'passport', 'visa', 'immigration',
    'expat', 'abroad', 'overseas', 'international', 'global',
    'world', 'continent', 'country', 'city', 'town', 'village',
    'island', 'beach', 'mountain', 'lake', 'river', 'forest',
    'national-park', 'landmark', 'monument', 'museum', 'gallery',
    'temple', 'church', 'castle', 'palace', 'ruins', 'heritage',
    'disney', 'theme-park', 'amusement', 'waterpark',
]

FASHION_BEAUTY_KEYWORDS = [
    'fashion', 'style', 'clothing', 'clothes', 'outfit', 'dress',
    'wear', 'wardrobe', 'closet', 'trend', 'designer', 'brand',
    'luxury', 'boutique', 'shop', 'store', 'mall', 'retail',
    'beauty', 'makeup', 'cosmetic', 'skincare', 'skin', 'hair',
    'nail', 'lash', 'brow', 'lip', 'eye', 'face', 'body',
    'fragrance', 'perfume', 'cologne', 'scent', 'aroma',
    'jewelry', 'jewel', 'ring', 'necklace', 'bracelet', 'earring',
    'watch', 'accessory', 'bag', 'purse', 'handbag', 'shoe',
    'sneaker', 'boot', 'heel', 'sandal', 'hat', 'cap', 'scarf',
    'sunglasses', 'glasses', 'eyewear',
]

PARENTING_KEYWORDS = [
    'parent', 'mom', 'mum', 'mama', 'mother', 'dad', 'papa',
    'father', 'baby', 'infant', 'toddler', 'child', 'kid', 'teen',
    'family', 'pregnant', 'expecting', 'newborn', 'nursery',
    'diaper', 'nappy', 'breastfeed', 'formula', 'teething',
    'sleep-train', 'potty', 'milestone', 'development', 'growth',
    'daycare', 'nanny', 'babysit', 'playdate', 'playground',
    'toy', 'lego', 'barbie', 'doll', 'action-figure', 'board-game',
    'birthday', 'party', 'celebration', 'holiday',
]

TECH_PROGRAMMING_KEYWORDS = [
    'tech', 'technology', 'software', 'hardware', 'computer',
    'laptop', 'desktop', 'server', 'cloud', 'aws', 'azure', 'gcp',
    'saas', 'paas', 'iaas', 'api', 'sdk', 'library', 'framework',
    'stack', 'fullstack', 'frontend', 'backend', 'devops', 'cicd',
    'docker', 'kubernetes', 'microservice', 'serverless', 'lambda',
    'function', 'database', 'sql', 'nosql', 'mongodb', 'postgres',
    'mysql', 'redis', 'cache', 'queue', 'kafka', 'rabbitmq',
    'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
    'node', 'deno', 'bun', 'rust', 'golang', 'java', 'kotlin',
    'swift', 'flutter', 'dart', 'ruby', 'rails', 'php', 'laravel',
    'wordpress', 'drupal', 'joomla', 'cms', 'blog', 'static-site',
    'jamstack', 'gatsby', 'nextjs', 'nuxtjs', 'sveltekit',
    'linux', 'windows', 'macos', 'ios', 'android', 'mobile',
    'app', 'web', 'native', 'hybrid', 'pwa', 'wasm', 'webassembly',
    'ai', 'machine-learning', 'deep-learning', 'neural', 'gpt',
    'llm', 'nlp', 'cv', 'robotics', 'automation', 'bot',
    'cybersecurity', 'security', 'hacking', 'pentest', 'firewall',
    'encryption', 'ssl', 'tls', 'oauth', 'jwt', 'auth',
    'gadget', 'device', 'iot', 'smart', 'wearable', 'drone',
    'vr', 'ar', 'metaverse', '3d', 'unity', 'unreal', 'blender',
    'geek', 'nerd', 'hacker', 'developer', 'engineer', 'coder',
    'programmer', 'startup', 'founder', 'entrepreneur',
]

PET_KEYWORDS = [
    'pet', 'dog', 'puppy', 'cat', 'kitten', 'bird', 'fish',
    'reptile', 'hamster', 'rabbit', 'bunny', 'horse', 'equine',
    'aquarium', 'terrarium', 'kennel', 'vet', 'veterinar',
    'breed', 'adopt', 'rescue', 'shelter', 'paw', 'fur', 'tail',
    'bark', 'meow', 'woof', 'leash', 'collar', 'treat',
]

AUTOMOTIVE_KEYWORDS = [
    'car', 'auto', 'vehicle', 'truck', 'suv', 'van', 'motorcycle',
    'bike', 'scooter', 'electric-vehicle', 'ev', 'tesla', 'ford',
    'toyota', 'honda', 'bmw', 'mercedes', 'audi', 'chevrolet',
    'drive', 'driver', 'road', 'highway', 'traffic', 'parking',
    'garage', 'mechanic', 'repair', 'maintenance', 'oil', 'tire',
    'brake', 'engine', 'transmission', 'exhaust', 'suspension',
    'detailing', 'wash', 'wax', 'polish',
]

SPORTS_KEYWORDS = [
    'sport', 'football', 'soccer', 'basketball', 'baseball',
    'hockey', 'tennis', 'golf', 'swimming', 'cycling', 'boxing',
    'mma', 'ufc', 'wrestling', 'volleyball', 'cricket', 'rugby',
    'nfl', 'nba', 'mlb', 'nhl', 'fifa', 'olympics', 'athlete',
    'coaching', 'training', 'fantasy', 'betting', 'odds', 'wager',
    'sportsbook', 'draft', 'league', 'tournament', 'championship',
    'hunting', 'fishing', 'camping', 'hiking', 'climbing', 'skiing',
    'snowboard', 'surf', 'skateboard', 'martial',
]

PHOTOGRAPHY_KEYWORDS = [
    'photo', 'photograph', 'camera', 'lens', 'dslr', 'mirrorless',
    'canon', 'nikon', 'sony', 'fuji', 'lightroom', 'photoshop',
    'editing', 'retouching', 'portrait', 'landscape', 'wedding',
    'studio', 'flash', 'lighting', 'exposure', 'aperture', 'shutter',
    'iso', 'raw', 'jpeg', 'print', 'album', 'gallery',
]

MUSIC_KEYWORDS = [
    'music', 'song', 'sing', 'guitar', 'piano', 'drum', 'bass',
    'violin', 'cello', 'flute', 'trumpet', 'saxophone', 'ukulele',
    'chord', 'tab', 'lyric', 'melody', 'harmony', 'rhythm',
    'beat', 'tempo', 'key', 'scale', 'note', 'sheet-music',
    'band', 'concert', 'festival', 'album', 'playlist', 'spotify',
    'itunes', 'soundcloud', 'producer', 'dj', 'mixing', 'mastering',
    'recording', 'studio', 'microphone', 'headphone', 'speaker',
    'audio', 'podcast', 'radio', 'stream',
]


def load_publishers():
    """Load all publishers from CSV."""
    publishers = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            publishers.append({
                'domain': row['domain'].strip().strip('"'),
                'name': row['name'].strip().strip('"'),
                'network': row['network'].strip(),
                'seller_id': row['seller_id'].strip(),
            })
    return publishers


def extract_domain_words(domain):
    """Extract meaningful words from a domain name."""
    # Remove TLD
    parts = domain.split('.')
    if len(parts) >= 2:
        # Handle multi-part TLDs like .co.uk
        if parts[-2] in ('co', 'com', 'org', 'net', 'gov', 'edu', 'ac', 'or'):
            base = '.'.join(parts[:-2])
        else:
            base = '.'.join(parts[:-1])
    else:
        base = domain

    # Split on hyphens and common separators
    words = re.split(r'[-_.]', base.lower())
    return words


def match_keywords(text, keywords):
    """Check if text matches any keywords. Returns list of matched keywords."""
    text_lower = text.lower()
    matches = []
    for kw in keywords:
        if kw in text_lower:
            matches.append(kw)
    return matches


def categorize_publisher(pub):
    """Categorize a publisher into one or more niches."""
    domain = pub['domain'].lower()
    name = pub['name'].lower()
    combined = f"{domain} {name}"
    domain_words = extract_domain_words(domain)
    domain_base = ' '.join(domain_words)
    search_text = f"{domain_base} {name.lower()}"

    categories = []
    scores = {}

    # Check each category
    checks = [
        ('Tools/Utilities', TOOL_KEYWORDS),
        ('Games/Entertainment', GAME_KEYWORDS),
        ('Finance/Calculators', FINANCE_KEYWORDS),
        ('Health/Fitness', HEALTH_FITNESS_KEYWORDS),
        ('Food/Recipe', FOOD_RECIPE_KEYWORDS),
        ('Education/Learning', EDUCATION_KEYWORDS),
        ('DIY/Home', DIY_HOME_KEYWORDS),
        ('Travel', TRAVEL_KEYWORDS),
        ('Fashion/Beauty', FASHION_BEAUTY_KEYWORDS),
        ('Parenting/Family', PARENTING_KEYWORDS),
        ('Tech/Programming', TECH_PROGRAMMING_KEYWORDS),
        ('Pets/Animals', PET_KEYWORDS),
        ('Automotive', AUTOMOTIVE_KEYWORDS),
        ('Sports/Outdoors', SPORTS_KEYWORDS),
        ('Photography', PHOTOGRAPHY_KEYWORDS),
        ('Music/Audio', MUSIC_KEYWORDS),
    ]

    for cat_name, keywords in checks:
        matches = match_keywords(search_text, keywords)
        if matches:
            # Weight matches in domain more heavily
            domain_matches = match_keywords(domain_base, keywords)
            score = len(matches) + len(domain_matches) * 2  # Domain matches count 3x total
            scores[cat_name] = (score, matches)

    if scores:
        # Sort by score, pick top category
        sorted_cats = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
        primary = sorted_cats[0][0]
        primary_matches = sorted_cats[0][1][1]

        # Also note secondary categories
        secondary = [c[0] for c in sorted_cats[1:] if c[1][0] >= 2]

        return primary, primary_matches, secondary

    return 'Other', [], []


def assess_rust_rebuild_potential(domain, name, category, matches):
    """Rate the Rust rebuild potential for a site."""
    domain_lower = domain.lower()
    name_lower = name.lower()
    combined = f"{domain_lower} {name_lower}"

    # High-value tool patterns
    high_patterns = [
        r'calc', r'convert', r'generat', r'compress', r'resize',
        r'optimi[zs]', r'minif', r'format', r'encod', r'decod',
        r'hash', r'encrypt', r'pdf', r'image', r'video', r'audio',
        r'ocr', r'transcri', r'qr', r'barcode', r'svg', r'css',
        r'json', r'xml', r'csv', r'markdown', r'regex', r'diff',
        r'merge', r'split', r'crop', r'watermark', r'screensho',
        r'download', r'extract', r'speed', r'test', r'bench',
        r'lint', r'valid', r'beautif', r'prettif', r'color.*pick',
        r'palette', r'font', r'gradient', r'shadow', r'border',
    ]

    medium_patterns = [
        r'tool', r'maker', r'builder', r'creator', r'editor',
        r'planner', r'tracker', r'counter', r'timer', r'chart',
        r'graph', r'diagram', r'template', r'resume', r'invoice',
        r'budget', r'quiz', r'game', r'puzzle', r'typing',
        r'password', r'random', r'lorem', r'mockup', r'wireframe',
        r'sitemap', r'check', r'scan', r'analyz', r'compar',
        r'search', r'find', r'lookup', r'translat',
    ]

    high_score = sum(1 for p in high_patterns if re.search(p, combined))
    medium_score = sum(1 for p in medium_patterns if re.search(p, combined))

    if high_score >= 2 or (high_score >= 1 and medium_score >= 1):
        return 'High'
    elif high_score >= 1 or medium_score >= 2:
        return 'Medium'
    elif medium_score >= 1:
        return 'Low'

    # Check if it's in a tool-related category at all
    if category in ('Tools/Utilities', 'Games/Entertainment', 'Finance/Calculators'):
        return 'Low'

    return None


def infer_tool_type(domain, name, matches):
    """Infer what type of tool a site likely provides."""
    combined = f"{domain.lower()} {name.lower()}"

    type_patterns = [
        (r'pdf', 'PDF Tool'),
        (r'image|photo|picture|pic|img', 'Image Tool'),
        (r'video|vid|movie|film', 'Video Tool'),
        (r'audio|sound|music|mp3|wav', 'Audio Tool'),
        (r'calc|math|comput', 'Calculator'),
        (r'convert|transform|chang', 'Converter'),
        (r'generat|creat|make|build', 'Generator/Creator'),
        (r'edit|modif|alter', 'Editor'),
        (r'compress|optimi[zs]|minif|reduc|shrink', 'Optimizer/Compressor'),
        (r'resize|scale|dimension', 'Resizer'),
        (r'format|beautif|prettif|lint', 'Formatter'),
        (r'merge|combin|join|concat', 'Merger'),
        (r'split|separ|divid|break', 'Splitter'),
        (r'crop|cut|trim', 'Cropper/Trimmer'),
        (r'encrypt|decrypt|cipher|secur', 'Encryption Tool'),
        (r'hash|md5|sha|checksum', 'Hash Tool'),
        (r'encod|decod|base64|url-encod', 'Encoder/Decoder'),
        (r'qr|barcode|scan', 'QR/Barcode Tool'),
        (r'ocr|text-recogn', 'OCR Tool'),
        (r'transcri|speech|voice', 'Transcription Tool'),
        (r'translat|language|i18n', 'Translation Tool'),
        (r'color|palette|picker|gradient', 'Color Tool'),
        (r'font|typograph|text', 'Typography/Text Tool'),
        (r'chart|graph|visual|plot|data', 'Chart/Data Visualization'),
        (r'diagram|flowchart|mindmap|draw', 'Diagram/Drawing Tool'),
        (r'template|resume|cv|letter|invoice', 'Template/Document Tool'),
        (r'budget|expense|financial|money|invest', 'Financial Calculator'),
        (r'mortgage|loan|interest|amortiz', 'Mortgage/Loan Calculator'),
        (r'bmi|calorie|nutrition|macro|diet', 'Health Calculator'),
        (r'workout|exercise|fitness|training', 'Fitness Tool'),
        (r'meal|recipe|cook|food|ingredient', 'Recipe/Meal Tool'),
        (r'timer|countdown|stopwatch|clock|alarm', 'Timer/Clock Tool'),
        (r'counter|tally|count', 'Counter Tool'),
        (r'password|random|uuid|token', 'Password/Random Generator'),
        (r'regex|pattern|match', 'Regex Tool'),
        (r'json|xml|csv|yaml|html|css', 'Code/Data Tool'),
        (r'ip|dns|whois|domain|ssl|http', 'Network/DNS Tool'),
        (r'speed|benchmark|perf|load', 'Speed/Performance Tool'),
        (r'typing|keyboard|wpm', 'Typing Tool'),
        (r'quiz|trivia|test|exam', 'Quiz/Test Tool'),
        (r'game|play|puzzle|sudoku|crossword|word', 'Game/Puzzle'),
        (r'map|location|geo|coordinate|distance', 'Map/Location Tool'),
        (r'unit|measur|length|weight|volume|temp', 'Unit Converter'),
        (r'date|time|age|calendar|schedule', 'Date/Time Tool'),
        (r'text|string|word|character|sentence', 'Text Processing Tool'),
        (r'planner|organiz|schedul|todo|task', 'Planner/Organizer'),
        (r'tracker|track|monitor|log', 'Tracker/Logger'),
        (r'compar|versus|vs|differ', 'Comparison Tool'),
        (r'search|find|lookup|discover', 'Search/Lookup Tool'),
        (r'download|extract|save|export', 'Downloader/Extractor'),
        (r'watermark|stamp|logo|brand', 'Watermark Tool'),
        (r'screensho|capture|record|screen', 'Screenshot/Screen Tool'),
        (r'embed|widget|iframe', 'Embed/Widget Tool'),
        (r'shorten|url|link|redirect', 'URL Tool'),
        (r'seo|keyword|rank|serp|backlink', 'SEO Tool'),
        (r'social|share|post|tweet|instagram', 'Social Media Tool'),
        (r'email|mail|newsletter|smtp', 'Email Tool'),
        (r'survey|poll|form|feedback|vote', 'Survey/Form Tool'),
        (r'sign|esign|document|contract', 'E-Signature Tool'),
        (r'note|memo|journal|diary|writing', 'Note/Writing Tool'),
        (r'weather|forecast|climate|temp', 'Weather Tool'),
        (r'astro|horoscope|zodiac|star', 'Astrology Tool'),
        (r'name.*generat|baby.*name|pet.*name', 'Name Generator'),
        (r'ai|chatbot|assistant|gpt', 'AI Tool'),
    ]

    for pattern, tool_type in type_patterns:
        if re.search(pattern, combined):
            return tool_type

    # Fall back to matches
    if matches:
        return f"Tool ({', '.join(matches[:3])})"

    return 'General Tool/Utility'


def assess_programmatic_seo_potential(domain, name, category, matches):
    """Assess if a site has programmatic SEO potential."""
    combined = f"{domain.lower()} {name.lower()}"

    seo_patterns = {
        'Template-based': [r'template', r'resume', r'invoice', r'letter', r'card', r'flyer', r'poster', r'banner', r'mockup', r'wireframe'],
        'Location-based': [r'local', r'city', r'state', r'country', r'weather', r'zip', r'area', r'region', r'map', r'near'],
        'Comparison/Review': [r'compar', r'review', r'versus', r'vs', r'best', r'top', r'rank', r'rate', r'altern'],
        'Data-driven': [r'stat', r'data', r'fact', r'number', r'figure', r'census', r'demographic', r'population', r'average', r'median'],
        'Reference/Lookup': [r'diction', r'encyclopedia', r'wiki', r'glossary', r'reference', r'define', r'meaning', r'synonym', r'antonym'],
        'Conversion-based': [r'convert', r'unit', r'measur', r'exchange', r'rate', r'currency', r'translat'],
        'Calculator-based': [r'calc', r'comput', r'estima', r'figure', r'formula', r'equation'],
        'Generator-based': [r'generat', r'creat', r'make', r'build', r'random', r'auto'],
    }

    matched_types = []
    for seo_type, patterns in seo_patterns.items():
        for p in patterns:
            if re.search(p, combined):
                matched_types.append(seo_type)
                break

    return matched_types


def main():
    print("Loading publishers...")
    publishers = load_publishers()
    print(f"Loaded {len(publishers)} publishers")

    # Network counts
    mediavine_count = sum(1 for p in publishers if p['network'] == 'mediavine')
    raptive_count = sum(1 for p in publishers if p['network'] == 'raptive')
    print(f"Mediavine: {mediavine_count}, Raptive: {raptive_count}")

    # Categorize all publishers
    print("\nCategorizing publishers...")
    categorized = defaultdict(list)
    tool_sites = []
    game_sites = []
    finance_sites = []
    programmatic_seo_sites = []

    for pub in publishers:
        primary_cat, matches, secondary = categorize_publisher(pub)
        pub['category'] = primary_cat
        pub['matches'] = matches
        pub['secondary'] = secondary
        categorized[primary_cat].append(pub)

        # Assess tool sites
        if primary_cat in ('Tools/Utilities', 'Tech/Programming', 'Education/Learning') or \
           any(m in ['tool', 'calc', 'convert', 'generat', 'maker', 'builder', 'editor', 'app', 'online', 'pdf', 'image', 'photo', 'video', 'audio'] for m in matches):
            rust_potential = assess_rust_rebuild_potential(pub['domain'], pub['name'], primary_cat, matches)
            if rust_potential:
                tool_type = infer_tool_type(pub['domain'], pub['name'], matches)
                tool_sites.append({
                    **pub,
                    'rust_potential': rust_potential,
                    'tool_type': tool_type,
                })

        # Also check games
        if primary_cat == 'Games/Entertainment' or \
           any(m in ['game', 'quiz', 'puzzle', 'trivia', 'word', 'play'] for m in matches):
            rust_potential = assess_rust_rebuild_potential(pub['domain'], pub['name'], primary_cat, matches)
            tool_type = infer_tool_type(pub['domain'], pub['name'], matches)
            game_sites.append({
                **pub,
                'rust_potential': rust_potential or 'Low',
                'tool_type': tool_type,
            })

        # Finance/calculator sites
        if primary_cat == 'Finance/Calculators' or \
           any(m in ['calc', 'mortgage', 'loan', 'invest', 'budget', 'tax', 'finance'] for m in matches):
            rust_potential = assess_rust_rebuild_potential(pub['domain'], pub['name'], primary_cat, matches)
            tool_type = infer_tool_type(pub['domain'], pub['name'], matches)
            finance_sites.append({
                **pub,
                'rust_potential': rust_potential or 'Low',
                'tool_type': tool_type,
            })

        # Programmatic SEO
        seo_types = assess_programmatic_seo_potential(pub['domain'], pub['name'], primary_cat, matches)
        if seo_types:
            programmatic_seo_sites.append({
                **pub,
                'seo_types': seo_types,
            })

    # Remove duplicates in tool_sites (same domain)
    seen_domains = set()
    unique_tool_sites = []
    for site in tool_sites:
        if site['domain'] not in seen_domains:
            seen_domains.add(site['domain'])
            unique_tool_sites.append(site)
    tool_sites = unique_tool_sites

    seen_domains = set()
    unique_game_sites = []
    for site in game_sites:
        if site['domain'] not in seen_domains:
            seen_domains.add(site['domain'])
            unique_game_sites.append(site)
    game_sites = unique_game_sites

    seen_domains = set()
    unique_finance_sites = []
    for site in finance_sites:
        if site['domain'] not in seen_domains:
            seen_domains.add(site['domain'])
            unique_finance_sites.append(site)
    finance_sites = unique_finance_sites

    seen_domains = set()
    unique_seo_sites = []
    for site in programmatic_seo_sites:
        if site['domain'] not in seen_domains:
            seen_domains.add(site['domain'])
            unique_seo_sites.append(site)
    programmatic_seo_sites = unique_seo_sites

    # Sort tool sites by potential
    potential_order = {'High': 0, 'Medium': 1, 'Low': 2}
    tool_sites.sort(key=lambda x: potential_order.get(x['rust_potential'], 3))
    game_sites.sort(key=lambda x: potential_order.get(x['rust_potential'], 3))
    finance_sites.sort(key=lambda x: potential_order.get(x['rust_potential'], 3))

    # Output results as JSON for further processing
    results = {
        'total_publishers': len(publishers),
        'mediavine_count': mediavine_count,
        'raptive_count': raptive_count,
        'categories': {cat: len(pubs) for cat, pubs in sorted(categorized.items(), key=lambda x: -len(x[1]))},
        'tool_sites_count': len(tool_sites),
        'game_sites_count': len(game_sites),
        'finance_sites_count': len(finance_sites),
        'programmatic_seo_count': len(programmatic_seo_sites),
        'tool_sites': tool_sites,
        'game_sites': game_sites,
        'finance_sites': finance_sites,
        'programmatic_seo_sites': programmatic_seo_sites,
        'category_details': {},
    }

    # Add top domains per category
    for cat, pubs in categorized.items():
        results['category_details'][cat] = {
            'count': len(pubs),
            'sample_domains': [p['domain'] for p in pubs[:20]],
            'network_breakdown': {
                'mediavine': sum(1 for p in pubs if p['network'] == 'mediavine'),
                'raptive': sum(1 for p in pubs if p['network'] == 'raptive'),
            }
        }

    # Print summary
    print("\n" + "="*80)
    print("PUBLISHER CATEGORIZATION SUMMARY")
    print("="*80)

    print(f"\nTotal publishers: {len(publishers)}")
    print(f"Mediavine: {mediavine_count}")
    print(f"Raptive: {raptive_count}")

    print(f"\n--- Categories ---")
    for cat, pubs in sorted(categorized.items(), key=lambda x: -len(x[1])):
        mv = sum(1 for p in pubs if p['network'] == 'mediavine')
        rp = sum(1 for p in pubs if p['network'] == 'raptive')
        print(f"  {cat}: {len(pubs)} (MV: {mv}, RP: {rp})")

    print(f"\n--- Tool/SaaS/Utility Sites: {len(tool_sites)} ---")
    high_tools = [s for s in tool_sites if s['rust_potential'] == 'High']
    med_tools = [s for s in tool_sites if s['rust_potential'] == 'Medium']
    low_tools = [s for s in tool_sites if s['rust_potential'] == 'Low']
    print(f"  High potential: {len(high_tools)}")
    print(f"  Medium potential: {len(med_tools)}")
    print(f"  Low potential: {len(low_tools)}")

    print(f"\n--- Top High-Potential Tool Sites ---")
    for site in high_tools[:30]:
        print(f"  {site['domain']:40s} | {site['tool_type']:30s} | {site['network']:10s} | matches: {', '.join(site['matches'][:5])}")

    print(f"\n--- Game/Quiz/Interactive Sites: {len(game_sites)} ---")
    for site in game_sites[:20]:
        print(f"  {site['domain']:40s} | {site['tool_type']:30s} | {site['network']:10s}")

    print(f"\n--- Finance Calculator Sites: {len(finance_sites)} ---")
    for site in finance_sites[:20]:
        print(f"  {site['domain']:40s} | {site['tool_type']:30s} | {site['network']:10s}")

    print(f"\n--- Programmatic SEO Sites: {len(programmatic_seo_sites)} ---")
    for site in programmatic_seo_sites[:20]:
        print(f"  {site['domain']:40s} | SEO types: {', '.join(site['seo_types'])}")

    # Save full results
    output_path = CSV_PATH.parent / 'analysis_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")

    return results


if __name__ == '__main__':
    main()
