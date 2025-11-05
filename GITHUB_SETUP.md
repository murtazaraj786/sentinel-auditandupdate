# GitHub Actions Setup for Sentinel Audit

## ✅ **Yes, it will work with Azure secrets!**

The script is designed to work with multiple authentication methods:

### 🔧 **Required GitHub Secrets**

Add these 4 secrets to your GitHub repository:

1. **`AZURE_CREDENTIALS`** - Complete service principal JSON
2. **`AZURE_SUBSCRIPTION_ID`** - Your subscription ID
3. **`RESOURCE_GROUP_NAME`** - Your resource group name  
4. **`WORKSPACE_NAME`** - Your Sentinel workspace name

### 🚀 **Quick Setup Steps**

#### 1. Create Azure Service Principal
```bash
az ad sp create-for-rbac \
  --name "github-sentinel-audit" \
  --role "Microsoft Sentinel Reader" \
  --scopes /subscriptions/6d3082d6-9e4a-443d-bbe1-713ca49f007b/resourceGroups/justgroup-rg-uks-sentinel \
  --sdk-auth
```

#### 2. Add GitHub Secrets
Go to your repo → Settings → Secrets → Actions → New secret:

- **`AZURE_CREDENTIALS`**: Paste the entire JSON from step 1
- **`AZURE_SUBSCRIPTION_ID`**: `6d3082d6-9e4a-443d-bbe1-713ca49f007b`
- **`RESOURCE_GROUP_NAME`**: `justgroup-rg-uks-sentinel`
- **`WORKSPACE_NAME`**: `log-sentinel-JustGroup`

#### 3. Done! 🎉

## 🔄 **How it works in GitHub Actions**

1. **Azure Login**: Uses `AZURE_CREDENTIALS` to authenticate
2. **Environment Variables**: Sets subscription, resource group, workspace from secrets
3. **Authentication Mode**: Uses `default` mode (Azure CLI credentials from login step)
4. **Script Location**: Runs from `./Sentinel Audit/` directory
5. **CSV Export**: Uploads CSV files as workflow artifacts

## 📊 **Workflow Features**

- **Scheduled**: Runs daily at 9 AM UTC automatically
- **Manual Trigger**: Run on-demand via "Run workflow" button
- **CSV Artifacts**: Downloads available for 30 days
- **Error Handling**: Clear error messages in workflow logs

## 🧪 **Test the Setup**

After adding secrets:
1. Go to **Actions** tab
2. Select **"Sentinel Audit"** workflow  
3. Click **"Run workflow"**
4. Watch it run and download CSV artifacts!

## 🔒 **Security Notes**

- ✅ Uses least-privilege (Reader role for audits)
- ✅ No secrets stored in code
- ✅ Service principal scoped to specific resource group
- ✅ Credentials automatically expire

The simplified script structure makes GitHub Actions integration much cleaner! 🚀