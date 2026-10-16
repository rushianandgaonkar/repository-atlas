"""Build a public-only catalog. No third-party Python dependencies."""
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote
import time

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'rushianandgaonkar'
EXCLUDED = {'repository-atlas'}

def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'repository-atlas-sync'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    for attempt in range(3):
        try:
            with urlopen(Request('https://api.github.com/' + path, headers=headers), timeout=40) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))

def public_repositories():
    result = []
    page = 1
    while True:
        batch = api(f'users/{OWNER}/repos?type=owner&per_page=100&page={page}')
        result.extend(r for r in batch if not r.get('private', True) and r['owner']['login'].lower() == OWNER.lower() and r['name'].lower() not in EXCLUDED)
        if len(batch) < 100:
            return result
        page += 1

def entry(meta, curated, upstream=None):
    """Merge live metadata with reviewed instructions; never infer runnable commands."""
    name = meta['name']
    old = curated.get(name, {})
    parent = upstream or {}
    url = meta['html_url']
    row = dict(old)
    row.update(name=name, category=old.get('category', 'New — needs review'),
        description=old.get('description') or meta.get('description') or 'No description provided. Open the README to learn more.',
        githubDescription=meta.get('description') or '', url=url, fork=bool(meta['fork']), private=False,
        stars=meta['stargazers_count'], forks=meta['forks_count'],
        upstream=parent.get('full_name'), upstreamUrl=parent.get('html_url'),
        upStars=parent.get('stargazers_count'), upForks=parent.get('forks_count'),
        language=meta.get('language') or 'Not specified',
        license=(meta.get('license') or {}).get('spdx_id') or 'Not specified',
        pushed=(meta.get('pushed_at') or '')[:10], upPushed=(parent.get('pushed_at') or '')[:10],
        archived=bool(meta.get('archived')), branch=meta['default_branch'])
    if not old:
        row.update(kind='Needs setup review', requirements='See the repository README',
            steps=['Open the repository README using the setup source link.',
                   'Check supported operating systems, prerequisites and configuration.',
                   'Follow the maintainer’s setup guide. Custom instructions have not been reviewed yet.'],
            command='', doc=url+'#readme', readmeVerified=False)
    return row

def build(rows, timestamp):
    assert all(not r['private'] and r['name'].lower() not in EXCLUDED for r in rows)
    template = (ROOT/'template.html').read_text()
    page = template.replace('__DATA__', json.dumps(rows, ensure_ascii=False).replace('<', '\\u003c'))
    page = page.replace('__SYNCED_AT__', json.dumps(timestamp))
    output = ROOT/'_site'
    output.mkdir(exist_ok=True)
    (output/'index.html').write_text(page)
    (output/'catalog.json').write_text(json.dumps({'syncedAt':timestamp, 'repositories':rows}, ensure_ascii=False, indent=2)+'\n')
    (output/'.nojekyll').touch()

def main():
    curated = {r['name']:r for r in json.loads((ROOT/'curated.json').read_text()) if not r.get('private', True)}
    rows=[]
    for meta in public_repositories():
        upstream=None
        if meta['fork']:
            detail=api('repos/'+quote(meta['full_name'], safe='/'))
            upstream=detail.get('parent')
            # Fail the build rather than publish incomplete upstream statistics.
            if upstream:
                upstream=api('repos/'+quote(upstream['full_name'], safe='/'))
        rows.append(entry(meta, curated, upstream))
    if not rows:
        raise RuntimeError('Empty inventory; refusing to replace the existing site.')
    build(rows, datetime.now(timezone.utc).isoformat())
    print(f'Built {len(rows)} public repositories.')

if __name__ == '__main__':
    main()
