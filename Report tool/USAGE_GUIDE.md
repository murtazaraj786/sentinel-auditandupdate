# 🛡️ Combined Sentinel & Defender XDR Report Generation Guide

## Quick Start

The report generator has been enhanced to support both Microsoft Sentinel and Defender XDR data sources. You can now create comprehensive security audit reports that include data from both platforms.

## ✅ What's New

1. **Enhanced report generator** - `generate_sentinel_hld_report.py` now supports XDR data
2. **Auto-detection** - Automatically finds XDR CSV files
3. **Combined runner** - `run_combined_report.py` for easy execution
4. **Comprehensive reporting** - Single document with both Sentinel and XDR insights

## 🚀 Usage Options

### Option 1: Automated (Recommended)
```powershell
# Navigate to the report folder
cd "Create Docx from output of auditfiles"

# Run the automated script
python run_combined_report.py
```

This script will:
- Auto-detect all required Sentinel files
- Auto-detect any available XDR files  
- Generate a comprehensive report
- Use timestamp-based filename

### Option 2: Manual with XDR Data
```powershell
python generate_sentinel_hld_report.py \
    --analytic-rules "../Sentinel Audit/sentinel_analytic_rules_20241105_103210.csv" \
    --data-connectors "../Sentinel Audit/sentinel_data_connectors_20241105_103210.csv" \
    --soc-ingestion "../Sentinel SOC Optimisation Audit/soc_data_ingestion_20241105_105531.csv" \
    --soc-recommendations "../Sentinel SOC Optimisation Audit/soc_recommendations_20241105_105531.csv" \
    --soc-rule-efficiency "../Sentinel SOC Optimisation Audit/soc_rule_efficiency_20241105_105531.csv" \
    --xdr-security-alerts "../Defender XDR Audit/defender_xdr_security_alerts_20241105_140322.csv" \
    --xdr-security-incidents "../Defender XDR Audit/defender_xdr_security_incidents_20241105_140322.csv" \
    --xdr-attack-simulations "../Defender XDR Audit/defender_xdr_attack_simulations_20241105_140322.csv" \
    --xdr-secure-score "../Defender XDR Audit/defender_xdr_secure_score_20241105_140322.csv" \
    --customer-name "Your Customer" \
    --output "Customer_Combined_Security_Audit.docx"
```

### Option 3: Sentinel Only (Original Functionality)
```powershell
python generate_sentinel_hld_report.py \
    --analytic-rules "../Sentinel Audit/sentinel_analytic_rules_20241105_103210.csv" \
    --data-connectors "../Sentinel Audit/sentinel_data_connectors_20241105_103210.csv" \
    --soc-ingestion "../Sentinel SOC Optimisation Audit/soc_data_ingestion_20241105_105531.csv" \
    --soc-recommendations "../Sentinel SOC Optimisation Audit/soc_recommendations_20241105_105531.csv" \
    --soc-rule-efficiency "../Sentinel SOC Optimisation Audit/soc_rule_efficiency_20241105_105531.csv" \
    --customer-name "Your Customer" \
    --output "Customer_Sentinel_Audit.docx"
```

## 📊 Report Sections

### Core Sentinel Sections (Always Included)
1. **Executive Summary**
2. **Data Connectors**  
3. **Analytic Rules**
4. **SOC Recommendations**
5. **SOC Rule Efficiency**
6. **SOC Data Ingestion**

### Additional XDR Sections (When Data Available)
7. **Defender XDR Security Alerts**
8. **Defender XDR Security Incidents** 
9. **Defender XDR Attack Simulations**
10. **Defender XDR Secure Score**

## 🔍 Auto-Detection Features

The system automatically looks for files in these locations:

**Sentinel Files:**
- `../Sentinel Audit/sentinel_*.csv`
- `../Sentinel SOC Optimisation Audit/soc_*.csv`

**XDR Files:**
- `../Defender XDR Audit/defender_xdr_*.csv`

**Customer Info:**
- Any metadata CSV files containing `customer_name` column

## ⚠️ Prerequisites

1. **Run the audits first:**
   - Sentinel audit (required)
   - SOC optimization audit (required)  
   - Defender XDR audit (optional)

2. **Install dependencies:**
   ```powershell
   pip install pandas python-docx openpyxl
   ```

## 💡 Tips

- **XDR data is optional** - The report works with just Sentinel data
- **File auto-detection** - No need to specify exact filenames if using standard locations
- **Customer name detection** - Automatically extracted from audit metadata
- **Timestamped outputs** - Each report has a unique filename

## 🎯 Example Workflow

1. Run Sentinel audit: `python ../Sentinel Audit/sentinel_audit.py`
2. Run SOC audit: `python "../Sentinel SOC Optimisation Audit/soc_optimization_audit.py"`
3. Run XDR audit: `python "../Defender XDR Audit/defender_xdr_audit.py"` (optional)
4. Generate report: `python run_combined_report.py`

The final report will be a professional Word document combining insights from all available data sources!