import logging
import json
import random
import numpy as np
from datetime import datetime, timedelta
from utils.forecasting import load_forecast_model, predict_demand
from app import db
from models import AgentAction, Product, Store, InventoryRecord

logger = logging.getLogger(__name__)

class DemandAgent:
    """
    Agent responsible for predicting future demand based on historical data.
    Uses Prophet forecasting model to make predictions.
    """
    
    def __init__(self):
        self.name = "Demand Agent"
        self.forecast_model = None
        logger.info("Demand Agent initialized")
    
    def predict_demand(self, product_id, store_id, days=30):
        """
        Predict demand for a product at a specific store for the next N days.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to forecast
            
        Returns:
            List of dictionaries with date and predicted demand value
        """
        logger.debug(f"Predicting demand for product {product_id} at store {store_id} for {days} days")
        
        try:
            # Try to load the forecast model if not already loaded
            if self.forecast_model is None:
                self.forecast_model = load_forecast_model()
            
            # Get predictions from Prophet model
            predictions = predict_demand(self.forecast_model, product_id, store_id, days)
            
            # Log this action
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            action = AgentAction(
                agent_type="demand",
                action="predict_demand",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps({
                    "days": days,
                    "avg_prediction": sum(p['value'] for p in predictions) / len(predictions) if predictions else 0,
                    "product_name": product.name if product else "Unknown",
                    "store_name": store.name if store else "Unknown"
                })
            )
            db.session.add(action)
            db.session.commit()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in demand prediction: {str(e)}")
            # If model fails, fall back to simulated predictions
            return self._simulate_predictions(product_id, store_id, days)
    
    def _simulate_predictions(self, product_id, store_id, days):
        """
        Simulate demand predictions when the model is unavailable.
        
        This is a fallback method only used when the actual forecasting model
        isn't available or fails.
        """
        logger.warning("Using simulated predictions as fallback")
        
        # Get current inventory as baseline
        inventory_record = InventoryRecord.query.filter_by(
            product_id=product_id, 
            store_id=store_id
        ).first()
        
        baseline = 10  # Default baseline
        if inventory_record:
            # Use current inventory to estimate reasonable demand
            baseline = max(5, inventory_record.quantity * 0.1)
        
        # Generate simulated predictions
        start_date = datetime.now()
        predictions = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # Add some randomness and a slight trend
            trend_factor = 1.0 + (i * 0.01)  # Slight upward trend
            
            # Weekend effect (higher demand on weekends)
            day_of_week = current_date.weekday()
            weekend_factor = 1.3 if day_of_week >= 5 else 1.0
            
            # Randomness factor
            random_factor = random.uniform(0.85, 1.15)
            
            # Calculate predicted value
            value = baseline * trend_factor * weekend_factor * random_factor
            
            predictions.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'value': round(value, 2)
            })
        
        return predictions
