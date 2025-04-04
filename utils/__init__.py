"""
Utility modules for the AI Inventory Optimization System.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import utility modules - removed generate_historical_sales_data from import
from utils.data_loader import load_sample_data
from utils.forecasting import predict_demand, load_forecast_model
from utils.web_scraper import WebScraper