# Microsoft Sentinel Audit and Update Tool

A Python tool for auditing Microsoft Sentinel data connectors and analytic rules, checking for available updates, and deploying those updates.

## Features

- **Data Connector Auditing**: List all data connectors in your Sentinel workspace and check for available updates
- **Analytic Rules Auditing**: 
  - List all installed analytic rules
  - View rule details including severity, status, and tactics
  - Check for available updates
  - Statistics by severity and enabled/disabled status
- **Deployment Capabilities**: Deploy updates to analytic rules and data connectors
- **Detailed Reporting**: Formatted console output and logging for audit trails

## Prerequisites

- Python 3.8 or higher
- Azure subscription with Microsoft Sentinel workspace
- Azure credentials with appropriate permissions:
  - Microsoft Sentinel Contributor (or Reader for audit-only)
  - Access to the resource group containing your Sentinel workspace

## Installation

1. Clone or download this repository

2. Install required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```powershell
   Copy-Item .env.example .env
   ```

4. Edit `.env` and fill in your Azure details:
   ```
   AZURE_SUBSCRIPTION_ID=your-subscription-id
   RESOURCE_GROUP_NAME=your-resource-group
   WORKSPACE_NAME=your-sentinel-workspace-name
   ```

## Authentication

The tool supports two authentication methods:

### 1. DefaultAzureCredential (Recommended)
Uses Azure CLI, Managed Identity, or other default credential chain. Simply ensure you're logged in:
```powershell
az login
```

### 2. Service Principal (Optional)
Add these to your `.env` file:
```
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

## Usage

### Basic Audit
Run the main audit tool to see all data connectors and analytic rules:
```powershell
python main.py
```

### Python Module Usage

You can also use the individual modules programmatically:

```python
from config import SentinelConfig
from auth import get_azure_credential
from analytic_rules import AnalyticRuleAuditor
from data_connectors import DataConnectorAuditor
from deployment import SentinelDeployment

# Initialize
config = SentinelConfig.from_env()
credential = get_azure_credential(config)

# Audit analytic rules
rule_auditor = AnalyticRuleAuditor(credential, config)
rules = rule_auditor.list_analytic_rules()

# Audit data connectors
connector_auditor = DataConnectorAuditor(credential, config)
connectors = connector_auditor.list_data_connectors()

# Deploy updates
deployer = SentinelDeployment(credential, config)
result = deployer.enable_analytic_rule('rule-name')
```

## Project Structure

```
sentinel-auditandupdate/
├── main.py                 # Main entry point
├── config.py               # Configuration management
├── auth.py                 # Azure authentication
├── data_connectors.py      # Data connector auditing
├── analytic_rules.py       # Analytic rule auditing
├── deployment.py           # Deployment functionality
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Output

The tool provides:
- **Console Output**: Formatted tables showing your Sentinel resources
- **Log File**: Detailed logs saved to `sentinel_audit.log`
- **Statistics**: Counts and breakdowns by status, severity, and type

### Example Output

```
================================================================================
  DATA CONNECTORS AUDIT
================================================================================

╒══════════════════════════╤════════╤═══════════════╕
│ Name                     │ Kind   │ Type          │
╞══════════════════════════╪════════╪═══════════════╡
│ AzureActiveDirectory     │ ...    │ DataConnector │
│ MicrosoftDefenderATP     │ ...    │ DataConnector │
╘══════════════════════════╧════════╧═══════════════╛

Total data connectors: 2

================================================================================
  ANALYTIC RULES AUDIT
================================================================================

╒═══════════════════════════════╤═══════════╤══════════╤══════════╤═══════════╕
│ Display Name                  │ Kind      │ Severity │ Status   │ Tactics   │
╞═══════════════════════════════╪═══════════╪══════════╪══════════╪═══════════╡
│ Suspicious Login Activity     │ Scheduled │ High     │ Enabled  │ Initial.. │
│ Malware Detection             │ Scheduled │ Medium   │ Enabled  │ Execution │
╘═══════════════════════════════╧═══════════╧══════════╧══════════╧═══════════╛

Total analytic rules: 2
  - Enabled: 2
  - Disabled: 0
```

## Security Best Practices

- Never commit `.env` file or credentials to version control
- Use Azure Managed Identity in production environments
- Follow the principle of least privilege for Azure permissions
- Regularly rotate service principal credentials if used
- Review audit logs regularly

## Troubleshooting

### Authentication Errors
- Ensure you're logged in: `az login`
- Verify your credentials have proper permissions
- Check that subscription ID, resource group, and workspace name are correct

### Import Errors
- Run: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

### No Resources Found
- Verify workspace name and resource group are correct
- Ensure your account has read access to the Sentinel workspace

## Future Enhancements

- Integration with Sentinel Content Hub API for actual update detection
- Automated deployment workflows
- Export to CSV/JSON for reporting
- Comparison against baseline configurations
- Solution package version tracking

## License

This project is provided as-is for use with Microsoft Sentinel.

## Contributing

Feel free to submit issues and enhancement requests!
