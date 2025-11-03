# Azure Service Principal Setup for GitHub Actions

This guide will help you create an Azure Service Principal and configure GitHub secrets for authentication.

## 🔐 Step 1: Create Azure Service Principal

Run this command in Azure Cloud Shell or local terminal (with Azure CLI installed):

```bash
az ad sp create-for-rbac \
  --name "github-sentinel-audit" \
  --role "Microsoft Sentinel Contributor" \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group-name} \
  --sdk-auth
```

**Replace these values**:
- `{subscription-id}`: Your Azure subscription ID
- `{resource-group-name}`: Resource group containing your Sentinel workspace

### Example:
```bash
az ad sp create-for-rbac \
  --name "github-sentinel-audit" \
  --role "Microsoft Sentinel Contributor" \
  --scopes /subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/sentinel-rg \
  --sdk-auth
```

### Output:
You'll get JSON output like this (⚠️ **SAVE THIS - you'll need it for GitHub**):

```json
{
  "clientId": "abcd1234-5678-90ab-cdef-1234567890ab",
  "clientSecret": "your-client-secret-here",
  "subscriptionId": "12345678-1234-1234-1234-123456789012",
  "tenantId": "87654321-4321-4321-4321-210987654321",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

## 📋 Step 2: Get Workspace Details

Find your Sentinel workspace details:

```bash
# List all Sentinel workspaces in your subscription
az sentinel workspace list --subscription {subscription-id}

# Or use Azure Portal:
# Navigate to your Sentinel workspace → Overview
# Note: Workspace name, Resource group name, Subscription ID
```

## 🔑 Step 3: Add Secrets to GitHub

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/{your-username}/sentinel-auditandupdate`

2. **Open Settings → Secrets and variables → Actions**

3. **Click "New repository secret"** and add these secrets:

### Required Secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AZURE_CREDENTIALS` | The **entire JSON output** from Step 1 | `{"clientId": "...", "clientSecret": "...", ...}` |
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID | `12345678-1234-1234-1234-123456789012` |
| `RESOURCE_GROUP_NAME` | Resource group containing Sentinel | `sentinel-rg` |
| `WORKSPACE_NAME` | Your Sentinel workspace name | `sentinel-workspace-prod` |

### How to Add Each Secret:

1. Click **"New repository secret"**
2. Name: `AZURE_CREDENTIALS`
3. Value: Paste the **entire JSON** from Step 1 (including the curly braces)
4. Click **"Add secret"**
5. Repeat for the other 3 secrets

## ✅ Step 4: Verify Permissions

Ensure the service principal has the right permissions:

```bash
# Check role assignments
az role assignment list \
  --assignee {clientId-from-step-1} \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}
```

### Required Roles:

For **audit-only** (read operations):
- ✅ `Reader` role is sufficient

For **deployments** (read + write operations):
- ✅ `Microsoft Sentinel Contributor` role (recommended)
- ✅ OR `Contributor` role

### Add Additional Permissions (if needed):

```bash
# Add Reader role for audits
az role assignment create \
  --assignee {clientId} \
  --role "Reader" \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}

# Add Sentinel Contributor for deployments
az role assignment create \
  --assignee {clientId} \
  --role "Microsoft Sentinel Contributor" \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}
```

## 🧪 Step 5: Test the Setup

### Option 1: Test Locally

Create a test file to verify credentials work:

```bash
# Set environment variables (PowerShell)
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
$env:RESOURCE_GROUP_NAME = "your-resource-group"
$env:WORKSPACE_NAME = "your-workspace-name"

# Run a quick audit
python main.py
```

### Option 2: Test in GitHub Actions

1. Go to **Actions** tab in your GitHub repository
2. Select **"Sentinel Audit and Update"** workflow
3. Click **"Run workflow"**
4. Leave defaults and click **"Run workflow"**
5. Watch the workflow run - it should complete successfully

## 🔒 Security Best Practices

### ✅ DO:
- Store credentials **only** in GitHub Secrets (never in code)
- Use least-privilege principle (Reader for audits, Contributor for deployments)
- Rotate client secrets regularly (Azure recommends every 90 days)
- Use environment protection for production deployments
- Limit service principal scope to specific resource group

### ❌ DON'T:
- Commit credentials to Git
- Share credentials in plain text
- Give subscription-level permissions unless necessary
- Use personal accounts for automation

## 🔄 Rotate Secrets (Recommended Every 90 Days)

```bash
# Reset service principal credentials
az ad sp credential reset \
  --id {clientId} \
  --display-name "github-sentinel-audit"
```

This will generate new credentials - update `AZURE_CREDENTIALS` secret in GitHub.

## 🐛 Troubleshooting

### Error: "Authorization failed"
- ✅ Verify service principal has correct role assignments
- ✅ Check resource group name is correct
- ✅ Ensure workspace exists in the specified resource group

### Error: "Invalid credentials"
- ✅ Verify `AZURE_CREDENTIALS` secret contains valid JSON
- ✅ Check client secret hasn't expired (default: 1 year)
- ✅ Ensure no extra spaces or characters in the JSON

### Error: "Subscription not found"
- ✅ Verify `AZURE_SUBSCRIPTION_ID` matches your subscription
- ✅ Check service principal has access to the subscription

### Workflow Doesn't Run
- ✅ Check workflow file is in `.github/workflows/` directory
- ✅ Verify YAML syntax is correct
- ✅ Ensure repository has Actions enabled (Settings → Actions)

## 📚 Additional Resources

- [Azure Service Principal Documentation](https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal)
- [GitHub Actions Secrets](https://docs.github.com/actions/security-guides/encrypted-secrets)
- [Azure CLI Reference](https://learn.microsoft.com/cli/azure/ad/sp)
- [Microsoft Sentinel RBAC](https://learn.microsoft.com/azure/sentinel/roles)

## 🎯 Quick Reference Card

Save this for easy access:

```bash
# Create Service Principal
az ad sp create-for-rbac --name "github-sentinel-audit" \
  --role "Microsoft Sentinel Contributor" \
  --scopes /subscriptions/YOUR_SUB_ID/resourceGroups/YOUR_RG \
  --sdk-auth

# Check Permissions
az role assignment list --assignee YOUR_CLIENT_ID

# Reset Credentials
az ad sp credential reset --id YOUR_CLIENT_ID

# Delete Service Principal (when no longer needed)
az ad sp delete --id YOUR_CLIENT_ID
```

---

**Next Steps**: After completing this setup, your GitHub Actions workflows will automatically authenticate to Azure and can audit/deploy Sentinel updates! 🚀
