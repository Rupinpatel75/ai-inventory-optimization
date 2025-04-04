"""
AI Inventory Optimization System

This is the main application file for the AI Inventory Optimization System.
It sets up the Flask application, database connection, and initializes the
required components.
"""

import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize database
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Configure database connection
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    logger.info(f"Database URI configured: {database_url[:12]}...")  # Log just the start for security
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./instance/inventory_optimization.db"
    logger.warning("No DATABASE_URL found. Using SQLite database.")

# Configure additional database settings
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Set secret key for sessions
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize database with app
db.init_app(app)

# Import routes and register them
from routes import register_routes
register_routes(app)

# Initialize database tables if needed
with app.app_context():
    # Import models after app is created
    import models
    
    # Create tables
    db.create_all()
    
    # Initialize sample data if database is empty
    def init_sample_data():
        """Initialize sample data if database is empty."""
        try:
            from models import Product
            from utils.data_loader import load_sample_data
            
            # Check if any products exist
            if not db.session.query(Product).first():
                logger.info("No products found. Loading sample data...")
                load_sample_data()
            else:
                logger.info("Sample data already loaded.")
        except Exception as e:
            logger.error(f"Error initializing sample data: {str(e)}")
    
    # Initialize sample data
    init_sample_data()