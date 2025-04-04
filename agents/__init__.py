"""
Agent modules for the AI Inventory Optimization System.
"""

import logging
from agents.demand_agent import DemandAgent
from agents.inventory_agent import InventoryAgent
from agents.pricing_agent import PricingAgent

logger = logging.getLogger(__name__)

# Create agent instances
demand_agent = DemandAgent()
inventory_agent = InventoryAgent()
pricing_agent = PricingAgent()

def get_agent(agent_type):
    """
    Factory function to get the appropriate agent instance.
    
    Args:
        agent_type: Type of agent to create (demand, inventory, pricing)
        
    Returns:
        Agent instance
    
    Raises:
        ValueError: If agent_type is not recognized
    """
    if agent_type == 'demand':
        return demand_agent
    elif agent_type == 'inventory':
        return inventory_agent
    elif agent_type == 'pricing':
        return pricing_agent
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")