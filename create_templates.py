import os

# Create the templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Base template
base_html = '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Inventory Optimization{% endblock %}</title>
    <!-- Bootstrap CSS (Replit theme) -->
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <!-- Navigation bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">AI Inventory System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/dashboard' %}active{% endif %}" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/logs' %}active{% endif %}" href="/logs">Logs</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main content -->
    <div class="container">
        <!-- Flash messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Page content -->
        {% block content %}{% endblock %}
    </div>

    <!-- Footer -->
    <footer class="footer mt-5 py-3 bg-dark">
        <div class="container text-center">
            <span class="text-muted">© 2025 AI Inventory Optimization System</span>
        </div>
    </footer>

    <!-- JavaScript dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''

# Index template
index_html = '''{% extends "base.html" %}

{% block title %}Home - AI Inventory Optimization{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">AI Inventory Optimization System</h2>
                <p class="card-text">
                    Welcome to the AI Inventory Optimization System, powered by a multi-agent
                    architecture designed to optimize your inventory management processes.
                </p>
                <hr>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Demand Forecasting</h5>
                                <p class="card-text">Predict future product demand using AI-powered analytics.</p>
                                <a href="/dashboard" class="btn btn-primary">View Forecasts</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Inventory Optimization</h5>
                                <p class="card-text">Get recommendations for optimal inventory levels.</p>
                                <a href="/dashboard" class="btn btn-primary">View Recommendations</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Pricing Strategies</h5>
                                <p class="card-text">Optimize pricing based on demand and market data.</p>
                                <a href="/dashboard" class="btn btn-primary">View Prices</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">Generate Predictions</h3>
                <p class="card-text">Select a product and store to generate demand forecasts, inventory recommendations, and pricing strategies.</p>
                
                <form id="predictionForm" class="mt-3">
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <label for="productSelect" class="form-label">Product</label>
                            <select class="form-select" id="productSelect" required>
                                <option value="" selected disabled>Select Product</option>
                                {% for product in products %}
                                <option value="{{ product.id }}">{{ product.name }} ({{ product.category }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label for="storeSelect" class="form-label">Store</label>
                            <select class="form-select" id="storeSelect" required>
                                <option value="" selected disabled>Select Store</option>
                                {% for store in stores %}
                                <option value="{{ store.id }}">{{ store.name }} ({{ store.location }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label for="daysInput" class="form-label">Days to Forecast</label>
                            <input type="number" class="form-control" id="daysInput" value="30" min="1" max="90" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Generate Predictions</button>
                </form>
                
                <div id="predictionResults" class="mt-4" style="display: none;">
                    <div class="alert alert-info">
                        <div class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="ms-2">Processing prediction... Please wait.</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const predictionResults = document.getElementById('predictionResults');
    
    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading indicator
        predictionResults.style.display = 'block';
        
        // Get form values
        const productId = document.getElementById('productSelect').value;
        const storeId = document.getElementById('storeSelect').value;
        const days = document.getElementById('daysInput').value;
        
        // Make API request
        fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: parseInt(productId),
                store_id: parseInt(storeId),
                days: parseInt(days)
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Process results and update UI
            if (data.success) {
                // Format the results in a user-friendly way
                let resultsHTML = `
                    <h4 class="mt-4">Prediction Results</h4>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card border-info">
                                <div class="card-header bg-info text-white">
                                    <h5 class="card-title mb-0">Demand Forecast</h5>
                                </div>
                                <div class="card-body">
                                    <p>Average predicted daily demand: <strong>${(data.predictions.reduce((sum, p) => sum + p.demand, 0) / data.predictions.length).toFixed(2)}</strong></p>
                                    <p>Forecast period: <strong>${days} days</strong></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-success">
                                <div class="card-header bg-success text-white">
                                    <h5 class="card-title mb-0">Inventory Recommendation</h5>
                                </div>
                                <div class="card-body">
                                    <p>Status: <strong>${data.inventory_recommendation.status}</strong></p>
                                    <p>Current quantity: <strong>${data.inventory_recommendation.current_quantity}</strong></p>
                                    <p>Recommended order: <strong>${data.inventory_recommendation.recommended_order}</strong></p>
                                    <p><em>${data.inventory_recommendation.reasoning}</em></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-warning">
                                <div class="card-header bg-warning text-dark">
                                    <h5 class="card-title mb-0">Pricing Recommendation</h5>
                                </div>
                                <div class="card-body">
                                    <p>Strategy: <strong>${data.pricing_recommendation.strategy}</strong></p>
                                    <p>Base price: <strong>$${data.pricing_recommendation.base_price.toFixed(2)}</strong></p>
                                    <p>Recommended price: <strong>$${data.pricing_recommendation.recommended_price.toFixed(2)}</strong></p>
                                    <p><em>${data.pricing_recommendation.explanation}</em></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <h4 class="mt-4">Demand Forecast Chart</h4>
                    <canvas id="demandChart" width="400" height="200"></canvas>
                `;
                
                predictionResults.innerHTML = resultsHTML;
                
                // Create chart
                const dates = data.predictions.map(p => p.date);
                const demands = data.predictions.map(p => p.demand);
                
                new Chart(document.getElementById('demandChart'), {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [{
                            label: 'Predicted Demand',
                            data: demands,
                            borderColor: 'rgba(54, 162, 235, 1)',
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderWidth: 2,
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Date'
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Demand'
                                },
                                beginAtZero: true
                            }
                        }
                    }
                });
                
            } else {
                // Show error
                predictionResults.innerHTML = `
                    <div class="alert alert-danger">
                        Error generating predictions: ${data.error}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            predictionResults.innerHTML = `
                <div class="alert alert-danger">
                    Error connecting to the server. Please try again.
                </div>
            `;
        });
    });
});
</script>
{% endblock %}'''

# Dashboard template
dashboard_html = '''{% extends "base.html" %}

{% block title %}Dashboard - AI Inventory Optimization{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">Dashboard</h2>
                <p class="card-text">View and analyze inventory data across all stores and products.</p>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Inventory Status by Store</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="inventoryByStoreChart" width="400" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Inventory Value by Category</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="inventoryByCategoryChart" width="400" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Inventory Report</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Product</th>
                                                <th>Category</th>
                                                <th>Store</th>
                                                <th>Location</th>
                                                <th>Quantity</th>
                                                <th>Base Price ($)</th>
                                                <th>Value ($)</th>
                                                <th>Last Updated</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody id="inventoryTable">
                                            <tr>
                                                <td colspan="9" class="text-center">
                                                    <div class="spinner-border" role="status">
                                                        <span class="visually-hidden">Loading...</span>
                                                    </div>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Fetch inventory data
    fetch('/api/inventory')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Process inventory data
                const inventoryRecords = data.inventory;
                
                // Create inventory table
                createInventoryTable(inventoryRecords);
                
                // Create store chart
                createStoreChart(inventoryRecords);
                
                // Create category chart
                createCategoryChart(inventoryRecords);
            } else {
                console.error('Error fetching inventory data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
    // Create inventory table
    function createInventoryTable(records) {
        const tableBody = document.getElementById('inventoryTable');
        let tableHTML = '';
        
        // Get products to access price information
        fetch('/api/products')
            .then(response => response.json())
            .then(productsData => {
                if (productsData.success) {
                    const products = productsData.products;
                    
                    // Build table rows
                    records.forEach(record => {
                        // Find product to get base price
                        const product = products.find(p => p.id === record.product_id);
                        const basePrice = product ? product.base_price : 0;
                        const value = basePrice * record.quantity;
                        
                        // Determine status based on quantity
                        let status, statusClass;
                        if (record.quantity <= 10) {
                            status = 'Low Stock';
                            statusClass = 'text-danger';
                        } else if (record.quantity <= 30) {
                            status = 'Medium Stock';
                            statusClass = 'text-warning';
                        } else {
                            status = 'Well Stocked';
                            statusClass = 'text-success';
                        }
                        
                        tableHTML += `
                            <tr>
                                <td>${record.product_name}</td>
                                <td>${product ? product.category : 'N/A'}</td>
                                <td>${record.store_name}</td>
                                <td>${record.store_id}</td>
                                <td>${record.quantity}</td>
                                <td>${basePrice.toFixed(2)}</td>
                                <td>${value.toFixed(2)}</td>
                                <td>${new Date(record.last_updated).toLocaleDateString()}</td>
                                <td class="${statusClass}">${status}</td>
                            </tr>
                        `;
                    });
                    
                    tableBody.innerHTML = tableHTML;
                }
            })
            .catch(error => {
                console.error('Error fetching products:', error);
            });
    }
    
    // Create store chart
    function createStoreChart(records) {
        // Group records by store
        const storeData = {};
        records.forEach(record => {
            if (!storeData[record.store_name]) {
                storeData[record.store_name] = 0;
            }
            storeData[record.store_name] += record.quantity;
        });
        
        // Extract labels and data
        const labels = Object.keys(storeData);
        const data = Object.values(storeData);
        
        // Create chart
        new Chart(document.getElementById('inventoryByStoreChart'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Items in Stock',
                    data: data,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 205, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Items in Stock'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Store'
                        }
                    }
                }
            }
        });
    }
    
    // Create category chart
    function createCategoryChart(records) {
        // We need products data to get categories
        fetch('/api/products')
            .then(response => response.json())
            .then(productsData => {
                if (productsData.success) {
                    const products = productsData.products;
                    
                    // Group by category and calculate value
                    const categoryData = {};
                    records.forEach(record => {
                        const product = products.find(p => p.id === record.product_id);
                        if (product) {
                            const category = product.category;
                            const value = product.base_price * record.quantity;
                            
                            if (!categoryData[category]) {
                                categoryData[category] = 0;
                            }
                            categoryData[category] += value;
                        }
                    });
                    
                    // Extract labels and data
                    const labels = Object.keys(categoryData);
                    const data = Object.values(categoryData);
                    
                    // Create chart
                    new Chart(document.getElementById('inventoryByCategoryChart'), {
                        type: 'pie',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Inventory Value',
                                data: data,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 205, 86, 0.7)',
                                    'rgba(75, 192, 192, 0.7)',
                                    'rgba(153, 102, 255, 0.7)'
                                ],
                                borderColor: [
                                    'rgba(255, 99, 132, 1)',
                                    'rgba(54, 162, 235, 1)',
                                    'rgba(255, 205, 86, 1)',
                                    'rgba(75, 192, 192, 1)',
                                    'rgba(153, 102, 255, 1)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            const label = context.label || '';
                                            const value = context.raw;
                                            return `${label}: $${value.toFixed(2)}`;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching products:', error);
            });
    }
});
</script>
{% endblock %}'''

# Logs template
logs_html = '''{% extends "base.html" %}

{% block title %}Agent Logs - AI Inventory Optimization{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">Agent Activity Logs</h2>
                <p class="card-text">View a history of actions taken by the AI agents in the system.</p>
                
                <div class="row mt-4">
                    <div class="col-md-12 mb-4">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">Agent Action Distribution</h5>
                                <div>
                                    <select id="chartTimeFrame" class="form-select form-select-sm">
                                        <option value="7">Last 7 days</option>
                                        <option value="30" selected>Last 30 days</option>
                                        <option value="90">Last 90 days</option>
                                    </select>
                                </div>
                            </div>
                            <div class="card-body">
                                <canvas id="agentActivityChart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="card-title mb-0">Detailed Logs</h5>
                                <div class="d-flex">
                                    <select id="agentTypeFilter" class="form-select form-select-sm me-2">
                                        <option value="">All Agents</option>
                                        <option value="demand">Demand Agent</option>
                                        <option value="inventory">Inventory Agent</option>
                                        <option value="pricing">Pricing Agent</option>
                                    </select>
                                    <select id="limitFilter" class="form-select form-select-sm">
                                        <option value="20">20 entries</option>
                                        <option value="50">50 entries</option>
                                        <option value="100">100 entries</option>
                                    </select>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Agent Type</th>
                                                <th>Action</th>
                                                <th>Product</th>
                                                <th>Store</th>
                                                <th>Details</th>
                                                <th>Timestamp</th>
                                            </tr>
                                        </thead>
                                        <tbody id="logsTable">
                                            <tr>
                                                <td colspan="6" class="text-center">
                                                    <div class="spinner-border" role="status">
                                                        <span class="visually-hidden">Loading...</span>
                                                    </div>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const agentTypeFilter = document.getElementById('agentTypeFilter');
    const limitFilter = document.getElementById('limitFilter');
    const chartTimeFrame = document.getElementById('chartTimeFrame');
    let agentActivityChart;
    
    // Initial logs load
    loadLogs();
    
    // Event listeners for filters
    agentTypeFilter.addEventListener('change', loadLogs);
    limitFilter.addEventListener('change', loadLogs);
    chartTimeFrame.addEventListener('change', updateActivityChart);
    
    // Load logs based on filters
    function loadLogs() {
        const agentType = agentTypeFilter.value;
        const limit = limitFilter.value;
        const logsTable = document.getElementById('logsTable');
        
        // Show loading
        logsTable.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </td>
            </tr>
        `;
        
        // Build query params
        let params = new URLSearchParams();
        if (agentType) params.append('agent_type', agentType);
        params.append('limit', limit);
        
        // Fetch logs
        fetch(`/api/logs?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const logs = data.logs;
                    
                    // Update table
                    if (logs.length === 0) {
                        logsTable.innerHTML = `
                            <tr>
                                <td colspan="6" class="text-center">No logs found</td>
                            </tr>
                        `;
                    } else {
                        let tableHTML = '';
                        logs.forEach(log => {
                            // Parse details if it's a JSON string
                            let details = log.details || '';
                            try {
                                if (details) {
                                    const parsedDetails = JSON.parse(details);
                                    details = Object.entries(parsedDetails)
                                        .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
                                        .join('<br>');
                                }
                            } catch (e) {
                                // If not valid JSON, use as-is
                            }
                            
                            // Format log entry
                            tableHTML += `
                                <tr>
                                    <td>
                                        <span class="badge rounded-pill bg-${getAgentColor(log.agent_type)}">
                                            ${capitalize(log.agent_type)}
                                        </span>
                                    </td>
                                    <td>${log.action}</td>
                                    <td>${log.product_name || 'N/A'}</td>
                                    <td>${log.store_name || 'N/A'}</td>
                                    <td>${details}</td>
                                    <td>${new Date(log.timestamp).toLocaleString()}</td>
                                </tr>
                            `;
                        });
                        logsTable.innerHTML = tableHTML;
                    }
                    
                    // Get all logs for chart
                    updateActivityChart();
                } else {
                    console.error('Error fetching logs');
                    logsTable.innerHTML = `
                        <tr>
                            <td colspan="6" class="text-center text-danger">Error loading logs</td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                logsTable.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-danger">Error connecting to the server</td>
                    </tr>
                `;
            });
    }
    
    // Update activity chart
    function updateActivityChart() {
        // Get days for time frame
        const days = parseInt(chartTimeFrame.value);
        
        // Fetch all logs for charting
        fetch(`/api/logs?limit=1000`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const logs = data.logs;
                    
                    // Process logs for chart
                    const agentCounts = {
                        'demand': 0,
                        'inventory': 0,
                        'pricing': 0
                    };
                    
                    // Calculate cutoff date
                    const cutoffDate = new Date();
                    cutoffDate.setDate(cutoffDate.getDate() - days);
                    
                    // Count recent actions by agent type
                    logs.forEach(log => {
                        const logDate = new Date(log.timestamp);
                        if (logDate >= cutoffDate) {
                            agentCounts[log.agent_type] = (agentCounts[log.agent_type] || 0) + 1;
                        }
                    });
                    
                    // Create or update chart
                    const ctx = document.getElementById('agentActivityChart').getContext('2d');
                    
                    const chartData = {
                        labels: ['Demand Agent', 'Inventory Agent', 'Pricing Agent'],
                        datasets: [{
                            label: 'Number of Actions',
                            data: [
                                agentCounts['demand'],
                                agentCounts['inventory'],
                                agentCounts['pricing']
                            ],
                            backgroundColor: [
                                'rgba(54, 162, 235, 0.7)',
                                'rgba(75, 192, 192, 0.7)',
                                'rgba(255, 159, 64, 0.7)'
                            ],
                            borderColor: [
                                'rgba(54, 162, 235, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(255, 159, 64, 1)'
                            ],
                            borderWidth: 1
                        }]
                    };
                    
                    // Destroy previous chart if exists
                    if (agentActivityChart) {
                        agentActivityChart.destroy();
                    }
                    
                    // Create new chart
                    agentActivityChart = new Chart(ctx, {
                        type: 'bar',
                        data: chartData,
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Number of Actions'
                                    }
                                }
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: `Agent Activity (Last ${days} Days)`
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
    // Helper functions
    function getAgentColor(agentType) {
        switch (agentType) {
            case 'demand': return 'primary';
            case 'inventory': return 'success';
            case 'pricing': return 'warning';
            default: return 'secondary';
        }
    }
    
    function capitalize(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});
</script>
{% endblock %}'''

# Write the HTML files
with open('templates/base.html', 'w') as f:
    f.write(base_html)

with open('templates/index.html', 'w') as f:
    f.write(index_html)

with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard_html)

with open('templates/logs.html', 'w') as f:
    f.write(logs_html)

# Create custom CSS file
custom_css = '''/* Custom styles for the AI Inventory Optimization System */

/* Dark-mode compatible styles */
body {
    padding-bottom: 70px;
}

.navbar-brand svg {
    vertical-align: text-bottom;
}

.card {
    margin-bottom: 20px;
    border-radius: 8px;
}

.card-header {
    border-radius: 8px 8px 0 0 !important;
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    z-index: 1000;
}

/* Dashboard styles */
.dashboard-number {
    font-size: 2rem;
    font-weight: bold;
}

.dashboard-label {
    font-size: 0.9rem;
    color: var(--bs-secondary);
}

/* Chart container */
.chart-container {
    position: relative;
    height: 300px;
    width: 100%;
}

/* Status indicators */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}

.status-low {
    background-color: var(--bs-danger);
}

.status-medium {
    background-color: var(--bs-warning);
}

.status-good {
    background-color: var(--bs-success);
}

/* Agent type badges */
.badge-demand {
    background-color: var(--bs-primary);
}

.badge-inventory {
    background-color: var(--bs-success);
}

.badge-pricing {
    background-color: var(--bs-warning);
    color: var(--bs-dark);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .card-title {
        font-size: 1.25rem;
    }
    
    .dashboard-number {
        font-size: 1.5rem;
    }
}
'''

with open('static/css/custom.css', 'w') as f:
    f.write(custom_css)

# Create JavaScript utilities for charts
chart_utils_js = '''// Chart.js utility functions

// Function to create a color with opacity
function createColor(color, opacity = 1) {
    return `rgba(${color}, ${opacity})`;
}

// Common chart colors (RGB values)
const chartColors = {
    blue: '54, 162, 235',
    red: '255, 99, 132',
    green: '75, 192, 192',
    yellow: '255, 205, 86',
    purple: '153, 102, 255',
    orange: '255, 159, 64'
};

// Function to create datasets with consistent colors
function createDataset(label, data, colorName = 'blue', options = {}) {
    const color = chartColors[colorName] || chartColors.blue;
    
    return {
        label,
        data,
        backgroundColor: createColor(color, 0.2),
        borderColor: createColor(color, 1),
        borderWidth: 2,
        tension: 0.1,
        ...options
    };
}

// Function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Function to format percentage
function formatPercent(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// Common chart options
const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        tooltip: {
            mode: 'index',
            intersect: false
        }
    }
};

// Prediction chart options
const predictionChartOptions = {
    ...commonChartOptions,
    scales: {
        x: {
            title: {
                display: true,
                text: 'Date'
            }
        },
        y: {
            beginAtZero: true,
            title: {
                display: true,
                text: 'Demand'
            }
        }
    }
};
'''

with open('static/js/chart_utils.js', 'w') as f:
    f.write(chart_utils_js)

# Create main JavaScript file
main_js = '''// Main JavaScript functionality for the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Show current date in header if element exists
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        currentDateElement.textContent = now.toLocaleDateString('en-US', options);
    }
    
    // Handle collapsible cards
    const cardToggles = document.querySelectorAll('.card-toggle');
    cardToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement.classList.contains('show')) {
                targetElement.classList.remove('show');
                this.innerHTML = '<i class="fas fa-chevron-down"></i>';
            } else {
                targetElement.classList.add('show');
                this.innerHTML = '<i class="fas fa-chevron-up"></i>';
            }
        });
    });
});

// Function to format dates for API requests
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Function to show loading indicator
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center my-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    }
}

// Function to show error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}
'''

with open('static/js/main.js', 'w') as f:
    f.write(main_js)

print("Templates and assets created successfully.")