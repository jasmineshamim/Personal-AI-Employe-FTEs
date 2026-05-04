# AI Employee - Gold Tier Implementation

A comprehensive autonomous AI employee system with full business integration including Odoo ERP, Facebook, Instagram, and Twitter/X.

**Tagline:** *Your complete business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## What is Gold Tier?

Gold Tier represents a fully autonomous AI employee with complete business integration:

- **Estimated setup time:** 40+ hours
- **Core additions:**
  - Full cross-domain integration (Personal + Business)
  - Odoo ERP integration (self-hosted via Docker)
  - Facebook & Instagram integration
  - Twitter/X integration
  - Multiple MCP servers for different action types
  - Weekly Business and Accounting Audit with CEO Briefing
  - Error recovery and graceful degradation
  - Comprehensive audit logging
  - Ralph Wiggum loop for autonomous multi-step task completion

---

## Gold Tier Requirements Checklist

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Silver requirements | ✅ | See SILVER_README.md |
| 2 | Full cross-domain integration | ✅ | Personal + Business |
| 3 | Odoo ERP integration | ✅ | Docker Compose + MCP |
| 4 | Facebook & Instagram integration | ✅ | Facebook MCP + Watcher |
| 5 | Twitter/X integration | ✅ | Twitter MCP + Watcher |
| 6 | Multiple MCP servers | ✅ | Email, Social, Odoo, Browser |
| 7 | Weekly Business Audit | ✅ | CEO Briefing generator |
| 8 | Error recovery | ✅ | Retry handlers + fallbacks |
| 9 | Audit logging | ✅ | Comprehensive logging |
| 10 | Ralph Wiggum loop | ✅ | Autonomous task completion |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Employee - Gold Tier                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SOURCES                           │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────┤
│  Gmail   │ WhatsApp │ Facebook │ Instagram│ Twitter  │  Odoo  │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (Watchers)                  │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │ Gmail  │ │ WhatsApp │ │ Facebook │ │ Twitter  │ │ Odoo   │  │
│  │ Watcher│ │ Watcher  │ │ Watcher  │ │ Watcher  │ │ Watcher│  │
│  └───┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘  │
└──────┼──────────┼────────────┼────────────┼────────────┼───────┘
       │          │            │            │            │
       └──────────┴────────────┴────────────┴────────────┘
                                │
                                ▼
              ┌─────────────────────────────────┐
              │      OBSIDIAN VAULT (Local)     │
              │  ┌───────────────────────────┐  │
              │  │ /Needs_Action/            │  │
              │  │ /Plans/                   │  │
              │  │ /Pending_Approval/        │  │
              │  │ /Approved/                │  │
              │  │ /Done/                    │  │
              │  │ /Logs/                    │  │
              │  │ /Briefings/               │  │
              │  │ /Accounting/              │  │
              │  │ Dashboard.md              │  │
              │  │ Business_Goals.md         │  │
              │  │ Company_Handbook.md       │  │
              │  └───────────────────────────┘  │
              └──────────────┬──────────────────┘
                             │
                             ▼
              ┌─────────────────────────────────┐
              │         REASONING LAYER         │
              │         CLAUDE CODE             │
              │  Read → Think → Plan → Execute  │
              └──────────────┬──────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  HUMAN-IN-THE-  │ │  ACTION LAYER   │ │  AUDIT LAYER    │
│  LOOP (HITL)    │ │  (MCP Servers)  │ │  (Logging)      │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
│ │ Pending     │ │ │ │ Email MCP   │ │ │ │ Audit Log   │ │
│ │ Approval    │ │ │ │ Social MCP  │ │ │ │ Generator   │ │
│ │ Review      │ │ │ │ Odoo MCP    │ │ │ │ Error Track │ │
│ └─────────────┘ │ │ │ Browser MCP │ │ │ └─────────────┘ │
└─────────────────┘ │ └─────────────┘ │ └─────────────────┘
                    └─────────────────┘
```

---

## Quick Start

### Prerequisites

Ensure you have completed Silver Tier setup and have:

- Docker Desktop installed and running
- Python 3.13+ with all Silver dependencies
- Node.js v24+
- Claude Code subscription
- Obsidian v1.10.6+

### 1. Install Gold Tier Dependencies

```bash
# Navigate to project root
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employe-FTEs

# Install Python dependencies
pip install -r scripts\requirements.txt

# Install additional Gold tier dependencies
pip install facebook-business tweepy xmltodict

# Install Playwright browsers (if not already done)
playwright install chromium
```

### 2. Set Up Odoo ERP (Docker)

```bash
# Start Odoo container
cd odoo
docker-compose up -d

# Wait for Odoo to initialize (2-3 minutes)
docker-compose logs -f

# Access Odoo at http://localhost:8069
# Default credentials: admin / admin
```

### 3. Configure Social Media Credentials

Create `.env` file in project root:

```bash
# Facebook App Credentials
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id

# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Odoo Credentials
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 4. Initialize Gold Tier Components

```bash
# Verify Odoo connection
python scripts\odoo_test.py AI_Employee_Vault

# Set up Facebook (first time)
python scripts\facebook_watcher.py AI_Employee_Vault --setup

# Set up Twitter (first time)
python scripts\twitter_watcher.py AI_Employee_Vault --setup

# Run verification
python scripts\verify_gold.py AI_Employee_Vault
```

### 5. Start All Watchers

```bash
# Start all watchers in background
start scripts\start-gold-watchers.bat

# Or start individually:
start scripts\filesystem_watcher.py AI_Employee_Vault
start scripts\gmail_watcher.py AI_Employee_Vault
start scripts\whatsapp_watcher.py AI_Employee_Vault
start scripts\facebook_watcher.py AI_Employee_Vault
start scripts\twitter_watcher.py AI_Employee_Vault
start scripts\odoo_watcher.py AI_Employee_Vault
```

### 6. Install Scheduled Tasks

```bash
# Install all scheduled tasks (Gold tier)
python scripts\task_scheduler.py AI_Employee_Vault --install-gold

# Verify tasks
python scripts\task_scheduler.py AI_Employee_Vault --list
```

---

## Core Components

### 1. Odoo ERP Integration

#### Docker Compose Setup

Odoo runs in Docker for local deployment:

```yaml
# odoo/docker-compose.yml
version: '3.8'
services:
  odoo:
    image: odoo:19.0
    container_name: ai_employee_odoo
    ports:
      - "8069:8069"
    environment:
      - ODOO_DB_NAME=odoo
      - ODOO_DB_USER=odoo
      - ODOO_DB_PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./odoo-custom-addons:/mnt/extra-addons
    depends_on:
      - db
  
  db:
    image: postgres:15
    container_name: ai_employee_odoo_db
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

#### Odoo MCP Server

The Odoo MCP server provides these capabilities:

- **Create Invoice**: Generate customer invoices
- **Record Payment**: Log payments against invoices
- **Create Contact**: Add new customers/vendors
- **List Invoices**: Retrieve invoice status
- **Generate Report**: Create accounting reports
- **Check Balance**: Get account balances

```bash
# Test Odoo connection
python scripts\odoo_test.py AI_Employee_Vault

# Create invoice via MCP
python scripts\mcp_odoo_server.py --create-invoice --customer "Client A" --amount 1500

# List pending invoices
python scripts\mcp_odoo_server.py --list-invoices --status draft
```

#### Odoo Watcher

Monitors Odoo for business events:

```bash
# Start Odoo watcher
python scripts\odoo_watcher.py AI_Employee_Vault

# Check for new invoices
python scripts\odoo_watcher.py AI_Employee_Vault --check-invoices

# Check for payments
python scripts\odoo_watcher.py AI_Employee_Vault --check-payments
```

### 2. Facebook & Instagram Integration

#### Facebook MCP Server

Capabilities:

- **Create Post**: Publish to Facebook Page
- **Create Story**: Post Instagram Story
- **Get Insights**: Retrieve page analytics
- **List Messages**: Get page messages
- **Send Message**: Reply to messages
- **Schedule Post**: Queue posts for later

```bash
# Create Facebook post
python scripts\facebook_poster.py AI_Employee_Vault --post "Your content"

# Create Instagram story
python scripts\facebook_poster.py AI_Employee_Vault --story --image path/to/image.jpg

# Get page insights
python scripts\facebook_poster.py AI_Employee_Vault --insights

# Process messages
python scripts\facebook_poster.py AI_Employee_Vault --process-messages
```

#### Facebook Watcher

Monitors Facebook/Instagram for engagement:

```bash
# Start Facebook watcher
python scripts\facebook_watcher.py AI_Employee_Vault

# Check for new messages
python scripts\facebook_watcher.py AI_Employee_Vault --check-messages

# Check for comments
python scripts\facebook_watcher.py AI_Employee_Vault --check-comments
```

### 3. Twitter/X Integration

#### Twitter MCP Server

Capabilities:

- **Create Tweet**: Post tweets
- **Create Thread**: Post tweet threads
- **Get Mentions**: Retrieve mentions
- **Reply to Tweet**: Respond to mentions
- **Get Analytics**: Retrieve tweet performance
- **Schedule Tweet**: Queue tweets

```bash
# Create tweet
python scripts\twitter_poster.py AI_Employee_Vault --tweet "Your content"

# Create thread
python scripts\twitter_poster.py AI_Employee_Vault --thread "First tweet" "Second tweet" "Third tweet"

# Process mentions
python scripts\twitter_poster.py AI_Employee_Vault --process-mentions

# Get analytics
python scripts\twitter_poster.py AI_Employee_Vault --analytics
```

#### Twitter Watcher

Monitors Twitter for mentions and engagement:

```bash
# Start Twitter watcher
python scripts\twitter_watcher.py AI_Employee_Vault

# Check for mentions
python scripts\twitter_watcher.py AI_Employee_Vault --check-mentions

# Check for DMs
python scripts\twitter_watcher.py AI_Employee_Vault --check-dms
```

### 4. Weekly Business Audit

The CEO Briefing generator creates comprehensive weekly reports:

```bash
# Generate weekly briefing
python scripts\ceo_briefing_generator.py AI_Employee_Vault

# Generate custom period briefing
python scripts\ceo_briefing_generator.py AI_Employee_Vault --start 2026-01-01 --end 2026-01-07

# Generate specific audit
python scripts\ceo_briefing_generator.py AI_Employee_Vault --audit subscriptions
```

**Briefing includes:**

- Revenue summary (from Odoo)
- Expense analysis
- Subscription audit
- Task completion rate
- Response time metrics
- Bottleneck identification
- Proactive suggestions

### 5. Ralph Wiggum Loop

Autonomous multi-step task completion:

```bash
# Start Ralph loop for task
python scripts\ralph_loop.py AI_Employee_Vault "Process all pending invoices"

# With completion promise
python scripts\ralph_loop.py AI_Employee_Vault "Complete task" --promise "TASK_COMPLETE"

# With max iterations
python scripts\ralph_loop.py AI_Employee_Vault "Complete task" --max-iterations 10
```

### 6. Audit Logging System

Comprehensive logging of all actions:

```bash
# View today's logs
python scripts\audit_viewer.py AI_Employee_Vault --today

# View logs by date
python scripts\audit_viewer.py AI_Employee_Vault --date 2026-01-07

# Export logs
python scripts\audit_viewer.py AI_Employee_Vault --export --format json

# Search logs
python scripts\audit_viewer.py AI_Employee_Vault --search "invoice"
```

---

## Workflow Examples

### Example 1: Invoice Creation Flow (Odoo)

1. WhatsApp message received: "Send me invoice for January"
2. WhatsApp Watcher creates action file
3. Claude reads and creates plan
4. Odoo MCP creates draft invoice
5. Approval request created in Pending_Approval
6. Human approves
7. Odoo MCP posts invoice and emails customer
8. Transaction logged in Audit Log
9. Files moved to Done

### Example 2: Social Media Campaign

1. Business_Goals.md updated: "Launch new product campaign"
2. Claude creates social media plan
3. Facebook MCP creates draft posts
4. Twitter MCP creates draft tweets
5. Approval files created
6. Human approves all
7. Posts scheduled across platforms
8. Engagement tracked by watchers
9. Weekly report includes campaign performance

### Example 3: Weekly CEO Briefing

1. Sunday 11:00 PM: Scheduled task triggers
2. Odoo Watcher extracts week's transactions
3. All watchers compile activity data
4. CEO Briefing Generator analyzes:
   - Revenue from Odoo invoices
   - Expenses from bank transactions
   - Task completion from Done folder
   - Response times from logs
5. Briefing written to Briefings/
6. Dashboard.md updated
7. Notification created for Monday morning

---

## Configuration

### Facebook App Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create new app (Business type)
3. Add Facebook Login product
4. Configure OAuth redirect URI
5. Get App ID and App Secret
6. Generate Page Access Token
7. Add to `.env` file

### Twitter API Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create new project and app
3. Generate API Key and Secret
4. Generate Access Token and Secret
5. Get Bearer Token
6. Add to `.env` file

### Odoo Configuration

1. Access Odoo at http://localhost:8069
2. Create database (done automatically by Docker)
3. Install required apps:
   - Invoicing
   - Accounting
   - Contacts
   - CRM (optional)
4. Configure chart of accounts
5. Set up fiscal year
6. Create initial contacts

---

## Directory Structure (Gold Tier)

```
Personal-AI-Employe-FTEs/
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/
│   ├── Needs_Action/
│   │   ├── Gmail/
│   │   ├── WhatsApp/
│   │   ├── Facebook/
│   │   ├── Twitter/
│   │   └── Odoo/
│   ├── Done/
│   ├── Plans/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Logs/
│   │   ├── audit_YYYY-MM-DD.json
│   │   ├── error_YYYY-MM-DD.json
│   │   └── activity_YYYY-MM-DD.md
│   ├── Briefings/
│   │   └── YYYY-MM-DD_Monday_Briefing.md
│   ├── Accounting/
│   │   ├── Current_Month.md
│   │   └── Transactions/
│   ├── Invoices/
│   ├── .whatsapp_session/
│   ├── .linkedin_session/
│   ├── .facebook_session/
│   └── .twitter_session/
├── odoo/
│   ├── docker-compose.yml
│   ├── odoo-custom-addons/
│   └── README.md
├── scripts/
│   ├── Core Watchers
│   │   ├── base_watcher.py
│   │   ├── filesystem_watcher.py
│   │   ├── gmail_watcher.py
│   │   ├── whatsapp_watcher.py
│   │   ├── facebook_watcher.py
│   │   ├── twitter_watcher.py
│   │   └── odoo_watcher.py
│   ├── Social Posters
│   │   ├── linkedin_api_poster.py
│   │   ├── facebook_poster.py
│   │   └── twitter_poster.py
│   ├── MCP Servers
│   │   ├── mcp_email_server.py
│   │   ├── mcp_social_server.py
│   │   └── mcp_odoo_server.py
│   ├── Management
│   │   ├── orchestrator.py
│   │   ├── plan_generator.py
│   │   ├── approval_manager.py
│   │   ├── task_scheduler.py
│   │   ├── ceo_briefing_generator.py
│   │   ├── ralph_loop.py
│   │   ├── audit_viewer.py
│   │   └── verify_gold.py
│   ├── Utilities
│   │   ├── retry_handler.py
│   │   ├── audit_logger.py
│   │   └── error_recovery.py
│   └── requirements.txt
├── .env
├── credentials.json
├── GOLD_README.md
└── docker-compose.yml
```

---

## Error Recovery & Graceful Degradation

### Retry Logic

All external API calls implement exponential backoff:

```python
# Automatic retry with backoff
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
def call_external_api():
    # API call here
    pass
```

### Graceful Degradation

| Component Failure | Degradation Strategy |
|-------------------|---------------------|
| Gmail API down | Queue emails locally |
| Facebook API error | Log for later retry |
| Odoo unavailable | Pause accounting ops |
| Twitter rate limit | Queue tweets |
| Claude Code error | Human notification |

### Watchdog Process

```bash
# Start watchdog (monitors all processes)
python scripts\watchdog.py AI_Employee_Vault

# View watchdog status
python scripts\watchdog.py AI_Employee_Vault --status
```

---

## Security Notes

### Credential Management

- **NEVER commit** credential files
- Use `.env` for environment variables
- Rotate credentials monthly
- Use separate test credentials for development

### Files to Keep Private

```
.env
credentials.json
token.json
*.whatsapp_session/
*.linkedin_session/
*.facebook_session/
*.twitter_session/
odoo/odoo-custom-addons/
```

### Permission Boundaries

| Action | Auto-Approve | Require Approval |
|--------|-------------|------------------|
| Email replies | Known contacts | New contacts, bulk |
| Social posts | Scheduled drafts | Replies, DMs |
| Invoices | < $100 recurring | All new, > $500 |
| Payments | Never | Always |

---

## Troubleshooting

### Odoo Issues

| Issue | Solution |
|-------|----------|
| Container won't start | Check Docker Desktop running |
| Can't connect to Odoo | Wait 2-3 min for initialization |
| Database error | Run `docker-compose down -v` and restart |
| Module not found | Install in Odoo Apps menu |

### Facebook Issues

| Issue | Solution |
|-------|----------|
| Token expired | Regenerate Page Access Token |
| Permission denied | Check app review status |
| Post fails | Verify page ID is correct |
| Rate limited | Wait 24 hours, reduce frequency |

### Twitter Issues

| Issue | Solution |
|-------|----------|
| Authentication failed | Regenerate API keys |
| Tweet too long | Use thread instead |
| Rate limited | Check Twitter API limits |
| Media upload fails | Check file size < 5MB |

### Ralph Loop Issues

| Issue | Solution |
|-------|----------|
| Loop won't terminate | Increase max-iterations |
| Task incomplete | Check completion promise |
| High token usage | Simplify task scope |

---

## Hackathon Checklist (Gold Tier)

- [ ] All Silver requirements complete
- [ ] Odoo ERP running in Docker
- [ ] Odoo MCP server functional
- [ ] Facebook integration working
- [ ] Instagram integration working
- [ ] Twitter/X integration working
- [ ] Weekly CEO Briefing generates
- [ ] Ralph Wiggum loop implemented
- [ ] Audit logging comprehensive
- [ ] Error recovery tested
- [ ] All watchers running simultaneously
- [ ] Demo video created (5-10 min)
- [ ] Documentation complete
- [ ] Security disclosure written

---

## Testing Gold Tier

### Run Full System Test

```bash
# Test all components
python scripts\verify_gold.py AI_Employee_Vault --full-test

# Test Odoo integration
python scripts\odoo_test.py AI_Employee_Vault

# Test Facebook integration
python scripts\facebook_test.py AI_Employee_Vault

# Test Twitter integration
python scripts\twitter_test.py AI_Employee_Vault

# Test CEO Briefing
python scripts\ceo_briefing_generator.py AI_Employee_Vault --test
```

### Demo Scenario

For your hackathon demo, run this complete flow:

1. **Trigger**: Send WhatsApp message "Invoice client for $500"
2. **Watch**: WhatsApp Watcher detects and creates action file
3. **Plan**: Claude creates invoice plan
4. **Execute**: Odoo MCP creates draft invoice
5. **Approve**: Human approves via Approval Manager
6. **Post**: Odoo MCP posts invoice
7. **Social**: Facebook/Twitter MCP announces new client
8. **Audit**: CEO Briefing includes this transaction
9. **Log**: All actions in audit log

---

## Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Silver Tier README](./SILVER_README.md)
- [Odoo Documentation](https://www.odoo.com/documentation)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Weekly Research Meetings

- **When:** Wednesdays at 10:00 PM
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)

---

*AI Employee v0.3 - Gold Tier*
*Built for the Personal AI Employee Hackathon 2026*
