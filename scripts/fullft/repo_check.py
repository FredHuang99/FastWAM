"""Read-only look at a public GitHub repository through the GitHub API (11-22, Opus; Insight v2 6.3 fact 5: has
MaP-WAM released code?). Lists the top-level entries, the last push time and the size; downloads nothing else and
runs nothing from the repository.
  /opt/mwam/bin/python scripts/fullft/repo_check.py aipixel/MaP-WAM
"""
import json
import sys
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "repo-check"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


for repo in sys.argv[1:]:
    try:
        meta = get(f"https://api.github.com/repos/{repo}")
        print(f"{repo}: pushed {meta.get('pushed_at')}, size {meta.get('size')} KB, stars {meta.get('stargazers_count')}, "
              f"description {meta.get('description')!r}")
        items = get(f"https://api.github.com/repos/{repo}/contents")
        print("  top level:", [f"{x.get('name')}{'/' if x.get('type') == 'dir' else ''}" for x in items])
    except Exception as e:                                          # noqa: BLE001
        print(f"{repo}: {type(e).__name__}: {e}")
