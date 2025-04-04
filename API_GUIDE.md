# API Usage Guide for AI Inventory Optimization System

This guide provides instructions on how to connect to and use the AI Inventory Optimization System, including how to make API requests.

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

**Endpoint:** `POST /api/predict`

**Request Body:**
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

**Example (using Python requests):**
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

**Example (using JavaScript fetch):**
```javascript
fetch('http://localhost:5000/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: 1,
    store_id: 1,
    days: 30
  }),
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => console.error('Error:', error));
```

### Get Inventory Data

**Endpoint:** `GET /api/inventory`

**Query Parameters:**
- `product_id` (optional): Filter by product ID
- `store_id` (optional): Filter by store ID

**Example (using curl):**
```bash
curl http://localhost:5000/api/inventory?product_id=1&store_id=1
```

### Get Agent Logs

**Endpoint:** `GET /api/logs`

**Query Parameters:**
- `agent_type` (optional): Filter by agent type (demand, inventory, pricing)
- `limit` (optional): Limit the number of results (default: 20)

**Example (using curl):**
```bash
curl http://localhost:5000/api/logs?agent_type=demand&limit=10
```

### Test Web Scraper

**Endpoint:** `POST /api/web-scraper-test`

**Request Body:**
```json
{
  "url": "https://example.com/product-page"
}
```

**Example (using curl):**
```bash
curl -X POST http://localhost:5000/api/web-scraper-test \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product-page"}'
```

## Integration with Other Systems

You can integrate this system with your existing ERP, e-commerce platform, or inventory management system by making API calls to the endpoints above.

For example, you might:

1. Set up a daily cron job that calls the predict endpoint to get updated forecasts.
2. Create a sync process that updates your inventory levels in both systems.
3. Implement pricing recommendations in your e-commerce platform based on the API responses.

## Authentication

Currently, the API does not require authentication. If you're deploying in a production environment, consider adding authentication middleware to secure the API endpoints.