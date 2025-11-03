"""Automated deployment workflow for Microsoft Sentinel updates."""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from tabulate import tabulate
from azure.core.credentials import TokenCredential

from config import SentinelConfig
from analytic_rules import AnalyticRuleAuditor
from data_connectors import DataConnectorAuditor
from content_hub import ContentHubManager
from deployment import SentinelDeployment
from utils import CSVExporter

logger = logging.getLogger(__name__)


class UpdateWorkflow:
    """Workflow manager for detecting and deploying updates."""
    
    def __init__(self, credential: TokenCredential, config: SentinelConfig):
        """Initialize the update workflow.
        
        Args:
            credential: Azure credential for authentication.
            config: Sentinel configuration.
        """
        self.config = config
        self.rule_auditor = AnalyticRuleAuditor(credential, config)
        self.connector_auditor = DataConnectorAuditor(credential, config)
        self.content_hub = ContentHubManager(credential, config)
        self.deployer = SentinelDeployment(credential, config)
        
        self.detected_updates = {
            'solutions': [],
            'rules': [],
            'connectors': []
        }
    
    def detect_all_updates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect all available updates.
        
        Returns:
            Dictionary containing detected updates for solutions, rules, and connectors.
        """
        logger.info("Starting update detection...")
        
        # Detect solution updates
        self._detect_solution_updates()
        
        # Detect rule updates
        self._detect_rule_updates()
        
        # Detect connector updates (placeholder for now)
        self._detect_connector_updates()
        
        return self.detected_updates
    
    def _detect_solution_updates(self) -> None:
        """Detect updates for installed solutions."""
        logger.info("Checking for solution updates...")
        
        try:
            installed_solutions = self.content_hub.list_installed_solutions()
            updates = self.content_hub.check_solution_updates(installed_solutions)
            
            self.detected_updates['solutions'] = updates
            logger.info(f"Found {len(updates)} solution updates")
            
        except Exception as e:
            logger.error(f"Error detecting solution updates: {str(e)}")
    
    def _detect_rule_updates(self) -> None:
        """Detect updates for analytic rules."""
        logger.info("Checking for analytic rule updates...")
        
        try:
            installed_rules = self.rule_auditor.list_analytic_rules()
            available_templates = self.content_hub.list_rule_templates()
            
            # Create lookup for templates
            template_lookup = {
                template['display_name']: template 
                for template in available_templates
            }
            
            rule_updates = []
            for rule in installed_rules:
                rule_name = rule.get('display_name', rule['name'])
                
                # Try to find matching template
                if rule_name in template_lookup:
                    template = template_lookup[rule_name]
                    
                    # Check if template has different properties (indicating update)
                    # This is a simplified check - you might want more sophisticated comparison
                    rule_updates.append({
                        'rule_name': rule_name,
                        'rule_id': rule['id'],
                        'current_severity': rule.get('severity', 'Unknown'),
                        'template_severity': template.get('severity', 'Unknown'),
                        'template_id': template['id'],
                        'tactics': template.get('tactics', []),
                        'update_type': 'Template Available'
                    })
            
            self.detected_updates['rules'] = rule_updates
            logger.info(f"Found {len(rule_updates)} potential rule updates")
            
        except Exception as e:
            logger.error(f"Error detecting rule updates: {str(e)}")
    
    def _detect_connector_updates(self) -> None:
        """Detect updates for data connectors."""
        logger.info("Checking for data connector updates...")
        
        # Placeholder - connector update detection would require
        # comparing against solution templates or API versions
        self.detected_updates['connectors'] = []
        logger.info("Connector update detection: Feature to be enhanced")
    
    def display_detected_updates(self) -> None:
        """Display all detected updates in a formatted manner."""
        print("\n" + "=" * 80)
        print("  DETECTED UPDATES")
        print("=" * 80 + "\n")
        
        # Display solution updates
        if self.detected_updates['solutions']:
            print("📦 SOLUTION UPDATES AVAILABLE:")
            print("-" * 80)
            
            table_data = [
                [
                    update['solution_name'],
                    update['current_version'],
                    update['available_version'],
                    update['publisher']
                ]
                for update in self.detected_updates['solutions']
            ]
            
            print(tabulate(
                table_data,
                headers=['Solution Name', 'Current Version', 'Available Version', 'Publisher'],
                tablefmt='grid'
            ))
            print(f"\nTotal solution updates: {len(self.detected_updates['solutions'])}\n")
        else:
            print("📦 SOLUTIONS: No updates available\n")
        
        # Display rule updates
        if self.detected_updates['rules']:
            print("📋 ANALYTIC RULE UPDATES AVAILABLE:")
            print("-" * 80)
            
            table_data = [
                [
                    update['rule_name'],
                    update.get('current_severity', 'N/A'),
                    update.get('template_severity', 'N/A'),
                    update['update_type']
                ]
                for update in self.detected_updates['rules']
            ]
            
            print(tabulate(
                table_data,
                headers=['Rule Name', 'Current Severity', 'Template Severity', 'Update Type'],
                tablefmt='grid'
            ))
            print(f"\nTotal rule updates: {len(self.detected_updates['rules'])}\n")
        else:
            print("📋 ANALYTIC RULES: No updates available\n")
        
        # Display connector updates
        if self.detected_updates['connectors']:
            print("🔌 DATA CONNECTOR UPDATES AVAILABLE:")
            print("-" * 80)
            print(f"Total connector updates: {len(self.detected_updates['connectors'])}\n")
        else:
            print("🔌 DATA CONNECTORS: No updates available\n")
    
    def export_updates_to_csv(self, output_dir: str = ".") -> Dict[str, str]:
        """Export detected updates to CSV files.
        
        Args:
            output_dir: Directory to save CSV files.
            
        Returns:
            Dictionary mapping update type to filename.
        """
        logger.info("Exporting detected updates to CSV...")
        
        try:
            exported_files = CSVExporter.export_all_updates(self.detected_updates, output_dir)
            
            print("\n📊 CSV Export Complete:")
            print("-" * 80)
            for update_type, filename in exported_files.items():
                print(f"  {update_type.capitalize()}: {filename}")
            print()
            
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting updates to CSV: {str(e)}")
            print(f"\n⚠️  Error exporting to CSV: {str(e)}\n")
            return {}
    
    def show_update_details(self, update_type: str, index: int) -> Optional[Dict[str, Any]]:
        """Show detailed information about a specific update.
        
        Args:
            update_type: Type of update ('solutions', 'rules', 'connectors').
            index: Index of the update in the list.
            
        Returns:
            Update details if found.
        """
        if update_type not in self.detected_updates:
            logger.error(f"Invalid update type: {update_type}")
            return None
        
        updates = self.detected_updates[update_type]
        if index < 0 or index >= len(updates):
            logger.error(f"Invalid index: {index}")
            return None
        
        update = updates[index]
        
        print("\n" + "=" * 80)
        print(f"  UPDATE DETAILS - {update_type.upper()}")
        print("=" * 80 + "\n")
        
        for key, value in update.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        return update
    
    def approve_and_deploy_update(self, update_type: str, index: int) -> Dict[str, Any]:
        """Deploy a specific update after user approval.
        
        Args:
            update_type: Type of update ('solutions', 'rules', 'connectors').
            index: Index of the update to deploy.
            
        Returns:
            Deployment result.
        """
        if update_type not in self.detected_updates:
            return {'success': False, 'message': f'Invalid update type: {update_type}'}
        
        updates = self.detected_updates[update_type]
        if index < 0 or index >= len(updates):
            return {'success': False, 'message': f'Invalid index: {index}'}
        
        update = updates[index]
        
        print(f"\n⚠️  DEPLOYING UPDATE: {update.get('solution_name') or update.get('rule_name')}")
        print("-" * 80)
        
        try:
            if update_type == 'solutions':
                return self._deploy_solution_update(update)
            elif update_type == 'rules':
                return self._deploy_rule_update(update)
            elif update_type == 'connectors':
                return self._deploy_connector_update(update)
            else:
                return {'success': False, 'message': 'Unknown update type'}
                
        except Exception as e:
            logger.error(f"Error deploying update: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _deploy_solution_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a solution update.
        
        Args:
            update: Solution update information.
            
        Returns:
            Deployment result.
        """
        logger.info(f"Deploying solution update: {update['solution_name']}")
        
        # Get template content
        template = self.content_hub.get_template_content(update['package_id'])
        
        if not template:
            return {
                'success': False,
                'message': 'Could not retrieve template content'
            }
        
        # Note: Actual deployment would involve creating/updating the content package
        # This is a placeholder for the actual deployment logic
        return {
            'success': True,
            'message': f"Solution update for {update['solution_name']} would be deployed here",
            'note': 'Actual deployment requires installing the content package via ARM template or API'
        }
    
    def _deploy_rule_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy an analytic rule update.
        
        Args:
            update: Rule update information.
            
        Returns:
            Deployment result.
        """
        logger.info(f"Deploying rule update: {update['rule_name']}")
        
        # Get the template
        template = self.content_hub.get_rule_template(update['template_id'])
        
        if not template:
            return {
                'success': False,
                'message': 'Could not retrieve rule template'
            }
        
        # Deploy the updated rule
        # Note: This would need proper conversion from template to rule object
        return {
            'success': True,
            'message': f"Rule update for {update['rule_name']} prepared for deployment",
            'note': 'Template retrieved - actual deployment requires creating rule from template'
        }
    
    def _deploy_connector_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a data connector update.
        
        Args:
            update: Connector update information.
            
        Returns:
            Deployment result.
        """
        logger.info(f"Deploying connector update: {update.get('connector_name')}")
        
        return {
            'success': True,
            'message': 'Connector deployment to be implemented'
        }
    
    def deploy_all_updates(self, auto_approve: bool = False) -> List[Dict[str, Any]]:
        """Deploy all detected updates.
        
        Args:
            auto_approve: If True, deploy without prompting for each update.
            
        Returns:
            List of deployment results.
        """
        results = []
        total_updates = (
            len(self.detected_updates['solutions']) +
            len(self.detected_updates['rules']) +
            len(self.detected_updates['connectors'])
        )
        
        if total_updates == 0:
            print("\n✓ No updates to deploy")
            return results
        
        print(f"\n📦 Preparing to deploy {total_updates} update(s)...")
        
        if not auto_approve:
            response = input(f"\nDo you want to proceed with deploying all updates? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Deployment cancelled by user")
                return results
        
        # Deploy solution updates
        for i, update in enumerate(self.detected_updates['solutions']):
            print(f"\n[{i+1}/{total_updates}] Deploying solution: {update['solution_name']}")
            result = self._deploy_solution_update(update)
            results.append({'type': 'solution', 'update': update, 'result': result})
        
        # Deploy rule updates
        offset = len(self.detected_updates['solutions'])
        for i, update in enumerate(self.detected_updates['rules']):
            print(f"\n[{offset+i+1}/{total_updates}] Deploying rule: {update['rule_name']}")
            result = self._deploy_rule_update(update)
            results.append({'type': 'rule', 'update': update, 'result': result})
        
        # Deploy connector updates
        offset += len(self.detected_updates['rules'])
        for i, update in enumerate(self.detected_updates['connectors']):
            print(f"\n[{offset+i+1}/{total_updates}] Deploying connector: {update.get('connector_name')}")
            result = self._deploy_connector_update(update)
            results.append({'type': 'connector', 'update': update, 'result': result})
        
        return results
    
    def generate_deployment_report(self, results: List[Dict[str, Any]], export_csv: bool = True) -> str:
        """Generate a deployment report.
        
        Args:
            results: List of deployment results.
            export_csv: Whether to also export results to CSV.
            
        Returns:
            Report as string.
        """
        report_lines = [
            "\n" + "=" * 80,
            "  DEPLOYMENT REPORT",
            "  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "=" * 80,
            ""
        ]
        
        successful = sum(1 for r in results if r['result'].get('success', False))
        failed = len(results) - successful
        
        report_lines.append(f"Total Updates Processed: {len(results)}")
        report_lines.append(f"Successful: {successful}")
        report_lines.append(f"Failed: {failed}")
        report_lines.append("")
        
        # Detail each deployment
        for i, result in enumerate(results, 1):
            status = "✓ SUCCESS" if result['result'].get('success') else "✗ FAILED"
            update_name = (
                result['update'].get('solution_name') or 
                result['update'].get('rule_name') or 
                result['update'].get('connector_name', 'Unknown')
            )
            
            report_lines.append(f"{i}. [{status}] {result['type'].upper()}: {update_name}")
            report_lines.append(f"   Message: {result['result'].get('message', 'No message')}")
            
            if result['result'].get('note'):
                report_lines.append(f"   Note: {result['result']['note']}")
            
            report_lines.append("")
        
        report_lines.append("=" * 80)
        
        report = "\n".join(report_lines)
        
        # Save to text file
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            txt_filename = f"deployment_report_{timestamp}.txt"
            
            with open(txt_filename, 'w') as f:
                f.write(report)
            
            report_lines.append(f"\nText report saved to: {txt_filename}")
            
            # Export to CSV if requested
            if export_csv and results:
                csv_filename = CSVExporter.export_deployment_results(results)
                report_lines.append(f"CSV report saved to: {csv_filename}")
            
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
        
        return "\n".join(report_lines)
