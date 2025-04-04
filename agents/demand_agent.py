"""
Demand Agent module for the AI Inventory Optimization System.

This module provides the demand forecasting agent that predicts
future product demand based on historical data and external factors.
"""

import logging
import json
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from utils.forecasting import predict_demand, get_historical_sales, analyze_seasonality
from models import Product, Store, PredictionLog, db

logger = logging.getLogger(__name__)

class DemandAgent(BaseAgent):
    """
    Demand forecasting agent that predicts future product demand
    based on historical sales data and external factors.
    """
    
    def __init__(self):
        """Initialize the demand agent."""
        super().__init__(agent_type="demand")
    
    def predict_product_demand(self, product_id, store_id, days=30):
        """
        Predict demand for a product at a store.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days to forecast
            
        Returns:
            Dictionary with prediction details
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
            
            # Get demand prediction
            prediction = predict_demand(product_id, store_id, days)
            
            if "error" in prediction:
                return prediction
            
            # Log the prediction to the database
            prediction_log = PredictionLog(
                product_id=product_id,
                store_id=store_id,
                prediction_days=days,
                avg_predicted_demand=prediction["avg_daily_demand"],
                timestamp=datetime.now()
            )
            
            db.session.add(prediction_log)
            db.session.commit()
            
            # Log the agent action
            self.log_action(
                action="Demand prediction",
                product_id=product_id,
                store_id=store_id,
                details=prediction
            )
            
            # Add product and store names to the response
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **prediction
            }
            
            # Extract chart data for visualization
            chart_data = {
                "dates": [p["date"] for p in prediction["daily_predictions"]],
                "values": [p["demand"] for p in prediction["daily_predictions"]]
            }
            
            result["chart_data"] = chart_data
            
            return result
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error predicting product demand: {str(e)}")
            return {
                "error": f"Failed to predict product demand: {str(e)}"
            }
    
    def get_historical_sales(self, product_id, store_id, days=90):
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
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Get historical sales data
            historical = get_historical_sales(product_id, store_id, days)
            
            if "error" in historical:
                return historical
            
            # Log the agent action
            self.log_action(
                action="Historical sales data retrieval",
                product_id=product_id,
                store_id=store_id,
                details={
                    "days": days,
                    "total_sales": historical.get("total_sales", 0),
                    "avg_daily_sales": historical.get("avg_daily_sales", 0)
                }
            )
            
            # Add product and store names to the response
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **historical
            }
            
            # Extract chart data for visualization
            chart_data = {
                "dates": [d["date"] for d in historical["daily_sales"]],
                "values": [d["sales"] for d in historical["daily_sales"]]
            }
            
            result["chart_data"] = chart_data
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting historical sales: {str(e)}")
            return {
                "error": f"Failed to get historical sales: {str(e)}"
            }
    
    def analyze_seasonality(self, product_id, store_id, days=365):
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
            # Get product and store to check if they exist
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            if not product or not store:
                logger.error(f"Product {product_id} or store {store_id} not found")
                return {
                    "error": f"Product {product_id} or store {store_id} not found"
                }
            
            # Analyze seasonality
            seasonality = analyze_seasonality(product_id, store_id, days)
            
            if "error" in seasonality:
                return seasonality
            
            # Log the agent action
            self.log_action(
                action="Seasonality analysis",
                product_id=product_id,
                store_id=store_id,
                details={
                    "peak_day": seasonality.get("peak_day", ""),
                    "peak_month": seasonality.get("peak_month", ""),
                    "seasonality_strength": seasonality.get("seasonality_strength", 0)
                }
            )
            
            # Add product and store names to the response
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                **seasonality
            }
            
            # Extract chart data for weekly pattern visualization
            weekly_chart_data = {
                "labels": [wp["day_name"] for wp in seasonality["weekly_pattern"]],
                "values": [wp["relative_to_avg"] for wp in seasonality["weekly_pattern"]]
            }
            
            # Extract chart data for monthly pattern visualization
            monthly_chart_data = {
                "labels": [mp["month_name"] for mp in seasonality["monthly_pattern"]],
                "values": [mp["relative_to_avg"] for mp in seasonality["monthly_pattern"]]
            }
            
            result["weekly_chart_data"] = weekly_chart_data
            result["monthly_chart_data"] = monthly_chart_data
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing seasonality: {str(e)}")
            return {
                "error": f"Failed to analyze seasonality: {str(e)}"
            }
    
    def analyze_external_factors(self, product_id, store_id):
        """
        Analyze external factors affecting demand.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            
        Returns:
            Dictionary with external factors analysis
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
            
            # In a real implementation, this would analyze weather data, economic indicators,
            # competitor actions, etc.
            # For now, we'll return a simplified analysis
            
            external_factors = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "weather_impact": {
                    "correlation": round(0.3 + (product_id * store_id % 10) / 20, 2),
                    "significance": "medium",
                    "description": "Moderate positive correlation with temperature for this product category."
                },
                "economic_indicators": {
                    "correlation": round(0.2 + (product_id * store_id % 5) / 10, 2),
                    "significance": "low",
                    "description": "Some correlation with local employment rate changes."
                },
                "competitor_actions": {
                    "significance": "high",
                    "description": "Promotions by competitors show strong negative impact on sales."
                },
                "social_media": {
                    "correlation": round(0.4 + (product_id * store_id % 7) / 20, 2),
                    "significance": "medium",
                    "description": "Social media sentiment shows moderate correlation with sales."
                }
            }
            
            # Generate natural language summary using LLM if available
            prompt = f"""
            Please provide a brief summary of the external factors affecting demand for {product.name} at {store.name}.
            
            Factors:
            - Weather: {external_factors['weather_impact']['description']} (Correlation: {external_factors['weather_impact']['correlation']})
            - Economic: {external_factors['economic_indicators']['description']} (Correlation: {external_factors['economic_indicators']['correlation']})
            - Competitors: {external_factors['competitor_actions']['description']}
            - Social Media: {external_factors['social_media']['description']} (Correlation: {external_factors['social_media']['correlation']})
            
            Based on the above, what are the 2-3 most significant external factors that should be monitored and incorporated into demand forecasting?
            Provide a short paragraph (3-4 sentences).
            """
            
            system_prompt = """
            You are a helpful AI assistant specializing in retail analytics and demand forecasting.
            Provide concise, actionable insights based on the data provided.
            Focus on the most significant factors affecting demand.
            """
            
            summary = self.analyze_with_llm(prompt, system_prompt)
            
            if summary:
                external_factors["summary"] = summary
            else:
                # Fallback if LLM is not available
                external_factors["summary"] = (
                    f"For {product.name} at {store.name}, competitor promotions appear to have the strongest "
                    f"impact on demand, showing a high significance. Social media sentiment and weather "
                    f"patterns also show moderate correlations of {external_factors['social_media']['correlation']} and "
                    f"{external_factors['weather_impact']['correlation']} respectively. It's recommended to closely "
                    f"monitor competitor actions and develop strategies to mitigate their impact."
                )
            
            # Log the agent action
            self.log_action(
                action="External factors analysis",
                product_id=product_id,
                store_id=store_id,
                details=external_factors
            )
            
            return external_factors
        
        except Exception as e:
            logger.error(f"Error analyzing external factors: {str(e)}")
            return {
                "error": f"Failed to analyze external factors: {str(e)}"
            }
    
    def explain_forecast(self, product_id, store_id, days=30):
        """
        Generate a natural language explanation of a demand forecast.
        
        Args:
            product_id: ID of the product
            store_id: ID of the store
            days: Number of days of forecast to explain
            
        Returns:
            Dictionary with forecast explanation
        """
        try:
            # Get the forecast
            forecast = self.predict_product_demand(product_id, store_id, days)
            
            if "error" in forecast:
                return forecast
            
            # Get seasonality analysis
            seasonality = self.analyze_seasonality(product_id, store_id)
            
            # Generate explanation using LLM if available
            product = self.get_product(product_id)
            store = self.get_store(store_id)
            
            # Prepare prompt with forecast data
            prompt = f"""
            Please explain the following demand forecast in clear, concise language for a store manager:
            
            Product: {product.name}
            Store: {store.name}
            Forecast period: {days} days
            Total forecasted demand: {forecast.get('total_demand', 0)} units
            Average daily demand: {forecast.get('avg_daily_demand', 0)} units
            Coefficient of variation: {forecast.get('coefficient_of_variation', 0)}
            
            """
            
            if "error" not in seasonality:
                prompt += f"""
                Seasonality patterns:
                - Peak day of week: {seasonality.get('peak_day', 'Unknown')}
                - Lowest day of week: {seasonality.get('trough_day', 'Unknown')}
                - Peak month: {seasonality.get('peak_month', 'Unknown')}
                - Lowest month: {seasonality.get('trough_month', 'Unknown')}
                - Seasonality strength: {seasonality.get('seasonality_strength', 0)}
                """
            
            prompt += """
            Please provide:
            1. A 3-4 sentence summary of the forecast, highlighting the most important insights
            2. 2-3 key actionable recommendations for the store manager based on this forecast
            
            Focus on practical implications for inventory management and staffing.
            """
            
            system_prompt = """
            You are a helpful AI assistant specializing in demand forecasting for retail.
            Provide clear, concise explanations that non-technical retail managers can understand.
            Focus on actionable insights and practical recommendations.
            """
            
            explanation = self.analyze_with_llm(prompt, system_prompt)
            
            if not explanation:
                # Fallback if LLM is not available
                explanation = (
                    f"The forecast for {product.name} at {store.name} predicts a total demand of "
                    f"{forecast.get('total_demand', 0)} units over the next {days} days, with an average "
                    f"daily demand of {forecast.get('avg_daily_demand', 0)} units. "
                    f"The demand shows {'high' if forecast.get('coefficient_of_variation', 0) > 0.5 else 'moderate' if forecast.get('coefficient_of_variation', 0) > 0.2 else 'low'} "
                    f"variability (coefficient of variation: {forecast.get('coefficient_of_variation', 0)}).\n\n"
                    f"Recommendations:\n"
                    f"1. Maintain sufficient safety stock due to the {'high' if forecast.get('coefficient_of_variation', 0) > 0.5 else 'moderate' if forecast.get('coefficient_of_variation', 0) > 0.2 else 'low'} variability in demand.\n"
                    f"2. Plan for higher staffing on {seasonality.get('peak_day', 'weekends')} when demand is expected to be highest.\n"
                    f"3. Consider running promotions during {seasonality.get('trough_month', 'slower months')} to boost sales during typically slower periods."
                )
            
            # Log the agent action
            self.log_action(
                action="Forecast explanation",
                product_id=product_id,
                store_id=store_id,
                details={"explanation": explanation}
            )
            
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "store_id": store_id,
                "store_name": store.name,
                "days": days,
                "forecast_summary": {
                    "total_demand": forecast.get('total_demand', 0),
                    "avg_daily_demand": forecast.get('avg_daily_demand', 0),
                    "coefficient_of_variation": forecast.get('coefficient_of_variation', 0)
                },
                "explanation": explanation
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error explaining forecast: {str(e)}")
            return {
                "error": f"Failed to explain forecast: {str(e)}"
            }