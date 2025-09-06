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

// Customer Selection Modal Functions
class CustomerSelection {
    constructor() {
        this.customers = [];
        this.filteredCustomers = [];
        this.selectedCustomer = null;
        this.modal = null;
        this.initialized = false;
        this.init();
    }

    init() {
        try {
            const modalElement = document.getElementById('customerSelectionModal');
            if (modalElement) {
                this.modal = new bootstrap.Modal(modalElement);
                this.setupEventListeners();
                this.initialized = true;
                console.log('CustomerSelection initialized successfully');
            } else {
                console.error('Modal element not found');
            }
        } catch (error) {
            console.error('Error initializing CustomerSelection:', error);
        }
    }

    setupEventListeners() {
        const searchInput = document.getElementById('customerSearchInput');
        const clearButton = document.getElementById('clearSearch');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterCustomers(e.target.value);
            });
        }
        
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                searchInput.value = '';
                this.filterCustomers('');
            });
        }
    }

    async show() {
        console.log('CustomerSelection.show() called');
        if (!this.initialized) {
            console.error('CustomerSelection not initialized');
            return;
        }
        
        try {
            this.modal.show();
            console.log('Modal shown, loading customers...');
            await this.loadCustomers();
            console.log('Customers loaded successfully');
        } catch (error) {
            console.error('Error in show():', error);
        }
    }

    async loadCustomers() {
        console.log('loadCustomers() called');
        const customerList = document.getElementById('customerList');
        const noCustomersFound = document.getElementById('noCustomersFound');
        
        if (!customerList) {
            console.error('customerList element not found!');
            return;
        }
        
        try {
            // Show loading state
            customerList.innerHTML = `
                <div class="col-12">
                    <div class="text-center p-5">
                        <div class="spinner-border text-primary mb-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <h5 class="text-muted">Loading customers...</h5>
                        <p class="text-muted">Fetching customer data from database</p>
                    </div>
                </div>
            `;

            console.log('Fetching customers from API...');
            
            // Try to fetch from the API first
            try {
                const response = await fetch('/api/customers', {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('API Response status:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('API Data received:', data);
                    
                    this.customers = data.customers || [];
                    this.filteredCustomers = [...this.customers];

                    console.log('Number of customers from API:', this.customers.length);

                    if (this.customers.length === 0) {
                        customerList.innerHTML = '';
                        noCustomersFound.classList.remove('d-none');
                    } else {
                        noCustomersFound.classList.add('d-none');
                        this.renderCustomers();
                    }
                    return;
                } else {
                    console.warn('API response not OK:', response.status, response.statusText);
                    throw new Error(`API returned ${response.status}: ${response.statusText}`);
                }
            } catch (apiError) {
                console.error('API fetch failed:', apiError);
                
                // Show error message but also load fallback data
                customerList.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>API Error:</strong> ${apiError.message}
                            <br><small>Loading sample data for demonstration...</small>
                        </div>
                    </div>
                `;
                
                // Wait a moment then load sample data
                setTimeout(() => {
                    this.loadSampleData();
                }, 1000);
            }

        } catch (error) {
            console.error('Error loading customers:', error);
            customerList.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-exclamation-triangle fa-2x me-3"></i>
                            <div>
                                <h5 class="alert-heading">Error loading customers</h5>
                                <p class="mb-2">${error.message}</p>
                                <button class="btn btn-outline-danger btn-sm" onclick="customerSelection.loadCustomers()">
                                    <i class="fas fa-redo me-1"></i>
                                    Try Again
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    loadSampleData() {
        console.log('Loading sample customer data...');
        
        // Use the actual customer data from your database as fallback
        this.customers = [
            {
                id: '89811f8e-bb1a-4100-b33f-238478faaf43',
                name: 'Karthikeyan A',
                father_name: 'Karthikeyan Father',
                mobile: '0861033707',
                email: null,
                address: 'No:7A Theeran Sivalingam Street,Kabilar Nagar,Manavalanagar',
                created_at: '2024-01-15T00:00:00'
            },
            {
                id: '869684df-50a4-4a5c-af1c-ba61e0d7a383',
                name: 'vasanth',
                father_name: 'EFGHJ',
                mobile: '0861033707',
                email: null,
                address: 'No:7A Theeran Sivalingam Street,Kabilar Nagar,Manavalanagar',
                created_at: '2024-02-20T00:00:00'
            },
            {
                id: '3ca3869b-ff95-4c02-a6a6-35ec4f0fb269',
                name: 'VK',
                father_name: 'VK FATHER',
                mobile: '8478282654',
                email: null,
                address: 'NO.15 MCK LAYOUT SAN FRANSICO COLUMBIA',
                created_at: '2024-03-10T00:00:00'
            }
        ];
        
        this.filteredCustomers = [...this.customers];
        console.log('Sample customers loaded:', this.customers.length);

        const customerList = document.getElementById('customerList');
        const noCustomersFound = document.getElementById('noCustomersFound');

        if (this.customers.length === 0) {
            customerList.innerHTML = '';
            noCustomersFound.classList.remove('d-none');
        } else {
            noCustomersFound.classList.add('d-none');
            this.renderCustomers();
        }
    }

    filterCustomers(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredCustomers = [...this.customers];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredCustomers = this.customers.filter(customer => 
                customer.name.toLowerCase().includes(term) ||
                customer.mobile.includes(term) ||
                (customer.email && customer.email.toLowerCase().includes(term)) ||
                customer.id.toLowerCase().includes(term) ||
                (customer.father_name && customer.father_name.toLowerCase().includes(term))
            );
        }
        this.renderCustomers();
    }

    renderCustomers() {
        const customerList = document.getElementById('customerList');
        const noCustomersFound = document.getElementById('noCustomersFound');

        if (this.filteredCustomers.length === 0) {
            customerList.innerHTML = '';
            noCustomersFound.classList.remove('d-none');
            return;
        }

        noCustomersFound.classList.add('d-none');
        
        customerList.innerHTML = this.filteredCustomers.map(customer => `
            <div class="col-md-6">
                <div class="customer-card" onclick="customerSelection.selectCustomer('${customer.id}')">
                    <div class="d-flex align-items-start">
                        <div class="customer-avatar">
                            ${customer.name.charAt(0).toUpperCase()}
                        </div>
                        <div class="flex-grow-1">
                            <div class="customer-info">
                                <h6 class="mb-2">${customer.name}</h6>
                                <div class="customer-detail">
                                    <i class="fas fa-user"></i>
                                    <span>Father: ${customer.father_name || 'N/A'}</span>
                                </div>
                                <div class="customer-detail">
                                    <i class="fas fa-phone"></i>
                                    <span>${customer.mobile}</span>
                                </div>
                                ${customer.email ? `
                                    <div class="customer-detail">
                                        <i class="fas fa-envelope"></i>
                                        <span>${customer.email}</span>
                                    </div>
                                ` : ''}
                                <div class="customer-detail">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <span>${customer.address ? customer.address.substring(0, 50) + (customer.address.length > 50 ? '...' : '') : 'No address'}</span>
                                </div>
                                <div class="customer-detail">
                                    <i class="fas fa-calendar-alt"></i>
                                    <span>Joined ${new Date(customer.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">ID: ${customer.id.substring(0, 8)}...</small>
                            <br>
                            <button class="btn btn-primary btn-sm mt-2 select-btn">
                                <i class="fas fa-check"></i>
                                Select
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    selectCustomer(customerId) {
        this.selectedCustomer = this.customers.find(c => c.id === customerId);
        
        if (this.selectedCustomer) {
            console.log('Customer selected:', this.selectedCustomer);
            // Close modal and navigate to new loan page
            this.modal.hide();
            window.location.href = `/loans/new?customer_id=${customerId}`;
        }
    }
}

// Global customer selection instance
let customerSelection;

// Function to open customer selection modal (called from dashboard quick actions)
function openCustomerSelectionModal() {
    console.log('openCustomerSelectionModal() called');
    
    if (!customerSelection) {
        console.log('Creating new CustomerSelection instance');
        customerSelection = new CustomerSelection();
    }
    
    console.log('Calling customerSelection.show()');
    customerSelection.show();
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
    
    // Initialize customer selection
    customerSelection = new CustomerSelection();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});