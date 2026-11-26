#!/usr/bin/env python3
import urllib.request
import json
import base64
import re
import os
import sys

INSTAGRAM_TOKEN = os.environ['INSTAGRAM_TOKEN']
GITHUB_TOKEN    = os.environ['MY_GITHUB_TOKEN']
GITHUB_REPO     = 'rooy81/tabito_hokkaido_post'
GITHUB_FILE     = 'posts.json'

# ══════════════════════════════════════════════
#  エリア設定
# ══════════════════════════════════════════════
# ※ 順番重要：固有名詞が明確なエリアを先にチェック。'札幌'は最後。
AREA_KEYWORDS = {
    '定山渓':                           ['定山渓'],
    'トマム':                           ['トマム', 'TOMAMU'],
    'ニセコ':                           ['ニセコ', '倶知安', 'キロロ'],
    '富良野・美瑛':                     ['富良野', '美瑛', 'びえい', 'ふらの', 'ファーム富田'],
    '旭川近郊':                         ['旭川', '旭山動物園', '旭山', '層雲峡', '東川', '東神楽', '沼田'],
    '稚内（道北）':                     ['稚内', '宗谷', '利尻', '礼文', '豊富', '幌延'],
    '函館近郊':                         ['函館', '函館山', '五稜郭', '松前', '江差', '長万部', '大沼', '七飯'],
    '帯広近郊（十勝）':                 ['帯広', '十勝', '芽室', '幕別', '音更', '士幌', '池田'],
    '釧路/根室/知床周辺':               ['釧路', '阿寒', '弟子屈', '川湯',
                                         '根室', '別海', '中標津', '標茶', '厚岸',
                                         '知床', 'ウトロ', '羅臼', '斜里'],
    '網走（オホーツク周辺）':           ['網走', 'オホーツク', '北見', '美幌', '津別',
                                         '紋別', 'ガリンコ号'],
    '登別/白老/洞爺湖/苫小牧方面':     ['登別', '室蘭', '苫小牧', '白老', 'ウポポイ', '洞爺'],
    '日高':                             ['日高', '浦河', '様似', 'えりも', '新冠', '新ひだか', '静内'],
    '小樽近郊':                         ['小樽', '余市', '仁木', '積丹'],
    '新千歳':                           ['新千歳', '千歳空港', '支笏湖', '氷濤まつり', '恵庭'],
    '札幌近郊(札幌以外)':               ['北広島', 'エスコン', 'ボールパーク', 'エスコンフィールド',
                                         '野幌', '石狩', '当別', '江別', '岩見沢'],
    '札幌':                             ['すすきの', '薄野', '狸小路', '円山', '大通公園',
                                         '藻岩山', '北海道神宮', '時計台', '中島公園', '北大',
                                         'テレビ塔', 'モエレ沼', '大倉山', '丘珠', '赤れんが庁舎',
                                         '二条市場', '札幌駅', 'さっぽろ雪まつり', '雪まつり',
                                         'AOAO SAPPORO', '大丸札幌', 'シハチ',
                                         '札幌市内', 'さっぽろ', '札幌'],
    '北海道全体':                       ['北海道全体', '道内全域', '北海道各地'],
    '旅行プラン':                       ['旅行プラン', 'モデルコース'],
}

DAICHI_MAP = {
    '道央': ['札幌', '札幌近郊(札幌以外)', '新千歳', '定山渓', '小樽近郊', 'ニセコ',
             '登別/白老/洞爺湖/苫小牧方面', 'トマム', '日高'],
    '道東': ['帯広近郊（十勝）', '釧路/根室/知床周辺', '網走（オホーツク周辺）'],
    '道南': ['函館近郊'],
    '道北': ['旭川近郊', '富良野・美瑛', '稚内（道北）'],
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
    m = re.search(r'[【\[]([^】\]]{3,80})[】\]]', caption)
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

    grume_kw = ['ラーメン', 'スープカレー', '海鮮', '寿司', '焼肉', 'ジンギスカン',
                'ソフトクリーム', 'スイーツ', 'カフェ', 'ケーキ', 'パン', '居酒屋',
                '丼', 'アイス', 'チーズ', 'バター', 'ミルク', 'グルメ', '横丁',
                '名店', '激ウマ', '絶品グルメ', 'ランチ', 'ディナー', 'レストラン',
                '食堂', '定食', 'ご当地', 'B級', '海老天', 'チキン', 'ザンギ',
                'ちゃんぽん', 'ビール', '日本酒', 'ウイスキー']
    omiyage_kw = ['お土産', 'おみやげ', '土産', '空港限定', 'お取り寄せ', 'ギフト',
                  '六花亭', '白い恋人', 'ロイズ', 'マルセイ', '北菓楼', 'もりもと',
                  '限定スイーツ']
    hotel_kw      = ['ホテル', '旅館', 'ヴィラ', 'ペンション', 'コテージ', 'グランピング',
                     '宿', '客室', '泊まって', '泊まり']
    hotel_body_kw = ['チェックイン', 'チェックアウト', '泊まってき', '宿泊して']
    onsen_kw  = ['温泉', '露天風呂', '大浴場', 'サウナ', 'ととのう', '湯めぐり',
                 '日帰り湯', '源泉', '温泉街', '足湯', '銭湯']
    event_kw  = ['まつり', '祭り', '花火', 'フェスタ', 'フェス', 'マルシェ', 'イベント',
                 'ライトアップ', '雪まつり', '朝市', 'フェア', 'festival']
    taiken_kw = ['スキー', 'スノーボード', '登山', 'トレッキング', 'ハイキング', 'カヌー',
                 'ラフティング', 'サイクリング', '乗馬', '釣り', 'キャンプ', 'ジップライン',
                 'さくらんぼ狩り', '果物狩り', '摘み取り', '掘り取り', '収穫体験',
                 'アウトドア体験', 'ツリートレッキング', 'パラグライダー', 'SUP',
                 'ウィンタースポーツ', 'スノーシュー', 'ナイタースキー']
    spot_kw   = ['公園', '展望', '夕日', '夕焼け', 'ラベンダー', '紅葉', '雪景色', '流氷',
                 '湖', '岬', 'フォトスポット', '絶景', '神社', '寺', '灯台', '滝', '夜景',
                 '観光スポット', '名所', '動物園', '水族館', '美術館', '博物館', '遊園地',
                 '庭園', '城', '砂丘', '氷瀑', '樹氷', 'ビュースポット', 'チューリップ',
                 '花畑', '菜の花', 'じゃがいも', '小麦畑', '牧場']

    if (re.search(r'[0-9１-９]+泊[0-9１-９]+日', title) or
        re.search(r'[0-9１-９]+選', title) or
        re.search(r'(完全攻略|おすすめ.+[0-9]+選|必見スポット|モデルコース|旅行プラン|観光ガイド|まとめ)', title)):
        return ['旅行プラン']

    cats = []

    is_hotel = (any(kw in title for kw in hotel_kw) or
                any(kw in body  for kw in hotel_body_kw))
    if is_hotel:
        cats.append('宿泊')

    if any(kw in body for kw in onsen_kw):
        cats.append('温泉')

    if any(kw in title for kw in grume_kw) and not is_hotel:
        cats.append('グルメ')

    if any(kw in title for kw in omiyage_kw):
        cats.append('お土産')
    elif any(kw in body for kw in ['お土産', 'おみやげ', '空港限定', 'お取り寄せ']):
        cats.append('お土産')

    if any(kw in title for kw in event_kw):
        cats.append('イベント')
    elif any(kw in body for kw in ['まつり', '祭り', '花火']):
        cats.append('イベント')

    is_grume = 'グルメ' in cats

    if any(kw in body for kw in taiken_kw) and not is_grume:
        cats.append('体験')

    if any(kw in title for kw in spot_kw) and not is_grume:
        cats.append('観光スポット')

    return cats

def fetch_instagram_posts():
    """Instagram API を使用して投稿を取得する"""
    all_posts = []
    url = (
        'https://graph.instagram.com/v21.0/me/media'
        '?fields=id,caption,media_url,thumbnail_url,permalink,timestamp,media_type'
        '&limit=50'
        f'&access_token={INSTAGRAM_TOKEN}'
    )
    while url:
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f'::error::Instagram API Error {e.code}: {body}')
            sys.exit(1)
        posts = data.get('data', [])
        all_posts.extend(posts)
        paging = data.get('paging', {})
        url = paging.get('next') if posts else None
    print(f'取得完了: {len(all_posts)}件')
    return all_posts

def fetch_existing_posts():
    github_sha = os.environ.get('GITHUB_SHA', '')
    if github_sha:
        raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/{github_sha}/{GITHUB_FILE}'
        print(f'コミットSHA指定でfetch: {github_sha[:8]}')
    else:
        sha = get_current_sha()
        if sha:
            raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/{sha}/{GITHUB_FILE}'
            print(f'APIからSHA取得してfetch: {sha[:8]}')
        else:
            raw_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE}'
    try:
        req = urllib.request.Request(raw_url)
        with urllib.request.urlopen(req) as resp:
            existing = json.loads(resp.read().decode())
        existing_map = {p['id']: p for p in existing if 'id' in p}
        print(f'既存データ: {len(existing_map)}件')
        return existing_map
    except Exception as e:
        print(f'既存データなし（新規作成）: {e}')
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
            area       = detect_area(caption) or ex.get('area', '')
            daichi     = detect_daichi(area)
            categories = ex.get('categories', [])
        else:
            area       = detect_area(caption)
            categories = detect_categories(caption)
            if '旅行プラン' in categories and not area:
                area = '北海道全体'
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

    print(f'新規: {new_count}件 / 既存引継ぎ: {len(formatted) - new_count}件')
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

# ═════════════════════════════════════════════
#  画像をリポジトリに保存（Instagramの画像URLは数日で期限切れになるため）
# ══════════════════════════════════════════════
IMAGE_DIR      = 'images'
IMAGE_BASE_URL = f'https://rooy81.github.io/tabito_hokkaido_post/{IMAGE_DIR}'

def gh_api(method, path, body=None):
    req = urllib.request.Request(
        f'https://api.github.com/repos/{GITHUB_REPO}{path}',
        data=json.dumps(body).encode('utf-8') if body is not None else None,
        method=method
    )
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    if body is not None:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def existing_image_ids():
    """リポジトリに保存済みの画像ID一覧（チェックアウト済みのフォルダとAPIの両方を確認）"""
    ids = set()
    if os.path.isdir(IMAGE_DIR):
        ids |= {f[:-4] for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')}
    try:
        tree = gh_api('GET', '/git/trees/main?recursive=1')
        for t in tree.get('tree', []):
            p = t.get('path', '')
            if p.startswith(IMAGE_DIR + '/') and p.endswith('.jpg'):
                ids.add(p[len(IMAGE_DIR) + 1:-4])
    except Exception as e:
        print(f'画像一覧の取得に失敗（続行）: {e}')
    return ids

def download(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def attach_images(posts):
    """新しい投稿の画像をダウンロードし、各投稿の画像URLを自前の保存先に差し替える"""
    saved   = existing_image_ids()
    new_imgs = {}
    for p in posts:
        pid = p['id']
        ig_url = p.get('thumbnail_url') or p.get('media_url') or ''
        p['ig_thumbnail_url'] = ig_url
        if pid not in saved and ig_url:
            try:
                new_imgs[pid] = download(ig_url)
                saved.add(pid)
            except Exception as e:
                print(f'画像DL失敗 {pid}: {e}')
        if pid in saved:
            p['thumbnail_url'] = f'{IMAGE_BASE_URL}/{pid}.jpg'
    print(f'画像: 新規保存 {len(new_imgs)}件 / 保存済み {len(saved)}件')
    return new_imgs

def commit_all(posts, new_imgs):
    """posts.json と新しい画像を1つのコミットでまとめて保存"""
    ref        = gh_api('GET', '/git/ref/heads/main')
    head_sha   = ref['object']['sha']
    base_tree  = gh_api('GET', f'/git/commits/{head_sha}')['tree']['sha']

    entries = []
    for i, (pid, data) in enumerate(new_imgs.items(), 1):
        blob = gh_api('POST', '/git/blobs', {
            'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'})
        entries.append({'path': f'{IMAGE_DIR}/{pid}.jpg', 'mode': '100644',
                        'type': 'blob', 'sha': blob['sha']})
        if i % 50 == 0:
            print(f'  画像アップロード {i}/{len(new_imgs)}')

    posts_json = json.dumps(posts, ensure_ascii=False, indent=2)
    entries.append({'path': GITHUB_FILE, 'mode': '100644', 'type': 'blob',
                    'content': posts_json})

    tree   = gh_api('POST', '/git/trees', {'base_tree': base_tree, 'tree': entries})
    commit = gh_api('POST', '/git/commits', {
        'message': f'Auto update: {len(posts)} posts (+{len(new_imgs)} images)',
        'tree': tree['sha'], 'parents': [head_sha]})
    gh_api('PATCH', '/git/refs/heads/main', {'sha': commit['sha']})
    print(f"保存完了: {commit['sha'][:8]}")

existing_map = fetch_existing_posts()
raw          = fetch_instagram_posts()
posts        = format_posts(raw, existing_map)
new_imgs     = attach_images(posts)
commit_all(posts, new_imgs)
