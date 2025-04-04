// Chart.js utility functions

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
