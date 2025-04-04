"""
Price Optimizer module for the AI Inventory Optimization System.

This module provides utilities for optimizing product pricing
based on demand elasticity, competitor pricing, and profit margins.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from utils.data_loader import get_pricing_metrics
from utils.forecasting import predict_demand

logger = logging.getLogger(__name__)

def calculate_optimal_price(product_id: int, store_id: int, current_price: float) -> Dict[str, Any]:
    """
    Calculate the optimal price for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current price of the product
        
    Returns:
        Dict with optimal price and parameters
    """
    try:
        # Get pricing metrics
        metrics = get_pricing_metrics(product_id, store_id)
        
        if not metrics:
            logger.warning(f"No pricing metrics found for product {product_id} at store {store_id}")
            # Use default metrics
            metrics = {
                "min_price": current_price * 0.8,
                "max_price": current_price * 1.2,
                "competitor_price": current_price * 0.95,
                "elasticity": -1.5,
                "margin_target": 0.3,
                "promotion_discount": 0.1
            }
        
        # Extract constraints
        min_price = metrics.get('min_price', current_price * 0.8)
        max_price = metrics.get('max_price', current_price * 1.2)
        competitor_price = metrics.get('competitor_price')
        elasticity = metrics.get('elasticity', -1.5)
        margin_target = metrics.get('margin_target', 0.3)
        
        # Get demand predictions at current price
        base_predictions = predict_demand(product_id, store_id, 30)
        base_demand = sum(p.get('demand', 0) for p in base_predictions)
        
        # Calculate estimated cost (assuming margin is price - cost / price)
        estimated_cost = current_price * (1 - margin_target)
        
        # Generate candidate prices
        # Start with a range of prices between min and max
        price_range = np.linspace(min_price, max_price, 10)
        
        # Add competitor-based prices
        if competitor_price is not None:
            # Add prices that are slightly above, equal to, and slightly below competitor
            competitor_prices = [
                competitor_price * 0.95,  # 5% below competitor
                competitor_price,         # match competitor
                competitor_price * 1.05   # 5% above competitor
            ]
            price_range = np.append(price_range, competitor_prices)
        
        # Add current price to the options
        price_range = np.append(price_range, current_price)
        
        # Remove duplicates and sort
        price_range = np.unique(price_range)
        
        # Evaluate each candidate price
        best_price = None
        best_profit = -float('inf')
        best_demand = 0
        price_evaluations = []
        
        for price in price_range:
            # Skip if outside constraints
            if price < min_price or price > max_price:
                continue
            
            # Calculate expected demand using elasticity
            if elasticity and current_price > 0:
                # Demand elasticity formula: % change in demand = elasticity * % change in price
                price_change_pct = (price - current_price) / current_price
                demand_change_pct = elasticity * price_change_pct
                expected_demand = base_demand * (1 + demand_change_pct)
            else:
                # If we don't have elasticity, assume linear relationship
                # As price increases, demand decreases proportionally
                if price > current_price:
                    factor = 1 - ((price - current_price) / current_price) * 0.5
                else:
                    factor = 1 + ((current_price - price) / current_price) * 0.3
                expected_demand = base_demand * factor
            
            # Ensure demand is not negative
            expected_demand = max(0, expected_demand)
            
            # Calculate expected profit
            profit_per_unit = price - estimated_cost
            expected_profit = profit_per_unit * expected_demand
            
            # Calculate margin
            margin = profit_per_unit / price if price > 0 else 0
            
            # Competitive position
            if competitor_price is not None:
                price_diff = price - competitor_price
                price_diff_pct = (price - competitor_price) / competitor_price * 100 if competitor_price > 0 else 0
            else:
                price_diff = None
                price_diff_pct = None
            
            # Store evaluation
            evaluation = {
                "price": round(price, 2),
                "expected_demand": round(expected_demand),
                "expected_profit": round(expected_profit, 2),
                "margin": round(margin, 2),
                "price_diff": round(price_diff, 2) if price_diff is not None else None,
                "price_diff_pct": round(price_diff_pct, 1) if price_diff_pct is not None else None
            }
            
            price_evaluations.append(evaluation)
            
            # Update best price if this one has higher profit
            if expected_profit > best_profit:
                best_profit = expected_profit
                best_price = price
                best_demand = expected_demand
        
        # If we didn't find a valid price, default to current price
        if best_price is None:
            best_price = current_price
            best_profit = (current_price - estimated_cost) * base_demand
            best_demand = base_demand
        
        # Construct result
        result = {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "optimal_price": round(best_price, 2),
            "estimated_cost": round(estimated_cost, 2),
            "expected_demand": round(best_demand),
            "expected_profit": round(best_profit, 2),
            "margin": round((best_price - estimated_cost) / best_price, 2) if best_price > 0 else 0,
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "competitor_price": round(competitor_price, 2) if competitor_price is not None else None,
            "price_elasticity": elasticity,
            "evaluations": price_evaluations
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating optimal price: {str(e)}")
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "error": f"Failed to calculate optimal price: {str(e)}"
        }

def get_pricing_recommendation(product_id: int, store_id: int, current_price: float) -> Dict[str, Any]:
    """
    Get a pricing recommendation for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current price of the product
        
    Returns:
        Dict with pricing recommendation
    """
    try:
        # Calculate optimal price
        optimal = calculate_optimal_price(product_id, store_id, current_price)
        
        # Check for errors
        if "error" in optimal:
            return optimal
        
        optimal_price = optimal.get('optimal_price', current_price)
        competitor_price = optimal.get('competitor_price')
        
        # Calculate price change
        price_diff = optimal_price - current_price
        price_change_pct = (optimal_price - current_price) / current_price * 100 if current_price > 0 else 0
        
        # Determine recommendation type
        if abs(price_change_pct) < 1:
            recommendation_type = "maintain"
            action = "Maintain current price"
        elif price_change_pct > 0:
            recommendation_type = "increase"
            action = "Increase price"
        else:
            recommendation_type = "decrease"
            action = "Decrease price"
        
        # Calculate expected impact
        expected_profit_current = (current_price - optimal.get('estimated_cost', 0)) * optimal.get('expected_demand', 0)
        expected_profit_optimal = optimal.get('expected_profit', 0)
        profit_impact = expected_profit_optimal - expected_profit_current
        profit_impact_pct = (profit_impact / expected_profit_current * 100) if expected_profit_current > 0 else 0
        
        # Generate explanation
        explanation = ""
        if recommendation_type == "maintain":
            explanation = f"The current price of ${current_price:.2f} is already optimal for this product."
        elif recommendation_type == "increase":
            explanation = f"Increasing the price to ${optimal_price:.2f} would optimize profit. "
            if competitor_price is not None:
                if optimal_price > competitor_price:
                    explanation += f"This is {((optimal_price - competitor_price) / competitor_price * 100):.1f}% above the competitor price of ${competitor_price:.2f}."
                else:
                    explanation += f"This is still {((competitor_price - optimal_price) / competitor_price * 100):.1f}% below the competitor price of ${competitor_price:.2f}."
        else:  # decrease
            explanation = f"Decreasing the price to ${optimal_price:.2f} would optimize profit. "
            if competitor_price is not None:
                if optimal_price > competitor_price:
                    explanation += f"This is {((optimal_price - competitor_price) / competitor_price * 100):.1f}% above the competitor price of ${competitor_price:.2f}."
                else:
                    explanation += f"This is {((competitor_price - optimal_price) / competitor_price * 100):.1f}% below the competitor price of ${competitor_price:.2f}."
        
        # Determine confidence
        if abs(price_change_pct) < 5:
            confidence = "high"  # Small change = high confidence
        elif abs(price_change_pct) < 15:
            confidence = "medium"
        else:
            confidence = "low"  # Large change = low confidence
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "recommended_price": optimal_price,
            "recommendation_type": recommendation_type,
            "action": action,
            "price_change": round(price_diff, 2),
            "price_change_pct": round(price_change_pct, 1),
            "expected_profit_impact": round(profit_impact, 2),
            "expected_profit_impact_pct": round(profit_impact_pct, 1),
            "explanation": explanation,
            "confidence": confidence,
            "competitor_price": competitor_price
        }
    
    except Exception as e:
        logger.error(f"Error getting pricing recommendation: {str(e)}")
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "error": f"Failed to get pricing recommendation: {str(e)}"
        }

def calculate_promotion_impact(product_id: int, store_id: int, current_price: float, discount_pct: float) -> Dict[str, Any]:
    """
    Calculate the impact of a price promotion on demand and profit.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_price: Current price of the product
        discount_pct: Discount percentage (0-1)
        
    Returns:
        Dict with promotion impact assessment
    """
    try:
        # Get pricing metrics
        metrics = get_pricing_metrics(product_id, store_id)
        
        if not metrics:
            logger.warning(f"No pricing metrics found for product {product_id} at store {store_id}")
            # Use default metrics
            metrics = {
                "min_price": current_price * 0.8,
                "max_price": current_price * 1.2,
                "competitor_price": current_price * 0.95,
                "elasticity": -1.5,
                "margin_target": 0.3,
                "promotion_discount": 0.1
            }
        
        # Extract relevant metrics
        elasticity = metrics.get('elasticity', -1.5)
        promotion_boost = metrics.get('promotion_boost', 1.5)  # Additional boost beyond elasticity
        margin_target = metrics.get('margin_target', 0.3)
        
        # Calculate promotional price
        promo_price = current_price * (1 - discount_pct)
        
        # Calculate estimated cost (assuming margin is price - cost / price)
        estimated_cost = current_price * (1 - margin_target)
        
        # Get demand predictions at current price
        base_predictions = predict_demand(product_id, store_id, 30)
        base_demand = sum(p.get('demand', 0) for p in base_predictions)
        
        # Calculate expected demand using elasticity
        if elasticity and current_price > 0:
            # Demand elasticity formula: % change in demand = elasticity * % change in price
            price_change_pct = -discount_pct  # Negative because price is decreasing
            demand_change_pct = elasticity * price_change_pct
            
            # Apply promotion boost (additional demand beyond elasticity)
            if promotion_boost > 1:
                demand_change_pct = demand_change_pct * promotion_boost
            
            expected_demand = base_demand * (1 + demand_change_pct)
        else:
            # If we don't have elasticity, assume promotion increases demand by 20-50%
            boost_factor = 1 + discount_pct * 5  # More discount = more boost
            expected_demand = base_demand * boost_factor
        
        # Ensure demand is not negative
        expected_demand = max(0, expected_demand)
        
        # Calculate financials
        base_profit = (current_price - estimated_cost) * base_demand
        promo_profit = (promo_price - estimated_cost) * expected_demand
        profit_impact = promo_profit - base_profit
        
        # Calculate cannialization rate (% of future sales brought forward)
        cannibalization_rate = 0.3  # Assume 30% of additional sales are borrowed from future
        
        # Adjusted profit impact considering cannibalization
        adjusted_demand_increase = expected_demand - base_demand
        cannibalized_demand = adjusted_demand_increase * cannibalization_rate
        future_lost_profit = cannibalized_demand * (current_price - estimated_cost)
        adjusted_profit_impact = profit_impact - future_lost_profit
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "promo_price": round(promo_price, 2),
            "discount_pct": round(discount_pct * 100, 1),
            "base_demand": round(base_demand),
            "expected_demand": round(expected_demand),
            "demand_increase_pct": round((expected_demand - base_demand) / base_demand * 100, 1) if base_demand > 0 else 0,
            "base_profit": round(base_profit, 2),
            "promo_profit": round(promo_profit, 2),
            "profit_impact": round(profit_impact, 2),
            "profit_impact_pct": round(profit_impact / base_profit * 100, 1) if base_profit > 0 else 0,
            "cannibalization_rate": cannibalization_rate,
            "adjusted_profit_impact": round(adjusted_profit_impact, 2),
            "is_profitable": adjusted_profit_impact > 0
        }
    
    except Exception as e:
        logger.error(f"Error calculating promotion impact: {str(e)}")
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_price": current_price,
            "discount_pct": discount_pct,
            "error": f"Failed to calculate promotion impact: {str(e)}"
        }