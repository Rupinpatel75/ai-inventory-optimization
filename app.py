import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory_system.db"
# SQLite doesn't need pool options but keeping them for future compatibility
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with SQLAlchemy
db.init_app(app)

# Import routes after app initialization to avoid circular imports
with app.app_context():
    from routes import register_routes
    from models import Product, Store, InventoryRecord, PredictionLog, AgentAction
    
    # Create database tables if they don't exist
    db.create_all()
    
    # Register routes
    register_routes(app)

# Import agents
from agents.demand_agent import DemandAgent
from agents.inventory_agent import InventoryAgent
from agents.pricing_agent import PricingAgent

# Create agent instances
demand_agent = DemandAgent()
inventory_agent = InventoryAgent()
pricing_agent = PricingAgent()

# Initialize with sample data if database is empty
def init_sample_data():
    with app.app_context():
        # Only initialize if no products exist
        if Product.query.count() == 0:
            # Add sample products
            products = [
                Product(name="Laptop", category="Electronics", base_price=899.99),
                Product(name="Smartphone", category="Electronics", base_price=599.99),
                Product(name="Headphones", category="Electronics", base_price=149.99),
                Product(name="T-shirt", category="Clothing", base_price=19.99),
                Product(name="Jeans", category="Clothing", base_price=39.99)
            ]
            db.session.add_all(products)
            db.session.commit()  # Commit to get product IDs
            
            # Add sample stores
            stores = [
                Store(name="Main Street Store", location="New York"),
                Store(name="Downtown Branch", location="Los Angeles"),
                Store(name="Shopping Mall", location="Chicago")
            ]
            db.session.add_all(stores)
            db.session.commit()  # Commit to get store IDs
            
            # Add sample inventory records
            inventory_records = []
            for product in products:
                for store in stores:
                    record = InventoryRecord(
                        product_id=product.id,
                        store_id=store.id,
                        quantity=50,
                        last_updated=datetime.now()
                    )
                    inventory_records.append(record)
            
            db.session.add_all(inventory_records)
            db.session.commit()
            logger.info("Sample data initialized")

# Initialize sample data when app starts
with app.app_context():
    init_sample_data()

# Create routes.py module
import os
routes_path = os.path.join(os.path.dirname(__file__), 'routes.py')
if not os.path.exists(routes_path):
    with open(routes_path, 'w') as f:
        f.write('''
from flask import render_template, request, jsonify, redirect, url_for
from models import Product, Store, InventoryRecord, PredictionLog, AgentAction
from app import db
from utils.forecasting import load_forecast_model, predict_demand
from agents.demand_agent import DemandAgent
from agents.inventory_agent import InventoryAgent
from agents.pricing_agent import PricingAgent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize agents
demand_agent = DemandAgent()
inventory_agent = InventoryAgent()
pricing_agent = PricingAgent()

def register_routes(app):
    @app.route('/')
    def index():
        """Main page of the application."""
        products = Product.query.all()
        stores = Store.query.all()
        return render_template('index.html', products=products, stores=stores)
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard showing inventory optimization insights."""
        products = Product.query.all()
        stores = Store.query.all()
        return render_template('dashboard.html', products=products, stores=stores)
    
    @app.route('/logs')
    def logs():
        """View showing agent activity logs."""
        logs = AgentAction.query.order_by(AgentAction.timestamp.desc()).limit(100).all()
        return render_template('logs.html', logs=logs)
    
    @app.route('/api/predict', methods=['POST'])
    def predict_endpoint():
        """API endpoint to get demand predictions."""
        try:
            data = request.json
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            days = data.get('days', 30)
            
            # Get predictions from demand agent
            predictions = demand_agent.predict_demand(product_id, store_id, days)
            
            # Get inventory recommendations
            inventory_rec = inventory_agent.optimize_inventory(product_id, store_id, predictions)
            
            # Get pricing recommendations
            pricing_rec = pricing_agent.optimize_price(product_id, store_id, predictions)
            
            # Log this prediction
            log = PredictionLog(
                product_id=product_id,
                store_id=store_id,
                prediction_days=days,
                avg_predicted_demand=sum(p['value'] for p in predictions) / len(predictions) if predictions else 0,
                timestamp=datetime.now()
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'inventory_recommendation': inventory_rec,
                'pricing_recommendation': pricing_rec
            })
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/inventory', methods=['GET'])
    def get_inventory():
        """Get current inventory levels."""
        product_id = request.args.get('product_id')
        store_id = request.args.get('store_id')
        
        query = InventoryRecord.query
        if product_id:
            query = query.filter_by(product_id=product_id)
        if store_id:
            query = query.filter_by(store_id=store_id)
        
        records = query.all()
        result = []
        for record in records:
            product = Product.query.get(record.product_id)
            store = Store.query.get(record.store_id)
            result.append({
                'id': record.id,
                'product_id': record.product_id,
                'product_name': product.name if product else 'Unknown',
                'store_id': record.store_id,
                'store_name': store.name if store else 'Unknown',
                'quantity': record.quantity,
                'last_updated': record.last_updated.isoformat()
            })
        
        return jsonify({
            'success': True,
            'inventory': result
        })
    
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        """Get agent action logs."""
        limit = int(request.args.get('limit', 20))
        agent_type = request.args.get('agent_type')
        
        query = AgentAction.query
        if agent_type:
            query = query.filter_by(agent_type=agent_type)
        
        logs = query.order_by(AgentAction.timestamp.desc()).limit(limit).all()
        result = []
        
        for log in logs:
            product = Product.query.get(log.product_id) if log.product_id else None
            store = Store.query.get(log.store_id) if log.store_id else None
            
            result.append({
                'id': log.id,
                'agent_type': log.agent_type,
                'action': log.action,
                'product_id': log.product_id,
                'product_name': product.name if product else None,
                'store_id': log.store_id,
                'store_name': store.name if store else None,
                'details': log.details,
                'timestamp': log.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'logs': result
        })
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        """Get all products."""
        products = Product.query.all()
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'base_price': product.base_price
            })
        
        return jsonify({
            'success': True,
            'products': result
        })
    
    @app.route('/api/stores', methods=['GET'])
    def get_stores():
        """Get all stores."""
        stores = Store.query.all()
        result = []
        for store in stores:
            result.append({
                'id': store.id,
                'name': store.name,
                'location': store.location
            })
        
        return jsonify({
            'success': True,
            'stores': result
        })
''')
