"""
Simplified database models for the AI Inventory Optimization System.

This file defines the database models compatible with the CSV data structure
used in the AI Inventory Optimization System. These models are simplified
versions of the full models described in models.py.
"""

from datetime import datetime
from app import db

class Product(db.Model):
    """Product model with simplified structure for CSV data."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    
    # Relationships
    inventory_items = db.relationship('Inventory', back_populates='product')
    agent_logs = db.relationship('AgentLog', back_populates='product')
    
    def __repr__(self):
        return f"<Product {self.name}>"

class Store(db.Model):
    """Store model with simplified structure for CSV data."""
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255))
    
    # Relationships
    inventory_items = db.relationship('Inventory', back_populates='store')
    agent_logs = db.relationship('AgentLog', back_populates='store')
    
    def __repr__(self):
        return f"<Store {self.name}>"

class Inventory(db.Model):
    """Inventory model with simplified structure for CSV data."""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    reorder_point = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    product = db.relationship('Product', back_populates='inventory_items')
    store = db.relationship('Store', back_populates='inventory_items')
    
    def __repr__(self):
        return f"<Inventory product_id={self.product_id} store_id={self.store_id}>"

class AgentLog(db.Model):
    """Agent log model for storing AI agent actions and recommendations."""
    __tablename__ = 'agent_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)  # demand, inventory, pricing
    action = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    details = db.Column(db.Text)  # JSON string of action details
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    product = db.relationship('Product', back_populates='agent_logs')
    store = db.relationship('Store', back_populates='agent_logs')
    
    def __repr__(self):
        return f"<AgentLog {self.agent_type} - {self.action}>"

class User(db.Model):
    """User model for authentication and permissions with simplified structure."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user, manager, analyst
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User {self.username}>"