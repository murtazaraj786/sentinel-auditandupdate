"""Main entry point for Microsoft Sentinel Audit and Update Tool."""

import logging
import sys
import argparse
from typing import Optional
from tabulate import tabulate
from config import SentinelConfig
from auth import get_azure_credential
from data_connectors import DataConnectorAuditor
from analytic_rules import AnalyticRuleAuditor
from deployment import SentinelDeployment
from content_hub import ContentHubManager
from workflow import UpdateWorkflow
from utils import CSVExporter

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


def run_update_workflow(config: SentinelConfig, credential, auto_approve: bool = False, export_csv: bool = True) -> None:
    """Run the automated update detection and deployment workflow.
    
    Args:
        config: Sentinel configuration.
        credential: Azure credential.
        auto_approve: If True, deploy all updates without prompting.
        export_csv: If True, export results to CSV.
    """
    print_section_header("UPDATE DETECTION AND DEPLOYMENT WORKFLOW")
    
    # Initialize workflow
    workflow = UpdateWorkflow(credential, config)
    
    # Detect updates
    print("🔍 Scanning for available updates...")
    updates = workflow.detect_all_updates()
    
    # Display detected updates
    workflow.display_detected_updates()
    
    # Export to CSV if requested
    if export_csv:
        total_updates = (
            len(updates['solutions']) +
            len(updates['rules']) +
            len(updates['connectors'])
        )
        
        if total_updates > 0:
            response = input("\n💾 Export detected updates to CSV? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                workflow.export_updates_to_csv()
    
    total_updates = (
        len(updates['solutions']) +
        len(updates['rules']) +
        len(updates['connectors'])
    )
    
    if total_updates == 0:
        print("✓ Your Sentinel workspace is up to date!")
        return
    
    # Ask user if they want to deploy
    print_section_header("DEPLOYMENT OPTIONS")
    print("1. Deploy all updates")
    print("2. Review and deploy individual updates")
    print("3. Skip deployment (audit only)")
    
    if auto_approve:
        choice = "1"
        print("\nAuto-approve enabled - deploying all updates...")
    else:
        choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Deploy all updates
        print_section_header("DEPLOYING ALL UPDATES")
        results = workflow.deploy_all_updates(auto_approve=auto_approve)
        
        # Generate and display report
        report = workflow.generate_deployment_report(results, export_csv=export_csv)
        print(report)
        
    elif choice == "2":
        # Interactive deployment
        print_section_header("INTERACTIVE DEPLOYMENT")
        
        # Deploy solutions
        for i, update in enumerate(updates['solutions']):
            print(f"\n--- Solution Update {i+1}/{len(updates['solutions'])} ---")
            workflow.show_update_details('solutions', i)
            
            response = input("\nDeploy this update? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                result = workflow.approve_and_deploy_update('solutions', i)
                print(f"Result: {result.get('message')}")
        
        # Deploy rules
        for i, update in enumerate(updates['rules']):
            print(f"\n--- Rule Update {i+1}/{len(updates['rules'])} ---")
            workflow.show_update_details('rules', i)
            
            response = input("\nDeploy this update? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                result = workflow.approve_and_deploy_update('rules', i)
                print(f"Result: {result.get('message')}")
        
        print("\n✓ Interactive deployment complete")
        
    else:
        print("\n✓ Audit complete - skipping deployment")
        print("You can run the tool again to deploy updates when ready.")


def run_audit_only(config: SentinelConfig, credential, export_csv: bool = True) -> None:
    """Run audit-only mode (original functionality).
    
    Args:
        config: Sentinel configuration.
        credential: Azure credential.
        export_csv: If True, offer to export results to CSV.
    """
    print_section_header("MICROSOFT SENTINEL AUDIT")
    
    # Initialize auditors
    data_connector_auditor = DataConnectorAuditor(credential, config)
    analytic_rule_auditor = AnalyticRuleAuditor(credential, config)
    
    # Run audits
    connectors = audit_data_connectors(data_connector_auditor)
    rules = audit_analytic_rules(analytic_rule_auditor)
    
    print_section_header("AUDIT COMPLETE")
    print("Run with --workflow flag to detect and deploy updates.")
    print("Check the logs for detailed information: sentinel_audit.log")
    
    # Offer CSV export
    if export_csv and (connectors or rules):
        print("\n" + "-" * 80)
        response = input("💾 Export audit results to CSV? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            try:
                exported_files = []
                
                if connectors:
                    filename = CSVExporter.export_data_connectors(connectors)
                    exported_files.append(filename)
                    print(f"  ✓ Data connectors exported to: {filename}")
                
                if rules:
                    filename = CSVExporter.export_analytic_rules(rules)
                    exported_files.append(filename)
                    print(f"  ✓ Analytic rules exported to: {filename}")
                
                print(f"\n📊 Exported {len(exported_files)} CSV file(s)")
                
            except Exception as e:
                print(f"⚠️  Error exporting to CSV: {str(e)}")


def audit_data_connectors(auditor: DataConnectorAuditor) -> list:
    """Audit data connectors and display results.
    
    Args:
        auditor: Data connector auditor instance.
        
    Returns:
        List of connectors.
    """
    print_section_header("DATA CONNECTORS AUDIT")
    
    try:
        connectors = auditor.list_data_connectors()
        
        if not connectors:
            print("No data connectors found.")
            return []
        
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
        
        return connectors
        
    except Exception as e:
        logger.error(f"Error during data connector audit: {str(e)}")
        print(f"Error: {str(e)}")
        return []


def audit_analytic_rules(auditor: AnalyticRuleAuditor) -> list:
    """Audit analytic rules and display results.
    
    Args:
        auditor: Analytic rule auditor instance.
        
    Returns:
        List of rules.
    """
    print_section_header("ANALYTIC RULES AUDIT")
    
    try:
        rules = auditor.list_analytic_rules()
        
        if not rules:
            print("No analytic rules found.")
            return []
        
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
        
        return rules
        
    except Exception as e:
        logger.error(f"Error during analytic rules audit: {str(e)}")
        print(f"Error: {str(e)}")
        return []


def main() -> None:
    """Main function to run the Sentinel audit and update tool."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Microsoft Sentinel Audit and Update Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Run audit only
  python main.py --workflow          # Detect updates with interactive deployment
  python main.py --workflow --auto   # Auto-deploy all updates
        """
    )
    
    parser.add_argument(
        '--workflow',
        action='store_true',
        help='Run update detection and deployment workflow'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-approve all updates (requires --workflow)'
    )
    
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Disable CSV export prompts'
    )
    
    args = parser.parse_args()
    
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
        
        # Determine CSV export preference
        export_csv = not args.no_csv
        
        # Run appropriate mode
        if args.workflow:
            run_update_workflow(config, credential, auto_approve=args.auto, export_csv=export_csv)
        else:
            run_audit_only(config, credential, export_csv=export_csv)
        
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
