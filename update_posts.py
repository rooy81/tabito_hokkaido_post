#!/usr/bin/env python3
import urllib.request
import json
import base64
import re
import os

INSTAGRAM_TOKEN = os.environ['INSTAGRAM_TOKEN']
GITHUB_TOKEN    = os.environ['MY_GITHUB_TOKEN']
GITHUB_REPO     = 'rooy81/tabito_hokkaido_post'
GITHUB_FILE     = 'posts.json'

# ââââââââââââââââââââââââââââââââââââââââââââââ
#  ã¨ãªã¢è¨­å®
# ââââââââââââââââââââââââââââââââââââââââââââââ
# â» é çªéè¦ï¼åºæåè©ãæç¢ºãªã¨ãªã¢ãåã«ãã§ãã¯ã'æ­å¹'ã¯æå¾ã
AREA_KEYWORDS = {
    'å®å±±æ¸':                           ['å®å±±æ¸'],
    'ããã ':                           ['ããã ', 'TOMAMU'],
    'ãã»ã³':                           ['ãã»ã³', 'å¶ç¥å®', 'ã­ã­ã­'],
    'å¯è¯éã»ç¾ç':                     ['å¯è¯é', 'ç¾ç', 'ã³ãã', 'ãµãã®', 'ãã¡ã¼ã å¯ç°'],
    'æ­å·è¿é':                         ['æ­å·', 'æ­å±±åç©å', 'æ­å±±', 'å±¤é²å³¡', 'æ±å·', 'æ±ç¥æ¥½', 'æ²¼ç°'],
    'ç¨åï¼éåï¼':                     ['ç¨å', 'å®è°·', 'å©å°»', 'ç¤¼æ', 'è±å¯', 'å¹å»¶'],
    'å½é¤¨è¿é':                         ['å½é¤¨', 'å½é¤¨å±±', 'äºç¨é­', 'æ¾å', 'æ±å·®', 'é·ä¸é¨', 'å¤§æ²¼', 'ä¸é£¯'],
    'å¸¯åºè¿éï¼ååï¼':                 ['å¸¯åº', 'åå', 'è½å®¤', 'å¹å¥', 'é³æ´', 'å£«å¹', 'æ± ç°'],
    'é§è·¯/æ ¹å®¤/ç¥åºå¨è¾º':               ['é§è·¯', 'é¿å¯', 'å¼å­å±', 'å·æ¹¯',
                                         'æ ¹å®¤', 'å¥æµ·', 'ä¸­æ¨æ´¥', 'æ¨è¶', 'åå²¸',
                                         'ç¥åº', 'ã¦ãã­', 'ç¾è¼', 'æé'],
    'ç¶²èµ°ï¼ãªãã¼ãã¯å¨è¾ºï¼':           ['ç¶²èµ°', 'ãªãã¼ãã¯', 'åè¦', 'ç¾å¹', 'æ´¥å¥',
                                         'ç´å¥', 'ã¬ãªã³ã³å·'],
    'ç»å¥/ç½è/æ´çºæ¹/è«å°ç§æ¹é¢':     ['ç»å¥', 'å®¤è­', 'è«å°ç§', 'ç½è', 'ã¦ããã¤', 'æ´çº'],
    'æ¥é«':                             ['æ¥é«', 'æµ¦æ²³', 'æ§ä¼¼', 'ããã', 'æ°å ', 'æ°ã²ã ã', 'éå'],
    'å°æ¨½è¿é':                         ['å°æ¨½', 'ä½å¸', 'ä»æ¨', 'ç©ä¸¹'],
    'æ°åæ­³':                           ['æ°åæ­³', 'åæ­³ç©ºæ¸¯', 'æ¯ç¬æ¹', 'æ°·æ¿¤ã¾ã¤ã', 'æµåº­'],
    'æ­å¹è¿é(æ­å¹ä»¥å¤)':               ['ååºå³¶', 'ã¨ã¹ã³ã³', 'ãã¼ã«ãã¼ã¯', 'ã¨ã¹ã³ã³ãã£ã¼ã«ã',
                                         'éå¹', 'ç³ç©', 'å½å¥', 'æ±å¥', 'å²©è¦æ²¢'],
    'æ­å¹':                             ['ãããã®', 'èé', 'ç¸å°è·¯', 'åå±±', 'å¤§éå¬å',
                                         'è»å²©å±±', 'åæµ·éç¥å®®', 'æè¨å°', 'ä¸­å³¶å¬å', 'åå¤§',
                                         'ãã¬ãå¡', 'ã¢ã¨ã¬æ²¼', 'å¤§åå±±', 'ä¸ç ', 'èµ¤ãããåºè',
                                         'äºæ¡å¸å ´', 'æ­å¹é§', 'ãã£ã½ãéªã¾ã¤ã', 'éªã¾ã¤ã',
                                         'AOAO SAPPORO', 'å¤§ä¸¸æ­å¹', 'ã·ãã',
                                         'æ­å¹å¸å', 'ãã£ã½ã', 'æ­å¹'],
    'åæµ·éå¨ä½':                       ['åæµ·éå¨ä½', 'éåå¨å', 'åæµ·éåå°'],
    'æè¡ãã©ã³':                       ['æè¡ãã©ã³', 'ã¢ãã«ã³ã¼ã¹'],
}

DAICHI_MAP = {
    'éå¤®': ['æ­å¹', 'æ­å¹è¿é(æ­å¹ä»¥å¤)', 'æ°åæ­³', 'å®å±±æ¸', 'å°æ¨½è¿é', 'ãã»ã³',
             'ç»å¥/ç½è/æ´çºæ¹/è«å°ç§æ¹é¢', 'ããã ', 'æ¥é«'],
    'éæ±': ['å¸¯åºè¿éï¼ååï¼', 'é§è·¯/æ ¹å®¤/ç¥åºå¨è¾º', 'ç¶²èµ°ï¼ãªãã¼ãã¯å¨è¾ºï¼'],
    'éå': ['å½é¤¨è¿é'],
    'éå': ['æ­å·è¿é', 'å¯è¯éã»ç¾ç', 'ç¨åï¼éåï¼'],
}

def detect_daichi(area):
    for daichi, areas in DAICHI_MAP.items():
        if area in areas:
            return daichi
    return ''

def get_body_text(caption):
    lines = caption.split('\n')
    body = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.count('#') >= 2:
            continue
        body.append(line)
    return '\n'.join(body).lower()

def extract_title(caption):
    m = re.search(r'[ã\[]([^ã\]]{3,80})[ã\]]', caption)
    if m:
        return m.group(1).lower()
    for line in caption.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) >= 3:
            return line[:50].lower()
    return ''

def detect_area(caption):
    body = get_body_text(caption)
    for area, keywords in AREA_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in body:
                return area
    return ''

def detect_categories(caption):
    title = extract_title(caption)
    body  = get_body_text(caption)

    grume_kw = ['ã©ã¼ã¡ã³', 'ã¹ã¼ãã«ã¬ã¼', 'æµ·é®®', 'å¯¿å¸', 'ç¼è', 'ã¸ã³ã®ã¹ã«ã³',
                'ã½ããã¯ãªã¼ã ', 'ã¹ã¤ã¼ã', 'ã«ãã§', 'ã±ã¼ã­', 'ãã³', 'å±éå±',
                'ä¸¼', 'ã¢ã¤ã¹', 'ãã¼ãº', 'ãã¿ã¼', 'ãã«ã¯', 'ã°ã«ã¡', 'æ¨ªä¸',
                'ååº', 'æ¿ã¦ã', 'çµ¶åã°ã«ã¡', 'ã©ã³ã', 'ãã£ãã¼', 'ã¬ã¹ãã©ã³',
                'é£å ', 'å®é£', 'ãå½å°', 'Bç´', 'æµ·èå¤©', 'ãã­ã³', 'ã¶ã³ã®',
                'ã¡ããã½ã', 'ãã¼ã«', 'æ¥æ¬é', 'ã¦ã¤ã¹ã­ã¼']
    omiyage_kw = ['ãåç£', 'ãã¿ãã', 'åç£', 'ç©ºæ¸¯éå®', 'ãåãå¯ã', 'ã®ãã',
                  'å­è±äº­', 'ç½ãæäºº', 'ã­ã¤ãº', 'ãã«ã»ã¤', 'åèæ¥¼', 'ãããã¨',
                  'éå®ã¹ã¤ã¼ã']
    hotel_kw      = ['ããã«', 'æé¤¨', 'ã´ã£ã©', 'ãã³ã·ã§ã³', 'ã³ãã¼ã¸', 'ã°ã©ã³ãã³ã°',
                     'å®¿', 'å®¢å®¤', 'æ³ã¾ã£ã¦', 'æ³ã¾ã']
    hotel_body_kw = ['ãã§ãã¯ã¤ã³', 'ãã§ãã¯ã¢ã¦ã', 'æ³ã¾ã£ã¦ã', 'å®¿æ³ãã¦']
    onsen_kw  = ['æ¸©æ³', 'é²å¤©é¢¨å', 'å¤§æµ´å ´', 'ãµã¦ã', 'ã¨ã¨ã®ã', 'æ¹¯ããã',
                 'æ¥å¸°ãæ¹¯', 'æºæ³', 'æ¸©æ³è¡', 'è¶³æ¹¯', 'é­æ¹¯']
    event_kw  = ['ã¾ã¤ã', 'ç¥­ã', 'è±ç«', 'ãã§ã¹ã¿', 'ãã§ã¹', 'ãã«ã·ã§', 'ã¤ãã³ã',
                 'ã©ã¤ãã¢ãã', 'éªã¾ã¤ã', 'æå¸', 'ãã§ã¢', 'festival']
    taiken_kw = ['ã¹ã­ã¼', 'ã¹ãã¼ãã¼ã', 'ç»å±±', 'ãã¬ãã­ã³ã°', 'ãã¤ã­ã³ã°', 'ã«ãã¼',
                 'ã©ããã£ã³ã°', 'ãµã¤ã¯ãªã³ã°', 'ä¹é¦¬', 'é£ã', 'ã­ã£ã³ã', 'ã¸ããã©ã¤ã³',
                 'ããããã¼ç©ã', 'æç©ç©ã', 'æã¿åã', 'æãåã', 'åç©«ä½é¨',
                 'ã¢ã¦ããã¢ä½é¨', 'ããªã¼ãã¬ãã­ã³ã°', 'ãã©ã°ã©ã¤ãã¼', 'SUP',
                 'ã¦ã£ã³ã¿ã¼ã¹ãã¼ã', 'ã¹ãã¼ã·ã¥ã¼', 'ãã¤ã¿ã¼ã¹ã­ã¼']
    spot_kw   = ['å¬å', 'å±æ', 'å¤æ¥', 'å¤ç¼ã', 'ã©ãã³ãã¼', 'ç´è', 'éªæ¯è²', 'æµæ°·',
                 'æ¹', 'å²¬', 'ãã©ãã¹ããã', 'çµ¶æ¯', 'ç¥ç¤¾', 'å¯º', 'ç¯å°', 'æ»', 'å¤æ¯',
                 'è¦³åã¹ããã', 'åæ', 'åç©å', 'æ°´æé¤¨', 'ç¾è¡é¤¨', 'åç©é¤¨', 'éåå°',
                 'åº­å', 'å', 'ç ä¸', 'æ°·ç', 'æ¨¹æ°·', 'ãã¥ã¼ã¹ããã', 'ãã¥ã¼ãªãã',
                 'è±ç', 'èã®è±', 'ããããã', 'å°éº¦ç', 'ç§å ´']

    if (re.search(r'[0-9ï¼-ï¼]+æ³[0-9ï¼-ï¼]+æ¥', title) or
        re.search(r'[0-9ï¼-ï¼]+é¸', title) or
        re.search(r'(å®å¨æ»ç¥|ãããã.+[0-9]+é¸|å¿è¦ã¹ããã|ã¢ãã«ã³ã¼ã¹|æè¡ãã©ã³|è¦³åã¬ã¤ã|ã¾ã¨ã)', title)):
        return ['æè¡ãã©ã³']

    cats = []

    is_hotel = (any(kw in title for kw in hotel_kw) or
                any(kw in body  for kw in hotel_body_kw))
    if is_hotel:
        cats.append('å®¿æ³')

    if any(kw in body for kw in onsen_kw):
        cats.append('æ¸©æ³')

    if any(kw in title for kw in grume_kw) and not is_hotel:
        cats.append('ã°ã«ã¡')

    if any(kw in title for kw in omiyage_kw):
        cats.append('ãåç£')
    elif any(kw in body for kw in ['ãåç£', 'ãã¿ãã', 'ç©ºæ¸¯éå®', 'ãåãå¯ã']):
        cats.append('ãåç£')

    if any(kw in title for kw in event_kw):
        cats.append('ã¤ãã³ã')
    elif any(kw in body for kw in ['ã¾ã¤ã', 'ç¥­ã', 'è±ç«']):
        cats.append('ã¤ãã³ã')

    is_grume = 'ã°ã«ã¡' in cats

    if any(kw in body for kw in taiken_kw) and not is_grume:
        cats.append('ä½é¨')

    if any(kw in title for kw in spot_kw) and not is_grume:
        cats.append('è¦³åã¹ããã')

    return cats

def fetch_instagram_posts():
    """Instagram API ãä½¿ç¨ãã¦æç¨¿ãåå¾ãã"""
    all_posts = []
    url = (
        'https://graph.instagram.com/v21.0/me/media'
        '?fields=id,caption,media_url,thumbnail_url,permalink,timestamp,media_type'
        '&limit=50'
        f'&access_token={INSTAGRAM_TOKEN}'
    )
    while url:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        posts = data.get('data', [])
        all_posts.extend(posts)
        paging = data.get('paging', {})
        url = paging.get('next') if posts else None
    print(f'åå¾å®äº: {len(all_posts)}ä»¶')
    return all_posts

def fetch_existing_posts():
    github_sha = os.environ.get('GITHUB_SHA', '')
    if github_sha:
        raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/{github_sha}/{GITHUB_FILE}'
        print(f'ã³ãããSHAæå®ã§fetch: {github_sha[:8]}')
    else:
        sha = get_current_sha()
        if sha:
            raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/{sha}/{GITHUB_FILE}'
            print(f'APIããSHAåå¾ãã¦fetch: {sha[:8]}')
        else:
            raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE}'
    try:
        req = urllib.request.Request(raw_url)
        with urllib.request.urlopen(req) as resp:
            existing = json.loads(resp.read().decode())
        existing_map = {p['id']: p for p in existing if 'id' in p}
        print(f'æ¢å­ãã¼ã¿: {len(existing_map)}ä»¶')
        return existing_map
    except Exception as e:
        print(f'æ¢å­ãã¼ã¿ãªãï¼æ°è¦ä½æï¼: {e}')
        return {}

def format_posts(raw_posts, existing_map):
    formatted = []
    new_count = 0
    for p in raw_posts:
        post_id = p.get('id', '')
        caption = (p.get('caption', '') or '').replace('"', '')
        thumbnail = p.get('thumbnail_url') or p.get('media_url', '')

        if post_id in existing_map:
            ex         = existing_map[post_id]
            area       = ex.get('area', '')
            daichi     = ex.get('daichi', '') or detect_daichi(area)
            categories = ex.get('categories', [])
        else:
            area       = detect_area(caption)
            categories = detect_categories(caption)
            if 'æè¡ãã©ã³' in categories and not area:
                area = 'åæµ·éå¨ä½'
            daichi     = detect_daichi(area)
            new_count += 1

        formatted.append({
            'id':            post_id,
            'caption':       caption,
            'media_url':     p.get('media_url', ''),
            'thumbnail_url': thumbnail,
            'permalink':     p.get('permalink', ''),
            'timestamp':     p.get('timestamp', ''),
            'media_type':    p.get('media_type', ''),
            'daichi':        daichi,
            'area':          area,
            'categories':    categories,
        })

    print(f'æ°è¦: {new_count}ä»¶ / æ¢å­å¼ç¶ã: {len(formatted) - new_count}ä»¶')
    return formatted

def get_current_sha():
    api_url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}'
    req = urllib.request.Request(api_url)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode()).get('sha', '')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def upload_to_github(posts, sha=None):
    content_b64 = base64.b64encode(
        json.dumps(posts, ensure_ascii=False, indent=2).encode('utf-8')
    ).decode('ascii')
    body = {'message': f'Auto update: {len(posts)} posts', 'content': content_b64}
    if sha:
        body['sha'] = sha
    req = urllib.request.Request(
        f'https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}',
        data=json.dumps(body).encode('utf-8'), method='PUT'
    )
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        print(f"ä¿å­å®äº: {result.get('commit',{}).get('sha','')[:8]}")

existing_map = fetch_existing_posts()
raw          = fetch_instagram_posts()
posts        = format_posts(raw, existing_map)
sha          = get_current_sha()
upload_to_github(posts, sha)
