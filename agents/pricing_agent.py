"""
Pricing Agent module for the AI Inventory Optimization System.

This module provides the pricing optimization agent that analyzes
price elasticity, recommends optimal pricing, and forecasts promotion impact.
"""

import logging
import json
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from utils.price_optimizer import (
    calculate_optimal_price,
    get_pricing_recommendation,
    calculate_promotion_impact,
    optimize_prices_across_portfolio
)
from models import Product, Store, db
import pandas as pd

logger = logging.getLogger(__name__)

class PricingAgent(BaseAgent):
    """
    Pricing optimization agent that analyzes price elasticity,
    recommends optimal pricing, and forecasts promotion impact.
    """
    
    def __init__(self):
        """Initialize the pricing agent."""
        super().__init__(agent_type="pricing")
    
    def calculate_optimal_price(self, product_id, store_id, elasticity=None):
        """
        Calculate the optimal price for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            elasticity: Price elasticity of demand (optional)
            
        Returns:
            Dictionary with optimal price information
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
            
            # Use current base price from the product
            current_price = product.base_price
            
            # Calculate optimal price
            result = calculate_optimal_price(product_id, store_id, current_price, elasticity)
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Optimal price calculation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "current_price": result.get("current_price", 0),
                    "optimal_price": result.get("optimal_price", 0),
                    "profit_change_pct": result.get("profit_change_pct", 0)
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate explanation
            explanation = self._explain_optimal_price(result, product, store)
            result["explanation"] = explanation
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating optimal price: {str(e)}")
            return {
                "error": f"Failed to calculate optimal price: {str(e)}"
            }
    
    def get_pricing_recommendation(self, product_id, store_id):
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
            
            # Use current base price from the product
            current_price = product.base_price
            
            # Get pricing recommendation
            result = get_pricing_recommendation(product_id, store_id, current_price)
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Pricing recommendation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "recommendation_type": result.get("recommendation_type", ""),
                    "recommended_price": result.get("recommended_price", 0),
                    "price_change_pct": result.get("price_change_pct", 0),
                    "confidence": result.get("confidence", "")
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            result["current_price"] = current_price
            
            # Generate explanation
            explanation = self._generate_pricing_explanation(result, product, store)
            result["explanation"] = explanation
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting pricing recommendation: {str(e)}")
            return {
                "error": f"Failed to get pricing recommendation: {str(e)}"
            }
    
    def calculate_promotion_impact(self, product_id, store_id, discount_pct):
        """
        Calculate the impact of a price promotion on demand and profit.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            discount_pct: Discount percentage (0-1 or 0-100)
            
        Returns:
            Dictionary with promotion impact details
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
            
            # Use current base price from the product
            current_price = product.base_price
            
            # Normalize discount_pct to 0-1 range if needed
            if discount_pct > 1:
                discount_pct = discount_pct / 100
            
            # Calculate promotion impact
            result = calculate_promotion_impact(product_id, store_id, current_price, discount_pct)
            
            if "error" in result:
                return result
            
            # Log the agent action
            self.log_action(
                action="Promotion impact calculation",
                product_id=product_id,
                store_id=store_id,
                details={
                    "discount_pct": result.get("discount_pct", 0),
                    "promotion_price": result.get("promotion_price", 0),
                    "demand_increase_pct": result.get("demand_increase_pct", 0),
                    "profit_change_pct": result.get("profit_change_pct", 0),
                    "is_recommended": result.get("is_recommended", False)
                }
            )
            
            # Add product and store names to the response
            result["product_name"] = product.name
            result["store_name"] = store.name
            
            # Generate recommendation
            recommendation = self._generate_promotion_recommendation(result, product, store)
            result["recommendation"] = recommendation
            
            return result
        
        except Exception as e:
            logger.error(f"Error calculating promotion impact: {str(e)}")
            return {
                "error": f"Failed to calculate promotion impact: {str(e)}"
            }
    
    def optimize_category_prices(self, category):
        """
        Optimize prices across a portfolio of products in the same category.
        
        Args:
            category: Product category to optimize
            
        Returns:
            Dictionary with optimized prices
        """
        try:
            # Get products in the given category
            products = db.session.query(Product).filter_by(category=category).all()
            
            if not products:
                return {
                    "error": f"No products found in category: {category}"
                }
            
            # Convert products to DataFrame for optimization
            product_data = [{
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'base_price': p.base_price
            } for p in products]
            
            product_df = pd.DataFrame(product_data)
            
            # Optimize prices
            result_df = optimize_prices_across_portfolio(product_df)
            
            if result_df is None:
                return {
                    "error": "Failed to optimize prices"
                }
            
            # Convert results back to a dictionary
            results = result_df.to_dict('records')
            
            # Calculate summary statistics
            avg_price_change = sum(r.get('price_change_pct', 0) for r in results) / len(results)
            avg_profit_impact = sum(r.get('profit_impact_pct', 0) for r in results) / len(results)
            
            increases = sum(1 for r in results if r.get('recommendation_type') == 'increase')
            decreases = sum(1 for r in results if r.get('recommendation_type') == 'decrease')
            maintains = sum(1 for r in results if r.get('recommendation_type') == 'maintain')
            
            # Log the agent action
            self.log_action(
                action="Category price optimization",
                details={
                    "category": category,
                    "product_count": len(products),
                    "avg_price_change": round(avg_price_change, 1),
                    "avg_profit_impact": round(avg_profit_impact, 1),
                    "increases": increases,
                    "decreases": decreases,
                    "maintains": maintains
                }
            )
            
            # Generate summary
            summary = self._generate_category_summary(
                category, results, avg_price_change, avg_profit_impact, 
                increases, decreases, maintains
            )
            
            return {
                "category": category,
                "product_count": len(products),
                "avg_price_change_pct": round(avg_price_change, 1),
                "avg_profit_impact_pct": round(avg_profit_impact, 1),
                "summary": summary,
                "recommendations": results,
                "increases": increases,
                "decreases": decreases,
                "maintains": maintains
            }
        
        except Exception as e:
            logger.error(f"Error optimizing category prices: {str(e)}")
            return {
                "error": f"Failed to optimize category prices: {str(e)}"
            }
    
    def compare_pricing_strategies(self, product_id, store_id, strategies=None):
        """
        Compare different pricing strategies for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            strategies: List of pricing strategies to compare (optional)
            
        Returns:
            Dictionary with strategy comparison
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
            
            # Use current base price from the product
            current_price = product.base_price
            
            # Define strategies if not provided
            if not strategies:
                strategies = [
                    {"name": "Current Price", "description": "Maintain current pricing", "change": 0},
                    {"name": "Optimal Price", "description": "Price for maximum profit", "change": "optimal"},
                    {"name": "5% Increase", "description": "Modest price increase", "change": 0.05},
                    {"name": "10% Increase", "description": "Significant price increase", "change": 0.10},
                    {"name": "5% Discount", "description": "Small discount", "change": -0.05},
                    {"name": "10% Discount", "description": "Moderate discount", "change": -0.10},
                    {"name": "25% Discount", "description": "Deep discount promotion", "change": -0.25}
                ]
            
            # Get optimal price calculation for reference
            optimal_result = calculate_optimal_price(product_id, store_id, current_price)
            
            if "error" in optimal_result:
                return optimal_result
            
            # Calculate results for each strategy
            strategy_results = []
            
            for strategy in strategies:
                change = strategy["change"]
                
                if change == "optimal":
                    # Use optimal price from the calculation
                    price = optimal_result["optimal_price"]
                    
                    # Copy relevant metrics from optimal result
                    strategy_result = {
                        "strategy_name": strategy["name"],
                        "description": strategy["description"],
                        "price": price,
                        "price_change_pct": optimal_result["price_difference_pct"],
                        "expected_demand": optimal_result["expected_demand"],
                        "demand_change_pct": optimal_result["demand_change_pct"],
                        "expected_profit": optimal_result["expected_profit"],
                        "profit_change_pct": optimal_result["profit_change_pct"]
                    }
                else:
                    # Calculate price based on percentage change
                    price = current_price * (1 + change)
                    
                    # Calculate impact of this price using a promotion impact calculation
                    # (reusing the promotion logic, but for any price change)
                    discount_pct = -change if change < 0 else 0
                    impact_result = calculate_promotion_impact(product_id, store_id, current_price, discount_pct)
                    
                    if "error" in impact_result:
                        continue
                    
                    # For price increases, adjust demand using elasticity from optimal price calculation
                    if change > 0:
                        elasticity = optimal_result.get("elasticity", -1.0)
                        price_ratio = price / current_price
                        demand_change_pct = ((price_ratio ** elasticity) - 1) * 100
                        expected_demand = optimal_result.get("current_demand", 0) * (1 + demand_change_pct/100)
                        
                        # Calculate expected profit
                        marginal_cost = current_price * 0.6  # Assume 60% of price is cost, same as in optimizer
                        profit_margin = price - marginal_cost
                        expected_profit = profit_margin * expected_demand
                        profit_change_pct = ((expected_profit / optimal_result.get("current_profit", 1)) - 1) * 100
                    else:
                        # For discounts, use promotion impact calculation
                        demand_change_pct = impact_result.get("demand_increase_pct", 0)
                        expected_demand = impact_result.get("expected_promotion_demand", 0)
                        expected_profit = impact_result.get("promotion_profit", 0)
                        profit_change_pct = impact_result.get("profit_change_pct", 0)
                    
                    strategy_result = {
                        "strategy_name": strategy["name"],
                        "description": strategy["description"],
                        "price": round(price, 2),
                        "price_change_pct": round(change * 100, 1),
                        "expected_demand": round(expected_demand),
                        "demand_change_pct": round(demand_change_pct, 1),
                        "expected_profit": round(expected_profit, 2),
                        "profit_change_pct": round(profit_change_pct, 1)
                    }
                
                strategy_results.append(strategy_result)
            
            # Sort strategies by expected profit
            strategy_results.sort(key=lambda x: x["expected_profit"], reverse=True)
            
            # Calculate comparison statistics
            best_strategy = strategy_results[0]["strategy_name"] if strategy_results else "Unknown"
            max_profit = max((s["expected_profit"] for s in strategy_results), default=0)
            max_demand = max((s["expected_demand"] for s in strategy_results), default=0)
            
            # Log the agent action
            self.log_action(
                action="Pricing strategy comparison",
                product_id=product_id,
                store_id=store_id,
                details={
                    "strategies_count": len(strategy_results),
                    "best_strategy": best_strategy,
                    "current_price": current_price,
                    "optimal_price": optimal_result.get("optimal_price", 0)
                }
            )
            
            # Generate recommendation
            recommendation = self._generate_strategy_recommendation(
                strategy_results, product, store, current_price
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "current_price": current_price,
                "best_strategy": best_strategy,
                "max_profit_strategy": strategy_results[0]["strategy_name"] if strategy_results else "Unknown",
                "max_demand_strategy": next((s["strategy_name"] for s in strategy_results if s["expected_demand"] == max_demand), "Unknown"),
                "strategies": strategy_results,
                "recommendation": recommendation
            }
        
        except Exception as e:
            logger.error(f"Error comparing pricing strategies: {str(e)}")
            return {
                "error": f"Failed to compare pricing strategies: {str(e)}"
            }
    
    def analyze_competitor_prices(self, product_id, store_id, competitor_prices=None):
        """
        Analyze competitor prices and provide recommendations.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            competitor_prices: Dictionary of competitor names and prices (optional)
            
        Returns:
            Dictionary with competitor price analysis
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
            
            # Use current base price from the product
            current_price = product.base_price
            
            # Use simulated competitor prices if not provided
            if not competitor_prices:
                # In a real implementation, this would come from a web scraper or external data source
                # For now, we'll use simulated values
                import random
                random.seed(product_id * store_id)  # For consistent results
                
                competitor_names = [
                    "MegaRetail", "Value Mart", "Super Deals", "Grand Merchandise", 
                    "Quality Products Inc."
                ]
                
                # Generate prices with some variation around current price
                competitor_prices = {}
                for name in competitor_names:
                    # Vary between -15% and +15% of current price
                    variation = random.uniform(-0.15, 0.15)
                    competitor_prices[name] = round(current_price * (1 + variation), 2)
            
            # Calculate statistics
            prices = list(competitor_prices.values())
            avg_competitor_price = sum(prices) / len(prices) if prices else 0
            min_competitor_price = min(prices) if prices else 0
            max_competitor_price = max(prices) if prices else 0
            
            # Calculate percentile of our price among competitors
            all_prices = prices + [current_price]
            all_prices.sort()
            our_rank = all_prices.index(current_price)
            percentile = our_rank / (len(all_prices) - 1) * 100 if len(all_prices) > 1 else 50
            
            # Determine our position relative to competitors
            if current_price < min_competitor_price:
                position = "below all competitors"
                position_pct = round((min_competitor_price - current_price) / current_price * 100, 1)
            elif current_price > max_competitor_price:
                position = "above all competitors"
                position_pct = round((current_price - max_competitor_price) / max_competitor_price * 100, 1)
            else:
                position = "within competitor range"
                position_pct = round(abs(current_price - avg_competitor_price) / avg_competitor_price * 100, 1)
            
            # Get optimal price calculation for reference
            optimal_result = calculate_optimal_price(product_id, store_id, current_price)
            optimal_price = optimal_result.get("optimal_price", current_price) if "error" not in optimal_result else current_price
            
            # Log the agent action
            self.log_action(
                action="Competitor price analysis",
                product_id=product_id,
                store_id=store_id,
                details={
                    "current_price": current_price,
                    "avg_competitor_price": round(avg_competitor_price, 2),
                    "min_competitor_price": min_competitor_price,
                    "max_competitor_price": max_competitor_price,
                    "position": position,
                    "competitor_count": len(competitor_prices)
                }
            )
            
            # Generate recommendation
            recommendation = self._generate_competitor_recommendation(
                current_price, optimal_price, avg_competitor_price, 
                position, position_pct, product, store
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "current_price": current_price,
                "optimal_price": optimal_price,
                "avg_competitor_price": round(avg_competitor_price, 2),
                "min_competitor_price": min_competitor_price,
                "max_competitor_price": max_competitor_price,
                "price_percentile": round(percentile),  # 0 = lowest, 100 = highest
                "position": position,
                "position_pct": position_pct,
                "competitor_prices": competitor_prices,
                "recommendation": recommendation
            }
        
        except Exception as e:
            logger.error(f"Error analyzing competitor prices: {str(e)}")
            return {
                "error": f"Failed to analyze competitor prices: {str(e)}"
            }
    
    def _explain_optimal_price(self, result, product, store):
        """Generate an explanation for optimal price calculation."""
        try:
            current_price = result.get("current_price", 0)
            optimal_price = result.get("optimal_price", 0)
            price_difference = result.get("price_difference", 0)
            price_difference_pct = result.get("price_difference_pct", 0)
            profit_change_pct = result.get("profit_change_pct", 0)
            elasticity = result.get("elasticity", 0)
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please explain the following optimal price calculation in clear, concise language:
            
            Product: {product.name}
            Store: {store.name}
            Current Price: ${current_price}
            Optimal Price: ${optimal_price}
            Price Difference: ${price_difference} ({price_difference_pct}%)
            Expected Profit Change: {profit_change_pct}%
            Price Elasticity: {elasticity}
            
            Explain what this means in practical terms for pricing strategy.
            Keep it brief and actionable, 2-3 sentences.
            """
            
            explanation = self.analyze_with_llm(prompt)
            
            if not explanation:
                # Fallback if LLM is not available
                if price_difference > 0:
                    explanation = (
                        f"Our analysis indicates that increasing the price of {product.name} from ${current_price} to "
                        f"${optimal_price} (a {price_difference_pct}% increase) would optimize profitability, potentially "
                        f"increasing profits by {profit_change_pct}%. This product has an elasticity of {elasticity}, "
                        f"meaning customers are relatively {'insensitive' if abs(elasticity) < 1 else 'sensitive'} to price changes."
                    )
                elif price_difference < 0:
                    explanation = (
                        f"Our analysis indicates that decreasing the price of {product.name} from ${current_price} to "
                        f"${optimal_price} (a {abs(price_difference_pct)}% decrease) would optimize profitability, potentially "
                        f"increasing profits by {profit_change_pct}%. This product has an elasticity of {elasticity}, "
                        f"meaning customers are relatively {'insensitive' if abs(elasticity) < 1 else 'sensitive'} to price changes."
                    )
                else:
                    explanation = (
                        f"The current price of ${current_price} for {product.name} appears to be very close to optimal. "
                        f"This product has an elasticity of {elasticity}, meaning customers are relatively "
                        f"{'insensitive' if abs(elasticity) < 1 else 'sensitive'} to price changes. Maintain the current "
                        f"pricing strategy and continue monitoring market conditions."
                    )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating optimal price explanation: {str(e)}")
            return "Error generating explanation"
    
    def _generate_pricing_explanation(self, result, product, store):
        """Generate an explanation for pricing recommendation."""
        try:
            recommendation_type = result.get("recommendation_type", "maintain")
            recommended_price = result.get("recommended_price", 0)
            current_price = result.get("current_price", 0)
            price_change_pct = result.get("price_change_pct", 0)
            profit_impact_pct = result.get("expected_profit_impact_pct", 0)
            confidence = result.get("confidence", "medium")
            action = result.get("action", "Maintain current price")
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please provide a brief, actionable explanation of the following pricing recommendation:
            
            Product: {product.name}
            Store: {store.name}
            Action: {action}
            Current Price: ${current_price}
            Recommended Price: ${recommended_price}
            Price Change: {price_change_pct}%
            Expected Profit Impact: {profit_impact_pct}%
            Confidence Level: {confidence}
            
            Provide a 2-3 sentence explanation of this recommendation and why it makes sense
            from a business perspective.
            """
            
            explanation = self.analyze_with_llm(prompt)
            
            if not explanation:
                # Fallback if LLM is not available
                if recommendation_type == "increase":
                    explanation = (
                        f"We recommend increasing the price of {product.name} from ${current_price} to "
                        f"${recommended_price} ({price_change_pct}% increase), which is projected to increase "
                        f"profits by approximately {profit_impact_pct}%. Our {confidence} confidence in this "
                        f"recommendation is based on price elasticity analysis showing that demand will not "
                        f"decrease significantly at the higher price point."
                    )
                elif recommendation_type == "decrease":
                    explanation = (
                        f"We recommend decreasing the price of {product.name} from ${current_price} to "
                        f"${recommended_price} ({abs(price_change_pct)}% decrease), which is projected to increase "
                        f"profits by approximately {profit_impact_pct}%. Our {confidence} confidence in this "
                        f"recommendation is based on price elasticity analysis showing that the increased demand "
                        f"at the lower price point will more than offset the reduced margin."
                    )
                else:
                    explanation = (
                        f"We recommend maintaining the current price of ${current_price} for {product.name}, "
                        f"as our analysis indicates it is already at or near the optimal price point. "
                        f"With {confidence} confidence, we believe this approach will maximize profitability "
                        f"while maintaining market position."
                    )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating pricing explanation: {str(e)}")
            return "Error generating explanation"
    
    def _generate_promotion_recommendation(self, result, product, store):
        """Generate a recommendation based on promotion impact analysis."""
        try:
            is_recommended = result.get("is_recommended", False)
            discount_pct = result.get("discount_pct", 0)
            regular_price = result.get("regular_price", 0)
            promotion_price = result.get("promotion_price", 0)
            demand_increase_pct = result.get("demand_increase_pct", 0)
            profit_change_pct = result.get("profit_change_pct", 0)
            promotion_roi = result.get("promotion_roi", 0)
            
            # Generate recommendation using LLM if available
            prompt = f"""
            Please provide a brief, actionable recommendation based on the following promotion analysis:
            
            Product: {product.name}
            Store: {store.name}
            Regular Price: ${regular_price}
            Promotion Price: ${promotion_price}
            Discount: {discount_pct}%
            Expected Demand Increase: {demand_increase_pct}%
            Profit Impact: {profit_change_pct}%
            Promotion ROI: {promotion_roi}%
            Recommended: {"Yes" if is_recommended else "No"}
            
            Provide a 2-3 sentence recommendation about whether to proceed with this promotion
            and what specific actions to take.
            """
            
            recommendation = self.analyze_with_llm(prompt)
            
            if not recommendation:
                # Fallback if LLM is not available
                if is_recommended:
                    recommendation = (
                        f"RECOMMENDED: Proceed with the {discount_pct}% discount promotion for {product.name}, "
                        f"reducing the price from ${regular_price} to ${promotion_price}. This promotion is projected "
                        f"to increase demand by {demand_increase_pct}%, resulting in a {profit_change_pct}% increase "
                        f"in profit and a promotion ROI of {promotion_roi}%. Implement this promotion during a period "
                        f"of typically lower sales to maximize its impact."
                    )
                else:
                    recommendation = (
                        f"NOT RECOMMENDED: The proposed {discount_pct}% discount for {product.name} is projected "
                        f"to {'decrease' if profit_change_pct < 0 else 'increase'} profits by only {abs(profit_change_pct)}%, "
                        f"which does not justify the promotion. Although demand would increase by {demand_increase_pct}%, "
                        f"the reduced margin would {'outweigh' if profit_change_pct < 0 else 'barely offset'} these gains. "
                        f"Consider a smaller discount or alternative promotional strategies for this product."
                    )
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating promotion recommendation: {str(e)}")
            return "Error generating recommendation"
    
    def _generate_category_summary(self, category, results, avg_price_change, avg_profit_impact, 
                                increases, decreases, maintains):
        """Generate a summary for category price optimization."""
        try:
            # Generate summary using LLM if available
            prompt = f"""
            Please provide a brief summary of the following category price optimization:
            
            Category: {category}
            Number of Products: {len(results)}
            Average Price Change: {round(avg_price_change, 1)}%
            Average Profit Impact: {round(avg_profit_impact, 1)}%
            Price Increases Recommended: {increases} products
            Price Decreases Recommended: {decreases} products
            Price Maintenance Recommended: {maintains} products
            
            Provide a 3-4 sentence summary of these results and the overall strategy recommendation
            for this product category.
            """
            
            summary = self.analyze_with_llm(prompt)
            
            if not summary:
                # Fallback if LLM is not available
                if avg_profit_impact > 3:
                    summary = (
                        f"Our price optimization analysis for the {category} category ({len(results)} products) indicates "
                        f"a potential profit improvement of {round(avg_profit_impact, 1)}% with an average price change of "
                        f"{round(avg_price_change, 1)}%. We recommend price increases for {increases} products and decreases "
                        f"for {decreases} products, while maintaining current prices for {maintains} products. "
                        f"Implementing these price adjustments could significantly enhance category profitability while "
                        f"maintaining competitive positioning."
                    )
                elif avg_profit_impact > 0:
                    summary = (
                        f"Our price optimization analysis for the {category} category ({len(results)} products) shows "
                        f"a modest potential profit improvement of {round(avg_profit_impact, 1)}% with an average price change of "
                        f"{round(avg_price_change, 1)}%. Price adjustments are recommended for {increases + decreases} products, "
                        f"with {maintains} products maintaining current prices. Consider implementing these changes gradually, "
                        f"prioritizing products with the highest individual profit impact."
                    )
                else:
                    summary = (
                        f"Based on our analysis of the {category} category ({len(results)} products), limited profit improvement "
                        f"opportunities exist with current market conditions. The projected average profit impact of "
                        f"{round(avg_profit_impact, 1)}% suggests that most products in this category are already priced "
                        f"appropriately relative to demand elasticity. Maintain current pricing for most products while "
                        f"closely monitoring market conditions for changes in demand patterns."
                    )
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating category summary: {str(e)}")
            return "Error generating summary"
    
    def _generate_strategy_recommendation(self, strategy_results, product, store, current_price):
        """Generate a recommendation based on pricing strategy comparison."""
        try:
            best_strategy = strategy_results[0] if strategy_results else {}
            best_name = best_strategy.get("strategy_name", "Unknown")
            best_price = best_strategy.get("price", current_price)
            best_profit_change = best_strategy.get("profit_change_pct", 0)
            
            current_strategy = next((s for s in strategy_results if s["strategy_name"] == "Current Price"), None)
            optimal_strategy = next((s for s in strategy_results if s["strategy_name"] == "Optimal Price"), None)
            
            # Generate recommendation using LLM if available
            prompt = f"""
            Please provide a brief, actionable recommendation based on the pricing strategy comparison:
            
            Product: {product.name}
            Store: {store.name}
            Current Price: ${current_price}
            Best Performing Strategy: {best_name} (${best_price})
            Expected Profit Change with Best Strategy: {best_profit_change}%
            
            Provide a 2-3 sentence recommendation about which pricing strategy to implement
            and why it's the best choice among the alternatives.
            """
            
            recommendation = self.analyze_with_llm(prompt)
            
            if not recommendation:
                # Fallback if LLM is not available
                if best_name == "Current Price":
                    recommendation = (
                        f"After comparing multiple pricing strategies for {product.name}, we recommend maintaining "
                        f"the current price of ${current_price}. This strategy outperforms all alternatives in terms "
                        f"of expected profitability. Continue monitoring market conditions and competitor pricing "
                        f"to ensure this remains the optimal approach."
                    )
                else:
                    recommendation = (
                        f"Based on our comprehensive strategy comparison, we recommend implementing the {best_name} "
                        f"strategy for {product.name}, setting the price at ${best_price}. This approach is projected "
                        f"to {'increase' if best_profit_change > 0 else 'maintain'} profits by {abs(best_profit_change)}% "
                        f"compared to the current price of ${current_price}. Consider implementing this change "
                        f"{'immediately' if best_profit_change > 5 else 'within the next pricing review cycle'}, monitoring "
                        f"sales closely to verify the projected impact."
                    )
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating strategy recommendation: {str(e)}")
            return "Error generating recommendation"
    
    def _generate_competitor_recommendation(self, current_price, optimal_price, avg_competitor_price, 
                                         position, position_pct, product, store):
        """Generate a recommendation based on competitor price analysis."""
        try:
            # Generate recommendation using LLM if available
            prompt = f"""
            Please provide a brief, actionable recommendation based on the competitor price analysis:
            
            Product: {product.name}
            Store: {store.name}
            Current Price: ${current_price}
            Optimal Price (based on elasticity): ${optimal_price}
            Average Competitor Price: ${avg_competitor_price}
            Position Relative to Competitors: {position.title()} ({position_pct}%)
            
            Provide a 2-3 sentence recommendation about how to adjust pricing given both
            the competitive landscape and our optimal pricing calculation.
            """
            
            recommendation = self.analyze_with_llm(prompt)
            
            if not recommendation:
                # Fallback if LLM is not available
                if position == "below all competitors":
                    if optimal_price > current_price:
                        recommendation = (
                            f"While {product.name} is currently priced {position_pct}% below all competitors, "
                            f"our elasticity analysis suggests increasing the price from ${current_price} to ${optimal_price} "
                            f"would optimize profitability. Consider a gradual price increase to bridge this gap, "
                            f"taking advantage of your competitive price advantage while moving closer to the profit-maximizing price point."
                        )
                    else:
                        recommendation = (
                            f"{product.name} is currently priced {position_pct}% below all competitors, which aligns with "
                            f"our elasticity-based optimal price of ${optimal_price}. Maintain this competitive pricing "
                            f"position to maximize market share and profits. Monitor competitor reactions to ensure "
                            f"this price advantage is sustainable."
                        )
                elif position == "above all competitors":
                    if optimal_price < current_price:
                        recommendation = (
                            f"{product.name} is currently priced {position_pct}% above all competitors, which may be "
                            f"hurting sales. Our elasticity analysis suggests a lower price of ${optimal_price} would "
                            f"optimize profitability. Consider reducing the price to improve price competitiveness "
                            f"while maintaining appropriate margins."
                        )
                    else:
                        recommendation = (
                            f"Despite being priced {position_pct}% above all competitors, our elasticity analysis for "
                            f"{product.name} supports the current premium pricing strategy. The optimal price of ${optimal_price} "
                            f"suggests customers value this product sufficiently to justify the premium. Maintain this "
                            f"positioning but ensure marketing clearly communicates the product's value proposition."
                        )
                else:  # within competitor range
                    if abs(current_price - optimal_price) / current_price > 0.05:
                        recommendation = (
                            f"While {product.name} is currently priced within the competitive range, our elasticity "
                            f"analysis suggests a {'higher' if optimal_price > current_price else 'lower'} price of "
                            f"${optimal_price} would optimize profitability. Consider adjusting the price closer to "
                            f"the optimal level while remaining mindful of your competitive positioning at "
                            f"${avg_competitor_price} on average."
                        )
                    else:
                        recommendation = (
                            f"The current price of ${current_price} for {product.name} is well-positioned within the "
                            f"competitive range and very close to our calculated optimal price of ${optimal_price}. "
                            f"Maintain the current pricing strategy, which effectively balances market competitiveness "
                            f"(average competitor price: ${avg_competitor_price}) with profit optimization."
                        )
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Error generating competitor recommendation: {str(e)}")
            return "Error generating recommendation"