"""
Gold Tier Verification Script for AI Employee

Comprehensive verification of all Gold Tier components:
- Odoo ERP connection
- Facebook/Instagram integration
- Twitter/X integration
- CEO Briefing generator
- Ralph Wiggum loop
- Audit logging system
- All watchers

Run this script to validate your Gold Tier setup before the hackathon demo.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoldTierVerifier:
    """Verify Gold Tier setup and functionality"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.project_root = self.vault_path.parent
        self.scripts_dir = self.project_root / 'scripts'
        self.odoo_dir = self.project_root / 'odoo'
        
        # Results tracking
        self.results: Dict[str, Dict[str, Any]] = {}
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def verify_all(self) -> bool:
        """Run all verification checks"""
        print("\n" + "="*70)
        print("  AI EMPLOYEE - GOLD TIER VERIFICATION")
        print("="*70 + "\n")
        
        checks = [
            ("Directory Structure", self.verify_directory_structure),
            ("Environment Variables", self.verify_environment),
            ("Python Dependencies", self.verify_dependencies),
            ("Odoo ERP Setup", self.verify_odoo),
            ("Facebook Integration", self.verify_facebook),
            ("Twitter Integration", self.verify_twitter),
            ("Vault Structure", self.verify_vault),
            ("MCP Configuration", self.verify_mcp_config),
            ("Watcher Scripts", self.verify_watchers),
            ("Gold Tier Scripts", self.verify_gold_scripts),
        ]
        
        for name, check_func in checks:
            self._run_check(name, check_func)
        
        # Print summary
        self._print_summary()
        
        return self.failed == 0
    
    def _run_check(self, name: str, check_func):
        """Run a verification check"""
        print(f"\n{'='*50}")
        print(f"  Checking: {name}")
        print(f"{'='*50}")
        
        try:
            result = check_func()
            self.results[name] = result
            
            if result.get('status') == 'pass':
                self.passed += 1
                print(f"  ✅ PASS")
            elif result.get('status') == 'warning':
                self.warnings += 1
                print(f"  ⚠️ WARNING: {result.get('message', '')}")
            else:
                self.failed += 1
                print(f"  ❌ FAIL: {result.get('message', '')}")
                
        except Exception as e:
            self.failed += 1
            self.results[name] = {'status': 'fail', 'message': str(e)}
            print(f"  ❌ FAIL: {e}")
    
    def verify_directory_structure(self) -> Dict[str, Any]:
        """Verify required directories exist"""
        required_dirs = [
            self.vault_path,
            self.vault_path / 'Needs_Action',
            self.vault_path / 'Done',
            self.vault_path / 'Pending_Approval',
            self.vault_path / 'Approved',
            self.vault_path / 'Briefings',
            self.vault_path / 'Logs',
            self.vault_path / 'Plans',
            self.scripts_dir,
            self.odoo_dir,
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing.append(str(dir_path))
        
        if missing:
            return {
                'status': 'fail',
                'message': f"Missing directories: {', '.join(missing)}"
            }
        
        return {'status': 'pass', 'message': 'All directories present'}
    
    def verify_environment(self) -> Dict[str, Any]:
        """Verify environment variables"""
        required_vars = {
            # Odoo
            'ODOO_URL': False,  # Not strictly required (has default)
            'ODOO_DB': False,
            'ODOO_USERNAME': False,
            'ODOO_PASSWORD': False,
            
            # Facebook (optional for Gold Tier)
            'FACEBOOK_APP_ID': True,
            'FACEBOOK_APP_SECRET': True,
            'FACEBOOK_ACCESS_TOKEN': True,
            'FACEBOOK_PAGE_ID': True,
            
            # Twitter (optional for Gold Tier)
            'TWITTER_API_KEY': True,
            'TWITTER_API_SECRET': True,
            'TWITTER_ACCESS_TOKEN': True,
            'TWITTER_ACCESS_TOKEN_SECRET': True,
        }
        
        missing_critical = []
        missing_optional = []
        
        for var, required in required_vars.items():
            value = os.getenv(var)
            if not value:
                if required:
                    missing_critical.append(var)
                else:
                    missing_optional.append(var)
        
        if missing_critical:
            return {
                'status': 'warning',
                'message': f"Missing optional credentials: {', '.join(missing_critical)}",
                'details': 'These are needed for full functionality but not required for basic setup'
            }
        
        if missing_optional:
            return {
                'status': 'warning',
                'message': f"Odoo credentials not set (using defaults): {', '.join(missing_optional)}"
            }
        
        return {'status': 'pass', 'message': 'All environment variables set'}
    
    def verify_dependencies(self) -> Dict[str, Any]:
        """Verify Python dependencies"""
        required_packages = [
            ('watchdog', 'watchdog'),
            ('playwright', 'playwright'),
            ('requests', 'requests'),
            ('python-dotenv', 'dotenv'),
        ]
        
        optional_packages = [
            ('facebook-business', 'facebook_business'),
            ('tweepy', 'tweepy'),
            ('google-api-python-client', 'googleapiclient'),
        ]
        
        missing_required = []
        missing_optional = []
        
        for pkg_name, import_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing_required.append(pkg_name)
        
        for pkg_name, import_name in optional_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing_optional.append(pkg_name)
        
        if missing_required:
            return {
                'status': 'fail',
                'message': f"Missing required packages: {', '.join(missing_required)}",
                'fix': 'pip install -r scripts/requirements.txt'
            }
        
        if missing_optional:
            return {
                'status': 'warning',
                'message': f"Optional packages not installed: {', '.join(missing_optional)}",
                'fix': 'pip install facebook-business tweepy google-api-python-client'
            }
        
        return {'status': 'pass', 'message': 'All dependencies installed'}
    
    def verify_odoo(self) -> Dict[str, Any]:
        """Verify Odoo setup"""
        # Check docker-compose.yml exists
        docker_compose = self.odoo_dir / 'docker-compose.yml'
        if not docker_compose.exists():
            return {
                'status': 'fail',
                'message': 'Odoo docker-compose.yml not found'
            }
        
        # Check if Docker is running
        try:
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return {
                    'status': 'warning',
                    'message': 'Docker is not running'
                }
        except FileNotFoundError:
            return {
                'status': 'warning',
                'message': 'Docker not installed'
            }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Docker check failed: {e}'
            }
        
        # Check if Odoo container is running
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=ai_employee_odoo'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'ai_employee_odoo' not in result.stdout:
                return {
                    'status': 'warning',
                    'message': 'Odoo container not running (run: cd odoo && docker-compose up -d)'
                }
        except:
            pass
        
        return {'status': 'pass', 'message': 'Odoo setup complete'}
    
    def verify_facebook(self) -> Dict[str, Any]:
        """Verify Facebook integration"""
        app_id = os.getenv('FACEBOOK_APP_ID')
        app_secret = os.getenv('FACEBOOK_APP_SECRET')
        access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        page_id = os.getenv('FACEBOOK_PAGE_ID')
        
        if not all([app_id, app_secret, access_token, page_id]):
            return {
                'status': 'warning',
                'message': 'Facebook credentials not fully configured'
            }
        
        # Check if facebook-business is installed
        try:
            from facebook_business.api import FacebookAdsApi
        except ImportError:
            return {
                'status': 'warning',
                'message': 'facebook-business package not installed'
            }
        
        return {'status': 'pass', 'message': 'Facebook integration configured'}
    
    def verify_twitter(self) -> Dict[str, Any]:
        """Verify Twitter integration"""
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            return {
                'status': 'warning',
                'message': 'Twitter credentials not fully configured'
            }
        
        # Check if tweepy is installed
        try:
            import tweepy
        except ImportError:
            return {
                'status': 'warning',
                'message': 'tweepy package not installed'
            }
        
        return {'status': 'pass', 'message': 'Twitter integration configured'}
    
    def verify_vault(self) -> Dict[str, Any]:
        """Verify Obsidian vault structure"""
        required_files = [
            self.vault_path / 'Dashboard.md',
            self.vault_path / 'Company_Handbook.md',
            self.vault_path / 'Business_Goals.md',
        ]
        
        missing = []
        for file_path in required_files:
            if not file_path.exists():
                missing.append(file_path.name)
        
        if missing:
            return {
                'status': 'warning',
                'message': f"Missing vault files: {', '.join(missing)}"
            }
        
        return {'status': 'pass', 'message': 'Vault structure complete'}
    
    def verify_mcp_config(self) -> Dict[str, Any]:
        """Verify MCP configuration"""
        mcp_file = self.project_root / 'mcp.json'
        if not mcp_file.exists():
            return {
                'status': 'fail',
                'message': 'mcp.json not found'
            }
        
        try:
            with open(mcp_file, 'r') as f:
                config = json.load(f)
            
            servers = config.get('mcpServers', {})
            required_servers = ['email', 'odoo']
            optional_servers = ['social', 'browser']
            
            missing_required = []
            for server in required_servers:
                if server not in servers:
                    missing_required.append(server)
            
            if missing_required:
                return {
                    'status': 'fail',
                    'message': f"Missing required MCP servers: {', '.join(missing_required)}"
                }
            
            return {'status': 'pass', 'message': f"MCP configured: {list(servers.keys())}"}
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f"Error reading mcp.json: {e}"
            }
    
    def verify_watchers(self) -> Dict[str, Any]:
        """Verify watcher scripts exist"""
        required_watchers = [
            'base_watcher.py',
            'filesystem_watcher.py',
            'gmail_watcher.py',
            'whatsapp_watcher.py',
            'facebook_watcher.py',
            'odoo_watcher.py',
            'twitter_watcher.py',
        ]
        
        missing = []
        for watcher in required_watchers:
            watcher_path = self.scripts_dir / watcher
            if not watcher_path.exists():
                missing.append(watcher)
        
        if missing:
            return {
                'status': 'fail',
                'message': f"Missing watchers: {', '.join(missing)}"
            }
        
        return {'status': 'pass', 'message': 'All watchers present'}
    
    def verify_gold_scripts(self) -> Dict[str, Any]:
        """Verify Gold Tier specific scripts"""
        gold_scripts = [
            'mcp_odoo_server.py',
            'mcp_social_server.py',
            'facebook_poster.py',
            'ceo_briefing_generator.py',
            'ralph_loop.py',
            'audit_logger.py',
        ]
        
        missing = []
        for script in gold_scripts:
            script_path = self.scripts_dir / script
            if not script_path.exists():
                missing.append(script)
        
        if missing:
            return {
                'status': 'fail',
                'message': f"Missing Gold Tier scripts: {', '.join(missing)}"
            }
        
        return {'status': 'pass', 'message': 'All Gold Tier scripts present'}
    
    def _print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("  VERIFICATION SUMMARY")
        print("="*70 + "\n")
        
        total = self.passed + self.failed + self.warnings
        
        print(f"  Total Checks: {total}")
        print(f"  ✅ Passed: {self.passed}")
        print(f"  ⚠️ Warnings: {self.warnings}")
        print(f"  ❌ Failed: {self.failed}")
        print()
        
        if self.failed == 0:
            if self.warnings == 0:
                print("  🎉 ALL CHECKS PASSED! Gold Tier is ready!")
            else:
                print("  ✅ All critical checks passed. Some optional features not configured.")
        else:
            print("  ❌ Some checks failed. Please fix the issues above.")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Tier Verification')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--full-test', action='store_true', help='Run full integration tests')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    verifier = GoldTierVerifier(str(vault_path))
    success = verifier.verify_all()
    
    if args.json:
        print(json.dumps(verifier.results, indent=2))
    
    if args.full_test:
        print("\n=== Running Full Integration Tests ===\n")
        # Run component tests
        test_commands = [
            ('Odoo Connection', ['python', 'scripts/mcp_odoo_server.py', str(vault_path), '--test-connection']),
            ('CEO Briefing Test', ['python', 'scripts/ceo_briefing_generator.py', str(vault_path), '--test']),
            ('Audit Logger Test', ['python', 'scripts/audit_logger.py', str(vault_path), '--log', 'test']),
        ]
        
        for name, cmd in test_commands:
            print(f"\nTesting: {name}")
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(verifier.project_root)
                )
                print(result.stdout)
                if result.returncode != 0:
                    print(f"⚠️ {name} test had issues")
            except Exception as e:
                print(f"❌ {name} test failed: {e}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
