"""
Entry point for the AI Inventory Optimization System.

This file is the entry point for the application when run on Replit or
with Gunicorn. It imports the Flask app from app.py and makes it
available to the WSGI server.
"""

import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting AI Inventory Optimization System")
    app.run(host="0.0.0.0", port=5000, debug=True)