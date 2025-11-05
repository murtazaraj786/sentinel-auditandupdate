#!/usr/bin/env python3
"""
Test script for Defender XDR Audit Tool
Validates authentication and basic connectivity
"""

import os
import sys
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
import requests

def test_azure_authentication():
    """Test Azure authentication."""
    print("🔐 Testing Azure Authentication...")
    
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://graph.microsoft.com/.default")
        
        if token:
            print("✅ Azure authentication successful")
            return True
        else:
            print("❌ Failed to get authentication token")
            return False
            
    except Exception as e:
        print(f"❌ Azure authentication failed: {e}")
        return False

def test_graph_connectivity():
    """Test Microsoft Graph API connectivity."""
    print("🌐 Testing Microsoft Graph API connectivity...")
    
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://graph.microsoft.com/.default")
        
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple endpoint
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Microsoft Graph API connectivity successful")
            user_data = response.json()
            print(f"   Connected as: {user_data.get('displayName', 'Unknown User')}")
            return True
        else:
            print(f"❌ Microsoft Graph API returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Microsoft Graph API connectivity failed: {e}")
        return False

def test_permissions():
    """Test required permissions for security endpoints."""
    print("🔑 Testing Security API permissions...")
    
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://graph.microsoft.com/.default")
        
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        # Test security alerts endpoint
        response = requests.get(
            "https://graph.microsoft.com/beta/security/alerts?$top=1",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Security alerts access successful")
            return True
        elif response.status_code == 403:
            print("❌ Insufficient permissions for security alerts")
            print("   Required: SecurityAlert.Read.All")
            return False
        else:
            print(f"❌ Security alerts endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Security permissions test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🛡️  Defender XDR Audit Tool - Connection Test")
    print("=" * 50)
    
    # Check environment variables
    tenant_id = os.getenv('AZURE_TENANT_ID')
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    
    print(f"📋 Environment Check:")
    print(f"   AZURE_TENANT_ID: {'✅ Set' if tenant_id else '❌ Missing'}")
    print(f"   AZURE_SUBSCRIPTION_ID: {'✅ Set' if subscription_id else '⚠️  Optional'}")
    print("")
    
    if not tenant_id and not subscription_id:
        print("❌ Either AZURE_TENANT_ID or AZURE_SUBSCRIPTION_ID must be set")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_azure_authentication():
        tests_passed += 1
    
    print("")
    
    if test_graph_connectivity():
        tests_passed += 1
    
    print("")
    
    if test_permissions():
        tests_passed += 1
    
    print("")
    print("=" * 50)
    
    if tests_passed == total_tests:
        print(f"✅ All tests passed ({tests_passed}/{total_tests})")
        print("🚀 Ready to run Defender XDR audit!")
    else:
        print(f"⚠️  Some tests failed ({tests_passed}/{total_tests})")
        print("🔧 Please check configuration and permissions")
        
        if tests_passed == 0:
            print("\n💡 Troubleshooting tips:")
            print("   1. Run 'az login' if using Azure CLI authentication")
            print("   2. Set AZURE_TENANT_ID environment variable")
            print("   3. Ensure your account has appropriate permissions")
    
    print("=" * 50)

if __name__ == "__main__":
    main()