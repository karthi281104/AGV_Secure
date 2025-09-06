/**
 * Payments Management JavaScript
 */

class PaymentsManager {
    constructor() {
        this.currentPage = 1;
        this.perPage = 12;
        this.searchQuery = '';
        this.methodFilter = '';
        this.dateFilter = '';
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPayments();
        this.loadStats();
        this.setDefaultDate();
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchQuery = e.target.value;
                    this.currentPage = 1;
                    this.loadPayments();
                }, 500);
            });
        }

        // Filter functionality
        const methodFilter = document.getElementById('methodFilter');
        if (methodFilter) {
            methodFilter.addEventListener('change', (e) => {
                this.methodFilter = e.target.value;
                this.currentPage = 1;
                this.loadPayments();
            });
        }

        const dateFilter = document.getElementById('dateFilter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.dateFilter = e.target.value;
                this.currentPage = 1;
                this.loadPayments();
            });
        }

        // Clear filters
        const clearFilters = document.getElementById('clearFilters');
        if (clearFilters) {
            clearFilters.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // New payment button
        const newPaymentBtn = document.getElementById('newPaymentBtn');
        if (newPaymentBtn) {
            newPaymentBtn.addEventListener('click', () => {
                window.location.href = '/payments/new';
            });
        }

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.getElementById('sidebar').classList.toggle('collapsed');
            });
        }
    }

    setDefaultDate() {
        const dateFilter = document.getElementById('dateFilter');
        if (dateFilter) {
            const today = new Date();
            dateFilter.value = today.toISOString().split('T')[0];
        }
    }

    clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('methodFilter').value = '';
        document.getElementById('dateFilter').value = '';
        
        this.searchQuery = '';
        this.methodFilter = '';
        this.dateFilter = '';
        this.currentPage = 1;
        
        this.loadPayments();
    }

    async loadPayments() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading(true);

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage
            });

            if (this.searchQuery && this.searchQuery.length >= 3) {
                params.append('q', this.searchQuery);
            }

            if (this.methodFilter) {
                params.append('method', this.methodFilter);
            }

            if (this.dateFilter) {
                params.append('date', this.dateFilter);
            }

            const response = await fetch(`/api/payments?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.renderPayments(data.payments);
                this.renderPagination(data.pagination);
            } else {
                this.showError(data.error || 'Error loading payments');
            }
        } catch (error) {
            console.error('Error loading payments:', error);
            this.showError('Network error loading payments');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    async loadStats() {
        try {
            // For now, we'll calculate stats from the current payments
            // In a real application, you'd have dedicated API endpoints for stats
            const response = await fetch('/api/payments?per_page=1000');
            const data = await response.json();

            if (response.ok) {
                const payments = data.payments;
                const today = new Date().toDateString();
                const thisMonth = new Date().getMonth();
                const thisYear = new Date().getFullYear();

                const stats = {
                    total: payments.length,
                    totalAmount: payments.reduce((sum, p) => sum + p.amount, 0),
                    todayCount: payments.filter(p => 
                        new Date(p.payment_date).toDateString() === today
                    ).length,
                    thisMonthAmount: payments.filter(p => {
                        const date = new Date(p.payment_date);
                        return date.getMonth() === thisMonth && date.getFullYear() === thisYear;
                    }).reduce((sum, p) => sum + p.amount, 0)
                };

                this.renderStats(stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderStats(stats) {
        document.getElementById('totalPayments').textContent = stats.total;
        document.getElementById('totalAmount').textContent = `₹${stats.totalAmount.toLocaleString()}`;
        document.getElementById('todayPayments').textContent = stats.todayCount;
        document.getElementById('thisMonthAmount').textContent = `₹${stats.thisMonthAmount.toLocaleString()}`;
    }

    renderPayments(payments) {
        const container = document.getElementById('paymentsContainer');
        const emptyState = document.getElementById('emptyState');

        if (payments.length === 0) {
            container.innerHTML = '';
            emptyState.classList.remove('d-none');
            return;
        }

        emptyState.classList.add('d-none');
        
        container.innerHTML = payments.map(payment => this.createPaymentCard(payment)).join('');

        // Bind events for payment cards
        this.bindPaymentCardEvents();
    }

    createPaymentCard(payment) {
        const paymentDate = new Date(payment.payment_date).toLocaleDateString();
        const methodClass = `method-${payment.payment_method.replace('_', '')}`;
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="payment-card" data-payment-id="${payment.id}">
                    <div class="d-flex align-items-start">
                        <div class="payment-info">
                            <div class="payment-number">${payment.payment_number}</div>
                            <div class="payment-amount">₹${payment.amount.toLocaleString()}</div>
                            <div class="payment-detail">
                                <i class="fas fa-user"></i>
                                ${payment.loan.customer_name}
                            </div>
                            <div class="payment-detail">
                                <i class="fas fa-phone"></i>
                                ${payment.loan.customer_mobile}
                            </div>
                            <div class="payment-detail">
                                <i class="fas fa-calendar"></i>
                                ${paymentDate}
                            </div>
                            <div class="payment-detail">
                                <span class="payment-method ${methodClass}">
                                    ${this.formatPaymentMethod(payment.payment_method)}
                                </span>
                            </div>
                        </div>
                        <div class="payment-actions">
                            <button class="btn-action btn-view" onclick="paymentsManager.viewPayment('${payment.id}')"
                                    title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-action btn-receipt" onclick="paymentsManager.printReceipt('${payment.id}')"
                                    title="Print Receipt">
                                <i class="fas fa-print"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatPaymentMethod(method) {
        const methods = {
            'cash': 'Cash',
            'bank_transfer': 'Bank Transfer',
            'cheque': 'Cheque',
            'online': 'Online'
        };
        return methods[method] || method;
    }

    bindPaymentCardEvents() {
        // Events are bound inline in the HTML for simplicity
    }

    async viewPayment(paymentId) {
        try {
            const response = await fetch(`/api/payments/${paymentId}`);
            const payment = await response.json();

            if (response.ok) {
                this.showPaymentDetails(payment);
            } else {
                this.showError(payment.error || 'Error loading payment details');
            }
        } catch (error) {
            console.error('Error loading payment details:', error);
            this.showError('Network error loading payment details');
        }
    }

    showPaymentDetails(payment) {
        const modal = new bootstrap.Modal(document.getElementById('paymentDetailsModal'));
        const body = document.getElementById('paymentDetailsBody');
        
        const paymentDate = new Date(payment.payment_date).toLocaleDateString();
        const createdDate = new Date(payment.created_at).toLocaleDateString();

        body.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Payment Information</h6>
                    <table class="table table-borderless">
                        <tr>
                            <td><strong>Payment Number:</strong></td>
                            <td>${payment.payment_number}</td>
                        </tr>
                        <tr>
                            <td><strong>Amount:</strong></td>
                            <td>₹${payment.amount.toLocaleString()}</td>
                        </tr>
                        <tr>
                            <td><strong>Payment Date:</strong></td>
                            <td>${paymentDate}</td>
                        </tr>
                        <tr>
                            <td><strong>Payment Method:</strong></td>
                            <td>${this.formatPaymentMethod(payment.payment_method)}</td>
                        </tr>
                        ${payment.transaction_id ? `
                        <tr>
                            <td><strong>Transaction ID:</strong></td>
                            <td>${payment.transaction_id}</td>
                        </tr>` : ''}
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Loan Information</h6>
                    <table class="table table-borderless">
                        <tr>
                            <td><strong>Loan Number:</strong></td>
                            <td>${payment.loan.loan_number}</td>
                        </tr>
                        <tr>
                            <td><strong>Customer:</strong></td>
                            <td>${payment.loan.customer_name}</td>
                        </tr>
                        <tr>
                            <td><strong>Mobile:</strong></td>
                            <td>${payment.loan.customer_mobile}</td>
                        </tr>
                        <tr>
                            <td><strong>Principal Amount:</strong></td>
                            <td>₹${payment.loan.principal_amount.toLocaleString()}</td>
                        </tr>
                    </table>
                </div>
            </div>
            ${payment.notes ? `
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Notes</h6>
                    <p class="border p-3 rounded bg-light">${payment.notes}</p>
                </div>
            </div>` : ''}
            <div class="row mt-3">
                <div class="col-12">
                    <small class="text-muted">Recorded on: ${createdDate}</small>
                </div>
            </div>
        `;

        modal.show();
    }

    printReceipt(paymentId) {
        // Implementation for printing receipt
        this.viewPayment(paymentId).then(() => {
            // After modal is shown, trigger print
            setTimeout(() => {
                window.print();
            }, 500);
        });
    }

    renderPagination(pagination) {
        const container = document.getElementById('pagination');
        
        if (pagination.pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '';
        
        // Previous button
        if (pagination.has_prev) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="paymentsManager.goToPage(${pagination.page - 1})">
                        Previous
                    </a>
                </li>
            `;
        }

        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === pagination.page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="paymentsManager.goToPage(${i})">${i}</a>
                </li>
            `;
        }

        // Next button
        if (pagination.has_next) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="paymentsManager.goToPage(${pagination.page + 1})">
                        Next
                    </a>
                </li>
            `;
        }

        container.innerHTML = html;
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadPayments();
    }

    showLoading(show) {
        const loadingState = document.getElementById('loadingState');
        if (loadingState) {
            loadingState.classList.toggle('d-none', !show);
        }
    }

    showError(message) {
        // Simple error display - you can enhance this
        console.error(message);
        alert(message);
    }
}

// Initialize payments manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.paymentsManager = new PaymentsManager();
});
