"""
Data loader utility for the AI Inventory Optimization System.

This module provides functionality to load sample data for
demonstration and testing purposes, as well as importing
real data from external sources.
"""

import logging
import random
import json
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from models import Product, Store, InventoryRecord, PredictionLog, db

logger = logging.getLogger(__name__)

def load_sample_data():
    """
    Load sample data into the database.
    
    Returns:
        Boolean indicating success
    """
    try:
        # Check if data already exists
        if db.session.query(Product).count() > 0:
            logger.info("Sample data already loaded")
            return True
        
        # Create sample products
        products = [
            {"name": "Basic T-Shirt", "category": "Clothing", "base_price": 19.99},
            {"name": "Premium Denim Jeans", "category": "Clothing", "base_price": 49.99},
            {"name": "Wireless Headphones", "category": "Electronics", "base_price": 79.99},
            {"name": "Smart Fitness Tracker", "category": "Electronics", "base_price": 129.99},
            {"name": "Organic Coffee Beans", "category": "Groceries", "base_price": 12.99},
            {"name": "Protein Bars (Box of 12)", "category": "Groceries", "base_price": 15.99},
            {"name": "Ergonomic Office Chair", "category": "Furniture", "base_price": 199.99},
            {"name": "Wooden Coffee Table", "category": "Furniture", "base_price": 249.99},
            {"name": "Professional Chef's Knife", "category": "Kitchen", "base_price": 89.99},
            {"name": "Non-Stick Cookware Set", "category": "Kitchen", "base_price": 149.99}
        ]
        
        # Create sample stores
        stores = [
            {"name": "Downtown Flagship", "location": "New York City"},
            {"name": "Westfield Mall", "location": "Los Angeles"},
            {"name": "Lakefront Center", "location": "Chicago"},
            {"name": "Tech Hub Store", "location": "San Francisco"},
            {"name": "Southern Outlet", "location": "Atlanta"}
        ]
        
        # Add products to database
        product_objs = []
        for p in products:
            product = Product(name=p["name"], category=p["category"], base_price=p["base_price"])
            db.session.add(product)
            product_objs.append(product)
        
        # Add stores to database
        store_objs = []
        for s in stores:
            store = Store(name=s["name"], location=s["location"])
            db.session.add(store)
            store_objs.append(store)
        
        db.session.commit()
        
        # Create inventory records with random quantities
        for product in product_objs:
            for store in store_objs:
                quantity = random.randint(10, 100)
                inventory = InventoryRecord(
                    product_id=product.id,
                    store_id=store.id,
                    quantity=quantity,
                    last_updated=datetime.now()
                )
                db.session.add(inventory)
        
        # Create some prediction logs
        for product in product_objs[:5]:  # Only for some products
            for store in store_objs[:3]:  # Only for some stores
                avg_predicted = random.uniform(5, 30)
                prediction = PredictionLog(
                    product_id=product.id,
                    store_id=store.id,
                    prediction_days=30,
                    avg_predicted_demand=avg_predicted,
                    timestamp=datetime.now() - timedelta(days=random.randint(1, 7))
                )
                db.session.add(prediction)
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Loaded {len(products)} products, {len(stores)} stores")
        logger.info(f"Created {len(products) * len(stores)} inventory records")
        logger.info("Sample data loaded successfully")
        
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading sample data: {str(e)}")
        return False

def import_csv_data(file_path, data_type):
    """
    Import data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        data_type: Type of data ('products', 'stores', or 'inventory')
        
    Returns:
        Dictionary with import results
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Read CSV file
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                data.append(row)
        
        if not data:
            return {"error": "CSV file is empty or improperly formatted"}
        
        # Process data based on type
        if data_type == 'products':
            return import_products(data)
        elif data_type == 'stores':
            return import_stores(data)
        elif data_type == 'inventory':
            return import_inventory(data)
        else:
            return {"error": f"Unknown data type: {data_type}"}
    
    except Exception as e:
        logger.error(f"Error importing CSV data: {str(e)}")
        return {"error": f"Failed to import CSV data: {str(e)}"}

def import_products(data):
    """
    Import product data.
    
    Args:
        data: List of dictionaries with product data
        
    Returns:
        Dictionary with import results
    """
    try:
        products_added = 0
        products_updated = 0
        errors = []
        
        for item in data:
            try:
                # Check for required fields
                if 'name' not in item or 'category' not in item or 'base_price' not in item:
                    errors.append(f"Missing required fields for product: {item}")
                    continue
                
                # Convert price to float
                try:
                    base_price = float(item['base_price'])
                except ValueError:
                    errors.append(f"Invalid base price for product: {item}")
                    continue
                
                # Check if product already exists
                existing = db.session.query(Product).filter_by(name=item['name']).first()
                
                if existing:
                    # Update existing product
                    existing.category = item['category']
                    existing.base_price = base_price
                    products_updated += 1
                else:
                    # Create new product
                    product = Product(
                        name=item['name'],
                        category=item['category'],
                        base_price=base_price
                    )
                    db.session.add(product)
                    products_added += 1
            
            except Exception as e:
                errors.append(f"Error processing product {item.get('name', 'unknown')}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return {
            "products_added": products_added,
            "products_updated": products_updated,
            "errors": errors,
            "success": True
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing products: {str(e)}")
        return {"error": f"Failed to import products: {str(e)}"}

def import_stores(data):
    """
    Import store data.
    
    Args:
        data: List of dictionaries with store data
        
    Returns:
        Dictionary with import results
    """
    try:
        stores_added = 0
        stores_updated = 0
        errors = []
        
        for item in data:
            try:
                # Check for required fields
                if 'name' not in item or 'location' not in item:
                    errors.append(f"Missing required fields for store: {item}")
                    continue
                
                # Check if store already exists
                existing = db.session.query(Store).filter_by(name=item['name']).first()
                
                if existing:
                    # Update existing store
                    existing.location = item['location']
                    stores_updated += 1
                else:
                    # Create new store
                    store = Store(
                        name=item['name'],
                        location=item['location']
                    )
                    db.session.add(store)
                    stores_added += 1
            
            except Exception as e:
                errors.append(f"Error processing store {item.get('name', 'unknown')}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return {
            "stores_added": stores_added,
            "stores_updated": stores_updated,
            "errors": errors,
            "success": True
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing stores: {str(e)}")
        return {"error": f"Failed to import stores: {str(e)}"}

def import_inventory(data):
    """
    Import inventory data.
    
    Args:
        data: List of dictionaries with inventory data
        
    Returns:
        Dictionary with import results
    """
    try:
        records_added = 0
        records_updated = 0
        errors = []
        
        for item in data:
            try:
                # Check for required fields
                if 'product_id' not in item or 'store_id' not in item or 'quantity' not in item:
                    errors.append(f"Missing required fields for inventory: {item}")
                    continue
                
                # Convert IDs and quantity to integers
                try:
                    product_id = int(item['product_id'])
                    store_id = int(item['store_id'])
                    quantity = int(item['quantity'])
                except ValueError:
                    errors.append(f"Invalid numeric values for inventory: {item}")
                    continue
                
                # Check if product and store exist
                product = db.session.query(Product).filter_by(id=product_id).first()
                store = db.session.query(Store).filter_by(id=store_id).first()
                
                if not product:
                    errors.append(f"Product ID {product_id} not found")
                    continue
                
                if not store:
                    errors.append(f"Store ID {store_id} not found")
                    continue
                
                # Check if inventory record already exists
                existing = db.session.query(InventoryRecord).filter_by(
                    product_id=product_id, store_id=store_id
                ).first()
                
                if existing:
                    # Update existing record
                    existing.quantity = quantity
                    existing.last_updated = datetime.now()
                    records_updated += 1
                else:
                    # Create new inventory record
                    record = InventoryRecord(
                        product_id=product_id,
                        store_id=store_id,
                        quantity=quantity,
                        last_updated=datetime.now()
                    )
                    db.session.add(record)
                    records_added += 1
            
            except Exception as e:
                errors.append(f"Error processing inventory record: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return {
            "records_added": records_added,
            "records_updated": records_updated,
            "errors": errors,
            "success": True
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing inventory: {str(e)}")
        return {"error": f"Failed to import inventory: {str(e)}"}

def generate_historical_sales_data(product_id, store_id, days=365, output_file=None):
    """
    Generate synthetic historical sales data for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days of historical data to generate
        output_file: Optional file path to save data as CSV
        
    Returns:
        DataFrame with synthetic sales data
    """
    try:
        # Get product and store details
        product = db.session.query(Product).filter_by(id=product_id).first()
        store = db.session.query(Store).filter_by(id=store_id).first()
        
        if not product or not store:
            logger.error(f"Product {product_id} or store {store_id} not found")
            return None
        
        # Set random seed for reproducibility
        random.seed(product_id * 1000 + store_id)
        
        # Generate base parameters
        base_demand = random.uniform(10, 100)  # Base daily demand
        trend = random.uniform(-0.0005, 0.001)  # Small daily trend
        yearly_seasonality = random.uniform(0.1, 0.3)  # Yearly seasonal variation
        weekly_seasonality = random.uniform(0.1, 0.3)  # Weekly seasonal variation
        price_elasticity = random.uniform(-2.0, -0.5)  # Price elasticity
        
        # Generate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        date_range = [start_date + timedelta(days=i) for i in range(days)]
        
        # Generate data
        sales_data = []
        
        for i, date in enumerate(date_range):
            # Calculate trend component
            trend_component = base_demand * (1 + trend * i)
            
            # Calculate yearly seasonality
            day_of_year = date.timetuple().tm_yday
            yearly_factor = 1 + yearly_seasonality * math.sin(day_of_year / 365 * 2 * math.pi)
            
            # Calculate weekly seasonality
            day_of_week = date.weekday()
            if day_of_week >= 5:  # Weekend
                weekly_factor = 1 + weekly_seasonality
            else:
                weekly_factor = 1 - (weekly_seasonality * 0.3)
            
            # Calculate price and promotion effects
            base_price = product.base_price
            
            # Occasionally have a promotion
            has_promotion = random.random() < 0.1  # 10% chance of promotion
            discount_pct = random.uniform(0.1, 0.3) if has_promotion else 0
            actual_price = base_price * (1 - discount_pct)
            
            # Calculate price effect
            if discount_pct > 0:
                price_ratio = actual_price / base_price
                price_effect = price_ratio ** price_elasticity
            else:
                price_effect = 1
            
            # Calculate final demand
            demand = trend_component * yearly_factor * weekly_factor * price_effect
            
            # Add noise
            noise = random.normalvariate(1, 0.2)
            final_demand = max(0, demand * noise)
            
            # Round to whole units
            units_sold = round(final_demand)
            
            # Calculate sales amount
            sales_amount = units_sold * actual_price
            
            # Add to data
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product_id,
                'product_name': product.name,
                'store_id': store_id,
                'store_name': store.name,
                'units_sold': units_sold,
                'price': round(actual_price, 2),
                'base_price': round(base_price, 2),
                'discount_pct': round(discount_pct * 100, 1),
                'sales_amount': round(sales_amount, 2),
                'day_of_week': day_of_week,
                'has_promotion': has_promotion
            })
        
        # Create DataFrame
        df = pd.DataFrame(sales_data)
        
        # Save to CSV if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            logger.info(f"Saved sales data to {output_file}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error generating historical sales data: {str(e)}")
        return None