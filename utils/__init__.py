"""
Utility modules for the AI Inventory Optimization System.

This package contains various utilities for forecasting, data loading,
web scraping, and more.
"""

import logging

logger = logging.getLogger(__name__)

# Import utilities for easier access
try:
    from .web_scraper import WebScraper
except ImportError:
    logger.warning("WebScraper import failed")
    WebScraper = None

try:
    from .llm_integration import (
        analyze_with_llm_provider, analyze_sales_pattern,
        explain_forecast, generate_inventory_recommendation,
        generate_pricing_recommendation
    )
except ImportError:
    logger.warning("LLM integration import failed")
    analyze_with_llm_provider = None
    analyze_sales_pattern = None
    explain_forecast = None
    generate_inventory_recommendation = None
    generate_pricing_recommendation = None