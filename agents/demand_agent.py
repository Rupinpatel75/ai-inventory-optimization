"""
Demand Agent module for the AI Inventory Optimization System.

This module provides the demand forecasting agent that predicts
future product demand based on historical data and market factors.
"""

import logging
from agents.base_agent import BaseAgent
from utils.forecasting import predict_demand, load_forecast_model
from utils.data_loader import generate_historical_sales_data
from models import PredictionLog, db
from datetime import datetime

logger = logging.getLogger(__name__)

class DemandAgent(BaseAgent):
    """
    Demand forecasting agent that predicts future product demand
    based on historical data and market factors.
    """
    
    def __init__(self):
        """Initialize the demand agent."""
        super().__init__(agent_type="demand")
    
    def predict_product_demand(self, product_id, store_id, days=30):
        """
        Predict demand for a product at a specific store for the given days.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to forecast
            
        Returns:
            List of dictionaries with date and predicted demand
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Generate demand predictions
            predictions = predict_demand(product_id, store_id, days)
            
            # Calculate average predicted demand
            total_demand = sum(p.get('demand', 0) for p in predictions)
            avg_demand = total_demand / days if days > 0 else 0
            
            # Log the prediction
            self._log_prediction(product_id, store_id, days, avg_demand)
            
            # Log the agent action
            details = {
                "days": days,
                "avg_demand": round(avg_demand, 2),
                "predictions": [
                    {"date": p["date"], "demand": p["demand"]} 
                    for p in predictions[:10]  # Include first 10 days in log
                ] + (
                    [{"...": "..."}] if len(predictions) > 10 else []
                )
            }
            
            self.log_action(
                action="Demand prediction",
                product_id=product_id,
                store_id=store_id,
                details=details
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "days": days,
                "avg_predicted_demand": round(avg_demand, 2),
                "total_predicted_demand": round(total_demand, 2),
                "predictions": predictions
            }
        
        except Exception as e:
            logger.error(f"Error predicting demand: {str(e)}")
            return {
                "error": f"Failed to predict demand: {str(e)}"
            }
    
    def get_historical_sales(self, product_id, store_id, days=90):
        """
        Get historical sales data for a product at a specific store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days of historical data
            
        Returns:
            List of dictionaries with date and sales data
        """
        try:
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Generate historical sales data
            sales_data = generate_historical_sales_data(product_id, store_id, days)
            
            # Log the agent action
            details = {
                "days": days,
                "data_points": len(sales_data),
                "samples": sales_data[:5] if sales_data else []  # Include first 5 days in log
            }
            
            self.log_action(
                action="Historical sales retrieval",
                product_id=product_id,
                store_id=store_id,
                details=details
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "days": days,
                "sales_data": sales_data
            }
        
        except Exception as e:
            logger.error(f"Error getting historical sales: {str(e)}")
            return {
                "error": f"Failed to get historical sales: {str(e)}"
            }
    
    def analyze_seasonality(self, product_id, store_id, days=90):
        """
        Analyze seasonality patterns in historical sales data.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days of historical data to analyze
            
        Returns:
            Dictionary with seasonality analysis
        """
        try:
            # Get historical sales data
            sales_response = self.get_historical_sales(product_id, store_id, days)
            
            if "error" in sales_response:
                return sales_response
            
            sales_data = sales_response.get("sales_data", [])
            
            if not sales_data:
                return {
                    "error": "No historical sales data available for analysis"
                }
            
            # Analyze by day of week
            day_of_week_sales = {i: [] for i in range(7)}  # 0 = Monday, 6 = Sunday
            
            for data_point in sales_data:
                day = data_point.get("day_of_week")
                sales = data_point.get("sales")
                if day is not None and sales is not None:
                    day_of_week_sales[day].append(sales)
            
            # Calculate average sales by day of week
            day_of_week_avg = {}
            for day, sales in day_of_week_sales.items():
                if sales:
                    day_of_week_avg[day] = sum(sales) / len(sales)
                else:
                    day_of_week_avg[day] = 0
            
            # Calculate overall average
            all_sales = [d.get("sales", 0) for d in sales_data]
            overall_avg = sum(all_sales) / len(all_sales) if all_sales else 0
            
            # Calculate seasonality factors
            dow_seasonality = {}
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for day, avg in day_of_week_avg.items():
                if overall_avg > 0:
                    factor = avg / overall_avg
                else:
                    factor = 1.0
                
                dow_seasonality[days_of_week[day]] = round(factor, 2)
            
            # Analyze by month
            month_sales = {i: [] for i in range(1, 13)}  # 1 = January, 12 = December
            
            for data_point in sales_data:
                month = data_point.get("month")
                sales = data_point.get("sales")
                if month and sales:
                    month_sales[month].append(sales)
            
            # Calculate average sales by month
            month_avg = {}
            for month, sales in month_sales.items():
                if sales:
                    month_avg[month] = sum(sales) / len(sales)
                else:
                    month_avg[month] = 0
            
            # Calculate monthly seasonality factors
            month_seasonality = {}
            months = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
            
            for month, avg in month_avg.items():
                if overall_avg > 0:
                    factor = avg / overall_avg
                else:
                    factor = 1.0
                
                month_seasonality[months[month-1]] = round(factor, 2)
            
            # Log the agent action
            details = {
                "day_of_week_seasonality": dow_seasonality,
                "month_seasonality": month_seasonality
            }
            
            self.log_action(
                action="Seasonality analysis",
                product_id=product_id,
                store_id=store_id,
                details=details
            )
            
            # Identify peak periods
            peak_day = max(dow_seasonality.items(), key=lambda x: x[1])[0]
            peak_month = max(month_seasonality.items(), key=lambda x: x[1])[0]
            
            # Identify low periods
            low_day = min(dow_seasonality.items(), key=lambda x: x[1])[0]
            low_month = min(month_seasonality.items(), key=lambda x: x[1])[0]
            
            return {
                "product_id": product_id,
                "product_name": sales_response.get("product_name"),
                "store_id": store_id,
                "store_name": sales_response.get("store_name"),
                "overall_avg_daily_sales": round(overall_avg, 2),
                "day_of_week_seasonality": dow_seasonality,
                "month_seasonality": month_seasonality,
                "peak_day": peak_day,
                "peak_month": peak_month,
                "low_day": low_day,
                "low_month": low_month,
                "samples_analyzed": len(sales_data)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing seasonality: {str(e)}")
            return {
                "error": f"Failed to analyze seasonality: {str(e)}"
            }
    
    def _log_prediction(self, product_id, store_id, days, avg_demand):
        """
        Log a demand prediction to the database.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days forecasted
            avg_demand: Average predicted demand
            
        Returns:
            None
        """
        try:
            prediction_log = PredictionLog(
                product_id=product_id,
                store_id=store_id,
                prediction_days=days,
                avg_predicted_demand=avg_demand,
                timestamp=datetime.now()
            )
            
            db.session.add(prediction_log)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error logging prediction: {str(e)}")
    
    def explain_forecast(self, product_id, store_id, days=30):
        """
        Generate a natural language explanation of the demand forecast.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast and explanation
        """
        try:
            # Get product and store
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get forecast
            forecast_response = self.predict_product_demand(product_id, store_id, days)
            
            if "error" in forecast_response:
                return forecast_response
            
            # Get seasonality analysis
            seasonality = self.analyze_seasonality(product_id, store_id)
            
            # Get forecast model parameters
            model = load_forecast_model(product_id, store_id)
            
            # Generate explanation using LLM if available
            prompt = f"""
            Please provide a brief explanation of the demand forecast for {product.name} at {store.name}.
            
            Product: {product.name}
            Category: {product.category}
            Store: {store.name}
            Location: {store.location}
            
            Forecast summary:
            - Days forecasted: {days}
            - Average daily demand: {forecast_response.get('avg_predicted_demand')} units
            - Total demand over {days} days: {forecast_response.get('total_predicted_demand')} units
            
            Model parameters:
            - Base daily sales: {model.get('avg_daily_sales')} units
            - Sales trend: {model.get('trend')}% per day
            - Seasonality factor: {model.get('seasonality_factor')}
            - Promotion effect: +{model.get('promotion_effect') * 100}%
            - Price elasticity: {model.get('price_elasticity')}
            
            Seasonality insights:
            - Peak day: {seasonality.get('peak_day')}
            - Peak month: {seasonality.get('peak_month')}
            - Lowest day: {seasonality.get('low_day')}
            - Lowest month: {seasonality.get('low_month')}
            
            Please provide a 3-4 sentence explanation of this forecast in plain language.
            """
            
            system_prompt = """
            You are a helpful AI assistant explaining a demand forecast to a retail manager.
            Your explanation should be clear, concise, and focused on actionable insights.
            Highlight key trends, peaks, and any unusual patterns in the forecast.
            """
            
            explanation = self.analyze_with_llm(prompt, system_prompt)
            
            if not explanation or "error" in explanation.lower():
                # Generate a basic explanation if LLM fails
                explanation = f"Forecast for {product.name} at {store.name} projects an average daily demand of {forecast_response.get('avg_predicted_demand')} units, with a total of {forecast_response.get('total_predicted_demand')} units over the next {days} days. "
                
                if seasonality.get('peak_day') and seasonality.get('peak_month'):
                    explanation += f"Sales are highest on {seasonality.get('peak_day')}s and during {seasonality.get('peak_month')}. "
                
                if model.get('trend', 0) > 0:
                    explanation += f"Demand shows an increasing trend of approximately {model.get('trend')}% per day."
                elif model.get('trend', 0) < 0:
                    explanation += f"Demand shows a decreasing trend of approximately {abs(model.get('trend'))}% per day."
                else:
                    explanation += f"Demand is relatively stable with no significant trend."
            
            # Log the agent action
            self.log_action(
                action="Forecast explanation",
                product_id=product_id,
                store_id=store_id,
                details={"explanation": explanation}
            )
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "forecast": forecast_response,
                "explanation": explanation,
                "seasonality": seasonality
            }
        
        except Exception as e:
            logger.error(f"Error explaining forecast: {str(e)}")
            return {
                "error": f"Failed to explain forecast: {str(e)}"
            }