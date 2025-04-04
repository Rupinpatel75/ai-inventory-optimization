import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from models import InventoryRecord, Product, Store
from app import db

logger = logging.getLogger(__name__)

class InventoryAgent(BaseAgent):
    """
    Agent responsible for making inventory optimization recommendations
    based on demand predictions and current inventory levels.
    """
    
    def __init__(self):
        super().__init__("Inventory Agent", "inventory")
        logger.info("Inventory Agent initialized")
    
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
        try:
            # Log action start
            self.log_action(
                action="optimize_inventory_start",
                product_id=product_id,
                store_id=store_id,
                details={
                    "prediction_count": len(demand_predictions) if demand_predictions else 0
                }
            )
            
            # Get current inventory level
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product_id,
                store_id=store_id
            ).first()
            
            if not inventory_record:
                logger.warning(f"No inventory record found for product {product_id} at store {store_id}")
                current_quantity = 0
            else:
                current_quantity = inventory_record.quantity
            
            # Get product and store details for context
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            if not product or not store:
                logger.warning(f"Product or store not found. Product ID: {product_id}, Store ID: {store_id}")
                return {
                    "error": "Product or store not found",
                    "recommendation": "Unable to make recommendation due to missing data"
                }
            
            # Calculate total predicted demand
            total_predicted_demand = sum(p.get('demand', 0) for p in demand_predictions)
            avg_daily_demand = total_predicted_demand / len(demand_predictions) if demand_predictions else 0
            
            # Basic recommendations based on inventory levels and demand
            if current_quantity <= 0:
                status = "OUT_OF_STOCK"
                urgency = "HIGH"
            elif current_quantity < avg_daily_demand * 3:
                status = "LOW_STOCK"
                urgency = "MEDIUM"
            elif current_quantity < avg_daily_demand * 7:
                status = "ADEQUATE"
                urgency = "LOW"
            else:
                status = "OVERSTOCKED"
                urgency = "NONE"
            
            # Calculate recommended order quantity
            # Target 14 days of inventory
            target_inventory = avg_daily_demand * 14
            recommended_order = max(0, target_inventory - current_quantity)
            
            # Use LLM to enhance recommendations if available
            enhanced_recommendations = {}
            if self.llm and self.llm.check_ollama_available():
                logger.info("Using LLM to enhance inventory recommendations")
                
                # Create context for LLM
                context = {
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "base_price": product.base_price
                    },
                    "store": {
                        "id": store.id,
                        "name": store.name,
                        "location": store.location
                    },
                    "inventory": {
                        "current_quantity": current_quantity,
                        "last_updated": inventory_record.last_updated.isoformat() if inventory_record else None
                    },
                    "demand": {
                        "average_daily": avg_daily_demand,
                        "total_predicted": total_predicted_demand,
                        "days_forecasted": len(demand_predictions)
                    },
                    "preliminary_assessment": {
                        "status": status,
                        "urgency": urgency,
                        "recommended_order": recommended_order
                    }
                }
                
                # Prompt for LLM
                prompt = f"""
                Analyze the inventory situation for product "{product.name}" at store "{store.name}".
                
                Based on the provided context:
                1. Evaluate if our preliminary inventory status assessment is accurate
                2. Suggest an optimal order quantity based on demand patterns
                3. Recommend inventory management actions
                4. Provide risk assessment
                
                Return your analysis as a JSON object with these keys:
                - "status": Current inventory status assessment
                - "urgency": Urgency level for restocking
                - "recommended_order": Optimal order quantity
                - "reasoning": Brief explanation of recommendations
                - "actions": Array of specific actions to take
                - "risks": Any potential risks to consider
                
                ONLY return the JSON object, nothing else.
                """
                
                llm_response = self.analyze_with_llm(
                    prompt=prompt,
                    context=context,
                    system_prompt="You are an inventory optimization expert. Provide data-driven inventory recommendations."
                )
                
                # Parse JSON from LLM response
                try:
                    # Extract JSON object if embedded in other text
                    import re
                    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if json_match:
                        llm_json = json_match.group(0)
                        enhanced_recommendations = json.loads(llm_json)
                    else:
                        # Try to parse the whole response as JSON
                        enhanced_recommendations = json.loads(llm_response)
                        
                    # Update recommended order from LLM if available
                    if 'recommended_order' in enhanced_recommendations:
                        try:
                            llm_order = float(enhanced_recommendations['recommended_order'])
                            # Only accept if reasonable
                            if 0 <= llm_order <= 1000:
                                recommended_order = llm_order
                        except (ValueError, TypeError):
                            pass
                except Exception as e:
                    logger.error(f"Failed to parse LLM recommendation JSON: {str(e)}")
            
            # Build final recommendation
            recommendation = {
                "product_id": product_id,
                "store_id": store_id,
                "current_quantity": current_quantity,
                "total_predicted_demand": total_predicted_demand,
                "average_daily_demand": avg_daily_demand,
                "status": enhanced_recommendations.get("status", status),
                "urgency": enhanced_recommendations.get("urgency", urgency),
                "recommended_order": round(recommended_order),
                "reasoning": enhanced_recommendations.get("reasoning", "Based on current inventory and predicted demand"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add actions if provided by LLM
            if "actions" in enhanced_recommendations:
                recommendation["actions"] = enhanced_recommendations["actions"]
                
            # Add risks if provided by LLM
            if "risks" in enhanced_recommendations:
                recommendation["risks"] = enhanced_recommendations["risks"]
            
            # Log action completion
            self.log_action(
                action="optimize_inventory_complete",
                product_id=product_id,
                store_id=store_id,
                details={
                    "status": recommendation["status"],
                    "urgency": recommendation["urgency"],
                    "recommended_order": recommendation["recommended_order"]
                }
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error in inventory optimization: {str(e)}")
            self.log_action(
                action="optimize_inventory_error",
                product_id=product_id,
                store_id=store_id,
                details={
                    "error": str(e)
                }
            )
            return {
                "error": str(e),
                "recommendation": "Error occurred during optimization"
            }
    
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
            # Log action start
            self.log_action(
                action="update_inventory_start",
                product_id=product_id,
                store_id=store_id,
                details={
                    "new_quantity": new_quantity
                }
            )
            
            # Find inventory record
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product_id,
                store_id=store_id
            ).first()
            
            old_quantity = 0
            if inventory_record:
                old_quantity = inventory_record.quantity
                inventory_record.quantity = new_quantity
                inventory_record.last_updated = datetime.now()
            else:
                # Create new record if it doesn't exist
                inventory_record = InventoryRecord(
                    product_id=product_id,
                    store_id=store_id,
                    quantity=new_quantity,
                    last_updated=datetime.now()
                )
                db.session.add(inventory_record)
            
            db.session.commit()
            
            # Log action completion
            self.log_action(
                action="update_inventory_complete",
                product_id=product_id,
                store_id=store_id,
                details={
                    "old_quantity": old_quantity,
                    "new_quantity": new_quantity,
                    "change": new_quantity - old_quantity
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            db.session.rollback()
            
            self.log_action(
                action="update_inventory_error",
                product_id=product_id,
                store_id=store_id,
                details={
                    "error": str(e),
                    "intended_quantity": new_quantity
                }
            )
            
            return False