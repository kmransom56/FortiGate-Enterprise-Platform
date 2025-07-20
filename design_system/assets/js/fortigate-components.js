/**
 * FortiGate Professional Design System - JavaScript Components
 * Version: 2.0.0
 * Interactive components and utilities for FortiGate applications
 */

class FortiGateComponents {
    constructor() {
        this.init();
    }

    init() {
        this.initTooltips();
        this.initStatusAnimations();
        this.initDeviceInteractions();
        this.initFilterControls();
        console.log('🛡️ FortiGate Design System initialized');
    }

    /**
     * Professional Tooltip System
     */
    initTooltips() {
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
        
        tooltipTriggers.forEach(trigger => {
            const tooltip = this.createTooltip(trigger.dataset.tooltip);
            
            trigger.addEventListener('mouseenter', (e) => {
                this.showTooltip(e, tooltip);
            });
            
            trigger.addEventListener('mouseleave', () => {
                this.hideTooltip(tooltip);
            });
        });
    }

    createTooltip(content) {
        const tooltip = document.createElement('div');
        tooltip.className = 'fortigate-tooltip';
        tooltip.innerHTML = content;
        document.body.appendChild(tooltip);
        return tooltip;
    }

    showTooltip(event, tooltip) {
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        tooltip.classList.add('show');
    }

    hideTooltip(tooltip) {
        tooltip.classList.remove('show');
    }

    /**
     * Status Widget Animations
     */
    initStatusAnimations() {
        const statusWidgets = document.querySelectorAll('.status-widget');
        
        statusWidgets.forEach((widget, index) => {
            // Staggered animation on page load
            setTimeout(() => {
                widget.style.opacity = '0';
                widget.style.transform = 'translateY(20px)';
                widget.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    widget.style.opacity = '1';
                    widget.style.transform = 'translateY(0)';
                }, 100);
            }, index * 150);
        });
    }

    /**
     * Device Icon Interactions
     */
    initDeviceInteractions() {
        const deviceIcons = document.querySelectorAll('.device-icon');
        
        deviceIcons.forEach(device => {
            device.addEventListener('click', (e) => {
                this.handleDeviceClick(e.target, device);
            });
            
            device.addEventListener('mouseenter', () => {
                this.animateDeviceHover(device, true);
            });
            
            device.addEventListener('mouseleave', () => {
                this.animateDeviceHover(device, false);
            });
        });
    }

    handleDeviceClick(target, device) {
        const deviceType = device.dataset.deviceType || 'unknown';
        const deviceName = device.dataset.deviceName || 'Unnamed Device';
        
        // Create professional device info popup
        this.showDeviceModal({
            type: deviceType,
            name: deviceName,
            status: device.dataset.status || 'unknown',
            ip: device.dataset.ip || 'N/A',
            lastSeen: device.dataset.lastSeen || 'Unknown'
        });
    }

    animateDeviceHover(device, isEntering) {
        if (isEntering) {
            device.style.transform = 'scale(1.1)';
            device.style.zIndex = '20';
        } else {
            device.style.transform = 'scale(1)';
            device.style.zIndex = '10';
        }
    }

    /**
     * Professional Device Modal
     */
    showDeviceModal(deviceData) {
        const modal = document.createElement('div');
        modal.className = 'device-modal-overlay';
        modal.innerHTML = `
            <div class="device-modal glass-container">
                <div class="device-modal-header">
                    <h3><i class="fas fa-${this.getDeviceIcon(deviceData.type)}"></i> ${deviceData.name}</h3>
                    <button class="modal-close" onclick="this.closest('.device-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="device-modal-body">
                    <div class="device-info-grid">
                        <div class="info-item">
                            <label>Type:</label>
                            <span class="device-type">${deviceData.type}</span>
                        </div>
                        <div class="info-item">
                            <label>Status:</label>
                            <span class="status-indicator ${deviceData.status}"></span>
                            <span>${deviceData.status}</span>
                        </div>
                        <div class="info-item">
                            <label>IP Address:</label>
                            <span class="ip-address">${deviceData.ip}</span>
                        </div>
                        <div class="info-item">
                            <label>Last Seen:</label>
                            <span class="last-seen">${deviceData.lastSeen}</span>
                        </div>
                    </div>
                    <div class="device-actions">
                        <button class="btn-fortigate btn-sm" onclick="window.open('http://${deviceData.ip}', '_blank')">
                            <i class="fas fa-external-link-alt"></i> Manage Device
                        </button>
                        <button class="btn-fortigate btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${deviceData.ip}')">
                            <i class="fas fa-copy"></i> Copy IP
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Animate modal appearance
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.device-modal').style.transform = 'scale(1)';
        }, 10);
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    getDeviceIcon(deviceType) {
        const iconMap = {
            'fortigate': 'shield-alt',
            'fortiswitch': 'network-wired', 
            'endpoint': 'laptop',
            'server': 'server',
            'printer': 'print',
            'phone': 'phone',
            'tablet': 'tablet-alt',
            'unknown': 'question-circle'
        };
        return iconMap[deviceType.toLowerCase()] || 'question-circle';
    }

    /**
     * Filter Controls
     */
    initFilterControls() {
        const filterButtons = document.querySelectorAll('.filter-button');
        const filteredElements = document.querySelectorAll('[data-filter-category]');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.handleFilterClick(button, filterButtons, filteredElements);
            });
        });
    }

    handleFilterClick(activeButton, allButtons, elements) {
        const filterValue = activeButton.dataset.filter;
        
        // Update button states
        allButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
        
        // Filter elements
        elements.forEach(element => {
            const categories = element.dataset.filterCategory.split(',');
            
            if (filterValue === 'all' || categories.includes(filterValue)) {
                element.style.display = '';
                element.style.opacity = '1';
                element.style.transform = 'scale(1)';
            } else {
                element.style.opacity = '0';
                element.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    element.style.display = 'none';
                }, 300);
            }
        });
    }

    /**
     * Live Status Updates
     */
    async updateStatuses(apiEndpoint = '/api/status') {
        try {
            const response = await fetch(apiEndpoint);
            if (!response.ok) throw new Error('Status update failed');
            
            const data = await response.json();
            
            // Update FortiGate status
            this.updateStatusElement('fortigate-status', data.fortigate || 'Offline');
            
            // Update device counts
            if (data.devices) {
                Object.keys(data.devices).forEach(deviceType => {
                    this.updateStatusElement(`${deviceType}-count`, data.devices[deviceType]);
                });
            }
            
            // Update status indicators
            this.updateStatusIndicators(data);
            
        } catch (error) {
            console.error('Status update failed:', error);
            this.showStatusError();
        }
    }

    updateStatusElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            
            // Add update animation
            element.classList.add('status-updated');
            setTimeout(() => {
                element.classList.remove('status-updated');
            }, 1000);
        }
    }

    updateStatusIndicators(data) {
        const indicators = document.querySelectorAll('.status-indicator');
        indicators.forEach(indicator => {
            const deviceId = indicator.dataset.deviceId;
            if (deviceId && data.statuses && data.statuses[deviceId]) {
                const status = data.statuses[deviceId];
                indicator.className = `status-indicator ${status}`;
            }
        });
    }

    showStatusError() {
        const statusElements = document.querySelectorAll('[id$="-status"]');
        statusElements.forEach(element => {
            element.textContent = 'Connection Error';
            element.classList.add('status-error');
        });
    }

    /**
     * Professional Loading States
     */
    showLoading(container) {
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>Loading FortiGate data...</p>
            </div>
        `;
        container.appendChild(loader);
    }

    hideLoading(container) {
        const loader = container.querySelector('.loading-overlay');
        if (loader) {
            loader.remove();
        }
    }

    /**
     * Utility Functions
     */
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Bytes';
        
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.fortiGateComponents = new FortiGateComponents();
    
    // Start live updates every 30 seconds
    setInterval(() => {
        window.fortiGateComponents.updateStatuses();
    }, 30000);
});

// CSS for modal and animations (to be added to fortigate-design-system.css)
const additionalCSS = `
/* Device Modal Styles */
.device-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.device-modal {
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    transform: scale(0.8);
    transition: transform 0.3s ease;
}

.device-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--gray-200);
}

.device-modal-header h3 {
    margin: 0;
    color: var(--fortinet-blue);
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: var(--gray-500);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.2s ease;
}

.modal-close:hover {
    background: var(--gray-100);
    color: var(--gray-700);
}

.device-info-grid {
    display: grid;
    gap: 1rem;
    padding: 1.5rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--gray-100);
}

.info-item label {
    font-weight: var(--font-weight-semibold);
    color: var(--gray-600);
}

.device-actions {
    display: flex;
    gap: 0.5rem;
    padding: 0 1.5rem 1.5rem;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
}

/* Loading Overlay */
.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255,255,255,0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.loading-content {
    text-align: center;
    color: var(--gray-600);
}

.loading-content p {
    margin-top: 1rem;
    font-weight: var(--font-weight-medium);
}

/* Status Update Animation */
.status-updated {
    animation: statusUpdate 1s ease;
}

@keyframes statusUpdate {
    0% { background-color: transparent; }
    50% { background-color: rgba(16,185,129,0.2); }
    100% { background-color: transparent; }
}

.status-error {
    color: var(--danger-color) !important;
    animation: errorPulse 2s infinite;
}

@keyframes errorPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
`;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FortiGateComponents;
}