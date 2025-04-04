"""
Data loader for the AI Inventory Optimization System.

This module handles loading CSV data files into the system for the three main data types:
1. Demand forecasting data
2. Inventory monitoring data 
3. Pricing optimization data

Each CSV file is mapped to the appropriate data structures and used by the respective
optimization algorithms.
"""

import os
import csv
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from models import Product, Store, InventoryRecord, PredictionLog, AgentAction, db
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Define paths to CSV files
DATA_DIR = 'attached_assets'
DEMAND_CSV = os.path.join(DATA_DIR, 'demand_forecasting.csv')
INVENTORY_CSV = os.path.join(DATA_DIR, 'inventory_monitoring.csv')
PRICING_CSV = os.path.join(DATA_DIR, 'pricing_optimization.csv')

def load_sample_data():
    """
    Load sample data from CSV files into the database.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load products and stores
        load_product_store_data()
        
        # Load inventory records
        load_inventory_records()
        
        logger.info("Sample data loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return False

def load_product_store_data():
    """
    Load product and store data from CSV files.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if any products exist
        if db.session.query(Product).first():
            logger.info("Products already exist, skipping product load")
            return True
        
        # Sample product data
        products = [
            {"name": "Premium Coffee Beans", "category": "Beverages", "base_price": 14.99},
            {"name": "Organic Whole Milk", "category": "Dairy", "base_price": 3.49},
            {"name": "Artisan Bread", "category": "Bakery", "base_price": 4.99},
            {"name": "Fresh Apples", "category": "Produce", "base_price": 1.99},
            {"name": "Grass-Fed Ground Beef", "category": "Meat", "base_price": 8.99},
            {"name": "Sparkling Water", "category": "Beverages", "base_price": 1.29},
            {"name": "Organic Eggs", "category": "Dairy", "base_price": 5.49},
            {"name": "Premium Potato Chips", "category": "Snacks", "base_price": 3.99},
            {"name": "Gourmet Chocolate", "category": "Confectionery", "base_price": 7.99},
            {"name": "Frozen Pizza", "category": "Frozen Foods", "base_price": 6.99}
        ]
        
        # Sample store data
        stores = [
            {"name": "Downtown Market", "location": "123 Main St, City Center"},
            {"name": "Suburban Plaza", "location": "456 Oak Ave, Westview"},
            {"name": "Neighborhood Express", "location": "789 Pine St, Eastside"},
            {"name": "University Store", "location": "321 College Rd, Campus Area"},
            {"name": "Beachfront Mart", "location": "654 Shore Dr, Oceanview"}
        ]
        
        # Add products to database
        for product_data in products:
            product = Product(**product_data)
            db.session.add(product)
        
        # Add stores to database
        for store_data in stores:
            store = Store(**store_data)
            db.session.add(store)
        
        db.session.commit()
        logger.info(f"Added {len(products)} products and {len(stores)} stores")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading product and store data: {str(e)}")
        return False

def load_inventory_records():
    """
    Load inventory records from CSV files.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if any inventory records exist
        if db.session.query(InventoryRecord).first():
            logger.info("Inventory records already exist, skipping inventory record load")
            return True
        
        # Get all products and stores
        products = db.session.query(Product).all()
        stores = db.session.query(Store).all()
        
        # Generate initial inventory for each product at each store
        for product in products:
            for store in stores:
                # Generate a random initial inventory between 10 and 100
                import random
                quantity = random.randint(10, 100)
                
                record = InventoryRecord(
                    product_id=product.id,
                    store_id=store.id,
                    quantity=quantity,
                    last_updated=datetime.now()
                )
                db.session.add(record)
        
        db.session.commit()
        logger.info(f"Added inventory records for {len(products)} products across {len(stores)} stores")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading inventory records: {str(e)}")
        return False

def load_demand_data():
    """
    Load demand forecasting data from CSV file.
    
    Returns:
        pandas.DataFrame: DataFrame with demand data, or None if error
    """
    try:
        if not os.path.exists(DEMAND_CSV):
            logger.warning(f"Demand data file not found: {DEMAND_CSV}")
            return None
        
        df = pd.read_csv(DEMAND_CSV)
        logger.info(f"Loaded demand data: {len(df)} rows")
        return df
    
    except Exception as e:
        logger.error(f"Error loading demand data: {str(e)}")
        return None

def load_inventory_data():
    """
    Load inventory monitoring data from CSV file.
    
    Returns:
        pandas.DataFrame: DataFrame with inventory data, or None if error
    """
    try:
        if not os.path.exists(INVENTORY_CSV):
            logger.warning(f"Inventory data file not found: {INVENTORY_CSV}")
            return None
        
        df = pd.read_csv(INVENTORY_CSV)
        logger.info(f"Loaded inventory data: {len(df)} rows")
        return df
    
    except Exception as e:
        logger.error(f"Error loading inventory data: {str(e)}")
        return None

def load_pricing_data():
    """
    Load pricing optimization data from CSV file.
    
    Returns:
        pandas.DataFrame: DataFrame with pricing data, or None if error
    """
    try:
        if not os.path.exists(PRICING_CSV):
            logger.warning(f"Pricing data file not found: {PRICING_CSV}")
            return None
        
        df = pd.read_csv(PRICING_CSV)
        logger.info(f"Loaded pricing data: {len(df)} rows")
        return df
    
    except Exception as e:
        logger.error(f"Error loading pricing data: {str(e)}")
        return None

def get_demand_metrics(product_id, store_id):
    """
    Get demand metrics for a specific product and store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        
    Returns:
        dict: Dictionary with demand metrics
    """
    try:
        # Load demand data
        demand_df = load_demand_data()
        if demand_df is None:
            return None
        
        # Filter for the specific product and store
        filtered_df = demand_df[(demand_df['product_id'] == product_id) & (demand_df['store_id'] == store_id)]
        
        if filtered_df.empty:
            logger.warning(f"No demand data found for product {product_id} at store {store_id}")
            return None
        
        # Extract metrics (adjust column names based on actual CSV structure)
        metrics = {
            "avg_daily_sales": filtered_df['avg_daily_sales'].values[0],
            "sales_trend": filtered_df['sales_trend'].values[0],
            "seasonality_factor": filtered_df['seasonality_factor'].values[0],
            "promotion_effect": filtered_df['promotion_effect'].values[0],
            "price_elasticity": filtered_df['price_elasticity'].values[0],
            "competitor_impact": filtered_df['competitor_impact'].values[0]
        }
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting demand metrics: {str(e)}")
        return None

def get_inventory_metrics(product_id, store_id):
    """
    Get inventory metrics for a specific product and store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        
    Returns:
        dict: Dictionary with inventory metrics
    """
    try:
        # Load inventory data
        inventory_df = load_inventory_data()
        if inventory_df is None:
            return None
        
        # Filter for the specific product and store
        filtered_df = inventory_df[(inventory_df['product_id'] == product_id) & (inventory_df['store_id'] == store_id)]
        
        if filtered_df.empty:
            logger.warning(f"No inventory data found for product {product_id} at store {store_id}")
            return None
        
        # Extract metrics (adjust column names based on actual CSV structure)
        metrics = {
            "lead_time": filtered_df['lead_time'].values[0],
            "holding_cost": filtered_df['holding_cost'].values[0],
            "stockout_cost": filtered_df['stockout_cost'].values[0],
            "reorder_point": filtered_df['reorder_point'].values[0],
            "safety_stock": filtered_df['safety_stock'].values[0],
            "min_order_qty": filtered_df['min_order_qty'].values[0]
        }
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting inventory metrics: {str(e)}")
        return None

def get_pricing_metrics(product_id, store_id):
    """
    Get pricing metrics for a specific product and store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        
    Returns:
        dict: Dictionary with pricing metrics
    """
    try:
        # Load pricing data
        pricing_df = load_pricing_data()
        if pricing_df is None:
            return None
        
        # Filter for the specific product and store
        filtered_df = pricing_df[(pricing_df['product_id'] == product_id) & (pricing_df['store_id'] == store_id)]
        
        if filtered_df.empty:
            logger.warning(f"No pricing data found for product {product_id} at store {store_id}")
            return None
        
        # Extract metrics (adjust column names based on actual CSV structure)
        metrics = {
            "min_price": filtered_df['min_price'].values[0],
            "max_price": filtered_df['max_price'].values[0],
            "competitor_price": filtered_df['competitor_price'].values[0],
            "elasticity": filtered_df['elasticity'].values[0],
            "margin_target": filtered_df['margin_target'].values[0],
            "promotion_discount": filtered_df['promotion_discount'].values[0]
        }
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting pricing metrics: {str(e)}")
        return None

def generate_historical_sales_data(product_id, store_id, days=90):
    """
    Generate historical sales data for a product at a store.
    
    Args:
        product_id: ID of the product
        store_id: ID of the store
        days: Number of days of historical data to generate
        
    Returns:
        List of dictionaries with date and sales data
    """
    try:
        # Get product and store
        product = db.session.query(Product).filter_by(id=product_id).first()
        store = db.session.query(Store).filter_by(id=store_id).first()
        
        if not product or not store:
            logger.warning(f"Product {product_id} or Store {store_id} not found")
            return []
        
        # Get demand metrics or use defaults
        metrics = get_demand_metrics(product_id, store_id)
        if not metrics:
            metrics = {
                "avg_daily_sales": 20,
                "sales_trend": 0.5,
                "seasonality_factor": 1.0,
                "promotion_effect": 0.2,
                "price_elasticity": -1.5,
                "competitor_impact": 0.1
            }
        
        # Generate historical data
        sales_data = []
        today = datetime.now()
        base_demand = metrics["avg_daily_sales"]
        trend = metrics["sales_trend"]
        seasonality_factor = metrics["seasonality_factor"]
        
        import numpy as np
        
        for i in range(days, 0, -1):
            day_offset = i
            hist_date = today - timedelta(days=day_offset)
            
            # Apply trend (percentage change per day)
            trend_factor = 1.0 - (trend * day_offset / 100)  # Reverse trend for historical data
            
            # Apply day-of-week seasonality
            day_of_week = hist_date.weekday()
            day_factor = 1.2 if day_of_week >= 5 else 1.0  # Higher sales on weekends
            
            # Apply month seasonality
            month = hist_date.month
            month_factor = 1.3 if month in [11, 12] else 1.0  # Higher sales in Nov, Dec
            
            # Apply random promotions
            promo_factor = 1.0
            if np.random.random() < 0.15:  # 15% chance of promotion on any day
                promo_factor = 1.0 + metrics["promotion_effect"]
            
            # Apply random noise
            noise = np.random.normal(1.0, 0.1)  # Random factor with mean 1.0 and std 0.1
            
            # Calculate sales
            sales = base_demand * trend_factor * day_factor * month_factor * seasonality_factor * promo_factor * noise
            
            # Ensure sales is positive
            sales = max(sales, 0)
            
            # Format date
            date_str = hist_date.strftime("%Y-%m-%d")
            
            sales_data.append({
                "date": date_str,
                "sales": round(sales, 1),
                "promotion": promo_factor > 1.0,
                "day_of_week": day_of_week,
                "month": month
            })
        
        return sales_data
    
    except Exception as e:
        logger.error(f"Error generating historical sales data: {str(e)}")
        return []