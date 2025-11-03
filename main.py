"""Main entry point for Microsoft Sentinel Audit and Update Tool."""

import logging
import sys
from typing import Optional
from tabulate import tabulate
from config import SentinelConfig
from auth import get_azure_credential
from data_connectors import DataConnectorAuditor
from analytic_rules import AnalyticRuleAuditor
from deployment import SentinelDeployment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sentinel_audit.log')
    ]
)

logger = logging.getLogger(__name__)


def print_section_header(title: str) -> None:
    """Print a formatted section header.
    
    Args:
        title: Section title to display.
    """
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def audit_data_connectors(auditor: DataConnectorAuditor) -> None:
    """Audit data connectors and display results.
    
    Args:
        auditor: Data connector auditor instance.
    """
    print_section_header("DATA CONNECTORS AUDIT")
    
    try:
        connectors = auditor.list_data_connectors()
        
        if not connectors:
            print("No data connectors found.")
            return
        
        # Prepare table data
        table_data = [
            [
                connector['name'],
                connector['kind'],
                connector['type'].split('/')[-1]
            ]
            for connector in connectors
        ]
        
        print(tabulate(
            table_data,
            headers=['Name', 'Kind', 'Type'],
            tablefmt='grid'
        ))
        
        print(f"\nTotal data connectors: {len(connectors)}")
        
        # Check for updates (placeholder functionality)
        print("\nChecking for available updates...")
        for connector in connectors[:3]:  # Check first 3 as example
            update_info = auditor.check_connector_updates(connector['id'])
            print(f"  - {connector['name']}: {update_info['message']}")
        
    except Exception as e:
        logger.error(f"Error during data connector audit: {str(e)}")
        print(f"Error: {str(e)}")


def audit_analytic_rules(auditor: AnalyticRuleAuditor) -> None:
    """Audit analytic rules and display results.
    
    Args:
        auditor: Analytic rule auditor instance.
    """
    print_section_header("ANALYTIC RULES AUDIT")
    
    try:
        rules = auditor.list_analytic_rules()
        
        if not rules:
            print("No analytic rules found.")
            return
        
        # Prepare table data
        table_data = [
            [
                rule.get('display_name', rule['name']),
                rule['kind'],
                rule.get('severity', 'N/A'),
                'Enabled' if rule.get('enabled', False) else 'Disabled',
                ', '.join(rule.get('tactics', [])) if rule.get('tactics') else 'N/A'
            ]
            for rule in rules
        ]
        
        print(tabulate(
            table_data,
            headers=['Display Name', 'Kind', 'Severity', 'Status', 'Tactics'],
            tablefmt='grid'
        ))
        
        print(f"\nTotal analytic rules: {len(rules)}")
        
        # Count by status
        enabled_count = sum(1 for rule in rules if rule.get('enabled', False))
        disabled_count = len(rules) - enabled_count
        print(f"  - Enabled: {enabled_count}")
        print(f"  - Disabled: {disabled_count}")
        
        # Count by severity
        severity_counts = {}
        for rule in rules:
            severity = rule.get('severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print("\nRules by severity:")
        for severity, count in sorted(severity_counts.items()):
            print(f"  - {severity}: {count}")
        
        # Check for updates (placeholder functionality)
        print("\nChecking for available updates...")
        for rule in rules[:3]:  # Check first 3 as example
            update_info = auditor.check_rule_updates(rule['id'])
            display_name = rule.get('display_name', rule['name'])
            print(f"  - {display_name}: {update_info['message']}")
        
    except Exception as e:
        logger.error(f"Error during analytic rules audit: {str(e)}")
        print(f"Error: {str(e)}")


def main() -> None:
    """Main function to run the Sentinel audit."""
    print_section_header("MICROSOFT SENTINEL AUDIT AND UPDATE TOOL")
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = SentinelConfig.from_env()
        
        if not config.validate():
            logger.error("Invalid configuration")
            print("Error: Invalid configuration. Please check your .env file.")
            return
        
        print(f"Subscription ID: {config.subscription_id}")
        print(f"Resource Group: {config.resource_group}")
        print(f"Workspace: {config.workspace_name}")
        
        # Get Azure credential
        logger.info("Authenticating with Azure...")
        credential = get_azure_credential(config)
        
        # Initialize auditors
        data_connector_auditor = DataConnectorAuditor(credential, config)
        analytic_rule_auditor = AnalyticRuleAuditor(credential, config)
        deployment_handler = SentinelDeployment(credential, config)
        
        # Run audits
        audit_data_connectors(data_connector_auditor)
        audit_analytic_rules(analytic_rule_auditor)
        
        print_section_header("AUDIT COMPLETE")
        print("For deployment functionality, use the deployment module.")
        print("Check the logs for detailed information: sentinel_audit.log")
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"\nConfiguration Error: {str(e)}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file based on .env.example")
        print("2. Set all required environment variables")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        print("Check sentinel_audit.log for detailed error information.")


if __name__ == "__main__":
    main()
