"""
Inventory optimization utility for the AI Inventory Optimization System.

This module provides functions for optimizing inventory levels,
calculating reorder points, and minimizing inventory costs.
"""

import logging
import math
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from utils.forecasting import predict_demand

logger = logging.getLogger(__name__)

def calculate_reorder_point(product_id, store_id, lead_time_days=3, service_level=0.95):
    """
    Calculate the optimal reorder point for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        lead_time_days: Supplier lead time in days
        service_level: Desired service level (0-1)
        
    Returns:
        Dictionary with reorder point information
    """
    try:
        # Get demand prediction for lead time period
        demand_data = predict_demand(product_id, store_id, days=lead_time_days)
        
        if "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract key values
        avg_daily_demand = demand_data.get("avg_daily_demand", 10)
        std_dev = demand_data.get("std_dev", 2)
        
        # Calculate lead time demand
        lead_time_demand = avg_daily_demand * lead_time_days
        
        # Calculate lead time demand standard deviation
        # Assuming independence of daily demand, we use the square root of time rule
        lead_time_std_dev = std_dev * math.sqrt(lead_time_days)
        
        # Calculate safety factor (z-score) based on service level
        # Approximation of the inverse of the standard normal CDF
        # More accurate methods would use statistical libraries
        if service_level >= 0.999:
            safety_factor = 3.09  # ~99.9%
        elif service_level >= 0.99:
            safety_factor = 2.33  # ~99%
        elif service_level >= 0.975:
            safety_factor = 1.96  # ~97.5%
        elif service_level >= 0.95:
            safety_factor = 1.65  # ~95%
        elif service_level >= 0.9:
            safety_factor = 1.28  # ~90%
        elif service_level >= 0.8:
            safety_factor = 0.84  # ~80%
        elif service_level >= 0.7:
            safety_factor = 0.52  # ~70%
        else:
            safety_factor = 0.0  # ~50%
        
        # Calculate safety stock
        safety_stock = safety_factor * lead_time_std_dev
        
        # Calculate reorder point (ROP)
        reorder_point = lead_time_demand + safety_stock
        
        # Round up to nearest integer
        reorder_point_rounded = math.ceil(reorder_point)
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "avg_daily_demand": round(avg_daily_demand, 2),
            "lead_time_days": lead_time_days,
            "lead_time_demand": round(lead_time_demand, 2),
            "demand_std_dev": round(std_dev, 2),
            "lead_time_std_dev": round(lead_time_std_dev, 2),
            "service_level": service_level,
            "safety_factor": round(safety_factor, 2),
            "safety_stock": round(safety_stock, 2),
            "reorder_point": reorder_point_rounded,
            "stockout_probability": round((1 - service_level) * 100, 2)
        }
    
    except Exception as e:
        logger.error(f"Error calculating reorder point: {str(e)}")
        return {"error": f"Failed to calculate reorder point: {str(e)}"}

def calculate_economic_order_quantity(product_id, store_id, holding_cost_pct=0.25, order_cost=25.0, days=365):
    """
    Calculate the economic order quantity (EOQ) for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        holding_cost_pct: Annual holding cost as a percentage of item value
        order_cost: Fixed cost per order
        days: Number of days to consider for annual demand
        
    Returns:
        Dictionary with EOQ information
    """
    try:
        # Get annual demand by extrapolating from a shorter forecast
        forecast_days = min(days, 90)  # Use at most 90 days for forecast
        demand_data = predict_demand(product_id, store_id, days=forecast_days)
        
        if "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract average daily demand and calculate annual demand
        avg_daily_demand = demand_data.get("avg_daily_demand", 10)
        annual_demand = avg_daily_demand * days
        
        # Assume unit cost is 60% of the product's base price
        # In a real implementation, this would come from the database
        unit_cost = 100  # Placeholder, would be replaced with actual cost
        
        # Calculate holding cost per unit per year
        holding_cost = unit_cost * holding_cost_pct
        
        # Calculate EOQ using the standard formula
        # EOQ = sqrt(2 * D * S / H)
        # Where:
        # D = Annual demand
        # S = Order cost
        # H = Holding cost per unit per year
        
        if holding_cost > 0:
            eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
            eoq_rounded = math.ceil(eoq)
            
            # Calculate number of orders per year
            orders_per_year = annual_demand / eoq_rounded
            
            # Calculate total annual cost
            ordering_cost = order_cost * orders_per_year
            holding_cost_total = holding_cost * (eoq_rounded / 2)  # Average inventory
            total_cost = ordering_cost + holding_cost_total
            
            # Calculate days between orders
            days_between_orders = days / orders_per_year
            
            return {
                "product_id": product_id,
                "store_id": store_id,
                "annual_demand": round(annual_demand),
                "unit_cost": round(unit_cost, 2),
                "holding_cost_pct": holding_cost_pct,
                "holding_cost_per_unit": round(holding_cost, 2),
                "order_cost": order_cost,
                "eoq": eoq_rounded,
                "orders_per_year": round(orders_per_year, 1),
                "days_between_orders": round(days_between_orders, 1),
                "average_inventory": round(eoq_rounded / 2),
                "annual_ordering_cost": round(ordering_cost, 2),
                "annual_holding_cost": round(holding_cost_total, 2),
                "total_annual_cost": round(total_cost, 2)
            }
        else:
            return {"error": "Holding cost must be greater than zero"}
    
    except Exception as e:
        logger.error(f"Error calculating EOQ: {str(e)}")
        return {"error": f"Failed to calculate EOQ: {str(e)}"}

def calculate_stockout_risk(product_id, store_id, current_stock, days=30):
    """
    Calculate the risk of stockout for a product at a store within a time period.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_stock: Current stock level
        days: Number of days to consider
        
    Returns:
        Dictionary with stockout risk information
    """
    try:
        # Get demand prediction
        demand_data = predict_demand(product_id, store_id, days=days)
        
        if "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract forecasted demand and variability
        total_demand = demand_data.get("total_demand", 0)
        avg_daily_demand = demand_data.get("avg_daily_demand", 0)
        std_dev = demand_data.get("std_dev", 0)
        
        # Calculate expected days until stockout
        if avg_daily_demand > 0:
            days_until_stockout = current_stock / avg_daily_demand
        else:
            days_until_stockout = float('inf')  # No demand, no stockout
        
        # Calculate probability of stockout within the period
        if std_dev > 0:
            # Using a simplified normal approximation
            z_score = (current_stock - total_demand) / (std_dev * math.sqrt(days))
            
            # Simple approximation of the normal CDF
            # In a real implementation, use statistical libraries
            if z_score < -3.0:
                stockout_probability = 0.999
            elif z_score < -2.0:
                stockout_probability = 0.975
            elif z_score < -1.0:
                stockout_probability = 0.84
            elif z_score < 0.0:
                stockout_probability = 0.5
            elif z_score < 1.0:
                stockout_probability = 0.16
            elif z_score < 2.0:
                stockout_probability = 0.025
            else:
                stockout_probability = 0.001
        else:
            # If no variability, it's deterministic
            stockout_probability = 1.0 if current_stock < total_demand else 0.0
        
        # Calculate expected stockout date
        if days_until_stockout < float('inf'):
            stockout_date = (datetime.now() + timedelta(days=days_until_stockout)).strftime("%Y-%m-%d")
        else:
            stockout_date = None
        
        # Determine risk level
        if stockout_probability > 0.7:
            risk_level = "high"
        elif stockout_probability > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_stock": current_stock,
            "forecasted_demand": round(total_demand),
            "avg_daily_demand": round(avg_daily_demand, 2),
            "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout < float('inf') else None,
            "stockout_date": stockout_date,
            "stockout_probability": round(stockout_probability * 100, 1),
            "risk_level": risk_level,
            "expected_remaining_stock": round(max(0, current_stock - total_demand)),
            "days": days
        }
    
    except Exception as e:
        logger.error(f"Error calculating stockout risk: {str(e)}")
        return {"error": f"Failed to calculate stockout risk: {str(e)}"}

def optimize_inventory_allocation(product_id, store_ids, total_stock):
    """
    Optimize the allocation of limited inventory across multiple stores.
    
    Args:
        product_id: ID of the product
        store_ids: List of store IDs
        total_stock: Total stock available for allocation
        
    Returns:
        Dictionary with allocation results
    """
    try:
        # Get demand predictions for each store
        store_demand = []
        
        for store_id in store_ids:
            demand_data = predict_demand(product_id, store_id, days=30)
            if "error" in demand_data:
                continue
            
            store_demand.append({
                "store_id": store_id,
                "demand": demand_data.get("total_demand", 0),
                "std_dev": demand_data.get("std_dev", 0) * math.sqrt(30)  # Scale daily std to monthly
            })
        
        if not store_demand:
            return {"error": "Could not retrieve demand data for any store"}
        
        # If total demand is less than available stock, allocate based on demand
        total_demand = sum(sd["demand"] for sd in store_demand)
        
        if total_demand <= total_stock:
            # Simple allocation based on demand
            allocation = []
            remaining_stock = total_stock
            
            for sd in store_demand:
                store_allocation = math.ceil(sd["demand"])
                remaining_stock -= store_allocation
                
                allocation.append({
                    "store_id": sd["store_id"],
                    "allocation": store_allocation,
                    "demand": round(sd["demand"]),
                    "coverage": round(store_allocation / sd["demand"] * 100 if sd["demand"] > 0 else 100)
                })
            
            # Distribute any remaining stock proportionally
            if remaining_stock > 0 and len(store_demand) > 0:
                for i in range(remaining_stock):
                    allocation[i % len(allocation)]["allocation"] += 1
                    allocation[i % len(allocation)]["coverage"] = round(
                        allocation[i % len(allocation)]["allocation"] / allocation[i % len(allocation)]["demand"] * 100
                        if allocation[i % len(allocation)]["demand"] > 0 else 100
                    )
        else:
            # Allocate proportionally to demand
            allocation = []
            remaining_stock = total_stock
            
            for sd in store_demand:
                proportion = sd["demand"] / total_demand
                store_allocation = math.floor(total_stock * proportion)
                remaining_stock -= store_allocation
                
                allocation.append({
                    "store_id": sd["store_id"],
                    "allocation": store_allocation,
                    "demand": round(sd["demand"]),
                    "coverage": round(store_allocation / sd["demand"] * 100 if sd["demand"] > 0 else 100)
                })
            
            # Distribute any remaining stock to stores with lowest coverage
            allocation.sort(key=lambda x: x["coverage"])
            
            for i in range(remaining_stock):
                allocation[i % len(allocation)]["allocation"] += 1
                allocation[i % len(allocation)]["coverage"] = round(
                    allocation[i % len(allocation)]["allocation"] / allocation[i % len(allocation)]["demand"] * 100
                    if allocation[i % len(allocation)]["demand"] > 0 else 100
                )
        
        # Sort by store_id for consistency
        allocation.sort(key=lambda x: x["store_id"])
        
        return {
            "product_id": product_id,
            "total_stock": total_stock,
            "total_demand": round(total_demand),
            "coverage_pct": round(total_stock / total_demand * 100 if total_demand > 0 else 100),
            "allocation": allocation,
            "allocation_strategy": "demand_proportional" if total_demand > total_stock else "demand_based"
        }
    
    except Exception as e:
        logger.error(f"Error optimizing inventory allocation: {str(e)}")
        return {"error": f"Failed to optimize inventory allocation: {str(e)}"}

def analyze_inventory_turnover(product_id, store_id, current_stock, days=90):
    """
    Analyze inventory turnover ratio and related metrics.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        current_stock: Current stock level
        days: Number of days to analyze
        
    Returns:
        Dictionary with inventory turnover analysis
    """
    try:
        # Get demand prediction
        demand_data = predict_demand(product_id, store_id, days=days)
        
        if "error" in demand_data:
            return {"error": demand_data["error"]}
        
        # Extract forecasted demand
        forecasted_demand = demand_data.get("total_demand", 0)
        avg_daily_demand = demand_data.get("avg_daily_demand", 0)
        
        # Calculate inventory turnover ratio
        # Turnover = Annual COGS / Average Inventory
        # We'll use demand as a proxy for COGS
        annual_demand = avg_daily_demand * 365
        
        if current_stock > 0:
            # Assuming current stock is representative of average inventory
            turnover_ratio = annual_demand / current_stock
            days_of_supply = current_stock / avg_daily_demand if avg_daily_demand > 0 else float('inf')
        else:
            turnover_ratio = float('inf')
            days_of_supply = 0
        
        # Determine turnover rating
        if turnover_ratio > 12:  # More than monthly turnover
            turnover_rating = "excellent"
        elif turnover_ratio > 6:  # More than bi-monthly turnover
            turnover_rating = "good"
        elif turnover_ratio > 3:  # More than quarterly turnover
            turnover_rating = "average"
        elif turnover_ratio > 0:
            turnover_rating = "poor"
        else:
            turnover_rating = "unknown"
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "current_stock": current_stock,
            "forecasted_demand_period": round(forecasted_demand),
            "avg_daily_demand": round(avg_daily_demand, 2),
            "annual_demand_estimate": round(annual_demand),
            "inventory_turnover_ratio": round(turnover_ratio, 2) if turnover_ratio < float('inf') else None,
            "days_of_supply": round(days_of_supply, 1) if days_of_supply < float('inf') else None,
            "turnover_rating": turnover_rating,
            "analysis_period_days": days
        }
    
    except Exception as e:
        logger.error(f"Error analyzing inventory turnover: {str(e)}")
        return {"error": f"Failed to analyze inventory turnover: {str(e)}"}