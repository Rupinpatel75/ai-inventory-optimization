"""
Models for the AI Inventory Optimization System.

This module defines the database models for the system, including
products, stores, inventory records, predictions, and agent actions.
"""

from datetime import datetime
from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey

class Product(db.Model):
    """Model representing a product in the inventory system."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    
    # Relationships
    inventory_records = relationship("InventoryRecord", back_populates="product")
    prediction_logs = relationship("PredictionLog", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name}>"


class Store(db.Model):
    """Model representing a physical store location."""
    __tablename__ = 'stores'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    
    # Relationships
    inventory_records = relationship("InventoryRecord", back_populates="store")
    prediction_logs = relationship("PredictionLog", back_populates="store")
    
    def __repr__(self):
        return f"<Store {self.name} ({self.location})>"


class InventoryRecord(db.Model):
    """Model representing the current inventory level of a product at a store."""
    __tablename__ = 'inventory_records'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_records")
    store = relationship("Store", back_populates="inventory_records")
    
    def __repr__(self):
        return f"<InventoryRecord {self.product_id} at {self.store_id}: {self.quantity}>"


class PredictionLog(db.Model):
    """Model logging demand predictions made by the system."""
    __tablename__ = 'prediction_logs'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    prediction_days = Column(Integer, nullable=False, default=30)
    avg_predicted_demand = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="prediction_logs")
    store = relationship("Store", back_populates="prediction_logs")
    
    def __repr__(self):
        return f"<PredictionLog {self.product_id} at {self.store_id}: {self.avg_predicted_demand}>"


class AgentAction(db.Model):
    """Model representing actions taken by AI agents in the system."""
    __tablename__ = 'agent_actions'

    id = Column(Integer, primary_key=True)
    agent_type = Column(String(50), nullable=False)  # 'demand', 'inventory', 'pricing'
    action = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=True)
    details = Column(Text, nullable=True)  # JSON string with action details
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    
    def __repr__(self):
        return f"<AgentAction {self.agent_type}: {self.action}>"