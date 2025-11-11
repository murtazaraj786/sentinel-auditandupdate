#!/usr/bin/env python3
"""
Setup script for Microsoft Security Audit Suite
Installs dependencies for all audit tools
"""

import os
import subprocess
import sys
from pathlib import Path

ENV_VARIABLES = [
    ("AZURE_TENANT_ID", "Azure AD tenant ID (GUID)", True),
    ("AZURE_SUBSCRIPTION_ID", "Subscription ID containing Microsoft Sentinel", True),
    ("RESOURCE_GROUP_NAME", "Resource group name for the Sentinel workspace", True),
    ("WORKSPACE_NAME", "Log Analytics workspace name (Sentinel)", True),
    ("AUTH_MODE", "Authentication preference (device/browser/cli/auto)", False),
    ("AZURE_CLIENT_ID", "Optional Azure app (client) ID for Microsoft Graph", False),
]

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


def _prompt_for_value(key: str, description: str, required: bool) -> str:
    """Prompt for an environment variable with optional default."""
    existing = os.environ.get(key, "").strip()
    while True:
        prompt = f"   {key} ({description})"
        if existing:
            prompt += f" [{existing}]"
        prompt += ": "
        try:
            value = input(prompt).strip()
        except KeyboardInterrupt:
            print("\n   ❌ Input cancelled by user")
            sys.exit(1)

        if not value:
            value = existing

        if required and not value:
            print("   ⚠️  This value is required. Please provide a value.")
            continue

        return value


def write_env_file(env_values):
    """Persist environment variables to a .env file."""
    env_path = Path(".env")
    if env_path.exists():
        choice = input(".env already exists. Overwrite? [y/N]: ").strip().lower()
        if choice not in {"y", "yes"}:
            print("   ⚠️  Skipped writing .env file.")
            return

    lines = [
        "# Environment configuration for Microsoft Security Audit Suite",
        "# Update these values as needed. Blank entries remain commented.",
    ]

    for key, _, _ in ENV_VARIABLES:
        value = env_values.get(key, "").strip()
        if value:
            lines.append(f"{key}={value}")
        else:
            lines.append(f"#{key}=")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"   ✅ Saved environment values to {env_path} (git-ignored)")


def collect_environment_variables():
    """Interactively collect and optionally persist environment variables."""
    print("🧾 Environment configuration wizard")
    print("   Provide values for the Azure settings used by the audit tools.")

    env_values = {}
    for key, description, required in ENV_VARIABLES:
        env_values[key] = _prompt_for_value(key, description, required)

    for key, value in env_values.items():
        if value:
            os.environ[key] = value

    print("\n   Summary of provided values:")
    for key, value in env_values.items():
        display_value = value if value else "(blank)"
        print(f"   - {key}: {display_value}")

    save_choice = input("\nSave these values to a .env file for reuse? [Y/n]: ").strip().lower()
    if save_choice in {"", "y", "yes"}:
        write_env_file(env_values)
    else:
        print("   ⚠️  Values not written to disk. Remember to set them before running audits.")

    print("\n   📌 Tip: load the .env file in PowerShell with `Get-Content .env | foreach{ if ($_ -notmatch '^#') { $name,$value = $_.Split('='); if($value){ Set-Item Env:$name $value } } }`")

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

    try:
        run_env_wizard = input("Would you like to fill out the environment configuration now? [Y/n]: ").strip().lower()
    except KeyboardInterrupt:
        print("\n⚠️  Environment configuration skipped by user")
        run_env_wizard = "n"

    if run_env_wizard in {"", "y", "yes"}:
        print("")
        collect_environment_variables()
    else:
        print("   ⚠️  Skipped environment configuration wizard. Remember to set variables manually.")

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