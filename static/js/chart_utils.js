/**
 * Chart utility functions for the AI Inventory Optimization System
 * Contains helper functions for creating and updating charts
 */

/**
 * Create a line chart for demand predictions
 * @param {string} elementId - ID of the canvas element
 * @param {Array} data - Array of data points with date and value properties
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart.js chart instance
 */
function createDemandLineChart(elementId, data, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Prepare data
    const labels = data.map(item => item.date);
    const values = data.map(item => item.value);
    
    // Default options
    const defaultOptions = {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Demand Forecast'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            },
            legend: {
                position: 'top',
            }
        },
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
                    text: 'Units'
                },
                beginAtZero: true
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Demand',
                data: values,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: chartOptions
    });
}

/**
 * Create a bar chart for comparison data
 * @param {string} elementId - ID of the canvas element
 * @param {Array} labels - Array of labels
 * @param {Array} datasets - Array of dataset objects
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart.js chart instance
 */
function createBarChart(elementId, labels, datasets, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: chartOptions
    });
}

/**
 * Create a pie chart for distribution data
 * @param {string} elementId - ID of the canvas element
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 * @param {Array} colors - Array of background colors
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart.js chart instance
 */
function createPieChart(elementId, labels, data, colors = [], options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default colors if not provided
    if (!colors || colors.length === 0) {
        colors = [
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(255, 206, 86, 0.7)'
        ];
    }
    
    // Ensure we have enough colors
    while (colors.length < data.length) {
        colors = colors.concat(colors);
    }
    
    // Default options
    const defaultOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: colors.slice(0, data.length).map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: chartOptions
    });
}

/**
 * Create a gauge chart to visualize a metric with threshold ranges
 * @param {string} elementId - ID of the canvas element
 * @param {number} value - Current value to display
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @param {Object} thresholds - Object defining threshold colors
 * @param {string} label - Label for the gauge
 * @returns {Chart} Chart.js chart instance
 */
function createGaugeChart(elementId, value, min, max, thresholds = {}, label = '') {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Default thresholds
    const defaultThresholds = {
        low: { threshold: 0.33, color: 'rgba(255, 99, 132, 0.8)' },
        medium: { threshold: 0.67, color: 'rgba(255, 206, 86, 0.8)' },
        high: { threshold: 1, color: 'rgba(75, 192, 192, 0.8)' }
    };
    
    // Merge thresholds
    const chartThresholds = { ...defaultThresholds, ...thresholds };
    
    // Normalize value between 0 and 1
    const range = max - min;
    const normalizedValue = (value - min) / range;
    
    // Calculate angle for needle
    const needleAngle = normalizedValue * Math.PI;
    
    // Create chart
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [1],
                backgroundColor: function(context) {
                    const value = normalizedValue;
                    if (value <= chartThresholds.low.threshold) {
                        return chartThresholds.low.color;
                    } else if (value <= chartThresholds.medium.threshold) {
                        return chartThresholds.medium.color;
                    } else {
                        return chartThresholds.high.color;
                    }
                },
                circumference: Math.PI,
                rotation: Math.PI
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '75%',
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false },
                title: {
                    display: !!label,
                    text: label,
                    position: 'bottom'
                }
            },
            layout: {
                padding: 20
            },
            animation: {
                animateRotate: true,
                animateScale: true
            }
        },
        plugins: [{
            id: 'gauge-needle',
            afterDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                
                // Draw value text
                ctx.restore();
                ctx.font = '20px Arial';
                ctx.fillStyle = 'white';
                ctx.textBaseline = 'middle';
                ctx.textAlign = 'center';
                ctx.fillText(value, width / 2, height * 0.7);
                
                // Draw min/max labels
                ctx.font = '12px Arial';
                ctx.fillText(min, width * 0.15, height * 0.85);
                ctx.fillText(max, width * 0.85, height * 0.85);
                
                // Draw needle
                ctx.save();
                ctx.translate(width / 2, height * 0.7);
                ctx.rotate(needleAngle);
                
                ctx.beginPath();
                ctx.moveTo(0, -10);
                ctx.lineTo(height * 0.4, 0);
                ctx.lineTo(0, 10);
                ctx.fillStyle = '#444';
                ctx.fill();
                ctx.restore();
            }
        }]
    });
}

/**
 * Update an existing chart with new data
 * @param {Chart} chart - Chart.js chart instance
 * @param {Array} labels - New labels
 * @param {Array} data - New data values
 * @param {number} datasetIndex - Index of dataset to update (default: 0)
 */
function updateChart(chart, labels, data, datasetIndex = 0) {
    chart.data.labels = labels;
    chart.data.datasets[datasetIndex].data = data;
    chart.update();
}

/**
 * Generate a random color
 * @param {number} opacity - Opacity value (0-1)
 * @returns {string} RGBA color string
 */
function getRandomColor(opacity = 0.7) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Generate an array of random colors
 * @param {number} count - Number of colors to generate
 * @param {number} opacity - Opacity value (0-1)
 * @returns {Array} Array of RGBA color strings
 */
function generateColorArray(count, opacity = 0.7) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(getRandomColor(opacity));
    }
    return colors;
}
