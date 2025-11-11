#!/usr/bin/env python3
"""
Microsoft Defender for Cloud Audit Script
Exports security assessments, recommendations, alerts, and compliance data to CSV files.
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
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError, HttpResponseError

# Try to import Azure Security Management, fallback gracefully
try:
    from azure.mgmt.security import SecurityCenterManagementClient
    SECURITY_CLIENT_AVAILABLE = True
except ImportError:
    print("⚠️  Azure Security Management SDK not available. Please install with:")
    print("   pip install azure-mgmt-security")
    SECURITY_CLIENT_AVAILABLE = False

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

def export_security_assessments(security_client, output_dir, timestamp):
    """Export security assessments and recommendations."""
    filename = os.path.join(output_dir, f"defender_cloud_assessments_{timestamp}.csv")
    assessments = []
    
    print("📊 Exporting Security Assessments...")
    
    try:
        # Get security assessments at subscription level
        assessment_results = security_client.assessments.list(f"subscriptions/{SUBSCRIPTION_ID}")
        
        for assessment in assessment_results:
            try:
                assessments.append({
                    'Assessment ID': assessment.name,
                    'Display Name': assessment.display_name or 'N/A',
                    'Resource Type': assessment.resource_details.get('source', 'N/A') if hasattr(assessment, 'resource_details') else 'N/A',
                    'Status': assessment.status.get('code', 'Unknown') if hasattr(assessment, 'status') else 'Unknown',
                    'Severity': assessment.status.get('severity', 'Unknown') if hasattr(assessment, 'status') else 'Unknown',
                    'Category': assessment.metadata.get('category', 'N/A') if hasattr(assessment, 'metadata') else 'N/A',
                    'Assessment Type': assessment.metadata.get('assessmentType', 'N/A') if hasattr(assessment, 'metadata') else 'N/A',
                    'Description': assessment.metadata.get('description', 'N/A') if hasattr(assessment, 'metadata') else 'N/A',
                    'Remediation': assessment.metadata.get('remediationDescription', 'N/A') if hasattr(assessment, 'metadata') else 'N/A',
                    'First Evaluation': assessment.status.get('firstEvaluationDate', 'N/A') if hasattr(assessment, 'status') else 'N/A',
                    'Status Change': assessment.status.get('statusChangeDate', 'N/A') if hasattr(assessment, 'status') else 'N/A'
                })
            except Exception as e:
                print(f"⚠️  Error processing assessment: {e}")
                continue
        
        # Write to CSV
        if assessments:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=assessments[0].keys())
                writer.writeheader()
                writer.writerows(assessments)
            
            print(f"✅ Security assessments exported to: {filename}")
            return len(assessments)
        else:
            print("⚠️  No security assessments found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting security assessments: {e}")
        return 0

def export_security_alerts(security_client, output_dir, timestamp):
    """Export Defender for Cloud security alerts."""
    filename = os.path.join(output_dir, f"defender_cloud_alerts_{timestamp}.csv")
    alerts = []
    
    print("🚨 Exporting Security Alerts...")
    
    try:
        # Get security alerts at subscription level
        alert_results = security_client.alerts.list_by_subscription(SUBSCRIPTION_ID)
        
        for alert in alert_results:
            try:
                alerts.append({
                    'Alert ID': alert.name,
                    'Alert Name': alert.alert_display_name or 'N/A',
                    'Severity': alert.severity or 'Unknown',
                    'Status': alert.state or 'Unknown',
                    'Alert Type': alert.alert_type or 'N/A',
                    'Confidence': alert.confidence or 'N/A',
                    'Time Generated': alert.time_generated_utc.isoformat() if alert.time_generated_utc else 'N/A',
                    'Start Time': alert.start_time_utc.isoformat() if alert.start_time_utc else 'N/A',
                    'End Time': alert.end_time_utc.isoformat() if alert.end_time_utc else 'N/A',
                    'Description': alert.description or 'N/A',
                    'Remediation': alert.remediation_steps or 'N/A',
                    'Compromised Entity': alert.compromised_entity or 'N/A',
                    'Vendor': alert.vendor_name or 'N/A',
                    'Product': alert.product_name or 'N/A',
                    'Resource Group': alert.resource_identifiers[0].get('resourceGroup', 'N/A') if alert.resource_identifiers else 'N/A',
                    'Resource Type': alert.resource_identifiers[0].get('type', 'N/A') if alert.resource_identifiers else 'N/A'
                })
            except Exception as e:
                print(f"⚠️  Error processing alert: {e}")
                continue
        
        # Write to CSV
        if alerts:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=alerts[0].keys())
                writer.writeheader()
                writer.writerows(alerts)
            
            print(f"✅ Security alerts exported to: {filename}")
            return len(alerts)
        else:
            print("⚠️  No security alerts found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting security alerts: {e}")
        return 0

def export_compliance_results(security_client, output_dir, timestamp):
    """Export compliance assessment results."""
    filename = os.path.join(output_dir, f"defender_cloud_compliance_{timestamp}.csv")
    compliance_results = []
    
    print("📋 Exporting Compliance Results...")
    
    try:
        # Get compliance results
        compliances = security_client.compliances.list(f"subscriptions/{SUBSCRIPTION_ID}")
        
        for compliance in compliances:
            try:
                compliance_results.append({
                    'Compliance ID': compliance.name,
                    'Assessment Time': compliance.assessment_timestamp.isoformat() if compliance.assessment_timestamp else 'N/A',
                    'Resource Count': compliance.resource_count or 0,
                    'Assessed Resource Count': compliance.assessed_resource_count or 0,
                    'Skipped Resource Count': compliance.skipped_resource_count or 0,
                    'Passed Controls': compliance.passed_controls or 0,
                    'Failed Controls': compliance.failed_controls or 0,
                    'Skipped Controls': compliance.skipped_controls or 0,
                    'Compliance Percentage': f"{(compliance.percentage * 100):.1f}%" if compliance.percentage else 'N/A'
                })
            except Exception as e:
                print(f"⚠️  Error processing compliance result: {e}")
                continue
        
        # Write to CSV
        if compliance_results:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=compliance_results[0].keys())
                writer.writeheader()
                writer.writerows(compliance_results)
            
            print(f"✅ Compliance results exported to: {filename}")
            return len(compliance_results)
        else:
            print("⚠️  No compliance results found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting compliance results: {e}")
        return 0

def export_secure_score(security_client, output_dir, timestamp):
    """Export Defender for Cloud Secure Score."""
    filename = os.path.join(output_dir, f"defender_cloud_secure_score_{timestamp}.csv")
    secure_scores = []
    
    print("📈 Exporting Secure Score...")
    
    try:
        # Get secure scores
        scores = security_client.secure_scores.list(f"subscriptions/{SUBSCRIPTION_ID}")
        
        for score in scores:
            try:
                secure_scores.append({
                    'Score ID': score.name,
                    'Display Name': score.display_name or 'N/A',
                    'Current Score': score.current_score or 0,
                    'Max Score': score.max_score or 0,
                    'Percentage': f"{(score.percentage * 100):.1f}%" if score.percentage else 'N/A',
                    'Weight': score.weight or 0
                })
            except Exception as e:
                print(f"⚠️  Error processing secure score: {e}")
                continue
        
        # Write to CSV
        if secure_scores:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=secure_scores[0].keys())
                writer.writeheader()
                writer.writerows(secure_scores)
            
            print(f"✅ Secure score exported to: {filename}")
            return len(secure_scores)
        else:
            print("⚠️  No secure score data found")
            return 0
            
    except Exception as e:
        print(f"❌ Error exporting secure score: {e}")
        return 0

def main():
    """Main function to run the Defender for Cloud audit."""
    print("🛡️  Starting Microsoft Defender for Cloud Audit")
    print("=" * 60)
    
    # Check if security client is available
    if not SECURITY_CLIENT_AVAILABLE:
        print("❌ Error: Azure Security Management SDK not installed")
        print("💡 Install with: pip install azure-mgmt-security>=4.0.0")
        sys.exit(1)
    
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
        
        # Initialize Security Center client
        security_client = SecurityCenterManagementClient(credential, SUBSCRIPTION_ID)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export data
        total_items = 0
        
        # Export security assessments
        assessment_count = export_security_assessments(security_client, output_dir, timestamp)
        total_items += assessment_count
        print("")
        
        # Export security alerts
        alert_count = export_security_alerts(security_client, output_dir, timestamp)
        total_items += alert_count
        print("")
        
        # Export compliance results
        compliance_count = export_compliance_results(security_client, output_dir, timestamp)
        total_items += compliance_count
        print("")
        
        # Export secure score
        score_count = export_secure_score(security_client, output_dir, timestamp)
        total_items += score_count
        print("")
        
        # Summary
        print("=" * 60)
        print("✅ Microsoft Defender for Cloud audit completed successfully!")
        print(f"📊 Total items exported: {total_items}")
        print(f"📁 Reports saved in: {output_dir}")
        print("=" * 60)
        
    except AzureError as e:
        print(f"❌ Azure error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()