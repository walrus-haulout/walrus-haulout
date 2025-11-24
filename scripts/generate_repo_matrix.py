#!/usr/bin/env python3
"""
Generate a GitHub Actions matrix from walrus_haulout_data.csv.

输出一个 JSON 数组，每个元素形如:
{
    "src": "owner/repo",                     # 要 fork 的源仓库
    "dst": "target_org/owner-repo"           # 目标组织下的仓库名（可自行改写）
}
"""

import csv
import json
import os
import sys

# ------------------- 配置 -------------------
CSV_FILE   = os.getenv('CSV_FILE', 'walrus_haulout_data.csv')
TARGET_ORG = os.getenv('TARGET_ORG', 'walrus-haulout')

# 分页控制（可在 workflow 中通过 env 传入）
#   OFFSET：从第几条记录开始（0‑based）
#   LIMIT ：最多返回多少条（默认 256，符合 GitHub Actions 限制）
OFFSET = int(os.getenv('OFFSET', '0'))
LIMIT  = int(os.getenv('LIMIT', '256'))
# ------------------------------------------------

repos = []
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        github_url = row.get('github_url', '').strip()
        if not github_url:
            continue

        # 统一去掉可能的 .git 后缀，然后取最后两个路径段作为 owner / repo
        parts = github_url.rstrip('.git').split('/')
        if len(parts) < 2:
            continue
        owner, repo = parts[-2], parts[-1]

        src = f"{owner}/{repo}"
        dst = f"{TARGET_ORG}/{owner}-{repo}"   # 你可以自行改成其他命名规则
        repos.append({"src": src, "dst": dst})

# ------------------- 分页 -------------------
# 先做 offset，再做 limit，确保不会超出列表范围
selected = repos[OFFSET:OFFSET + LIMIT]
print(json.dumps(selected))