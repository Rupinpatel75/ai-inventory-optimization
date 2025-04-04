import logging
import random
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

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
    # Check if we already have data
    if Product.query.count() > 0:
        logger.info("Database already contains data, skipping sample data load")
        return True
    
    try:
        # Add sample products
        products = [
            Product(name="T-Shirt Basic", category="Apparel", base_price=19.99),
            Product(name="Premium Jeans", category="Apparel", base_price=59.99),
            Product(name="Smartphone X", category="Electronics", base_price=699.99),
            Product(name="Wireless Earbuds", category="Electronics", base_price=129.99),
            Product(name="Coffee Maker", category="Home Goods", base_price=89.99),
            Product(name="Blender Pro", category="Home Goods", base_price=49.99),
            Product(name="Running Shoes", category="Footwear", base_price=79.99),
            Product(name="Casual Sneakers", category="Footwear", base_price=49.99),
            Product(name="Vitamin C Serum", category="Health & Beauty", base_price=24.99),
            Product(name="Moisturizing Cream", category="Health & Beauty", base_price=15.99)
        ]
        
        db.session.add_all(products)
        db.session.commit()
        logger.info(f"Added {len(products)} sample products")
        
        # Add sample stores
        stores = [
            Store(name="Downtown Store", location="123 Main St, Downtown"),
            Store(name="Westside Mall", location="456 West Blvd, Westside"),
            Store(name="Eastside Plaza", location="789 East Ave, Eastside"),
            Store(name="Suburban Outlet", location="101 Suburb Rd, Suburbia")
        ]
        
        db.session.add_all(stores)
        db.session.commit()
        logger.info(f"Added {len(stores)} sample stores")
        
        # Add sample inventory
        inventory_records = []
        
        for product in products:
            for store in stores:
                # Random inventory levels
                inventory_records.append(
                    InventoryRecord(
                        product_id=product.id,
                        store_id=store.id,
                        quantity=random.randint(5, 100),
                        last_updated=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
                )
        
        db.session.add_all(inventory_records)
        db.session.commit()
        logger.info(f"Added {len(inventory_records)} sample inventory records")
        
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
    # Get all products and stores
    products = Product.query.all()
    stores = Store.query.all()
    
    if not products or not stores:
        logger.warning("No products or stores found for generating historical data")
        return pd.DataFrame()
    
    # Prepare data structure
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate sales data for each product at each store
    for product in products:
        for store in stores:
            # Get current inventory as a reference point
            inventory_record = InventoryRecord.query.filter_by(
                product_id=product.id,
                store_id=store.id
            ).first()
            
            avg_daily_sales = random.randint(2, 10)  # Base average daily sales
            
            # Generate daily sales with variations
            current_date = start_date
            while current_date <= end_date:
                # Daily, weekly, and seasonal patterns
                day_of_week = current_date.weekday()
                week_of_year = current_date.isocalendar()[1]
                
                # Weekend boost
                day_factor = 1.5 if day_of_week >= 5 else 1.0
                
                # Seasonal variations (simplified)
                month = current_date.month
                if month in [11, 12]:  # Holiday season
                    seasonal_factor = 1.3
                elif month in [6, 7, 8]:  # Summer
                    seasonal_factor = 1.2 if product.category in ["Apparel", "Footwear"] else 1.0
                else:
                    seasonal_factor = 1.0
                
                # Product-specific trend
                trend_factor = 1.0 + (0.001 * (current_date - start_date).days)
                
                # Random noise
                noise = random.uniform(0.7, 1.3)
                
                # Calculate sales
                sales = round(avg_daily_sales * day_factor * seasonal_factor * trend_factor * noise)
                
                data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'product_id': product.id,
                    'product_name': product.name,
                    'store_id': store.id,
                    'store_name': store.name,
                    'sales': sales,
                    'price': product.base_price
                })
                
                current_date += timedelta(days=1)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    logger.info(f"Generated historical sales data: {len(df)} records")
    
    return df

def load_external_data(data_path):
    """
    Load external data from CSV files.
    
    Args:
        data_path: Path to the data file
        
    Returns:
        DataFrame with loaded data
    """
    try:
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            logger.info(f"Loaded external data from {data_path}: {len(df)} records")
            return df
        else:
            logger.warning(f"Data file not found: {data_path}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading external data: {str(e)}")
        return pd.DataFrame()