import logging
import json
import random
from datetime import datetime
from app import db
from models import AgentAction, Product, Store, InventoryRecord

logger = logging.getLogger(__name__)

class PricingAgent:
    """
    Agent responsible for determining optimal pricing strategies
    based on demand predictions and inventory levels.
    """
    
    def __init__(self):
        self.name = "Pricing Agent"
        logger.info("Pricing Agent initialized")
        
        # Configuration parameters
        self.min_profit_margin = 0.15  # Minimum profit margin to maintain
        self.max_discount = 0.30       # Maximum discount percentage allowed
        self.price_elasticity = -1.2   # Price elasticity of demand coefficient
    
    def optimize_price(self, product_id, store_id, demand_predictions):
        """
        Determine optimal pricing strategy based on demand predictions and inventory.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            demand_predictions: List of dictionaries with date and predicted demand
            
        Returns:
            Dictionary with pricing recommendations
        """
        logger.debug(f"Optimizing price for product {product_id} at store {store_id}")
        
        try:
            # Get product details
            product = Product.query.get(product_id)
            if not product:
                logger.warning(f"Product {product_id} not found")
                return {"error": "Product not found"}
            
            base_price = product.base_price
            
            # Get current inventory level
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product_id, 
                store_id=store_id
            ).first()
            
            if not inventory_record:
                logger.warning(f"No inventory record found for product {product_id} at store {store_id}")
                return {"error": "No inventory record found"}
            
            current_stock = inventory_record.quantity
            
            # Calculate total predicted demand
            total_predicted_demand = sum(p['value'] for p in demand_predictions)
            daily_avg_demand = total_predicted_demand / len(demand_predictions) if demand_predictions else 0
            
            # Determine inventory status (overstocked, understocked, or balanced)
            days_of_supply = current_stock / daily_avg_demand if daily_avg_demand > 0 else 30
            
            inventory_status = "balanced"
            if days_of_supply > 45:  # More than 45 days of supply indicates overstocking
                inventory_status = "overstocked"
            elif days_of_supply < 15:  # Less than 15 days of supply indicates understocking
                inventory_status = "understocked"
            
            # Calculate recommended price adjustment based on inventory status
            price_adjustment = 0
            
            if inventory_status == "overstocked":
                # Calculate discount based on how overstocked the item is
                overstock_factor = min((days_of_supply - 30) / 30, 1.0)
                price_adjustment = -self.max_discount * overstock_factor
            elif inventory_status == "understocked":
                # Calculate premium based on how understocked the item is
                understock_factor = min((15 - days_of_supply) / 15, 1.0)
                price_adjustment = 0.10 * understock_factor  # Add up to 10% premium
            
            # Ensure we maintain minimum profit margin
            min_price = base_price * (1 + self.min_profit_margin)
            max_price = base_price * 1.3  # Cap at 30% increase
            
            # Calculate recommended price
            recommended_price = base_price * (1 + price_adjustment)
            recommended_price = max(min_price, min(recommended_price, max_price))
            
            # Calculate expected demand impact
            price_change_pct = price_adjustment
            demand_impact_pct = price_change_pct * self.price_elasticity
            new_expected_demand = daily_avg_demand * (1 + demand_impact_pct)
            
            # Generate recommendation
            recommendation = {
                "base_price": round(base_price, 2),
                "current_stock": current_stock,
                "inventory_status": inventory_status,
                "days_of_supply": round(days_of_supply, 1),
                "price_adjustment_pct": round(price_adjustment * 100, 1),
                "recommended_price": round(recommended_price, 2),
                "expected_demand_change_pct": round(demand_impact_pct * 100, 1),
                "original_daily_demand": round(daily_avg_demand, 2),
                "new_expected_daily_demand": round(new_expected_demand, 2)
            }
            
            # Log this action
            store = Store.query.get(store_id)
            
            action = AgentAction(
                agent_type="pricing",
                action="optimize_price",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps({
                    "base_price": round(base_price, 2),
                    "recommended_price": round(recommended_price, 2),
                    "inventory_status": inventory_status,
                    "product_name": product.name,
                    "store_name": store.name if store else "Unknown"
                })
            )
            db.session.add(action)
            db.session.commit()
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error in price optimization: {str(e)}")
            return {"error": str(e)}
    
    def apply_price_change(self, product_id, store_id, new_price):
        """
        Apply a price change to a product at a specific store.
        This would be used to implement pricing decisions.
        
        In a real system, this might update a pricing database or POS system.
        In this demo, it just logs the action.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            new_price: New price to apply
            
        Returns:
            Boolean indicating success
        """
        try:
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            if not product or not store:
                logger.warning(f"Product {product_id} or Store {store_id} not found")
                return False
            
            # Log the price change action
            action = AgentAction(
                agent_type="pricing",
                action="apply_price_change",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps({
                    "old_price": product.base_price,
                    "new_price": new_price,
                    "product_name": product.name,
                    "store_name": store.name
                })
            )
            db.session.add(action)
            
            # In a real system, we'd update the price in a pricing database
            # For this demo, we'll just log the action
            
            db.session.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error applying price change: {str(e)}")
            db.session.rollback()
            return False
