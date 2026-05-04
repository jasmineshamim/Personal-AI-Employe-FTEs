"""
Odoo ERP MCP Server for AI Employee - Gold Tier

Provides MCP (Model Context Protocol) interface for Odoo ERP operations:
- Create and manage invoices
- Record payments
- Manage contacts (customers/vendors)
- Generate accounting reports
- Check account balances
- Track inventory (optional)

Uses Odoo's JSON-RPC API for communication.
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from xmlrpc.client import ServerProxy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OdooMCP:
    """Odoo ERP MCP Server"""
    
    def __init__(self, vault_path: Optional[str] = None):
        self.vault_path = Path(vault_path) if vault_path else Path.cwd()
        
        # Odoo configuration from environment
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
        
        # Connect to Odoo
        self._connect()
    
    def _connect(self):
        """Authenticate and connect to Odoo"""
        try:
            common = ServerProxy(self.common_endpoint)
            
            # Authenticate
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
        
        try:
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
        except Exception as e:
            logger.error(f"Error executing {method} on {model}: {e}")
            raise
    
    # Invoice Operations
    
    def create_invoice(
        self,
        partner_id: int,
        invoice_type: str = 'out_invoice',
        lines: Optional[List[Dict]] = None,
        payment_term: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new invoice
        
        Args:
            partner_id: Customer/Vendor ID
            invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)
            lines: Invoice line items [{'product_id': int, 'quantity': float, 'price_unit': float}]
            payment_term: Payment term ID
        
        Returns:
            Invoice data including ID
        """
        invoice_lines = []
        
        if lines:
            for line in lines:
                invoice_lines.append((0, 0, {
                    'product_id': line.get('product_id'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                    'name': line.get('name', 'Service'),
                }))
        
        invoice_data = {
            'partner_id': partner_id,
            'move_type': invoice_type,
            'invoice_line_ids': invoice_lines,
        }
        
        if payment_term:
            invoice_data['invoice_payment_term_id'] = payment_term
        
        invoice_id = self._execute('account.move', 'create', invoice_data)
        
        # Get full invoice data
        invoice = self._execute(
            'account.move',
            'read',
            [invoice_id],
            {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date']}
        )
        
        return invoice[0] if invoice else {}
    
    def get_invoices(
        self,
        partner_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get invoices with optional filters
        
        Args:
            partner_id: Filter by customer/vendor
            state: Filter by state (draft, posted, paid, cancel)
            limit: Maximum number of results
        
        Returns:
            List of invoices
        """
        domain = []
        
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        
        if state:
            domain.append(('state', '=', state))
        
        invoice_ids = self._execute(
            'account.move',
            'search',
            domain,
            {'limit': limit, 'order': 'invoice_date desc'}
        )
        
        invoices = self._execute(
            'account.move',
            'read',
            [invoice_ids],
            {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'payment_state']}
        )
        
        return invoices
    
    def post_invoice(self, invoice_id: int) -> bool:
        """Post (confirm) an invoice"""
        try:
            self._execute('account.move', 'action_post', [invoice_id])
            return True
        except Exception as e:
            logger.error(f"Error posting invoice: {e}")
            return False
    
    def register_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: Optional[str] = None,
        payment_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register payment for an invoice
        
        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            payment_method: Payment method name
        
        Returns:
            Payment result
        """
        try:
            # Create payment wizard
            wizard_data = {
                'payment_date': payment_date or datetime.now().strftime('%Y-%m-%d'),
                'amount': amount,
            }
            
            wizard_id = self._execute(
                'account.payment.register',
                'create',
                wizard_data
            )
            
            # Create payment
            self._execute(
                'account.payment.register',
                'action_create_payments',
                [wizard_id]
            )
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'amount': amount,
                'payment_date': payment_date
            }
            
        except Exception as e:
            logger.error(f"Error registering payment: {e}")
            return {'success': False, 'error': str(e)}
    
    # Contact Operations
    
    def create_contact(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_company: bool = True,
        customer: bool = True,
        vendor: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new contact (customer/vendor)
        
        Args:
            name: Contact name
            email: Email address
            phone: Phone number
            is_company: True for company, False for individual
            customer: Is a customer
            vendor: Is a vendor
        
        Returns:
            Contact data
        """
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'is_company': is_company,
            'customer_rank': 1 if customer else 0,
            'supplier_rank': 1 if vendor else 0,
        }
        
        contact_id = self._execute('res.partner', 'create', contact_data)
        
        contact = self._execute(
            'res.partner',
            'read',
            [contact_id],
            {'fields': ['name', 'email', 'phone', 'customer_rank', 'supplier_rank']}
        )
        
        return contact[0] if contact else {}
    
    def get_contacts(
        self,
        search_term: Optional[str] = None,
        customer: Optional[bool] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get contacts with optional filters"""
        domain = []
        
        if search_term:
            domain.append(('name', 'ilike', search_term))
        
        if customer is True:
            domain.append(('customer_rank', '>', 0))
        elif customer is False:
            domain.append(('supplier_rank', '>', 0))
        
        contact_ids = self._execute(
            'res.partner',
            'search',
            domain,
            {'limit': limit}
        )
        
        contacts = self._execute(
            'res.partner',
            'read',
            [contact_ids],
            {'fields': ['name', 'email', 'phone', 'customer_rank', 'supplier_rank']}
        )
        
        return contacts
    
    # Accounting Operations
    
    def get_account_balance(self, account_code: Optional[str] = None) -> Dict[str, float]:
        """
        Get account balances
        
        Args:
            account_code: Specific account code to filter
        
        Returns:
            Dictionary of account balances
        """
        domain = []
        
        if account_code:
            domain.append(('code', '=', account_code))
        
        account_ids = self._execute('account.account', 'search', domain)
        
        accounts = self._execute(
            'account.account',
            'read',
            [account_ids],
            {'fields': ['code', 'name', 'balance']}
        )
        
        return {
            acc['code']: acc['balance']
            for acc in accounts
        }
    
    def generate_trial_balance(
        self,
        date_from: str,
        date_to: str
    ) -> List[Dict[str, Any]]:
        """
        Generate trial balance report
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
        
        Returns:
            Trial balance data
        """
        # This would typically use Odoo's report engine
        # Simplified version here
        
        account_ids = self._execute(
            'account.account',
            'search',
            []
        )
        
        accounts = self._execute(
            'account.account',
            'read',
            [account_ids],
            {'fields': ['code', 'name', 'balance', 'debit', 'credit']}
        )
        
        return accounts
    
    # Reporting Operations
    
    def get_partner_ledger(self, partner_id: int) -> List[Dict[str, Any]]:
        """Get ledger for a specific partner"""
        move_line_ids = self._execute(
            'account.move.line',
            'search',
            [('partner_id', '=', partner_id)],
            {'order': 'date desc', 'limit': 50}
        )
        
        lines = self._execute(
            'account.move.line',
            'read',
            [move_line_ids],
            {'fields': ['date', 'move_id', 'debit', 'credit', 'balance', 'name']}
        )
        
        return lines
    
    def get_sales_report(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """
        Get sales report for period
        
        Args:
            date_from: Start date
            date_to: End date
        
        Returns:
            Sales summary
        """
        invoice_ids = self._execute(
            'account.move',
            'search',
            [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '=', 'posted')
            ]
        )
        
        invoices = self._execute(
            'account.move',
            'read',
            [invoice_ids],
            {'fields': ['amount_total', 'amount_untaxed', 'amount_tax']}
        )
        
        total_sales = sum(inv.get('amount_total', 0) for inv in invoices)
        total_untaxed = sum(inv.get('amount_untaxed', 0) for inv in invoices)
        total_tax = sum(inv.get('amount_tax', 0) for inv in invoices)
        
        return {
            'total_sales': total_sales,
            'total_untaxed': total_untaxed,
            'total_tax': total_tax,
            'invoice_count': len(invoices),
            'period': f"{date_from} to {date_to}"
        }
    
    # MCP Tool Methods (for Claude Code integration)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        return [
            {
                'name': 'odoo_create_invoice',
                'description': 'Create a new customer or vendor invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'partner_id': {'type': 'integer', 'description': 'Customer/Vendor ID'},
                        'invoice_type': {'type': 'string', 'description': 'out_invoice or in_invoice'},
                        'lines': {'type': 'array', 'description': 'Invoice line items'},
                        'payment_term': {'type': 'integer', 'description': 'Payment term ID'}
                    },
                    'required': ['partner_id']
                }
            },
            {
                'name': 'odoo_get_invoices',
                'description': 'Get invoices with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'partner_id': {'type': 'integer'},
                        'state': {'type': 'string'},
                        'limit': {'type': 'integer'}
                    }
                }
            },
            {
                'name': 'odoo_post_invoice',
                'description': 'Post (confirm) an invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer'}
                    },
                    'required': ['invoice_id']
                }
            },
            {
                'name': 'odoo_register_payment',
                'description': 'Register payment for an invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer'},
                        'amount': {'type': 'number'},
                        'payment_date': {'type': 'string'},
                        'payment_method': {'type': 'string'}
                    },
                    'required': ['invoice_id', 'amount']
                }
            },
            {
                'name': 'odoo_create_contact',
                'description': 'Create a new contact (customer/vendor)',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'is_company': {'type': 'boolean'},
                        'customer': {'type': 'boolean'},
                        'vendor': {'type': 'boolean'}
                    },
                    'required': ['name']
                }
            },
            {
                'name': 'odoo_get_contacts',
                'description': 'Search contacts',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'search_term': {'type': 'string'},
                        'customer': {'type': 'boolean'},
                        'limit': {'type': 'integer'}
                    }
                }
            },
            {
                'name': 'odoo_get_account_balance',
                'description': 'Get account balances',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'account_code': {'type': 'string'}
                    }
                }
            },
            {
                'name': 'odoo_get_sales_report',
                'description': 'Get sales report for period',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'date_from': {'type': 'string'},
                        'date_to': {'type': 'string'}
                    },
                    'required': ['date_from', 'date_to']
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        try:
            if tool_name == 'odoo_create_invoice':
                return self.create_invoice(**arguments)
            elif tool_name == 'odoo_get_invoices':
                invoices = self.get_invoices(**arguments)
                return {'invoices': invoices}
            elif tool_name == 'odoo_post_invoice':
                success = self.post_invoice(arguments['invoice_id'])
                return {'success': success}
            elif tool_name == 'odoo_register_payment':
                return self.register_payment(**arguments)
            elif tool_name == 'odoo_create_contact':
                return self.create_contact(**arguments)
            elif tool_name == 'odoo_get_contacts':
                contacts = self.get_contacts(**arguments)
                return {'contacts': contacts}
            elif tool_name == 'odoo_get_account_balance':
                return self.get_account_balance(**arguments)
            elif tool_name == 'odoo_get_sales_report':
                return self.get_sales_report(**arguments)
            else:
                return {'error': f'Unknown tool: {tool_name}'}
        except Exception as e:
            return {'error': str(e)}


def main():
    """Main entry point for Odoo MCP Server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('vault_path', type=str, nargs='?', help='Path to Obsidian vault')
    parser.add_argument('--test-connection', action='store_true', help='Test Odoo connection')
    parser.add_argument('--list-tools', action='store_true', help='List available tools')
    parser.add_argument('--call-tool', type=str, help='Call a tool (JSON)')
    parser.add_argument('--create-invoice', type=str, help='Create invoice (JSON)')
    parser.add_argument('--get-invoices', action='store_true', help='Get recent invoices')
    parser.add_argument('--create-contact', type=str, help='Create contact (JSON)')
    parser.add_argument('--get-sales', type=str, help='Get sales report (date_from,date_to)')
    
    args = parser.parse_args()
    
    vault_path = args.vault_path if args.vault_path else str(Path.cwd())
    odoo = OdooMCP(vault_path)
    
    if args.test_connection:
        if odoo.connected:
            print("✅ Connected to Odoo successfully!")
            print(f"   URL: {odoo.odoo_url}")
            print(f"   Database: {odoo.odoo_db}")
            print(f"   User ID: {odoo.uid}")
        else:
            print("❌ Failed to connect to Odoo")
            print("   Check your .env file and ensure Odoo is running")
        return
    
    if args.list_tools:
        tools = odoo.list_tools()
        print("\n=== Available Odoo MCP Tools ===\n")
        for tool in tools:
            print(f"**{tool['name']}**")
            print(f"   {tool['description']}")
            print()
        return
    
    if args.get_invoices:
        invoices = odoo.get_invoices(limit=5)
        print("\n=== Recent Invoices ===\n")
        for inv in invoices:
            print(f"  {inv.get('name', 'N/A')}: ${inv.get('amount_total', 0):.2f} - {inv.get('state', 'N/A')}")
        return
    
    if args.create_invoice:
        data = json.loads(args.create_invoice)
        result = odoo.create_invoice(**data)
        print(f"\n✅ Invoice created: {result}")
        return
    
    if args.create_contact:
        data = json.loads(args.create_contact)
        result = odoo.create_contact(**data)
        print(f"\n✅ Contact created: {result}")
        return
    
    if args.get_sales:
        dates = args.get_sales.split(',')
        if len(dates) == 2:
            report = odoo.get_sales_report(dates[0], dates[1])
            print(f"\n=== Sales Report ===\n")
            print(f"  Total Sales: ${report.get('total_sales', 0):.2f}")
            print(f"  Invoices: {report.get('invoice_count', 0)}")
        return


if __name__ == '__main__':
    main()
