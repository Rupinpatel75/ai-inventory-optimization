import logging
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from models import PredictionLog
from app import db
from utils.forecasting import predict_demand as forecast_demand

logger = logging.getLogger(__name__)

class DemandAgent(BaseAgent):
    """
    Agent responsible for predicting future demand based on historical data.
    Uses Prophet forecasting model to make predictions.
    """
    
    def __init__(self):
        super().__init__("Demand Agent", "demand")
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
        try:
            # Log action start
            self.log_action(
                action="predict_demand_start",
                product_id=product_id,
                store_id=store_id,
                details={
                    "prediction_days": days
                }
            )
            
            # Get predictions from the forecasting model
            # In a production system, this would use a trained model
            # For now, we'll use the utility function that might use a model or fallback
            logger.info(f"Getting demand predictions for product {product_id} at store {store_id}")
            
            # Try to get predictions from forecasting utility
            predictions = forecast_demand(None, product_id, store_id, days)
            
            # If forecasting failed or returned empty, try to use LLM augmentation
            if not predictions and self.llm and self.llm.check_ollama_available():
                logger.info("Using LLM to augment demand prediction")
                
                # Create a context for the LLM
                context = {
                    "product_id": product_id,
                    "store_id": store_id,
                    "days": days,
                    "current_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Ask LLM for insights
                prompt = f"""
                Based on available data, provide reasonable demand predictions for product ID {product_id} 
                at store ID {store_id} for the next {days} days. 
                
                Consider:
                1. If it's a seasonal product
                2. General market trends
                3. Day of week effects
                4. Recent demand patterns
                
                Return a JSON array with daily predictions in this format:
                [
                  {{"date": "YYYY-MM-DD", "demand": numeric_value}},
                  ...
                ]
                
                ONLY return the JSON array, nothing else.
                """
                
                llm_response = self.analyze_with_llm(
                    prompt=prompt,
                    context=context,
                    system_prompt="You are a demand forecasting expert. Provide realistic demand predictions based on product and store context."
                )
                
                # Parse JSON from LLM response
                try:
                    # Extract JSON array if embedded in other text
                    import re
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', llm_response, re.DOTALL)
                    if json_match:
                        llm_json = json_match.group(0)
                        llm_predictions = json.loads(llm_json)
                        predictions = llm_predictions
                    else:
                        # Try to parse the whole response as JSON
                        predictions = json.loads(llm_response)
                except Exception as e:
                    logger.error(f"Failed to parse LLM prediction JSON: {str(e)}")
                    # Fallback to simulated predictions
                    predictions = self._simulate_predictions(product_id, store_id, days)
            elif not predictions:
                # If forecasting failed and LLM is not available, use simulated data
                logger.warning("Forecasting failed and LLM not available, using simulated predictions")
                predictions = self._simulate_predictions(product_id, store_id, days)
            
            # Calculate average predicted demand
            total_demand = sum(p.get('demand', 0) for p in predictions)
            avg_demand = total_demand / len(predictions) if predictions else 0
            
            # Log the prediction to the database
            prediction_log = PredictionLog(
                product_id=product_id,
                store_id=store_id,
                prediction_days=days,
                avg_predicted_demand=avg_demand,
                timestamp=datetime.now()
            )
            db.session.add(prediction_log)
            db.session.commit()
            
            # Log action completion
            self.log_action(
                action="predict_demand_complete",
                product_id=product_id,
                store_id=store_id,
                details={
                    "prediction_days": days,
                    "avg_predicted_demand": avg_demand,
                    "predictions_count": len(predictions)
                }
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in demand prediction: {str(e)}")
            self.log_action(
                action="predict_demand_error",
                product_id=product_id,
                store_id=store_id,
                details={
                    "error": str(e)
                }
            )
            return []
    
    def _simulate_predictions(self, product_id, store_id, days):
        """
        Simulate demand predictions when the model is unavailable.
        
        This is a fallback method only used when the actual forecasting model
        isn't available or fails.
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