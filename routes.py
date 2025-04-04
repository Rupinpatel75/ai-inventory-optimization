"""
Routes for the AI Inventory Optimization System.
"""

import json
import logging
from flask import render_template, request, jsonify
from utils.forecasting import predict_demand, load_forecast_model
from utils.data_loader import load_sample_data, generate_historical_sales_data
from utils.web_scraper import WebScraper
from agents import demand_agent, inventory_agent, pricing_agent
from models import Product, Store, InventoryRecord, PredictionLog, AgentAction, db

logger = logging.getLogger(__name__)
web_scraper = WebScraper()

def register_routes(app):
    """Register all routes with the Flask app."""
    
    # Web UI routes
    @app.route('/')
    def index():
        """Main page of the application."""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard showing inventory optimization insights."""
        # Get products and stores for the dashboard
        products = db.session.query(Product).all()
        stores = db.session.query(Store).all()
        
        return render_template('dashboard.html', products=products, stores=stores)
    
    @app.route('/logs')
    def logs():
        """View showing agent activity logs."""
        return render_template('logs.html')
    
    # API routes
    @app.route('/api/predict', methods=['POST'])
    def predict_endpoint():
        """API endpoint to get demand predictions."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            days = data.get('days', 30)
            
            if not product_id or not store_id:
                return jsonify({"success": False, "error": "product_id and store_id are required"}), 400
            
            # Use the demand agent to make predictions
            result = demand_agent.predict_product_demand(product_id, store_id, days)
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 400
            
            return jsonify({"success": True, "data": result})
            
        except Exception as e:
            logger.error(f"Error in predict endpoint: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/inventory', methods=['GET'])
    def get_inventory():
        """Get current inventory levels."""
        try:
            product_id = request.args.get('product_id', type=int)
            store_id = request.args.get('store_id', type=int)
            
            # Build query
            query = db.session.query(
                InventoryRecord, 
                Product.name.label('product_name'),
                Store.name.label('store_name')
            ).join(
                Product, InventoryRecord.product_id == Product.id
            ).join(
                Store, InventoryRecord.store_id == Store.id
            )
            
            # Apply filters if provided
            if product_id:
                query = query.filter(InventoryRecord.product_id == product_id)
            if store_id:
                query = query.filter(InventoryRecord.store_id == store_id)
            
            # Execute query
            results = query.all()
            
            # Format response
            inventory_data = []
            for record, product_name, store_name in results:
                inventory_data.append({
                    "id": record.id,
                    "product_id": record.product_id,
                    "product_name": product_name,
                    "store_id": record.store_id,
                    "store_name": store_name,
                    "quantity": record.quantity,
                    "last_updated": record.last_updated.isoformat() if record.last_updated else None
                })
            
            return jsonify({"success": True, "inventory": inventory_data})
            
        except Exception as e:
            logger.error(f"Error getting inventory: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        """Get agent action logs."""
        try:
            agent_type = request.args.get('agent_type')
            limit = request.args.get('limit', 20, type=int)
            
            # Build query
            query = db.session.query(
                AgentAction,
                Product.name.label('product_name'),
                Store.name.label('store_name')
            ).outerjoin(
                Product, AgentAction.product_id == Product.id
            ).outerjoin(
                Store, AgentAction.store_id == Store.id
            )
            
            # Apply filters if provided
            if agent_type:
                query = query.filter(AgentAction.agent_type == agent_type)
            
            # Order by timestamp (newest first) and limit
            query = query.order_by(AgentAction.timestamp.desc()).limit(limit)
            
            # Execute query
            results = query.all()
            
            # Format response
            logs_data = []
            for action, product_name, store_name in results:
                # Try to parse details as JSON if it's a string
                details = action.details
                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except (json.JSONDecodeError, TypeError):
                        # Keep as string if not valid JSON
                        pass
                
                logs_data.append({
                    "id": action.id,
                    "agent_type": action.agent_type,
                    "action": action.action,
                    "product_id": action.product_id,
                    "product_name": product_name,
                    "store_id": action.store_id,
                    "store_name": store_name,
                    "details": details,
                    "timestamp": action.timestamp.isoformat() if action.timestamp else None
                })
            
            return jsonify({"success": True, "logs": logs_data})
            
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        """Get all products."""
        try:
            products = db.session.query(Product).all()
            
            products_data = []
            for product in products:
                products_data.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "base_price": product.base_price
                })
            
            return jsonify({"success": True, "products": products_data})
            
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/stores', methods=['GET'])
    def get_stores():
        """Get all stores."""
        try:
            stores = db.session.query(Store).all()
            
            stores_data = []
            for store in stores:
                stores_data.append({
                    "id": store.id,
                    "name": store.name,
                    "location": store.location
                })
            
            return jsonify({"success": True, "stores": stores_data})
            
        except Exception as e:
            logger.error(f"Error getting stores: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/llm/status', methods=['GET'])
    def get_llm_status():
        """Check if LLM is available and working."""
        from utils.llm_integration import llm_manager
        
        try:
            available = llm_manager.ollama_available
            models = llm_manager.available_models
            preferred = llm_manager.preferred_model
            
            # Test a simple prompt if available
            test_response = None
            if available and preferred:
                test_response = llm_manager.chat_completion(
                    "Respond with a single word: Working?",
                    "You are a helpful AI assistant. Keep your response very brief."
                )
            
            return jsonify({
                "success": True,
                "available": available,
                "models": models,
                "preferred_model": preferred,
                "test_response": test_response
            })
            
        except Exception as e:
            logger.error(f"Error checking LLM status: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/web-scraper-test', methods=['POST'])
    def test_web_scraper():
        """Test the web scraper with a URL."""
        try:
            data = request.get_json()
            
            if not data or not data.get('url'):
                return jsonify({"success": False, "error": "URL is required"}), 400
            
            url = data.get('url')
            
            # Extract text content
            content = web_scraper.extract_text_content(url)
            
            # Truncate if too long
            if len(content) > 5000:
                content = content[:5000] + "... (truncated)"
            
            return jsonify({
                "success": True,
                "url": url,
                "content": content
            })
            
        except Exception as e:
            logger.error(f"Error testing web scraper: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/agents/<agent_type>/test', methods=['GET'])
    def test_agent(agent_type):
        """Test a specific agent with sample data."""
        try:
            if agent_type not in ['demand', 'inventory', 'pricing']:
                return jsonify({"success": False, "error": f"Unknown agent type: {agent_type}"}), 400
            
            # Get first product and store for testing
            product = db.session.query(Product).first()
            store = db.session.query(Store).first()
            
            if not product or not store:
                return jsonify({"success": False, "error": "No products or stores found. Please ensure sample data is loaded."}), 400
            
            result = {}
            
            # Test appropriate agent functionality
            if agent_type == 'demand':
                # Test demand prediction
                result['prediction'] = demand_agent.predict_product_demand(product.id, store.id, 7)
                # Test historical data
                result['historical'] = demand_agent.get_historical_sales(product.id, store.id, 30)
                # Test seasonality analysis
                result['seasonality'] = demand_agent.analyze_seasonality(product.id, store.id)
            
            elif agent_type == 'inventory':
                # Get current inventory
                result['current_inventory'] = inventory_agent.get_current_inventory(product.id, store.id)
                # Get optimal inventory levels
                result['optimal_levels'] = inventory_agent.get_optimal_inventory_levels(product.id, store.id)
                # Get reorder recommendation
                result['reorder_recommendation'] = inventory_agent.get_reorder_recommendation(product.id, store.id)
                # Get stockout risk
                result['stockout_risk'] = inventory_agent.get_stockout_risk(product.id, store.id)
            
            elif agent_type == 'pricing':
                # Get optimal price
                result['optimal_price'] = pricing_agent.get_optimal_price(product.id, store.id)
                # Get price recommendation
                result['price_recommendation'] = pricing_agent.get_price_recommendation(product.id, store.id)
                # Get competitor prices
                result['competitor_prices'] = pricing_agent.get_competitor_prices(product.id, store.id)
                # Analyze promotion
                result['promotion_analysis'] = pricing_agent.analyze_promotion(product.id, store.id, 0.1)
            
            return jsonify({
                "success": True,
                "agent_type": agent_type,
                "product": {"id": product.id, "name": product.name},
                "store": {"id": store.id, "name": store.name},
                "results": result
            })
            
        except Exception as e:
            logger.error(f"Error testing {agent_type} agent: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # Setup data route
    @app.route('/api/setup-data', methods=['POST'])
    def setup_data():
        """Load sample data into the database."""
        try:
            result = load_sample_data()
            
            if result:
                return jsonify({"success": True, "message": "Sample data loaded successfully"})
            else:
                return jsonify({"success": False, "error": "Failed to load sample data. Check logs for details."}), 500
            
        except Exception as e:
            logger.error(f"Error setting up sample data: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # Inventory update route
    @app.route('/api/inventory/update', methods=['POST'])
    def update_inventory():
        """Update inventory level for a product at a store."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            product_id = data.get('product_id')
            store_id = data.get('store_id')
            quantity = data.get('quantity')
            action = data.get('action', 'manual update')
            
            if not product_id or not store_id or quantity is None:
                return jsonify({"success": False, "error": "product_id, store_id, and quantity are required"}), 400
            
            # Use the inventory agent to update inventory
            result = inventory_agent.update_inventory(product_id, store_id, quantity, action)
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 400
            
            return jsonify({"success": True, "data": result})
            
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # Price update route
    @app.route('/api/price/update', methods=['POST'])
    def update_price():
        """Update base price for a product."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            product_id = data.get('product_id')
            new_price = data.get('new_price')
            
            if not product_id or new_price is None:
                return jsonify({"success": False, "error": "product_id and new_price are required"}), 400
            
            # Use the pricing agent to update price
            result = pricing_agent.update_base_price(product_id, new_price)
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 400
            
            return jsonify({"success": True, "data": result})
            
        except Exception as e:
            logger.error(f"Error updating price: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500