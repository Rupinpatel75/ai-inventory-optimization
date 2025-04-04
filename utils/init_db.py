"""
Database initialization utility for the AI Inventory Optimization System.

This module creates the base database tables with simplified schema
for compatibility with the CSV files, and provides functionality to
load data from the included CSV files.
"""

import os
import csv
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from app import db
from models_simplified import Product, Store, Inventory, AgentLog, User

logger = logging.getLogger(__name__)

def create_simplified_tables():
    """Create database tables compatible with the simplified CSV format."""
    
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        base_price FLOAT NOT NULL,
        category VARCHAR(50)
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(50) NOT NULL,
        location VARCHAR(255)
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS inventory (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id),
        store_id INTEGER NOT NULL REFERENCES stores(id),
        quantity INTEGER NOT NULL DEFAULT 0,
        reorder_point INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id SERIAL PRIMARY KEY,
        agent_type VARCHAR(50) NOT NULL,
        action VARCHAR(100) NOT NULL,
        product_id INTEGER REFERENCES products(id),
        store_id INTEGER REFERENCES stores(id),
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))
    
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))
    
    db.session.commit()
    logger.info("Created simplified database tables")

def import_demand_forecasting_data(file_path):
    """
    Import product and store data from demand_forecasting.csv
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        df = pd.read_csv(file_path)
        
        # Extract unique products and insert them
        products_df = df[['Product ID']].drop_duplicates()
        for _, row in products_df.iterrows():
            product_id = int(row['Product ID'])
            
            # Add some dummy data since CSV doesn't have all required fields
            product_name = f"Product {product_id}"
            category = "General"
            base_price = 50.0
            
            db.session.execute(
                text("INSERT INTO products (id, name, base_price, category) VALUES (:id, :name, :price, :category) ON CONFLICT (id) DO NOTHING"),
                {"id": product_id, "name": product_name, "price": base_price, "category": category}
            )
        
        # Extract unique stores and insert them
        stores_df = df[['Store ID']].drop_duplicates()
        for _, row in stores_df.iterrows():
            store_id = int(row['Store ID'])
            
            # Add some dummy data since CSV doesn't have all required fields
            store_name = f"Store {store_id}"
            store_code = f"ST{store_id:03d}"
            
            db.session.execute(
                text("INSERT INTO stores (id, name, code, location) VALUES (:id, :name, :code, :location) ON CONFLICT (id) DO NOTHING"),
                {"id": store_id, "name": store_name, "code": store_code, "location": "Main Location"}
            )
        
        db.session.commit()
        logger.info(f"Imported products and stores from {file_path}")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing data from {file_path}: {e}")
        return False

def import_inventory_data(file_path):
    """
    Import inventory data from inventory_monitoring.csv
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            product_id = int(row['Product ID'])
            store_id = int(row['Store ID'])
            quantity = int(row['Stock Levels'])
            reorder_point = int(row['Reorder Point'])
            
            # Check if product and store exist
            product_exists = db.session.execute(
                text("SELECT 1 FROM products WHERE id = :id"), 
                {"id": product_id}
            ).scalar()
            
            store_exists = db.session.execute(
                text("SELECT 1 FROM stores WHERE id = :id"), 
                {"id": store_id}
            ).scalar()
            
            if not product_exists:
                # Create placeholder product
                db.session.execute(
                    text("INSERT INTO products (id, name, base_price, category) VALUES (:id, :name, :price, :category)"),
                    {"id": product_id, "name": f"Product {product_id}", "price": 50.0, "category": "General"}
                )
            
            if not store_exists:
                # Create placeholder store
                db.session.execute(
                    text("INSERT INTO stores (id, name, code, location) VALUES (:id, :name, :code, :location)"),
                    {"id": store_id, "name": f"Store {store_id}", "code": f"ST{store_id:03d}", "location": "Main Location"}
                )
            
            # Insert or update inventory
            db.session.execute(
                text("""
                INSERT INTO inventory (product_id, store_id, quantity, reorder_point)
                VALUES (:product_id, :store_id, :quantity, :reorder_point)
                ON CONFLICT (product_id, store_id) DO UPDATE 
                SET quantity = :quantity, reorder_point = :reorder_point
                """), 
                {
                    "product_id": product_id, 
                    "store_id": store_id, 
                    "quantity": quantity, 
                    "reorder_point": reorder_point
                }
            )
        
        db.session.commit()
        logger.info(f"Imported inventory data from {file_path}")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing inventory data from {file_path}: {e}")
        return False

def create_default_admin_user():
    """Create a default admin user for the system."""
    try:
        # Check if user already exists
        admin_exists = db.session.execute(
            text("SELECT 1 FROM users WHERE username = :username"), 
            {"username": "admin"}
        ).scalar()
        
        if not admin_exists:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash("admin123")
            
            db.session.execute(
                text("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (:username, :email, :password_hash, :role)
                """),
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password_hash": password_hash,
                    "role": "admin"
                }
            )
            
            db.session.commit()
            logger.info("Created default admin user")
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating default admin user: {e}")
        return False

def initialize_database():
    """Initialize the database with tables and sample data."""
    try:
        # Create tables
        create_simplified_tables()
        
        # Import data from CSV files
        import_demand_forecasting_data("attached_assets/demand_forecasting.csv")
        import_inventory_data("attached_assets/inventory_monitoring.csv")
        
        # Create admin user
        create_default_admin_user()
        
        logger.info("Database initialization completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    # For manual execution
    initialize_database()