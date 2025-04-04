import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app import db
from models import Product, Store, InventoryRecord

logger = logging.getLogger(__name__)

def load_sample_data():
    """
    Load sample data into the database for demonstration purposes.
    Only loads data if the database is empty.
    
    Returns:
        Boolean indicating success
    """
    try:
        # Check if data already exists
        if Product.query.count() > 0:
            logger.info("Database already contains data, skipping sample data loading")
            return True
        
        # Add sample products
        products = [
            Product(name="Laptop", category="Electronics", base_price=899.99),
            Product(name="Smartphone", category="Electronics", base_price=599.99),
            Product(name="Headphones", category="Electronics", base_price=149.99),
            Product(name="T-shirt", category="Clothing", base_price=19.99),
            Product(name="Jeans", category="Clothing", base_price=39.99)
        ]
        db.session.add_all(products)
        db.session.flush()  # Flush to get IDs
        
        # Add sample stores
        stores = [
            Store(name="Main Street Store", location="New York"),
            Store(name="Downtown Branch", location="Los Angeles"),
            Store(name="Shopping Mall", location="Chicago")
        ]
        db.session.add_all(stores)
        db.session.flush()  # Flush to get IDs
        
        # Add sample inventory records
        inventory_records = []
        for product in products:
            for store in stores:
                # Generate a slightly different quantity for each product/store
                quantity = np.random.randint(20, 100)
                
                record = InventoryRecord(
                    product_id=product.id,
                    store_id=store.id,
                    quantity=quantity,
                    last_updated=datetime.now()
                )
                inventory_records.append(record)
        
        db.session.add_all(inventory_records)
        db.session.commit()
        
        logger.info(f"Successfully loaded sample data: {len(products)} products, {len(stores)} stores")
        return True
        
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        db.session.rollback()
        return False

def generate_historical_sales_data(days=90):
    """
    Generate historical sales data for model training purposes.
    
    Args:
        days: Number of days of historical data to generate
        
    Returns: 
        DataFrame with historical sales data
    """
    products = Product.query.all()
    stores = Store.query.all()
    
    if not products or not stores:
        logger.error("No products or stores in database")
        return None
    
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for product in products:
        for store in stores:
            # Create a base demand that's consistent for this product/store
            base_demand = (product.id * 7) + (store.id * 5)
            
            # Generate daily data
            current_date = start_date
            while current_date <= end_date:
                # Add weekly seasonality (higher on weekends)
                day_of_week = current_date.weekday()
                seasonal_factor = 1.3 if day_of_week >= 5 else 1.0
                
                # Add monthly trend (increasing sales over time)
                days_since_start = (current_date - start_date).days
                trend_factor = 1.0 + (days_since_start * 0.001)
                
                # Add some randomness
                noise = np.random.normal(1.0, 0.2)
                
                # Calculate sales quantity
                quantity = round(base_demand * seasonal_factor * trend_factor * noise)
                quantity = max(0, quantity)  # Ensure non-negative
                
                data.append({
                    'date': current_date,
                    'product_id': product.id,
                    'product_name': product.name,
                    'store_id': store.id,
                    'store_name': store.name,
                    'quantity': quantity
                })
                
                current_date += timedelta(days=1)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    logger.info(f"Generated {len(df)} historical sales records for {len(products)} products across {len(stores)} stores")
    return df
