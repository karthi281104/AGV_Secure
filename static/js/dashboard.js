class Dashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.showLoading();
        this.setupEventListeners();
        this.loadUserProfile();
        this.loadDashboardData();
        this.updateCurrentTime();
        this.setupAutoRefresh();
        this.hideLoading();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobileToggle');
        const sidebar = document.getElementById('sidebar');

        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });

        // Chart period change
        const chartPeriod = document.getElementById('chartPeriod');
        if (chartPeriod) {
            chartPeriod.addEventListener('change', () => {
                this.updateCharts();
            });
        }

        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 1000);
        }
    }

    async loadUserProfile() {
        try {
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const user = await response.json();
                this.updateUserProfile(user);
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
            this.setDefaultProfile();
        }
    }

    updateUserProfile(user) {
        const profileName = document.getElementById('profileName');
        const profileRole = document.getElementById('profileRole');
        const profileAvatar = document.getElementById('profileAvatar');

        if (profileName) profileName.textContent = user.name || 'Employee';
        if (profileRole) profileRole.textContent = user.role || 'Employee';
        if (profileAvatar) {
            profileAvatar.src = user.picture ||
                `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || 'User')}&background=667eea&color=fff&size=128`;
        }
    }

    setDefaultProfile() {
        const profileName = document.getElementById('profileName');
        const profileRole = document.getElementById('profileRole');
        const profileAvatar = document.getElementById('profileAvatar');

        if (profileName) profileName.textContent = 'Employee';
        if (profileRole) profileRole.textContent = 'Employee';
        if (profileAvatar) {
            profileAvatar.src = 'https://ui-avatars.com/api/?name=Employee&background=667eea&color=fff&size=128';
        }
    }

    updateCurrentTime() {
        const currentTimeElement = document.getElementById('currentTime');
        if (currentTimeElement) {
            const now = new Date();
            const options = {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            currentTimeElement.textContent = now.toLocaleDateString('en-US', options);
        }

        // Update every minute
        setTimeout(() => this.updateCurrentTime(), 60000);
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard/stats');
            if (response.ok) {
                const data = await response.json();
                this.updateStats(data);
                this.updateCharts(data);
                this.updateRecentActivity(data);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorState();
        }
    }

    updateStats(data) {
        // Update stat values
        this.animateCountUp('totalCustomers', data.total_customers || 0);
        this.animateCountUp('totalDisbursed', data.total_disbursed || 0, true);
        this.animateCountUp('totalInterest', data.total_interest || 0, true);
        this.animateCountUp('activeLoans', data.active_loans || 0);

        // Update change indicators with actual data
        const customersChange = data.customers_change || 0;
        const disbursedChange = data.disbursed_change || 0;
        const interestChange = data.interest_change || 0;
        const loansChange = data.loans_change || 0;

        this.updateChangeIndicator('customersChange', 
            `${customersChange > 0 ? '+' : ''}${customersChange.toFixed(1)}% from last month`, 
            customersChange >= 0 ? 'positive' : 'negative');
        this.updateChangeIndicator('disbursedChange', 
            `${disbursedChange > 0 ? '+' : ''}${disbursedChange.toFixed(1)}% from last month`, 
            disbursedChange >= 0 ? 'positive' : 'negative');
        this.updateChangeIndicator('interestChange', 
            `${interestChange > 0 ? '+' : ''}${interestChange.toFixed(1)}% from last month`, 
            interestChange >= 0 ? 'positive' : 'negative');
        this.updateChangeIndicator('loansChange', 
            `${loansChange > 0 ? '+' : ''}${loansChange.toFixed(1)}% from last month`, 
            loansChange >= 0 ? 'positive' : 'negative');
    }

    animateCountUp(elementId, finalValue, isCurrency = false) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const duration = 2000;
        const startTime = Date.now();

        const animate = () => {
            const currentTime = Date.now();
            const progress = Math.min((currentTime - startTime) / duration, 1);

            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (finalValue - startValue) * easeOutQuart;

            if (isCurrency) {
                element.textContent = this.formatCurrency(currentValue);
            } else {
                element.textContent = Math.floor(currentValue).toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    formatCurrency(amount) {
        if (amount >= 10000000) { // 1 crore
            return `₹${(amount / 10000000).toFixed(1)}Cr`;
        } else if (amount >= 100000) { // 1 lakh
            return `₹${(amount / 100000).toFixed(1)}L`;
        } else if (amount >= 1000) { // 1 thousand
            return `₹${(amount / 1000).toFixed(1)}K`;
        } else {
            return `₹${amount.toFixed(0)}`;
        }
    }

    updateChangeIndicator(elementId, change, type) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.className = `stat-change ${type}`;
        element.innerHTML = `
            <i class="fas fa-arrow-${type === 'positive' ? 'up' : 'down'}"></i>
            ${change}
        `;
    }

    updateCharts(data) {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not available - displaying fallback content');
            this.showChartFallback();
            return;
        }
        
        this.createDisbursementChart(data);
        this.createLoanTypesChart(data);
    }

    showChartFallback() {
        // Show fallback content for charts when Chart.js is not available
        const disbursementContainer = document.getElementById('disbursementChart');
        const loanTypesContainer = document.getElementById('loanTypesChart');
        
        if (disbursementContainer) {
            disbursementContainer.parentElement.innerHTML = `
                <div class="chart-fallback">
                    <i class="fas fa-chart-line"></i>
                    <p>Chart visualization unavailable</p>
                    <small>Chart.js library required for data visualization</small>
                </div>
            `;
        }
        
        if (loanTypesContainer) {
            loanTypesContainer.parentElement.innerHTML = `
                <div class="chart-fallback">
                    <i class="fas fa-chart-pie"></i>
                    <p>Chart visualization unavailable</p>
                    <small>Chart.js library required for data visualization</small>
                </div>
            `;
        }
    }

    createDisbursementChart(data) {
        const ctx = document.getElementById('disbursementChart');
        if (!ctx || typeof Chart === 'undefined') return;

        // Destroy existing chart if it exists
        if (this.charts.disbursement) {
            this.charts.disbursement.destroy();
        }

        // Sample data - replace with actual data from backend
        const monthlyData = data.monthlyData || [
            { month: 1, amount: 4500000 },
            { month: 2, amount: 5200000 },
            { month: 3, amount: 4800000 },
            { month: 4, amount: 6100000 },
            { month: 5, amount: 5800000 },
            { month: 6, amount: 7200000 }
        ];

        const labels = monthlyData.map(d => {
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return months[d.month - 1];
        });

        const amounts = monthlyData.map(d => d.amount);

        this.charts.disbursement = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Disbursement Amount',
                    data: amounts,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `Amount: ${this.formatCurrency(context.raw)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#64748b'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            color: '#64748b',
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    createLoanTypesChart(data) {
        const ctx = document.getElementById('loanTypesChart');
        if (!ctx || typeof Chart === 'undefined') return;

        // Destroy existing chart if it exists
        if (this.charts.loanTypes) {
            this.charts.loanTypes.destroy();
        }

        this.charts.loanTypes = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Gold Loans', 'Land Loans', 'Bond Loans', 'Others'],
                datasets: [{
                    data: [65, 20, 10, 5],
                    backgroundColor: [
                        '#667eea',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            color: '#64748b'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateRecentActivity(data) {
        this.updateRecentLoans(data.recentLoans || []);
        this.updateRecentPayments(data.recentPayments || []);
    }

    updateRecentLoans(loans) {
        const container = document.getElementById('recentLoans');
        if (!container) return;

        if (loans.length === 0) {
            container.innerHTML = '<div class="activity-loading">No recent loans</div>';
            return;
        }

        container.innerHTML = loans.map(loan => `
            <div class="activity-item">
                <div class="activity-icon" style="background: rgba(16, 185, 129, 0.1); color: #10b981;">
                    <i class="fas fa-plus-circle"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">New loan disbursed</div>
                    <div class="activity-subtitle">${loan.customer || 'N/A'} - ${this.formatCurrency(loan.amount || 0)} - ${loan.type || 'Loan'}</div>
                    <div class="activity-date">${this.formatRelativeTime(loan.date)}</div>
                </div>
            </div>
        `).join('');
    }

    updateRecentPayments(payments) {
        const container = document.getElementById('recentPayments');
        if (!container) return;

        if (payments.length === 0) {
            container.innerHTML = '<div class="activity-loading">No recent payments</div>';
            return;
        }

        container.innerHTML = payments.map(payment => `
            <div class="activity-item">
                <div class="activity-icon" style="background: rgba(16, 185, 129, 0.1); color: #10b981;">
                    <i class="fas fa-money-bill"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Payment received</div>
                    <div class="activity-subtitle">${payment.customer || 'N/A'} - ${this.formatCurrency(payment.amount || 0)}</div>
                    <div class="activity-date">${this.formatRelativeTime(payment.date)}</div>
                </div>
            </div>
        `).join('');
    }

    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }

    setupAutoRefresh() {
        // Refresh dashboard data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }

    handleResize() {
        // Redraw charts on resize
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }

    showErrorState() {
        const statsCards = document.querySelectorAll('.stat-value');
        statsCards.forEach(card => {
            card.textContent = 'Error';
        });

        const activityContainers = ['recentLoans', 'recentPayments'];
        activityContainers.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.innerHTML = '<div class="activity-loading">Error loading data</div>';
            }
        });
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});