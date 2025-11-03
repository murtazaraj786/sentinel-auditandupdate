"""Module for deploying updates to Microsoft Sentinel."""

import logging
from typing import Dict, Any, Optional
from azure.mgmt.securityinsight import SecurityInsights
from azure.mgmt.securityinsight.models import ScheduledAlertRule
from azure.core.credentials import TokenCredential
from config import SentinelConfig

logger = logging.getLogger(__name__)


class SentinelDeployment:
    """Handler for deploying updates to Microsoft Sentinel."""
    
    def __init__(self, credential: TokenCredential, config: SentinelConfig):
        """Initialize the deployment handler.
        
        Args:
            credential: Azure credential for authentication.
            config: Sentinel configuration.
        """
        self.client = SecurityInsights(credential, config.subscription_id)
        self.config = config
    
    def deploy_analytic_rule(self, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy or update an analytic rule.
        
        Args:
            rule_config: Configuration dictionary for the analytic rule.
            
        Returns:
            Deployment result information.
        """
        try:
            rule_id = rule_config.get('rule_id') or rule_config.get('name')
            
            logger.info(f"Deploying analytic rule: {rule_id}")
            
            # Note: This is a simplified example. Full implementation would need
            # to handle different rule types (Scheduled, MLBehaviorAnalytics, etc.)
            # and all their specific properties.
            
            result = self.client.alert_rules.create_or_update(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                rule_id=rule_id,
                alert_rule=rule_config  # This would need proper model object
            )
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': f"Successfully deployed rule: {rule_id}",
                'details': result
            }
            
        except Exception as e:
            logger.error(f"Error deploying analytic rule: {str(e)}")
            return {
                'success': False,
                'rule_id': rule_id,
                'message': f"Failed to deploy rule: {str(e)}"
            }
    
    def update_data_connector(self, connector_id: str, connector_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update a data connector configuration.
        
        Args:
            connector_id: ID of the data connector.
            connector_config: Updated configuration for the connector.
            
        Returns:
            Update result information.
        """
        try:
            logger.info(f"Updating data connector: {connector_id}")
            
            result = self.client.data_connectors.create_or_update(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                data_connector_id=connector_id,
                data_connector=connector_config  # This would need proper model object
            )
            
            return {
                'success': True,
                'connector_id': connector_id,
                'message': f"Successfully updated connector: {connector_id}",
                'details': result
            }
            
        except Exception as e:
            logger.error(f"Error updating data connector: {str(e)}")
            return {
                'success': False,
                'connector_id': connector_id,
                'message': f"Failed to update connector: {str(e)}"
            }
    
    def enable_analytic_rule(self, rule_id: str) -> Dict[str, Any]:
        """Enable an analytic rule.
        
        Args:
            rule_id: ID of the analytic rule to enable.
            
        Returns:
            Operation result.
        """
        try:
            # Get current rule
            rule = self.client.alert_rules.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                rule_id=rule_id
            )
            
            # Update enabled status
            if hasattr(rule, 'enabled'):
                rule.enabled = True
                
                result = self.client.alert_rules.create_or_update(
                    resource_group_name=self.config.resource_group,
                    workspace_name=self.config.workspace_name,
                    rule_id=rule_id,
                    alert_rule=rule
                )
                
                return {
                    'success': True,
                    'rule_id': rule_id,
                    'message': f"Successfully enabled rule: {rule_id}"
                }
            else:
                return {
                    'success': False,
                    'rule_id': rule_id,
                    'message': "Rule does not support enable/disable"
                }
                
        except Exception as e:
            logger.error(f"Error enabling rule: {str(e)}")
            return {
                'success': False,
                'rule_id': rule_id,
                'message': f"Failed to enable rule: {str(e)}"
            }
    
    def disable_analytic_rule(self, rule_id: str) -> Dict[str, Any]:
        """Disable an analytic rule.
        
        Args:
            rule_id: ID of the analytic rule to disable.
            
        Returns:
            Operation result.
        """
        try:
            # Get current rule
            rule = self.client.alert_rules.get(
                resource_group_name=self.config.resource_group,
                workspace_name=self.config.workspace_name,
                rule_id=rule_id
            )
            
            # Update enabled status
            if hasattr(rule, 'enabled'):
                rule.enabled = False
                
                result = self.client.alert_rules.create_or_update(
                    resource_group_name=self.config.resource_group,
                    workspace_name=self.config.workspace_name,
                    rule_id=rule_id,
                    alert_rule=rule
                )
                
                return {
                    'success': True,
                    'rule_id': rule_id,
                    'message': f"Successfully disabled rule: {rule_id}"
                }
            else:
                return {
                    'success': False,
                    'rule_id': rule_id,
                    'message': "Rule does not support enable/disable"
                }
                
        except Exception as e:
            logger.error(f"Error disabling rule: {str(e)}")
            return {
                'success': False,
                'rule_id': rule_id,
                'message': f"Failed to disable rule: {str(e)}"
            }
