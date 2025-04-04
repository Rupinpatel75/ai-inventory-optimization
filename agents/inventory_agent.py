"""
Inventory Agent module for the AI Inventory Optimization System.

This module provides the inventory management agent that optimizes
inventory levels based on demand forecasts and business constraints.
"""

import logging
from agents.base_agent import BaseAgent
from utils.inventory_optimizer import calculate_optimal_inventory, get_reorder_recommendation, calculate_stockout_risk
from utils.forecasting import predict_demand
from models import InventoryRecord, db
from datetime import datetime

logger = logging.getLogger(__name__)

class InventoryAgent(BaseAgent):
    """
    Inventory management agent that optimizes inventory levels
    based on demand forecasts and business constraints.
    """
    
    def __init__(self):
        """Initialize the inventory agent."""
        super().__init__(agent_type="inventory")
    
    def get_current_inventory(self, product_id, store_id):
        """
        Get current inventory level for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with inventory details
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get inventory record
            inventory = db.session.query(InventoryRecord).filter_by(
                product_id=product_id, store_id=store_id
            ).first()
            
            if not inventory:
                logger.error(f"No inventory record found for product {product_id} at store {store_id}")
                return {
                    "error": f"No inventory record found for product {product_id} at store {store_id}"
                }
            
            # Format last updated time
            last_updated = inventory.last_updated.strftime("%Y-%m-%d %H:%M:%S") if inventory.last_updated else None
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "quantity": inventory.quantity,
                "last_updated": last_updated
            }
        
        except Exception as e:
            logger.error(f"Error getting current inventory: {str(e)}")
            return {
                "error": f"Failed to get current inventory: {str(e)}"
            }
    
    def update_inventory(self, product_id, store_id, quantity, action="manual update"):
        """
        Update inventory level for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            quantity: New inventory quantity
            action: Description of the action that led to update
            
        Returns:
            Dictionary with update result
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get inventory record
            inventory = db.session.query(InventoryRecord).filter_by(
                product_id=product_id, store_id=store_id
            ).first()
            
            if not inventory:
                logger.error(f"No inventory record found for product {product_id} at store {store_id}")
                return {
                    "error": f"No inventory record found for product {product_id} at store {store_id}"
                }
            
            # Save old quantity for logging
            old_quantity = inventory.quantity
            
            # Update inventory
            inventory.quantity = quantity
            inventory.last_updated = datetime.now()
            
            db.session.commit()
            
            # Log the agent action
            details = {
                "old_quantity": old_quantity,
                "new_quantity": quantity,
                "change": quantity - old_quantity,
                "action": action
            }
            
            self.log_action(
                action=f"Inventory update ({action})",
                product_id=product_id,
                store_id=store_id,
                details=details
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "old_quantity": old_quantity,
                "new_quantity": quantity,
                "change": quantity - old_quantity,
                "success": True
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating inventory: {str(e)}")
            return {
                "error": f"Failed to update inventory: {str(e)}",
                "success": False
            }
    
    def get_optimal_inventory_levels(self, product_id, store_id):
        """
        Calculate optimal inventory levels for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with optimal inventory levels
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Calculate optimal inventory
            optimal = calculate_optimal_inventory(product_id, store_id)
            
            # Log the agent action
            self.log_action(
                action="Optimal inventory calculation",
                product_id=product_id,
                store_id=store_id,
                details=optimal
            )
            
            # Add product and store names
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **optimal
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating optimal inventory: {str(e)}")
            return {
                "error": f"Failed to calculate optimal inventory: {str(e)}"
            }
    
    def get_reorder_recommendation(self, product_id, store_id):
        """
        Get recommendation on whether to reorder and how much.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with reorder recommendation
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get current inventory
            inventory_response = self.get_current_inventory(product_id, store_id)
            
            if "error" in inventory_response:
                return inventory_response
            
            current_stock = inventory_response.get("quantity", 0)
            
            # Get reorder recommendation
            recommendation = get_reorder_recommendation(current_stock, product_id, store_id)
            
            # Log the agent action
            self.log_action(
                action="Reorder recommendation",
                product_id=product_id,
                store_id=store_id,
                details=recommendation
            )
            
            # Add product and store names
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **recommendation
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting reorder recommendation: {str(e)}")
            return {
                "error": f"Failed to get reorder recommendation: {str(e)}"
            }
    
    def get_stockout_risk(self, product_id, store_id):
        """
        Calculate the risk of stockout for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with stockout risk assessment
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get current inventory
            inventory_response = self.get_current_inventory(product_id, store_id)
            
            if "error" in inventory_response:
                return inventory_response
            
            current_stock = inventory_response.get("quantity", 0)
            
            # Calculate stockout risk
            risk = calculate_stockout_risk(current_stock, product_id, store_id)
            
            # Log the agent action
            self.log_action(
                action="Stockout risk assessment",
                product_id=product_id,
                store_id=store_id,
                details=risk
            )
            
            # Add product and store names
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **risk
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating stockout risk: {str(e)}")
            return {
                "error": f"Failed to calculate stockout risk: {str(e)}"
            }
    
    def explain_recommendation(self, product_id, store_id):
        """
        Generate a natural language explanation of inventory recommendations.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with recommendation and explanation
        """
        try:
            # Get product and store
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get inventory data
            inventory = self.get_current_inventory(product_id, store_id)
            if "error" in inventory:
                return inventory
            
            current_stock = inventory.get("quantity", 0)
            
            # Get reorder recommendation
            recommendation = self.get_reorder_recommendation(product_id, store_id)
            if "error" in recommendation:
                return recommendation
            
            # Get stockout risk
            risk = self.get_stockout_risk(product_id, store_id)
            if "error" in risk:
                return risk
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please provide a brief explanation of the inventory recommendation for {product.name} at {store.name}.
            
            Product: {product.name}
            Category: {product.category}
            Current stock: {current_stock} units
            
            Recommendation:
            - Should reorder: {"Yes" if recommendation.get("should_reorder") else "No"}
            - Suggested order quantity: {recommendation.get("suggested_order")} units
            - Reorder point: {recommendation.get("reorder_point")} units
            - Days of stock remaining: {recommendation.get("days_remaining")} days
            - Predicted demand (30 days): {recommendation.get("predicted_demand_30d")} units
            - Urgency: {recommendation.get("urgency")}
            
            Stockout risk:
            - Days until stockout: {risk.get("days_until_stockout")} days
            - Stockout probability: {risk.get("stockout_probability") * 100}%
            - Risk level: {risk.get("risk_level")}
            
            Please provide a 3-4 sentence explanation of this recommendation in plain language, 
            focusing on actionable insights for the store manager.
            """
            
            system_prompt = """
            You are a helpful AI assistant explaining inventory recommendations to a store manager.
            Your explanation should be clear, concise, and focused on actionable insights.
            If the product needs to be reordered, emphasize the urgency and recommended quantity.
            If the product doesn't need to be reordered, explain why and when it might need attention.
            """
            
            explanation = self.analyze_with_llm(prompt, system_prompt)
            
            if not explanation or "error" in explanation.lower():
                # Generate a basic explanation if LLM fails
                if recommendation.get("should_reorder"):
                    explanation = f"Recommend ordering {recommendation.get('suggested_order')} units of {product.name} for {store.name}. "
                    if risk.get("days_until_stockout"):
                        explanation += f"Current stock of {current_stock} units will be depleted in approximately {risk.get('days_until_stockout')} days. "
                    explanation += f"Urgency level: {recommendation.get('urgency')}."
                else:
                    explanation = f"No need to reorder {product.name} for {store.name} at this time. "
                    explanation += f"Current stock of {current_stock} units is sufficient for approximately {recommendation.get('days_remaining')} days. "
                    explanation += f"Stockout risk is {risk.get('risk_level').lower()}."
            
            # Log the agent action
            self.log_action(
                action="Inventory recommendation explanation",
                product_id=product_id,
                store_id=store_id,
                details={"explanation": explanation}
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "current_stock": current_stock,
                "recommendation": recommendation,
                "stockout_risk": risk,
                "explanation": explanation
            }
        
        except Exception as e:
            logger.error(f"Error explaining recommendation: {str(e)}")
            return {
                "error": f"Failed to explain recommendation: {str(e)}"
            }