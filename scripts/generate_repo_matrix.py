#!/usr/bin/env python3
"""
Generate a GitHub Actions matrix from walrus_haulout_data.csv.

输出一个 JSON 数组，每个元素形如:
{
    "src": "github/owner",                   # 源用户/组织（需要 github 前缀）
    "dst": "github/target_org",              # 目标组织（需要 github 前缀）
    "static_list": "repo",                   # 要 fork 的具体仓库名
    "force_update": true                     # 强制更新已存在的仓库
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
OFFSET = int(os.getenv('OFFSET') or 0)
LIMIT  = int(os.getenv('LIMIT') or 256)
# ------------------------------------------------

repos = []
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        github_url = row.get('github_url', '').strip()
        if not github_url:
            continue

        # 移除协议和域名前缀（如 https://github.com/）
        # 支持 https://github.com/ 和 http://github.com/ 以及不带协议的格式
        github_url = github_url.replace('https://github.com/', '').replace('http://github.com/', '')
        
        # 统一去掉可能的 .git 后缀，然后取最后两个路径段作为 owner / repo
        parts = github_url.rstrip('.git').rstrip('/').split('/')
        if len(parts) < 2:
            # 跳过只有 owner 没有 repo 的 URL
            continue
        owner, repo = parts[0], parts[1]

        # hub-mirror-action 的正确格式:
        # src: github/源用户名, dst: github/目标组织, static_list: 仓库名, force_update: true
        repos.append({
            "src": f"github/{owner}",
            "dst": f"github/{TARGET_ORG}",
            "static_list": repo,
            "force_update": True
        })

# ------------------- 分页 -------------------
# 先做 offset，再做 limit，确保不会超出列表范围
selected = repos[OFFSET:OFFSET + LIMIT]
print(json.dumps(selected))