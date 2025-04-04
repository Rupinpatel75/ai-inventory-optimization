"""
AI Inventory Optimization System

This is the main application file for the AI Inventory Optimization System.
It sets up the Flask application, database connection, and initializes the
required components.
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)

# Configure the application
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-development-only')

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask application
db.init_app(app)

# Sample data for initialization
def init_sample_data():
    """Initialize sample data if database is empty."""
    try:
        logger.info("Initializing database with CSV data...")
        # Import the database initialization utility
        from utils.init_db import initialize_database
        
        # Initialize database with CSV data
        initialize_database()
        
        # Check if there are any products in the database
        from models_simplified import Product, Store
        product_count = db.session.query(Product).count()
        store_count = db.session.query(Store).count()
        logger.info(f"Database now has {product_count} products and {store_count} stores")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Initialize routes
def register_blueprints():
    """Register Flask blueprints for routes."""
    # Import routes at runtime to avoid circular imports
    from routes_simplified import register_routes
    register_routes(app)

# Flask application setup
def setup_application():
    """Set up the application before the first request."""
    try:
        # Create database tables
        with app.app_context():
            # Import and create tables for simplified models
            from models_simplified import Product, Store, Inventory, AgentLog, User
            db.create_all()
            init_sample_data()
            
        # Initialize agent system
        try:
            from agents import initialize_agents
            agents = initialize_agents()
            logger.info(f"Initialized agents: {', '.join(agents.keys())}")
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
        
        logger.info("Application setup completed successfully")
    except Exception as e:
        logger.error(f"Error during application setup: {str(e)}")

# Call setup application at startup
with app.app_context():
    setup_application()

# Register blueprints
register_blueprints()

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)