"""
Base agent module for the AI Inventory Optimization System.

This module provides the base agent class that all specialized agents
inherit from, with common functionality for LLM integration, logging,
and reasoning.
"""

import json
import logging
from datetime import datetime
from models import Product, Store, AgentAction, db

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base agent class with common functionality for all agent types.
    
    This provides:
    - LLM integration for reasoning
    - Logging actions to database
    - Common helper methods
    """
    
    def __init__(self, agent_type="base"):
        """
        Initialize the base agent.
        
        Args:
            agent_type: Type of the agent (e.g., 'demand', 'inventory', 'pricing')
        """
        self.agent_type = agent_type
        logger.info(f"Initializing {agent_type} agent")
    
    def get_product(self, product_id):
        """
        Get product details by ID.
        
        Args:
            product_id: ID of the product
            
        Returns:
            Product object or None if not found
        """
        try:
            return db.session.query(Product).filter_by(id=product_id).first()
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            return None
    
    def get_store(self, store_id):
        """
        Get store details by ID.
        
        Args:
            store_id: ID of the store
            
        Returns:
            Store object or None if not found
        """
        try:
            return db.session.query(Store).filter_by(id=store_id).first()
        except Exception as e:
            logger.error(f"Error getting store {store_id}: {str(e)}")
            return None
    
    def log_action(self, action, product_id=None, store_id=None, details=None):
        """
        Log an agent action to the database.
        
        Args:
            action: Description of the action
            product_id: Optional product ID
            store_id: Optional store ID
            details: Optional JSON serializable details
            
        Returns:
            AgentAction object or None if error
        """
        try:
            # Convert details to JSON string if provided
            details_json = None
            if details:
                if isinstance(details, str):
                    details_json = details
                else:
                    try:
                        details_json = json.dumps(details)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Could not serialize action details: {str(e)}")
                        details_json = str(details)
            
            # Create agent action record
            agent_action = AgentAction(
                agent_type=self.agent_type,
                action=action,
                product_id=product_id,
                store_id=store_id,
                details=details_json,
                timestamp=datetime.now()
            )
            
            # Add to database
            db.session.add(agent_action)
            db.session.commit()
            
            return agent_action
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error logging agent action: {str(e)}")
            return None
    
    def analyze_with_llm(self, prompt, system_prompt=None):
        """
        Analyze data using LLM.
        
        Args:
            prompt: Prompt for the LLM
            system_prompt: Optional system prompt
            
        Returns:
            LLM response
        """
        try:
            # Import here to avoid circular imports
            from utils.llm_integration import llm_manager
            
            # Check if LLM is available
            if not llm_manager.ollama_available:
                return None
            
            # Get response from LLM
            response = llm_manager.chat_completion(prompt, system_prompt)
            
            return response
        
        except Exception as e:
            logger.error(f"Error analyzing with LLM: {str(e)}")
            return None