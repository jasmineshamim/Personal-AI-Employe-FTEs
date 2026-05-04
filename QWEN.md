# Personal AI Employee FTEs - Project Context

## Project Overview

This is a **hackathon blueprint project** for building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI employee powered by Claude Code and Obsidian. The project proposes a local-first approach to automation where an AI agent proactively manages personal and business affairs 24/7.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine and executor |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard and long-term memory |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |

### Key Concepts

- **Watcher Pattern:** Lightweight Python scripts monitor inputs and create `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop:** A Stop hook pattern that keeps Claude iterating until tasks are complete
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Business Handover:** Autonomous weekly audits generating "Monday Morning CEO Briefing"

## Directory Structure

```
Personal-AI-Employe-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint document
├── skills-lock.json          # Skill version tracking
├── .gitattributes            # Git text normalization
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/  # Browser automation skill
│           ├── SKILL.md               # Skill documentation
│           ├── references/
│           │   └── playwright-tools.md  # MCP tool reference
│           └── scripts/
│               ├── mcp-client.py      # Universal MCP client (HTTP/stdio)
│               ├── start-server.sh    # Start Playwright MCP server
│               ├── stop-server.sh     # Stop Playwright MCP server
│               └── verify.py          # Server health check
```

## Key Files

### 1. `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
The main blueprint document (1201 lines) containing:
- Architecture overview and tech stack
- Tiered hackathon deliverables (Bronze/Silver/Gold/Platinum)
- Watcher implementation templates (Gmail, WhatsApp, Filesystem)
- MCP server configuration examples
- Ralph Wiggum loop pattern documentation
- Business handover templates and CEO briefing format

### 2. `.qwen/skills/browsing-with-playwright/`
A Qwen skill for browser automation via Playwright MCP:
- **SKILL.md:** Server lifecycle management, quick reference, workflows
- **mcp-client.py:** Universal MCP client supporting HTTP and stdio transports
- **playwright-tools.md:** Complete tool reference (22 tools available)

### 3. `skills-lock.json`
Tracks installed skills and their versions for reproducibility.

## Usage

### For Hackathon Participants

1. **Read the blueprint:** Start with `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
2. **Choose your tier:** Bronze (8-12h), Silver (20-30h), Gold (40+h), or Platinum (60+h)
3. **Set up prerequisites:**
   - Claude Code subscription
   - Obsidian v1.10.6+
   - Python 3.13+
   - Node.js v24+
4. **Create Obsidian vault** with folders: `/Inbox`, `/Needs_Action`, `/Done`, `/Pending_Approval`
5. **Implement watchers** using provided templates
6. **Configure MCP servers** for external actions

### For Qwen Code Sessions

When working with this project:

1. **Browser Automation:** Use the `browsing-with-playwright` skill for web interactions
   ```bash
   # Start server
   bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
   
   # Verify
   python .qwen/skills/browsing-with-playwright/scripts/verify.py
   ```

2. **MCP Client Usage:**
   ```bash
   # List tools
   python mcp-client.py list -u http://localhost:8808
   
   # Call tool
   python mcp-client.py call -u http://localhost:8808 -t browser_navigate -p '{"url": "https://example.com"}'
   ```

3. **File-based Communication:** Follow the watcher pattern - write `.md` files to trigger AI actions

## Development Conventions

- **Local-first:** All data stored in local Markdown files (Obsidian vault)
- **File-based triggers:** Actions triggered by file creation/movement
- **Human approval:** Sensitive actions require explicit file-based approval
- **Audit logging:** All actions logged in Markdown for traceability

## Weekly Research Meetings

- **When:** Wednesdays at 10:00 PM
- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube:** https://www.youtube.com/@panaversity

## Related Documentation

- [Playwright Tools Reference](.qwen/skills/browsing-with-playwright/references/playwright-tools.md)
- [Skill Documentation](.qwen/skills/browsing-with-playwright/SKILL.md)
- [MCP Client Source](.qwen/skills/browsing-with-playwright/scripts/mcp-client.py)
