#!/usr/bin/env python3
"""
Fork all GitHub projects from walrus_haulout_data.csv to the target organization.
"""

import os
import csv
import json
import time
import requests
from urllib.parse import urlparse

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
GITHUB_TOKEN = os.getenv('FORK_TOKEN') or os.getenv('GITHUB_TOKEN')
TARGET_ORG = os.getenv('TARGET_ORG', 'walrus-haulout')
CSV_FILE = 'walrus_haulout_data.csv'
REPORT_FILE = 'fork_report.json'

# GitHub API base URL
API_BASE = 'https://api.github.com'

def parse_github_url(url):
    """
    Extract owner and repo name from GitHub URL.
    Examples:
    - https://github.com/owner/repo -> (owner, repo)
    - https://github.com/owner/repo.git -> (owner, repo)
    """
    if not url or 'github.com' not in url.lower():
        return None, None
    
    try:
        path = urlparse(url).path.strip('/')
        # Remove .git suffix if present
        if path.endswith('.git'):
            path = path[:-4]
        
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
    except:
        pass
    
    return None, None

def fork_repository(owner, repo, target_org):
    """Fork a repository to the target organization with retry handling.

    Returns:
        tuple[bool, str]: (success, message)
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/forks"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"organization": target_org}

    max_retries = 5
    backoff = 2  # seconds, will double each retry
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.Timeout:
            if attempt == max_retries:
                return False, f"Timeout while forking {owner}/{repo}"
            time.sleep(backoff)
            backoff *= 2
            continue
        except Exception as e:
            return False, f"Error forking {owner}/{repo}: {str(e)}"

        if response.status_code == 202:
            return True, f"Successfully forked {owner}/{repo}"
        if response.status_code == 404:
            return False, f"Repository {owner}/{repo} not found or private"
        if response.status_code == 403:
            # Rate limiting detection
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_seconds = int(retry_after)
                except ValueError:
                    wait_seconds = 60
                if attempt < max_retries:
                    time.sleep(wait_seconds)
                    continue
                return False, f"Rate limited: retry after {wait_seconds}s"
            # Fork already exists case
            error_msg = response.json().get("message", "Unknown error")
            if "already exists" in error_msg.lower():
                return True, f"Fork already exists for {owner}/{repo}"
            return False, f"Permission denied: {error_msg}"
        # Other non‑success statuses
        if attempt < max_retries:
            # Exponential backoff before retrying
            time.sleep(backoff)
            backoff *= 2
            continue
        return False, f"Failed to fork {owner}/{repo}: {response.status_code} - {response.text}"


def main():
    if not GITHUB_TOKEN:
        print("ERROR: FORK_TOKEN (or GITHUB_TOKEN) environment variable not set")
        return 1
    
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: CSV file {CSV_FILE} not found")
        return 1
    
    print(f"Starting fork process to organization: {TARGET_ORG}")
    print(f"Reading projects from: {CSV_FILE}\n")
    
    # Read CSV and extract GitHub URLs
    projects = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            github_url = row.get('github_url', '').strip()
            if github_url:
                owner, repo = parse_github_url(github_url)
                if owner and repo:
                    projects.append({
                        'project_name': row.get('projectName', 'Unknown'),
                        'github_url': github_url,
                        'owner': owner,
                        'repo': repo
                    })
    
    print(f"Found {len(projects)} projects with GitHub URLs\n")
    
    # Fork each repository
    report = {
        'total': len(projects),
        'successful': 0,
        'failed': 0,
        'results': []
    }
    
    for i, project in enumerate(projects, 1):
        print(f"[{i}/{len(projects)}] Forking {project['owner']}/{project['repo']}...")
        
        success, message = fork_repository(project['owner'], project['repo'], TARGET_ORG)
        
        result = {
            'project_name': project['project_name'],
            'github_url': project['github_url'],
            'owner': project['owner'],
            'repo': project['repo'],
            'success': success,
            'message': message
        }
        
        report['results'].append(result)
        
        if success:
            report['successful'] += 1
            print(f"  ✓ {message}")
        else:
            report['failed'] += 1
            print(f"  ✗ {message}")
        
        # Polite delay between forks (increased to 5 seconds)
        if i < len(projects):
            time.sleep(5)
    
    # Save report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Fork Summary:")
    print(f"  Total: {report['total']}")
    print(f"  Successful: {report['successful']}")
    print(f"  Failed: {report['failed']}")
    print(f"  Report saved to: {REPORT_FILE}")
    print(f"{'='*60}")
    
    return 0 if report['failed'] == 0 else 1

if __name__ == '__main__':
    exit(main())
