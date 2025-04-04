import os
import logging
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)

def load_forecast_model():
    """
    Load the Prophet forecasting model from a pickle file.
    If the model file doesn't exist, return None.
    
    Returns:
        Prophet model object or None if file not found
    """
    model_path = os.path.join("utils", "demand_model.pkl")
    
    try:
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            logger.info("Prophet model loaded successfully")
            return model
        else:
            logger.warning(f"Model file not found at {model_path}")
            return None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

def predict_demand(model, product_id, store_id, days=30):
    """
    Generate demand predictions using the Prophet model.
    If the model is not available, use simulated data.
    
    Args:
        model: Prophet model object
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days to forecast
        
    Returns:
        List of dictionaries with date and predicted demand value
    """
    try:
        if model is None:
            logger.warning("No Prophet model available, using simulated data")
            return _generate_simulated_predictions(product_id, store_id, days)
        
        # In a real system, we would prepare the forecast dataframe
        # with historical data specific to this product/store
        
        # For this demo, we'll create a future dataframe for Prophet
        future_dates = pd.DataFrame({
            'ds': [datetime.now() + timedelta(days=i) for i in range(days)]
        })
        
        # Make predictions
        forecast = model.predict(future_dates)
        
        # Extract relevant columns and convert to list of dictionaries
        predictions = []
        for _, row in forecast.iterrows():
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'value': round(max(0, row['yhat']), 2)  # Ensure non-negative values
            })
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error in demand prediction: {str(e)}")
        return _generate_simulated_predictions(product_id, store_id, days)

def _generate_simulated_predictions(product_id, store_id, days):
    """
    Generate simulated demand predictions when the Prophet model is unavailable.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days to forecast
        
    Returns:
        List of dictionaries with date and simulated demand value
    """
    # Create a seed based on product and store IDs for consistent randomness
    np.random.seed(product_id * 100 + store_id)
    
    # Generate baseline demand (different for each product/store combination)
    baseline = 10 + (product_id % 5) * 5 + (store_id % 3) * 3
    
    # Create date range
    start_date = datetime.now()
    predictions = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Add weekly seasonality (higher on weekends)
        day_of_week = current_date.weekday()
        seasonal_factor = 1.3 if day_of_week >= 5 else 1.0
        
        # Add slight trend
        trend = 1.0 + (i * 0.005)
        
        # Add randomness
        noise = np.random.normal(1.0, 0.15)
        
        # Calculate demand
        demand = baseline * seasonal_factor * trend * noise
        
        predictions.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'value': round(max(0, demand), 2)  # Ensure non-negative values
        })
    
    return predictions
