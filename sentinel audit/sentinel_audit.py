#!/usr/bin/env python3
"""
Simple Sentinel Audit Script
Exports enabled data connectors and analytic rules to CSV files.
"""

import os
import csv
import sys
from datetime import datetime
from pathlib import Path
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


def resolve_output_dir() -> Path:
    """Resolve and create the output directory for generated reports."""
    base_dir = Path(__file__).resolve().parent.parent
    env_value = os.getenv('OUTPUT_DIR')

    if env_value:
        candidate = Path(env_value)
        if not candidate.is_absolute():
            candidate = (base_dir / candidate).resolve()
    else:
        candidate = base_dir / "output"

    candidate.mkdir(parents=True, exist_ok=True)
    return candidate

def get_azure_credential():
    """Get Azure credentials with interactive options."""
    
    # Check for authentication mode preference
    auth_mode = os.getenv('AUTH_MODE', '').lower()
    
    # If AUTH_MODE is set, use it directly
    if auth_mode == 'device':
        print("🔐 Using Device Code authentication")
        print("📱 You'll be prompted to visit a URL and enter a code")
        return DeviceCodeCredential()
    
    elif auth_mode == 'browser':
        print("🌐 Using Interactive Browser authentication")
        print("🖥️  A browser window will open for authentication")
        return InteractiveBrowserCredential()
    
    elif auth_mode == 'cli':
        print("🔄 Using Azure CLI authentication")
        print("💡 Make sure you've run 'az login' first")
        return DefaultAzureCredential()
    
    elif all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("🔑 Using Service Principal authentication")
        return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET) # type: ignore
    
    # If no AUTH_MODE set, prompt user for choice
    else:
        print("\n� Choose Authentication Method:")
        print("1. 🌐 Interactive Browser Login (opens browser window)")
        print("2. 📱 Device Code Login (enter code on another device)")
        print("3. 🔄 Azure CLI (if you've already run 'az login')")
        print("4. ⚡ Auto-detect (try Azure CLI first, then prompt)")
        
        while True:
            try:
                choice = input("\nEnter choice (1-4): ").strip()
                
                if choice == '1':
                    print("🌐 Using Interactive Browser authentication")
                    print("🖥️  A browser window will open for authentication")
                    return InteractiveBrowserCredential()
                
                elif choice == '2':
                    print("🔐 Using Device Code authentication")
                    print("📱 You'll be prompted to visit a URL and enter a code")
                    return DeviceCodeCredential()
                
                elif choice == '3':
                    print("🔄 Using Azure CLI authentication")
                    print("💡 Make sure you've run 'az login' first")
                    return DefaultAzureCredential()
                
                elif choice == '4':
                    print("⚡ Auto-detecting authentication method...")
                    return DefaultAzureCredential()
                
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                    
            except KeyboardInterrupt:
                print("\n❌ Authentication cancelled by user")
                sys.exit(1)
            except Exception:
                print("❌ Invalid input. Please enter 1, 2, 3, or 4.")

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

def export_to_csv(data, file_path: Path, fieldnames):
    """Export data to CSV file."""
    try:
        with file_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Exported {len(data)} records to {file_path}")
    except Exception as e:
        print(f"❌ Error writing to {file_path}: {e}")

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
        
        # Resolve output directory
        output_dir = resolve_output_dir()
        print(f"📁 Output directory: {output_dir}")

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save customer information to metadata file
        metadata_file = output_dir / f'sentinel_customer_info_{timestamp}.csv'
        with metadata_file.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['customer_name', 'subscription_name', 'subscription_id', 'tenant_id', 'audit_timestamp'])
            writer.writeheader()
            customer_info['audit_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            writer.writerow(customer_info)
        print(f"💾 Customer metadata saved to: {metadata_file}")
        
        # Export to CSV files (always emit files for downstream tooling)
        connector_fields = ['Connector', 'Type', 'Count', 'Status']
        connector_file = output_dir / f'sentinel_data_connectors_{timestamp}.csv'
        export_to_csv(connectors, connector_file, connector_fields)
        if not connectors:
            print("⚠️  No data connectors found — exported empty report")

        rule_fields = ['Name', 'Enabled']
        rule_file = output_dir / f'sentinel_analytic_rules_{timestamp}.csv'
        export_to_csv(rules, rule_file, rule_fields)
        if not rules:
            print("⚠️  No enabled analytic rules found — exported empty report")
        
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