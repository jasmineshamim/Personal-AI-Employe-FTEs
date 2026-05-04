# LinkedIn API Auto Poster - Setup Guide

## Overview

This uses LinkedIn's **official API** for reliable automated posting (no browser automation).

---

## Step 1: Create LinkedIn Developer App

1. Go to **https://www.linkedin.com/developers/**
2. Click **"Create app"** (sign in if needed)
3. Fill in app details:
   - **App name:** AI Employee (or your choice)
   - **LinkedIn Page:** Select or create a page
   - **Privacy Policy:** Can use your website or GitHub profile
   - **User Agreement:** Can use your website or GitHub profile
4. Click **"Create app"**

---

## Step 2: Get API Credentials

1. In your app dashboard, click **"Auth"** tab
2. Copy these values:
   - **Client ID**
   - **Client Secret**
3. Click **"Edit"** next to OAuth 2.0 Redirect URLs
4. Add: `http://localhost:8080`
5. Click **"Save"**

---

## Step 3: Enable Posting Permission

1. In app dashboard, click **"Permissions"** tab
2. Find **"Share on LinkedIn"** (`w_member_social`)
3. Click **"Request"** or **"Enable"**
4. Accept the terms

**Note:** This permission is auto-approved for most accounts.

---

## Step 4: Create Credentials File

1. Copy the template:
   ```bash
   copy linkedin_api_credentials_template.json linkedin_api_credentials.json
   ```

2. Edit `linkedin_api_credentials.json`:
   ```json
   {
     "client_id": "paste_your_client_id_here",
     "client_secret": "paste_your_client_secret_here",
     "redirect_uri": "http://localhost:8080"
   }
   ```

3. **Save the file** (never commit to git!)

---

## Step 5: Authenticate

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employe-FTEs
python scripts\linkedin_api_poster.py AI_Employee_Vault --auth
```

**What happens:**
1. Browser opens automatically
2. Click "Allow" to authorize your app
3. Authorization code is captured
4. Access token is saved

**Token lasts 60 days** - then re-run authentication.

---

## Step 6: Auto Post!

```bash
# Text-only post
python scripts\linkedin_api_poster.py AI_Employee_Vault --autopost "Hello LinkedIn! This post was created by my AI Employee! #AI #Automation"

# Check status
python scripts\linkedin_api_poster.py AI_Employee_Vault --status
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `--auth` | Authenticate with LinkedIn |
| `--autopost "text"` | Auto post content |
| `--status` | Check authentication status |

---

## Troubleshooting

### "Permission denied" or "Insufficient permissions"

- Make sure `w_member_social` permission is enabled
- Go to LinkedIn Developers → Your App → Permissions

### "Invalid client_id"

- Check your `linkedin_api_credentials.json` file
- Make sure Client ID is copied correctly (no spaces)

### "Token expired"

```bash
# Re-authenticate
python scripts\linkedin_api_poster.py AI_Employee_Vault --auth
```

### "Port 8080 already in use"

- Close any other apps using port 8080
- Or edit `redirect_uri` in credentials to use different port (e.g., 8081)

---

## Security Notes

- **Never commit** `linkedin_api_credentials.json` to git
- **Never share** your Client Secret
- Add to `.gitignore`:
  ```
  linkedin_api_credentials.json
  .linkedin_api_token.json
  ```

---

## Integration with AI Employee

Add to your orchestrator workflow:

```bash
# After AI processes email and decides to post
python scripts\linkedin_api_poster.py AI_Employee_Vault --autopost "Generated content"
```

---

## API Limits

- **50 posts per day** per user
- **Rate limit:** 500 requests per 15 minutes
- More than enough for AI Employee use!

---

*LinkedIn API Auto Poster v1.0*
*For AI Employee Silver Tier*
