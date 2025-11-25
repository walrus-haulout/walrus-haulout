# Fork Hackathon Projects - GitHub Action

This GitHub Action automatically forks all Walrus Haulout Hackathon projects from `walrus_haulout_data.csv` to the `walrus-haulout` organization.

## 🎯 Overview

The fork automation system consists of:
- **GitHub Action**: `.github/workflows/fork-projects.yml` - Workflow definition
- **Python Script**: `scripts/fork_projects.py` - Core forking logic with retry handling
- **Data Source**: `walrus_haulout_data.csv` - Project list extracted from DeepSurge

## 🔧 Setup

### Step 1: Create a GitHub Personal Access Token

1. Navigate to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Configure the token:
   - **Note**: `Walrus Haulout Fork Bot`
   - **Expiration**: `No expiration` (or as needed)
   - **Select scopes**:
     ```
     ✅ repo (Full control of repositories)
        ✅ repo:status
        ✅ repo_deployment
        ✅ public_repo
        ✅ repo:invite
     ✅ workflow (Update GitHub Action workflows)
     ✅ admin:org (Full control of orgs and teams)
        ✅ write:org - Required to fork to organization
        ✅ read:org
     ```
4. Click **"Generate token"**
5. **Copy the token immediately** (format: `ghp_xxxxxxxxxxxx...`)

### Step 2: Add Token to Repository Secrets

1. Go to repository: `https://github.com/walrus-haulout/walrus-haulout/settings/secrets/actions`
2. Click **"New repository secret"**
3. Configure:
   - **Name**: `FORK_TOKEN`
   - **Value**: Paste your personal access token
4. Click **"Add secret"**

### Step 3: Verify CSV Data Format

Ensure `walrus_haulout_data.csv` contains the following required columns:
- `projectName` - Project name (for reporting)
- `github_url` - Full GitHub repository URL

Example:
```csv
projectName,github_url,track,status
Backstage,https://github.com/N3xt-Ep0ch-L4bs/Backstage-app,Data Marketplaces,submitted
ALETHEIA,https://github.com/preyam2002/Aletheia,Provably Authentic,submitted
```

## 🚀 Usage

### Manual Trigger (Recommended for First Run)

1. Go to **Actions** tab: `https://github.com/walrus-haulout/walrus-haulout/actions`
2. Select **"Fork Hackathon Projects"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Monitor the workflow execution in real-time

### Automatic Schedule

The workflow runs automatically **every Sunday at midnight UTC** (`cron: '0 0 * * 0'`).

To modify the schedule, edit `.github/workflows/fork-projects.yml`:
```yaml
schedule:
  - cron: '0 0 * * 0'  # Change this cron expression
```

## 📊 Features

### Intelligent Retry Logic

The script includes robust error handling:
- **Automatic Retries**: Up to 5 attempts per repository
- **Exponential Backoff**: 2s → 4s → 8s → 16s → 32s
- **Rate Limit Handling**: Respects `Retry-After` headers
- **Timeout Protection**: 30-second timeout per API call

### Error Handling

| Error Type | Status Code | Behavior |
|------------|-------------|----------|
| Success | 202 | Fork created successfully |
| Already Exists | 403 | Skipped (counted as success) |
| Not Found | 404 | Repository private or doesn't exist |
| Rate Limited | 403 | Wait and retry with backoff |
| Timeout | N/A | Retry up to 5 times |

### Polite API Usage

- **5-second delay** between each fork request
- Prevents rate limiting issues
- Total time for 256 projects: ~21 minutes

## 📥 Output

### Workflow Logs

View detailed logs in the Actions tab:
```
Starting fork process to organization: walrus-haulout
Found 256 projects with GitHub URLs

[1/256] Forking N3xt-Ep0ch-L4bs/Backstage-app...
  ✓ Successfully forked N3xt-Ep0ch-L4bs/Backstage-app
[2/256] Forking preyam2002/Aletheia...
  ✓ Successfully forked preyam2002/Aletheia
...

============================================================
Fork Summary:
  Total: 256
  Successful: 250
  Failed: 6
  Report saved to: fork_report.json
============================================================
```

### Fork Report Artifact

Download the `fork-report` artifact for detailed JSON report:

```json
{
  "total": 256,
  "successful": 250,
  "failed": 6,
  "results": [
    {
      "project_name": "Backstage",
      "github_url": "https://github.com/N3xt-Ep0ch-L4bs/Backstage-app",
      "owner": "N3xt-Ep0ch-L4bs",
      "repo": "Backstage-app",
      "success": true,
      "message": "Successfully forked N3xt-Ep0ch-L4bs/Backstage-app"
    }
  ]
}
```

**Artifact retention**: 30 days

## 🔍 Troubleshooting

### Common Issues

**Issue**: `ERROR: FORK_TOKEN environment variable not set`
- **Solution**: Verify `FORK_TOKEN` is properly configured in repository secrets

**Issue**: `Bad credentials (401)`
- **Solution**: Regenerate personal access token with correct scopes

**Issue**: `Repository not found (404)`
- **Cause**: Repository is private or doesn't exist
- **Solution**: Check if you have access to the source repository

**Issue**: `Rate limited`
- **Solution**: Wait for the retry mechanism to handle it, or increase delay in `fork_projects.py`

### Verify Token Permissions

Test your token locally:
```bash
export GITHUB_TOKEN="your_token_here"
export TARGET_ORG="walrus-haulout"
python scripts/fork_projects.py
```

## 🏗️ Implementation Details

### Architecture

```
.github/workflows/fork-projects.yml
    ↓ triggers
scripts/fork_projects.py
    ↓ reads
walrus_haulout_data.csv
    ↓ forks to
github.com/walrus-haulout/*
    ↓ generates
fork_report.json
```

### Python Dependencies

```txt
requests>=2.25.1  # GitHub API calls
pandas>=1.3.0     # CSV processing
```

### Key Functions

- `parse_github_url(url)` - Extract owner/repo from GitHub URLs
- `fork_repository(owner, repo, target_org)` - Fork with retry logic
- `main()` - Orchestrates the entire forking process

## 📝 Best Practices

1. **First Run**: Use manual trigger to monitor progress
2. **Token Security**: Never commit tokens to git
3. **Rate Limits**: Keep 5-second delay between forks
4. **CSV Updates**: Run scraper (`streamlit run app.py`) to update project list
5. **Error Review**: Check fork report for failed repositories

## 🔄 Workflow Configuration

Current configuration in `.github/workflows/fork-projects.yml`:

```yaml
name: Fork Hackathon Projects
on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

env:
  GITHUB_TOKEN: ${{ secrets.FORK_TOKEN }}
  TARGET_ORG: walrus-haulout
```

## 📚 Additional Resources

- [GitHub API - Create Fork](https://docs.github.com/en/rest/repos/forks#create-a-fork)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Managing Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

---

**Last Updated**: 2025-11-25  
**Maintained by**: Walrus Haulout Community
