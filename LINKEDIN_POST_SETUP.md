# LinkedIn Post Skill - Quick Setup Guide

## Overview

This skill uses LinkedIn's **official API v2** for reliable automated posting.

---

## Step 1: Create LinkedIn Developer App (5 minutes)

1. **Go to:** https://www.linkedin.com/developers/
2. **Click:** "Create app"
3. **Fill in:**
   - App name: `AI Employee`
   - LinkedIn Page: Select any page (or create one)
   - Privacy Policy: `https://github.com/yourusername`
   - User Agreement: `https://github.com/yourusername`
4. **Click:** "Create app"

---

## Step 2: Get API Credentials (2 minutes)

1. **Click "Auth" tab** in your app dashboard
2. **Copy:**
   - Client ID
   - Client Secret (click "Show")
3. **Click "Edit"** on OAuth 2.0 Redirect URLs
4. **Add:** `http://localhost:8080`
5. **Click "Save"**

---

## Step 3: Enable Permission (1 minute)

1. **Click "Permissions" tab**
2. **Find:** "Share on LinkedIn" (`w_member_social`)
3. **Click:** "Request" or "Enable"
4. **Accept** the terms

---

## Step 4: Create Credentials File (1 minute)

Create `linkedin_api_credentials.json` in project root:

```json
{
  "client_id": "PASTE_YOUR_CLIENT_ID_HERE",
  "client_secret": "PASTE_YOUR_CLIENT_SECRET_HERE",
  "redirect_uri": "http://localhost:8080"
}
```

**Example:**
```json
{
  "client_id": "1234567890abcdef",
  "client_secret": "GOCSPX-abc123xyz",
  "redirect_uri": "http://localhost:8080"
}
```

**Save the file!**

---

## Step 5: Authenticate (2 minutes)

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employe-FTEs
python scripts\linkedin_post.py --auth
```

**What happens:**
1. Browser opens automatically
2. Sign in to LinkedIn (if needed)
3. Click **"Allow"** to authorize
4. Terminal captures the code
5. Token saved to `.linkedin_api_token.json`

**Token lasts 60 days!**

---

## Step 6: Auto Post! (Works 100%)

```bash
# Text post
python scripts\linkedin_post.py --post "Hello LinkedIn from my AI Employee! #AI #Automation"

# Share article
python scripts\linkedin_post.py --post "Great article!" --url https://example.com --title "Article Title"

# Check status
python scripts\linkedin_post.py --status
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `--auth` | Authenticate with LinkedIn |
| `--post "text"` | Post text content |
| `--post "text" --url URL` | Share article/link |
| `--post "text" --image path.jpg` | Post with image (text-only for now) |
| `--status` | Check authentication status |
| `--vault PATH` | Specify vault path |

---

## Troubleshooting

### "Credentials file not found"

Create `linkedin_api_credentials.json` in project root with your credentials.

### "Invalid JSON in credentials file"

Make sure the JSON is valid:
- No trailing commas
- All strings in quotes
- Use this validator: https://jsonlint.com/

### "Token expired"

```bash
python scripts\linkedin_post.py --auth
```

### "Permission denied"

1. Go to LinkedIn Developers → Your App → Permissions
2. Enable `w_member_social`
3. Wait 5 minutes

### "Port 8080 already in use"

Change redirect_uri in credentials:
```json
{
  "redirect_uri": "http://localhost:8081"
}
```

---

## Security Notes

- **Never commit** `linkedin_api_credentials.json` to git
- **Never share** Client Secret
- Add to `.gitignore`:
  ```
  linkedin_api_credentials.json
  .linkedin_api_token.json
  ```

---

## Integration Example

```python
# In your AI Employee orchestrator
import subprocess

def post_to_linkedin(content):
    subprocess.run([
        'python', 'scripts/linkedin_post.py',
        '--post', content
    ])

# Usage
post_to_linkedin("New product launch! #AI")
```

---

## API Limits

| Limit | Value |
|-------|-------|
| Posts per day | 50 |
| API calls per 15 min | 500 |
| Token validity | 60 days |

---

*LinkedIn Post Skill v1.0*
*For AI Employee Silver Tier*
