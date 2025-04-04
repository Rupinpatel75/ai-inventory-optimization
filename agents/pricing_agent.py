"""
Pricing Agent module for the AI Inventory Optimization System.

This module provides the pricing optimization agent that suggests
optimal prices based on market data, competitor prices, and demand elasticity.
"""

import logging
from agents.base_agent import BaseAgent
from utils.price_optimizer import calculate_optimal_price, get_pricing_recommendation, calculate_promotion_impact
from utils.web_scraper import WebScraper
from models import Product, Store, db
from datetime import datetime

logger = logging.getLogger(__name__)

class PricingAgent(BaseAgent):
    """
    Pricing optimization agent that suggests optimal prices
    based on market data, competitor prices, and demand elasticity.
    """
    
    def __init__(self):
        """Initialize the pricing agent."""
        super().__init__(agent_type="pricing")
        self.scraper = WebScraper()
    
    def get_optimal_price(self, product_id, store_id):
        """
        Calculate the optimal price for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with optimal price and parameters
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
            
            # Use current base price as starting point
            current_price = product.base_price
            
            # Calculate optimal price
            optimal = calculate_optimal_price(product_id, store_id, current_price)
            
            # Log the agent action
            self.log_action(
                action="Optimal price calculation",
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
            logger.error(f"Error calculating optimal price: {str(e)}")
            return {
                "error": f"Failed to calculate optimal price: {str(e)}"
            }
    
    def get_price_recommendation(self, product_id, store_id):
        """
        Get a pricing recommendation for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with pricing recommendation
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
            
            # Use current base price as starting point
            current_price = product.base_price
            
            # Get pricing recommendation
            recommendation = get_pricing_recommendation(product_id, store_id, current_price)
            
            # Log the agent action
            self.log_action(
                action="Price recommendation",
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
            logger.error(f"Error getting price recommendation: {str(e)}")
            return {
                "error": f"Failed to get price recommendation: {str(e)}"
            }
    
    def analyze_promotion(self, product_id, store_id, discount_pct=0.1):
        """
        Analyze the impact of a price promotion on demand and profit.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            discount_pct: Discount percentage (0-1)
            
        Returns:
            Dictionary with promotion impact assessment
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
            
            # Ensure discount is in proper format (0-1)
            if discount_pct > 1:
                discount_pct = discount_pct / 100  # Convert from percentage to decimal
            
            # Use current base price as starting point
            current_price = product.base_price
            
            # Calculate promotion impact
            impact = calculate_promotion_impact(product_id, store_id, current_price, discount_pct)
            
            # Log the agent action
            self.log_action(
                action="Promotion analysis",
                product_id=product_id,
                store_id=store_id,
                details=impact
            )
            
            # Add product and store names
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **impact
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing promotion: {str(e)}")
            return {
                "error": f"Failed to analyze promotion: {str(e)}"
            }
    
    def get_competitor_prices(self, product_id, store_id):
        """
        Get competitor prices for a product.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with competitor prices
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
            
            # Get competitor prices using the web scraper
            competitor_prices = self.scraper.get_competitor_prices(product.name, product.category)
            
            # Calculate statistics
            if competitor_prices:
                prices = [cp["price"] for cp in competitor_prices]
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                # Calculate how our price compares
                our_price = product.base_price
                relative_position = (our_price - min_price) / (max_price - min_price) if max_price > min_price else 0.5
                relative_position = round(relative_position * 100)  # Convert to percentage
                
                # Count how many competitors have lower/higher prices
                lower_count = sum(1 for p in prices if p < our_price)
                higher_count = sum(1 for p in prices if p > our_price)
                equal_count = sum(1 for p in prices if p == our_price)
                
                stats = {
                    "avg_price": round(avg_price, 2),
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2),
                    "our_price": round(our_price, 2),
                    "relative_position": f"{relative_position}%",  # e.g. "75%" means we're 75% of the way from min to max
                    "lower_count": lower_count,
                    "higher_count": higher_count,
                    "equal_count": equal_count,
                    "competitors_count": len(competitor_prices)
                }
            else:
                stats = {
                    "our_price": round(product.base_price, 2),
                    "competitors_count": 0
                }
            
            # Log the agent action
            self.log_action(
                action="Competitor price analysis",
                product_id=product_id,
                store_id=store_id,
                details={
                    "competitor_count": len(competitor_prices),
                    "stats": stats,
                    "sample": competitor_prices[:3] if competitor_prices else []
                }
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "competitor_prices": competitor_prices,
                "stats": stats
            }
        
        except Exception as e:
            logger.error(f"Error getting competitor prices: {str(e)}")
            return {
                "error": f"Failed to get competitor prices: {str(e)}"
            }
    
    def update_base_price(self, product_id, new_price):
        """
        Update the base price of a product.
        
        Args:
            product_id: ID of the product
            new_price: New base price
            
        Returns:
            Dictionary with update result
        """
        try:
            # Get product to check if it exists
            product = self.get_product(product_id)
            
            if not product:
                logger.error(f"Product {product_id} not found")
                return {
                    "error": f"Product {product_id} not found"
                }
            
            # Save old price for logging
            old_price = product.base_price
            
            # Update price
            product.base_price = new_price
            db.session.commit()
            
            # Log the agent action
            details = {
                "old_price": round(old_price, 2),
                "new_price": round(new_price, 2),
                "change": round(new_price - old_price, 2),
                "change_pct": round((new_price - old_price) / old_price * 100, 1) if old_price > 0 else 0
            }
            
            self.log_action(
                action="Base price update",
                product_id=product_id,
                details=details
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "old_price": round(old_price, 2),
                "new_price": round(new_price, 2),
                "change": round(new_price - old_price, 2),
                "change_pct": f"{details['change_pct']}%",
                "success": True
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating base price: {str(e)}")
            return {
                "error": f"Failed to update base price: {str(e)}",
                "success": False
            }
    
    def explain_recommendation(self, product_id, store_id):
        """
        Generate a natural language explanation of pricing recommendations.
        
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
            
            # Get price recommendation
            recommendation = self.get_price_recommendation(product_id, store_id)
            if "error" in recommendation:
                return recommendation
            
            # Get competitor prices (if possible)
            competitor_data = self.get_competitor_prices(product_id, store_id)
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please provide a brief explanation of the pricing recommendation for {product.name} at {store.name}.
            
            Product: {product.name}
            Category: {product.category}
            Current price: ${product.base_price:.2f}
            
            Recommendation:
            - Recommended price: ${recommendation.get('recommended_price', 0):.2f}
            - Price change: ${recommendation.get('price_change', 0):.2f} ({recommendation.get('price_change_pct', 0)}%)
            - Action: {recommendation.get('action', 'Unknown')}
            - Expected profit impact: ${recommendation.get('expected_profit_impact', 0):.2f} ({recommendation.get('expected_profit_impact_pct', 0)}%)
            - Confidence: {recommendation.get('confidence', 'medium')}
            
            """
            
            if 'stats' in competitor_data:
                stats = competitor_data.get('stats', {})
                prompt += f"""
                Competitor Analysis:
                - Average competitor price: ${stats.get('avg_price', 0):.2f}
                - Range: ${stats.get('min_price', 0):.2f} to ${stats.get('max_price', 0):.2f}
                - Competitors with lower prices: {stats.get('lower_count', 0)}
                - Competitors with higher prices: {stats.get('higher_count', 0)}
                - Our relative position: {stats.get('relative_position', '50%')}
                """
            
            prompt += """
            Please provide a 3-4 sentence explanation of this recommendation in plain language, 
            focusing on actionable insights for the store manager.
            Explain why this price is recommended and what impact it will have on profit and competitive position.
            """
            
            system_prompt = """
            You are a helpful AI assistant explaining pricing recommendations to a store manager.
            Your explanation should be clear, concise, and focused on actionable insights.
            Use plain language and avoid technical terms unless necessary.
            """
            
            explanation = self.analyze_with_llm(prompt, system_prompt)
            
            if not explanation or "error" in explanation.lower():
                # Generate a basic explanation if LLM fails
                if recommendation.get('recommendation_type') == 'increase':
                    explanation = f"Recommend increasing the price of {product.name} from ${product.base_price:.2f} to ${recommendation.get('recommended_price', 0):.2f}. "
                    explanation += f"This represents a {recommendation.get('price_change_pct', 0)}% increase. "
                    explanation += f"Expected profit impact: ${recommendation.get('expected_profit_impact', 0):.2f} ({recommendation.get('expected_profit_impact_pct', 0)}%)."
                elif recommendation.get('recommendation_type') == 'decrease':
                    explanation = f"Recommend decreasing the price of {product.name} from ${product.base_price:.2f} to ${recommendation.get('recommended_price', 0):.2f}. "
                    explanation += f"This represents a {abs(recommendation.get('price_change_pct', 0))}% decrease. "
                    explanation += f"Expected profit impact: ${recommendation.get('expected_profit_impact', 0):.2f} ({recommendation.get('expected_profit_impact_pct', 0)}%)."
                else:
                    explanation = f"Recommend maintaining the current price of ${product.base_price:.2f} for {product.name}. "
                    explanation += f"This price is already optimal based on market conditions and demand elasticity."
            
            # Log the agent action
            self.log_action(
                action="Price recommendation explanation",
                product_id=product_id,
                store_id=store_id,
                details={"explanation": explanation}
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "current_price": round(product.base_price, 2),
                "recommendation": recommendation,
                "competitor_data": competitor_data if 'error' not in competitor_data else None,
                "explanation": explanation
            }
        
        except Exception as e:
            logger.error(f"Error explaining recommendation: {str(e)}")
            return {
                "error": f"Failed to explain recommendation: {str(e)}"
            }