// Auralite Main JavaScript

// Global variables
let refreshInterval = null;

// Initialize on document ready
$(document).ready(function() {
    console.log('Auralite initialized');
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-refresh for dashboard
    if (window.location.pathname === '/dashboard') {
        startAutoRefresh(30000); // Refresh every 30 seconds
    }
    
    // Load notifications
    loadNotifications();
});

// Start auto-refresh
function startAutoRefresh(interval) {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    refreshInterval = setInterval(function() {
        refreshData();
    }, interval);
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Refresh dashboard data
function refreshData() {
    console.log('Refreshing data...');
    
    // Update stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStats(data.stats);
            }
        });
    
    // Update recent detections
    fetch('/api/detections?limit=10')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDetections(data.detections);
            }
        });
}

// Update stats display
function updateStats(stats) {
    // Update stats cards if they exist
    $('.stats-card').each(function(index, card) {
        // Implementation depends on your specific card structure
        console.log('Updating stats:', stats);
    });
}

// Update detections table
function updateDetections(detections) {
    const tableBody = $('#detectionsTable tbody');
    if (tableBody.length) {
        tableBody.empty();
        
        detections.forEach(d => {
            const row = `
                <tr>
                    <td>${d.timestamp}</td>
                    <td>${d.location_name}</td>
                    <td><span class="badge bg-warning">${d.detection_type}</span></td>
                    <td>${(d.confidence * 100).toFixed(1)}%</td>
                    <td>${Math.round(d.duration_seconds)}s</td>
                    <td>
                        ${d.confidence > 0.9 ? 
                            '<span class="badge bg-danger">Critical</span>' : 
                            d.confidence > 0.75 ? 
                            '<span class="badge bg-warning">Warning</span>' : 
                            '<span class="badge bg-info">Info</span>'}
                    </td>
                </tr>
            `;
            tableBody.append(row);
        });
    }
}

// Load notifications
function loadNotifications() {
    fetch('/api/detections?limit=5')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.detections.length > 0) {
                const criticalCount = data.detections.filter(d => d.confidence > 0.9).length;
                if (criticalCount > 0) {
                    showNotification(
                        'Critical Alerts',
                        `${criticalCount} critical mining activities detected`,
                        'danger'
                    );
                }
            }
        });
}

// Show notification
function showNotification(title, message, type = 'info') {
    // Create toast notification
    const toast = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add to container
    const container = $('#toastContainer');
    if (!container.length) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    $('#toastContainer').append(toast);
    $('.toast').toast('show');
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        $('.toast').first().remove();
    }, 5000);
}

// Export data
function exportData(format = 'csv') {
    fetch(`/api/detections?limit=1000`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let content = '';
                const detections = data.detections;
                
                if (format === 'csv') {
                    // Create CSV header
                    const headers = Object.keys(detections[0]).join(',');
                    const rows = detections.map(d => Object.values(d).join(',')).join('\n');
                    content = headers + '\n' + rows;
                    
                    // Download CSV
                    downloadFile(content, 'auralite_detections.csv', 'text/csv');
                } else if (format === 'json') {
                    content = JSON.stringify(detections, null, 2);
                    downloadFile(content, 'auralite_detections.json', 'application/json');
                }
            }
        });
}

// Download file helper
function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type: type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleString();
}

// Calculate risk color
function getRiskColor(risk) {
    switch(risk.toLowerCase()) {
        case 'high': return '#e74c3c';
        case 'medium': return '#f39c12';
        case 'low': return '#27ae60';
        default: return '#95a5a6';
    }
}

// Handle errors
function handleError(error) {
    console.error('Error:', error);
    showNotification('Error', 'An error occurred. Please try again.', 'danger');
}
