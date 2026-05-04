# AI Employee - Bronze Tier Implementation

A local-first autonomous AI employee system powered by Qwen Code and Obsidian.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r scripts/requirements.txt
```

### 2. Verify Setup

```bash
python scripts/verify.py AI_Employee_Vault
```

### 3. Start the File System Watcher

```bash
# Windows
scripts\start-watcher.bat

# Or manually
python scripts/filesystem_watcher.py AI_Employee_Vault
```

### 4. Test the Workflow

1. Drop a file in `AI_Employee_Vault/Inbox/`
2. The watcher creates an action file in `Needs_Action/`
3. Run the orchestrator to process with Qwen Code:

```bash
# Windows
scripts\run-orchestrator.bat --process

# Or manually
python scripts/orchestrator.py AI_Employee_Vault --process
```

---

## What is Bronze Tier?

Bronze Tier is the **minimum viable deliverable** for the AI Employee hackathon:

- **Estimated setup time:** 8-12 hours
- **Core features:**
  - Obsidian vault with Dashboard, Company Handbook, and Business Goals
  - File System Watcher that monitors for new files
  - Qwen Code integration for processing tasks
  - Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Employee                           │
│                     Bronze Tier                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User drops    │────▶│  File System    │────▶│  Creates .md    │
│   file in       │     │  Watcher        │     │  in Needs_      │
│   /Inbox        │     │  (Python)       │     │  Action         │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Move to /Done  │◀────│  Process &      │◀────│  Qwen Code      │
│  when complete  │     │  execute        │     │  reads & plans  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Directory Structure

```
Personal-AI-Employe-FTEs/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # Objectives and metrics
│   ├── Inbox/                   # Drop folder for new files
│   ├── Needs_Action/            # Pending action files
│   ├── Done/                    # Completed items
│   ├── Plans/                   # Multi-step task plans
│   ├── Pending_Approval/        # Awaiting human approval
│   ├── Approved/                # Approved actions
│   ├── Rejected/                # Rejected items
│   └── Logs/                    # Activity logs
├── scripts/
│   ├── base_watcher.py          # Abstract watcher class
│   ├── filesystem_watcher.py    # File system monitor
│   ├── orchestrator.py          # Master process
│   ├── verify.py                # Setup verification
│   ├── requirements.txt         # Python dependencies
│   ├── start-watcher.bat        # Windows startup script
│   └── run-orchestrator.bat     # Windows orchestrator script
└── BRONZE_README.md             # This file
```

---

## Core Components

### 1. File System Watcher (`filesystem_watcher.py`)

Monitors the `/Inbox` folder for new files and creates corresponding action files.

```bash
python scripts/filesystem_watcher.py AI_Employee_Vault
```

**Features:**
- Event-driven file detection
- Automatic action file creation
- Duplicate prevention
- Activity logging

### 2. Orchestrator (`orchestrator.py`)

Triggers Qwen Code to process pending items and updates the dashboard.

```bash
# Show status
python scripts/orchestrator.py AI_Employee_Vault --status

# Process pending items
python scripts/orchestrator.py AI_Employee_Vault --process

# Continuous mode (check every 60s)
python scripts/orchestrator.py AI_Employee_Vault --continuous
```

### 3. Dashboard (`Dashboard.md`)

Real-time summary of system status, pending tasks, and recent activity.

---

## Usage Examples

### Example 1: Process a Text File

1. Create a text file `AI_Employee_Vault/Inbox/task.txt`:
   ```
   Please summarize this document and create a action plan.
   ```

2. The watcher detects it and creates:
   `Needs_Action/FILE_20260228_120000_task.txt.md`

3. Run the orchestrator:
   ```bash
   python scripts/orchestrator.py AI_Employee_Vault --process
   ```

4. Qwen Code reads the file, creates a plan, and moves it to `/Done`

### Example 2: Drop a Request File

1. Copy the test file already in `Inbox/TEST_REQUEST_001.md`

2. Run the orchestrator to process it

3. Check `Done/` for the completed file

---

## Configuration

### Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to customize:
- Communication guidelines
- Payment approval thresholds
- Task prioritization rules
- Contact lists
- Service rates

### Business Goals

Edit `AI_Employee_Vault/Business_Goals.md` to set:
- Revenue targets
- Key metrics
- Active projects
- Subscription inventory

---

## Troubleshooting

### Watcher doesn't detect files

- Ensure the watcher is running: `python scripts/filesystem_watcher.py ...`
- Check that files are dropped in `/Inbox` (not `/Needs_Action`)
- Verify file permissions allow reading

### Qwen Code not found

Make sure Qwen Code is installed and in your PATH.

Verify installation:
```bash
qwen --version
```

### Orchestrator shows no pending items

- Check `Needs_Action/` folder for `.md` files
- Ensure the watcher created action files (check logs)

---

## Next Steps (Silver Tier)

After completing Bronze tier, consider adding:

1. **Gmail Watcher** - Monitor Gmail for new messages
2. **WhatsApp Watcher** - Monitor WhatsApp via Playwright
3. **MCP Server Integration** - Send emails, make payments
4. **Human-in-the-Loop** - Approval workflow for sensitive actions
5. **Scheduled Operations** - Cron-based daily briefings

---

## Security Notes

- **Never commit credentials** - Use environment variables
- **Review before approving** - Always check approval requests
- **Audit logs** - Check `Logs/` folder regularly
- **Rate limiting** - Don't process too many items too fast

---

## Hackathon Checklist

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md created
- [x] Business_Goals.md created
- [x] Basic folder structure (/Inbox, /Needs_Action, /Done)
- [x] One working Watcher script (File System)
- [x] Qwen Code integration via orchestrator
- [ ] Qwen Code successfully reading/writing to vault (requires Qwen installation)
- [ ] All AI functionality as Agent Skills (future enhancement)

---

## Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Obsidian Download](https://obsidian.md/download)
- [Watchdog Documentation](https://pypi.org/project/watchdog/)

---

## Weekly Research Meetings

- **When:** Wednesdays at 10:00 PM
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)

---

*AI Employee v0.1 - Bronze Tier*
*Built for the Personal AI Employee Hackathon 2026*
