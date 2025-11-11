# Azure Web Application Firewall (WAF) Audit Tool

This tool audits your Azure Web Application Firewall configurations across all WAF services and exports policies, rules, and analytics to CSV files.

## What it does

The Azure WAF audit exports the following data:

1. **Application Gateway WAF** - Regional WAF policies and configurations
2. **Front Door WAF** - Global WAF policies and edge protection rules  
3. **CDN WAF** - Content delivery network security policies
4. **WAF Summary** - Comprehensive analysis and recommendations

## Prerequisites

- Azure subscription with WAF services deployed
- Appropriate permissions to read WAF configurations  
- Python 3.8 or higher

## Required Permissions

Your account (or service principal) needs these Azure RBAC roles:

- `Reader` - Read Azure resources and configurations
- `Network Contributor` - (Optional) For more detailed network data

### Specific Azure Permissions

- `Microsoft.Network/applicationGateways/read`
- `Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies/read`
- `Microsoft.Cdn/profiles/read`
- `Microsoft.Cdn/profiles/securityPolicies/read`
- `Microsoft.Network/frontdoors/read`
- `Microsoft.Network/FrontDoorWebApplicationFirewallPolicies/read`

## Quick Setup

1. **Install dependencies:**

   ```powershell
   pip install -r waf_requirements.txt
   ```

2. **Set environment variables:**

   ```powershell
   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
   $env:AZURE_TENANT_ID = "your-tenant-id"
   $env:AUTH_MODE = "device"
   ```

3. **Run the audit:**

   ```powershell
   python azure_waf_audit.py
   ```

## Authentication Options

### Option 1: Azure CLI (Recommended for Testing)

```powershell
az login
$env:AZURE_TENANT_ID = "your-tenant-id"
python azure_waf_audit.py
```

### Option 2: Interactive Browser

```powershell
$env:AUTH_MODE = "browser"
$env:AZURE_TENANT_ID = "your-tenant-id"
python azure_waf_audit.py
```

### Option 3: Device Code

```powershell
$env:AUTH_MODE = "device"
$env:AZURE_TENANT_ID = "your-tenant-id"
python azure_waf_audit.py
```

### Option 4: Service Principal (For Automation)

```powershell
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_ID = "your-app-registration-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
python azure_waf_audit.py
```

## Output Files

The tool generates 4 CSV files with timestamps:

1. **`azure_waf_app_gateway_YYYYMMDD_HHMMSS.csv`** - Application Gateway WAF configurations
2. **`azure_waf_front_door_YYYYMMDD_HHMMSS.csv`** - Front Door WAF policies
3. **`azure_waf_cdn_YYYYMMDD_HHMMSS.csv`** - CDN WAF security policies
4. **`azure_waf_summary_YYYYMMDD_HHMMSS.csv`** - Summary analysis and recommendations

## Key Audit Areas

### Application Gateway WAF

- Regional load balancer protection
- Custom rules and exclusions
- OWASP rule set configurations
- SSL termination and certificates
- Backend pool health and routing

### Front Door WAF

- Global anycast protection
- Rate limiting and throttling rules
- Geo-filtering and IP restrictions
- DDoS protection integration
- Custom response codes and pages

### CDN WAF

- Edge location security policies
- Origin protection strategies
- Bot detection and mitigation
- Caching security headers
- Content delivery optimization

### Security Recommendations

- Policy mode analysis (Detection vs Prevention)
- Rule set version compliance
- Custom rule effectiveness
- Performance impact assessment
- Cost optimization opportunities

## Example Output

```
🔥 Starting Azure Web Application Firewall (WAF) Audit
======================================================================
🔐 Using Device Code authentication
📱 You'll be prompted to visit a URL and enter a code
🏢 Customer: Contoso Corporation
🆔 Subscription: 12345678-1234-1234-1234-123456789012
🔑 Tenant ID: 87654321-4321-4321-4321-210987654321

📁 Output directory: C:\audit-reports\output

🔥 Exporting Application Gateway WAF Configurations...
✅ Application Gateway WAF configurations exported to: azure_waf_app_gateway_20241111_143022.csv

🚪 Exporting Front Door WAF Configurations...
✅ Front Door WAF configurations exported to: azure_waf_front_door_20241111_143022.csv

🌐 Exporting CDN WAF Configurations...
✅ CDN WAF configurations exported to: azure_waf_cdn_20241111_143022.csv

📊 Generating WAF Summary and Recommendations...
✅ WAF summary exported to: azure_waf_summary_20241111_143022.csv

======================================================================
✅ Azure WAF audit completed successfully!
📊 Total WAF configurations found: 12
   🔥 Application Gateway WAF: 8
   🚪 Front Door WAF: 3
   🌐 CDN WAF: 1
📁 Reports saved in: C:\audit-reports\output
======================================================================
```

## WAF Service Comparison

| Service | Use Case | Scope | Key Features |
|---------|----------|-------|--------------|
| **Application Gateway WAF** | Regional apps | Single region | Layer 7 LB, SSL termination, Custom rules |
| **Front Door WAF** | Global apps | Multi-region | Global anycast, DDoS, Edge optimization |
| **CDN WAF** | Static content | Global CDN | Caching, Bot protection, Origin security |

## Troubleshooting

### Permission Issues

```
❌ Azure error: The client does not have authorization to perform action 'Microsoft.Network/applicationGateways/read'
```

**Solution:** Request `Reader` or `Network Contributor` role from subscription administrator.

### Authentication Problems

```
❌ Error: AZURE_SUBSCRIPTION_ID must be set
```

**Solution:** Set required environment variables as shown in setup section.

### No WAF Found

```
⚠️  No Application Gateway WAF configurations found
```

**Possible causes:**

- No WAF policies deployed in subscription
- WAF services not enabled
- Insufficient permissions to read network resources

## Integration with Existing Audit Suite

This tool integrates seamlessly with your existing security audit framework:

```powershell
# Run all audits together
cd "Sentinel Audit"
python sentinel_audit.py

cd "../Sentinel SOC Optimisation Audit"
python soc_optimization_audit.py

cd "../Defender XDR Audit"
python defender_xdr_audit.py

cd "../Defender for Cloud Audit"
python defender_cloud_audit.py

cd "../Azure WAF Audit"
python azure_waf_audit.py
```

## Best Practices

1. **Regular Review**: Audit WAF configurations monthly
2. **Rule Tuning**: Monitor false positives and adjust exclusions
3. **Performance Testing**: Verify WAF impact on application response times
4. **Compliance Mapping**: Align WAF rules with security requirements
5. **Cost Optimization**: Review request volumes and scaling needs
6. **Security Monitoring**: Correlate WAF logs with SIEM alerts

## WAF Security Checklist

- [ ] **Prevention Mode**: WAF policies set to block (not just detect)
- [ ] **Latest Rule Sets**: Using current OWASP CRS versions
- [ ] **Custom Rules**: Application-specific protection rules configured
- [ ] **Rate Limiting**: Appropriate throttling for your application
- [ ] **Geo-blocking**: Restrict access from unauthorized countries
- [ ] **SSL/TLS**: Proper certificate configuration and protocols
- [ ] **Logging**: WAF logs integrated with monitoring systems
- [ ] **Tuning**: Regular review of blocked vs allowed requests

## Support

For issues specific to this audit tool:

1. Check Azure permissions for WAF services
2. Verify subscription ID and authentication credentials
3. Review Azure Activity Log for API call errors
4. Test with minimal `Reader` permissions first
5. Check WAF service availability in your regions