import logging
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from models import Product, InventoryRecord
from app import db

logger = logging.getLogger(__name__)

class PricingAgent(BaseAgent):
    """
    Agent responsible for determining optimal pricing strategies
    based on demand predictions and inventory levels.
    """
    
    def __init__(self):
        super().__init__("Pricing Agent", "pricing")
        logger.info("Pricing Agent initialized")
    
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
        try:
            # Log action start
            self.log_action(
                action="optimize_price_start",
                product_id=product_id,
                store_id=store_id,
                details={
                    "prediction_count": len(demand_predictions) if demand_predictions else 0
                }
            )
            
            # Get product details
            product = Product.query.get(product_id)
            if not product:
                logger.warning(f"Product not found with ID: {product_id}")
                return {
                    "error": "Product not found",
                    "recommendation": "Unable to make pricing recommendation"
                }
            
            # Get current inventory level
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product_id,
                store_id=store_id
            ).first()
            
            current_inventory = inventory_record.quantity if inventory_record else 0
            
            # Calculate total predicted demand
            total_predicted_demand = sum(p.get('demand', 0) for p in demand_predictions)
            avg_daily_demand = total_predicted_demand / len(demand_predictions) if demand_predictions else 0
            
            # Get base price from product
            base_price = product.base_price
            
            # Basic pricing logic - adjust based on inventory vs. demand
            inventory_demand_ratio = current_inventory / max(1, avg_daily_demand * 7)  # Inventory vs. 7-day demand
            
            # Default pricing strategy
            if inventory_demand_ratio <= 0.5:  # Low inventory compared to demand
                strategy = "PREMIUM"
                price_adjustment = 1.15  # 15% markup
                explanation = "Low inventory relative to demand suggests premium pricing to maximize margin."
            elif inventory_demand_ratio <= 1.0:  # Balanced inventory and demand
                strategy = "STANDARD"
                price_adjustment = 1.0  # Standard price
                explanation = "Balanced inventory and demand indicate maintaining standard pricing."
            elif inventory_demand_ratio <= 2.0:  # Moderate excess inventory
                strategy = "DISCOUNT"
                price_adjustment = 0.9  # 10% discount
                explanation = "Moderate excess inventory suggests a small discount to increase sales velocity."
            else:  # Significant excess inventory
                strategy = "CLEARANCE"
                price_adjustment = 0.75  # 25% discount
                explanation = "Significant excess inventory indicates need for clearance pricing to reduce stock."
            
            # Calculate recommended price
            recommended_price = round(base_price * price_adjustment, 2)
            
            # Use LLM for enhanced pricing strategy if available
            if self.llm and self.llm.check_ollama_available():
                logger.info("Using LLM to enhance pricing recommendations")
                
                # Get additional market data if available
                market_data = self._get_market_data(product)
                
                # Create context for LLM
                context = {
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "base_price": product.base_price
                    },
                    "inventory": {
                        "current_quantity": current_inventory,
                        "inventory_demand_ratio": inventory_demand_ratio
                    },
                    "demand": {
                        "average_daily": avg_daily_demand,
                        "total_predicted": total_predicted_demand,
                        "days_forecasted": len(demand_predictions)
                    },
                    "pricing": {
                        "base_price": base_price,
                        "preliminary_strategy": strategy,
                        "preliminary_price_adjustment": price_adjustment,
                        "preliminary_recommended_price": recommended_price
                    },
                    "market_data": market_data
                }
                
                # Prompt for LLM
                prompt = f"""
                Analyze optimal pricing strategy for product "{product.name}" with base price ${base_price}.
                
                Based on the provided context:
                1. Evaluate if our preliminary pricing strategy is appropriate
                2. Suggest an optimal price point considering inventory levels and demand
                3. Recommend specific pricing actions (increase, maintain, discount)
                4. Consider competitor pricing and market position if data available
                
                Return your analysis as a JSON object with these keys:
                - "strategy": Overall pricing strategy (e.g., PREMIUM, STANDARD, DISCOUNT, CLEARANCE)
                - "recommended_price": Specific price point recommendation (number)
                - "price_adjustment": Multiplier applied to base price (e.g., 0.9 for 10% discount)
                - "rationale": Brief explanation of your recommendation
                - "actions": Array of specific actions to take
                - "expected_impact": Anticipated effect on sales and revenue
                
                ONLY return the JSON object, nothing else.
                """
                
                llm_response = self.analyze_with_llm(
                    prompt=prompt,
                    context=context,
                    system_prompt="You are a pricing optimization expert. Provide data-driven pricing recommendations."
                )
                
                # Parse JSON from LLM response
                try:
                    # Extract JSON object if embedded in other text
                    import re
                    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if json_match:
                        llm_json = json_match.group(0)
                        enhanced_pricing = json.loads(llm_json)
                        
                        # Update from LLM recommendations if valid
                        if 'recommended_price' in enhanced_pricing:
                            try:
                                llm_price = float(enhanced_pricing['recommended_price'])
                                # Only accept if within reasonable range (50-200% of base price)
                                if 0.5 * base_price <= llm_price <= 2.0 * base_price:
                                    recommended_price = llm_price
                                    price_adjustment = round(llm_price / base_price, 2)
                            except (ValueError, TypeError):
                                pass
                                
                        if 'strategy' in enhanced_pricing:
                            strategy = enhanced_pricing['strategy']
                            
                        if 'rationale' in enhanced_pricing:
                            explanation = enhanced_pricing['rationale']
                    else:
                        # Try to parse the whole response as JSON
                        enhanced_pricing = json.loads(llm_response)
                except Exception as e:
                    logger.error(f"Failed to parse LLM pricing JSON: {str(e)}")
                    enhanced_pricing = {}
            else:
                enhanced_pricing = {}
            
            # Build final recommendation
            recommendation = {
                "product_id": product_id,
                "store_id": store_id,
                "base_price": base_price,
                "recommended_price": recommended_price,
                "price_adjustment": price_adjustment,
                "strategy": strategy,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add additional fields from LLM if available
            if "actions" in enhanced_pricing:
                recommendation["actions"] = enhanced_pricing["actions"]
                
            if "expected_impact" in enhanced_pricing:
                recommendation["expected_impact"] = enhanced_pricing["expected_impact"]
            
            # Log action completion
            self.log_action(
                action="optimize_price_complete",
                product_id=product_id,
                store_id=store_id,
                details={
                    "strategy": strategy,
                    "recommended_price": recommended_price,
                    "price_adjustment": price_adjustment
                }
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error in price optimization: {str(e)}")
            self.log_action(
                action="optimize_price_error",
                product_id=product_id,
                store_id=store_id,
                details={
                    "error": str(e)
                }
            )
            return {
                "error": str(e),
                "recommendation": "Error occurred during price optimization"
            }
    
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
            # Get product details
            product = Product.query.get(product_id)
            if not product:
                logger.warning(f"Product not found with ID: {product_id}")
                return False
            
            # Calculate price adjustment
            price_adjustment = round(new_price / product.base_price, 2)
            
            # Log action
            self.log_action(
                action="apply_price_change",
                product_id=product_id,
                store_id=store_id,
                details={
                    "base_price": product.base_price,
                    "new_price": new_price,
                    "price_adjustment": price_adjustment
                }
            )
            
            # In a real system, this would update a pricing database
            # For now, we'll just return success
            return True
            
        except Exception as e:
            logger.error(f"Error applying price change: {str(e)}")
            self.log_action(
                action="apply_price_change_error",
                product_id=product_id,
                store_id=store_id,
                details={
                    "error": str(e),
                    "attempted_price": new_price
                }
            )
            return False
    
    def _get_market_data(self, product):
        """
        Get market data for a product to inform pricing decisions.
        
        This would typically involve fetching competitor pricing, market trends, etc.
        In this demo, we'll return simulated data or use the web scraper to get real data.
        
        Args:
            product: Product object
            
        Returns:
            Dictionary with market data
        """
        market_data = {
            "average_market_price": None,
            "price_range": None,
            "competitor_prices": [],
            "market_trends": [],
            "source": "simulated"
        }
        
        # Try to use web scraper to get real market data
        if self.scraper:
            try:
                # Construct search query for product
                search_term = f"{product.name} {product.category} price"
                
                # We could scrape e-commerce sites or price comparison sites
                # For demo purposes, we'll just log the attempt
                logger.info(f"Would search for market data with query: {search_term}")
                
                # In a real system, this might call an e-commerce API or scrape sites
                # For now, we'll use simulated data
            except Exception as e:
                logger.error(f"Error fetching market data: {str(e)}")
        
        # Simulate market data based on product info
        base_price = product.base_price
        
        # Simulate average market price (±15% of base price)
        avg_market_price = round(base_price * random.uniform(0.85, 1.15), 2)
        
        # Simulate price range
        price_range = {
            "min": round(base_price * 0.7, 2),
            "max": round(base_price * 1.3, 2)
        }
        
        # Simulate competitor prices
        competitor_prices = [
            {"name": "Competitor A", "price": round(base_price * random.uniform(0.9, 1.1), 2)},
            {"name": "Competitor B", "price": round(base_price * random.uniform(0.85, 1.2), 2)},
            {"name": "Competitor C", "price": round(base_price * random.uniform(0.8, 1.3), 2)}
        ]
        
        # Simulate market trends
        market_trends = [
            {"trend": "Seasonal demand increase" if random.random() > 0.5 else "Seasonal demand decrease"},
            {"trend": "Price competition increasing" if random.random() > 0.5 else "Market prices stabilizing"}
        ]
        
        # Update market data
        market_data.update({
            "average_market_price": avg_market_price,
            "price_range": price_range,
            "competitor_prices": competitor_prices,
            "market_trends": market_trends
        })
        
        return market_data