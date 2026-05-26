#!/usr/bin/env python3
import urllib.request
import json
import base64
import os

INSTAGRAM_TOKEN = os.environ['INSTAGRAM_TOKEN']
GITHUB_TOKEN    = os.environ['MY_GITHUB_TOKEN']
GITHUB_REPO     = 'rooy81/tabito_hokkaido_post'
GITHUB_FILE     = 'posts.json'

def detect_daichi(area):
    for daichi, areas in DAICHI_MAP.items():
        if area in areas:
            return daichi
    return ''

AREA_KEYWORDS = {
    '札幌近郊（千歳等）': ['札幌','新千歳','千歳','恵庭','江別','北広島','岩見沢','すすきの','狸小路','円山','大通','藻岩'],
    '小樽近郊':           ['小樽','余市','仁木','積丹'],
    'ニセコ':             ['ニセコ','倶知安','キロロ'],
    '登別/白老/洞爺湖/苫小牧方面': ['登別','室蘭','苫小牧','白老','ウポポイ','洞爺'],
    'トマム':             ['トマム','tomamu','Tomamu'],
    '定山渓':             ['定山渓'],
    '日高':               ['日高','浦河','様似','えりも','新冠','新ひだか','静内'],
    '帯広近郊（十勝）':   ['帯広','十勝','芽室','幕別','音更','士幌','池田'],
    '釧路近郊':           ['釧路','阿寒','弟子屈','川湯'],
    '網走（オホーツク）': ['網走','オホーツク','北見','紋別'],
    '知床':               ['知床','羅臼','ウトロ','斜里'],
    '根室近郊':           ['根室','別海','中標津','標茶','厚岸'],
    '函館近郊':           ['函館','函館山','五稜郭','松前','江差','長万部','大沼','七飯'],
    '旭川近郊':           ['旭川','旭山動物園','旭山'],
    '富良野・美瑛':       ['富良野','美瑛','びえい','ふらの'],
    '稚内（道北）':       ['稚内','宗谷','利尻','礼文','豊富','幌延'],
    '北海道全体':         ['北海道全体','道内全域'],
    '旅行プラン':         ['旅行プラン','旅程','モデルコース'],
}

DAICHI_MAP = {
    '道央': ['札幌近郊（千歳等）', '小樽近郊', 'ニセコ',
             '登別/白老/洞爺湖/苫小牧方面', 'トマム', '定山渓', '日高'],
    '道東': ['帯広近郊（十勝）', '釧路近郊', '網走（オホーツク）',
             '知床', '根室近郊'],
    '道南': ['函館近郊'],
    '道北': ['旭川近郊', '富良野・美瑛', '稚内（道北）'],
}

CATEGORY_KEYWORDS = {
    'グルメ':      ['グルメ','ランチ','ディナー','飯','食事','ラーメン','スープカレー',
                    '海鮮','寿司','焼肉','ジンギスカン','スイーツ','ソフトクリーム',
                    'カフェ','ケーキ','パン','居酒屋','定食','おいしい','美味','うまい',
                    '食べ','グルメ旅','名物','ご飯','めし','丼','チーズ','バター','ミルク','アイス'],
    '観光スポット': ['観光','絶景','景色','風景','自然','公園','展望','夕日','夕焼け',
                    '花','ラベンダー','紅葉','雪景色','流氷','湖','岬','スポット',
                    '撮影','写真','フォトスポット','映え','インスタ映え','神社','寺',
                    '灯台','滝','山','川','海','星空','オーロラ'],
    '宿泊':        ['宿泊','ホテル','旅館','泊まり','宿','ペンション','ゲストハウス','コテージ','グランピング'],
    'イベント':    ['イベント','祭り','花火','まつり','夏祭り','冬まつり','雪まつり','festival','マルシェ','フェス','市場','朝市'],
    '旅行プラン':  ['プラン'],
    '体験':        ['体験','アクティビティ','アウトドア','スキー','スノーボード','登山',
                    'トレッキング','ハイキング','カヌー','ラフティング','サイクリング','乗馬','釣り','キャンプ'],
    'お土産':      ['お土産','おみやげ','土産','みやげ','お菓子','六花亭','白い恋人','ロイズ','マルセイ','北菓楼'],
    '温泉':        ['温泉','onsen','露天風呂','大浴場','銭湯','源泉','湯めぐり','日帰り湯','足湯'],
}

def detect_area(caption):
    cap = caption.lower()
    for area, keywords in AREA_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in cap:
                return area
    return ''

def detect_categories(caption):
    cap = caption.lower()
    cats = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in cap:
                cats.append(cat)
                break
    return cats

def fetch_instagram_posts():
    all_posts = []
    url = (
        'https://graph.instagram.com/me/media'
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
    print(f'取得完了: {len(all_posts)}件')
    return all_posts

def format_posts(raw_posts):
    formatted = []
    for p in raw_posts:
        caption = p.get('caption', '') or ''
        caption_clean = caption.replace('"', '')
        thumbnail = p.get('thumbnail_url') or p.get('media_url', '')
        area = detect_area(caption)
        daichi = detect_daichi(area)
        categories = detect_categories(caption)
        formatted.append({
            'id': p.get('id', ''),
            'caption': caption_clean,
            'media_url': p.get('media_url', ''),
            'thumbnail_url': thumbnail,
            'permalink': p.get('permalink', ''),
            'timestamp': p.get('timestamp', ''),
            'media_type': p.get('media_type', ''),
            'daichi': daichi,
            'area': area,
            'categories': categories,
        })
    return formatted

def get_current_sha():
    api_url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}'
    req = urllib.request.Request(api_url)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get('sha', '')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def upload_to_github(posts, sha=None):
    content_str = json.dumps(posts, ensure_ascii=False, indent=2)
    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('ascii')
    api_url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}'
    body = {'message': f'Auto update: {len(posts)} posts', 'content': content_b64}
    if sha:
        body['sha'] = sha
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, method='PUT')
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        print(f"完了: {result.get('commit',{}).get('sha','')[:8]}")

raw = fetch_instagram_posts()
posts = format_posts(raw)
sha = get_current_sha()
upload_to_github(posts, sha)
