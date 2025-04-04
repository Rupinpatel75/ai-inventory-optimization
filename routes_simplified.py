"""
Simplified route definitions for the AI Inventory Optimization System.

This module defines HTTP routes and views using the simplified models.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from app import db
from models_simplified import Product, Store, Inventory, AgentLog, User

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask application."""
    
    # Home and dashboard routes
    @app.route('/')
    def index():
        """Render the home page."""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Render the main dashboard."""
        # Get counts for the dashboard
        product_count = db.session.query(Product).count()
        store_count = db.session.query(Store).count()
        inventory_count = db.session.query(Inventory).count()
        
        # Get recent agent logs
        recent_logs = db.session.query(AgentLog).order_by(
            AgentLog.timestamp.desc()
        ).limit(10).all()
        
        # Get total inventory value
        inventory_value_query = db.session.query(
            db.func.sum(Product.base_price * Inventory.quantity)
        ).join(
            Inventory, Product.id == Inventory.product_id
        ).scalar()
        
        total_inventory_value = inventory_value_query or 0
        
        # Get low stock items
        low_stock_items = db.session.query(
            Product, Inventory, Store
        ).join(
            Inventory, Product.id == Inventory.product_id
        ).join(
            Store, Store.id == Inventory.store_id
        ).filter(
            Inventory.quantity <= Inventory.reorder_point
        ).limit(10).all()
        
        return render_template(
            'dashboard.html',
            product_count=product_count,
            store_count=store_count,
            inventory_count=inventory_count,
            supplier_count=0,  # Not in simplified model
            recent_logs=recent_logs,
            total_inventory_value=total_inventory_value,
            low_stock_items=low_stock_items
        )
    
    # Agent logs route
    @app.route('/logs')
    def agent_logs():
        """Display agent logs."""
        # Filter parameters
        agent_type = request.args.get('agent_type')
        days = request.args.get('days', 7, type=int)
        
        # Base query
        query = db.session.query(AgentLog)
        
        # Apply filters
        if agent_type:
            query = query.filter(AgentLog.agent_type == agent_type)
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(AgentLog.timestamp >= cutoff_date)
        
        # Execute query with ordering
        logs = query.order_by(AgentLog.timestamp.desc()).all()
        
        return render_template(
            'logs.html',
            logs=logs,
            agent_type=agent_type,
            days=days
        )
    
    # API routes for agents
    @app.route('/api/agents/demand/forecast', methods=['POST'])
    def demand_forecast_api():
        """API endpoint for demand forecasting."""
        try:
            data = request.json
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            days = data.get('days', 30)
            
            # In a real application, this would call the demand agent
            # For now, we'll just return a placeholder response
            forecast_data = {
                'product_id': product_id,
                'store_id': store_id,
                'forecast_period': f"{days} days",
                'forecast_quantity': 150,
                'confidence_level': 0.85,
                'forecast_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Log the action
            log_entry = AgentLog(
                agent_type="demand",
                action="forecast_demand",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps(forecast_data),
                timestamp=datetime.now()
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'forecast': forecast_data
            })
            
        except Exception as e:
            logger.error(f"Error in demand forecast API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/agents/inventory/optimize', methods=['POST'])
    def inventory_optimize_api():
        """API endpoint for inventory optimization."""
        try:
            data = request.json
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            
            # In a real application, this would call the inventory agent
            # For now, we'll just return a placeholder response
            optimization_data = {
                'product_id': product_id,
                'store_id': store_id,
                'current_quantity': 75,
                'optimal_quantity': 120,
                'reorder_point': 30,
                'reorder_quantity': 60,
                'stockout_risk': 0.15,
                'recommendation': 'Increase inventory by 45 units'
            }
            
            # Log the action
            log_entry = AgentLog(
                agent_type="inventory",
                action="optimize_inventory",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps(optimization_data),
                timestamp=datetime.now()
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'optimization': optimization_data
            })
            
        except Exception as e:
            logger.error(f"Error in inventory optimization API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/agents/pricing/optimize', methods=['POST'])
    def pricing_optimize_api():
        """API endpoint for pricing optimization."""
        try:
            data = request.json
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            
            # Get the current product
            product = db.session.query(Product).get(product_id)
            if not product:
                return jsonify({
                    'success': False,
                    'error': 'Product not found'
                }), 404
            
            # In a real application, this would call the pricing agent
            # For now, we'll just return a placeholder response
            optimization_data = {
                'product_id': product_id,
                'store_id': store_id,
                'current_price': product.base_price,
                'optimal_price': round(product.base_price * 1.15, 2),
                'min_price': round(product.base_price * 0.9, 2),
                'max_price': round(product.base_price * 1.3, 2),
                'competitor_avg_price': round(product.base_price * 1.1, 2),
                'price_elasticity': -1.5,
                'recommendation': f"Increase price to ${round(product.base_price * 1.15, 2)}"
            }
            
            # Log the action
            log_entry = AgentLog(
                agent_type="pricing",
                action="optimize_pricing",
                product_id=product_id,
                store_id=store_id,
                details=json.dumps(optimization_data),
                timestamp=datetime.now()
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'optimization': optimization_data
            })
            
        except Exception as e:
            logger.error(f"Error in pricing optimization API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500