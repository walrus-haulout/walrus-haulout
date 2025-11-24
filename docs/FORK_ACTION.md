# Fork Hackathon Projects

This GitHub Action automatically forks all projects listed in `walrus_haulout_data.csv` to the `walrus-haulout` organization.

## Setup

### 1. Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Walrus Haulout Fork Bot")
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `admin:org` (if forking to an organization you don't own)
5. Click "Generate token" and copy the token

### 2. Add Token to Repository Secrets

1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `FORK_TOKEN`
4. Value: Paste your GitHub token
5. Click "Add secret"

### 3. Prepare the CSV File

Make sure `walrus_haulout_data.csv` exists in the repository root with at least the following columns:
- `projectName` - Name of the project
- `github_url` - GitHub repository URL

Example:
```csv
projectName,github_url
Project A,https://github.com/user1/project-a
Project B,https://github.com/user2/project-b
```

## Usage

### Manual Trigger

1. Go to the "Actions" tab in your repository
2. Select "Fork Hackathon Projects" workflow
3. Click "Run workflow"
4. The workflow will fork all projects to `walrus-haulout` organization

### Automatic Schedule

The workflow runs automatically every Sunday at midnight UTC.

## Output

After the workflow completes:
1. Check the workflow logs for detailed fork status
2. Download the `fork-report` artifact to see a JSON report with:
   - Total projects processed
   - Successful forks
   - Failed forks (with error messages)

## Notes

- The script skips repositories that are already forked
- Private repositories will fail unless you have access
- Rate limiting: 2 seconds delay between each fork to respect GitHub API limits
- The workflow uses Python 3.9 and requires `requests` and `pandas` packages
