# Microsoft Defender for Cloud Audit Tool

This tool audits your Microsoft Defender for Cloud environment and exports security assessments, alerts, compliance data, and secure scores to CSV files.

## What it does

The Defender for Cloud audit exports the following data:

1. **Security Assessments** - Security recommendations and vulnerability assessments
2. **Security Alerts** - Active security alerts and threats detected
3. **Compliance Results** - Regulatory compliance assessments and scores
4. **Secure Score** - Overall security posture scoring and trending

## Prerequisites

- Azure subscription with Microsoft Defender for Cloud enabled
- Appropriate permissions to read security data
- Python 3.8 or higher

## Required Permissions

Your account (or service principal) needs these Azure RBAC roles:

- `Security Reader` - Read security assessments and alerts
- `Reader` - Read Azure resources and configurations
- `Security Admin` - (Optional) For more detailed security data

### Specific Azure Permissions:
- `Microsoft.Security/assessments/read`
- `Microsoft.Security/alerts/read`
- `Microsoft.Security/compliances/read`
- `Microsoft.Security/secureScores/read`
- `Microsoft.Resources/subscriptions/read`

## Quick Setup

1. **Install dependencies:**
   ```powershell
   pip install -r defender_cloud_requirements.txt
   ```

2. **Set environment variables:**
   ```powershell
   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
   $env:AZURE_TENANT_ID = "your-tenant-id"
   $env:AUTH_MODE = "device"
   ```

3. **Run the audit:**
   ```powershell
   python defender_cloud_audit.py
   ```

## Authentication Options

### Option 1: Azure CLI (Recommended for Testing)
```powershell
az login
$env:AZURE_TENANT_ID = "your-tenant-id"
python defender_cloud_audit.py
```

### Option 2: Interactive Browser
```powershell
$env:AUTH_MODE = "browser"
$env:AZURE_TENANT_ID = "your-tenant-id"
python defender_cloud_audit.py
```

### Option 3: Device Code
```powershell
$env:AUTH_MODE = "device"
$env:AZURE_TENANT_ID = "your-tenant-id"
python defender_cloud_audit.py
```

### Option 4: Service Principal (For Automation)
```powershell
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_ID = "your-app-registration-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
python defender_cloud_audit.py
```

## Output Files

The tool generates 4 CSV files with timestamps:

1. **`defender_cloud_assessments_YYYYMMDD_HHMMSS.csv`** - Security assessments and recommendations
2. **`defender_cloud_alerts_YYYYMMDD_HHMMSS.csv`** - Active security alerts
3. **`defender_cloud_compliance_YYYYMMDD_HHMMSS.csv`** - Compliance assessment results
4. **`defender_cloud_secure_score_YYYYMMDD_HHMMSS.csv`** - Security posture scores

## Key Audit Areas

### Security Assessments
- Resource vulnerabilities and misconfigurations
- Security recommendations with risk levels
- Remediation guidance and impact analysis

### Security Alerts
- Threat detections and suspicious activities
- Alert severity levels and affected resources
- Investigation steps and remediation actions

### Compliance Monitoring
- Regulatory compliance assessments (PCI-DSS, SOC, etc.)
- Policy compliance percentages
- Control failures and recommendations

### Secure Score Analytics
- Overall security posture measurement
- Score breakdown by category
- Improvement recommendations and impact

## Example Output

```
🛡️  Starting Microsoft Defender for Cloud Audit
============================================================
🔐 Using Device Code authentication
📱 You'll be prompted to visit a URL and enter a code
🏢 Customer: Contoso Corporation
🆔 Subscription: 12345678-1234-1234-1234-123456789012
🔑 Tenant ID: 87654321-4321-4321-4321-210987654321

📁 Output directory: C:\audit-reports\output

📊 Exporting Security Assessments...
✅ Security assessments exported to: defender_cloud_assessments_20241111_143022.csv

🚨 Exporting Security Alerts...
✅ Security alerts exported to: defender_cloud_alerts_20241111_143022.csv

📋 Exporting Compliance Results...
✅ Compliance results exported to: defender_cloud_compliance_20241111_143022.csv

📈 Exporting Secure Score...
✅ Secure score exported to: defender_cloud_secure_score_20241111_143022.csv

============================================================
✅ Microsoft Defender for Cloud audit completed successfully!
📊 Total items exported: 284
📁 Reports saved in: C:\audit-reports\output
============================================================
```

## Troubleshooting

### Permission Issues
```
❌ Azure error: The client does not have authorization to perform action 'Microsoft.Security/assessments/read'
```
**Solution:** Request `Security Reader` role from subscription administrator.

### Authentication Problems
```
❌ Error: AZURE_SUBSCRIPTION_ID must be set
```
**Solution:** Set required environment variables as shown in setup section.

### No Data Found
```
⚠️  No security assessments found
```
**Possible causes:**
- Defender for Cloud not enabled on subscription
- No security policies assigned
- Insufficient permissions

## Integration with Existing Audit Suite

This tool integrates seamlessly with your existing security audit framework:

```powershell
# Run all audits together
cd "Sentinel Audit"
python sentinel_audit.py

cd "../Sentinel SOC Optimisation Audit"  
python soc_optimization_audit.py

cd "../Defender XDR Audit"
python defender_xdr_audit.py

cd "../Defender for Cloud Audit"
python defender_cloud_audit.py
```

## Best Practices

1. **Regular Auditing**: Run monthly to track security posture improvements
2. **Baseline Establishment**: Create initial baseline for comparison
3. **Remediation Tracking**: Use assessment IDs to track fix implementation
4. **Compliance Monitoring**: Schedule before compliance reviews
5. **Alert Analysis**: Correlate with Sentinel and XDR data for comprehensive view

## Support

For issues specific to this audit tool:
1. Check Azure permissions and Defender for Cloud enablement
2. Verify subscription ID and authentication credentials
3. Review Azure Activity Log for API call errors
4. Test with minimal `Security Reader` permissions first