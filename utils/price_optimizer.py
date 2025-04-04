"""
Price optimization utility for the AI Inventory Optimization System.

This module provides functions for optimizing product pricing
based on demand elasticity, competitor prices, and market trends.
"""

import logging
import math
import random
import pandas as pd
import numpy as np
from utils.forecasting import predict_demand

logger = logging.getLogger(__name__)

def calculate_optimal_price(product_id, store_id, current_price, elasticity=None):
    """
    Calculate the optimal price using price elasticity of demand.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current price of the product
        elasticity: Price elasticity of demand (optional)
        
    Returns:
        Dictionary with optimal price information
    """
    try:
        # In a real implementation, we would estimate price elasticity from historical data
        # For now, we'll use a simulated value
        if elasticity is None:
            # Most products have elasticity between -0.5 (inelastic) and -2.0 (elastic)
            elasticity = random.uniform(-2.0, -0.5)
        
        # Get current demand at current price
        demand_data = predict_demand(product_id, store_id, days=30)
        if isinstance(demand_data, dict) and "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract demand quantities
        current_demand = demand_data.get("avg_daily_demand", 10) * 30  # Monthly demand
        
        # Calculate marginal cost (in a real system, this would come from database)
        marginal_cost = current_price * 0.6  # Assume 60% of price is cost
        
        # Calculate optimal price using elasticity formula
        # For profit maximization, optimal price is: P = MC / (1 + 1/e)
        # Where: P = optimal price, MC = marginal cost, e = price elasticity
        optimal_price = marginal_cost / (1 + 1/elasticity)
        
        # Ensure price is positive
        optimal_price = max(optimal_price, marginal_cost * 1.1)  # At least 10% markup
        
        # Calculate expected demand at optimal price
        # Using constant elasticity demand function: Q2 = Q1 * (P2/P1)^e
        price_ratio = optimal_price / current_price
        expected_demand = current_demand * (price_ratio ** elasticity)
        
        # Calculate profit margins and expected profit
        current_margin = current_price - marginal_cost
        optimal_margin = optimal_price - marginal_cost
        
        current_profit = current_margin * current_demand
        expected_profit = optimal_margin * expected_demand
        
        # Round prices to appropriate precision
        optimal_price = round(optimal_price, 2)
        
        return {
            "current_price": round(current_price, 2),
            "optimal_price": optimal_price,
            "price_difference": round(optimal_price - current_price, 2),
            "price_difference_pct": round((optimal_price - current_price) / current_price * 100, 1),
            "elasticity": round(elasticity, 2),
            "current_demand": round(current_demand),
            "expected_demand": round(expected_demand),
            "demand_change_pct": round((expected_demand - current_demand) / current_demand * 100, 1),
            "current_margin": round(current_margin, 2),
            "optimal_margin": round(optimal_margin, 2),
            "current_profit": round(current_profit, 2),
            "expected_profit": round(expected_profit, 2),
            "profit_change": round(expected_profit - current_profit, 2),
            "profit_change_pct": round((expected_profit - current_profit) / current_profit * 100, 1)
        }
    
    except Exception as e:
        logger.error(f"Error calculating optimal price: {str(e)}")
        return {"error": f"Failed to calculate optimal price: {str(e)}"}

def get_pricing_recommendation(product_id, store_id, current_price):
    """
    Get a pricing recommendation including action, confidence level, and rationale.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current price of the product
        
    Returns:
        Dictionary with pricing recommendation details
    """
    try:
        # Calculate optimal price
        optimal = calculate_optimal_price(product_id, store_id, current_price)
        
        if "error" in optimal:
            return optimal
        
        # Extract key values
        optimal_price = optimal["optimal_price"]
        price_difference = optimal["price_difference"]
        price_difference_pct = optimal["price_difference_pct"]
        profit_change = optimal["profit_change"]
        profit_change_pct = optimal["profit_change_pct"]
        
        # Determine recommendation based on price difference
        # Only recommend changes if the difference is significant (>3%)
        if price_difference_pct > 3:
            recommendation_type = "increase"
            action = "Increase price"
        elif price_difference_pct < -3:
            recommendation_type = "decrease"
            action = "Decrease price"
        else:
            recommendation_type = "maintain"
            action = "Maintain current price"
        
        # Determine confidence level based on elasticity reliability
        # In a real system, this would be based on statistical measures
        elasticity_reliability = random.uniform(0.6, 0.9)  # Simulated
        
        if elasticity_reliability > 0.8:
            confidence = "high"
        elif elasticity_reliability > 0.7:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "recommended_price": optimal_price,
            "price_change": price_difference,
            "price_change_pct": price_difference_pct,
            "recommendation_type": recommendation_type,
            "action": action,
            "confidence": confidence,
            "expected_profit_impact": profit_change,
            "expected_profit_impact_pct": profit_change_pct,
            "elasticity": optimal["elasticity"]
        }
    
    except Exception as e:
        logger.error(f"Error getting pricing recommendation: {str(e)}")
        return {"error": f"Failed to get pricing recommendation: {str(e)}"}

def calculate_promotion_impact(product_id, store_id, current_price, discount_pct):
    """
    Calculate the impact of a price promotion on demand and profit.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current regular price of the product
        discount_pct: Discount percentage (0-1)
        
    Returns:
        Dictionary with promotion impact details
    """
    try:
        # Ensure discount is in proper format (0-1)
        if discount_pct > 1:
            discount_pct = discount_pct / 100
        
        # Calculate promotion price
        promotion_price = current_price * (1 - discount_pct)
        
        # Get current demand at regular price
        demand_data = predict_demand(product_id, store_id, days=30)
        if isinstance(demand_data, dict) and "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract demand quantities and estimate elasticity
        current_demand = demand_data.get("avg_daily_demand", 10) * 30  # Monthly demand
        elasticity = random.uniform(-3.0, -1.0)  # Higher elasticity during promotions
        
        # Calculate expected demand during promotion
        # Using constant elasticity demand function: Q2 = Q1 * (P2/P1)^e
        price_ratio = promotion_price / current_price
        promotion_demand = current_demand * (price_ratio ** elasticity)
        
        # Calculate profit margins and expected profit
        marginal_cost = current_price * 0.6  # Assume 60% of price is cost
        
        current_margin = current_price - marginal_cost
        promotion_margin = promotion_price - marginal_cost
        
        current_profit = current_margin * current_demand
        promotion_profit = promotion_margin * promotion_demand
        
        # Calculate ROI of promotion
        profit_change = promotion_profit - current_profit
        revenue_sacrificed = (current_price - promotion_price) * promotion_demand
        promotion_roi = profit_change / revenue_sacrificed if revenue_sacrificed > 0 else 0
        
        # Determine if promotion is recommended
        is_recommended = promotion_profit > current_profit
        
        return {
            "regular_price": round(current_price, 2),
            "promotion_price": round(promotion_price, 2),
            "discount_pct": round(discount_pct * 100, 1),
            "regular_demand": round(current_demand),
            "expected_promotion_demand": round(promotion_demand),
            "demand_increase": round(promotion_demand - current_demand),
            "demand_increase_pct": round((promotion_demand - current_demand) / current_demand * 100, 1),
            "regular_profit": round(current_profit, 2),
            "promotion_profit": round(promotion_profit, 2),
            "profit_change": round(profit_change, 2),
            "profit_change_pct": round((promotion_profit - current_profit) / current_profit * 100, 1),
            "promotion_roi": round(promotion_roi * 100, 1),
            "is_recommended": is_recommended,
            "elasticity_during_promotion": round(elasticity, 2)
        }
    
    except Exception as e:
        logger.error(f"Error calculating promotion impact: {str(e)}")
        return {"error": f"Failed to calculate promotion impact: {str(e)}"}

def optimize_prices_across_portfolio(product_data, elasticity_matrix=None):
    """
    Optimize prices across a portfolio of products considering cross-elasticities.
    
    Args:
        product_data: DataFrame with product information including current prices
        elasticity_matrix: Matrix of own and cross-price elasticities (optional)
        
    Returns:
        DataFrame with optimized prices and expected profit impact
    """
    try:
        # In a real implementation, this would use advanced mathematical optimization
        # considering own-price and cross-price elasticities
        
        # For simplicity, we'll just apply individual product optimization
        results = []
        
        for _, product in product_data.iterrows():
            product_id = product.get('id')
            current_price = product.get('base_price')
            
            # Get simple recommendation (assumes store_id=1 for simplicity)
            recommendation = get_pricing_recommendation(product_id, 1, current_price)
            
            if "error" not in recommendation:
                results.append({
                    'product_id': product_id,
                    'current_price': current_price,
                    'recommended_price': recommendation.get('recommended_price'),
                    'price_change_pct': recommendation.get('price_change_pct'),
                    'profit_impact_pct': recommendation.get('expected_profit_impact_pct'),
                    'recommendation_type': recommendation.get('recommendation_type'),
                    'confidence': recommendation.get('confidence')
                })
        
        return pd.DataFrame(results) if results else None
    
    except Exception as e:
        logger.error(f"Error optimizing portfolio prices: {str(e)}")
        return None