# Odoo ERP Setup for AI Employee - Gold Tier

This directory contains the Odoo ERP setup for the AI Employee Gold Tier implementation.

## Quick Start

### 1. Start Odoo with Docker

```bash
# Navigate to odoo directory
cd odoo

# Start Odoo and PostgreSQL containers
docker-compose up -d

# Wait for Odoo to initialize (2-3 minutes)
docker-compose logs -f
```

### 2. Access Odoo

Open your browser and go to: http://localhost:8069

**Default Credentials:**
- Database: `odoo`
- Username: `admin`
- Password: `admin`

### 3. Initial Configuration

1. **Create Database** (if not auto-created):
   - Click "Create Database"
   - Master password: `admin` (from docker-compose)
   - Database name: `odoo`
   - Email: your-email@example.com
   - Password: admin

2. **Install Required Apps**:
   - Go to Apps menu
   - Install these modules:
     - **Invoicing** (essential for invoice management)
     - **Accounting** (for full accounting features)
     - **Contacts** (for customer/vendor management)
     - **CRM** (optional, for customer relationship)
     - **Sales** (optional, for sales orders)

3. **Configure Chart of Accounts**:
   - Go to Accounting → Configuration → Settings
   - Select your country's chart of accounts
   - Complete the setup wizard

4. **Set Up Fiscal Year**:
   - Accounting → Configuration → Settings
   - Configure fiscal year dates
   - Set tax return periods

## Directory Structure

```
odoo/
├── docker-compose.yml          # Docker configuration
├── odoo-custom-addons/         # Custom modules (create this folder)
├── odoo-config/               # Odoo configuration files
├── README.md                  # This file
└── scripts/
    ├── init_odoo.py           # Initialization script
    └── sample_data.py         # Sample data for testing
```

## Create Required Folders

```bash
# Create folders for custom addons and config
mkdir odoo-custom-addons
mkdir odoo-config
```

## Odoo Configuration

### odoo-config/odoo.conf

```ini
[options]
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo
data_dir = /var/lib/odoo
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
log_level = info
logfile = /var/log/odoo/odoo.log
```

## Integration with AI Employee

### Environment Variables

Add to your `.env` file:

```bash
# Odoo ERP Credentials
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
ODOO_API_KEY=your_api_key  # Generate in Odoo settings
```

### Generate Odoo API Key

1. Log in to Odoo as admin
2. Go to Settings → Users & Companies → Users
3. Click on your user (admin)
4. Click "Action" → "Reset Password"
5. Use this password as API key

## Common Operations

### Start Odoo

```bash
docker-compose up -d
```

### Stop Odoo

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f
```

### Restart Odoo

```bash
docker-compose restart
```

### Backup Database

```bash
docker-compose exec db pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U odoo odoo < backup_20260114.sql
```

## Testing Connection

```bash
# Test Odoo connection
python scripts/odoo_test.py AI_Employee_Vault

# Create test invoice
python scripts/mcp_odoo_server.py --test-connection
```

## Troubleshooting

### Container Won't Start

```bash
# Check Docker is running
docker ps

# View container logs
docker-compose logs odoo

# Restart containers
docker-compose down
docker-compose up -d
```

### Database Connection Error

```bash
# Check database container
docker-compose ps db

# Restart database
docker-compose restart db
```

### Can't Access Web Interface

1. Check if port 8069 is in use:
   ```bash
   netstat -ano | findstr :8069
   ```

2. Try different port in docker-compose.yml:
   ```yaml
   ports:
     - "8070:8069"  # Use port 8070 instead
   ```

### Reset Odoo

```bash
# Complete reset (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
```

## Security Notes

- **Change default password** immediately in production
- **Never expose Odoo** directly to internet without HTTPS
- **Use environment variables** for sensitive data
- **Regular backups** are essential
- **Keep Odoo updated** to latest version

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation)
- [Odoo 19 External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html#json-rpc-http-endpoint)

---

*Odoo Setup for AI Employee Gold Tier - January 2026*
