#!/usr/bin/env python3
"""
Comprehensive Security Audit Launcher
Includes new Defender for Cloud and Azure WAF audits
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print the audit suite banner."""
    print("🛡️" + "=" * 80)
    print("🛡️  MICROSOFT SECURITY AUDIT SUITE - EXTENDED EDITION")
    print("🛡️" + "=" * 80)
    print("🎯 Sentinel Audit        - Data connectors & analytic rules")
    print("📊 SOC Optimization      - Rule efficiency & cost analysis") 
    print("🛡️ Defender XDR Audit    - M365 security posture & incidents")
    print("🔐 Defender for Cloud    - Security assessments & compliance")
    print("🔥 Azure WAF Audit       - Web application firewall policies")
    print("🛡️" + "=" * 80)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['AZURE_SUBSCRIPTION_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        print("\n💡 Set environment variables:")
        print('   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"')
        print('   $env:AZURE_TENANT_ID = "your-tenant-id"')
        print('   $env:RESOURCE_GROUP_NAME = "your-resource-group"')
        print('   $env:WORKSPACE_NAME = "your-sentinel-workspace-name"')
        print('   $env:AUTH_MODE = "device"  # or browser, cli')
        return False
    
    return True

def run_audit(script_path, description, working_dir=None):
    """Run an individual audit script."""
    print(f"\n🚀 Starting {description}...")
    print("=" * 60)
    
    try:
        if working_dir:
            original_dir = os.getcwd()
            os.chdir(working_dir)
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True)
        
        if working_dir:
            os.chdir(original_dir)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        if working_dir:
            os.chdir(original_dir)
        return False

def install_requirements(requirements_file, description):
    """Install requirements for an audit tool."""
    print(f"📦 Installing requirements for {description}...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Requirements installed for {description}")
        else:
            print(f"⚠️  Warning: Failed to install some requirements for {description}")
            print(f"   Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error installing requirements for {description}: {e}")
        return False

def main():
    """Main function with interactive menu."""
    print_banner()
    
    if not check_environment():
        sys.exit(1)
    
    print("\n🔐 AUDIT OPTIONS:")
    print("=" * 60)
    print("1. Sentinel Basic Audit (Data connectors & rules)")
    print("2. SOC Optimization Audit (Efficiency & costs)")
    print("3. Defender XDR Audit (M365 security posture)")
    print("4. Defender for Cloud Audit (Security assessments)")
    print("5. Azure WAF Audit (Web application firewalls)")
    print("6. Run ALL audits (Complete security assessment)")
    print("7. Install all requirements")
    print("8. Exit")
    
    while True:
        try:
            choice = input("\nChoose audit option (1-8): ").strip()
            
            if choice == '1':
                # Sentinel Basic Audit
                working_dir = "Sentinel Audit"
                if os.path.exists(working_dir):
                    run_audit("sentinel_audit.py", "Sentinel Basic Audit", working_dir)
                else:
                    print(f"❌ Directory '{working_dir}' not found")
                break
                
            elif choice == '2':
                # SOC Optimization Audit
                working_dir = "Sentinel SOC Optimisation Audit"
                if os.path.exists(working_dir):
                    run_audit("soc_optimization_audit.py", "SOC Optimization Audit", working_dir)
                else:
                    print(f"❌ Directory '{working_dir}' not found")
                break
                
            elif choice == '3':
                # Defender XDR Audit
                working_dir = "Defender XDR Audit"
                if os.path.exists(working_dir):
                    run_audit("defender_xdr_audit.py", "Defender XDR Audit", working_dir)
                else:
                    print(f"❌ Directory '{working_dir}' not found")
                break
                
            elif choice == '4':
                # Defender for Cloud Audit
                working_dir = "Defender for Cloud Audit"
                if os.path.exists(working_dir):
                    run_audit("defender_cloud_audit.py", "Defender for Cloud Audit", working_dir)
                else:
                    print(f"❌ Directory '{working_dir}' not found")
                break
                
            elif choice == '5':
                # Azure WAF Audit
                working_dir = "Azure WAF Audit"
                if os.path.exists(working_dir):
                    run_audit("azure_waf_audit.py", "Azure WAF Audit", working_dir)
                else:
                    print(f"❌ Directory '{working_dir}' not found")
                break
                
            elif choice == '6':
                # Run ALL audits
                print("\n🚀 Starting COMPREHENSIVE Security Audit...")
                print("=" * 80)
                
                audits = [
                    ("Sentinel Audit", "sentinel_audit.py", "Sentinel Basic Audit"),
                    ("Sentinel SOC Optimisation Audit", "soc_optimization_audit.py", "SOC Optimization Audit"),
                    ("Defender XDR Audit", "defender_xdr_audit.py", "Defender XDR Audit"),
                    ("Defender for Cloud Audit", "defender_cloud_audit.py", "Defender for Cloud Audit"),
                    ("Azure WAF Audit", "azure_waf_audit.py", "Azure WAF Audit")
                ]
                
                successful_audits = 0
                total_audits = len(audits)
                
                for working_dir, script, description in audits:
                    if os.path.exists(working_dir):
                        if run_audit(script, description, working_dir):
                            successful_audits += 1
                        time.sleep(2)  # Brief pause between audits
                    else:
                        print(f"⚠️  Skipping {description} - directory '{working_dir}' not found")
                
                print("\n" + "=" * 80)
                print("🎯 COMPREHENSIVE AUDIT SUMMARY")
                print("=" * 80)
                print(f"✅ Successful audits: {successful_audits}/{total_audits}")
                print(f"📁 Check output folder for all generated reports")
                print("=" * 80)
                break
                
            elif choice == '7':
                # Install all requirements
                print("\n📦 Installing all requirements...")
                print("=" * 60)
                
                requirements = [
                    ("Sentinel Audit/simple_requirements.txt", "Sentinel Basic Audit"),
                    ("Sentinel SOC Optimisation Audit/soc_requirements.txt", "SOC Optimization"),
                    ("Defender XDR Audit/xdr_requirements.txt", "Defender XDR"),
                    ("Defender for Cloud Audit/defender_cloud_requirements.txt", "Defender for Cloud"),
                    ("Azure WAF Audit/waf_requirements.txt", "Azure WAF")
                ]
                
                for req_file, description in requirements:
                    if os.path.exists(req_file):
                        install_requirements(req_file, description)
                    else:
                        print(f"⚠️  Requirements file not found: {req_file}")
                
                print("\n✅ Requirements installation completed!")
                break
                
            elif choice == '8':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()