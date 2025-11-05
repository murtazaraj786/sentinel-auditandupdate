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
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
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
        return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET) # type: ignore
    
    else:
        print("🔄 Using Default Azure Credential (trying Azure CLI first)")
        print("💡 If this fails, set AUTH_MODE=device or AUTH_MODE=browser")
        return DefaultAzureCredential()

def get_customer_info(credential):
    """Get customer information from Azure subscription and tenant details."""
    try:
        # Get subscription info
        subscription_client = SubscriptionClient(credential)
        subscription = subscription_client.subscriptions.get(SUBSCRIPTION_ID) # type: ignore
        
        # Get tenant info from resource management
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID) # type: ignore
        tenant_id = subscription.tenant_id # type: ignore
        
        # Extract meaningful customer name
        subscription_name = subscription.display_name or "Unknown Subscription"
        
        # Common patterns to clean up subscription names
        customer_name = subscription_name.replace("Microsoft Azure Sponsorship", "").strip()
        customer_name = customer_name.replace("Pay-As-You-Go", "").strip()
        customer_name = customer_name.replace("Free Trial", "").strip()
        customer_name = customer_name.split("-")[0].strip() if "-" in customer_name else customer_name
        
        # If still generic, try to extract from resource group pattern
        if customer_name.lower() in ["", "microsoft", "azure", "subscription"]:
            if RESOURCE_GROUP:
                # Extract customer name from resource group (common pattern: customer-rg-region)
                rg_parts = RESOURCE_GROUP.split("-")
                if len(rg_parts) > 0:
                    customer_name = rg_parts[0].title()
        
        # Fallback to a cleaned subscription name
        if not customer_name or customer_name.lower() in ["", "microsoft", "azure"]:
            customer_name = "Azure Customer"
            
        return {
            "customer_name": customer_name,
            "subscription_name": subscription_name,
            "subscription_id": SUBSCRIPTION_ID,
            "tenant_id": str(tenant_id) if tenant_id else "Unknown"
        }
        
    except Exception as e:
        print(f"⚠️  Could not retrieve customer info: {e}")
        # Fallback to resource group-based naming
        if RESOURCE_GROUP:
            customer_name = RESOURCE_GROUP.split("-")[0].title()
        else:
            customer_name = "Azure Customer"
            
        return {
            "customer_name": customer_name,
            "subscription_name": "Unknown Subscription",
            "subscription_id": SUBSCRIPTION_ID or "Unknown",
            "tenant_id": "Unknown"
        }

def audit_data_connectors(client):
    """Audit data connectors and return a clean summary."""
    print("Auditing data connectors...")
    connectors = []
    connector_counts = {}
    
    try:
        # List all data connectors
        data_connectors = client.data_connectors.list(
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
        
        # Count connectors by type
        for connector in data_connectors:
            connector_type = connector.kind
            if connector_type not in connector_counts:
                connector_counts[connector_type] = 0
            connector_counts[connector_type] += 1
        
        # Create clean summary
        for connector_type, count in connector_counts.items():
            # Create friendly names
            friendly_names = {
                'AzureSecurityCenter': 'Microsoft Defender for Cloud',
                'AzureActiveDirectory': 'Azure Active Directory',
                'AzureAdvancedThreatProtection': 'Microsoft Defender for Identity',
                'MicrosoftDefenderAdvancedThreatProtection': 'Microsoft Defender for Endpoint',
                'MicrosoftCloudAppSecurity': 'Microsoft Defender for Cloud Apps',
                'Office365': 'Microsoft 365',
                'MicrosoftThreatIntelligence': 'Microsoft Threat Intelligence',
                'SecurityEvents': 'Security Events via AMA',
                'WindowsFirewall': 'Windows Defender Firewall'
            }
            
            display_name = friendly_names.get(connector_type, connector_type)
            
            print(f"  Found: {display_name} ({count} instances)")
            
            connectors.append({
                'Connector': display_name,
                'Type': connector_type,
                'Count': count,
                'Status': 'Active'
            })
        
        print(f"Found {len(connectors)} connector types ({sum(connector_counts.values())} total instances)")
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
        
        # Get customer information first
        print("🏢 Retrieving customer information...")
        customer_info = get_customer_info(credential)
        print(f"📊 Auditing: {customer_info['customer_name']}")
        print(f"📋 Subscription: {customer_info['subscription_name']}")
        print(f"🆔 Tenant ID: {customer_info['tenant_id']}")
        print()
        
        client = SecurityInsights(credential, SUBSCRIPTION_ID) # type: ignore
        
        # Audit data connectors
        connectors = audit_data_connectors(client)
        
        # Audit analytic rules  
        rules = audit_analytic_rules(client)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save customer information to metadata file
        metadata_file = f'sentinel_customer_info_{timestamp}.csv'
        with open(metadata_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['customer_name', 'subscription_name', 'subscription_id', 'tenant_id', 'audit_timestamp'])
            writer.writeheader()
            customer_info['audit_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            writer.writerow(customer_info)
        print(f"💾 Customer metadata saved to: {metadata_file}")
        
        # Export to CSV files
        if connectors:
            connector_fields = ['Connector', 'Type', 'Count', 'Status']
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