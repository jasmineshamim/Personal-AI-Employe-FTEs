---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files in Obsidian vault.
  Uses Gmail API to fetch unread emails and converts them into markdown files for
  Claude Code to process. Supports keyword filtering and priority detection.
---

# Gmail Watcher Skill

Monitor Gmail inbox and create actionable files for new emails.

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. First-Time Authentication

```bash
python scripts/gmail_watcher.py AI_Employee_Vault --authenticate
```

This will open a browser window for OAuth authentication and create `token.json`.

## Usage

### Start Gmail Watcher

```bash
# Basic (check every 2 minutes)
python scripts/gmail_watcher.py AI_Employee_Vault

# Custom interval (check every 30 seconds)
python scripts/gmail_watcher.py AI_Employee_Vault --interval 30

# With keyword filtering
python scripts/gmail_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment"
```

### Stop Watcher

Press `Ctrl+C` in the terminal.

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Gmail API credentials
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json

# Watcher settings
GMAIL_CHECK_INTERVAL=120
GMAIL_KEYWORDS=urgent,asap,invoice,payment,help
```

### Keyword Filtering

By default, the watcher flags emails containing:
- urgent
- asap
- invoice
- payment
- help

Customize with `--keywords` flag or `GMAIL_KEYWORDS` env variable.

## Output Format

Each email creates a file in `Needs_Action/`:

```markdown
---
type: email
from: client@example.com
subject: Invoice Request
received: 2026-02-28T10:30:00
priority: high
status: pending
---

# Email Content

[Email body text...]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Delete `token.json` and re-authenticate |
| No emails detected | Check Gmail API quota, verify label filters |
| Duplicate emails | Ensure `processed_ids` is being saved |

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- Store credentials in secure location
- Use app-specific passwords if 2FA enabled
- Review Gmail API permissions regularly
