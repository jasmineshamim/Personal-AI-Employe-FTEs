#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify AI Employee Setup - Bronze Tier

Checks that all required components are in place and working.

Usage:
    python verify.py /path/to/vault
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version is 3.13+"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 13):
        print("  [WARN] Python 3.13+ recommended, but may work with 3.8+")
    else:
        print("  [OK] Python version OK")
    return True


def check_dependencies():
    """Check required Python packages."""
    print("\nChecking dependencies...")
    
    all_ok = True
    
    # Core dependencies
    try:
        import watchdog
        print(f"  [OK] watchdog installed")
    except ImportError:
        print(f"  [FAIL] watchdog not installed")
        print(f"    Install with: pip install watchdog")
        all_ok = False
    
    # Gmail dependencies (optional for Silver Tier)
    try:
        from google.oauth2.credentials import Credentials
        print(f"  [OK] google-api-python-client installed")
    except ImportError:
        print(f"  [WARN] google-api-python-client not installed (Gmail Watcher won't work)")
        # Don't fail - it's optional
    
    # Playwright dependencies (optional for Silver Tier)
    try:
        import playwright
        print(f"  [OK] playwright installed")
    except ImportError:
        print(f"  [WARN] playwright not installed (WhatsApp/LinkedIn won't work)")
        # Don't fail - it's optional
    
    return all_ok


def check_vault_structure(vault_path: Path) -> bool:
    """Check vault folder structure."""
    print("\nChecking vault structure...")
    
    # Bronze Tier folders
    bronze_folders = [
        'Inbox',
        'Needs_Action',
        'Done',
    ]
    
    # Silver Tier folders
    silver_folders = [
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs',
        'Briefings'
    ]
    
    all_ok = True
    
    print("  Bronze Tier:")
    for folder in bronze_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"    [OK] /{folder}")
        else:
            print(f"    [FAIL] /{folder} - MISSING")
            all_ok = False
    
    print("  Silver Tier:")
    for folder in silver_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"    [OK] /{folder}")
        else:
            print(f"    [FAIL] /{folder} - MISSING")
            all_ok = False
    
    return all_ok


def check_vault_files(vault_path: Path) -> bool:
    """Check required vault files."""
    print("\nChecking vault files...")
    
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md'
    ]
    
    all_ok = True
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [FAIL] {file} - MISSING")
            all_ok = False
    
    return all_ok


def check_scripts(scripts_path: Path) -> bool:
    """Check required scripts."""
    print("\nChecking scripts...")
    
    # Bronze Tier scripts
    bronze_scripts = [
        'base_watcher.py',
        'filesystem_watcher.py',
        'orchestrator.py'
    ]
    
    # Silver Tier scripts
    silver_scripts = [
        'gmail_watcher.py',
        'whatsapp_watcher.py',
        'linkedin_poster.py',
        'plan_generator.py',
        'approval_manager.py',
        'task_scheduler.py'
    ]
    
    all_ok = True
    
    print("  Bronze Tier:")
    for script in bronze_scripts:
        script_path = scripts_path / script
        if script_path.exists():
            print(f"    [OK] {script}")
        else:
            print(f"    [FAIL] {script} - MISSING")
            all_ok = False
    
    print("  Silver Tier:")
    for script in silver_scripts:
        script_path = scripts_path / script
        if script_path.exists():
            print(f"    [OK] {script}")
        else:
            print(f"    [FAIL] {script} - MISSING")
            all_ok = False
    
    return all_ok


def check_qwen_code() -> bool:
    """Check if Qwen Code is installed."""
    print("\nChecking Qwen Code...")

    try:
        result = subprocess.run(
            ['qwen', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"  [OK] Qwen Code installed")
            print(f"    {result.stdout.strip()}")
            return True
        else:
            print(f"  [FAIL] Qwen Code returned error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  [FAIL] Qwen Code not found in PATH")
        print("    Make sure Qwen Code is installed and in your PATH.")
        return False
    except subprocess.TimeoutExpired:
        print("  [WARN] Qwen Code check timed out")
        return False
    except Exception as e:
        print(f"  [FAIL] Error checking Qwen Code: {e}")
        return False


def test_watcher_import(vault_path: Path) -> bool:
    """Test that watcher scripts can be imported."""
    print("\nTesting watcher imports...")
    
    scripts_dir = vault_path.parent / 'scripts'
    sys.path.insert(0, str(scripts_dir))
    
    try:
        from base_watcher import BaseWatcher
        print("  [OK] base_watcher imports OK")
    except Exception as e:
        print(f"  [FAIL] base_watcher import failed: {e}")
        return False
    
    try:
        from filesystem_watcher import FilesystemWatcher
        print("  [OK] filesystem_watcher imports OK")
    except Exception as e:
        print(f"  [FAIL] filesystem_watcher import failed: {e}")
        return False
    
    return True


def main():
    print("=" * 60)
    print("AI Employee Setup Verification - Bronze Tier")
    print("=" * 60)
    
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        # Try default location relative to script
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    if not vault_path.exists():
        print(f"\nError: Vault path does not exist: {vault_path}")
        print("Usage: python verify.py /path/to/vault")
        sys.exit(1)
    
    print(f"\nVault path: {vault_path}")
    scripts_path = vault_path.parent / 'scripts'
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Vault Structure", check_vault_structure(vault_path)),
        ("Vault Files", check_vault_files(vault_path)),
        ("Scripts", check_scripts(scripts_path)),
        ("Qwen Code", check_qwen_code()),
        ("Watcher Imports", test_watcher_import(vault_path)),
    ]
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[OK] All checks passed! Your Silver Tier setup is complete.")
        print("\nNext steps:")
        print("  1. Set up Gmail: python scripts/gmail_watcher.py <vault> --authenticate")
        print("  2. Set up WhatsApp: python scripts/whatsapp_watcher.py <vault> --setup")
        print("  3. Set up LinkedIn: python scripts/linkedin_poster.py <vault> --login")
        print("  4. Install scheduled tasks: python scripts/task_scheduler.py <vault> --install")
        print("  5. Start watchers and run orchestrator")
        sys.exit(0)
    else:
        print("\n[FAIL] Some checks failed. Please fix the issues above.")
        print("\nNote: Gmail, Playwright dependencies are optional.")
        print("      They're needed for Silver Tier features only.")
        sys.exit(1)


if __name__ == '__main__':
    main()
