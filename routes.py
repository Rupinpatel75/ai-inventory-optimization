"""
Route definitions for the AI Inventory Optimization System.

This module defines all HTTP routes and views for the application.
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
    
    # Product routes
    @app.route('/products')
    def product_list():
        """Display all products."""
        products = db.session.query(Product).filter_by(active=True).all()
        return render_template('products/list.html', products=products)
    
    @app.route('/products/<int:product_id>')
    def product_detail(product_id):
        """Display details for a specific product."""
        product = db.session.query(Product).get_or_404(product_id)
        inventory = db.session.query(
            Inventory, Store
        ).join(
            Store, Store.id == Inventory.store_id
        ).filter(
            Inventory.product_id == product_id,
            Store.active == True
        ).all()
        
        sales = db.session.query(Sale).filter(
            Sale.product_id == product_id
        ).order_by(Sale.date.desc()).limit(30).all()
        
        forecasts = db.session.query(Forecast).filter(
            Forecast.product_id == product_id,
            Forecast.forecast_date >= datetime.now()
        ).order_by(Forecast.forecast_date).all()
        
        return render_template(
            'products/detail.html',
            product=product,
            inventory=inventory,
            sales=sales,
            forecasts=forecasts
        )
    
    # Store routes
    @app.route('/stores')
    def store_list():
        """Display all stores."""
        stores = db.session.query(Store).filter_by(active=True).all()
        return render_template('stores/list.html', stores=stores)
    
    @app.route('/stores/<int:store_id>')
    def store_detail(store_id):
        """Display details for a specific store."""
        store = db.session.query(Store).get_or_404(store_id)
        inventory = db.session.query(
            Inventory, Product
        ).join(
            Product, Product.id == Inventory.product_id
        ).filter(
            Inventory.store_id == store_id,
            Product.active == True
        ).all()
        
        sales = db.session.query(
            Sale, Product
        ).join(
            Product, Product.id == Sale.product_id
        ).filter(
            Sale.store_id == store_id
        ).order_by(Sale.date.desc()).limit(30).all()
        
        return render_template(
            'stores/detail.html',
            store=store,
            inventory=inventory,
            sales=sales
        )
    
    # Inventory routes
    @app.route('/inventory')
    def inventory_list():
        """Display all inventory."""
        inventory = db.session.query(
            Inventory, Product, Store
        ).join(
            Product, Product.id == Inventory.product_id
        ).join(
            Store, Store.id == Inventory.store_id
        ).filter(
            Product.active == True,
            Store.active == True
        ).all()
        
        return render_template('inventory/list.html', inventory=inventory)
    
    # Supplier routes
    @app.route('/suppliers')
    def supplier_list():
        """Display all suppliers."""
        suppliers = db.session.query(Supplier).filter_by(active=True).all()
        return render_template('suppliers/list.html', suppliers=suppliers)
    
    @app.route('/suppliers/<int:supplier_id>')
    def supplier_detail(supplier_id):
        """Display details for a specific supplier."""
        supplier = db.session.query(Supplier).get_or_404(supplier_id)
        products = db.session.query(Product).filter_by(
            supplier_id=supplier_id,
            active=True
        ).all()
        
        return render_template(
            'suppliers/detail.html',
            supplier=supplier,
            products=products
        )
    
    # Reports routes
    @app.route('/reports')
    def reports_list():
        """Display available reports."""
        return render_template('reports/list.html')
    
    @app.route('/reports/inventory-value')
    def inventory_value_report():
        """Display inventory value report."""
        inventory_by_category = db.session.query(
            Product.category,
            db.func.sum(Product.base_price * Inventory.quantity).label('value'),
            db.func.sum(Inventory.quantity).label('quantity')
        ).join(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Product.active == True
        ).group_by(
            Product.category
        ).all()
        
        inventory_by_store = db.session.query(
            Store.name,
            db.func.sum(Product.base_price * Inventory.quantity).label('value'),
            db.func.sum(Inventory.quantity).label('quantity')
        ).join(
            Inventory, Store.id == Inventory.store_id
        ).join(
            Product, Product.id == Inventory.product_id
        ).filter(
            Product.active == True,
            Store.active == True
        ).group_by(
            Store.name
        ).all()
        
        return render_template(
            'reports/inventory_value.html',
            inventory_by_category=inventory_by_category,
            inventory_by_store=inventory_by_store
        )
    
    @app.route('/reports/sales-performance')
    def sales_performance_report():
        """Display sales performance report."""
        # Last 30 days of sales by date
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        daily_sales = db.session.query(
            db.func.date(Sale.date).label('date'),
            db.func.sum(Sale.total_price).label('revenue'),
            db.func.sum(Sale.quantity).label('quantity')
        ).filter(
            Sale.date >= thirty_days_ago
        ).group_by(
            db.func.date(Sale.date)
        ).order_by(
            db.func.date(Sale.date)
        ).all()
        
        # Sales by product category
        sales_by_category = db.session.query(
            Product.category,
            db.func.sum(Sale.total_price).label('revenue'),
            db.func.sum(Sale.quantity).label('quantity')
        ).join(
            Product, Product.id == Sale.product_id
        ).filter(
            Sale.date >= thirty_days_ago
        ).group_by(
            Product.category
        ).order_by(
            db.func.sum(Sale.total_price).desc()
        ).all()
        
        # Sales by store
        sales_by_store = db.session.query(
            Store.name,
            db.func.sum(Sale.total_price).label('revenue'),
            db.func.sum(Sale.quantity).label('quantity')
        ).join(
            Store, Store.id == Sale.store_id
        ).filter(
            Sale.date >= thirty_days_ago
        ).group_by(
            Store.name
        ).order_by(
            db.func.sum(Sale.total_price).desc()
        ).all()
        
        return render_template(
            'reports/sales_performance.html',
            daily_sales=daily_sales,
            sales_by_category=sales_by_category,
            sales_by_store=sales_by_store
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
    
    # Data import routes
    @app.route('/data/import', methods=['GET', 'POST'])
    def data_import():
        """Handle data imports."""
        if request.method == 'POST':
            import_type = request.form.get('import_type')
            
            if 'file' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            
            if file:
                # Start a new import record
                import_record = DataImport(
                    import_type=import_type,
                    source=file.filename,
                    status='pending',
                    start_time=datetime.now()
                )
                db.session.add(import_record)
                db.session.commit()
                
                # Save the file to a temporary location
                upload_dir = os.path.join(app.instance_path, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, file.filename)
                file.save(file_path)
                
                try:
                    # Process the file based on import type
                    # This would be handled by specialized import functions in a real app
                    # For now, we'll just update the status
                    import_record.status = 'completed'
                    import_record.records_processed = 100
                    import_record.records_succeeded = 95
                    import_record.records_failed = 5
                    import_record.end_time = datetime.now()
                    db.session.commit()
                    
                    flash(f'Successfully imported {import_record.records_succeeded} records', 'success')
                    
                except Exception as e:
                    logger.error(f"Error processing import: {str(e)}")
                    import_record.status = 'failed'
                    import_record.error_message = str(e)
                    import_record.end_time = datetime.now()
                    db.session.commit()
                    
                    flash(f'Error processing import: {str(e)}', 'error')
                
                return redirect(url_for('data_import_history'))
        
        return render_template('data/import.html')
    
    @app.route('/data/imports')
    def data_import_history():
        """Display data import history."""
        imports = db.session.query(DataImport).order_by(DataImport.start_time.desc()).all()
        return render_template('data/imports.html', imports=imports)
    
    # Static file routes
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500