/**
 * Reports and Analytics JavaScript
 */

class ReportsManager {
    constructor() {
        this.charts = {};
        this.reportData = {};
        this.currentDateRange = 'month';
        this.init();
    }

    init() {
        this.setCurrentDate();
        this.initializeDateRanges();
        this.loadInitialData();
        this.setupEventListeners();
    }

    setCurrentDate() {
        const currentDate = new Date().toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        document.getElementById('currentDate').textContent = currentDate;
    }

    initializeDateRanges() {
        const today = new Date();
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        
        document.getElementById('fromDate').value = firstDayOfMonth.toISOString().split('T')[0];
        document.getElementById('toDate').value = today.toISOString().split('T')[0];
    }

    setupEventListeners() {
        // Date range selector
        document.getElementById('dateRange').addEventListener('change', (e) => {
            this.handleDateRangeChange(e.target.value);
        });

        // Report type filter
        document.getElementById('reportType').addEventListener('change', (e) => {
            this.filterReportsByType(e.target.value);
        });
    }

    handleDateRangeChange(range) {
        const today = new Date();
        let fromDate, toDate = today;

        switch (range) {
            case 'today':
                fromDate = today;
                break;
            case 'week':
                fromDate = new Date(today.setDate(today.getDate() - 7));
                break;
            case 'month':
                fromDate = new Date(today.getFullYear(), today.getMonth(), 1);
                break;
            case 'quarter':
                fromDate = new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3, 1);
                break;
            case 'year':
                fromDate = new Date(today.getFullYear(), 0, 1);
                break;
            case 'custom':
                // Don't auto-set dates for custom range
                return;
        }

        if (range !== 'custom') {
            document.getElementById('fromDate').value = fromDate.toISOString().split('T')[0];
            document.getElementById('toDate').value = toDate.toISOString().split('T')[0];
            this.generateReports();
        }
    }

    async loadInitialData() {
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadMetrics(),
                this.loadChartData(),
                this.loadReportTables()
            ]);
        } catch (error) {
            console.error('Error loading reports data:', error);
            this.showError('Failed to load reports data');
        } finally {
            this.showLoading(false);
        }
    }

    async loadMetrics() {
        try {
            const fromDate = document.getElementById('fromDate').value;
            const toDate = document.getElementById('toDate').value;
            
            const response = await fetch(`/api/reports/metrics?from=${fromDate}&to=${toDate}`);
            if (!response.ok) throw new Error('Failed to fetch metrics');
            
            const metrics = await response.json();
            this.updateMetricsDisplay(metrics);
        } catch (error) {
            console.error('Error loading metrics:', error);
            // Set default values
            this.updateMetricsDisplay({
                totalLoansAmount: 0,
                totalCustomers: 0,
                averageInterest: 0,
                monthlyGrowth: 0
            });
        }
    }

    updateMetricsDisplay(metrics) {
        document.getElementById('totalLoansAmount').textContent = `₹${this.formatNumber(metrics.totalLoansAmount || 0)}`;
        document.getElementById('totalCustomers').textContent = metrics.totalCustomers || 0;
        document.getElementById('averageInterest').textContent = `${(metrics.averageInterest || 0).toFixed(1)}%`;
        document.getElementById('monthlyGrowth').textContent = `${(metrics.monthlyGrowth || 0).toFixed(1)}%`;

        // Update change indicators
        document.getElementById('loansChange').textContent = `+${(metrics.loansGrowth || 0).toFixed(1)}%`;
        document.getElementById('customersChange').textContent = `+${(metrics.customersGrowth || 0).toFixed(1)}%`;
        document.getElementById('interestChange').textContent = `${(metrics.interestChange || 0).toFixed(1)}%`;
        document.getElementById('growthChange').textContent = `+${(metrics.growthChange || 0).toFixed(1)}%`;
    }

    async loadChartData() {
        try {
            const fromDate = document.getElementById('fromDate').value;
            const toDate = document.getElementById('toDate').value;
            
            const response = await fetch(`/api/reports/charts?from=${fromDate}&to=${toDate}`);
            if (!response.ok) throw new Error('Failed to fetch chart data');
            
            const chartData = await response.json();
            this.initializeCharts(chartData);
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.initializeChartsWithSampleData();
        }
    }

    initializeCharts(data) {
        this.initializeLoanTrendChart(data.loanTrend || []);
        this.initializeLoanTypesChart(data.loanTypes || []);
        this.initializeFinancialOverviewChart(data.financialOverview || []);
    }

    initializeChartsWithSampleData() {
        // Sample data for demonstration
        const sampleLoanTrend = [
            { date: '2024-01', amount: 150000 },
            { date: '2024-02', amount: 180000 },
            { date: '2024-03', amount: 220000 },
            { date: '2024-04', amount: 190000 },
            { date: '2024-05', amount: 250000 },
            { date: '2024-06', amount: 280000 }
        ];

        const sampleLoanTypes = [
            { type: 'Gold Loan', count: 45, amount: 2250000 },
            { type: 'Personal Loan', count: 20, amount: 1000000 },
            { type: 'Business Loan', count: 15, amount: 750000 },
            { type: 'Vehicle Loan', count: 10, amount: 500000 }
        ];

        this.initializeLoanTrendChart(sampleLoanTrend);
        this.initializeLoanTypesChart(sampleLoanTypes);
        this.initializeFinancialOverviewChart([]);
    }

    initializeLoanTrendChart(data) {
        const ctx = document.getElementById('loanTrendChart').getContext('2d');
        
        if (this.charts.loanTrend) {
            this.charts.loanTrend.destroy();
        }

        this.charts.loanTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date),
                datasets: [{
                    label: 'Loan Amount (₹)',
                    data: data.map(item => item.amount),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + (value / 1000) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    initializeLoanTypesChart(data) {
        const ctx = document.getElementById('loanTypesChart').getContext('2d');
        
        if (this.charts.loanTypes) {
            this.charts.loanTypes.destroy();
        }

        this.charts.loanTypes = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.type),
                datasets: [{
                    data: data.map(item => item.count),
                    backgroundColor: [
                        '#6366f1',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6'
                    ],
                    borderWidth: 0
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
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    initializeFinancialOverviewChart(data) {
        const ctx = document.getElementById('financialOverviewChart').getContext('2d');
        
        if (this.charts.financialOverview) {
            this.charts.financialOverview.destroy();
        }

        // Sample data if no data provided
        const chartData = data.length > 0 ? data : [
            { month: 'Jan', disbursed: 500000, collected: 450000, outstanding: 50000 },
            { month: 'Feb', disbursed: 600000, collected: 550000, outstanding: 100000 },
            { month: 'Mar', disbursed: 750000, collected: 650000, outstanding: 200000 },
            { month: 'Apr', disbursed: 650000, collected: 600000, outstanding: 250000 },
            { month: 'May', disbursed: 800000, collected: 720000, outstanding: 330000 },
            { month: 'Jun', disbursed: 900000, collected: 800000, outstanding: 430000 }
        ];

        this.charts.financialOverview = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.map(item => item.month),
                datasets: [
                    {
                        label: 'Disbursed',
                        data: chartData.map(item => item.disbursed),
                        backgroundColor: '#6366f1',
                        borderRadius: 4
                    },
                    {
                        label: 'Collected',
                        data: chartData.map(item => item.collected),
                        backgroundColor: '#10b981',
                        borderRadius: 4
                    },
                    {
                        label: 'Outstanding',
                        data: chartData.map(item => item.outstanding),
                        backgroundColor: '#f59e0b',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + (value / 1000) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    async loadReportTables() {
        try {
            await Promise.all([
                this.loadLoanSummaryTable(),
                this.loadCustomerAnalysisTable(),
                this.loadPerformanceMetrics()
            ]);
        } catch (error) {
            console.error('Error loading report tables:', error);
        }
    }

    async loadLoanSummaryTable() {
        try {
            const response = await fetch('/api/reports/loans-summary');
            if (!response.ok) throw new Error('Failed to fetch loan summary');
            
            const loans = await response.json();
            this.populateLoanSummaryTable(loans);
        } catch (error) {
            console.error('Error loading loan summary:', error);
            this.populateLoanSummaryTable([]);
        }
    }

    populateLoanSummaryTable(loans) {
        const tbody = document.getElementById('loanSummaryTable');
        
        if (loans.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-info-circle"></i> No loan data available for the selected period
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = loans.map(loan => `
            <tr>
                <td><strong>${loan.loan_number}</strong></td>
                <td>
                    <div class="customer-info">
                        <strong>${loan.customer_name}</strong>
                        <small class="text-muted d-block">${loan.customer_mobile}</small>
                    </div>
                </td>
                <td><strong>₹${this.formatNumber(loan.principal_amount)}</strong></td>
                <td>${loan.interest_rate}%</td>
                <td>${loan.tenure_months} months</td>
                <td>${new Date(loan.disbursed_date).toLocaleDateString('en-IN')}</td>
                <td>
                    <span class="badge bg-${this.getLoanStatusColor(loan.status)}">${loan.status || 'Active'}</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewLoanDetails('${loan.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadCustomerAnalysisTable() {
        try {
            const response = await fetch('/api/reports/customer-analysis');
            if (!response.ok) throw new Error('Failed to fetch customer analysis');
            
            const customers = await response.json();
            this.populateCustomerAnalysisTable(customers.customers || []);
            this.updateCustomerStats(customers.stats || {});
        } catch (error) {
            console.error('Error loading customer analysis:', error);
            this.populateCustomerAnalysisTable([]);
            this.updateCustomerStats({});
        }
    }

    populateCustomerAnalysisTable(customers) {
        const tbody = document.getElementById('customerAnalysisTable');
        
        if (customers.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <i class="fas fa-info-circle"></i> No customer data available
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = customers.map(customer => `
            <tr>
                <td>
                    <strong>${customer.name}</strong>
                    <small class="text-muted d-block">${customer.mobile}</small>
                </td>
                <td><span class="badge bg-primary">${customer.total_loans}</span></td>
                <td><strong>₹${this.formatNumber(customer.total_amount)}</strong></td>
                <td>${customer.last_loan_date ? new Date(customer.last_loan_date).toLocaleDateString('en-IN') : 'N/A'}</td>
                <td>
                    <div class="credit-score">
                        <span class="score-value">${customer.credit_score || 'N/A'}</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${(customer.credit_score || 0) / 10}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${this.getCustomerStatusColor(customer.status)}">${customer.status || 'Active'}</span>
                </td>
            </tr>
        `).join('');
    }

    updateCustomerStats(stats) {
        document.getElementById('newCustomersCount').textContent = stats.newCustomers || 0;
        document.getElementById('activeCustomersCount').textContent = stats.activeCustomers || 0;
        document.getElementById('averageLoanSize').textContent = `₹${this.formatNumber(stats.averageLoanSize || 0)}`;
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch('/api/reports/performance-metrics');
            if (!response.ok) throw new Error('Failed to fetch performance metrics');
            
            const metrics = await response.json();
            this.updatePerformanceDisplay(metrics);
        } catch (error) {
            console.error('Error loading performance metrics:', error);
            this.updatePerformanceDisplay({});
        }
    }

    updatePerformanceDisplay(metrics) {
        const approvalRate = metrics.approvalRate || 85;
        const processingTime = metrics.processingTime || 3;
        const satisfaction = metrics.satisfaction || 92;
        const defaultRate = metrics.defaultRate || 2.5;

        document.getElementById('approvalRate').textContent = `${approvalRate}%`;
        document.getElementById('processingTime').textContent = `${processingTime} days`;
        document.getElementById('satisfaction').textContent = `${satisfaction}%`;
        document.getElementById('defaultRate').textContent = `${defaultRate}%`;

        // Update progress bars
        document.getElementById('approvalRateBar').style.width = `${approvalRate}%`;
        document.getElementById('processingTimeBar').style.width = `${(10 - processingTime) * 10}%`;
        document.getElementById('satisfactionBar').style.width = `${satisfaction}%`;
        document.getElementById('defaultRateBar').style.width = `${Math.min(defaultRate * 10, 100)}%`;

        // Update financial overview stats
        document.getElementById('totalPortfolio').textContent = `₹${this.formatNumber(metrics.totalPortfolio || 0)}`;
        document.getElementById('totalInterest').textContent = `₹${this.formatNumber(metrics.totalInterest || 0)}`;
        document.getElementById('outstandingAmount').textContent = `₹${this.formatNumber(metrics.outstandingAmount || 0)}`;
        document.getElementById('collectionRate').textContent = `${(metrics.collectionRate || 0).toFixed(1)}%`;
    }

    getLoanStatusColor(status) {
        switch (status?.toLowerCase()) {
            case 'active': return 'success';
            case 'completed': return 'primary';
            case 'overdue': return 'warning';
            case 'defaulted': return 'danger';
            default: return 'secondary';
        }
    }

    getCustomerStatusColor(status) {
        switch (status?.toLowerCase()) {
            case 'active': return 'success';
            case 'inactive': return 'secondary';
            case 'blacklisted': return 'danger';
            default: return 'primary';
        }
    }

    formatNumber(num) {
        if (num >= 10000000) {
            return (num / 10000000).toFixed(1) + 'Cr';
        } else if (num >= 100000) {
            return (num / 100000).toFixed(1) + 'L';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString('en-IN');
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        // You can implement a toast notification or alert here
        console.error(message);
    }

    filterReportsByType(type) {
        // Implement filtering logic based on report type
        console.log('Filtering by type:', type);
    }
}

// Global functions for button actions
function generateReports() {
    if (window.reportsManager) {
        window.reportsManager.loadInitialData();
    }
}

function exportReports() {
    // Implement Excel export functionality
    alert('Excel export functionality will be implemented');
}

function printReports() {
    window.print();
}

function changeChartPeriod(period) {
    // Update chart based on period
    console.log('Changing chart period to:', period);
}

function viewLoanDetails(loanId) {
    // Navigate to loan details page
    window.location.href = `/loans/${loanId}`;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.reportsManager = new ReportsManager();
});
