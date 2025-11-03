# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions to automate Microsoft Sentinel audits and deployments.

## 📋 Prerequisites

1. GitHub repository with this code
2. Azure Sentinel workspace
3. Azure credentials with appropriate permissions

## 🔐 Authentication Options

### Option 1: Azure OIDC (Recommended)

OIDC provides keyless authentication without storing credentials in GitHub.

#### Setup Steps:

1. **Register Azure App**:
   ```bash
   az ad app create --display-name "github-sentinel-audit"
   ```

2. **Create Service Principal**:
   ```bash
   APP_ID=$(az ad app list --display-name "github-sentinel-audit" --query [0].appId -o tsv)
   az ad sp create --id $APP_ID
   ```

3. **Create Federated Credential**:
   ```bash
   OBJECT_ID=$(az ad app list --display-name "github-sentinel-audit" --query [0].id -o tsv)
   
   cat <<EOF > credential.json
   {
     "name": "github-actions",
     "issuer": "https://token.actions.githubusercontent.com",
     "subject": "repo:YOUR_GITHUB_ORG/sentinel-auditandupdate:ref:refs/heads/main",
     "audiences": ["api://AzureADTokenExchange"]
   }
   EOF
   
   az ad app federated-credential create --id $OBJECT_ID --parameters credential.json
   ```

4. **Assign Azure Permissions**:
   ```bash
   SUBSCRIPTION_ID="your-subscription-id"
   RESOURCE_GROUP="your-resource-group"
   SP_OBJECT_ID=$(az ad sp list --display-name "github-sentinel-audit" --query [0].id -o tsv)
   
   # Reader for audits
   az role assignment create \
     --assignee $SP_OBJECT_ID \
     --role "Reader" \
     --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"
   
   # Contributor for deployments
   az role assignment create \
     --assignee $SP_OBJECT_ID \
     --role "Microsoft Sentinel Contributor" \
     --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"
   ```

5. **Add GitHub Secrets**:
   Go to your repository → Settings → Secrets and variables → Actions → New repository secret:
   
   - `AZURE_CLIENT_ID`: Application (client) ID
   - `AZURE_TENANT_ID`: Directory (tenant) ID
   - `AZURE_SUBSCRIPTION_ID`: Your subscription ID
   - `RESOURCE_GROUP_NAME`: Your resource group name
   - `WORKSPACE_NAME`: Your Sentinel workspace name

### Option 2: Service Principal with Secret

1. **Create Service Principal**:
   ```bash
   az ad sp create-for-rbac --name "github-sentinel-audit" \
     --role "Microsoft Sentinel Contributor" \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
     --sdk-auth
   ```

2. **Copy the JSON output** and add it as `AZURE_CREDENTIALS` secret in GitHub

3. **Add additional secrets**:
   - `AZURE_SUBSCRIPTION_ID`
   - `RESOURCE_GROUP_NAME`
   - `WORKSPACE_NAME`

4. **Update workflow** to use Service Principal authentication (uncomment the alternative login step)

## 🚀 Workflows

### 1. Sentinel Audit and Update (`sentinel-audit.yml`)

**Triggers**:
- Scheduled: Daily at 9 AM UTC
- Manual: Via workflow dispatch
- (Optional) On push to main branch

**Capabilities**:
- Audit Sentinel workspace for updates
- Auto-deploy updates (when enabled)
- Export CSV reports as artifacts
- Create GitHub issues when updates are found

**Manual Trigger Options**:
- `auto_deploy`: Automatically deploy all updates (default: false)
- `export_csv`: Export results to CSV (default: true)

### 2. Deploy Sentinel Updates (`sentinel-deploy-updates.yml`)

**Triggers**:
- Manual only (workflow dispatch)

**Capabilities**:
- Controlled deployment with environment approval
- Choose deployment mode (auto/interactive)
- Select update types (all/analytic-rules/data-connectors/solutions)
- Generate deployment reports

**Manual Trigger Options**:
- `deployment_mode`: auto | interactive
- `update_type`: all | analytic-rules | data-connectors | solutions

## 🔧 Configuration

### Schedule Customization

Edit the cron schedule in `sentinel-audit.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
  # - cron: '0 9 * * 1'  # Weekly on Mondays at 9 AM UTC
  # - cron: '0 9 1 * *'  # Monthly on the 1st at 9 AM UTC
```

### Environment Protection

For production deployments, set up environment protection:

1. Go to repository → Settings → Environments
2. Create environment named `production`
3. Add protection rules:
   - Required reviewers (select team members)
   - Wait timer (optional delay before deployment)
   - Deployment branches (restrict to main branch)

### Notifications

#### Slack Notifications

Add to workflow after deployment step:

```yaml
- name: Slack Notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Sentinel Audit Complete",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Status*: ${{ job.status }}\n*Run*: #${{ github.run_number }}"
            }
          }
        ]
      }
```

#### Email Notifications

Add to workflow:

```yaml
- name: Send Email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Sentinel Updates Available
    to: security-team@company.com
    from: GitHub Actions
    body: Updates detected in Sentinel workspace. Check workflow run ${{ github.run_number }}
```

## 📊 Viewing Results

### Artifacts

After each workflow run:
1. Go to Actions → Select workflow run
2. Scroll to "Artifacts" section
3. Download CSV reports and deployment logs

### Job Summaries

GitHub Actions automatically creates a summary for each run with:
- Workflow details
- Auto-deploy status
- Links to artifacts

## 🔍 Troubleshooting

### Authentication Fails

**OIDC Issues**:
- Verify federated credential subject matches: `repo:OWNER/REPO:ref:refs/heads/BRANCH`
- Ensure service principal has correct permissions
- Check tenant ID and client ID are correct

**Service Principal Issues**:
- Verify JSON credentials are properly formatted
- Check role assignments on resource group
- Ensure secrets are not expired

### Script Fails

**Check logs**:
```bash
# View workflow logs in GitHub Actions tab
# Common issues:
- Missing Python dependencies (check requirements.txt)
- Incorrect environment variables
- Azure API rate limiting
```

### No CSV Exported

- Check if `--no-csv` flag is being used
- Verify write permissions in workflow
- Check artifact upload step didn't fail

## 🎯 Best Practices

1. **Use OIDC** for keyless authentication (more secure)
2. **Enable environment protection** for production deployments
3. **Set up branch protection** to prevent unauthorized workflow changes
4. **Review artifacts regularly** to track changes over time
5. **Use manual triggers** for deployments (avoid auto-deploy in production)
6. **Monitor workflow runs** for failures and audit results
7. **Rotate credentials** if using service principal with secrets
8. **Set artifact retention** based on compliance requirements

## 📝 Example Usage

### Run Scheduled Audit
Workflow runs automatically daily at 9 AM UTC. Results are uploaded as artifacts.

### Manual Audit (No Deployment)
1. Go to Actions → Sentinel Audit and Update
2. Click "Run workflow"
3. Leave `auto_deploy` unchecked
4. Click "Run workflow"

### Manual Deployment
1. Go to Actions → Deploy Sentinel Updates
2. Click "Run workflow"
3. Select deployment mode and update type
4. Click "Run workflow"
5. Approve deployment if environment protection is enabled

### Download Reports
1. Go to Actions → Select completed workflow
2. Scroll to Artifacts section
3. Download `sentinel-audit-reports-{run-number}.zip`
4. Extract CSV files for analysis

## 🔗 Additional Resources

- [Azure OIDC Documentation](https://docs.microsoft.com/azure/developer/github/connect-from-azure)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Microsoft Sentinel API Reference](https://docs.microsoft.com/rest/api/securityinsights/)
