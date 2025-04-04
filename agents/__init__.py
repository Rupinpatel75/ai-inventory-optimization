"""
Agent modules for the AI Inventory Optimization System.
"""

import logging

from agents.demand_agent import DemandAgent
from agents.inventory_agent import InventoryAgent
from agents.pricing_agent import PricingAgent

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent factory function
def get_agent(agent_type):
    """
    Factory function to get the appropriate agent instance.
    
    Args:
        agent_type: Type of agent to create (demand, inventory, pricing)
        
    Returns:
        Agent instance
    """
    if agent_type == "demand":
        return DemandAgent()
    elif agent_type == "inventory":
        return InventoryAgent()
    elif agent_type == "pricing":
        return PricingAgent()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

# Create global instances for easy import
demand_agent = None
inventory_agent = None
pricing_agent = None

try:
    demand_agent = DemandAgent()
    logger.info("Demand Agent initialized")
except Exception as e:
    logger.error(f"Error initializing Demand Agent: {str(e)}")

try:
    inventory_agent = InventoryAgent()
    logger.info("Inventory Agent initialized")
except Exception as e:
    logger.error(f"Error initializing Inventory Agent: {str(e)}")

try:
    pricing_agent = PricingAgent()
    logger.info("Pricing Agent initialized")
except Exception as e:
    logger.error(f"Error initializing Pricing Agent: {str(e)}")