/**
 * AI Inventory Optimization System - Main JavaScript
 * 
 * Common functions and utilities for the web application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check LLM Status on page load
    checkLLMStatus();
    
    // Set up periodic LLM status check
    setInterval(checkLLMStatus, 60000); // Check every minute
});

/**
 * Check if the LLM is available
 */
function checkLLMStatus() {
    fetch('/api/llm-status')
        .then(response => response.json())
        .then(data => {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            if (data.success) {
                if (data.llm_available) {
                    statusDot.classList.remove('status-offline');
                    statusDot.classList.add('status-online');
                    statusText.textContent = 'LLM Status: Online';
                } else {
                    statusDot.classList.remove('status-online');
                    statusDot.classList.add('status-offline');
                    statusText.textContent = 'LLM Status: Offline';
                }
            } else {
                statusDot.classList.remove('status-online');
                statusDot.classList.add('status-offline');
                statusText.textContent = 'LLM Status: Error';
            }
        })
        .catch(error => {
            console.error('Error checking LLM status:', error);
            
            // Update UI to show error
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            statusDot.classList.remove('status-online');
            statusDot.classList.add('status-offline');
            statusText.textContent = 'LLM Status: Error';
        });
}

/**
 * Format a number as currency
 */
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

/**
 * Format a date string to display format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'info') {
    // Check if toast container exists, create if not
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
}

/**
 * Get a color for a chart based on index
 */
function getChartColor(index) {
    const colors = [
        '#0dcaf0', // info
        '#0d6efd', // primary
        '#6610f2', // purple
        '#fd7e14', // orange
        '#20c997', // teal
        '#d63384', // pink
        '#198754', // success
        '#dc3545', // danger
        '#ffc107', // warning
        '#6c757d'  // secondary
    ];
    
    return colors[index % colors.length];
}

/**
 * Initialize tooltips on a page
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
