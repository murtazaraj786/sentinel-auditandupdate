"""Utility functions for comparing and analyzing Sentinel resources."""

import logging
import json
import csv
from typing import Dict, Any, List, Tuple, Optional
from difflib import unified_diff
from datetime import datetime

logger = logging.getLogger(__name__)


class ResourceComparator:
    """Utility class for comparing Sentinel resources."""
    
    @staticmethod
    def compare_rule_properties(current: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current rule with template to identify differences.
        
        Args:
            current: Current rule properties.
            template: Template rule properties.
            
        Returns:
            Dictionary containing differences.
        """
        differences = {
            'has_changes': False,
            'changes': []
        }
        
        # Properties to compare
        comparable_props = [
            'display_name', 'description', 'severity', 'tactics', 
            'techniques', 'query', 'query_frequency', 'query_period',
            'trigger_operator', 'trigger_threshold', 'enabled'
        ]
        
        for prop in comparable_props:
            current_value = current.get(prop)
            template_value = template.get(prop)
            
            if current_value != template_value:
                differences['has_changes'] = True
                differences['changes'].append({
                    'property': prop,
                    'current': current_value,
                    'template': template_value
                })
        
        return differences
    
    @staticmethod
    def get_query_diff(current_query: str, template_query: str) -> str:
        """Generate a unified diff between two KQL queries.
        
        Args:
            current_query: Current KQL query.
            template_query: Template KQL query.
            
        Returns:
            Unified diff string.
        """
        current_lines = current_query.splitlines(keepends=True) if current_query else []
        template_lines = template_query.splitlines(keepends=True) if template_query else []
        
        diff = unified_diff(
            current_lines,
            template_lines,
            fromfile='Current Query',
            tofile='Template Query',
            lineterm=''
        )
        
        return '\n'.join(diff)
    
    @staticmethod
    def format_changes_summary(differences: Dict[str, Any]) -> str:
        """Format differences into a readable summary.
        
        Args:
            differences: Dictionary of differences from compare_rule_properties.
            
        Returns:
            Formatted string summary.
        """
        if not differences.get('has_changes'):
            return "No changes detected"
        
        lines = ["Changes detected:"]
        lines.append("-" * 60)
        
        for change in differences['changes']:
            prop = change['property'].replace('_', ' ').title()
            current = change['current']
            template = change['template']
            
            lines.append(f"\n{prop}:")
            lines.append(f"  Current:  {current}")
            lines.append(f"  Template: {template}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def compare_tactics_techniques(current: List[str], template: List[str]) -> Dict[str, List[str]]:
        """Compare tactics and techniques between current and template.
        
        Args:
            current: Current list of tactics/techniques.
            template: Template list of tactics/techniques.
            
        Returns:
            Dictionary with added, removed, and unchanged items.
        """
        current_set = set(current) if current else set()
        template_set = set(template) if template else set()
        
        return {
            'added': list(template_set - current_set),
            'removed': list(current_set - template_set),
            'unchanged': list(current_set & template_set)
        }


class VersionComparator:
    """Utility class for comparing version strings."""
    
    @staticmethod
    def parse_version(version: str) -> Tuple[int, ...]:
        """Parse a version string into a tuple of integers.
        
        Args:
            version: Version string (e.g., "1.2.3").
            
        Returns:
            Tuple of version numbers.
        """
        try:
            parts = version.split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        except Exception as e:
            logger.warning(f"Error parsing version '{version}': {str(e)}")
            return (0,)
    
    @staticmethod
    def compare(version1: str, version2: str) -> int:
        """Compare two version strings.
        
        Args:
            version1: First version string.
            version2: Second version string.
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2.
        """
        v1_tuple = VersionComparator.parse_version(version1)
        v2_tuple = VersionComparator.parse_version(version2)
        
        # Pad shorter version with zeros
        max_len = max(len(v1_tuple), len(v2_tuple))
        v1_tuple = v1_tuple + (0,) * (max_len - len(v1_tuple))
        v2_tuple = v2_tuple + (0,) * (max_len - len(v2_tuple))
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    
    @staticmethod
    def is_newer(current: str, available: str) -> bool:
        """Check if available version is newer than current.
        
        Args:
            current: Current version string.
            available: Available version string.
            
        Returns:
            True if available is newer.
        """
        return VersionComparator.compare(current, available) < 0


class ChangeAnalyzer:
    """Analyze changes and provide insights."""
    
    @staticmethod
    def analyze_severity_change(current: str, template: str) -> Dict[str, Any]:
        """Analyze severity level change.
        
        Args:
            current: Current severity.
            template: Template severity.
            
        Returns:
            Analysis of the change.
        """
        severity_order = ['Informational', 'Low', 'Medium', 'High', 'Critical']
        
        try:
            current_idx = severity_order.index(current)
            template_idx = severity_order.index(template)
            
            if template_idx > current_idx:
                return {
                    'change_type': 'increased',
                    'impact': 'higher',
                    'recommendation': 'Review: Severity has been upgraded, indicating potentially more critical threat.'
                }
            elif template_idx < current_idx:
                return {
                    'change_type': 'decreased',
                    'impact': 'lower',
                    'recommendation': 'Review: Severity has been downgraded, threat assessment may have changed.'
                }
            else:
                return {
                    'change_type': 'unchanged',
                    'impact': 'none',
                    'recommendation': 'No severity change.'
                }
        except ValueError:
            return {
                'change_type': 'unknown',
                'impact': 'unknown',
                'recommendation': 'Unable to compare severity levels.'
            }
    
    @staticmethod
    def assess_update_risk(differences: Dict[str, Any]) -> str:
        """Assess the risk level of applying an update.
        
        Args:
            differences: Dictionary of differences.
            
        Returns:
            Risk level (Low, Medium, High).
        """
        if not differences.get('has_changes'):
            return 'None'
        
        changes = differences.get('changes', [])
        
        # High risk properties
        high_risk_props = ['query', 'trigger_threshold', 'trigger_operator']
        # Medium risk properties
        medium_risk_props = ['severity', 'tactics', 'techniques', 'query_frequency']
        
        has_high_risk = any(c['property'] in high_risk_props for c in changes)
        has_medium_risk = any(c['property'] in medium_risk_props for c in changes)
        
        if has_high_risk:
            return 'High - Query or detection logic changed'
        elif has_medium_risk:
            return 'Medium - Classification or frequency changed'
        else:
            return 'Low - Only metadata changed'
    
    @staticmethod
    def generate_change_summary(rule_name: str, differences: Dict[str, Any]) -> str:
        """Generate a comprehensive change summary.
        
        Args:
            rule_name: Name of the rule.
            differences: Differences dictionary.
            
        Returns:
            Formatted change summary.
        """
        lines = [
            f"\n{'=' * 80}",
            f"  CHANGE SUMMARY: {rule_name}",
            f"{'=' * 80}",
            ""
        ]
        
        risk = ChangeAnalyzer.assess_update_risk(differences)
        lines.append(f"Risk Assessment: {risk}")
        lines.append("")
        
        if not differences.get('has_changes'):
            lines.append("No changes detected.")
            return '\n'.join(lines)
        
        lines.append("Properties Changed:")
        lines.append("-" * 80)
        
        for change in differences['changes']:
            prop = change['property'].replace('_', ' ').title()
            lines.append(f"\n• {prop}")
            
            # Special handling for certain properties
            if change['property'] == 'severity':
                current = change['current']
                template = change['template']
                analysis = ChangeAnalyzer.analyze_severity_change(current, template)
                lines.append(f"  Current:  {current}")
                lines.append(f"  New:      {template}")
                lines.append(f"  Impact:   {analysis['recommendation']}")
                
            elif change['property'] in ['tactics', 'techniques']:
                current = change['current'] or []
                template = change['template'] or []
                comparison = ResourceComparator.compare_tactics_techniques(current, template)
                
                if comparison['added']:
                    lines.append(f"  Added: {', '.join(comparison['added'])}")
                if comparison['removed']:
                    lines.append(f"  Removed: {', '.join(comparison['removed'])}")
                if comparison['unchanged']:
                    lines.append(f"  Unchanged: {', '.join(comparison['unchanged'])}")
                    
            else:
                lines.append(f"  Current: {change['current']}")
                lines.append(f"  New:     {change['template']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return '\n'.join(lines)


def export_comparison_report(comparisons: List[Dict[str, Any]], filename: str = "comparison_report.json") -> bool:
    """Export comparison results to a JSON file.
    
    Args:
        comparisons: List of comparison results.
        filename: Output filename.
        
    Returns:
        True if export was successful.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(comparisons, f, indent=2, default=str)
        
        logger.info(f"Comparison report exported to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting comparison report: {str(e)}")
        return False


class CSVExporter:
    """Utility class for exporting data to CSV format."""
    
    @staticmethod
    def export_analytic_rules(rules: List[Dict[str, Any]], filename: str = None) -> str:
        """Export analytic rules to CSV.
        
        Args:
            rules: List of analytic rule dictionaries.
            filename: Output filename (auto-generated if not provided).
            
        Returns:
            Filename of the exported CSV.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytic_rules_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not rules:
                    logger.warning("No rules to export")
                    return filename
                
                # Define headers
                fieldnames = [
                    'name', 'display_name', 'kind', 'severity', 'enabled', 
                    'tactics', 'techniques', 'description', 'id'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for rule in rules:
                    # Convert lists to comma-separated strings
                    row = rule.copy()
                    if 'tactics' in row and isinstance(row['tactics'], list):
                        row['tactics'] = ', '.join(row['tactics'])
                    if 'techniques' in row and isinstance(row['techniques'], list):
                        row['techniques'] = ', '.join(row['techniques'])
                    
                    writer.writerow(row)
            
            logger.info(f"Exported {len(rules)} rules to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting rules to CSV: {str(e)}")
            raise
    
    @staticmethod
    def export_data_connectors(connectors: List[Dict[str, Any]], filename: str = None) -> str:
        """Export data connectors to CSV.
        
        Args:
            connectors: List of data connector dictionaries.
            filename: Output filename (auto-generated if not provided).
            
        Returns:
            Filename of the exported CSV.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_connectors_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not connectors:
                    logger.warning("No connectors to export")
                    return filename
                
                fieldnames = ['name', 'kind', 'type', 'id', 'etag']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for connector in connectors:
                    writer.writerow(connector)
            
            logger.info(f"Exported {len(connectors)} connectors to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting connectors to CSV: {str(e)}")
            raise
    
    @staticmethod
    def export_solution_updates(updates: List[Dict[str, Any]], filename: str = None) -> str:
        """Export solution updates to CSV.
        
        Args:
            updates: List of solution update dictionaries.
            filename: Output filename (auto-generated if not provided).
            
        Returns:
            Filename of the exported CSV.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solution_updates_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not updates:
                    logger.warning("No solution updates to export")
                    return filename
                
                fieldnames = [
                    'solution_name', 'current_version', 'available_version', 
                    'publisher', 'package_id', 'installed_id'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for update in updates:
                    writer.writerow(update)
            
            logger.info(f"Exported {len(updates)} solution updates to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting solution updates to CSV: {str(e)}")
            raise
    
    @staticmethod
    def export_rule_updates(updates: List[Dict[str, Any]], filename: str = None) -> str:
        """Export analytic rule updates to CSV.
        
        Args:
            updates: List of rule update dictionaries.
            filename: Output filename (auto-generated if not provided).
            
        Returns:
            Filename of the exported CSV.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rule_updates_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not updates:
                    logger.warning("No rule updates to export")
                    return filename
                
                fieldnames = [
                    'rule_name', 'rule_id', 'current_severity', 'template_severity',
                    'tactics', 'template_id', 'update_type'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for update in updates:
                    row = update.copy()
                    if 'tactics' in row and isinstance(row['tactics'], list):
                        row['tactics'] = ', '.join(row['tactics'])
                    writer.writerow(row)
            
            logger.info(f"Exported {len(updates)} rule updates to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting rule updates to CSV: {str(e)}")
            raise
    
    @staticmethod
    def export_deployment_results(results: List[Dict[str, Any]], filename: str = None) -> str:
        """Export deployment results to CSV.
        
        Args:
            results: List of deployment result dictionaries.
            filename: Output filename (auto-generated if not provided).
            
        Returns:
            Filename of the exported CSV.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"deployment_results_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not results:
                    logger.warning("No deployment results to export")
                    return filename
                
                fieldnames = [
                    'type', 'item_name', 'success', 'message', 'note', 'timestamp'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {
                        'type': result.get('type', 'unknown'),
                        'item_name': (
                            result.get('update', {}).get('solution_name') or
                            result.get('update', {}).get('rule_name') or
                            result.get('update', {}).get('connector_name', 'Unknown')
                        ),
                        'success': result.get('result', {}).get('success', False),
                        'message': result.get('result', {}).get('message', ''),
                        'note': result.get('result', {}).get('note', ''),
                        'timestamp': datetime.now().isoformat()
                    }
                    writer.writerow(row)
            
            logger.info(f"Exported {len(results)} deployment results to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting deployment results to CSV: {str(e)}")
            raise
    
    @staticmethod
    def export_all_updates(detected_updates: Dict[str, List[Dict[str, Any]]], 
                          output_dir: str = ".") -> Dict[str, str]:
        """Export all detected updates to separate CSV files.
        
        Args:
            detected_updates: Dictionary with 'solutions', 'rules', 'connectors' keys.
            output_dir: Output directory for CSV files.
            
        Returns:
            Dictionary mapping update type to exported filename.
        """
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Export solutions
            if detected_updates.get('solutions'):
                filename = f"{output_dir}/solution_updates_{timestamp}.csv"
                CSVExporter.export_solution_updates(detected_updates['solutions'], filename)
                exported_files['solutions'] = filename
            
            # Export rules
            if detected_updates.get('rules'):
                filename = f"{output_dir}/rule_updates_{timestamp}.csv"
                CSVExporter.export_rule_updates(detected_updates['rules'], filename)
                exported_files['rules'] = filename
            
            # Export connectors (if any)
            if detected_updates.get('connectors'):
                filename = f"{output_dir}/connector_updates_{timestamp}.csv"
                # Create a simple export for connectors
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, 
                                          fieldnames=['connector_name', 'update_info'])
                    writer.writeheader()
                    for connector in detected_updates['connectors']:
                        writer.writerow(connector)
                exported_files['connectors'] = filename
            
            logger.info(f"Exported all updates to {len(exported_files)} CSV files")
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting all updates: {str(e)}")
            raise
