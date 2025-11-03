# Microsoft Sentinel Audit and Update Tool

A Python tool for auditing Microsoft Sentinel data connectors and analytic rules, checking for available updates, and deploying those updates with an automated workflow.

## Features

- **Data Connector Auditing**: List all data connectors in your Sentinel workspace and check for available updates
- **Analytic Rules Auditing**:
  - List all installed analytic rules
  - View rule details including severity, status, and tactics
  - Check for available updates from templates
  - Statistics by severity and enabled/disabled status
- **Automated Update Detection**: Scan for updates to solutions, rules, and connectors
- **Change Preview**: View detailed comparisons between current and updated versions
- **Approval-Based Deployment**:
  - Interactive mode to review and approve each update individually
  - Batch mode to deploy all updates at once
  - Auto-approve mode for automated workflows
- **CSV Export**: Export audit results, detected updates, and deployment reports to CSV format
- **Deployment Reports**: Generate detailed reports (text and CSV) of deployment activities
- **Detailed Reporting**: Formatted console output and logging for audit trails## Prerequisites

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

### 1. Basic Audit (View Only)

Run a basic audit to view all data connectors and analytic rules without deploying updates:

```powershell
python main.py
```

### 2. Update Detection and Deployment Workflow

Run the automated workflow to detect updates and deploy them interactively:

```powershell
python main.py --workflow
```

This will:
1. Scan for available updates to solutions, rules, and connectors
2. Display all detected updates with details
3. Offer deployment options:
   - Deploy all updates at once
   - Review and deploy individual updates
   - Skip deployment (audit only)

### 3. Auto-Deploy All Updates

Automatically deploy all detected updates without prompting:

```powershell
python main.py --workflow --auto
```

**⚠️ Warning**: Use auto-deploy with caution in production environments!

### 4. Export to CSV

Export audit results and updates to CSV files for reporting:

```powershell
# Audit mode - prompts for CSV export after displaying results
python main.py

# Workflow mode - prompts for CSV export of detected updates
python main.py --workflow

# Disable CSV export prompts
python main.py --no-csv
python main.py --workflow --no-csv
```

CSV files include:
- **Audit Mode**: 
  - `analytic_rules_YYYYMMDD_HHMMSS.csv` - All installed analytic rules
  - `data_connectors_YYYYMMDD_HHMMSS.csv` - All data connectors
- **Workflow Mode**:
  - `solution_updates_YYYYMMDD_HHMMSS.csv` - Available solution updates
  - `rule_updates_YYYYMMDD_HHMMSS.csv` - Available rule updates
  - `deployment_results_YYYYMMDD_HHMMSS.csv` - Deployment outcomes

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
├── main.py                 # Main entry point with workflow support
├── config.py               # Configuration management
├── auth.py                 # Azure authentication
├── data_connectors.py      # Data connector auditing
├── analytic_rules.py       # Analytic rule auditing
├── deployment.py           # Deployment functionality
├── content_hub.py          # Content Hub and solution management
├── workflow.py             # Automated update detection and deployment workflow
├── utils.py                # Comparison and analysis utilities
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

### Example Output - Update Workflow

```
================================================================================
  UPDATE DETECTION AND DEPLOYMENT WORKFLOW
================================================================================

🔍 Scanning for available updates...

================================================================================
  DETECTED UPDATES
================================================================================

📦 SOLUTION UPDATES AVAILABLE:
--------------------------------------------------------------------------------
╒═══════════════════════════╤═════════════════╤═══════════════════╤════════════╕
│ Solution Name             │ Current Version │ Available Version │ Publisher  │
╞═══════════════════════════╪═════════════════╪═══════════════════╪════════════╡
│ Azure Active Directory    │ 2.0.1           │ 2.0.5             │ Microsoft  │
│ Microsoft Defender XDR    │ 1.5.0           │ 1.6.2             │ Microsoft  │
╘═══════════════════════════╧═════════════════╧═══════════════════╧════════════╛

Total solution updates: 2

📋 ANALYTIC RULE UPDATES AVAILABLE:
--------------------------------------------------------------------------------
╒═════════════════════════════════╤══════════════════╤══════════════════╤═══════════════╕
│ Rule Name                       │ Current Severity │ Template Severity│ Update Type   │
╞═════════════════════════════════╪══════════════════╪══════════════════╪═══════════════╡
│ Suspicious Sign-in Activity     │ Medium           │ High             │ Template Avai │
│ Malware Detection Alert         │ High             │ High             │ Template Avai │
╘═════════════════════════════════╧══════════════════╧══════════════════╧═══════════════╛

Total rule updates: 2

================================================================================
  DEPLOYMENT OPTIONS
================================================================================
1. Deploy all updates
2. Review and deploy individual updates
3. Skip deployment (audit only)
```

## Workflow Features

### Update Detection
The tool automatically detects:
- **Solution Updates**: Compares installed solution versions with available versions in Content Hub
- **Rule Updates**: Matches installed rules with templates to identify updates
- **Property Changes**: Analyzes what has changed (severity, query, tactics, etc.)

### Change Preview
Before deploying, view:
- Version differences
- Changed properties
- Risk assessment (Low/Medium/High)
- Query differences for analytic rules
- Impact analysis for severity changes

### Deployment Modes

#### Interactive Mode
Review each update individually and approve/reject:
```powershell
python main.py --workflow
# Choose option 2 when prompted
```

#### Batch Mode
Deploy all updates at once with a single approval:
```powershell
python main.py --workflow
# Choose option 1 when prompted
```

#### Auto-Deploy Mode
Automatically deploy all updates without prompting (for automation):
```powershell
python main.py --workflow --auto
```

### Deployment Reports
After deployment, the tool generates:
- Console summary of results
- Detailed text report saved to file (`deployment_report_YYYYMMDD_HHMMSS.txt`)
- Success/failure statistics
- Individual deployment outcomes

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

## GitHub Actions Integration

This tool can be automated using GitHub Actions for scheduled audits and controlled deployments.

**Quick Setup**:
1. Create Azure Service Principal: See **[SETUP_AZURE_SECRETS.md](SETUP_AZURE_SECRETS.md)** for step-by-step instructions
2. Add 4 secrets to GitHub: `AZURE_CREDENTIALS`, `AZURE_SUBSCRIPTION_ID`, `RESOURCE_GROUP_NAME`, `WORKSPACE_NAME`
3. Workflows will run automatically!

**Available Workflows**:
- `sentinel-audit.yml`: Scheduled audits (daily at 9 AM UTC) with optional auto-deployment
- `sentinel-deploy-updates.yml`: Manual deployment with environment protection

**Key Features**:
- ✅ Automated daily/weekly audits
- ✅ CSV reports as workflow artifacts
- ✅ Azure Service Principal authentication (simple setup)
- ✅ Environment protection for production deployments
- ✅ Slack/email notifications (optional)

For advanced OIDC setup, see **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)**.

## Future Enhancements

- Advanced filtering for selective deployments
- Rollback capabilities for failed deployments
- Custom update approval workflows
- Integration with ITSM tools for change management

## License

This project is provided as-is for use with Microsoft Sentinel.

## Contributing

Feel free to submit issues and enhancement requests!
