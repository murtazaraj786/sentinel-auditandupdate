# Simple Sentinel Audit Tool

A single-script tool to audit Microsoft Sentinel and export enabled resources to CSV.

## Quick Setup

1. **Install dependencies**:
   ```powershell
   pip install -r simple_requirements.txt
   ```

2. **Set environment variables**:
   ```powershell
   # Required
   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
   $env:RESOURCE_GROUP_NAME = "your-resource-group"
   $env:WORKSPACE_NAME = "your-sentinel-workspace-name"
   
   # Choose authentication method
   $env:AUTH_MODE = "device"    # or "browser" or leave empty for Azure CLI
   ```

3. **Run the script**:
   ```powershell
   python sentinel_audit.py
   ```

## Authentication Options

| Method | Command | Description |
|--------|---------|-------------|
| **Device Code** | `$env:AUTH_MODE = "device"` | Shows a code to enter at https://microsoft.com/devicelogin |
| **Browser** | `$env:AUTH_MODE = "browser"` | Opens browser window for login |
| **Azure CLI** | `az login` first | Uses existing Azure CLI session |
| **Service Principal** | Set CLIENT_ID, CLIENT_SECRET, TENANT_ID | For automation |

## Output

The script creates two CSV files:
- `sentinel_data_connectors_YYYYMMDD_HHMMSS.csv` - Enabled data connectors
- `sentinel_analytic_rules_YYYYMMDD_HHMMSS.csv` - Enabled analytic rules

## Features

✅ **Simple**: Single file, minimal dependencies  
✅ **Fast**: Only fetches enabled resources  
✅ **CSV Export**: Timestamped files for easy tracking  
✅ **Error Handling**: Clear error messages  
✅ **Authentication**: Azure CLI or Service Principal  

## Data Connector CSV Fields

- Name
- Type
- State
- Created
- Modified

## Analytic Rules CSV Fields

- Name
- Type
- Severity
- Tactics
- Query (truncated)
- Enabled
- Created
- Modified