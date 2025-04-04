# AI Inventory Optimization System

A multi-agent AI-powered inventory optimization system that provides demand forecasting, inventory management, and pricing recommendations.

## Overview

This system uses a multi-agent architecture to optimize inventory management:

1. **Demand Agent**: Forecasts future product demand based on historical data
2. **Inventory Agent**: Makes inventory level recommendations based on demand predictions
3. **Pricing Agent**: Suggests optimal pricing strategies based on demand and inventory levels

## Features

- AI-powered demand forecasting
- Inventory level optimization recommendations
- Dynamic pricing strategy suggestions
- Web dashboard for monitoring agent activities and recommendations
- Detailed logging of all agent actions

## Technical Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, Bootstrap CSS, Chart.js
- **AI Models**: Custom forecasting models

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Access the dashboard at http://localhost:5000/dashboard

## License

MIT