"""
Entry point for the AI Inventory Optimization System.

This is a simplified version to help debug the application.
"""

import logging
from app_simplified import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting AI Inventory Optimization System (simplified)")
    app.run(host="0.0.0.0", port=5000, debug=True)