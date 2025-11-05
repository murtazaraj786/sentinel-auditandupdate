#!/usr/bin/env python3
"""
Simple Sentinel Audit Script
Exports enabled data connectors and analytic rules to CSV files.
"""

import os
import csv
import sys
from datetime import datetime
from azure.identity import DefaultAzureCredential, ClientSecretCredential, InteractiveBrowserCredential, DeviceCodeCredential
from azure.mgmt.securityinsight import SecurityInsights
from azure.core.exceptions import AzureError

# Configuration
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('RESOURCE_GROUP_NAME')
WORKSPACE_NAME = os.getenv('WORKSPACE_NAME')

# Optional service principal authentication
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

def get_azure_credential():
    """Get Azure credentials with interactive options."""
    
    # Check for authentication mode preference
    auth_mode = os.getenv('AUTH_MODE', 'auto').lower()
    
    if auth_mode == 'device':
        print("🔐 Using Device Code authentication")
        print("📱 You'll be prompted to visit a URL and enter a code")
        return DeviceCodeCredential()
    
    elif auth_mode == 'browser':
        print("🌐 Using Interactive Browser authentication")
        print("🖥️  A browser window will open for authentication")
        return InteractiveBrowserCredential()
    
    elif all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("🔑 Using Service Principal authentication")
        return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    
    else:
        print("🔄 Using Default Azure Credential (trying Azure CLI first)")
        print("💡 If this fails, set AUTH_MODE=device or AUTH_MODE=browser")
        return DefaultAzureCredential()

def audit_data_connectors(client):
    """Audit data connectors and return all of them."""
    print("Auditing data connectors...")
    connectors = []
    
    try:
        # List all data connectors
        data_connectors = client.data_connectors.list(
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
        
        for connector in data_connectors:
            # Get friendly name or fall back to type
            friendly_name = getattr(connector, 'friendly_name', None) or getattr(connector, 'data_type_friendly_name', None) or connector.kind
            
            # Get tenant ID for some connector types that show it
            tenant_info = ""
            if hasattr(connector, 'tenant_id') and connector.tenant_id:
                tenant_info = f" (Tenant: {connector.tenant_id[:8]}...)"
            
            # Get subscription ID for some connector types
            sub_info = ""
            if hasattr(connector, 'subscription_id') and connector.subscription_id:
                sub_info = f" (Sub: {connector.subscription_id[:8]}...)"
            
            display_name = f"{friendly_name}{tenant_info}{sub_info}"
            
            print(f"  Found connector: {display_name}")
            
            # Try to get better date info
            created_date = 'Unknown'
            modified_date = 'Unknown'
            
            if hasattr(connector, 'system_data') and connector.system_data:
                if hasattr(connector.system_data, 'created_at') and connector.system_data.created_at:
                    created_date = str(connector.system_data.created_at)[:10]  # Just the date part
                if hasattr(connector.system_data, 'last_modified_at') and connector.system_data.last_modified_at:
                    modified_date = str(connector.system_data.last_modified_at)[:10]  # Just the date part
            
            connectors.append({
                'Name': display_name,
                'Type': connector.kind,
                'State': getattr(connector, 'state', 'Active'),
                'Created': created_date,
                'Modified': modified_date
            })
        
        print(f"Found {len(connectors)} total data connectors")
        return connectors
        
    except AzureError as e:
        print(f"Error fetching data connectors: {e}")
        return []

def audit_analytic_rules(client):
    """Audit analytic rules and return enabled ones."""
    print("Auditing analytic rules...")
    rules = []
    
    try:
        # List all alert rules
        alert_rules = client.alert_rules.list(
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
        
        for rule in alert_rules:
            # Only include enabled rules
            if hasattr(rule, 'enabled') and rule.enabled:
                rules.append({
                    'Name': rule.display_name or rule.name,
                    'Enabled': rule.enabled
                })
        
        print(f"Found {len(rules)} enabled analytic rules")
        return rules
        
    except AzureError as e:
        print(f"Error fetching analytic rules: {e}")
        return []

def export_to_csv(data, filename, fieldnames):
    """Export data to CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Exported {len(data)} records to {filename}")
    except Exception as e:
        print(f"❌ Error writing to {filename}: {e}")

def main():
    """Main function."""
    print("🔍 Microsoft Sentinel Audit Tool")
    print("=" * 50)
    
    # Check for .env file and load it
    env_file = '.env'
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"📁 Loaded configuration from {env_file}")
    
    # Check required environment variables
    if not all([SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME]):
        print("❌ Missing required environment variables:")
        print("   AZURE_SUBSCRIPTION_ID")
        print("   RESOURCE_GROUP_NAME") 
        print("   WORKSPACE_NAME")
        print()
        print("💡 Authentication Options:")
        print("   AUTH_MODE=device   - Device code authentication")
        print("   AUTH_MODE=browser  - Browser-based authentication")
        print("   (or use Azure CLI: az login)")
        print()
        print("📝 Example setup:")
        print('   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"')
        print('   $env:RESOURCE_GROUP_NAME = "your-resource-group"')
        print('   $env:WORKSPACE_NAME = "your-workspace-name"')
        print('   $env:AUTH_MODE = "device"')
        sys.exit(1)
    
    print(f"Subscription: {SUBSCRIPTION_ID}")
    print(f"Resource Group: {RESOURCE_GROUP}")
    print(f"Workspace: {WORKSPACE_NAME}")
    print()
    
    try:
        # Get credentials and create client
        credential = get_azure_credential()
        client = SecurityInsights(credential, SUBSCRIPTION_ID)
        
        # Audit data connectors
        connectors = audit_data_connectors(client)
        
        # Audit analytic rules  
        rules = audit_analytic_rules(client)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to CSV files
        if connectors:
            connector_fields = ['Name', 'Type', 'State', 'Created', 'Modified']
            export_to_csv(connectors, f'sentinel_data_connectors_{timestamp}.csv', connector_fields)
        else:
            print("⚠️  No data connectors found")
        
        if rules:
            rule_fields = ['Name', 'Enabled']
            export_to_csv(rules, f'sentinel_analytic_rules_{timestamp}.csv', rule_fields)
        else:
            print("⚠️  No enabled analytic rules found")
        
        print()
        print("✅ Audit completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Data Connectors: {len(connectors)}")
        print(f"   - Analytic Rules: {len(rules)}")
        
    except AzureError as e:
        print(f"❌ Azure error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()