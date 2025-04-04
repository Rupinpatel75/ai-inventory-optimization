"""
Agent modules for the AI Inventory Optimization System.

This package contains the various agent implementations for demand forecasting,
inventory management, and pricing optimization.
"""

import logging

logger = logging.getLogger(__name__)

# Import agent classes for easier access
try:
    from .base_agent import BaseAgent
except ImportError:
    logger.warning("BaseAgent import failed")
    BaseAgent = None

# Initialize agent instances
demand_agent = None
inventory_agent = None
pricing_agent = None

# Initialize demand agent
try:
    from .demand_agent import DemandAgent
    demand_agent = DemandAgent()
    logger.info("Demand agent initialized")
except ImportError:
    logger.warning("DemandAgent import failed")

# Initialize inventory agent
try:
    from .inventory_agent import InventoryAgent
    inventory_agent = InventoryAgent()
    logger.info("Inventory agent initialized")
except ImportError:
    logger.warning("InventoryAgent import failed")

# Initialize pricing agent
try:
    from .pricing_agent import PricingAgent
    pricing_agent = PricingAgent()
    logger.info("Pricing agent initialized")
except ImportError:
    logger.warning("PricingAgent import failed")

def get_agent(agent_type):
    """
    Get an agent instance by type.
    
    Args:
        agent_type (str): Type of agent to get ('demand', 'inventory', 'pricing')
        
    Returns:
        Agent instance or None if not available
    """
    if agent_type == 'demand':
        return demand_agent
    elif agent_type == 'inventory':
        return inventory_agent
    elif agent_type == 'pricing':
        return pricing_agent
    else:
        logger.warning(f"Unknown agent type: {agent_type}")
        return None

def initialize_agents():
    """
    Initialize all agent instances if they are not already initialized.
    
    Returns:
        dict: Dictionary of initialized agents
    """
    global demand_agent, inventory_agent, pricing_agent
    
    agents = {}
    
    # Initialize demand agent if needed
    if demand_agent is None:
        try:
            from .demand_agent import DemandAgent
            demand_agent = DemandAgent()
            logger.info("Demand agent initialized")
        except ImportError:
            logger.warning("DemandAgent import failed")
    
    if demand_agent:
        agents['demand'] = demand_agent
    
    # Initialize inventory agent if needed
    if inventory_agent is None:
        try:
            from .inventory_agent import InventoryAgent
            inventory_agent = InventoryAgent()
            logger.info("Inventory agent initialized")
        except ImportError:
            logger.warning("InventoryAgent import failed")
    
    if inventory_agent:
        agents['inventory'] = inventory_agent
    
    # Initialize pricing agent if needed
    if pricing_agent is None:
        try:
            from .pricing_agent import PricingAgent
            pricing_agent = PricingAgent()
            logger.info("Pricing agent initialized")
        except ImportError:
            logger.warning("PricingAgent import failed")
    
    if pricing_agent:
        agents['pricing'] = pricing_agent
    
    return agents