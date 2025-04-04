"""
Entry point for the AI Inventory Optimization System.

This file is the entry point for the application when run on Replit or
with Gunicorn. It imports the Flask app from app.py and makes it
available to the WSGI server.
"""

from app import app

if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)