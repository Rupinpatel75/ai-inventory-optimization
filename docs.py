"""
AI Inventory Optimization System - Documentation

This file contains documentation on how to connect to and use the AI Inventory
Optimization System, including how to make API requests.

## Database Connection

To connect the system to your PostgreSQL database:

1. Set the DATABASE_URL environment variable:
   ```
   export DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

2. The application will automatically use this connection string to connect to your PostgreSQL instance.

3. If the DATABASE_URL is not set, the system will fallback to a local SQLite database.

## API Endpoints

### Generate Demand Predictions

Endpoint: POST /api/predict

Request Body:
{
  "product_id": 1,
  "store_id": 1,
  "days": 30
}

Example (using curl):
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "store_id": 1, "days": 30}'

Example (using Python requests):
```python
import requests
import json

url = "http://localhost:5000/api/predict"
payload = {
  "product_id": 1,
  "store_id": 1,
  "days": 30
}
headers = {
  "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)
data = response.json()
print(data)
```

### Get Inventory Data

Endpoint: GET /api/inventory

Query Parameters:
- product_id (optional): Filter by product ID
- store_id (optional): Filter by store ID

Example (using curl):
curl http://localhost:5000/api/inventory?product_id=1&store_id=1

### Get Agent Logs

Endpoint: GET /api/logs

Query Parameters:
- agent_type (optional): Filter by agent type (demand, inventory, pricing)
- limit (optional): Limit the number of results (default: 20)

Example (using curl):
curl http://localhost:5000/api/logs?agent_type=demand&limit=10

### Test Web Scraper

Endpoint: POST /api/web-scraper-test

Request Body:
{
  "url": "https://example.com/product-page"
}

Example (using curl):
curl -X POST http://localhost:5000/api/web-scraper-test \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product-page"}'

## Integration with Other Systems

You can integrate this system with your existing ERP, e-commerce platform, or inventory management
system by making API calls to the endpoints above.

For example, you might:

1. Set up a daily cron job that calls the predict endpoint to get updated forecasts.
2. Create a sync process that updates your inventory levels in both systems.
3. Implement pricing recommendations in your e-commerce platform based on the API responses.
"""

# Code example to demonstrate API usage
def api_usage_example():
    """Example Python code showing how to use the API"""
    import requests
    import json
    
    # Base URL for the API (replace with your actual server URL)
    base_url = "http://localhost:5000"
    
    # Generate demand predictions
    def predict_demand(product_id, store_id, days=30):
        url = f"{base_url}/api/predict"
        payload = {
            "product_id": product_id,
            "store_id": store_id,
            "days": days
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()
    
    # Get inventory levels
    def get_inventory(product_id=None, store_id=None):
        url = f"{base_url}/api/inventory"
        params = {}
        
        if product_id:
            params["product_id"] = product_id
        if store_id:
            params["store_id"] = store_id
            
        response = requests.get(url, params=params)
        return response.json()
    
    # Get agent logs
    def get_logs(agent_type=None, limit=20):
        url = f"{base_url}/api/logs"
        params = {"limit": limit}
        
        if agent_type:
            params["agent_type"] = agent_type
            
        response = requests.get(url, params=params)
        return response.json()
    
    # Test web scraper
    def test_web_scraper(url):
        api_url = f"{base_url}/api/web-scraper-test"
        payload = {"url": url}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        return response.json()
    
    # Example usage:
    # predictions = predict_demand(1, 1, 30)
    # inventory = get_inventory(product_id=1)
    # logs = get_logs(agent_type="demand", limit=10)
    # scraper_result = test_web_scraper("https://example.com/product-page")