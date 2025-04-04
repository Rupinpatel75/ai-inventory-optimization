"""
Database models for the AI Inventory Optimization System.

This module defines all the SQLAlchemy models used in the application,
including Products, Stores, Inventory, Sales, etc.
"""

from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Boolean, JSON
from app import db

class Product(db.Model):
    """Product model representing items being sold."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)
    subcategory = Column(String(50))
    base_price = Column(Float, nullable=False, default=0.0)
    cost_price = Column(Float)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    inventory_records = relationship("Inventory", back_populates="product")
    sales_records = relationship("Sale", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"

class Store(db.Model):
    """Store model representing physical or online retail locations."""
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    postal_code = Column(String(20))
    region = Column(String(50), index=True)
    store_type = Column(String(50))  # physical, online, hybrid
    size = Column(Integer)  # in square feet/meters
    opened_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    # Relationships
    inventory_records = relationship("Inventory", back_populates="store")
    sales_records = relationship("Sale", back_populates="store")
    
    def __repr__(self):
        return f"<Store {self.id}: {self.name}>"

class Supplier(db.Model):
    """Supplier model representing product vendors."""
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_name = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(50))
    address = Column(String(200))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    postal_code = Column(String(20))
    lead_time_days = Column(Integer)  # average lead time in days
    reliability_score = Column(Float)  # 0-100 score
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    # Relationships
    products = relationship("Product", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier {self.id}: {self.name}>"

class Inventory(db.Model):
    """Inventory model tracking product stock at each store."""
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    quantity = Column(Integer, default=0)
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    last_restock_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_records")
    store = relationship("Store", back_populates="inventory_records")
    
    __table_args__ = (
        db.UniqueConstraint('product_id', 'store_id', name='uix_inventory_product_store'),
    )
    
    def __repr__(self):
        return f"<Inventory: {self.product_id} at {self.store_id}, qty: {self.quantity}>"

class Sale(db.Model):
    """Sale model recording individual product sales."""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    promotion_id = Column(Integer, ForeignKey('promotions.id'))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="sales_records")
    store = relationship("Store", back_populates="sales_records")
    promotion = relationship("Promotion")
    
    def __repr__(self):
        return f"<Sale {self.id}: {self.product_id} at {self.store_id}, qty: {self.quantity}>"

class PriceHistory(db.Model):
    """PriceHistory model tracking price changes for products."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    previous_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    change_date = Column(DateTime, nullable=False)
    change_reason = Column(String(200))
    changed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory {self.id}: {self.product_id}, {self.previous_price} -> {self.new_price}>"

class Promotion(db.Model):
    """Promotion model for tracking sales promotions."""
    __tablename__ = 'promotions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    discount_type = Column(String(50))  # percentage, fixed_amount, bogo, etc.
    discount_value = Column(Float)  # percentage or amount
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))  # for product-specific promotions
    category = Column(String(50))  # for category-wide promotions
    min_purchase_amount = Column(Float)
    min_purchase_quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Promotion {self.id}: {self.name}>"

class Forecast(db.Model):
    """Forecast model storing demand predictions."""
    __tablename__ = 'forecasts'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    forecast_date = Column(DateTime, nullable=False)  # date for which forecast is made
    forecast_quantity = Column(Float, nullable=False)  # predicted demand quantity
    confidence_level = Column(Float)  # confidence in prediction (0-1)
    forecast_method = Column(String(100))  # method used for forecasting
    forecast_period = Column(String(50))  # daily, weekly, monthly
    created_at = Column(DateTime, default=datetime.now)
    actual_quantity = Column(Float)  # actual demand, filled after the fact
    
    __table_args__ = (
        db.UniqueConstraint('product_id', 'store_id', 'forecast_date', 'forecast_period', 
                         name='uix_forecast_product_store_date_period'),
    )
    
    def __repr__(self):
        return f"<Forecast {self.id}: {self.product_id} at {self.store_id}, qty: {self.forecast_quantity}>"

class AgentLog(db.Model):
    """AgentLog model for tracking agent actions."""
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True)
    agent_type = Column(String(50), nullable=False, index=True)  # demand, inventory, pricing
    action = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    store_id = Column(Integer, ForeignKey('stores.id'))
    details = Column(Text)  # JSON-serialized details
    timestamp = Column(DateTime, nullable=False, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<AgentLog {self.id}: {self.agent_type} - {self.action}>"

class CompetitorPrice(db.Model):
    """CompetitorPrice model storing competitor pricing data."""
    __tablename__ = 'competitor_prices'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    competitor_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String(500))
    date_observed = Column(DateTime, nullable=False, default=datetime.now)
    active = Column(Boolean, default=True)
    
    __table_args__ = (
        db.UniqueConstraint('product_id', 'competitor_name', 'date_observed', 
                         name='uix_competitor_price_product_competitor_date'),
    )
    
    def __repr__(self):
        return f"<CompetitorPrice {self.id}: {self.product_id}, {self.competitor_name}, ${self.price}>"

class User(db.Model):
    """User model for application users."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))
    first_name = Column(String(64))
    last_name = Column(String(64))
    role = Column(String(50), default='user')  # user, admin, analyst
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User {self.id}: {self.username}>"

class SystemConfig(db.Model):
    """SystemConfig model for application configuration."""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(200))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(String(100))
    
    def __repr__(self):
        return f"<SystemConfig {self.id}: {self.key}>"

class DataImport(db.Model):
    """DataImport model for tracking data imports."""
    __tablename__ = 'data_imports'
    
    id = Column(Integer, primary_key=True)
    import_type = Column(String(50), nullable=False)  # products, sales, inventory, etc.
    source = Column(String(200))  # file name, API name, etc.
    status = Column(String(50), nullable=False)  # pending, in_progress, completed, failed
    records_processed = Column(Integer, default=0)
    records_succeeded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    error_message = Column(Text)
    metadata = Column(JSON)  # additional info about the import
    
    def __repr__(self):
        return f"<DataImport {self.id}: {self.import_type}, {self.status}>"