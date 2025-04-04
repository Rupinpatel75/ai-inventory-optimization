"""
Entry point for the AI Inventory Optimization System.

This file is the entry point for the application when run on Replit or
with Gunicorn. It imports the Flask app from app.py and makes it
available to the WSGI server.
"""

import os
import logging
from app import app, db, init_sample_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the database and sample data before first request
with app.app_context():
    db.create_all()
    init_sample_data()
    logger.info("Application initialized")

# Export the app for Gunicorn or other WSGI servers
if __name__ == "__main__":
    # Start the development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)