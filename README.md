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
- Web scraping capability for market intelligence

## Technical Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, Bootstrap CSS, Chart.js
- **AI Models**: Custom forecasting models with LLM integration
- **Utilities**: Web scraping, API integrations, and data processing

## System Setup and Installation

### Prerequisites
- Python 3.9+
- PostgreSQL database
- pip for package management

### Installation Steps
1. Clone this repository
   ```bash
   git clone https://github.com/Rupinpatel75/ai-inventory-optimization.git
   cd ai-inventory-optimization
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   # Database connection (required)
   export DATABASE_URL=postgresql://username:password@localhost:5432/inventory_db
   
   # Optional variables
   export SESSION_SECRET=your_session_secret_key
   export FLASK_DEBUG=1  # For development only
   ```

4. Initialize the database
   ```bash
   # The app will automatically create tables and sample data on first run
   # Make sure PostgreSQL is running and the database exists
   ```

5. Run the application
   ```bash
   python main.py
   ```

6. Access the web interface
   - Main page: http://localhost:5000/
   - Dashboard: http://localhost:5000/dashboard
   - Agent logs: http://localhost:5000/logs

## API Usage Guide

The system provides several API endpoints to interact with the AI agents programmatically.

### Generate Demand Predictions

**Endpoint:** `POST /api/predict`

**Body:**
```json
{
  "product_id": 1,
  "store_id": 1,
  "days": 30
}
```

**Example (using curl):**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "store_id": 1, "days": 30}'
```

**Response:**
```json
{
  "success": true,
  "predictions": [
    {"date": "2025-04-05", "demand": 15},
    {"date": "2025-04-06", "demand": 18},
    ...
  ],
  "inventory_recommendation": {
    "status": "ADEQUATE",
    "current_quantity": 50,
    "recommended_order": 30,
    "reasoning": "Current stock will cover approximately 10 days..."
  },
  "pricing_recommendation": {
    "strategy": "STANDARD",
    "base_price": 599.99,
    "recommended_price": 629.99,
    "explanation": "Demand is consistent with slight increase trend..."
  }
}
```

### Get Inventory Data

**Endpoint:** `GET /api/inventory?product_id=1&store_id=1`

**Example:**
```bash
curl http://localhost:5000/api/inventory?product_id=1&store_id=1
```

### Get Agent Logs

**Endpoint:** `GET /api/logs?agent_type=demand&limit=10`

**Example:**
```bash
curl http://localhost:5000/api/logs?agent_type=demand&limit=10
```

### Test Web Scraper

**Endpoint:** `POST /api/web-scraper-test`

**Body:**
```json
{
  "url": "https://example.com/product-page"
}
```

## Integration with External Systems

The system can be integrated with ERP systems, e-commerce platforms, or POS systems via the APIs detailed above. Use the prediction endpoint to regularly update your inventory management system with AI-optimized recommendations.

## License

MIT