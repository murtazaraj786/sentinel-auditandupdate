#!/usr/bin/env python3
"""
Combined Sentinel and Defender XDR Report Generator
This script demonstrates how to generate a comprehensive audit report
that includes both Sentinel and Defender XDR data.
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def resolve_output_dir() -> Path:
    """Resolve the shared output directory for audit artifacts."""
    base_dir = Path(__file__).resolve().parent.parent
    env_value = os.getenv('OUTPUT_DIR')

    if env_value:
        candidate = Path(env_value)
        if not candidate.is_absolute():
            candidate = (base_dir / candidate).resolve()
    else:
        candidate = base_dir / "output"

    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def find_latest_file(output_dir: Path, pattern: str) -> Optional[str]:
    """Find the most recent file matching the pattern within output_dir."""
    files = sorted(output_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(files[0]) if files else None

def main():
    print("🔍 Combined Sentinel & Defender XDR Report Generator")
    print("=" * 60)
    
    # Required Sentinel files (these must be provided)
    script_dir = Path(__file__).resolve().parent
    generator_path = script_dir / "generate_sentinel_hld_report.py"

    output_dir = resolve_output_dir()
    print(f"📁 Scanning output directory: {output_dir}")

    required_sentinel_files = {
        "--analytic-rules": "sentinel_analytic_rules_*.csv",
        "--data-connectors": "sentinel_data_connectors_*.csv",
        "--soc-ingestion": "soc_data_ingestion_*.csv",
        "--soc-recommendations": "soc_recommendations_*.csv",
        "--soc-rule-efficiency": "soc_rule_efficiency_*.csv",
    }
    
    # Optional Defender XDR files
    optional_xdr_files = {
        "--xdr-security-alerts": "defender_xdr_security_alerts_*.csv",
        "--xdr-security-incidents": "defender_xdr_security_incidents_*.csv",
        "--xdr-attack-simulations": "defender_xdr_attack_simulations_*.csv",
        "--xdr-secure-score": "defender_xdr_secure_score_*.csv",
    }
    
    # Build command arguments
    cmd_args = [sys.executable, str(generator_path)]
    
    # Find required Sentinel files
    missing_required = []
    for arg, pattern in required_sentinel_files.items():
        found_file = find_latest_file(output_dir, pattern)

        if found_file:
            cmd_args.extend([arg, found_file])
            print(f"✅ Found {arg}: {found_file}")
        else:
            missing_required.append(arg)
            print(f"❌ Missing {arg} (pattern: {pattern})")
    
    if missing_required:
        print(f"\n❌ Cannot proceed - missing required files: {', '.join(missing_required)}")
        print("Please ensure you have run the Sentinel audits first.")
        return 1
    
    # Find optional XDR files
    xdr_files_found = 0
    for arg, pattern in optional_xdr_files.items():
        found_file = find_latest_file(output_dir, pattern)

        if found_file:
            cmd_args.extend([arg, found_file])
            print(f"✅ Found {arg}: {found_file}")
            xdr_files_found += 1
        else:
            print(f"⚠️  Optional {arg} not found (pattern: {pattern})")
    
    # Set output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = output_dir / f"combined_sentinel_xdr_audit_{timestamp}.docx"
    cmd_args.extend(["--output", str(output_filename)])
    
    print(f"\n📊 Generating report with {xdr_files_found} XDR data sources...")
    print(f"📁 Output file: {output_filename}")
    print("\n" + "=" * 60)
    
    # Run the report generator
    try:
        env = os.environ.copy()
        env['OUTPUT_DIR'] = str(output_dir)
        result = subprocess.run(cmd_args, check=True, capture_output=True, text=True, env=env)
        print("✅ Report generated successfully!")
        print(f"📄 Report saved as: {output_filename}")
        
        if result.stdout:
            print(f"Output: {result.stdout}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating report: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return 1
    except FileNotFoundError:
        print("❌ Could not find generate_sentinel_hld_report.py")
        print("Please make sure you're running this from the correct directory.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())