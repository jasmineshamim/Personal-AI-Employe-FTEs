# AI Employee - Silver Tier Implementation

A local-first autonomous AI employee system powered by Qwen Code and Obsidian.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## What is Silver Tier?

Silver Tier builds upon Bronze Tier with advanced automation capabilities:

- **Estimated setup time:** 20-30 hours
- **Core additions:**
  - Multiple Watcher scripts (Gmail + WhatsApp + File System)
  - LinkedIn auto-posting for business promotion
  - Plan.md generation for Claude reasoning
  - Human-in-the-loop approval workflow
  - Windows Task Scheduler integration

---

## Silver Tier Requirements Checklist

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | See BRONZE_README.md |
| 2 | 2+ Watcher scripts | ✅ | Gmail, WhatsApp, File System |
| 3 | LinkedIn auto-posting | ✅ | LinkedIn Poster skill |
| 4 | Plan.md generation | ✅ | Plan Generator |
| 5 | Human-in-the-loop approval | ✅ | Approval Manager |
| 6 | Scheduling | ✅ | Windows Task Scheduler |

---

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install -r scripts/requirements.txt

# Gmail Watcher (optional)
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# WhatsApp & LinkedIn (Playwright)
pip install playwright
playwright install chromium
```

### 2. Verify Setup

```bash
python scripts/verify.py AI_Employee_Vault
```

### 3. Start All Watchers

```bash
# File System Watcher
start scripts\filesystem_watcher.py AI_Employee_Vault

# Gmail Watcher (requires setup)
python scripts\gmail_watcher.py AI_Employee_Vault --authenticate
python scripts\gmail_watcher.py AI_Employee_Vault

# WhatsApp Watcher (requires setup)
python scripts\whatsapp_watcher.py AI_Employee_Vault --setup
python scripts\whatsapp_watcher.py AI_Employee_Vault
```

### 4. Install Scheduled Tasks

```bash
python scripts\task_scheduler.py AI_Employee_Vault --install
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Employee - Silver Tier                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Gmail Watch  │  │ WhatsApp     │  │ File System  │
│ (Gmail API)  │  │ (Playwright) │  │ (watchdog)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Needs_Action/     │
              │   (action files)    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Plan Generator    │
              │   (creates plans)   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Qwen Code         │
              │   (reasoning)       │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Pending     │ │   Done/     │ │  LinkedIn   │
│ Approval/   │ │ (completed) │ │   Poster    │
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

## Core Components

### 1. Gmail Watcher (`gmail_watcher.py`)

Monitors Gmail for important unread emails using Gmail API.

```bash
# First-time authentication
python scripts/gmail_watcher.py AI_Employee_Vault --authenticate

# Start watching
python scripts/gmail_watcher.py AI_Employee_Vault

# Custom keywords
python scripts/gmail_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment"
```

**Features:**
- OAuth 2.0 authentication
- Keyword filtering
- Priority detection
- Automatic action file creation

---

### 2. WhatsApp Watcher (`whatsapp_watcher.py`)

Monitors WhatsApp Web for messages containing important keywords.

```bash
# First-time setup (scan QR code)
python scripts/whatsapp_watcher.py AI_Employee_Vault --setup

# Start watching
python scripts/whatsapp_watcher.py AI_Employee_Vault

# Headless mode
python scripts/whatsapp_watcher.py AI_Employee_Vault --headless
```

**⚠️ Warning:** Respect WhatsApp Terms of Service.

**Features:**
- QR code authentication
- Session persistence
- Keyword detection
- Priority flagging

---

### 3. LinkedIn Poster (`linkedin_poster.py`)

Automates LinkedIn posting for business promotion.

```bash
# First-time login
python scripts/linkedin_poster.py AI_Employee_Vault --login

# Create draft post (requires approval)
python scripts/linkedin_poster.py AI_Employee_Vault --create "Excited to announce our new AI service!"

# Post directly
python scripts/linkedin_poster.py AI_Employee_Vault --post "Your post content"

# Process inbox for scheduled posts
python scripts/linkedin_poster.py AI_Employee_Vault --process-inbox
```

**Features:**
- Draft mode with approval
- Direct posting
- Image support
- Post logging

---

### 4. Plan Generator (`plan_generator.py`)

Creates structured Plan.md files for multi-step tasks.

```bash
# Generate plans for all pending items
python scripts/plan_generator.py AI_Employee_Vault --generate-all

# Create custom plan
python scripts/plan_generator.py AI_Employee_Vault --task "Process client invoice" --objective "Generate and send invoice"
```

**Features:**
- Automatic plan generation from action files
- Task-type specific templates
- Priority handling
- Execution logging

---

### 5. Approval Manager (`approval_manager.py`)

Manages human-in-the-loop approval workflow.

```bash
# Check pending approvals
python scripts/approval_manager.py AI_Employee_Vault --status

# Approve a file
python scripts/approval_manager.py AI_Employee_Vault --approve FILENAME.md

# Reject a file
python scripts/approval_manager.py AI_Employee_Vault --reject FILENAME.md --reason "Not approved"

# Watch for approvals
python scripts/approval_manager.py AI_Employee_Vault --watch
```

**Features:**
- Pending approval tracking
- Approval/rejection with reasons
- Audit logging
- Continuous monitoring

---

### 6. Task Scheduler (`task_scheduler.py`)

Windows Task Scheduler integration for automated operations.

```bash
# Install all scheduled tasks
python scripts\task_scheduler.py AI_Employee_Vault --install

# List scheduled tasks
python scripts\task_scheduler.py AI_Employee_Vault --list

# Remove scheduled tasks
python scripts\task_scheduler.py AI_Employee_Vault --uninstall

# Run daily briefing manually
python scripts\task_scheduler.py AI_Employee_Vault --run-daily-briefing
```

**Scheduled Tasks:**
| Task | Schedule | Purpose |
|------|----------|---------|
| Daily Briefing | 8:00 AM daily | Process pending items |
| Health Check | Every hour | Monitor system status |
| Weekly Audit | Monday 7:00 AM | Generate weekly report |

---

## Workflow Examples

### Example 1: Email → Plan → Action → Approval

1. Gmail Watcher detects important email
2. Creates action file in `Needs_Action/`
3. Plan Generator creates plan in `Plans/`
4. Qwen Code processes the plan
5. If approval needed, file goes to `Pending_Approval/`
6. Human approves via Approval Manager
7. Action executed, file moved to `Done/`

### Example 2: LinkedIn Post with Approval

1. Create draft post:
   ```bash
   python scripts/linkedin_poster.py AI_Employee_Vault --create "New service launch!"
   ```

2. Review draft in `Pending_Approval/`

3. Approve:
   ```bash
   python scripts/approval_manager.py AI_Employee_Vault --approve LINKEDIN_DRAFT_*.md
   ```

4. Post is published to LinkedIn

### Example 3: Scheduled Daily Briefing

1. Task Scheduler runs at 8:00 AM
2. Orchestrator processes all pending items
3. Plans generated for new tasks
4. Dashboard updated with status
5. Briefing logged in `Briefings/`

---

## Configuration

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project, enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` to project root
5. Authenticate:
   ```bash
   python scripts/gmail_watcher.py AI_Employee_Vault --authenticate
   ```

### WhatsApp Session Setup

```bash
python scripts/whatsapp_watcher.py AI_Employee_Vault --setup
```

Scan QR code with your phone. Session saved to `.whatsapp_session/`.

### LinkedIn Session Setup

```bash
python scripts/linkedin_poster.py AI_Employee_Vault --login
```

Log in to LinkedIn. Session saved to `.linkedin_session/`.

---

## Directory Structure (Silver Tier)

```
Personal-AI-Employe-FTEs/
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Plans/              # NEW: Multi-step task plans
│   ├── Pending_Approval/   # NEW: Awaiting human approval
│   ├── Approved/           # NEW: Approved actions
│   ├── Rejected/           # NEW: Rejected items
│   ├── Logs/
│   ├── Briefings/          # NEW: Daily/weekly briefings
│   ├── .whatsapp_session/  # WhatsApp session (private)
│   └── .linkedin_session/  # LinkedIn session (private)
├── scripts/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py         # NEW
│   ├── whatsapp_watcher.py      # NEW
│   ├── linkedin_poster.py       # NEW
│   ├── orchestrator.py
│   ├── plan_generator.py        # NEW
│   ├── approval_manager.py      # NEW
│   ├── task_scheduler.py        # NEW
│   ├── verify.py
│   └── requirements.txt
├── credentials.json              # Gmail OAuth (private)
├── token.json                    # Gmail token (private)
└── SILVER_README.md              # This file
```

---

## Troubleshooting

### Gmail Watcher Issues

| Issue | Solution |
|-------|----------|
| Authentication failed | Delete `token.json`, re-authenticate |
| No emails detected | Check Gmail API quota |
| Duplicate emails | Clear `processed_ids` cache |

### WhatsApp Watcher Issues

| Issue | Solution |
|-------|----------|
| QR code every time | Check session folder permissions |
| No messages detected | Ensure WhatsApp Web loaded |
| Browser crashes | Try without `--headless` |

### LinkedIn Poster Issues

| Issue | Solution |
|-------|----------|
| Login required | Re-run `--login` |
| Post fails | LinkedIn selectors may have changed |
| Rate limited | Reduce posting frequency |

### Approval Manager Issues

| Issue | Solution |
|-------|----------|
| File not found | Check filename spelling |
| Can't approve | Ensure file is in `Pending_Approval/` |

### Task Scheduler Issues

| Issue | Solution |
|-------|----------|
| Task not running | Check Task Scheduler library |
| Permission denied | Run as Administrator |
| Python not found | Use full path to python.exe |

---

## Security Notes

- **Never commit** `credentials.json`, `token.json`, `.whatsapp_session/`, `.linkedin_session/`
- Add to `.gitignore`:
  ```
  credentials.json
  token.json
  *.whatsapp_session/
  *.linkedin_session/
  ```
- Review API permissions regularly
- Rotate credentials monthly
- Monitor logs for unusual activity

---

## Hackathon Checklist (Silver Tier)

- [x] All Bronze requirements complete
- [x] Gmail Watcher implemented
- [x] WhatsApp Watcher implemented
- [x] LinkedIn Poster implemented
- [x] Plan.md generator working
- [x] Approval workflow functional
- [x] Task Scheduler integration
- [ ] All watchers running simultaneously
- [ ] Demo video created
- [ ] Documentation complete

---

## Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Bronze Tier README](./BRONZE_README.md)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Playwright Docs](https://playwright.dev/python/)
- [Obsidian](https://obsidian.md/)

---

## Weekly Research Meetings

- **When:** Wednesdays at 10:00 PM
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)

---

*AI Employee v0.2 - Silver Tier*
*Built for the Personal AI Employee Hackathon 2026*
