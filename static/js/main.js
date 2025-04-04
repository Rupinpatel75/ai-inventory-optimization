/**
 * Main JavaScript for AI Inventory Optimization System
 */

// Global state for the application
const appState = {
    products: [],
    stores: [],
    llmAvailable: false,
};

// Initialize the application when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    checkLLMStatus();
    
    // Add click handler for tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Check LLM connection status
 */
function checkLLMStatus() {
    fetch('/api/llm-status')
        .then(response => response.json())
        .then(data => {
            appState.llmAvailable = data.llm_available;
            updateLLMStatusIndicator();
        })
        .catch(error => {
            console.error('Error checking LLM status:', error);
            appState.llmAvailable = false;
            updateLLMStatusIndicator();
        });
}

/**
 * Update the LLM status indicator in the UI
 */
function updateLLMStatusIndicator() {
    const statusElement = document.getElementById('llm-status');
    if (!statusElement) return;
    
    if (appState.llmAvailable) {
        statusElement.innerHTML = '<span class="badge text-bg-success me-2">LLM: Available</span>';
    } else {
        statusElement.innerHTML = '<span class="badge text-bg-warning me-2">LLM: Unavailable</span>';
    }
}

/**
 * Format currency values
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

/**
 * Format date values
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Format percentage values
 */
function formatPercent(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

/**
 * Get badge class for inventory status
 */
function getInventoryStatusBadgeClass(status) {
    status = status.toUpperCase();
    if (status === 'OUT_OF_STOCK') return 'danger';
    if (status === 'LOW_STOCK') return 'warning';
    if (status === 'ADEQUATE') return 'success';
    if (status === 'OVERSTOCKED') return 'info';
    return 'secondary';
}

/**
 * Get badge class for pricing strategy
 */
function getPricingStrategyBadgeClass(strategy) {
    strategy = strategy.toUpperCase();
    if (strategy === 'PREMIUM') return 'info';
    if (strategy === 'STANDARD') return 'primary';
    if (strategy === 'DISCOUNT') return 'warning';
    if (strategy === 'CLEARANCE') return 'danger';
    return 'secondary';
}

/**
 * Get badge class for agent type
 */
function getAgentTypeBadgeClass(agentType) {
    agentType = agentType.toLowerCase();
    if (agentType === 'demand') return 'danger';
    if (agentType === 'inventory') return 'primary';
    if (agentType === 'pricing') return 'warning';
    return 'secondary';
}

/**
 * Show an error message to the user
 */
function showErrorMessage(message) {
    // Check if we already have an alert container
    let alertContainer = document.getElementById('alert-container');
    
    if (!alertContainer) {
        // Create a container for alerts if it doesn't exist
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    // Create the alert
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.innerHTML += alertHtml;
    
    // Automatically remove the alert after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Show a success message to the user
 */
function showSuccessMessage(message) {
    // Check if we already have an alert container
    let alertContainer = document.getElementById('alert-container');
    
    if (!alertContainer) {
        // Create a container for alerts if it doesn't exist
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    // Create the alert
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-success alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.innerHTML += alertHtml;
    
    // Automatically remove the alert after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, 5000);
}
