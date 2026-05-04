# Gold Tier Quick Start Guide

## Complete Gold Tier Setup in 30 Minutes

This guide walks you through setting up all Gold Tier components for the AI Employee hackathon.

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **Python 3.13+** installed
- ✅ **Node.js v24+** installed
- ✅ **Git** installed
- ✅ **Claude Code** subscription active
- ✅ **Obsidian** installed

---

## Step 1: Install Python Dependencies (5 minutes)

```bash
# Navigate to project root
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employe-FTEs

# Install all Gold Tier dependencies
pip install -r scripts\requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## Step 2: Set Up Environment Variables (5 minutes)

Create a `.env` file in the project root:

```bash
# Copy the template
copy .env.template .env

# Edit .env with your credentials
notepad .env
```

### Required Credentials

#### Odoo ERP (Local)
```
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

#### Facebook (Optional for full demo)
1. Go to https://developers.facebook.com/
2. Create a new app (Business type)
3. Add Facebook Login product
4. Get credentials from app dashboard

```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_instagram_id (optional)
```

#### Twitter/X (Optional for full demo)
1. Go to https://developer.twitter.com/
2. Create a project and app
3. Get API credentials

```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
```

---

## Step 3: Start Odoo ERP (5 minutes)

```bash
# Navigate to odoo directory
cd odoo

# Start Odoo containers
docker-compose up -d

# Wait for initialization (check logs)
docker-compose logs -f

# Press Ctrl+C to exit logs
# Access Odoo at http://localhost:8069
```

**First-time Odoo Setup:**

1. Open http://localhost:8069
2. Default credentials: `admin` / `admin`
3. Create database (if prompted)
4. Install apps:
   - Invoicing
   - Accounting
   - Contacts

---

## Step 4: Verify Setup (2 minutes)

```bash
# Return to project root
cd ..

# Run Gold Tier verification
python scripts\verify_gold.py AI_Employee_Vault

# Run full integration tests
python scripts\verify_gold.py AI_Employee_Vault --full-test
```

Expected output:
- ✅ All critical checks pass
- ⚠️ Warnings for optional credentials (if not configured)

---

## Step 5: Configure MCP Servers (3 minutes)

The `mcp.json` file is already configured with:

- **email**: Gmail integration
- **odoo**: Odoo ERP integration
- **social**: Facebook & Twitter integration
- **browser**: Browser automation

Verify MCP configuration:

```bash
# Test Odoo MCP
python scripts\mcp_odoo_server.py AI_Employee_Vault --test-connection

# Test Social MCP
python scripts\mcp_social_server.py --test

# List available tools
python scripts\mcp_odoo_server.py --list-tools
python scripts\mcp_social_server.py --list-tools
```

---

## Step 6: Start All Watchers (2 minutes)

```bash
# Start all Gold Tier watchers
scripts\start-gold-watchers.bat AI_Employee_Vault

# Or start individually:
start python scripts\filesystem_watcher.py AI_Employee_Vault
start python scripts\gmail_watcher.py AI_Employee_Vault
start python scripts\whatsapp_watcher.py AI_Employee_Vault
start python scripts\facebook_watcher.py AI_Employee_Vault
start python scripts\twitter_watcher.py AI_Employee_Vault
start python scripts\odoo_watcher.py AI_Employee_Vault
```

---

## Step 7: Generate First CEO Briefing (3 minutes)

```bash
# Generate weekly briefing
python scripts\ceo_briefing_generator.py AI_Employee_Vault --test

# View the briefing
notepad AI_Employee_Vault\Briefings\*_Monday_Briefing.md
```

---

## Step 8: Test Ralph Wiggum Loop (5 minutes)

```bash
# Run demo mode
python scripts\ralph_loop.py AI_Employee_Vault "Process all pending items" --demo

# Run actual loop (max 5 iterations)
python scripts\ralph_loop.py AI_Employee_Vault "Review and process Needs_Action folder" --max-iterations 5
```

---

## Step 9: Test Audit Logging (1 minute)

```bash
# View today's audit log
python scripts\audit_logger.py AI_Employee_Vault --view

# Log a test entry
python scripts\audit_logger.py AI_Employee_Vault --log "test_action"

# Search logs
python scripts\audit_logger.py AI_Employee_Vault --search "test"
```

---

## Step 10: Run Complete Demo Flow (10 minutes)

### Scenario: Invoice Client and Post on Social Media

1. **Trigger**: Create action file
   ```bash
   notepad AI_Employee_Vault\Needs_Action\TEST_invoice_request.md
   ```
   
   Content:
   ```markdown
   ---
   type: test_request
   priority: high
   ---
   
   # Test Invoice Request
   
   Create invoice for Client A ($1,500) and post on social media.
   ```

2. **Process with Claude Code**
   ```bash
   claude --prompt "Process the test invoice request in Needs_Action folder"
   ```

3. **Check Results**
   - View created invoice in Odoo
   - Check social media drafts
   - Review audit logs

---

## Troubleshooting

### Docker Issues

```bash
# Check Docker is running
docker ps

# Restart Docker Desktop if needed

# Restart Odoo containers
cd odoo
docker-compose down
docker-compose up -d
```

### Python Import Errors

```bash
# Reinstall dependencies
pip install -r scripts\requirements.txt --force-reinstall

# Verify installation
python scripts\verify_gold.py AI_Employee_Vault
```

### Credential Issues

```bash
# Check .env file
type .env

# Reload environment variables
# Close and reopen terminal
```

---

## Hackathon Demo Checklist

Before your demo, verify:

- [ ] All watchers running (6 terminal windows)
- [ ] Odoo accessible at http://localhost:8069
- [ ] CEO Briefing generated in Briefings/
- [ ] Audit logs being created in Logs/Audit/
- [ ] MCP servers configured in mcp.json
- [ ] .env file has required credentials
- [ ] Demo scenario tested end-to-end

---

## Next Steps

After setup is complete:

1. **Customize Business Goals**: Edit `AI_Employee_Vault/Business_Goals.md`
2. **Configure Subscription Audit**: Add your actual subscriptions to tracking
3. **Set Up Scheduled Tasks**: Use Windows Task Scheduler for automation
4. **Create Demo Script**: Plan your 5-10 minute demo video

---

## Resources

- [Gold Tier README](./GOLD_README.md)
- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Odoo Documentation](https://www.odoo.com/documentation)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)

---

*Gold Tier Quick Start - AI Employee Hackathon 2026*
