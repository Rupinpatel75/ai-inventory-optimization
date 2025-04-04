"""
Base Agent module for the AI Inventory Optimization System.

This module provides the base functionality for all specialized agents
including logging, database access, and LLM integration.
"""

import logging
import json
from datetime import datetime
from models import Product, Store, AgentLog, db
try:
    from utils.llm_integration import analyze_with_llm_provider
except ImportError:
    analyze_with_llm_provider = None

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system.
    
    This class provides common functionality like logging, database access,
    and LLM integration that all specialized agents will inherit.
    """
    
    def __init__(self, agent_type):
        """
        Initialize the base agent with a specified type.
        
        Args:
            agent_type (str): Type of the agent (e.g., 'demand', 'inventory', 'pricing')
        """
        self.agent_type = agent_type
        self.cache = {}
    
    def log_action(self, action, product_id=None, store_id=None, details=None):
        """
        Log an agent action to the database.
        
        Args:
            action (str): Description of the action performed
            product_id (int, optional): ID of the product involved
            store_id (int, optional): ID of the store involved
            details (dict, optional): Additional details about the action
        
        Returns:
            bool: True if logging succeeded, False otherwise
        """
        try:
            if details is None:
                details = {}
            
            # Ensure details is serializable
            serialized_details = json.dumps(details)
            
            # Create log entry
            log_entry = AgentLog(
                agent_type=self.agent_type,
                action=action,
                product_id=product_id,
                store_id=store_id,
                details=serialized_details,
                timestamp=datetime.now()
            )
            
            # Add and commit to database
            db.session.add(log_entry)
            db.session.commit()
            
            logger.info(f"Agent {self.agent_type} logged action: {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging agent action: {str(e)}")
            # Rollback in case of error
            db.session.rollback()
            return False
    
    def get_product(self, product_id):
        """
        Get a product by ID.
        
        Args:
            product_id: ID of the product
            
        Returns:
            Product object or None if not found
        """
        try:
            # Try to get from cache first
            cache_key = f"product_{product_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Query the database
            product = db.session.query(Product).filter_by(id=product_id).first()
            
            # Cache for future use
            if product:
                self.cache[cache_key] = product
            
            return product
            
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            return None
    
    def get_store(self, store_id):
        """
        Get a store by ID.
        
        Args:
            store_id: ID of the store
            
        Returns:
            Store object or None if not found
        """
        try:
            # Try to get from cache first
            cache_key = f"store_{store_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Query the database
            store = db.session.query(Store).filter_by(id=store_id).first()
            
            # Cache for future use
            if store:
                self.cache[cache_key] = store
            
            return store
            
        except Exception as e:
            logger.error(f"Error retrieving store {store_id}: {str(e)}")
            return None
    
    def get_all_products(self, category=None):
        """
        Get all products, optionally filtered by category.
        
        Args:
            category (str, optional): Product category to filter by
            
        Returns:
            List of Product objects
        """
        try:
            query = db.session.query(Product)
            
            if category:
                query = query.filter_by(category=category)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving products: {str(e)}")
            return []
    
    def get_all_stores(self, region=None):
        """
        Get all stores, optionally filtered by region.
        
        Args:
            region (str, optional): Store region to filter by
            
        Returns:
            List of Store objects
        """
        try:
            query = db.session.query(Store)
            
            if region:
                query = query.filter_by(region=region)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving stores: {str(e)}")
            return []
    
    def analyze_with_llm(self, prompt):
        """
        Analyze a prompt using an LLM provider.
        
        Args:
            prompt (str): The prompt to analyze
            
        Returns:
            str: The LLM response or None if not available/error
        """
        try:
            # Skip if no LLM integration is available
            if analyze_with_llm_provider is None:
                logger.warning("LLM integration not available")
                return None
            
            # Call the LLM provider
            response = analyze_with_llm_provider(
                prompt=prompt,
                agent_type=self.agent_type
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing with LLM: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear the agent's cache."""
        self.cache = {}
        logger.info(f"Agent {self.agent_type} cache cleared")
    
    def get_recent_logs(self, limit=20):
        """
        Get recent logs for this agent type.
        
        Args:
            limit (int): Maximum number of logs to return
            
        Returns:
            List of AgentLog objects
        """
        try:
            logs = db.session.query(AgentLog).filter_by(
                agent_type=self.agent_type
            ).order_by(
                AgentLog.timestamp.desc()
            ).limit(limit).all()
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving agent logs: {str(e)}")
            return []