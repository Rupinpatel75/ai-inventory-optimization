"""
Simplified version of app.py for the AI Inventory Optimization System.
"""

import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base class for models
class Base(DeclarativeBase):
    pass

# Create extensions
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Flask config
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development_secret_key")

# Initialize extensions with app
db.init_app(app)

# Create a basic route for testing
@app.route('/')
def index():
    return render_template('index.html')

# Create a dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Create tables
with app.app_context():
    # Import the models
    from models_simplified import Product, Store, Inventory, AgentLog, User
    db.create_all()
    logger.info("Created database tables")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)