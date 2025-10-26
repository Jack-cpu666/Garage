// Metropolis Parking Management - Frontend JavaScript

// Initialize Socket.IO
const socket = io();

// State
let monitoringActive = false;
let tokenMonitorActive = false;

// ==================== Tab Management ====================

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');

            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');

            // Load data for certain tabs
            if (tabName === 'members') loadMembers();
            if (tabName === 'blacklist') loadBlacklist();
            if (tabName === 'visits') loadVisits();
            if (tabName === 'occupancy') loadOccupancy();
        });
    });
}

// ==================== Gate Controls ====================

async function openGate(laneId, gateName, siteId) {
    const statusEl = document.getElementById('gate-status');
    statusEl.textContent = `Opening ${gateName}...`;
    statusEl.style.color = '#FFA726';

    try {
        const response = await fetch('/api/gate/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lane_id: laneId,
                gate_name: gateName,
                site_id: siteId
            })
        });

        const data = await response.json();

        if (data.success) {
            statusEl.textContent = `✓ ${gateName} opened!`;
            statusEl.style.color = '#4CAF50';
        } else {
            statusEl.textContent = `✗ Failed to open ${gateName}`;
            statusEl.style.color = '#F44336';
        }

        // Reset status after 3 seconds
        setTimeout(() => {
            statusEl.textContent = 'Ready';
            statusEl.style.color = '';
        }, 3000);

    } catch (error) {
        console.error('Error opening gate:', error);
        statusEl.textContent = '✗ Error opening gate';
        statusEl.style.color = '#F44336';
    }
}

async function openAllGates() {
    if (!confirm('Open ALL gates at BOTH sites?\n\n- 6th Street Exit (4005)\n- L Street Exit (4005)\n- Bank of America Exit (4007)\n\nContinue?')) {
        return;
    }

    const gates = [
        ['5568', '6th Street Exit', '4005'],
        ['5569', 'L Street Exit', '4005'],
        ['5565', 'Bank of America Exit', '4007']
    ];

    for (const [laneId, name, siteId] of gates) {
        await openGate(laneId, name, siteId);
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    alert('All gates have been opened!');
}

// ==================== Monitoring ====================

function toggleMonitoring() {
    const btn = document.getElementById('toggle-monitor-btn');
    const statusIcon = document.getElementById('monitor-status-icon');
    const statusText = document.getElementById('monitor-status-text');

    if (!monitoringActive) {
        socket.emit('start_monitoring');
        monitoringActive = true;
        btn.textContent = 'Stop Monitoring';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-danger');
        statusIcon.textContent = '🟢';
        statusText.textContent = 'Monitoring: ON';
    } else {
        socket.emit('stop_monitoring');
        monitoringActive = false;
        btn.textContent = 'Start Monitoring';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-success');
        statusIcon.textContent = '⚫';
        statusText.textContent = 'Monitoring: OFF';
    }
}

// ==================== Members Management ====================

async function loadMembers() {
    try {
        const response = await fetch('/api/members');
        const data = await response.json();

        const listEl = document.getElementById('members-list');
        listEl.innerHTML = '';

        if (data.members.length === 0) {
            listEl.innerHTML = '<li style="text-align: center; color: #888;">No members added yet</li>';
            return;
        }

        data.members.forEach(plate => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="plate-text">${plate}</span>
                <button class="remove-btn" onclick="removeMember('${plate}')">Remove</button>
            `;
            listEl.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading members:', error);
    }
}

async function addMember() {
    const input = document.getElementById('member-plate-input');
    const plate = input.value.trim().toUpperCase();

    if (!plate) {
        alert('Please enter a license plate');
        return;
    }

    try {
        const response = await fetch('/api/members/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plate })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            loadMembers();
            alert(`Added ${plate} to members`);
        } else {
            alert(data.message || 'Failed to add member');
        }
    } catch (error) {
        console.error('Error adding member:', error);
        alert('Error adding member');
    }
}

async function removeMember(plate) {
    if (!confirm(`Remove ${plate} from members?`)) {
        return;
    }

    try {
        const response = await fetch('/api/members/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plate })
        });

        const data = await response.json();

        if (data.success) {
            loadMembers();
            alert(`Removed ${plate}`);
        } else {
            alert(data.message || 'Failed to remove member');
        }
    } catch (error) {
        console.error('Error removing member:', error);
        alert('Error removing member');
    }
}

// ==================== Blacklist Management ====================

async function loadBlacklist() {
    try {
        const response = await fetch('/api/blacklist');
        const data = await response.json();

        const listEl = document.getElementById('blacklist-list');
        listEl.innerHTML = '';

        if (data.blacklist.length === 0) {
            listEl.innerHTML = '<li style="text-align: center; color: #888;">No blacklisted plates</li>';
            return;
        }

        data.blacklist.forEach(plate => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="plate-text">${plate}</span>
                <button class="remove-btn" onclick="removeBlacklist('${plate}')">Remove</button>
            `;
            listEl.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading blacklist:', error);
    }
}

async function addBlacklist() {
    const input = document.getElementById('blacklist-plate-input');
    const plate = input.value.trim().toUpperCase();

    if (!plate) {
        alert('Please enter a license plate');
        return;
    }

    if (!confirm(`Add ${plate} to blacklist?\n\nThis vehicle will be BLOCKED even if it's a member.`)) {
        return;
    }

    try {
        const response = await fetch('/api/blacklist/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plate })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            loadBlacklist();
            alert(`Added ${plate} to blacklist`);
        } else {
            alert(data.message || 'Failed to add to blacklist');
        }
    } catch (error) {
        console.error('Error adding to blacklist:', error);
        alert('Error adding to blacklist');
    }
}

async function removeBlacklist(plate) {
    if (!confirm(`Remove ${plate} from blacklist?`)) {
        return;
    }

    try {
        const response = await fetch('/api/blacklist/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ plate })
        });

        const data = await response.json();

        if (data.success) {
            loadBlacklist();
            alert(`Removed ${plate} from blacklist`);
        } else {
            alert(data.message || 'Failed to remove from blacklist');
        }
    } catch (error) {
        console.error('Error removing from blacklist:', error);
        alert('Error removing from blacklist');
    }
}

// ==================== Token Management ====================

async function refreshToken() {
    if (!confirm('Manually refresh authentication token?\n\nThis will use headless browser to get a new token.')) {
        return;
    }

    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '🔄 Refreshing...';

    try {
        const response = await fetch('/api/token/refresh', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            alert('Token refreshed successfully!\n\nThe application will now use the new token.');
            location.reload();
        } else {
            alert('Failed to refresh token.\n\nCheck console for details.');
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        alert('Error refreshing token');
    } finally {
        btn.disabled = false;
        btn.textContent = '🧪 Test Token Refresh';
    }
}

function toggleTokenMonitor() {
    const btn = document.getElementById('toggle-token-monitor-btn');
    const statusIcon = document.getElementById('token-monitor-status-icon');
    const statusText = document.getElementById('token-monitor-status-text');

    if (!tokenMonitorActive) {
        socket.emit('start_token_monitor');
        tokenMonitorActive = true;
        btn.textContent = 'Stop Auto-Monitor';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-danger');
        statusIcon.textContent = '🟢';
        statusText.textContent = 'Auto-Monitor: ON - Checking every 3 minutes';
    } else {
        socket.emit('stop_token_monitor');
        tokenMonitorActive = false;
        btn.textContent = 'Start Auto-Monitor';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-success');
        statusIcon.textContent = '⚫';
        statusText.textContent = 'Auto-Monitor: OFF';
    }
}

// ==================== Visits & Occupancy ====================

async function loadVisits() {
    const sites = ['4005', '4007'];

    for (const siteId of sites) {
        const el = document.getElementById(`visits-${siteId}`);
        el.textContent = 'Loading...';

        try {
            const response = await fetch(`/api/visits/${siteId}?count=10`);
            const data = await response.json();

            if (data.success && data.data) {
                el.textContent = JSON.stringify(data.data, null, 2);
            } else {
                el.textContent = 'No data available';
            }
        } catch (error) {
            console.error(`Error loading visits for site ${siteId}:`, error);
            el.textContent = 'Error loading data';
        }
    }
}

async function loadOccupancy() {
    const sites = ['4005', '4007'];

    for (const siteId of sites) {
        const el = document.getElementById(`occupancy-${siteId}`);
        el.textContent = 'Loading...';

        try {
            const response = await fetch(`/api/occupancy/${siteId}`);
            const data = await response.json();

            if (data.success && data.data) {
                el.textContent = JSON.stringify(data.data, null, 2);
            } else {
                el.textContent = 'No data available';
            }
        } catch (error) {
            console.error(`Error loading occupancy for site ${siteId}:`, error);
            el.textContent = 'Error loading data';
        }
    }
}

// ==================== Socket.IO Events ====================

socket.on('connected', (data) => {
    console.log('Connected to server:', data);
});

socket.on('monitoring_update', (data) => {
    const logBox = document.getElementById('monitor-log');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${data.message}`;
    logBox.appendChild(entry);
    logBox.scrollTop = logBox.scrollHeight;
});

socket.on('token_update', (data) => {
    const statusText = document.getElementById('token-monitor-status-text');
    statusText.textContent = `Auto-Monitor: ON - ${data.message}`;
});

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Metropolis Parking Management...');

    // Initialize tabs
    initTabs();

    // Load initial data
    loadMembers();
    loadBlacklist();

    console.log('Initialization complete');
});
