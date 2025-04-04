"""
Inventory optimization utility for the AI Inventory Optimization System.

This module provides functions for optimizing inventory levels
based on demand forecasts, lead times, and other inventory parameters.
"""

import logging
import math
import random
import pandas as pd
import numpy as np
from utils.forecasting import predict_demand

logger = logging.getLogger(__name__)

def calculate_optimal_inventory(product_id, store_id, lead_time_days=7, service_level=0.95, holding_cost_pct=0.25):
    """
    Calculate optimal inventory levels using the Economic Order Quantity (EOQ) model.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        lead_time_days: Lead time for replenishment in days
        service_level: Desired service level (probability of not stocking out)
        holding_cost_pct: Inventory holding cost as a percentage of item value
        
    Returns:
        Dictionary with optimal inventory parameters
    """
    try:
        # In a real implementation, these would be retrieved from the database
        # For now, we'll use simulated values
        
        # Get demand forecast
        demand_data = predict_demand(product_id, store_id, days=30)
        if isinstance(demand_data, dict) and "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract relevant values
        daily_demand = demand_data.get("avg_daily_demand", 10)
        demand_stddev = demand_data.get("std_dev", 3)
        
        # Simulate ordering cost and item value
        ordering_cost = 50  # Fixed cost to place an order
        item_value = 100    # Value of each item
        
        # Calculate EOQ (Economic Order Quantity)
        annual_demand = daily_demand * 365
        holding_cost = item_value * holding_cost_pct
        
        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        eoq = round(eoq)
        
        # Calculate reorder point with safety stock
        lead_time_demand = daily_demand * lead_time_days
        safety_stock = demand_stddev * math.sqrt(lead_time_days) * 1.645  # Z-score for 95% service level
        reorder_point = round(lead_time_demand + safety_stock)
        
        # Calculate optimal parameters
        order_frequency = annual_demand / eoq if eoq > 0 else 0
        order_frequency_days = 365 / order_frequency if order_frequency > 0 else 0
        
        # Calculate total costs
        annual_ordering_cost = (annual_demand / eoq) * ordering_cost if eoq > 0 else 0
        annual_holding_cost = (eoq / 2) * holding_cost
        total_cost = annual_ordering_cost + annual_holding_cost
        
        return {
            "economic_order_quantity": eoq,
            "reorder_point": reorder_point,
            "safety_stock": round(safety_stock),
            "lead_time_days": lead_time_days,
            "order_frequency_per_year": round(order_frequency, 1),
            "order_frequency_days": round(order_frequency_days, 1),
            "annual_ordering_cost": round(annual_ordering_cost, 2),
            "annual_holding_cost": round(annual_holding_cost, 2),
            "total_annual_cost": round(total_cost, 2),
            "service_level": service_level * 100,
            "avg_daily_demand": daily_demand,
            "demand_stddev": demand_stddev
        }
    
    except Exception as e:
        logger.error(f"Error calculating optimal inventory: {str(e)}")
        return {"error": f"Failed to calculate optimal inventory: {str(e)}"}

def get_reorder_recommendation(current_stock, product_id, store_id, lead_time_days=7):
    """
    Get a recommendation on whether to reorder a product.
    
    Args:
        current_stock: Current inventory level
        product_id: ID of the product
        store_id: ID of the store
        lead_time_days: Lead time for replenishment in days
        
    Returns:
        Dictionary with reorder recommendation details
    """
    try:
        # Get optimal inventory levels
        optimal = calculate_optimal_inventory(product_id, store_id, lead_time_days)
        
        if "error" in optimal:
            return optimal
        
        # Extract relevant values
        reorder_point = optimal["reorder_point"]
        eoq = optimal["economic_order_quantity"]
        avg_daily_demand = optimal["avg_daily_demand"]
        
        # Calculate days of stock remaining
        days_remaining = current_stock / avg_daily_demand if avg_daily_demand > 0 else 30
        
        # Determine if reorder is needed
        should_reorder = current_stock <= reorder_point
        
        # Calculate suggested order quantity
        suggested_order = eoq if should_reorder else 0
        
        # Determine urgency level
        if days_remaining < lead_time_days:
            urgency = "High"
        elif days_remaining < lead_time_days * 1.5:
            urgency = "Medium"
        else:
            urgency = "Low"
        
        # Predict total demand over next 30 days
        predicted_demand_30d = avg_daily_demand * 30
        
        return {
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "should_reorder": should_reorder,
            "suggested_order": suggested_order,
            "days_remaining": round(days_remaining, 1),
            "lead_time_days": lead_time_days,
            "urgency": urgency,
            "predicted_demand_30d": round(predicted_demand_30d)
        }
    
    except Exception as e:
        logger.error(f"Error getting reorder recommendation: {str(e)}")
        return {"error": f"Failed to get reorder recommendation: {str(e)}"}

def calculate_stockout_risk(current_stock, product_id, store_id, forecast_days=30):
    """
    Calculate the risk of stocking out for a product.
    
    Args:
        current_stock: Current inventory level
        product_id: ID of the product
        store_id: ID of the store
        forecast_days: Number of days to forecast
        
    Returns:
        Dictionary with stockout risk assessment
    """
    try:
        # Get demand forecast
        demand_data = predict_demand(product_id, store_id, days=forecast_days)
        
        if isinstance(demand_data, dict) and "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract relevant values
        avg_daily_demand = demand_data.get("avg_daily_demand", 10)
        demand_stddev = demand_data.get("std_dev", 3)
        
        # Calculate days until stockout (simple average model)
        days_until_stockout = current_stock / avg_daily_demand if avg_daily_demand > 0 else forecast_days
        days_until_stockout = min(days_until_stockout, forecast_days)
        
        # Calculate probability of stockout within forecast period
        # Using simplified model: probability that demand exceeds current stock
        total_demand_mean = avg_daily_demand * forecast_days
        total_demand_stddev = demand_stddev * math.sqrt(forecast_days)
        
        if total_demand_stddev > 0:
            z_score = (current_stock - total_demand_mean) / total_demand_stddev
            # Approximation of the standard normal CDF
            stockout_probability = 0.5 * (1 - math.erf(z_score / math.sqrt(2)))
        else:
            stockout_probability = 0.5
        
        # Determine risk level
        if stockout_probability > 0.75:
            risk_level = "High"
        elif stockout_probability > 0.25:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "days_until_stockout": round(days_until_stockout, 1),
            "stockout_probability": round(stockout_probability, 2),
            "forecast_days": forecast_days,
            "risk_level": risk_level,
            "avg_daily_demand": avg_daily_demand,
            "demand_stddev": demand_stddev
        }
    
    except Exception as e:
        logger.error(f"Error calculating stockout risk: {str(e)}")
        return {"error": f"Failed to calculate stockout risk: {str(e)}"}

def optimize_inventory_order(inventory_data, demand_forecast, lead_time_days=7, service_level=0.95):
    """
    Optimize inventory order quantities across multiple products and stores.
    
    Args:
        inventory_data: DataFrame with current inventory levels
        demand_forecast: DataFrame with demand forecast
        lead_time_days: Lead time for replenishment in days
        service_level: Desired service level
        
    Returns:
        DataFrame with optimized order quantities
    """
    try:
        # In a real implementation, this would use mathematical optimization
        # to determine the best allocation of limited resources
        
        # For simplicity, we'll just apply individual product optimization
        results = []
        
        for _, row in inventory_data.iterrows():
            product_id = row.get('product_id')
            store_id = row.get('store_id')
            current_stock = row.get('quantity', 0)
            
            # Get reorder recommendation
            recommendation = get_reorder_recommendation(
                current_stock, product_id, store_id, lead_time_days
            )
            
            if "error" not in recommendation:
                results.append({
                    'product_id': product_id,
                    'store_id': store_id,
                    'current_stock': current_stock,
                    'should_reorder': recommendation.get('should_reorder', False),
                    'order_quantity': recommendation.get('suggested_order', 0),
                    'days_remaining': recommendation.get('days_remaining', 0),
                    'urgency': recommendation.get('urgency', 'Low')
                })
        
        return pd.DataFrame(results) if results else None
    
    except Exception as e:
        logger.error(f"Error optimizing inventory orders: {str(e)}")
        return None