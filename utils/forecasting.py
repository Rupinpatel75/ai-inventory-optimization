"""
Forecasting utility for the AI Inventory Optimization System.

This module provides demand forecasting functionality based on
historical data, seasonality detection, and trend analysis.
"""

import logging
import math
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def predict_demand(product_id, store_id, days=30):
    """
    Predict demand for a product at a store for a given number of days.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days to forecast
        
    Returns:
        Dictionary with prediction details
    """
    try:
        # In a real implementation, this would use trained ML models
        # For now, we'll use simulated values based on product_id and store_id
        
        # Generate a seed based on product_id and store_id for consistent results
        random.seed(product_id * 1000 + store_id)
        
        # Base demand (daily units)
        base_demand = random.uniform(5, 50)
        
        # Randomize parameters for this product/store
        trend = random.uniform(-0.01, 0.02)  # Daily trend factor
        seasonality = random.uniform(0.1, 0.4)  # Seasonality amplitude
        noise_level = random.uniform(0.05, 0.2)  # Demand noise
        
        # Generate daily predictions
        predictions = []
        cumulative_demand = 0
        
        for day in range(days):
            # Calculate trend component
            trend_component = base_demand * (1 + trend * day)
            
            # Calculate seasonality component (weekly pattern)
            # Higher demand on weekends, lower on weekdays
            day_of_week = day % 7
            if day_of_week >= 5:  # Weekend
                seasonality_component = trend_component * seasonality
            else:  # Weekday
                seasonality_component = trend_component * (-seasonality * 0.5)
            
            # Add noise
            noise = random.normalvariate(0, noise_level * base_demand)
            
            # Calculate total demand for the day
            day_demand = max(0, trend_component + seasonality_component + noise)
            
            # Add to daily predictions
            predictions.append({
                "day": day + 1,
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "demand": round(day_demand, 1)
            })
            
            # Add to cumulative demand
            cumulative_demand += day_demand
        
        # Calculate summary statistics
        total_demand = cumulative_demand
        avg_daily_demand = total_demand / days
        
        # Calculate standard deviation
        squared_diffs = [(pred["demand"] - avg_daily_demand) ** 2 for pred in predictions]
        variance = sum(squared_diffs) / days
        std_dev = math.sqrt(variance)
        
        # Save prediction to database (in a real implementation)
        # Here we would log the prediction to the PredictionLog model
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "days": days,
            "total_demand": round(total_demand),
            "avg_daily_demand": round(avg_daily_demand, 2),
            "std_dev": round(std_dev, 2),
            "coefficient_of_variation": round(std_dev / avg_daily_demand, 2) if avg_daily_demand > 0 else 0,
            "daily_predictions": predictions
        }
    
    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
        return {"error": f"Failed to predict demand: {str(e)}"}

def get_historical_sales(product_id, store_id, days=90):
    """
    Get historical sales data for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days of historical data to retrieve
        
    Returns:
        Dictionary with historical sales data
    """
    try:
        # In a real implementation, this would query a database
        # For now, we'll generate synthetic historical data
        
        # Generate a seed based on product_id and store_id for consistent results
        random.seed(product_id * 2000 + store_id)
        
        # Base demand (daily units)
        base_demand = random.uniform(5, 50)
        
        # Parameters
        trend = random.uniform(-0.005, 0.01)  # Daily trend factor
        seasonality = random.uniform(0.1, 0.3)  # Seasonality amplitude
        noise_level = random.uniform(0.1, 0.25)  # Demand noise
        
        # Generate daily historical data
        historical_data = []
        total_sales = 0
        
        for day in range(days, 0, -1):
            # Calculate days ago
            days_ago = day
            date = datetime.now() - timedelta(days=days_ago)
            
            # Calculate trend component
            trend_component = base_demand * (1 + trend * (days - days_ago))
            
            # Calculate seasonality component (weekly pattern)
            day_of_week = date.weekday()
            if day_of_week >= 5:  # Weekend
                seasonality_component = trend_component * seasonality
            else:  # Weekday
                seasonality_component = trend_component * (-seasonality * 0.5)
            
            # Add noise
            noise = random.normalvariate(0, noise_level * base_demand)
            
            # Calculate total sales for the day
            day_sales = max(0, trend_component + seasonality_component + noise)
            
            # Add to historical data
            historical_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "sales": round(day_sales, 1),
                "day_of_week": day_of_week
            })
            
            # Add to total sales
            total_sales += day_sales
        
        # Calculate summary statistics
        avg_daily_sales = total_sales / days
        
        # Calculate standard deviation
        squared_diffs = [(day["sales"] - avg_daily_sales) ** 2 for day in historical_data]
        variance = sum(squared_diffs) / days
        std_dev = math.sqrt(variance)
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "days": days,
            "total_sales": round(total_sales),
            "avg_daily_sales": round(avg_daily_sales, 2),
            "std_dev": round(std_dev, 2),
            "coefficient_of_variation": round(std_dev / avg_daily_sales, 2) if avg_daily_sales > 0 else 0,
            "daily_sales": historical_data
        }
    
    except Exception as e:
        logger.error(f"Error getting historical sales: {str(e)}")
        return {"error": f"Failed to get historical sales: {str(e)}"}

def analyze_seasonality(product_id, store_id, days=365):
    """
    Analyze seasonality patterns for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days of historical data to analyze
        
    Returns:
        Dictionary with seasonality analysis
    """
    try:
        # Get historical sales data
        historical = get_historical_sales(product_id, store_id, days)
        
        if "error" in historical:
            return historical
        
        daily_sales = historical.get("daily_sales", [])
        
        # Analyze weekly patterns
        day_of_week_sales = [0] * 7
        day_of_week_counts = [0] * 7
        
        for day in daily_sales:
            dow = day.get("day_of_week", 0)
            sales = day.get("sales", 0)
            
            day_of_week_sales[dow] += sales
            day_of_week_counts[dow] += 1
        
        # Calculate average sales by day of week
        weekly_pattern = []
        overall_avg = historical.get("avg_daily_sales", 1)
        
        for dow in range(7):
            if day_of_week_counts[dow] > 0:
                avg_sales = day_of_week_sales[dow] / day_of_week_counts[dow]
                relative_to_avg = avg_sales / overall_avg if overall_avg > 0 else 1
                
                weekly_pattern.append({
                    "day_of_week": dow,
                    "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dow],
                    "avg_sales": round(avg_sales, 2),
                    "relative_to_avg": round(relative_to_avg, 2),
                    "sample_size": day_of_week_counts[dow]
                })
        
        # Analyze monthly patterns (simplified)
        monthly_pattern = []
        for month in range(1, 13):
            # In a real implementation, this would analyze actual monthly data
            # For demo purposes, we'll create a simulated pattern
            random.seed(product_id * 3000 + store_id + month)
            
            monthly_factor = random.uniform(0.7, 1.3)
            
            monthly_pattern.append({
                "month": month,
                "month_name": ["January", "February", "March", "April", "May", "June", 
                             "July", "August", "September", "October", "November", "December"][month - 1],
                "relative_to_avg": round(monthly_factor, 2)
            })
        
        # Detect peaks and troughs
        weekly_factors = [wp["relative_to_avg"] for wp in weekly_pattern]
        monthly_factors = [mp["relative_to_avg"] for mp in monthly_pattern]
        
        peak_day = weekly_pattern[weekly_factors.index(max(weekly_factors))]["day_name"]
        trough_day = weekly_pattern[weekly_factors.index(min(weekly_factors))]["day_name"]
        
        peak_month = monthly_pattern[monthly_factors.index(max(monthly_factors))]["month_name"]
        trough_month = monthly_pattern[monthly_factors.index(min(monthly_factors))]["month_name"]
        
        seasonality_strength = max(monthly_factors) / min(monthly_factors) if min(monthly_factors) > 0 else 1
        
        return {
            "product_id": product_id,
            "store_id": store_id,
            "weekly_pattern": weekly_pattern,
            "monthly_pattern": monthly_pattern,
            "peak_day": peak_day,
            "trough_day": trough_day,
            "peak_month": peak_month,
            "trough_month": trough_month,
            "seasonality_strength": round(seasonality_strength, 2),
            "has_strong_seasonality": seasonality_strength > 1.5
        }
    
    except Exception as e:
        logger.error(f"Error analyzing seasonality: {str(e)}")
        return {"error": f"Failed to analyze seasonality: {str(e)}"}

def load_forecast_model(model_name):
    """
    Load a forecast model (placeholder for a real implementation).
    
    Args:
        model_name: Name of the forecast model to load
        
    Returns:
        Dictionary with model information
    """
    # In a real implementation, this would load trained ML models
    # For now, we'll just return a message
    logger.info(f"Placeholder for loading forecast model: {model_name}")
    
    return {
        "model_name": model_name,
        "type": "time_series",
        "is_loaded": True,
        "accuracy": 0.85
    }