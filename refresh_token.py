import os, urllib.request, urllib.error, json, base64, sys, subprocess

subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyNaCl', '--quiet'], check=True)
from nacl import encoding, public

INSTAGRAM_TOKEN = os.environ['INSTAGRAM_TOKEN']
MY_GITHUB_TOKEN = os.environ['MY_GITHUB_TOKEN']
GITHUB_REPO     = 'rooy81/tabito_hokkaido_post'

# 1. Refresh Instagram token
print('Refreshing Instagram token...')
url = (
    'https://graph.instagram.com/refresh_access_token'
    '?grant_type=ig_refresh_token'
    f'&access_token={INSTAGRAM_TOKEN}'
)
try:
    with urllib.request.urlopen(urllib.request.Request(url)) as r:
        data = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    print(f'::error::Instagram refresh failed {e.code}: {e.read().decode()}')
    sys.exit(1)

new_token  = data['access_token']
expires_in = data.get('expires_in', 0)
print(f'Token refreshed — expires in {int(expires_in)//86400} days')

# 2. Encrypt and update GitHub Secret
def gh_get(path):
    req = urllib.request.Request(
        f'https://api.github.com{path}',
        headers={'Authorization': f'Bearer {MY_GITHUB_TOKEN}',
                 'Accept': 'application/vnd.github.v3+json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def gh_put(path, body):
    req = urllib.request.Request(
        f'https://api.github.com{path}',
        data=json.dumps(body).encode(), method='PUT',
        headers={'Authorization': f'Bearer {MY_GITHUB_TOKEN}',
                 'Accept': 'application/vnd.github.v3+json',
                 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return r.status

pk  = gh_get(f'/repos/{GITHUB_REPO}/actions/secrets/public-key')
box = public.SealedBox(public.PublicKey(pk['key'].encode(), encoding.Base64Encoder()))
enc = base64.b64encode(box.encrypt(new_token.encode())).decode()
st  = gh_put(f'/repos/{GITHUB_REPO}/actions/secrets/INSTAGRAM_TOKEN',
             {'encrypted_value': enc, 'key_id': pk['key_id']})
print(f'GitHub Secret updated (HTTP {st})')
print('Done!')
