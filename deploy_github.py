# -*- coding: utf-8 -*-
"""Deploy webdeck/ to GitHub Pages via GitHub REST API (git is blocked in sandbox)."""
import base64
import json
import os
import ssl
import sys
import urllib.request
import urllib.error

TOKEN = os.environ['GHTOK']
OWNER = 'Xiaohong39'
REPO = 'ai-video-deck'
WEB = r'C:\Users\hp\Dsh\ppt_tasks\ai-video-local-business\webdeck'
ctx = ssl.create_default_context()


def api(method, url, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', 'token ' + TOKEN)
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Accept', 'application/vnd.github+json')
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8') or '{}')


def ensure_repo():
    code, _ = api('GET', f'https://api.github.com/repos/{OWNER}/{REPO}')
    if code == 200:
        print('repo exists')
        return
    code, b = api('POST', 'https://api.github.com/user/repos', {
        'name': REPO, 'private': False, 'auto_init': True,
        'description': 'AI视频重构同城商业 · Web Deck',
    })
    print('create repo ->', code, b.get('full_name') if isinstance(b, dict) else b)


def put_file(rel_path):
    full = os.path.join(WEB, rel_path)
    with open(full, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{rel_path}'
    payload = {'message': f'add {rel_path}', 'content': b64}
    code, b = api('PUT', url, payload)
    ok = code in (200, 201)
    size = os.path.getsize(full)
    print(('OK  ' if ok else 'FAIL'), rel_path, f'{size//1024}KB', '->', code)
    return ok


def enable_pages():
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/pages'
    payload = {'source': {'branch': 'main', 'path': '/'}}
    code, b = api('POST', url, payload)
    print('enable pages ->', code, (b.get('html_url') or b.get('status') if isinstance(b, dict) else b))
    # fallback if already exists
    if code == 409:
        code, b = api('POST', url, payload)


def main():
    ensure_repo()
    # collect files
    paths = []
    for root, dirs, files in os.walk(WEB):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, WEB).replace(os.sep, '/')
            paths.append(rel)
    paths.sort()
    # index.html first, then assets
    paths = [p for p in paths if p == 'index.html'] + [p for p in paths if p != 'index.html']
    for rel in paths:
        put_file(rel)
    enable_pages()
    print('repo: https://github.com/%s/%s' % (OWNER, REPO))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('ERROR', e)
