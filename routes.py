from flask import render_template, request, jsonify, redirect, url_for
from models import Product, Store, InventoryRecord, PredictionLog, AgentAction
from app import db
from utils.forecasting import load_forecast_model, predict_demand
from agents import demand_agent, inventory_agent, pricing_agent
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

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
                avg_predicted_demand=sum(p['demand'] for p in predictions) / len(predictions) if predictions else 0,
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
            
            # Parse JSON details if present
            details = None
            if log.details:
                try:
                    details = json.loads(log.details)
                except:
                    details = log.details
            
            result.append({
                'id': log.id,
                'agent_type': log.agent_type,
                'action': log.action,
                'product_id': log.product_id,
                'product_name': product.name if product else None,
                'store_id': log.store_id,
                'store_name': store.name if store else None,
                'details': details,
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
        
    @app.route('/api/llm-status', methods=['GET'])
    def get_llm_status():
        """Check if LLM is available and working."""
        from utils.llm_integration import llm_manager
        
        llm_available = False
        llm_message = "LLM not initialized"
        
        if llm_manager:
            llm_available = llm_manager.check_ollama_available()
            llm_message = "LLM available and responding" if llm_available else "LLM not available"
        
        return jsonify({
            'success': True,
            'llm_available': llm_available,
            'message': llm_message
        })
        
    @app.route('/api/web-scraper-test', methods=['POST'])
    def test_web_scraper():
        """Test the web scraper with a URL."""
        from utils.web_scraper import scraper
        
        try:
            data = request.json
            url = data.get('url')
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'No URL provided'
                }), 400
                
            # Extract text content
            text_content = scraper.extract_text_content(url)
            
            # Limit response size
            max_length = 1000
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "... (truncated)"
            
            return jsonify({
                'success': True,
                'url': url,
                'content_length': len(text_content),
                'content_preview': text_content
            })
        except Exception as e:
            logger.error(f"Web scraper test error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/agent-test/<agent_type>', methods=['POST'])
    def test_agent(agent_type):
        """Test a specific agent with sample data."""
        try:
            from agents import get_agent
            
            data = request.json
            product_id = data.get('product_id', 1)
            store_id = data.get('store_id', 1)
            
            # Get the agent
            try:
                agent = get_agent(agent_type)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f"Unknown agent type: {agent_type}"
                }), 400
            
            result = {}
            
            # Test different agent types
            if agent_type == 'demand':
                predictions = agent.predict_demand(product_id, store_id, days=7)
                result = {
                    'agent_type': agent_type,
                    'predictions': predictions
                }
            elif agent_type == 'inventory':
                # First get demand predictions
                demand_predictions = demand_agent.predict_demand(product_id, store_id, days=7)
                recommendation = agent.optimize_inventory(product_id, store_id, demand_predictions)
                result = {
                    'agent_type': agent_type,
                    'recommendation': recommendation
                }
            elif agent_type == 'pricing':
                # First get demand predictions
                demand_predictions = demand_agent.predict_demand(product_id, store_id, days=7)
                recommendation = agent.optimize_price(product_id, store_id, demand_predictions)
                result = {
                    'agent_type': agent_type,
                    'recommendation': recommendation
                }
            
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            logger.error(f"Agent test error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500