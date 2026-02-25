// Auralite - Aravalli Hills Monitoring System

let refreshInterval = null;

$(document).ready(function () {
    console.log('Auralite Aravalli initialized');

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

    // Auto-refresh for dashboard
    if (window.location.pathname === '/dashboard') {
        startAutoRefresh(30000);
    }
});

function startAutoRefresh(interval) {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(refreshData, interval);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function refreshData() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => {
            if (data.success) console.log('Stats refreshed:', data.stats);
        });
}

// Export data
function exportData(format) {
    fetch('/api/acoustic/all?limit=1000')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.data.length > 0) {
                if (format === 'csv') {
                    const headers = Object.keys(data.data[0]).join(',');
                    const rows = data.data.map(d => Object.values(d).join(',')).join('\n');
                    downloadFile(headers + '\n' + rows, 'auralite_detections.csv', 'text/csv');
                } else {
                    downloadFile(JSON.stringify(data.data, null, 2), 'auralite_detections.json', 'application/json');
                }
            }
        });
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function formatDate(date) {
    return new Date(date).toLocaleString();
}

function getRiskColor(risk) {
    switch (risk.toLowerCase()) {
        case 'critical': return '#8b0000';
        case 'high': return '#e74c3c';
        case 'medium': return '#f39c12';
        case 'low': return '#27ae60';
        default: return '#95a5a6';
    }
}

function getSeverityIcon(severity) {
    switch (severity) {
        case 'CRITICAL': return 'skull-crossbones';
        case 'HIGH': return 'exclamation-triangle';
        case 'MEDIUM': return 'info-circle';
        default: return 'check-circle';
    }
}
