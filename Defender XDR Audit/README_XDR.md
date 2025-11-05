# Defender XDR Audit Tool

This tool audits your Microsoft Defender XDR (previously Microsoft 365 Defender) environment and exports security data to CSV files.

## What it does

The Defender XDR audit exports the following data:

1. **Security Alerts** - Active security alerts from Microsoft 365 Defender
2. **Security Incidents** - Security incidents and their status
3. **Attack Simulation Training** - Phishing simulation campaigns and results
4. **Microsoft Secure Score** - Current security posture score and recommendations

## Prerequisites

- Azure subscription with Microsoft 365 Defender enabled
- Appropriate permissions to read security data
- Python 3.8 or higher

## Required Permissions

Your account (or service principal) needs these Microsoft Graph permissions:

- `SecurityAlert.Read.All`
- `SecurityIncident.Read.All` 
- `SecurityActions.Read.All`
- `User.Read.All`
- `Directory.Read.All`

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r xdr_requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # For Azure CLI authentication (recommended for testing)
   export AZURE_TENANT_ID="your-tenant-id"
   
   # OR for Service Principal authentication
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"
   ```

3. **Run the audit:**
   ```bash
   python defender_xdr_audit.py
   ```

## Authentication Options

### Option 1: Azure CLI (Recommended for Testing)
```bash
az login
export AZURE_TENANT_ID="your-tenant-id"
python defender_xdr_audit.py
```

### Option 2: Interactive Browser
```bash
export AUTH_MODE=browser
export AZURE_TENANT_ID="your-tenant-id"
python defender_xdr_audit.py
```

### Option 3: Device Code
```bash
export AUTH_MODE=device
export AZURE_TENANT_ID="your-tenant-id"
python defender_xdr_audit.py
```

### Option 4: Service Principal (For Automation)
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-app-registration-id"
export AZURE_CLIENT_SECRET="your-client-secret"
python defender_xdr_audit.py
```

## Output Files

The script creates CSV files with timestamps:

- `defender_xdr_security_alerts_YYYYMMDD_HHMMSS.csv`
- `defender_xdr_security_incidents_YYYYMMDD_HHMMSS.csv`
- `defender_xdr_attack_simulations_YYYYMMDD_HHMMSS.csv`
- `defender_xdr_secure_score_YYYYMMDD_HHMMSS.csv`

## Setting up Service Principal

If you need to create a service principal for automated runs:

1. **Create App Registration:**
   ```bash
   az ad app create --display-name "Defender-XDR-Audit"
   ```

2. **Create Service Principal:**
   ```bash
   az ad sp create --id <app-id-from-step-1>
   ```

3. **Create Client Secret:**
   ```bash
   az ad app credential reset --id <app-id> --append
   ```

4. **Grant API Permissions:**
   - Go to Azure Portal → App Registrations → Your App
   - API Permissions → Add Permission → Microsoft Graph → Application Permissions
   - Add the required permissions listed above
   - Grant admin consent

## Troubleshooting

### Permission Issues
If you get "Forbidden" or "Insufficient privileges" errors:
- Ensure your account has Security Administrator or Global Administrator role
- For service principals, ensure API permissions are granted with admin consent

### No Data Found
If the script reports no data:
- Check that your tenant has Microsoft 365 Defender enabled
- Verify you have the correct tenant ID
- Some data might not be available in trial or basic licenses

### Authentication Failures
- Try `az login` first if using Azure CLI authentication
- Use `AUTH_MODE=browser` or `AUTH_MODE=device` for interactive authentication
- Verify service principal credentials if using automated authentication

## Example Output

```
🛡️  Starting Defender XDR Audit
==================================================
🔄 Using Default Azure Credential (trying Azure CLI first)
🏢 Customer: Contoso Corporation
🆔 Tenant ID: 12345678-1234-1234-1234-123456789012

📊 Exporting Security Alerts...
✅ Security alerts exported to: defender_xdr_security_alerts_20241105_143022.csv

🔍 Exporting Security Incidents...
✅ Security incidents exported to: defender_xdr_security_incidents_20241105_143022.csv

🎯 Exporting Attack Simulation Trainings...
✅ Attack simulations exported to: defender_xdr_attack_simulations_20241105_143022.csv

📈 Exporting Secure Score Data...
✅ Secure score exported to: defender_xdr_secure_score_20241105_143022.csv

==================================================
✅ Defender XDR audit completed successfully!
📊 Total items exported: 156
📁 Files created in current directory
==================================================
```