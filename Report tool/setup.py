#!/usr/bin/env python3
"""
Setup script for Sentinel HLD Report Generator
Installs required dependencies and validates the environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_packages():
    """Install required packages from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def validate_imports():
    """Validate that all required modules can be imported"""
    print("\n🔍 Validating imports...")
    
    required_modules = [
        ("pandas", "pd"),
        ("docx", "Document"),
        ("openpyxl", None)  # Used by pandas for Excel support
    ]
    
    failed_imports = []
    
    for module, attr in required_modules:
        try:
            if attr:
                exec(f"from {module} import {attr}")
                print(f"✅ {module}.{attr}")
            else:
                exec(f"import {module}")
                print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version >= min_version:
        print(f"✅ Python {'.'.join(map(str, current_version))} (minimum {'.'.join(map(str, min_version))} required)")
        return True
    else:
        print(f"❌ Python {'.'.join(map(str, current_version))} is too old. Minimum {'.'.join(map(str, min_version))} required")
        return False

def create_sample_command():
    """Create a sample command file for easy testing"""
    sample_cmd = Path(__file__).parent / "sample_command.bat"
    
    sample_content = '''@echo off
REM Sample command to generate a Sentinel HLD report
REM Update the CSV file paths to match your actual files

python generate_sentinel_hld_report.py ^
    --analytic-rules "../Sentinel Audit/sentinel_analytic_rules_20241105_103210.csv" ^
    --data-connectors "../Sentinel Audit/sentinel_data_connectors_20241105_103210.csv" ^
    --soc-ingestion "../Sentinel SOC Optimisation Audit/soc_data_ingestion_20241105_105531.csv" ^
    --soc-recommendations "../Sentinel SOC Optimisation Audit/soc_recommendations_20241105_105531.csv" ^
    --soc-rule-efficiency "../Sentinel SOC Optimisation Audit/soc_rule_efficiency_20241105_105531.csv" ^
    --customer-name "Just Group" ^
    --output "JustGroup_Sentinel_HLD_Report.docx" ^
    --preview-rows 10

echo.
echo Report generation complete!
echo Check for JustGroup_Sentinel_HLD_Report.docx in the current directory.
pause
'''
    
    try:
        sample_cmd.write_text(sample_content, encoding='utf-8')
        print(f"✅ Created sample command file: {sample_cmd}")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample command: {e}")
        return False

def create_sample_powershell():
    """Create a sample PowerShell command for cross-platform support"""
    sample_ps1 = Path(__file__).parent / "sample_command.ps1"
    
    sample_content = '''# Sample PowerShell command to generate a Sentinel HLD report
# Update the CSV file paths to match your actual files

$ErrorActionPreference = "Stop"

Write-Host "🚀 Generating Sentinel HLD Report..." -ForegroundColor Green

python generate_sentinel_hld_report.py `
    --analytic-rules "../Sentinel Audit/sentinel_analytic_rules_20241105_103210.csv" `
    --data-connectors "../Sentinel Audit/sentinel_data_connectors_20241105_103210.csv" `
    --soc-ingestion "../Sentinel SOC Optimisation Audit/soc_data_ingestion_20241105_105531.csv" `
    --soc-recommendations "../Sentinel SOC Optimisation Audit/soc_recommendations_20241105_105531.csv" `
    --soc-rule-efficiency "../Sentinel SOC Optimisation Audit/soc_rule_efficiency_20241105_105531.csv" `
    --customer-name "Just Group" `
    --output "JustGroup_Sentinel_HLD_Report.docx" `
    --preview-rows 10

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Report generation complete!" -ForegroundColor Green
    Write-Host "📄 Check for JustGroup_Sentinel_HLD_Report.docx in the current directory." -ForegroundColor Cyan
} else {
    Write-Host "❌ Report generation failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Read-Host "Press Enter to continue..."
'''
    
    try:
        sample_ps1.write_text(sample_content, encoding='utf-8')
        print(f"✅ Created sample PowerShell script: {sample_ps1}")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample PowerShell script: {e}")
        return False

def main():
    """Main setup function"""
    print("🎯 Sentinel HLD Report Generator Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version too old")
        return False
    
    # Install packages
    if not install_packages():
        print("\n❌ Setup failed: Could not install required packages")
        return False
    
    # Validate imports
    if not validate_imports():
        print("\n❌ Setup failed: Import validation failed")
        print("💡 Try running: pip install --upgrade pandas python-docx openpyxl")
        return False
    
    # Create sample command files
    print("\n📝 Creating sample command files...")
    create_sample_command()
    create_sample_powershell()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Run the audit scripts to generate CSV files")
    print("2. Update the sample command files with your CSV file paths")
    print("3. Run: python generate_sentinel_hld_report.py [options]")
    print("\n📁 Sample commands created:")
    print("   - sample_command.bat (Windows)")
    print("   - sample_command.ps1 (PowerShell)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)