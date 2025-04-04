"""
Forecasting module for the AI Inventory Optimization System.

This module provides utilities for forecasting future demand based on
historical data, seasonality factors, and other business metrics.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.data_loader import get_demand_metrics

logger = logging.getLogger(__name__)

def load_forecast_model(product_id: int, store_id: int) -> Dict[str, Any]:
    """
    Load forecasting model for a specific product and store.
    
    In a production system, this would load a trained machine learning model from storage.
    For this demo, we'll use a simplified approach based on metrics from CSV data.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        
    Returns:
        Dictionary with model parameters
    """
    try:
        # Get demand metrics from CSV data
        metrics = get_demand_metrics(product_id, store_id)
        
        if not metrics:
            logger.warning(f"No demand metrics found for product {product_id} at store {store_id}")
            # Return default model parameters
            return {
                "avg_daily_sales": 10,
                "trend": 0.0,
                "seasonality_factor": 1.0,
                "promotion_effect": 0.0,
                "price_elasticity": -1.5,
                "competitor_impact": 0.0
            }
        
        # Extract model parameters from metrics
        model = {
            "avg_daily_sales": metrics.get("avg_daily_sales", 10),
            "trend": metrics.get("sales_trend", 0.0),
            "seasonality_factor": metrics.get("seasonality_factor", 1.0),
            "promotion_effect": metrics.get("promotion_effect", 0.0),
            "price_elasticity": metrics.get("price_elasticity", -1.5),
            "competitor_impact": metrics.get("competitor_impact", 0.0)
        }
        
        return model
    except Exception as e:
        logger.error(f"Error loading forecast model: {str(e)}")
        # Return default model parameters
        return {
            "avg_daily_sales": 10,
            "trend": 0.0,
            "seasonality_factor": 1.0,
            "promotion_effect": 0.0,
            "price_elasticity": -1.5,
            "competitor_impact": 0.0
        }

def predict_demand(product_id: int, store_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """
    Predict demand for a product at a specific store for the next N days.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days to forecast
        
    Returns:
        List of dictionaries with date and predicted demand value
    """
    try:
        # Load model parameters
        model = load_forecast_model(product_id, store_id)
        
        # Generate predictions
        predictions = []
        base_demand = model["avg_daily_sales"]
        trend = model["trend"]
        seasonality_factor = model["seasonality_factor"]
        
        today = datetime.now()
        
        for i in range(days):
            day_offset = i + 1
            forecast_date = today + timedelta(days=day_offset)
            
            # Apply trend (percentage change per day)
            trend_factor = 1.0 + (trend * day_offset / 100)
            
            # Apply day-of-week seasonality (simplified: weekends have higher demand)
            day_of_week = forecast_date.weekday()
            day_factor = 1.2 if day_of_week >= 5 else 1.0  # Higher demand on weekends
            
            # Apply month seasonality (simplified: Q4 has higher demand)
            month = forecast_date.month
            month_factor = 1.3 if month >= 10 else 1.0  # Higher demand in Q4
            
            # Apply a slight randomness to make the forecast more realistic
            noise = np.random.normal(1.0, 0.05)  # Random factor with mean 1.0 and std 0.05
            
            # Calculate demand
            demand = base_demand * trend_factor * day_factor * month_factor * seasonality_factor * noise
            
            # Ensure demand is positive
            demand = max(demand, 0)
            
            # Format date
            date_str = forecast_date.strftime("%Y-%m-%d")
            
            predictions.append({
                "date": date_str,
                "demand": round(demand, 1)
            })
        
        return predictions
    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
        # Return basic predictions on error
        return _generate_fallback_predictions(days)

def _generate_fallback_predictions(days: int) -> List[Dict[str, Any]]:
    """
    Generate fallback predictions if the forecasting model fails.
    
    Args:
        days: Number of days to forecast
        
    Returns:
        List of dictionaries with date and predicted demand value
    """
    predictions = []
    today = datetime.now()
    
    for i in range(days):
        day_offset = i + 1
        forecast_date = today + timedelta(days=day_offset)
        date_str = forecast_date.strftime("%Y-%m-%d")
        
        # Generate a random demand between 5 and 15
        demand = np.random.uniform(5, 15)
        
        predictions.append({
            "date": date_str,
            "demand": round(demand, 1)
        })
    
    return predictions