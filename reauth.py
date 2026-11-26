#!/usr/bin/env python3
"""
Instagramトークンの再取得（ログインが無効にされたとき用）
使い方: https://rooy81.github.io/tabito_hokkaido_post/?reauth を開いて「許可」
        → 表示されたコードを Actions の「Reauth Instagram」に貼って Run workflow
"""
import os, sys, json, base64, subprocess, urllib.request, urllib.parse, urllib.error

APP_ID      = '856277193666740'
REDIRECT    = 'https://rooy81.github.io/tabito_hokkaido_post/'
GITHUB_REPO = 'rooy81/tabito_hokkaido_post'

code       = os.environ['CODE'].strip().split('#')[0]
app_secret = os.environ['IG_APP_SECRET']
gh_token   = os.environ['MY_GITHUB_TOKEN']
if 'code=' in code:  # URLごと貼られた場合
    code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get('code', [''])[0]

def get_json(req):
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f'::error::HTTP {e.code}: {e.read().decode()}')
        sys.exit(1)

# 1. コード → 短期トークン
short = get_json(urllib.request.Request(
    'https://api.instagram.com/oauth/access_token',
    data=urllib.parse.urlencode({
        'client_id': APP_ID, 'client_secret': app_secret,
        'grant_type': 'authorization_code', 'redirect_uri': REDIRECT, 'code': code,
    }).encode()))['access_token']
print(f'::add-mask::{short}')
print('短期トークン取得OK')

# 2. 短期 → 長期（60日）
res = get_json(urllib.request.Request(
    'https://graph.instagram.com/access_token?grant_type=ig_exchange_token'
    f'&client_secret={app_secret}&access_token={short}'))
token = res['access_token']
print(f'::add-mask::{token}')
print(f"長期トークン取得OK（{int(res.get('expires_in', 0)) // 86400}日）")

# 3. GitHub Secret INSTAGRAM_TOKEN を更新
subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyNaCl', '--quiet'], check=True)
from nacl import encoding, public

def gh(method, path, body=None):
    req = urllib.request.Request(
        f'https://api.github.com/repos/{GITHUB_REPO}{path}',
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={'Authorization': f'Bearer {gh_token}',
                 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return r.status, (r.read().decode() or '{}')

_, pk = gh('GET', '/actions/secrets/public-key')
pk = json.loads(pk)
box = public.SealedBox(public.PublicKey(pk['key'].encode(), encoding.Base64Encoder()))
enc = base64.b64encode(box.encrypt(token.encode())).decode()
st, _ = gh('PUT', '/actions/secrets/INSTAGRAM_TOKEN', {'encrypted_value': enc, 'key_id': pk['key_id']})
print(f'INSTAGRAM_TOKEN 更新: HTTP {st}')

# 4. 投稿の取得を実行
st, _ = gh('POST', '/actions/workflows/update_posts.yml/dispatches', {'ref': 'main'})
print(f'update_posts 起動: HTTP {st}')
print('完了！1〜5分でサイトに反映されます。')
