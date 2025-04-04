import logging
import json
import random
from datetime import datetime
from app import db
from models import AgentAction, Product, Store, InventoryRecord

logger = logging.getLogger(__name__)

class InventoryAgent:
    """
    Agent responsible for making inventory optimization recommendations
    based on demand predictions and current inventory levels.
    """
    
    def __init__(self):
        self.name = "Inventory Agent"
        logger.info("Inventory Agent initialized")
        
        # Configuration parameters
        self.safety_stock_days = 7  # Days of safety stock to maintain
        self.lead_time_days = 3     # Average lead time for restocking
        self.holding_cost_pct = 0.2  # Annual holding cost as percentage of item value
    
    def optimize_inventory(self, product_id, store_id, demand_predictions):
        """
        Make inventory optimization recommendations based on demand predictions.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            demand_predictions: List of dictionaries with date and predicted demand
            
        Returns:
            Dictionary with inventory recommendations
        """
        logger.debug(f"Optimizing inventory for product {product_id} at store {store_id}")
        
        try:
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
            
            # Calculate Economic Order Quantity (EOQ)
            product = Product.query.get(product_id)
            if not product:
                logger.warning(f"Product {product_id} not found")
                return {"error": "Product not found"}
            
            item_cost = product.base_price * 0.6  # Assuming cost is 60% of base price
            annual_demand = daily_avg_demand * 365
            ordering_cost = 50  # Fixed cost per order in $
            
            # EOQ formula = sqrt(2DO/H) where D is annual demand, O is ordering cost, H is holding cost
            daily_holding_cost = item_cost * self.holding_cost_pct / 365
            eoq = (2 * annual_demand * ordering_cost / (daily_holding_cost * 365)) ** 0.5
            eoq = max(round(eoq), 1)  # Ensure minimum of 1
            
            # Calculate reorder point
            safety_stock = daily_avg_demand * self.safety_stock_days
            lead_time_demand = daily_avg_demand * self.lead_time_days
            reorder_point = round(safety_stock + lead_time_demand)
            
            # Determine if restocking is needed
            days_of_supply = current_stock / daily_avg_demand if daily_avg_demand > 0 else 30
            restock_needed = current_stock <= reorder_point
            restock_quantity = eoq if restock_needed else 0
            
            # Calculate excess inventory
            excess_inventory = max(0, current_stock - (daily_avg_demand * 30))
            
            # Generate recommendation
            recommendation = {
                "current_stock": current_stock,
                "daily_avg_demand": round(daily_avg_demand, 2),
                "days_of_supply": round(days_of_supply, 1),
                "reorder_point": reorder_point,
                "economic_order_quantity": eoq,
                "restock_needed": restock_needed,
                "restock_quantity": restock_quantity,
                "excess_inventory": round(excess_inventory, 1),
                "safety_stock": round(safety_stock, 1)
            }
            
            # Log this action
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            action = AgentAction(
                agent_type="inventory",
                action="optimize_inventory",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps({
                    "current_stock": current_stock,
                    "restock_needed": restock_needed,
                    "restock_quantity": restock_quantity,
                    "product_name": product.name if product else "Unknown",
                    "store_name": store.name if store else "Unknown"
                })
            )
            db.session.add(action)
            db.session.commit()
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error in inventory optimization: {str(e)}")
            return {"error": str(e)}
    
    def update_inventory(self, product_id, store_id, new_quantity):
        """
        Update the inventory quantity for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            new_quantity: New inventory quantity
            
        Returns:
            Boolean indicating success
        """
        try:
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product_id, 
                store_id=store_id
            ).first()
            
            if not inventory_record:
                inventory_record = InventoryRecord(
                    product_id=product_id,
                    store_id=store_id,
                    quantity=new_quantity,
                    last_updated=datetime.now()
                )
                db.session.add(inventory_record)
            else:
                old_quantity = inventory_record.quantity
                inventory_record.quantity = new_quantity
                inventory_record.last_updated = datetime.now()
            
            # Log this action
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            action = AgentAction(
                agent_type="inventory",
                action="update_inventory",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps({
                    "old_quantity": old_quantity if 'old_quantity' in locals() else None,
                    "new_quantity": new_quantity,
                    "product_name": product.name if product else "Unknown",
                    "store_name": store.name if store else "Unknown"
                })
            )
            db.session.add(action)
            db.session.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            db.session.rollback()
            return False
