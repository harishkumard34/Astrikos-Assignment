const BACKEND_URL = ""; // Empty string means it will use the current domain

const devicesGrid = document.getElementById("devices-grid");
const alertsList = document.getElementById("alerts-list");

// Store seen alerts so we don't re-animate them
let seenAlerts = new Set();

async function fetchStatus() {
    try {
        const response = await fetch(`${BACKEND_URL}/status`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        renderDashboard(data);
    } catch (error) {
        console.error("Failed to fetch status:", error);
    }
}

function renderDashboard(data) {
    // 1. Render Devices
    devicesGrid.innerHTML = '';
    
    // Check if there are active alerts to mark cards as danger/warning
    const alertsByDevice = {};
    data.alerts.forEach(a => {
        if (!alertsByDevice[a.device_id]) alertsByDevice[a.device_id] = [];
        alertsByDevice[a.device_id].push(a.type);
    });

    for (const [deviceId, metrics] of Object.entries(data.devices)) {
        const card = document.createElement("div");
        card.className = "device-card";
        card.id = `device-${deviceId}`;
        
        // Determine card color based on alerts
        if (alertsByDevice[deviceId]) {
            if (alertsByDevice[deviceId].includes("SENSOR_FAULT")) {
                card.classList.add("danger");
            } else if (alertsByDevice[deviceId].includes("GRADUAL_FAILURE")) {
                card.classList.add("warning");
            }
        }

        let metricsHtml = '';
        for (const [metric, value] of Object.entries(metrics)) {
            metricsHtml += `
                <div class="metric">
                    <span class="metric-name">${metric.replace('_', ' ')}</span>
                    <span class="metric-value">${typeof value === 'number' ? value.toFixed(2) : value}</span>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="device-header">
                <span class="device-name">${deviceId}</span>
            </div>
            <div class="device-metrics">
                ${metricsHtml}
            </div>
        `;
        devicesGrid.appendChild(card);
    }

    // 2. Render Alerts
    if (data.alerts.length === 0) {
        alertsList.innerHTML = '<div class="empty-state">No active alerts. System healthy.</div>';
        seenAlerts.clear();
    } else {
        // Only render if there's a change or first load to avoid flickering
        // Re-building whole list for simplicity but adding animation only to new ones
        let newHtml = '';
        data.alerts.forEach(alert => {
            const isNew = !seenAlerts.has(alert.timestamp);
            seenAlerts.add(alert.timestamp);
            
            const timeStr = new Date(alert.timestamp).toLocaleTimeString();
            const alertClass = alert.type.toLowerCase();
            
            // If it's not new, strip the animation class to avoid re-playing
            const animStyle = isNew ? '' : 'style="animation: none;"';
            
            newHtml += `
                <div class="alert-item ${alertClass}" ${animStyle} onclick="highlightDevice('${alert.device_id}')">
                    <div class="alert-header">
                        <span>${alert.device_id} • ${alert.metric}</span>
                        <span>${timeStr}</span>
                    </div>
                    <div class="alert-message">
                        <strong>[${alert.type.replace('_', ' ')}]</strong> ${alert.message}
                    </div>
                </div>
            `;
        });
        
        // Only update DOM if HTML changed (basic diffing)
        if (alertsList.innerHTML !== newHtml) {
            alertsList.innerHTML = newHtml;
        }
    }
}

// Poll every 1 second
setInterval(fetchStatus, 1000);
fetchStatus(); // initial fetch

window.highlightDevice = function(deviceId) {
    const card = document.getElementById(`device-${deviceId}`);
    if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.add('highlight-pulse');
        setTimeout(() => {
            card.classList.remove('highlight-pulse');
        }, 2000);
    }
};
