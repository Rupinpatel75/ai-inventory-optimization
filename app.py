"""
AI Inventory Optimization System

This is the main application file for the AI Inventory Optimization System.
It sets up the Flask application, database connection, and initializes the
required components.
"""

import os
import logging
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base model class
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database (PostgreSQL in production, SQLite for development)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # For PostgreSQL deployed on platforms like Heroku
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/inventory_optimization.db"

# Configure SQLAlchemy
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with extensions
db.init_app(app)

# Import routes after creating app to avoid circular imports
from routes import register_routes

# Register routes
register_routes(app)

def init_sample_data():
    """Initialize sample data if database is empty."""
    from models import Product, Store, Supplier, Inventory, Sale, User, SystemConfig
    
    try:
        # Check if we already have data
        if db.session.query(Product).count() > 0:
            return
        
        logger.info("Initializing sample data...")
        
        # Create sample supplier
        supplier = Supplier(
            name="Demo Supplier",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890",
            city="New York",
            country="USA",
            lead_time_days=3,
            reliability_score=85.0
        )
        db.session.add(supplier)
        db.session.commit()
        
        # Create sample products
        products = [
            Product(
                sku="P001",
                name="Basic T-Shirt",
                description="100% cotton basic t-shirt",
                category="Apparel",
                subcategory="T-Shirts",
                base_price=19.99,
                cost_price=8.50,
                supplier_id=supplier.id
            ),
            Product(
                sku="P002",
                name="Premium Jeans",
                description="High-quality denim jeans",
                category="Apparel",
                subcategory="Pants",
                base_price=49.99,
                cost_price=22.50,
                supplier_id=supplier.id
            ),
            Product(
                sku="P003",
                name="Wireless Headphones",
                description="Noise-cancelling wireless headphones",
                category="Electronics",
                subcategory="Audio",
                base_price=129.99,
                cost_price=65.00,
                supplier_id=supplier.id
            ),
            Product(
                sku="P004",
                name="Smart Watch",
                description="Fitness and health tracking smart watch",
                category="Electronics",
                subcategory="Wearables",
                base_price=199.99,
                cost_price=95.00,
                supplier_id=supplier.id
            ),
            Product(
                sku="P005",
                name="Coffee Maker",
                description="Programmable 12-cup coffee maker",
                category="Home",
                subcategory="Kitchen",
                base_price=79.99,
                cost_price=35.00,
                supplier_id=supplier.id
            )
        ]
        db.session.add_all(products)
        db.session.commit()
        
        # Create sample stores
        stores = [
            Store(
                name="Downtown Store",
                address="123 Main St",
                city="New York",
                state="NY",
                country="USA",
                postal_code="10001",
                region="Northeast",
                store_type="physical",
                size=5000
            ),
            Store(
                name="West Coast Store",
                address="456 Ocean Ave",
                city="Los Angeles",
                state="CA",
                country="USA",
                postal_code="90001",
                region="West",
                store_type="physical",
                size=7500
            ),
            Store(
                name="Online Store",
                city="N/A",
                country="USA",
                region="Online",
                store_type="online"
            )
        ]
        db.session.add_all(stores)
        db.session.commit()
        
        # Create sample inventory
        inventory_records = []
        for product in products:
            for store in stores:
                inventory_records.append(
                    Inventory(
                        product_id=product.id,
                        store_id=store.id,
                        quantity=100,
                        reorder_point=20,
                        reorder_quantity=50
                    )
                )
        db.session.add_all(inventory_records)
        db.session.commit()
        
        # Create sample admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash="pbkdf2:sha256:150000$QS3Rc9Iq$7c8fb6841a9bb2d9026332b5fe9b430f6a89a52a95e7be22abe28c1a2857d7d7",  # "password"
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        
        # Create system config
        system_config = SystemConfig(
            key="system_initialized",
            value="true",
            description="Flag indicating if the system has been initialized with sample data"
        )
        db.session.add(system_config)
        db.session.commit()
        
        logger.info("Sample data initialization complete")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing sample data: {str(e)}")

@app.before_first_request
def setup_application():
    """Set up the application before the first request."""
    # Create all tables in the database
    with app.app_context():
        db.create_all()
        init_sample_data()

# Run the application
if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        init_sample_data()
    
    # Start the development server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)