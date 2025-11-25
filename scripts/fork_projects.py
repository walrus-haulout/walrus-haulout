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

# Feature flags
SYNC_EXISTING_FORKS = os.getenv('SYNC_EXISTING_FORKS', 'true').lower() in ('true', '1', 'yes')

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

def check_fork_exists(owner, repo, target_org):
    """Check if a fork already exists in the target organization.
    
    Returns:
        tuple[bool, str]: (exists, message)
    """
    # The forked repo will have the same name as the original
    url = f"{API_BASE}/repos/{target_org}/{repo}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Repository exists, check if it's a fork
            repo_data = response.json()
            if repo_data.get('fork'):
                # Verify it's a fork of the source repo
                source = repo_data.get('source', {})
                if source.get('owner', {}).get('login') == owner and source.get('name') == repo:
                    return True, f"Fork of {owner}/{repo} already exists at {target_org}/{repo}"
            # Repository exists but not a fork of this source
            return True, f"Repository {target_org}/{repo} exists (but not a fork of {owner}/{repo})"
        elif response.status_code == 404:
            # Repository doesn't exist, safe to fork
            return False, ""
        else:
            # Other errors, assume doesn't exist to attempt fork
            return False, f"Could not verify (status {response.status_code})"
    except Exception as e:
        # On error, assume doesn't exist to attempt fork
        return False, f"Could not verify: {str(e)}"


def sync_fork(owner, repo, target_org):
    """Sync an existing fork with its upstream repository.
    
    Returns:
        tuple[bool, str]: (success, message)
    """
    url = f"{API_BASE}/repos/{target_org}/{repo}/merge-upstream"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"branch": "main"}  # Try main first
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return True, f"Successfully synced {target_org}/{repo} with {owner}/{repo}"
        elif response.status_code == 409:
            # Already up to date or merge conflict
            result = response.json()
            message = result.get('message', '')
            if 'up to date' in message.lower():
                return True, f"Fork {target_org}/{repo} is already up to date"
            return False, f"Cannot sync {target_org}/{repo}: {message}"
        elif response.status_code == 422:
            # Try with master branch
            data = {"branch": "master"}
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return True, f"Successfully synced {target_org}/{repo} with {owner}/{repo}"
            elif response.status_code == 409:
                result = response.json()
                message = result.get('message', '')
                if 'up to date' in message.lower():
                    return True, f"Fork {target_org}/{repo} is already up to date"
            return False, f"Cannot sync {target_org}/{repo}: branch mismatch or conflict"
        else:
            return False, f"Failed to sync {target_org}/{repo}: {response.status_code}"
    except Exception as e:
        return False, f"Error syncing {target_org}/{repo}: {str(e)}"



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

    max_retries = 10  # Increased for 'submitted too quickly' errors
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
            error_msg = response.json().get("message", "Unknown error")
            
            # Special handling for "submitted too quickly" error
            if "submitted too quickly" in error_msg.lower():
                if attempt < max_retries:
                    # Wait longer for this specific error (60 seconds)
                    wait_time = 60
                    print(f"    ⚠️  Rate limited (submitted too quickly), waiting {wait_time}s... (attempt {attempt}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                return False, f"Permission denied: {error_msg}"
            
            # Rate limiting detection (Retry-After header)
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_seconds = int(retry_after)
                except ValueError:
                    wait_seconds = 60
                if attempt < max_retries:
                    print(f"    ⚠️  Rate limited, waiting {wait_seconds}s... (attempt {attempt}/{max_retries})")
                    time.sleep(wait_seconds)
                    continue
                return False, f"Rate limited: retry after {wait_seconds}s"
            
            # Fork already exists case
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
    print(f"Configuration:")
    print(f"  - Sync existing forks: {'✓ Enabled' if SYNC_EXISTING_FORKS else '✗ Disabled'}")
    print(f"  - Delay between operations: 10 seconds")
    print(f"  - Max retries per fork: 10")
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
        'skipped': 0,
        'synced': 0,
        'forked': 0,
        'results': []
    }
    
    for i, project in enumerate(projects, 1):
        owner = project['owner']
        repo = project['repo']
        
        print(f"[{i}/{len(projects)}] Processing {owner}/{repo}...")
        
        # Step 1: Check if fork already exists
        exists, check_msg = check_fork_exists(owner, repo, TARGET_ORG)
        
        if exists:
            # Repository already exists in target org
            if "already exists at" in check_msg:
                # It's a valid fork
                if SYNC_EXISTING_FORKS:
                    # Sync is enabled, try to update it
                    print(f"  📦 Fork exists, attempting to sync...")
                    success, message = sync_fork(owner, repo, TARGET_ORG)
                    
                    result = {
                        'project_name': project['project_name'],
                        'github_url': project['github_url'],
                        'owner': owner,
                        'repo': repo,
                        'action': 'sync',
                        'success': success,
                        'message': message
                    }
                    
                    if success:
                        report['successful'] += 1
                        report['synced'] += 1
                        print(f"  ✓ {message}")
                    else:
                        # Sync failed, but fork exists - count as skipped
                        report['skipped'] += 1
                        print(f"  ⚠️  {message} (fork exists but sync failed)")
                        result['success'] = True  # Don't count as failure
                        result['message'] = f"Fork exists ({message})"
                else:
                    # Sync is disabled, just skip
                    report['skipped'] += 1
                    result = {
                        'project_name': project['project_name'],
                        'github_url': project['github_url'],
                        'owner': owner,
                        'repo': repo,
                        'action': 'skip',
                        'success': True,
                        'message': f"Fork already exists at {TARGET_ORG}/{repo} (sync disabled)"
                    }
                    print(f"  ⏭️  Fork already exists (sync disabled)")
            else:
                # Repository exists but not a fork of the source - skip
                report['skipped'] += 1
                result = {
                    'project_name': project['project_name'],
                    'github_url': project['github_url'],
                    'owner': owner,
                    'repo': repo,
                    'action': 'skip',
                    'success': True,
                    'message': check_msg
                }
                print(f"  ⏭️  {check_msg}")
        else:
            # Fork doesn't exist, create it
            print(f"  🔄 Creating fork...")
            success, message = fork_repository(owner, repo, TARGET_ORG)
            
            result = {
                'project_name': project['project_name'],
                'github_url': project['github_url'],
                'owner': owner,
                'repo': repo,
                'action': 'fork',
                'success': success,
                'message': message
            }
            
            if success:
                report['successful'] += 1
                report['forked'] += 1
                print(f"  ✓ {message}")
            else:
                report['failed'] += 1
                print(f"  ✗ {message}")
        
        report['results'].append(result)
        
        # Increased delay between operations (10 seconds)
        # This helps avoid "submitted too quickly" errors
        if i < len(projects):
            time.sleep(10)
    
    # Save report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Fork Summary:")
    print(f"  Total: {report['total']}")
    print(f"  Successful: {report['successful']}")
    print(f"    - New forks: {report['forked']}")
    print(f"    - Synced: {report['synced']}")
    print(f"  Skipped: {report['skipped']}")
    print(f"  Failed: {report['failed']}")
    print(f"  Report saved to: {REPORT_FILE}")
    print(f"{'='*60}")
    
    # Always return 0 to allow the workflow to continue and upload the report
    # Failures are logged in the report and printed to stdout
    if report['failed'] > 0:
        print(f"\n⚠️  Completed with {report['failed']} failures. Check the report for details.")
    
    return 0

if __name__ == '__main__':
    exit(main())
