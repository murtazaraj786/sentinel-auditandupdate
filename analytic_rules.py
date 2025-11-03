"""Module for auditing and managing Microsoft Sentinel analytic rules."""

import logging
from typing import List, Dict, Any, Optional
from azure.mgmt.securityinsight import SecurityInsights
from azure.core.credentials import TokenCredential
from config import SentinelConfig

logger = logging.getLogger(__name__)


class AnalyticRuleAuditor:
    """Auditor for Microsoft Sentinel analytic rules."""
    
    def __init__(self, credential: TokenCredential, config: SentinelConfig):
        """Initialize the analytic rule auditor.
        
        Args:
            credential: Azure credential for authentication.
            config: Sentinel configuration.
        """
        self.client = SecurityInsights(credential, config.subscription_id)
        self.config = config
    
    def list_analytic_rules(self) -> List[Dict[str, Any]]:
        """List all analytic rules in the Sentinel workspace.
        
        Returns:
            List of analytic rule details.
        """
        try:
            rules = []
            rule_list = self.client.alert_rules.list(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name
            )
            
            for rule in rule_list:
                rule_info = {
                    'id': rule.id,
                    'name': rule.name,
                    'type': rule.type,
                    'kind': rule.kind if hasattr(rule, 'kind') else 'Unknown',
                    'etag': rule.etag if hasattr(rule, 'etag') else None
                }
                
                # Add additional properties based on rule kind
                if hasattr(rule, 'display_name'):
                    rule_info['display_name'] = rule.display_name
                if hasattr(rule, 'enabled'):
                    rule_info['enabled'] = rule.enabled
                if hasattr(rule, 'severity'):
                    rule_info['severity'] = rule.severity
                if hasattr(rule, 'tactics'):
                    rule_info['tactics'] = rule.tactics
                
                rules.append(rule_info)
            
            logger.info(f"Found {len(rules)} analytic rules")
            return rules
            
        except Exception as e:
            logger.error(f"Error listing analytic rules: {str(e)}")
            raise
    
    def get_rule_details(self, rule_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific analytic rule.
        
        Args:
            rule_id: The ID of the analytic rule.
            
        Returns:
            Detailed rule information.
        """
        try:
            rule = self.client.alert_rules.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                rule_id=rule_id
            )
            
            rule_details = {
                'id': rule.id,
                'name': rule.name,
                'type': rule.type,
                'kind': rule.kind if hasattr(rule, 'kind') else 'Unknown'
            }
            
            # Extract all available properties
            for attr in ['display_name', 'description', 'enabled', 'severity', 
                        'tactics', 'techniques', 'query', 'query_frequency', 
                        'query_period', 'trigger_operator', 'trigger_threshold']:
                if hasattr(rule, attr):
                    rule_details[attr] = getattr(rule, attr)
            
            return rule_details
            
        except Exception as e:
            logger.error(f"Error getting rule details for {rule_id}: {str(e)}")
            raise
    
    def check_rule_updates(self, rule_id: str) -> Dict[str, Any]:
        """Check if updates are available for a specific analytic rule.
        
        Args:
            rule_id: The ID of the analytic rule.
            
        Returns:
            Dictionary containing update information.
        """
        # Note: This is a placeholder. The actual implementation would need to
        # compare against the Sentinel content hub or solution templates.
        logger.info(f"Checking updates for rule: {rule_id}")
        
        return {
            'rule_id': rule_id,
            'update_available': False,
            'current_version': 'Unknown',
            'latest_version': 'Unknown',
            'changes': [],
            'message': 'Update check functionality to be implemented with Content Hub API'
        }
    
    def get_rules_by_solution(self, solution_name: str) -> List[Dict[str, Any]]:
        """Get all analytic rules associated with a specific solution.
        
        Args:
            solution_name: Name of the Sentinel solution.
            
        Returns:
            List of rules from the specified solution.
        """
        # This would filter rules based on solution metadata
        all_rules = self.list_analytic_rules()
        
        # Placeholder filtering logic
        # In practice, you'd check rule metadata or tags
        solution_rules = [
            rule for rule in all_rules 
            if solution_name.lower() in str(rule.get('name', '')).lower()
        ]
        
        logger.info(f"Found {len(solution_rules)} rules for solution: {solution_name}")
        return solution_rules
