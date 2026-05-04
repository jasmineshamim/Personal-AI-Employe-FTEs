"""
Odoo ERP Watcher for AI Employee - Gold Tier

Monitors Odoo for business events:
- New invoices created
- Payments received
- Low stock alerts (if inventory enabled)
- Overdue invoices
- New customers/vendors

Creates action files in Needs_Action folder for Claude to process.
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from xmlrpc.client import ServerProxy

from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OdooWatcher(BaseWatcher):
    """Watcher for Odoo ERP events"""
    
    def __init__(
        self,
        vault_path: str,
        check_interval: int = 600,  # 10 minutes
        keywords: Optional[List[str]] = None
    ):
        super().__init__(vault_path, check_interval)
        
        # Odoo configuration
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        
        # XML-RPC endpoints
        self.common_endpoint = f"{self.odoo_url}/xmlrpc/2/common"
        self.object_endpoint = f"{self.odoo_url}/xmlrpc/2/object"
        
        # Session
        self.uid = None
        self.connected = False
        
        # Track processed items
        self.processed_invoices = set()
        self.processed_payments = set()
        
        # Session file
        self.session_file = self.vault_path / '.odoo_session' / 'state.json'
        self._load_session()
        
        # Connect to Odoo
        self._connect()
    
    def _connect(self):
        """Authenticate with Odoo"""
        try:
            common = ServerProxy(self.common_endpoint)
            
            self.uid = common.authenticate(
                self.odoo_db,
                self.odoo_username,
                self.odoo_password,
                {}
            )
            
            if self.uid:
                self.connected = True
                logger.info(f"Connected to Odoo as user {self.uid}")
            else:
                logger.error("Failed to authenticate with Odoo")
                
        except Exception as e:
            logger.error(f"Error connecting to Odoo: {e}")
            self.connected = False
    
    def _execute(self, model: str, method: str, *args, **kwargs):
        """Execute Odoo model method"""
        if not self.connected:
            self._connect()
        
        if not self.connected:
            raise Exception("Not connected to Odoo")
        
        models = ServerProxy(self.object_endpoint)
        return models.execute_kw(
            self.odoo_db,
            self.uid,
            self.odoo_password,
            model,
            method,
            args,
            kwargs
        )
    
    def _load_session(self):
        """Load session state"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                    self.processed_invoices = set(state.get('processed_invoices', []))
                    self.processed_payments = set(state.get('processed_payments', []))
                logger.info(f"Loaded Odoo session: {len(self.processed_invoices)} invoices tracked")
            except Exception as e:
                logger.error(f"Failed to load session: {e}")
    
    def _save_session(self):
        """Save session state"""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.session_file, 'w') as f:
                json.dump({
                    'processed_invoices': list(self.processed_invoices),
                    'processed_payments': list(self.processed_payments)
                }, f)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new Odoo events"""
        if not self.connected:
            return []
        
        updates = []
        
        try:
            # Check for new invoices
            invoices = self._check_new_invoices()
            updates.extend(invoices)
            
            # Check for new payments
            payments = self._check_new_payments()
            updates.extend(payments)
            
            # Check for overdue invoices
            overdue = self._check_overdue_invoices()
            updates.extend(overdue)
            
            # Check for new contacts
            contacts = self._check_new_contacts()
            updates.extend(contacts)
            
        except Exception as e:
            logger.error(f"Error checking Odoo updates: {e}")
        
        return updates
    
    def _check_new_invoices(self) -> List[Dict[str, Any]]:
        """Check for new draft invoices"""
        invoices = []
        
        try:
            # Get draft invoices from last check
            one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            
            invoice_ids = self._execute(
                'account.move',
                'search',
                [
                    ('move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('state', '=', 'draft'),
                    ('create_date', '>=', one_hour_ago)
                ]
            )
            
            if invoice_ids:
                invoice_data = self._execute(
                    'account.move',
                    'read',
                    [invoice_ids],
                    {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'move_type']}
                )
                
                for inv in invoice_data:
                    inv_id = inv.get('id')
                    if inv_id and inv_id not in self.processed_invoices:
                        # Get partner name
                        partner_name = 'Unknown'
                        if inv.get('partner_id'):
                            partner = self._execute(
                                'res.partner',
                                'read',
                                [inv['partner_id'][0]],
                                {'fields': ['name']}
                            )
                            if partner:
                                partner_name = partner[0].get('name', 'Unknown')
                        
                        invoice_event = {
                            'type': 'odoo_new_invoice',
                            'id': inv_id,
                            'name': inv.get('name', 'N/A'),
                            'partner': partner_name,
                            'amount': inv.get('amount_total', 0),
                            'invoice_date': inv.get('invoice_date'),
                            'invoice_type': inv.get('move_type', 'out_invoice'),
                            'priority': 'high' if inv.get('amount_total', 0) > 1000 else 'medium'
                        }
                        invoices.append(invoice_event)
                        self.processed_invoices.add(inv_id)
        
        except Exception as e:
            logger.error(f"Error checking new invoices: {e}")
        
        return invoices
    
    def _check_new_payments(self) -> List[Dict[str, Any]]:
        """Check for new payments"""
        payments = []
        
        try:
            one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            
            payment_ids = self._execute(
                'account.payment',
                'search',
                [
                    ('state', '=', 'posted'),
                    ('date', '>=', one_hour_ago)
                ]
            )
            
            if payment_ids:
                payment_data = self._execute(
                    'account.payment',
                    'read',
                    [payment_ids],
                    {'fields': ['name', 'partner_id', 'amount', 'date', 'payment_type']}
                )
                
                for payment in payment_data:
                    payment_id = payment.get('id')
                    if payment_id and payment_id not in self.processed_payments:
                        # Get partner name
                        partner_name = 'Unknown'
                        if payment.get('partner_id'):
                            partner = self._execute(
                                'res.partner',
                                'read',
                                [payment['partner_id'][0]],
                                {'fields': ['name']}
                            )
                            if partner:
                                partner_name = partner[0].get('name', 'Unknown')
                        
                        payment_event = {
                            'type': 'odoo_new_payment',
                            'id': payment_id,
                            'name': payment.get('name', 'N/A'),
                            'partner': partner_name,
                            'amount': payment.get('amount', 0),
                            'date': payment.get('date'),
                            'payment_type': payment.get('payment_type', 'inbound'),
                            'priority': 'high' if payment.get('amount', 0) > 1000 else 'medium'
                        }
                        payments.append(payment_event)
                        self.processed_payments.add(payment_id)
        
        except Exception as e:
            logger.error(f"Error checking new payments: {e}")
        
        return payments
    
    def _check_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Check for overdue invoices"""
        overdue = []
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            overdue_ids = self._execute(
                'account.move',
                'search',
                [
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '=', 'not_paid'),
                    ('invoice_date_due', '<', today)
                ]
            )
            
            if overdue_ids:
                overdue_data = self._execute(
                    'account.move',
                    'read',
                    [overdue_ids[:5]],  # Limit to 5
                    {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date_due']}
                )
                
                for inv in overdue_data:
                    # Get partner name
                    partner_name = 'Unknown'
                    if inv.get('partner_id'):
                        partner = self._execute(
                            'res.partner',
                            'read',
                            [inv['partner_id'][0]],
                            {'fields': ['name']}
                        )
                        if partner:
                            partner_name = partner[0].get('name', 'Unknown')
                    
                    overdue_event = {
                        'type': 'odoo_overdue_invoice',
                        'id': inv.get('id'),
                        'name': inv.get('name', 'N/A'),
                        'partner': partner_name,
                        'amount': inv.get('amount_total', 0),
                        'due_date': inv.get('invoice_date_due'),
                        'priority': 'high'
                    }
                    overdue.append(overdue_event)
        
        except Exception as e:
            logger.error(f"Error checking overdue invoices: {e}")
        
        return overdue
    
    def _check_new_contacts(self) -> List[Dict[str, Any]]:
        """Check for new contacts"""
        contacts = []
        
        try:
            one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            
            contact_ids = self._execute(
                'res.partner',
                'search',
                [
                    ('create_date', '>=', one_hour_ago)
                ],
                {'limit': 10}
            )
            
            if contact_ids:
                contact_data = self._execute(
                    'res.partner',
                    'read',
                    [contact_ids],
                    {'fields': ['name', 'email', 'phone', 'customer_rank', 'supplier_rank']}
                )
                
                for contact in contact_data:
                    contact_event = {
                        'type': 'odoo_new_contact',
                        'id': contact.get('id'),
                        'name': contact.get('name', 'Unknown'),
                        'email': contact.get('email'),
                        'phone': contact.get('phone'),
                        'is_customer': contact.get('customer_rank', 0) > 0,
                        'is_vendor': contact.get('supplier_rank', 0) > 0,
                        'priority': 'normal'
                    }
                    contacts.append(contact_event)
        
        except Exception as e:
            logger.error(f"Error checking new contacts: {e}")
        
        return contacts
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        
        filename = f"{item_type.upper()}_{item.get('name', 'Unknown')}_{timestamp}.md"
        filepath = self.needs_action / 'Odoo' / filename
        
        # Ensure Odoo subfolder exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        priority = item.get('priority', 'normal')
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'normal': '🟢'}.get(priority, '⚪')
        
        # Build content based on type
        if item_type == 'odoo_new_invoice':
            content = self._create_invoice_action_file(item, priority_emoji)
        elif item_type == 'odoo_new_payment':
            content = self._create_payment_action_file(item, priority_emoji)
        elif item_type == 'odoo_overdue_invoice':
            content = self._create_overdue_action_file(item, priority_emoji)
        elif item_type == 'odoo_new_contact':
            content = self._create_contact_action_file(item, priority_emoji)
        else:
            content = self._create_generic_action_file(item, priority_emoji)
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Odoo action file: {filepath}")
        
        # Save session
        self._save_session()
        
        return filepath
    
    def _create_invoice_action_file(self, item: Dict, priority_emoji: str) -> str:
        """Create action file for new invoice"""
        return f"""---
type: {item.get('type', 'odoo_new_invoice')}
invoice_id: {item.get('id')}
invoice_name: {item.get('name')}
partner: {item.get('partner')}
amount: {item.get('amount')}
invoice_date: {item.get('invoice_date')}
priority: {item.get('priority')}
status: pending
source: odoo
---

# {priority_emoji} New Invoice Created in Odoo

**Invoice:** {item.get('name')}
**Customer/Vendor:** {item.get('partner')}
**Amount:** ${item.get('amount', 0):.2f}
**Date:** {item.get('invoice_date')}
**Priority:** {item.get('priority')}

## Details

A new invoice has been created in Odoo ERP and is in draft state.

## Suggested Actions

- [ ] Review invoice details in Odoo
- [ ] Verify line items and amounts
- [ ] Post invoice (if correct)
- [ ] Send to customer (if sales invoice)
- [ ] Record in accounting

## Odoo Navigation

1. Go to Accounting → Invoices
2. Search for: {item.get('name')}
3. Review and post

---
*Created by Odoo Watcher - Gold Tier AI Employee*
"""
    
    def _create_payment_action_file(self, item: Dict, priority_emoji: str) -> str:
        """Create action file for new payment"""
        payment_direction = 'Received' if item.get('payment_type') == 'inbound' else 'Made'
        
        return f"""---
type: {item.get('type', 'odoo_new_payment')}
payment_id: {item.get('id')}
payment_name: {item.get('name')}
partner: {item.get('partner')}
amount: {item.get('amount')}
date: {item.get('date')}
direction: {payment_direction}
priority: {item.get('priority')}
status: pending
source: odoo
---

# {priority_emoji} New Payment {payment_direction}

**Payment:** {item.get('name')}
**Partner:** {item.get('partner')}
**Amount:** ${item.get('amount', 0):.2f}
**Date:** {item.get('date')}
**Direction:** {payment_direction}

## Details

A new payment has been recorded in Odoo ERP.

## Suggested Actions

- [ ] Verify payment amount matches invoice
- [ ] Confirm bank reconciliation
- [ ] Update customer balance
- [ ] Send receipt (if received)

## Odoo Navigation

1. Go to Accounting → Payments
2. Search for: {item.get('name')}
3. Review and reconcile

---
*Created by Odoo Watcher - Gold Tier AI Employee*
"""
    
    def _create_overdue_action_file(self, item: Dict, priority_emoji: str) -> str:
        """Create action file for overdue invoice"""
        return f"""---
type: {item.get('type', 'odoo_overdue_invoice')}
invoice_id: {item.get('id')}
invoice_name: {item.get('name')}
partner: {item.get('partner')}
amount: {item.get('amount')}
due_date: {item.get('due_date')}
priority: high
status: pending
source: odoo
---

# {priority_emoji} OVERDUE INVOICE - Action Required

**Invoice:** {item.get('name')}
**Customer:** {item.get('partner')}
**Amount:** ${item.get('amount', 0):.2f}
**Due Date:** {item.get('due_date')}
**Priority:** HIGH

## ⚠️ Urgent

This invoice is overdue and requires immediate attention.

## Suggested Actions

- [ ] Contact customer for payment
- [ ] Send payment reminder
- [ ] Check if there's a dispute
- [ ] Consider late fees
- [ ] Update collection status in Odoo

## Odoo Navigation

1. Go to Accounting → Customers → Invoices
2. Filter by: Overdue
3. Find: {item.get('name')}
4. Send reminder or make collection note

---
*Created by Odoo Watcher - Gold Tier AI Employee*
"""
    
    def _create_contact_action_file(self, item: Dict, priority_emoji: str) -> str:
        """Create action file for new contact"""
        return f"""---
type: {item.get('type', 'odoo_new_contact')}
contact_id: {item.get('id')}
name: {item.get('name')}
email: {item.get('email')}
phone: {item.get('phone')}
is_customer: {item.get('is_customer')}
is_vendor: {item.get('is_vendor')}
priority: normal
status: pending
source: odoo
---

# {priority_emoji} New Contact Added to Odoo

**Name:** {item.get('name')}
**Email:** {item.get('email') or 'N/A'}
**Phone:** {item.get('phone') or 'N/A'}
**Customer:** {'Yes' if item.get('is_customer') else 'No'}
**Vendor:** {'Yes' if item.get('is_vendor') else 'No'}

## Details

A new contact has been added to Odoo ERP.

## Suggested Actions

- [ ] Verify contact information
- [ ] Add additional details (address, tax ID)
- [ ] Set payment terms
- [ ] Link to existing records if duplicate

## Odoo Navigation

1. Go to Contacts
2. Search for: {item.get('name')}
3. Review and complete information

---
*Created by Odoo Watcher - Gold Tier AI Employee*
"""
    
    def _create_generic_action_file(self, item: Dict, priority_emoji: str) -> str:
        """Create generic action file"""
        return f"""---
type: {item.get('type', 'unknown')}
priority: {item.get('priority')}
status: pending
source: odoo
---

# {priority_emoji} Odoo Event

**Type:** {item.get('type')}
**Priority:** {item.get('priority')}

## Details

{json.dumps(item, indent=2, default=str)}

## Suggested Actions

- [ ] Review event details
- [ ] Take appropriate action in Odoo
- [ ] Document in vault

---
*Created by Odoo Watcher - Gold Tier AI Employee*
"""


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo Watcher')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=600, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--check-invoices', action='store_true', help='Check invoices only')
    parser.add_argument('--check-payments', action='store_true', help='Check payments only')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    if args.setup:
        print("\n=== Odoo Watcher Setup ===\n")
        print("Add to your .env file:")
        print("  ODOO_URL=http://localhost:8069")
        print("  ODOO_DB=odoo")
        print("  ODOO_USERNAME=admin")
        print("  ODOO_PASSWORD=admin")
        print("\nEnsure Odoo is running:")
        print("  cd odoo")
        print("  docker-compose up -d")
        return
    
    watcher = OdooWatcher(
        vault_path=str(vault_path),
        check_interval=args.interval
    )
    
    logger.info("Starting Odoo Watcher...")
    
    if args.once or args.check_invoices or args.check_payments:
        logger.info("Running single check...")
        updates = watcher.check_for_updates()
        
        for update in updates:
            watcher.create_action_file(update)
        
        logger.info(f"Found {len(updates)} updates")
    else:
        # Run continuously
        try:
            while True:
                updates = watcher.check_for_updates()
                
                for update in updates:
                    watcher.create_action_file(update)
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")


if __name__ == '__main__':
    main()
