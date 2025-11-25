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

## ⚙️ Configuration Options

You can customize the fork automation behavior using environment variables in `.github/workflows/fork-projects.yml`:

### SYNC_EXISTING_FORKS

Controls whether to automatically sync existing forks with their upstream repositories.

**Default**: `true`

**Options**:
- `'true'` - Sync existing forks with upstream (keeps forks up-to-date)
- `'false'` - Skip existing forks (only create new forks)

**Example**:
```yaml
env:
  SYNC_EXISTING_FORKS: 'false'  # Disable auto-sync
```

**Use Cases**:
- **Enable sync** (`true`): Regular weekly runs to keep all forks updated
- **Disable sync** (`false`): One-time fork to create snapshots without future updates

### TARGET_ORG

The target organization where repositories will be forked.

**Default**: `walrus-haulout`

**Example**:
```yaml
env:
  TARGET_ORG: 'my-org'
```


## 📊 Features

### Intelligent Fork Management

The script includes smart fork management:
- **Pre-Check**: Verifies if fork already exists before attempting to create
- **Auto-Sync**: Automatically syncs existing forks with upstream repositories
- **Smart Skip**: Skips repositories that exist but aren't forks of the source
- **Categorized Actions**:
  - 🔄 **New Fork**: Creating a new fork
  - 📦 **Sync**: Updating existing fork from upstream
  - ⏭️ **Skip**: Repository exists but not applicable

### Intelligent Retry Logic

The script includes robust error handling:
- **Automatic Retries**: Up to 10 attempts per repository (increased for rate limiting)
- **Exponential Backoff**: 2s → 4s → 8s → 16s → 32s
- **Special Handling for "Submitted Too Quickly"**: 60-second wait + retry
- **Rate Limit Handling**: Respects `Retry-After` headers
- **Timeout Protection**: 30-second timeout per API call

### Error Handling

| Error Type | Status Code | Behavior |
|------------|-------------|----------|
| Success | 202 | Fork created successfully |
| Already Exists (Sync) | 200/409 | Synced or already up-to-date |
| Not Found | 404 | Repository private or doesn't exist |
| Submitted Too Quickly | 403 | Wait 60s and retry (up to 10 times) |
| Rate Limited | 403 | Wait and retry with backoff |
| Timeout | N/A | Retry up to 10 times |

### Polite API Usage

- **10-second delay** between each operation (increased from 5s)
- **Prevents rate limiting** with intelligent retry
- **Total time for 256 projects**: ~44 minutes (10s × 256 + retries)
- **Reduced API stress**: Pre-check avoids unnecessary fork attempts

## 📥 Output

### Workflow Logs

View detailed logs in the Actions tab:
```
Starting fork process to organization: walrus-haulout
Configuration:
  - Sync existing forks: ✓ Enabled
  - Delay between operations: 10 seconds
  - Max retries per fork: 10
Reading projects from: walrus_haulout_data.csv

Found 256 projects with GitHub URLs

[1/256] Processing N3xt-Ep0ch-L4bs/Backstage-app...
  🔄 Creating fork...
  ✓ Successfully forked N3xt-Ep0ch-L4bs/Backstage-app

[2/256] Processing preyam2002/Aletheia...
  📦 Fork exists, attempting to sync...
  ✓ Successfully synced walrus-haulout/Aletheia with preyam2002/Aletheia

[3/256] Processing anthonykimani/OpenTruth...
  📦 Fork exists, attempting to sync...
  ✓ Fork walrus-haulout/OpenTruth is already up to date

[159/256] Processing deranalabs/walrus-estate...
  🔄 Creating fork...
    ⚠️  Rate limited (submitted too quickly), waiting 60s... (attempt 1/10)
  ✓ Successfully forked deranalabs/walrus-estate
...

============================================================
Fork Summary:
  Total: 256
  Successful: 250
    - New forks: 180
    - Synced: 70
  Skipped: 4
  Failed: 2
  Report saved to: fork_report.json
============================================================
```

**With Sync Disabled** (`SYNC_EXISTING_FORKS: 'false'`):
```
[2/256] Processing preyam2002/Aletheia...
  ⏭️  Fork already exists (sync disabled)
```

### Fork Report Artifact

Download the `fork-report` artifact for detailed JSON report:

```json
{
  "total": 256,
  "successful": 250,
  "failed": 2,
  "skipped": 4,
  "synced": 70,
  "forked": 180,
  "results": [
    {
      "project_name": "Backstage",
      "github_url": "https://github.com/N3xt-Ep0ch-L4bs/Backstage-app",
      "owner": "N3xt-Ep0ch-L4bs",
      "repo": "Backstage-app",
      "action": "fork",
      "success": true,
      "message": "Successfully forked N3xt-Ep0ch-L4bs/Backstage-app"
    },
    {
      "project_name": "ALETHEIA",
      "github_url": "https://github.com/preyam2002/Aletheia",
      "owner": "preyam2002",
      "repo": "Aletheia",
      "action": "sync",
      "success": true,
      "message": "Successfully synced walrus-haulout/Aletheia with preyam2002/Aletheia"
    }
  ]
}
```

**Report Fields:**
- `action`: Type of operation (`fork`, `sync`, or `skip`)
- `success`: Whether the operation succeeded
- `message`: Detailed result message

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
- `check_fork_exists(owner, repo, target_org)` - Check if fork already exists in target org
- `sync_fork(owner, repo, target_org)` - Sync existing fork with upstream repository
- `fork_repository(owner, repo, target_org)` - Fork with intelligent retry logic
- `main()` - Orchestrates the entire forking process with pre-check and sync

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
