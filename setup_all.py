#!/usr/bin/env python3
"""
Setup script for Microsoft Security Audit Suite
Installs dependencies for all audit tools
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def setup_sentinel_audit():
    """Set up Sentinel audit dependencies."""
    print("📊 Setting up Sentinel Audit...")
    
    sentinel_dir = Path("Sentinel Audit")
    if not sentinel_dir.exists():
        print("   ⚠️  Sentinel Audit directory not found")
        return False
    
    success, output = run_command(
        "pip install -r simple_requirements.txt",
        cwd=sentinel_dir
    )
    
    if success:
        print("   ✅ Sentinel audit dependencies installed")
        return True
    else:
        print(f"   ❌ Failed to install Sentinel dependencies: {output}")
        return False

def setup_soc_optimization():
    """Set up SOC optimization audit dependencies."""
    print("🔍 Setting up SOC Optimization...")
    
    soc_dir = Path("Sentinel SOC Optimisation Audit")
    if not soc_dir.exists():
        print("   ⚠️  SOC Optimization directory not found")
        return False
    
    success, output = run_command(
        "pip install -r soc_requirements.txt",
        cwd=soc_dir
    )
    
    if success:
        print("   ✅ SOC optimization dependencies installed")
        return True
    else:
        print(f"   ❌ Failed to install SOC dependencies: {output}")
        return False

def setup_defender_xdr():
    """Set up Defender XDR audit dependencies."""
    print("🛡️  Setting up Defender XDR Audit...")
    
    xdr_dir = Path("Defender XDR Audit")
    if not xdr_dir.exists():
        print("   ⚠️  Defender XDR Audit directory not found")
        return False
    
    success, output = run_command(
        "pip install -r xdr_requirements.txt",
        cwd=xdr_dir
    )
    
    if success:
        print("   ✅ Defender XDR audit dependencies installed")
        return True
    else:
        print(f"   ❌ Failed to install Defender XDR dependencies: {output}")
        return False

def test_installations():
    """Test that all packages are installed correctly."""
    print("🧪 Testing installations...")
    
    test_packages = [
        'azure.identity',
        'azure.mgmt.securityinsight',
        'azure.mgmt.subscription',
        'requests'
    ]
    
    all_good = True
    
    for package in test_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Not installed")
            all_good = False
    
    return all_good

def main():
    """Main setup function."""
    print("🚀 Microsoft Security Audit Suite Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"🐍 Python version: {sys.version.split()[0]} ✅")
    print("")
    
    # Upgrade pip first
    print("⬆️  Upgrading pip...")
    success, _ = run_command("python -m pip install --upgrade pip")
    if success:
        print("   ✅ pip upgraded")
    else:
        print("   ⚠️  pip upgrade failed, continuing anyway")
    print("")
    
    # Setup each component
    components_success = []
    
    components_success.append(setup_sentinel_audit())
    components_success.append(setup_soc_optimization())
    components_success.append(setup_defender_xdr())
    
    print("")
    
    # Test installations
    if test_installations():
        print("   ✅ All packages installed correctly")
    else:
        print("   ⚠️  Some packages may have installation issues")
    
    print("")
    print("=" * 50)
    
    successful_components = sum(components_success)
    total_components = len(components_success)
    
    if successful_components == total_components:
        print(f"✅ Setup completed successfully! ({successful_components}/{total_components})")
        print("")
        print("🎯 Next steps:")
        print("   1. Set up your environment variables (see README.md)")
        print("   2. Run individual audit scripts or use GitHub Actions")
        print("   3. Test connectivity with the test scripts")
    else:
        print(f"⚠️  Setup completed with issues ({successful_components}/{total_components})")
        print("")
        print("🔧 Troubleshooting:")
        print("   1. Check that you have internet connectivity")
        print("   2. Ensure pip is up to date")
        print("   3. Try installing dependencies manually")
    
    print("=" * 50)

if __name__ == "__main__":
    main()