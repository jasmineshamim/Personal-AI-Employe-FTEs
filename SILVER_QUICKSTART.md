# Silver Tier - Quick Start Guide

## Overview

Silver Tier adds the following capabilities to your AI Employee:

| Feature | Description | Status |
|---------|-------------|--------|
| Gmail Watcher | Monitor Gmail for important emails | ✅ Ready |
| LinkedIn Poster | Auto-post to LinkedIn for business | ✅ Ready |
| Plan Generator | Create structured plans for tasks | ✅ Ready |
| Approval Manager | Human-in-the-loop workflow | ✅ Ready |
| Task Scheduler | Windows scheduled tasks | ✅ Ready |

---

## Quick Setup (15 minutes)

### Step 1: Verify Installation

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employe-FTEs
python scripts\verify.py AI_Employee_Vault
```

Expected output: All Silver Tier scripts should show [OK].

### Step 2: Set Up Gmail Watcher

You already have `credentials.json` in the project root.

**Authenticate with Gmail:**

```bash
python scripts\gmail_watcher.py AI_Employee_Vault --authenticate
```

**What happens:**
1. A URL will be displayed
2. Open the URL in your browser
3. Sign in with your Google account
4. Grant permissions
5. The browser will redirect to localhost (this is normal)
6. `token.json` will be created automatically

**Start Gmail Watcher:**

```bash
python scripts\gmail_watcher.py AI_Employee_Vault
```

**Keep this running in a separate terminal window.**

---

### Step 3: Set Up LinkedIn Poster

**Login to LinkedIn:**

```bash
python scripts\linkedin_poster.py AI_Employee_Vault --login
```

**What happens:**
1. Browser opens with LinkedIn
2. Log in to your account
3. Wait for your feed to load
4. Close the browser
5. Session saved to `.linkedin_session/`

**Test posting (create draft):**

```bash
python scripts\linkedin_poster.py AI_Employee_Vault --create "Testing my AI Employee Silver Tier! #AI #Automation"
```

**Approve the draft:**

```bash
# View pending drafts
python scripts\approval_manager.py AI_Employee_Vault --status

# Approve (replace FILENAME with actual file)
python scripts\approval_manager.py AI_Employee_Vault --approve LINKEDIN_DRAFT_*.md
```

---

### Step 4: Install Scheduled Tasks

```bash
python scripts\task_scheduler.py AI_Employee_Vault --install
```

This creates:
- **Daily Briefing** - 8:00 AM every day
- **Health Check** - Every hour
- **Weekly Audit** - Monday at 7:00 AM

---

## Daily Workflow

### Morning (8:00 AM)

Task Scheduler automatically runs the daily briefing:

```bash
# Or run manually
python scripts\orchestrator.py AI_Employee_Vault --process
```

### During the Day

1. **Gmail Watcher** runs continuously, detecting important emails
2. **File System Watcher** monitors the Inbox folder
3. New items create action files in `Needs_Action/`
4. Plans are generated automatically

### Evening

1. Check `Dashboard.md` for status
2. Review `Pending_Approval/` for items needing your action
3. Approve or reject items

---

## Commands Reference

### Gmail Watcher

```bash
# Authenticate (first time only)
python scripts\gmail_watcher.py AI_Employee_Vault --authenticate

# Start watching
python scripts\gmail_watcher.py AI_Employee_Vault

# Custom interval (30 seconds)
python scripts\gmail_watcher.py AI_Employee_Vault --interval 30

# Custom keywords
python scripts\gmail_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment"
```

### LinkedIn Poster

```bash
# Login (first time only)
python scripts\linkedin_poster.py AI_Employee_Vault --login

# Create draft post
python scripts\linkedin_poster.py AI_Employee_Vault --create "Your post content"

# Post directly
python scripts\linkedin_poster.py AI_Employee_Vault --post "Your post content"

# Process inbox for scheduled posts
python scripts\linkedin_poster.py AI_Employee_Vault --process-inbox
```

### Orchestrator

```bash
# Show status
python scripts\orchestrator.py AI_Employee_Vault --status

# Process pending items
python scripts\orchestrator.py AI_Employee_Vault --process

# Generate plans only
python scripts\orchestrator.py AI_Employee_Vault --generate-plans

# Continuous mode
python scripts\orchestrator.py AI_Employee_Vault --continuous --interval 60
```

### Approval Manager

```bash
# Check pending approvals
python scripts\approval_manager.py AI_Employee_Vault --status

# Approve a file
python scripts\approval_manager.py AI_Employee_Vault --approve FILENAME.md

# Reject a file
python scripts\approval_manager.py AI_Employee_Vault --reject FILENAME.md --reason "Not approved"

# Watch for approvals
python scripts\approval_manager.py AI_Employee_Vault --watch
```

### Task Scheduler

```bash
# Install all tasks
python scripts\task_scheduler.py AI_Employee_Vault --install

# List tasks
python scripts\task_scheduler.py AI_Employee_Vault --list

# Remove tasks
python scripts\task_scheduler.py AI_Employee_Vault --uninstall

# Run daily briefing manually
python scripts\task_scheduler.py AI_Employee_Vault --run-daily-briefing
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Silver Tier Architecture                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Gmail        │  │ LinkedIn     │  │ File System  │
│ Watcher      │  │ Poster       │  │ Watcher      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Needs_Action/     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Plan Generator    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Qwen Code         │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Pending     │ │   Done/     │ │  LinkedIn   │
│ Approval/   │ │             │ │   Posted    │
│ (HITL)      │ │             │ │             │
└──────┬──────┘ └─────────────┘ └─────────────┘
       │
       ▼
┌─────────────┐
│ Approved/   │
│ (executed)  │
└─────────────┘
```

---

## Troubleshooting

### Gmail Watcher Issues

**Problem:** Authentication fails

```bash
# Delete token and re-authenticate
del token.json
python scripts\gmail_watcher.py AI_Employee_Vault --authenticate
```

**Problem:** No emails detected

- Check Gmail API quota in Google Cloud Console
- Verify credentials.json is correct
- Check watcher.log for errors

### LinkedIn Poster Issues

**Problem:** Login required every time

```bash
# Check session folder exists
dir AI_Employee_Vault\.linkedin_session

# Re-login
python scripts\linkedin_poster.py AI_Employee_Vault --login
```

**Problem:** Post fails

- LinkedIn selectors may have changed
- Try non-headless mode for debugging
- Check browser console for errors

### General Issues

**Problem:** Qwen Code not found

```bash
# Verify installation
qwen --version

# Use full path
python scripts\orchestrator.py AI_Employee_Vault --process --qwen "C:\Users\Dell\AppData\Roaming\npm\qwen.cmd"
```

---

## Security Checklist

- [ ] `credentials.json` - Keep private, never commit to git
- [ ] `token.json` - Contains OAuth token, keep private
- [ ] `.linkedin_session/` - Contains LinkedIn session, keep private
- [ ] `.whatsapp_session/` - Contains WhatsApp session, keep private
- [ ] Add to `.gitignore`:
  ```
  credentials.json
  token.json
  *.linkedin_session/
  *.whatsapp_session/
  ```

---

## Next Steps (Gold Tier)

After mastering Silver Tier, consider:

1. **WhatsApp Watcher** - Monitor WhatsApp Web messages
2. **MCP Email Server** - Send emails via MCP
3. **Odoo Integration** - Accounting system integration
4. **Weekly CEO Briefing** - Autonomous business audits
5. **Ralph Wiggum Loop** - Persistent multi-step task completion

---

## Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Bronze Tier README](./BRONZE_README.md)
- [Silver Tier README](./SILVER_README.md)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Playwright Docs](https://playwright.dev/python/)

---

*AI Employee v0.2 - Silver Tier*
*Built for the Personal AI Employee Hackathon 2026*
