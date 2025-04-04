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
    from models import (
        Product, Store, Supplier, Inventory, Sale, 
        User, Promotion, AgentLog, SystemConfig
    )
    
    # Check if we have any data already
    if db.session.query(Product).count() > 0:
        logger.info("Database already has data, skipping sample data initialization")
        return
    
    logger.info("Initializing sample data...")
    
    # Create sample suppliers
    suppliers = [
        Supplier(
            name="Tech Components Inc.",
            contact_name="John Smith",
            email="john.smith@techcomp.com",
            phone="555-123-4567",
            lead_time_days=5,
            reliability_score=0.92,
            city="San Francisco",
            state="CA",
            country="USA"
        ),
        Supplier(
            name="Global Electronics",
            contact_name="Sara Johnson",
            email="sara.j@globalelec.com",
            phone="555-987-6543",
            lead_time_days=7,
            reliability_score=0.85,
            city="Boston",
            state="MA",
            country="USA"
        ),
        Supplier(
            name="QuickShip Distributors",
            contact_name="Mike Williams",
            email="mike.w@quickship.com",
            phone="555-456-7890",
            lead_time_days=3,
            reliability_score=0.95,
            city="Dallas",
            state="TX",
            country="USA"
        )
    ]
    
    for supplier in suppliers:
        db.session.add(supplier)
    
    # Commit suppliers to get their IDs
    db.session.commit()
    
    # Create sample products
    products = [
        Product(
            sku="LAP-001",
            name="Premium Laptop",
            description="High-performance laptop with 16GB RAM and 512GB SSD",
            category="Electronics",
            subcategory="Computers",
            brand="TechBrand",
            supplier_id=suppliers[0].id,
            base_price=899.99,
            cost_price=699.99,
            min_stock_level=15,
            lead_time_days=5
        ),
        Product(
            sku="PHONE-002",
            name="Smartphone X",
            description="Latest smartphone with 128GB storage and 5G capability",
            category="Electronics",
            subcategory="Phones",
            brand="MobileTech",
            supplier_id=suppliers[1].id,
            base_price=699.99,
            cost_price=499.99,
            min_stock_level=25,
            lead_time_days=4
        ),
        Product(
            sku="AUDIO-003",
            name="Wireless Headphones",
            description="Noise-cancelling wireless headphones with 20hr battery life",
            category="Electronics",
            subcategory="Audio",
            brand="SoundWave",
            supplier_id=suppliers[2].id,
            base_price=149.99,
            cost_price=89.99,
            min_stock_level=30,
            lead_time_days=3
        ),
        Product(
            sku="TABLET-004",
            name="Pro Tablet",
            description="10-inch tablet with high-resolution display and stylus support",
            category="Electronics",
            subcategory="Tablets",
            brand="TechBrand",
            supplier_id=suppliers[0].id,
            base_price=499.99,
            cost_price=349.99,
            min_stock_level=20,
            lead_time_days=6
        ),
        Product(
            sku="WATCH-005",
            name="Smart Watch",
            description="Fitness tracking smartwatch with heart rate monitor",
            category="Electronics",
            subcategory="Wearables",
            brand="FitTech",
            supplier_id=suppliers[1].id,
            base_price=199.99,
            cost_price=129.99,
            min_stock_level=25,
            lead_time_days=5
        )
    ]
    
    for product in products:
        db.session.add(product)
    
    # Commit products to get their IDs
    db.session.commit()
    
    # Create sample stores
    stores = [
        Store(
            name="Downtown Flagship Store",
            code="STORE-001",
            store_type="retail",
            address="123 Main Street",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            size_sqft=5000,
            manager_name="Jane Anderson"
        ),
        Store(
            name="West Side Location",
            code="STORE-002",
            store_type="retail",
            address="456 West Avenue",
            city="Los Angeles",
            state="CA",
            country="USA",
            postal_code="90001",
            size_sqft=3500,
            manager_name="Robert Johnson"
        ),
        Store(
            name="Central Warehouse",
            code="WAREHOUSE-001",
            store_type="warehouse",
            address="789 Distribution Blvd",
            city="Chicago",
            state="IL",
            country="USA",
            postal_code="60007",
            size_sqft=15000,
            manager_name="Thomas Wilson"
        ),
        Store(
            name="Online Fulfillment Center",
            code="ONLINE-001",
            store_type="online",
            address="321 E-Commerce Way",
            city="Seattle",
            state="WA",
            country="USA",
            postal_code="98101",
            size_sqft=12000,
            manager_name="Lisa Brown"
        )
    ]
    
    for store in stores:
        db.session.add(store)
    
    # Commit stores to get their IDs
    db.session.commit()
    
    # Create sample inventory records
    inventory_records = []
    
    # Add inventory for each product in each store
    for product in products:
        for store in stores:
            # Different quantities based on store type
            if store.store_type == "warehouse":
                quantity = 150 + (product.id * 10)
                reorder_point = 50
                reorder_quantity = 100
            elif store.store_type == "online":
                quantity = 100 + (product.id * 8)
                reorder_point = 40
                reorder_quantity = 80
            else:  # retail
                quantity = 50 + (product.id * 5)
                reorder_point = 20
                reorder_quantity = 40
            
            inventory = Inventory(
                product_id=product.id,
                store_id=store.id,
                quantity=quantity,
                reorder_point=reorder_point,
                reorder_quantity=reorder_quantity,
                last_restock_date=datetime(2023, 3, 1),
                last_count_date=datetime(2023, 3, 15),
            )
            inventory_records.append(inventory)
    
    for inventory in inventory_records:
        db.session.add(inventory)
    
    # Create sample sales data
    sales_records = []
    
    # Generate 90 days of sales data for each product in each store
    import random
    from datetime import timedelta
    
    start_date = datetime(2023, 1, 1)
    for product in products:
        # Base demand varies by product
        base_demand = 5 + (product.id * 2)
        
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            
            # Weekend effect
            weekend_factor = 1.5 if current_date.weekday() >= 5 else 1.0
            
            # Monthly seasonality (higher at beginning of month)
            day_of_month = current_date.day
            monthly_factor = 1.2 if day_of_month <= 5 else 1.0
            
            for store in stores:
                # Store type affects demand
                if store.store_type == "retail":
                    store_factor = 1.0
                elif store.store_type == "online":
                    store_factor = 1.2
                else:  # warehouse - mostly bulk orders
                    store_factor = 0.3
                
                # Calculate quantity with some randomness
                base_quantity = base_demand * weekend_factor * monthly_factor * store_factor
                quantity = max(1, int(base_quantity + random.normalvariate(0, base_quantity * 0.2)))
                
                # 10% of the time, no sales occur
                if random.random() < 0.1 and store.store_type != "online":
                    continue
                
                # Calculate pricing with occasional discounts
                discount_percent = 0
                if random.random() < 0.2:  # 20% chance of discount
                    discount_percent = random.choice([5, 10, 15, 20])
                
                unit_price = product.base_price * (1 - discount_percent / 100)
                total_price = unit_price * quantity
                discount_amount = product.base_price * quantity * discount_percent / 100
                
                sale = Sale(
                    product_id=product.id,
                    store_id=store.id,
                    date=current_date,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    total_price=round(total_price, 2),
                    discount_amount=round(discount_amount, 2),
                    transaction_id=f"TX-{current_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                )
                sales_records.append(sale)
    
    # Add batches of records to avoid memory issues
    batch_size = 100
    for i in range(0, len(sales_records), batch_size):
        batch = sales_records[i:i+batch_size]
        for sale in batch:
            db.session.add(sale)
        db.session.commit()
    
    # Create an admin user
    import werkzeug.security
    
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=werkzeug.security.generate_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True,
        last_login=datetime.now()
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    # Add system configuration
    configs = [
        SystemConfig(
            key="inventory_low_threshold_percent",
            value="20",
            description="Percentage below reorder point to consider inventory critically low",
            value_type="int"
        ),
        SystemConfig(
            key="default_forecast_days",
            value="30",
            description="Default number of days for demand forecasting",
            value_type="int"
        ),
        SystemConfig(
            key="enable_price_optimization",
            value="true",
            description="Enable automatic price optimization suggestions",
            value_type="boolean"
        ),
        SystemConfig(
            key="competitor_price_tracking",
            value="true",
            description="Enable competitor price tracking",
            value_type="boolean"
        ),
        SystemConfig(
            key="llm_providers",
            value='["openai", "ollama", "local_embedding"]',
            description="Configured LLM providers",
            value_type="json"
        )
    ]
    
    for config in configs:
        db.session.add(config)
    
    db.session.commit()
    
    logger.info("Sample data initialization complete")

# Initialize routes
def register_blueprints():
    """Register Flask blueprints for routes."""
    # Import routes at runtime to avoid circular imports
    from routes import register_routes
    register_routes(app)

# Flask application setup
def setup_application():
    """Set up the application before the first request."""
    try:
        # Create database tables
        with app.app_context():
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