#!/usr/bin/env python3
"""
Defender XDR Audit Script
Exports security configurations, detection rules, and policies to CSV files.
"""

import os
import csv
import sys
import json
import requests
from datetime import datetime
from azure.identity import DefaultAzureCredential, ClientSecretCredential, InteractiveBrowserCredential, DeviceCodeCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import AzureError

# Configuration
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

# Microsoft Graph API endpoints
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
SECURITY_BASE_URL = "https://graph.microsoft.com/beta/security"

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

def get_access_token(credential):
    """Get access token for Microsoft Graph API."""
    try:
        token = credential.get_token("https://graph.microsoft.com/.default")
        return token.token
    except Exception as e:
        print(f"❌ Failed to get access token: {e}")
        sys.exit(1)

def make_graph_request(access_token, endpoint, params=None):
    """Make a request to Microsoft Graph API."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Failed to make request to {endpoint}: {e}")
        return None

def get_customer_info(credential):
    """Get customer information from Azure subscription and tenant details."""
    try:
        # Get subscription info if available
        if SUBSCRIPTION_ID:
            subscription_client = SubscriptionClient(credential)
            subscription = subscription_client.subscriptions.get(SUBSCRIPTION_ID)
            subscription_name = subscription.display_name or "Unknown Subscription"
            tenant_id = subscription.tenant_id
        else:
            subscription_name = "Microsoft 365 Tenant"
            tenant_id = TENANT_ID or "Unknown"
        
        # Extract meaningful customer name
        customer_name = subscription_name.replace("Microsoft Azure Sponsorship", "").strip()
        customer_name = customer_name.replace("Pay-As-You-Go", "").strip()
        customer_name = customer_name.replace("Free Trial", "").strip()
        customer_name = customer_name.split("-")[0].strip() if "-" in customer_name else customer_name
        
        # Fallback to a generic name
        if not customer_name or customer_name.lower() in ["", "microsoft", "azure"]:
            customer_name = "Microsoft 365 Customer"
            
        return {
            "customer_name": customer_name,
            "subscription_name": subscription_name,
            "subscription_id": SUBSCRIPTION_ID or "N/A",
            "tenant_id": str(tenant_id) if tenant_id else "Unknown"
        }
        
    except Exception as e:
        print(f"⚠️  Could not retrieve customer info: {e}")
        return {
            "customer_name": "Microsoft 365 Customer",
            "subscription_name": "Unknown",
            "subscription_id": SUBSCRIPTION_ID or "N/A",
            "tenant_id": TENANT_ID or "Unknown"
        }

def export_security_alerts(access_token, customer_info):
    """Export security alerts from Microsoft 365 Defender."""
    print("📊 Exporting Security Alerts...")
    
    endpoint = f"{SECURITY_BASE_URL}/alerts"
    params = {
        '$top': 1000,
        '$filter': "createdDateTime ge 2024-01-01T00:00:00Z",
        '$select': 'id,title,category,severity,status,createdDateTime,lastModifiedDateTime,classification,determination,serviceSource'
    }
    
    data = make_graph_request(access_token, endpoint, params)
    if not data or 'value' not in data:
        print("⚠️  No security alerts data found")
        return
    
    filename = f"defender_xdr_security_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Customer', 'Tenant ID', 'Alert ID', 'Title', 'Category', 'Severity', 
            'Status', 'Created Date', 'Modified Date', 'Classification', 
            'Determination', 'Service Source', 'Export Date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for alert in data['value']:
            writer.writerow({
                'Customer': customer_info['customer_name'],
                'Tenant ID': customer_info['tenant_id'],
                'Alert ID': alert.get('id', ''),
                'Title': alert.get('title', ''),
                'Category': alert.get('category', ''),
                'Severity': alert.get('severity', ''),
                'Status': alert.get('status', ''),
                'Created Date': alert.get('createdDateTime', ''),
                'Modified Date': alert.get('lastModifiedDateTime', ''),
                'Classification': alert.get('classification', ''),
                'Determination': alert.get('determination', ''),
                'Service Source': alert.get('serviceSource', ''),
                'Export Date': datetime.now().isoformat()
            })
    
    print(f"✅ Security alerts exported to: {filename}")
    return len(data['value'])

def export_security_incidents(access_token, customer_info):
    """Export security incidents from Microsoft 365 Defender."""
    print("🔍 Exporting Security Incidents...")
    
    endpoint = f"{SECURITY_BASE_URL}/incidents"
    params = {
        '$top': 1000,
        '$filter': "createdDateTime ge 2024-01-01T00:00:00Z",
        '$select': 'id,displayName,status,severity,classification,determination,createdDateTime,lastModifiedDateTime,assignedTo'
    }
    
    data = make_graph_request(access_token, endpoint, params)
    if not data or 'value' not in data:
        print("⚠️  No security incidents data found")
        return
    
    filename = f"defender_xdr_security_incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Customer', 'Tenant ID', 'Incident ID', 'Display Name', 'Status', 
            'Severity', 'Classification', 'Determination', 'Created Date', 
            'Modified Date', 'Assigned To', 'Export Date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for incident in data['value']:
            assigned_to = incident.get('assignedTo', {})
            assigned_to_name = assigned_to.get('displayName', '') if assigned_to else ''
            
            writer.writerow({
                'Customer': customer_info['customer_name'],
                'Tenant ID': customer_info['tenant_id'],
                'Incident ID': incident.get('id', ''),
                'Display Name': incident.get('displayName', ''),
                'Status': incident.get('status', ''),
                'Severity': incident.get('severity', ''),
                'Classification': incident.get('classification', ''),
                'Determination': incident.get('determination', ''),
                'Created Date': incident.get('createdDateTime', ''),
                'Modified Date': incident.get('lastModifiedDateTime', ''),
                'Assigned To': assigned_to_name,
                'Export Date': datetime.now().isoformat()
            })
    
    print(f"✅ Security incidents exported to: {filename}")
    return len(data['value'])

def export_attack_simulation_trainings(access_token, customer_info):
    """Export attack simulation training campaigns."""
    print("🎯 Exporting Attack Simulation Trainings...")
    
    endpoint = f"{GRAPH_BASE_URL}/security/attackSimulation/simulations"
    
    data = make_graph_request(access_token, endpoint)
    if not data or 'value' not in data:
        print("⚠️  No attack simulation data found")
        return
    
    filename = f"defender_xdr_attack_simulations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Customer', 'Tenant ID', 'Simulation ID', 'Display Name', 'Status', 
            'Attack Type', 'Created Date', 'Launch Date', 'End Date', 
            'Users Count', 'Export Date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for simulation in data['value']:
            writer.writerow({
                'Customer': customer_info['customer_name'],
                'Tenant ID': customer_info['tenant_id'],
                'Simulation ID': simulation.get('id', ''),
                'Display Name': simulation.get('displayName', ''),
                'Status': simulation.get('status', ''),
                'Attack Type': simulation.get('attackType', ''),
                'Created Date': simulation.get('createdDateTime', ''),
                'Launch Date': simulation.get('launchDateTime', ''),
                'End Date': simulation.get('completionDateTime', ''),
                'Users Count': len(simulation.get('includedAccountTarget', {}).get('addressees', [])),
                'Export Date': datetime.now().isoformat()
            })
    
    print(f"✅ Attack simulations exported to: {filename}")
    return len(data['value'])

def export_secure_score(access_token, customer_info):
    """Export Microsoft Secure Score data."""
    print("📈 Exporting Secure Score Data...")
    
    endpoint = f"{GRAPH_BASE_URL}/security/secureScores"
    params = {'$top': 1}
    
    data = make_graph_request(access_token, endpoint, params)
    if not data or 'value' not in data or len(data['value']) == 0:
        print("⚠️  No secure score data found")
        return
    
    filename = f"defender_xdr_secure_score_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Customer', 'Tenant ID', 'Current Score', 'Max Score', 'Percentage', 
            'Created Date', 'Enabled Services', 'Licensed Users', 'Export Date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        latest_score = data['value'][0]
        percentage = (latest_score.get('currentScore', 0) / latest_score.get('maxScore', 1)) * 100 if latest_score.get('maxScore', 0) > 0 else 0
        
        writer.writerow({
            'Customer': customer_info['customer_name'],
            'Tenant ID': customer_info['tenant_id'],
            'Current Score': latest_score.get('currentScore', 0),
            'Max Score': latest_score.get('maxScore', 0),
            'Percentage': f"{percentage:.1f}%",
            'Created Date': latest_score.get('createdDateTime', ''),
            'Enabled Services': ', '.join(latest_score.get('enabledServices', [])),
            'Licensed Users': latest_score.get('licensedUserCount', 0),
            'Export Date': datetime.now().isoformat()
        })
    
    print(f"✅ Secure score exported to: {filename}")
    return 1

def main():
    """Main function to run the Defender XDR audit."""
    print("🛡️  Starting Defender XDR Audit")
    print("=" * 50)
    
    # Validate environment variables
    if not TENANT_ID and not SUBSCRIPTION_ID:
        print("❌ Error: Either AZURE_TENANT_ID or AZURE_SUBSCRIPTION_ID must be set")
        sys.exit(1)
    
    try:
        # Get credentials
        credential = get_azure_credential()
        
        # Get customer information
        customer_info = get_customer_info(credential)
        print(f"🏢 Customer: {customer_info['customer_name']}")
        print(f"🆔 Tenant ID: {customer_info['tenant_id']}")
        print("")
        
        # Get access token for Microsoft Graph
        access_token = get_access_token(credential)
        
        # Export data
        total_items = 0
        
        alerts_count = export_security_alerts(access_token, customer_info)
        if alerts_count:
            total_items += alerts_count
        
        incidents_count = export_security_incidents(access_token, customer_info)
        if incidents_count:
            total_items += incidents_count
        
        simulations_count = export_attack_simulation_trainings(access_token, customer_info)
        if simulations_count:
            total_items += simulations_count
        
        score_count = export_secure_score(access_token, customer_info)
        if score_count:
            total_items += score_count
        
        print("")
        print("=" * 50)
        print(f"✅ Defender XDR audit completed successfully!")
        print(f"📊 Total items exported: {total_items}")
        print(f"📁 Files created in current directory")
        print("=" * 50)
        
    except AzureError as e:
        print(f"❌ Azure authentication error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()