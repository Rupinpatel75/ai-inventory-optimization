"""
Database models for the AI Inventory Optimization System.

This module defines all database models for the application, including products,
stores, inventory, sales, and agent logs.
"""

import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from app import db

class User(db.Model):
    """User model for authentication and permissions."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # admin, user, manager, analyst
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Product(db.Model):
    """Product model for storing product information."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    base_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))  # format: LxWxH
    min_stock_level = db.Column(db.Integer, default=10)
    lead_time_days = db.Column(db.Integer, default=7)  # typical reorder lead time
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    inventory = relationship("Inventory", back_populates="product")
    sales = relationship("Sale", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    promotions = relationship("Promotion", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name}>"

class Supplier(db.Model):
    """Supplier model for storing supplier information."""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    lead_time_days = db.Column(db.Integer)  # average lead time for orders
    reliability_score = db.Column(db.Float)  # 0-1 score based on past performance
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    products = relationship("Product", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier {self.name}>"

class Store(db.Model):
    """Store model for storing store/location information."""
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    store_type = db.Column(db.String(50))  # warehouse, retail, online
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    manager_name = db.Column(db.String(100))
    size_sqft = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    inventory = relationship("Inventory", back_populates="store")
    sales = relationship("Sale", back_populates="store")
    
    def __repr__(self):
        return f"<Store {self.name}>"

class Inventory(db.Model):
    """Inventory model for storing current inventory levels."""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer)
    reorder_quantity = db.Column(db.Integer)
    last_restock_date = db.Column(db.DateTime)
    last_count_date = db.Column(db.DateTime)
    shelf_location = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    store = relationship("Store", back_populates="inventory")
    
    def __repr__(self):
        return f"<Inventory {self.product_id} at {self.store_id}>"

class Sale(db.Model):
    """Sale model for storing sales transactions."""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0)
    transaction_id = db.Column(db.String(50))
    customer_id = db.Column(db.String(50))
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    store = relationship("Store", back_populates="sales")
    promotion = relationship("Promotion")
    
    def __repr__(self):
        return f"<Sale {self.id} on {self.date}>"

class Forecast(db.Model):
    """Forecast model for storing demand forecasts."""
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    forecast_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    confidence_level = db.Column(db.Float)  # 0-1 confidence in the forecast
    forecast_method = db.Column(db.String(50))
    created_by = db.Column(db.String(50))  # agent or user
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="forecasts")
    
    def __repr__(self):
        return f"<Forecast for {self.product_id} at {self.store_id} on {self.forecast_date}>"

class AgentLog(db.Model):
    """Log model for storing agent actions and recommendations."""
    __tablename__ = 'agent_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)  # demand, inventory, pricing
    action = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    details = db.Column(db.Text)  # JSON string of action details
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product")
    store = relationship("Store")
    user = relationship("User")
    
    def get_details_dict(self):
        """Parse the details JSON string into a dictionary."""
        if self.details:
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def __repr__(self):
        return f"<AgentLog {self.agent_type} - {self.action}>"

class PriceHistory(db.Model):
    """Price history model for tracking product price changes."""
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    change_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    reason = db.Column(db.String(200))
    changed_by = db.Column(db.String(50))  # agent or user
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory for {self.product_id} on {self.change_date}>"

class Promotion(db.Model):
    """Promotion model for storing promotional campaigns."""
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    discount_type = db.Column(db.String(20))  # percentage, fixed amount
    discount_value = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="promotions")
    
    def __repr__(self):
        return f"<Promotion {self.name}>"

class CompetitorPrice(db.Model):
    """Competitor price model for storing competitor pricing information."""
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    competitor_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_observed = db.Column(db.DateTime, default=datetime.now, nullable=False)
    url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    # Relationships
    product = relationship("Product")
    
    def __repr__(self):
        return f"<CompetitorPrice for {self.product_id} from {self.competitor_name}>"

class DataImport(db.Model):
    """Data import model for tracking imports of external data."""
    __tablename__ = 'data_imports'
    
    id = db.Column(db.Integer, primary_key=True)
    import_type = db.Column(db.String(50), nullable=False)  # products, sales, inventory
    source = db.Column(db.String(255), nullable=False)  # filename or source description
    status = db.Column(db.String(20), nullable=False)  # pending, processing, completed, failed
    records_processed = db.Column(db.Integer)
    records_succeeded = db.Column(db.Integer)
    records_failed = db.Column(db.Integer)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    imported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<DataImport {self.import_type} - {self.status}>"

class SystemConfig(db.Model):
    """System configuration model for storing system-wide settings."""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # string, int, float, boolean, json
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def get_typed_value(self):
        """Return the value converted to its specified type."""
        if self.value_type == 'int':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', 'yes', '1')
        elif self.value_type == 'json':
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        else:  # default to string
            return self.value
    
    def __repr__(self):
        return f"<SystemConfig {self.key}>"