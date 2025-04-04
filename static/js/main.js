/**
 * Main JavaScript file for the AI Inventory Optimization System
 * Contains global utility functions and initialization code
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Inventory Optimization System initialized');
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

/**
 * Format a number with commas as thousands separators
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format a date as a string
 * @param {Date|string} date - Date object or date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(date, includeTime = false) {
    const d = new Date(date);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return d.toLocaleDateString('en-US', options);
}

/**
 * Format a price with currency symbol
 * @param {number} price - The price to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted price
 */
function formatPrice(price, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(price);
}

/**
 * Calculate the percentage change between two values
 * @param {number} oldValue - Original value
 * @param {number} newValue - New value
 * @returns {number} Percentage change
 */
function calculatePercentageChange(oldValue, newValue) {
    if (oldValue === 0) return newValue > 0 ? 100 : 0;
    return ((newValue - oldValue) / Math.abs(oldValue)) * 100;
}

/**
 * Format a percentage value
 * @param {number} value - Percentage value
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage
 */
function formatPercentage(value, decimals = 1) {
    return `${value > 0 ? '+' : ''}${value.toFixed(decimals)}%`;
}

/**
 * Show a success toast notification
 * @param {string} message - Message to display
 */
function showSuccessToast(message) {
    showToast(message, 'success');
}

/**
 * Show an error toast notification
 * @param {string} message - Message to display
 */
function showErrorToast(message) {
    showToast(message, 'danger');
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast bg-${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">AI Inventory System</strong>
                <small>${formatDate(new Date(), true)}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body text-${type === 'warning' ? 'dark' : 'white'}">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
