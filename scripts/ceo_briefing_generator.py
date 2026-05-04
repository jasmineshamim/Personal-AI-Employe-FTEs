"""
CEO Briefing Generator for AI Employee - Gold Tier

Generates comprehensive weekly business briefings including:
- Revenue summary (from Odoo)
- Expense analysis
- Task completion metrics
- Response time tracking
- Subscription audit
- Bottleneck identification
- Proactive suggestions

Outputs to Briefings/ folder as Markdown for Obsidian.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from xmlrpc.client import ServerProxy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CEOBriefingGenerator:
    """Generate weekly CEO briefings"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_folder = self.vault_path / 'Briefings'
        self.logs_folder = self.vault_path / 'Logs'
        self.done_folder = self.vault_path / 'Done'
        self.accounting_folder = self.vault_path / 'Accounting'
        
        # Ensure folders exist
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Odoo configuration
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        
        # Odoo connection
        self.odoo_uid = None
        self.odoo_connected = False
        self._connect_odoo()
    
    def _connect_odoo(self):
        """Connect to Odoo"""
        try:
            common = ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            
            self.odoo_uid = common.authenticate(
                self.odoo_db,
                self.odoo_username,
                self.odoo_password,
                {}
            )
            
            if self.odoo_uid:
                self.odoo_connected = True
                logger.info("Connected to Odoo for briefing generation")
            else:
                logger.warning("Could not connect to Odoo - financial data will be limited")
                
        except Exception as e:
            logger.warning(f"Odoo connection failed: {e}")
            self.odoo_connected = False
    
    def _execute_odoo(self, model: str, method: str, *args, **kwargs):
        """Execute Odoo method"""
        if not self.odoo_connected:
            return None
        
        try:
            models = ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
            return models.execute_kw(
                self.odoo_db,
                self.odoo_uid,
                self.odoo_password,
                model,
                method,
                args,
                kwargs
            )
        except Exception as e:
            logger.error(f"Odoo execution error: {e}")
            return None
    
    def generate_briefing(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        audit_type: Optional[str] = None
    ) -> Path:
        """
        Generate CEO briefing
        
        Args:
            start_date: Start of period (default: 7 days ago)
            end_date: End of period (default: today)
            audit_type: Specific audit type (subscriptions, revenue, tasks)
        
        Returns:
            Path to generated briefing file
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=7)
        
        # Determine day name for Monday briefing
        if start_date.weekday() == 0:  # Monday
            briefing_name = f"{start_date.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        else:
            briefing_name = f"{start_date.strftime('%Y-%m-%d')}_Weekly_Briefing.md"
        
        filepath = self.briefings_folder / briefing_name
        
        # Gather all data
        logger.info("Generating CEO Briefing...")
        
        data = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            'revenue': self._get_revenue_data(start_date, end_date),
            'expenses': self._get_expense_data(start_date, end_date),
            'tasks': self._get_task_metrics(start_date, end_date),
            'subscriptions': self._audit_subscriptions() if audit_type != 'revenue' else {},
            'social_media': self._get_social_media_metrics(),
            'bottlenecks': self._identify_bottlenecks(start_date, end_date),
            'suggestions': self._generate_suggestions(start_date, end_date)
        }
        
        # Generate briefing content
        content = self._render_briefing(data)
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"CEO Briefing generated: {filepath}")
        
        # Update Dashboard
        self._update_dashboard(data)
        
        return filepath
    
    def _get_revenue_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get revenue data from Odoo"""
        if not self.odoo_connected:
            return self._get_revenue_from_files(start_date, end_date)
        
        try:
            # Get posted customer invoices
            invoice_ids = self._execute_odoo(
                'account.move',
                'search',
                [
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', start_date.strftime('%Y-%m-%d')),
                    ('invoice_date', '<=', end_date.strftime('%Y-%m-%d'))
                ]
            )
            
            if not invoice_ids:
                return {'total': 0, 'invoices': [], 'trend': 'stable'}
            
            invoices = self._execute_odoo(
                'account.move',
                'read',
                [invoice_ids],
                {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'payment_state']}
            )
            
            total = sum(inv.get('amount_total', 0) for inv in invoices)
            paid = sum(inv.get('amount_total', 0) for inv in invoices if inv.get('payment_state') == 'paid')
            pending = total - paid
            
            # Get previous period for trend
            prev_start = start_date - (end_date - start_date)
            prev_total = self._get_previous_revenue(prev_start, start_date)
            
            trend = 'increasing' if total > prev_total else ('decreasing' if total < prev_total else 'stable')
            
            return {
                'total': total,
                'paid': paid,
                'pending': pending,
                'invoice_count': len(invoices),
                'trend': trend,
                'previous_period': prev_total,
                'invoices': invoices[:10]  # Top 10
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue data: {e}")
            return self._get_revenue_from_files(start_date, end_date)
    
    def _get_revenue_from_files(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Fallback: Get revenue from vault files"""
        total = 0
        count = 0
        
        # Look for invoice files in Done folder
        for file in self.done_folder.rglob('*.md'):
            content = file.read_text(encoding='utf-8')
            if 'invoice' in content.lower() and 'amount' in content.lower():
                # Simple parsing - look for amount patterns
                import re
                amounts = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', content)
                for amount in amounts:
                    try:
                        total += float(amount.replace(',', ''))
                        count += 1
                    except:
                        pass
        
        return {
            'total': total,
            'paid': total * 0.8,  # Estimate
            'pending': total * 0.2,
            'invoice_count': count,
            'trend': 'stable',
            'previous_period': total * 0.95
        }
    
    def _get_previous_revenue(self, start: datetime, end: datetime) -> float:
        """Get revenue for previous period"""
        if not self.odoo_connected:
            return 0
        
        invoice_ids = self._execute_odoo(
            'account.move',
            'search',
            [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', end.strftime('%Y-%m-%d'))
            ]
        )
        
        if not invoice_ids:
            return 0
        
        invoices = self._execute_odoo(
            'account.move',
            'read',
            [invoice_ids],
            {'fields': ['amount_total']}
        )
        
        return sum(inv.get('amount_total', 0) for inv in invoices)
    
    def _get_expense_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get expense data"""
        if not self.odoo_connected:
            return self._get_expenses_from_files()
        
        try:
            # Get vendor bills
            bill_ids = self._execute_odoo(
                'account.move',
                'search',
                [
                    ('move_type', '=', 'in_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', start_date.strftime('%Y-%m-%d')),
                    ('invoice_date', '<=', end_date.strftime('%Y-%m-%d'))
                ]
            )
            
            if not bill_ids:
                return {'total': 0, 'bills': []}
            
            bills = self._execute_odoo(
                'account.move',
                'read',
                [bill_ids],
                {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date']}
            )
            
            total = sum(bill.get('amount_total', 0) for bill in bills)
            
            return {
                'total': total,
                'bill_count': len(bills),
                'bills': bills[:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting expense data: {e}")
            return self._get_expenses_from_files()
    
    def _get_expenses_from_files(self) -> Dict[str, Any]:
        """Fallback: Get expenses from files"""
        return {'total': 0, 'bill_count': 0, 'bills': []}
    
    def _get_task_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get task completion metrics from vault"""
        completed = 0
        pending = 0
        overdue = 0
        
        # Count completed tasks
        for file in self.done_folder.rglob('*.md'):
            content = file.read_text(encoding='utf-8')
            if '[x]' in content:
                import re
                completed += len(re.findall(r'\- \[x\]', content))
        
        # Count pending tasks
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            pending = len(list(needs_action.rglob('*.md')))
        
        # Calculate completion rate
        total = completed + pending
        rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': rate,
            'total': total
        }
    
    def _audit_subscriptions(self) -> Dict[str, Any]:
        """Audit subscriptions for unused services"""
        subscriptions = []
        flags = []
        
        # Common subscription patterns
        subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'github.com': 'GitHub',
            'aws.amazon.com': 'AWS',
            'azure.microsoft.com': 'Azure',
        }
        
        if self.odoo_connected:
            # Search vendor bills for subscriptions
            for pattern, name in subscription_patterns.items():
                bill_ids = self._execute_odoo(
                    'account.move',
                    'search',
                    [
                        ('move_type', '=', 'in_invoice'),
                        ('narration', 'ilike', pattern),
                        ('state', '=', 'posted')
                    ],
                    {'limit': 1}
                )
                
                if bill_ids:
                    bills = self._execute_odoo(
                        'account.move',
                        'read',
                        [bill_ids],
                        {'fields': ['amount_total', 'invoice_date']}
                    )
                    
                    if bills:
                        subscriptions.append({
                            'name': name,
                            'last_charge': bills[0].get('invoice_date'),
                            'amount': bills[0].get('amount_total', 0)
                        })
        
        # Check for flags
        for sub in subscriptions:
            if sub.get('amount', 0) > 100:
                flags.append({
                    'subscription': sub['name'],
                    'reason': 'High cost',
                    'action': 'Review necessity'
                })
        
        return {
            'subscriptions': subscriptions,
            'total_monthly': sum(s.get('amount', 0) for s in subscriptions),
            'flags': flags
        }
    
    def _get_social_media_metrics(self) -> Dict[str, Any]:
        """Get social media activity metrics"""
        metrics = {
            'facebook': {'posts': 0, 'engagement': 0},
            'twitter': {'tweets': 0, 'engagement': 0},
            'linkedin': {'posts': 0, 'engagement': 0},
            'instagram': {'posts': 0, 'engagement': 0}
        }
        
        # Read from log files
        for log_file in self.logs_folder.glob('social_*.json'):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    metrics['facebook']['posts'] += len(logs)
            except:
                pass
        
        for log_file in self.logs_folder.glob('twitter_*.json'):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    metrics['twitter']['posts'] = len(logs)
            except:
                pass
        
        return metrics
    
    def _identify_bottlenecks(self, start_date: datetime, end_date: datetime) -> List[Dict[str, str]]:
        """Identify business bottlenecks"""
        bottlenecks = []
        
        # Check for overdue invoices
        if self.odoo_connected:
            overdue_ids = self._execute_odoo(
                'account.move',
                'search',
                [
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '=', 'not_paid'),
                    ('invoice_date_due', '<', datetime.now().strftime('%Y-%m-%d'))
                ]
            )
            
            if overdue_ids and len(overdue_ids) > 3:
                bottlenecks.append({
                    'area': 'Accounts Receivable',
                    'issue': f'{len(overdue_ids)} overdue invoices',
                    'impact': 'Cash flow delay',
                    'suggestion': 'Send payment reminders'
                })
        
        # Check pending tasks
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            pending_count = len(list(needs_action.rglob('*.md')))
            if pending_count > 10:
                bottlenecks.append({
                    'area': 'Task Processing',
                    'issue': f'{pending_count} pending items',
                    'impact': 'Delayed responses',
                    'suggestion': 'Increase processing frequency'
                })
        
        return bottlenecks
    
    def _generate_suggestions(self, start_date: datetime, end_date: datetime) -> List[Dict[str, str]]:
        """Generate proactive suggestions"""
        suggestions = []
        
        revenue = self._get_revenue_data(start_date, end_date)
        expenses = self._get_expense_data(start_date, end_date)
        
        # Revenue suggestions
        if revenue.get('trend') == 'decreasing':
            suggestions.append({
                'category': 'Revenue',
                'suggestion': 'Revenue is down compared to last period',
                'action': 'Review sales pipeline and follow up on leads',
                'priority': 'high'
            })
        
        # Expense suggestions - fix division by zero
        total_revenue = revenue.get('total', 0)
        total_expenses = expenses.get('total', 0)
        profit = total_revenue - total_expenses
        
        if total_revenue > 0:
            profit_margin = (profit / total_revenue) * 100
            if profit_margin < 20:
                suggestions.append({
                    'category': 'Expenses',
                    'suggestion': f'Profit margin is {profit_margin:.1f}%',
                    'action': 'Review expenses for cost-cutting opportunities',
                    'priority': 'high'
                })
        else:
            # No revenue data - suggest adding Odoo integration
            suggestions.append({
                'category': 'Accounting',
                'suggestion': 'No revenue data available',
                'action': 'Connect Odoo ERP for automated financial tracking',
                'priority': 'medium'
            })
        
        # Task suggestions
        tasks = self._get_task_metrics(start_date, end_date)
        if tasks.get('completion_rate', 100) < 70:
            suggestions.append({
                'category': 'Productivity',
                'suggestion': f'Task completion rate is {tasks["completion_rate"]:.1f}%',
                'action': 'Consider automating more tasks or adjusting priorities',
                'priority': 'medium'
            })
        
        return suggestions
    
    def _render_briefing(self, data: Dict[str, Any]) -> str:
        """Render briefing as Markdown"""
        period = data['period']
        revenue = data['revenue']
        expenses = data['expenses']
        tasks = data['tasks']
        subscriptions = data['subscriptions']
        social = data['social_media']
        bottlenecks = data['bottlenecks']
        suggestions = data['suggestions']
        
        # Calculate profit
        profit = revenue.get('total', 0) - expenses.get('total', 0)
        profit_margin = (profit / revenue.get('total', 1)) * 100 if revenue.get('total', 0) > 0 else 0
        
        # Trend emoji
        trend_emoji = {'increasing': '📈', 'decreasing': '📉', 'stable': '➡️'}.get(revenue.get('trend', 'stable'), '➡️')
        
        content = f"""---
generated: {period['generated']}
period: {period['start']} to {period['end']}
type: ceo_briefing
---

# 👔 Monday Morning CEO Briefing

**Generated:** {period['generated']}
**Period:** {period['start']} to {period['end']}

---

## 📊 Executive Summary

{self._generate_executive_summary(revenue, expenses, tasks)}

---

## 💰 Revenue

| Metric | Value |
|--------|-------|
| **Total Revenue** | ${revenue.get('total', 0):,.2f} |
| **Paid** | ${revenue.get('paid', 0):,.2f} |
| **Pending** | ${revenue.get('pending', 0):,.2f} |
| **Invoices** | {revenue.get('invoice_count', 0)} |
| **Trend** | {trend_emoji} {revenue.get('trend', 'stable').title()} |

### Recent Invoices

"""
        
        for inv in revenue.get('invoices', [])[:5]:
            partner = inv.get('partner_id', ['Unknown'])[1] if isinstance(inv.get('partner_id'), list) else 'Unknown'
            content += f"- **{inv.get('name', 'N/A')}**: ${inv.get('amount_total', 0):,.2f} - {inv.get('payment_state', 'N/A')}\n"
        
        content += f"""
---

## 💸 Expenses

| Metric | Value |
|--------|-------|
| **Total Expenses** | ${expenses.get('total', 0):,.2f} |
| **Bills** | {expenses.get('bill_count', 0)} |

---

## 📈 Profit & Loss

| Metric | Value |
|--------|-------|
| **Revenue** | ${revenue.get('total', 0):,.2f} |
| **Expenses** | ${expenses.get('total', 0):,.2f} |
| **Profit** | ${profit:,.2f} |
| **Margin** | {profit_margin:.1f}% |

---

## ✅ Task Completion

| Metric | Value |
|--------|-------|
| **Completed** | {tasks.get('completed', 0)} |
| **Pending** | {tasks.get('pending', 0)} |
| **Completion Rate** | {tasks.get('completion_rate', 0):.1f}% |

---

## 📱 Social Media Activity

| Platform | Posts | Engagement |
|----------|-------|------------|
| Facebook | {social.get('facebook', {}).get('posts', 0)} | - |
| Twitter | {social.get('twitter', {}).get('posts', 0)} | - |
| LinkedIn | {social.get('linkedin', {}).get('posts', 0)} | - |
| Instagram | {social.get('instagram', {}).get('posts', 0)} | - |

---

## 🔄 Subscription Audit

**Total Monthly:** ${subscriptions.get('total_monthly', 0):,.2f}

"""
        
        for sub in subscriptions.get('subscriptions', [])[:10]:
            content += f"- **{sub.get('name')}**: ${sub.get('amount', 0):,.2f} (last: {sub.get('last_charge', 'N/A')})\n"
        
        if subscriptions.get('flags'):
            content += "\n### ⚠️ Flags\n"
            for flag in subscriptions.get('flags', []):
                content += f"- **{flag['subscription']}**: {flag['reason']} - {flag['action']}\n"
        
        if bottlenecks:
            content += "\n---\n\n## 🚧 Bottlenecks\n\n"
            for bn in bottlenecks:
                content += f"### {bn['area']}\n"
                content += f"- **Issue:** {bn['issue']}\n"
                content += f"- **Impact:** {bn['impact']}\n"
                content += f"- **Suggestion:** {bn['suggestion']}\n\n"
        
        if suggestions:
            content += "\n---\n\n## 💡 Proactive Suggestions\n\n"
            for sug in suggestions:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(sug.get('priority', 'low'), '⚪')
                content += f"### {priority_emoji} {sug['category']}\n"
                content += f"**Observation:** {sug['suggestion']}\n"
                content += f"**Action:** {sug['action']}\n\n"
        
        content += f"""
---

## 📋 Action Items for This Week

- [ ] Review overdue invoices and send reminders
- [ ] Process pending items in Needs_Action folder
- [ ] Review subscription flags
- [ ] Address identified bottlenecks
- [ ] Implement high-priority suggestions

---

*Briefing generated by AI Employee Gold Tier - Your 24/7 Business Partner*
"""
        
        return content
    
    def _generate_executive_summary(self, revenue: Dict, expenses: Dict, tasks: Dict) -> str:
        """Generate executive summary text"""
        profit = revenue.get('total', 0) - expenses.get('total', 0)
        trend = revenue.get('trend', 'stable')
        
        if trend == 'increasing' and profit > 0:
            return "Strong performance with revenue growth and healthy profits. Key metrics trending positively."
        elif trend == 'decreasing' and profit > 0:
            return "Revenue declined but maintaining profitability. Review sales pipeline and consider cost optimization."
        elif profit < 0:
            return "Loss incurred this period. Immediate attention required on both revenue generation and expense management."
        else:
            return "Stable performance with consistent revenue. Focus on growth opportunities and operational efficiency."
    
    def _update_dashboard(self, data: Dict[str, Any]):
        """Update Dashboard.md with briefing highlights"""
        dashboard_file = self.vault_path / 'Dashboard.md'
        
        if not dashboard_file.exists():
            return
        
        content = dashboard_file.read_text(encoding='utf-8')
        
        # Add latest briefing summary
        revenue = data['revenue']
        tasks = data['tasks']
        
        update = f"""

## 📊 Latest Briefing Update ({data['period']['generated']})

- **Revenue This Period:** ${revenue.get('total', 0):,.2f} ({revenue.get('trend', 'stable')})
- **Task Completion:** {tasks.get('completion_rate', 0):.1f}%
- **Pending Items:** {tasks.get('pending', 0)}

"""
        
        # Insert after first heading
        lines = content.split('\n')
        insert_idx = 1
        for i, line in enumerate(lines):
            if line.startswith('#'):
                insert_idx = i + 1
                break
        
        lines.insert(insert_idx, update)
        dashboard_file.write_text('\n'.join(lines), encoding='utf-8')


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--audit', type=str, choices=['subscriptions', 'revenue', 'tasks'], help='Specific audit type')
    parser.add_argument('--test', action='store_true', help='Test mode (generate sample)')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    generator = CEOBriefingGenerator(str(vault_path))
    
    if args.test:
        print("\n=== CEO Briefing Generator Test ===\n")
        print("Testing connection to Odoo...")
        if generator.odoo_connected:
            print("✅ Odoo connected")
        else:
            print("⚠️ Odoo not connected (will use file-based data)")
        
        print("\nGenerating sample briefing...")
        filepath = generator.generate_briefing()
        print(f"✅ Briefing generated: {filepath}")
        return
    
    start_date = datetime.strptime(args.start, '%Y-%m-%d') if args.start else None
    end_date = datetime.strptime(args.end, '%Y-%m-%d') if args.end else None
    
    filepath = generator.generate_briefing(start_date, end_date, args.audit)
    print(f"✅ CEO Briefing generated: {filepath}")


if __name__ == '__main__':
    main()
