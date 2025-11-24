#!/usr/bin/env python3
"""Generate a GitHub Actions matrix from walrus_haulout_data.csv.
The output is a JSON array of objects with keys:
  src: "owner/repo"
  dst: "target_org/owner-repo" (optional, can be same as src)
"""
import csv, json, os, sys

CSV_FILE = os.getenv('CSV_FILE', 'walrus_haulout_data.csv')
TARGET_ORG = os.getenv('TARGET_ORG', 'walrus-haulout')

repos = []
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row.get('github_url', '').strip()
        if not url:
            continue
        # extract owner/repo
        parts = url.rstrip('.git').split('/')
        if len(parts) < 2:
            continue
        owner, repo = parts[-2], parts[-1]
        src = f"{owner}/{repo}"
        dst = f"{TARGET_ORG}/{owner}-{repo}"  # optional naming scheme
        repos.append({"src": src, "dst": dst})

print(json.dumps(repos))
