---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for new messages containing important keywords.
  Uses Playwright to automate WhatsApp Web and extract messages. Creates
  action files in Obsidian vault for Claude Code to process.
  WARNING: Respect WhatsApp Terms of Service when using this tool.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web for important messages and create actionable files.

## ⚠️ Important Notice

This tool uses WhatsApp Web automation. Be aware of:
- WhatsApp Terms of Service
- Rate limiting to avoid account restrictions
- Privacy considerations for message content

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time Setup

Run the watcher once to set up the browser session:

```bash
python scripts/whatsapp_watcher.py AI_Employee_Vault --setup
```

This will:
1. Open Chromium browser
2. Navigate to WhatsApp Web
3. You scan QR code with your phone
4. Session is saved for future use

## Usage

### Start WhatsApp Watcher

```bash
# Basic (check every 30 seconds)
python scripts/whatsapp_watcher.py AI_Employee_Vault

# Custom interval
python scripts/whatsapp_watcher.py AI_Employee_Vault --interval 60

# Custom keywords
python scripts/whatsapp_watcher.py AI_Employee_Vault --keywords "urgent,invoice,payment,help"

# Headless mode (no browser UI)
python scripts/whatsapp_watcher.py AI_Employee_Vault --headless
```

### Stop Watcher

Press `Ctrl+C` in the terminal.

## Configuration

### Session Storage

Browser session is stored in:
```
AI_Employee_Vault/.whatsapp_session/
```

**Never share this folder** - it contains your WhatsApp session.

### Keyword Filtering

Default keywords that trigger action files:
- urgent
- asap
- invoice
- payment
- help

Customize with `--keywords` flag.

## Output Format

Each important message creates a file in `Needs_Action/`:

```markdown
---
type: whatsapp_message
from: +1234567890
chat: John Doe
received: 2026-02-28T10:30:00
priority: high
status: pending
---

# WhatsApp Message

**From:** John Doe (+1234567890)
**Received:** 2026-02-28 10:30:00

## Message Content

Hey, can you send me the invoice for last month?

## Suggested Actions
- [ ] Reply to message
- [ ] Take required action
- [ ] Mark as processed
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code shows every time | Session not saving - check folder permissions |
| No messages detected | Ensure WhatsApp Web is loaded |
| Browser crashes | Try non-headless mode |
| Rate limited | Increase check interval |

## Security Notes

- Keep session folder private
- Don't commit session files to git
- Log out from WhatsApp Web when not in use
- Monitor for unusual account activity
