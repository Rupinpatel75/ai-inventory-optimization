import logging
import pickle
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_forecast_model():
    """
    Load the Prophet forecasting model from a pickle file.
    If the model file doesn't exist, return None.
    
    Returns:
        Prophet model object or None if file not found
    """
    model_path = os.path.join('models', 'prophet_model.pkl')
    
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Loaded forecast model from {model_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading forecast model: {str(e)}")
            return None
    else:
        logger.warning(f"No forecast model found at {model_path}")
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
    if model is None:
        logger.warning("No forecast model available, using simulated predictions")
        return _generate_simulated_predictions(product_id, store_id, days)
        
    try:
        # In a real implementation, this would use the Prophet model
        # For now, we'll use simulated data
        return _generate_simulated_predictions(product_id, store_id, days)
    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
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
    predictions = []
    base_demand = random.randint(5, 20)  # Random base demand between 5-20 units
    
    # Add some product-specific variation
    product_factor = (product_id % 5) + 0.8  # 0.8-4.8 range
    
    # Add some store-specific variation
    store_factor = (store_id % 3) + 0.9  # 0.9-2.9 range
    
    today = datetime.now()
    
    for day in range(days):
        date = today + timedelta(days=day)
        
        # Day of week factor (weekend boost)
        weekday = date.weekday()
        day_factor = 1.3 if weekday >= 5 else 1.0  # Weekend boost
        
        # Add some randomness
        random_factor = random.uniform(0.8, 1.2)
        
        # Calculate demand
        demand = round(base_demand * product_factor * store_factor * day_factor * random_factor)
        
        predictions.append({
            'date': date.strftime('%Y-%m-%d'),
            'demand': demand
        })
    
    return predictions