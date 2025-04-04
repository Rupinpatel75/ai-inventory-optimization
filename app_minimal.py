"""
Minimal version of the application to ensure we can get it working.
"""

import os
import logging
from flask import Flask, render_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Basic routes for testing
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Inventory Optimization System</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1>AI Inventory Optimization System</h1>
            <p>Welcome to the inventory optimization system!</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)