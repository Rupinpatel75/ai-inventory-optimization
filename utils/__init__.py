"""
Utility modules for the AI Inventory Optimization System.
"""

# Import utility modules for easier access
from utils.web_scraper import scraper
from utils.llm_integration import llm_manager
from utils.forecasting import predict_demand, load_forecast_model
from utils.data_loader import load_sample_data, generate_historical_sales_data