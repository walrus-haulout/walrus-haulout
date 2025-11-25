# Changelog

All notable changes to the Walrus Haulout project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed - 2025-11-25

- **Simplified Fork Automation**: Removed `fork-repos-via-hub-mirror.yml` workflow in favor of the more reliable `fork-projects.yml` implementation
  - Removed: `.github/workflows/fork-repos-via-hub-mirror.yml`
  - Removed: `scripts/generate_repo_matrix.py`
  - The `fork-projects.yml` workflow has proven to be more stable and easier to maintain

### Improved - 2025-11-25

- **Enhanced Documentation**: Significantly improved `docs/FORK_ACTION.md` with:
  - Detailed setup instructions with exact token permission requirements
  - Comprehensive troubleshooting guide
  - Step-by-step manual trigger instructions
  - Implementation details and architecture overview
  - Best practices and common issues
  - Example outputs and error handling information

### Technical Details

**Why the change?**
- `fork-projects.yml` uses direct GitHub API calls via Python's `requests` library
- More transparent error handling with detailed JSON reports
- Simpler configuration (no need for hub-mirror-action complexity)
- Built-in retry logic with exponential backoff
- Easier to debug and maintain

**Fork Automation Features:**
- ✅ Automatic retry with exponential backoff (up to 5 attempts)
- ✅ Rate limit handling with `Retry-After` header respect
- ✅ Detailed fork report artifact (30-day retention)
- ✅ Skips already-forked repositories
- ✅ 5-second polite delay between requests
- ✅ ~21 minutes total time for 256 projects

---

## Previous Changes

For historical changes, please refer to the Git commit history.
