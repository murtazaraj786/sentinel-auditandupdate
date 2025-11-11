#!/usr/bin/env python3
"""
Azure Web Application Firewall (WAF) Audit Script
Exports WAF policies, rules, and analytics to CSV files.
"""

import os
import csv
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from azure.identity import DefaultAzureCredential, ClientSecretCredential, InteractiveBrowserCredential, DeviceCodeCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.cdn import CdnManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.frontdoor import FrontDoorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError, HttpResponseError

# Configuration
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
PUBLIC_CLIENT_ID = os.getenv('AZURE_PUBLIC_CLIENT_ID', '04b07795-8ddb-461a-bbee-02f9e1bf7b46')

# Output directory
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '../output')

def get_azure_credential():
    """Get Azure credentials with interactive options."""
    
    # Check for authentication mode preference
    auth_mode = os.getenv('AUTH_MODE', '').lower()
    
    # If AUTH_MODE is set, use it directly
    if auth_mode == 'device':
        print("🔐 Using Device Code authentication")
        print("📱 You'll be prompted to visit a URL and enter a code")
        return DeviceCodeCredential(
            client_id=PUBLIC_CLIENT_ID,
            tenant_id=TENANT_ID
        )
    
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
        return ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
    
    else:
        # Interactive selection
        print("\n🔐 Authentication Options:")
        print("1. Device Code (📱 any device)")
        print("2. Browser Login (🌐 GUI required)")
        print("3. Azure CLI (🔄 if already logged in)")
        print("4. Auto-detect")
        
        while True:
            try:
                choice = input("\nChoose authentication method (1-4): ").strip()
                
                if choice == '1':
                    return DeviceCodeCredential(
                        client_id=PUBLIC_CLIENT_ID,
                        tenant_id=TENANT_ID
                    )
                elif choice == '2':
                    return InteractiveBrowserCredential()
                elif choice == '3':
                    return DefaultAzureCredential()
                elif choice == '4':
                    return DefaultAzureCredential()
                else:
                    print("❌ Invalid choice. Please enter 1-4.")
            except KeyboardInterrupt:
                print("\n❌ Authentication cancelled.")
                sys.exit(1)

def resolve_output_dir():
    """Resolve and create output directory."""
    
    # Try different potential output directories
    potential_dirs = [
        OUTPUT_DIR,  # Environment variable
        '../output',  # Relative to script
        './output',   # Current directory
        '.'          # Fallback to current directory
    ]
    
    for dir_path in potential_dirs:
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(dir_path)
            
            # Create directory if it doesn't exist
            os.makedirs(abs_path, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(abs_path, 'test_write_permissions.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return abs_path
            except:
                continue
                
        except:
            continue
    
    # If all else fails, use current directory
    return os.getcwd()

def get_customer_info(credential):
    """Get customer information from Azure subscription."""
    try:
        subscription_client = SubscriptionClient(credential)
        subscription = subscription_client.subscriptions.get(SUBSCRIPTION_ID)
        
        # Extract meaningful customer name
        subscription_name = subscription.display_name or "Unknown Subscription"
        customer_name = subscription_name.replace("Microsoft Azure Sponsorship", "").strip()
        customer_name = customer_name.replace("Pay-As-You-Go", "").strip()
        customer_name = customer_name.replace("Free Trial", "").strip()
        customer_name = customer_name.split("-")[0].strip() if "-" in customer_name else customer_name
        
        # Fallback to a generic name
        if not customer_name or len(customer_name) < 3:
            customer_name = "Azure Customer"
        
        return {
            'customer_name': customer_name,
            'subscription_id': SUBSCRIPTION_ID,
            'subscription_name': subscription_name,
            'tenant_id': TENANT_ID or "Unknown"
        }
        
    except Exception as e:
        print(f"⚠️  Warning: Could not retrieve subscription info: {e}")
        return {
            'customer_name': "Azure Customer",
            'subscription_id': SUBSCRIPTION_ID or "Unknown",
            'subscription_name': "Unknown Subscription",
            'tenant_id': TENANT_ID or "Unknown"
        }

def export_application_gateway_waf(network_client, output_dir, timestamp):
    """Export Application Gateway WAF policies and configurations."""
    filename = os.path.join(output_dir, f"azure_waf_app_gateway_{timestamp}.csv")
    waf_configs = []
    
    print("🔥 Exporting Application Gateway WAF Configurations...")
    
    try:
        # Get Application Gateway WAF policies
        waf_policies = network_client.web_application_firewall_policies.list_all()
        
        for policy in waf_policies:
            try:
                # Extract policy details
                waf_config = {
                    'Resource Name': policy.name,
                    'Resource Group': policy.id.split('/')[4] if policy.id else 'N/A',
                    'Location': policy.location or 'N/A',
                    'Policy Mode': policy.policy_settings.mode if policy.policy_settings else 'N/A',
                    'Policy State': policy.policy_settings.state if policy.policy_settings else 'N/A',
                    'Request Body Check': policy.policy_settings.request_body_check if policy.policy_settings else 'N/A',
                    'Max Request Body Size': policy.policy_settings.max_request_body_size_in_kb if policy.policy_settings else 'N/A',
                    'File Upload Limit': policy.policy_settings.file_upload_limit_in_mb if policy.policy_settings else 'N/A',
                    'Rule Set Type': policy.managed_rules.managed_rule_sets[0].rule_set_type if policy.managed_rules and policy.managed_rules.managed_rule_sets else 'N/A',
                    'Rule Set Version': policy.managed_rules.managed_rule_sets[0].rule_set_version if policy.managed_rules and policy.managed_rules.managed_rule_sets else 'N/A',
                    'Custom Rules Count': len(policy.custom_rules) if policy.custom_rules else 0,
                    'Exclusions Count': len(policy.managed_rules.exclusions) if policy.managed_rules and policy.managed_rules.exclusions else 0,
                    'Associated Gateways': 'Multiple' if policy.application_gateways and len(policy.application_gateways) > 1 else '1' if policy.application_gateways else '0'
                }
                
                waf_configs.append(waf_config)
                
            except Exception as e:
                print(f"⚠️  Error processing WAF policy: {e}")
                continue
        
        # Get Application Gateways with WAF enabled
        app_gateways = network_client.application_gateways.list_all()
        
        for gateway in app_gateways:
            try:
                if hasattr(gateway, 'web_application_firewall_configuration') and gateway.web_application_firewall_configuration:
                    waf_config = {
                        'Resource Name': gateway.name,
                        'Resource Group': gateway.id.split('/')[4] if gateway.id else 'N/A',
                        'Location': gateway.location or 'N/A',
                        'Policy Mode': gateway.web_application_firewall_configuration.firewall_mode,
                        'Policy State': gateway.web_application_firewall_configuration.enabled,
                        'Request Body Check': gateway.web_application_firewall_configuration.request_body_check,
                        'Max Request Body Size': gateway.web_application_firewall_configuration.max_request_body_size_in_kb,
                        'File Upload Limit': gateway.web_application_firewall_configuration.file_upload_limit_in_mb,
                        'Rule Set Type': gateway.web_application_firewall_configuration.rule_set_type,
                        'Rule Set Version': gateway.web_application_firewall_configuration.rule_set_version,
                        'Custom Rules Count': len(gateway.web_application_firewall_configuration.disabled_rule_groups) if gateway.web_application_firewall_configuration.disabled_rule_groups else 0,
                        'Exclusions Count': len(gateway.web_application_firewall_configuration.exclusions) if gateway.web_application_firewall_configuration.exclusions else 0,
                        'Associated Gateways': '1 (Legacy Config)'
                    }
                    
                    waf_configs.append(waf_config)
                
            except Exception as e:
                print(f"⚠️  Error processing Application Gateway: {e}")
                continue
        
        # Write to CSV
        if waf_configs:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if waf_configs:
                    writer = csv.DictWriter(csvfile, fieldnames=waf_configs[0].keys())
                    writer.writeheader()
                    writer.writerows(waf_configs)
            
            print(f"✅ Application Gateway WAF configurations exported to: {filename}")
            return len(waf_configs)
        else:
            print("⚠️  No Application Gateway WAF configurations found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting Application Gateway WAF: {e}")
        return 0

def export_front_door_waf(frontdoor_client, output_dir, timestamp):
    """Export Front Door WAF policies and configurations."""
    filename = os.path.join(output_dir, f"azure_waf_front_door_{timestamp}.csv")
    frontdoor_wafs = []
    
    print("🚪 Exporting Front Door WAF Configurations...")
    
    try:
        # Get Front Door WAF policies
        try:
            waf_policies = frontdoor_client.policies.list_by_subscription(SUBSCRIPTION_ID)
            
            for policy in waf_policies:
                try:
                    frontdoor_wafs.append({
                        'Policy Name': policy.name,
                        'Resource Group': policy.id.split('/')[4] if policy.id else 'N/A',
                        'Location': policy.location or 'Global',
                        'Policy Mode': policy.policy_settings.mode if policy.policy_settings else 'N/A',
                        'Policy State': policy.policy_settings.enabled_state if policy.policy_settings else 'N/A',
                        'Request Body Check': policy.policy_settings.request_body_check if policy.policy_settings else 'N/A',
                        'Custom Block Response Code': policy.policy_settings.custom_block_response_status_code if policy.policy_settings else 'N/A',
                        'Custom Block Response Body': policy.policy_settings.custom_block_response_body if policy.policy_settings else 'N/A',
                        'Managed Rules Count': len(policy.managed_rules.managed_rule_sets) if policy.managed_rules and policy.managed_rules.managed_rule_sets else 0,
                        'Custom Rules Count': len(policy.custom_rules.rules) if policy.custom_rules and policy.custom_rules.rules else 0,
                        'Resource State': policy.resource_state,
                        'Frontend Endpoints': 'Multiple' if hasattr(policy, 'frontend_endpoints') and policy.frontend_endpoints and len(policy.frontend_endpoints) > 1 else '1' if hasattr(policy, 'frontend_endpoints') and policy.frontend_endpoints else '0'
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error processing Front Door WAF policy: {e}")
                    continue
        except Exception as e:
            print(f"⚠️  Front Door WAF policies not accessible: {e}")
        
        # Write to CSV
        if frontdoor_wafs:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=frontdoor_wafs[0].keys())
                writer.writeheader()
                writer.writerows(frontdoor_wafs)
            
            print(f"✅ Front Door WAF configurations exported to: {filename}")
            return len(frontdoor_wafs)
        else:
            print("⚠️  No Front Door WAF configurations found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting Front Door WAF: {e}")
        return 0

def export_cdn_waf(cdn_client, output_dir, timestamp):
    """Export CDN WAF policies and configurations."""
    filename = os.path.join(output_dir, f"azure_waf_cdn_{timestamp}.csv")
    cdn_wafs = []
    
    print("🌐 Exporting CDN WAF Configurations...")
    
    try:
        # Get resource groups to iterate through CDN profiles
        resource_client = ResourceManagementClient(cdn_client._config.credential, SUBSCRIPTION_ID)
        resource_groups = resource_client.resource_groups.list()
        
        for rg in resource_groups:
            try:
                # Get CDN profiles in each resource group
                cdn_profiles = cdn_client.profiles.list_by_resource_group(rg.name)
                
                for profile in cdn_profiles:
                    try:
                        # Get security policies for CDN profile
                        if hasattr(cdn_client, 'security_policies'):
                            security_policies = cdn_client.security_policies.list_by_profile(rg.name, profile.name)
                            
                            for policy in security_policies:
                                try:
                                    cdn_wafs.append({
                                        'Policy Name': policy.name,
                                        'CDN Profile': profile.name,
                                        'Resource Group': rg.name,
                                        'Location': profile.location or 'Global',
                                        'CDN SKU': profile.sku.name if profile.sku else 'N/A',
                                        'Policy Type': policy.type,
                                        'Deployment Status': policy.deployment_status if hasattr(policy, 'deployment_status') else 'N/A',
                                        'Domain Count': len(policy.domains) if hasattr(policy, 'domains') and policy.domains else 0,
                                        'Profile State': profile.resource_state if hasattr(profile, 'resource_state') else 'N/A',
                                        'Provisioning State': profile.provisioning_state if hasattr(profile, 'provisioning_state') else 'N/A'
                                    })
                                except Exception as e:
                                    print(f"⚠️  Error processing CDN security policy: {e}")
                                    continue
                    except Exception as e:
                        print(f"⚠️  Error accessing CDN profile security policies: {e}")
                        continue
            except Exception as e:
                print(f"⚠️  Error accessing resource group {rg.name}: {e}")
                continue
        
        # Write to CSV
        if cdn_wafs:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=cdn_wafs[0].keys())
                writer.writeheader()
                writer.writerows(cdn_wafs)
            
            print(f"✅ CDN WAF configurations exported to: {filename}")
            return len(cdn_wafs)
        else:
            print("⚠️  No CDN WAF configurations found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting CDN WAF: {e}")
        return 0

def export_waf_summary(output_dir, timestamp, app_gw_count, frontdoor_count, cdn_count):
    """Export WAF summary and recommendations."""
    filename = os.path.join(output_dir, f"azure_waf_summary_{timestamp}.csv")
    
    print("📊 Generating WAF Summary and Recommendations...")
    
    summary_data = [
        {
            'WAF Service': 'Application Gateway WAF',
            'Configurations Found': app_gw_count,
            'Service Type': 'Regional Load Balancer',
            'Use Case': 'Internal/Regional Web Applications',
            'Key Benefits': 'Layer 7 protection, Custom rules, SSL termination',
            'Recommendations': 'Review custom rules and exclusions' if app_gw_count > 0 else 'Consider for regional web apps'
        },
        {
            'WAF Service': 'Front Door WAF',
            'Configurations Found': frontdoor_count,
            'Service Type': 'Global Load Balancer',
            'Use Case': 'Global Web Applications',
            'Key Benefits': 'Global anycast, DDoS protection, Edge optimization',
            'Recommendations': 'Review rate limiting and geo-filtering' if frontdoor_count > 0 else 'Consider for global applications'
        },
        {
            'WAF Service': 'CDN WAF',
            'Configurations Found': cdn_count,
            'Service Type': 'Content Delivery Network',
            'Use Case': 'Static Content Protection',
            'Key Benefits': 'Edge caching, Global distribution, Bot protection',
            'Recommendations': 'Review caching policies and origin protection' if cdn_count > 0 else 'Consider for content delivery'
        }
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
        
        print(f"✅ WAF summary exported to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error exporting WAF summary: {e}")
        return False

def main():
    """Main function to run the Azure WAF audit."""
    print("🔥 Starting Azure Web Application Firewall (WAF) Audit")
    print("=" * 70)
    
    # Validate environment variables
    if not SUBSCRIPTION_ID:
        print("❌ Error: AZURE_SUBSCRIPTION_ID must be set")
        print("\n💡 Set environment variables:")
        print('   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"')
        print('   $env:AZURE_TENANT_ID = "your-tenant-id"')
        print('   $env:AUTH_MODE = "device"  # or browser, cli')
        sys.exit(1)
    
    try:
        # Get credentials
        credential = get_azure_credential()
        
        # Get customer information
        customer_info = get_customer_info(credential)
        print(f"🏢 Customer: {customer_info['customer_name']}")
        print(f"🆔 Subscription: {customer_info['subscription_id']}")
        print(f"🔑 Tenant ID: {customer_info['tenant_id']}")
        print("")
        
        # Resolve output directory
        output_dir = resolve_output_dir()
        print(f"📁 Output directory: {output_dir}")
        print("")
        
        # Initialize clients
        network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
        cdn_client = CdnManagementClient(credential, SUBSCRIPTION_ID)
        frontdoor_client = FrontDoorManagementClient(credential, SUBSCRIPTION_ID)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export data
        total_items = 0
        
        # Export Application Gateway WAF configurations
        app_gw_count = export_application_gateway_waf(network_client, output_dir, timestamp)
        total_items += app_gw_count
        print("")
        
        # Export Front Door WAF configurations
        frontdoor_count = export_front_door_waf(frontdoor_client, output_dir, timestamp)
        total_items += frontdoor_count
        print("")
        
        # Export CDN WAF configurations
        cdn_count = export_cdn_waf(cdn_client, output_dir, timestamp)
        total_items += cdn_count
        print("")
        
        # Generate summary report
        export_waf_summary(output_dir, timestamp, app_gw_count, frontdoor_count, cdn_count)
        print("")
        
        # Summary
        print("=" * 70)
        print("✅ Azure WAF audit completed successfully!")
        print(f"📊 Total WAF configurations found: {total_items}")
        print(f"   🔥 Application Gateway WAF: {app_gw_count}")
        print(f"   🚪 Front Door WAF: {frontdoor_count}")
        print(f"   🌐 CDN WAF: {cdn_count}")
        print(f"📁 Reports saved in: {output_dir}")
        print("=" * 70)
        
    except AzureError as e:
        print(f"❌ Azure error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()