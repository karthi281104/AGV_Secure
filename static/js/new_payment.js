/**
 * New Payment Form JavaScript
 */

class NewPaymentForm {
    constructor() {
        this.selectedLoan = null;
        this.selectedMethod = null;
        this.isSubmitting = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setDefaultDate();
    }

    bindEvents() {
        // Loan search
        const loanSearch = document.getElementById('loanSearch');
        if (loanSearch) {
            let searchTimeout;
            loanSearch.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchLoans(e.target.value);
                }, 500);
            });
        }

        // Payment method selection
        document.querySelectorAll('.method-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectPaymentMethod(card);
            });
        });

        // Form submission
        const form = document.getElementById('paymentForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitPayment();
            });
        }

        // Amount input validation
        const amountInput = document.getElementById('paymentAmount');
        if (amountInput) {
            amountInput.addEventListener('input', () => {
                this.validateForm();
            });
        }

        // Date input validation
        const dateInput = document.getElementById('paymentDate');
        if (dateInput) {
            dateInput.addEventListener('change', () => {
                this.validateForm();
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
        const dateInput = document.getElementById('paymentDate');
        if (dateInput) {
            const today = new Date();
            dateInput.value = today.toISOString().split('T')[0];
        }
    }

    async searchLoans(query) {
        const resultsContainer = document.getElementById('loanResults');
        
        if (!query || query.length < 3) {
            resultsContainer.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/loans/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                this.renderLoanResults(data.loans);
            } else {
                resultsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        Error searching loans: ${data.error}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error searching loans:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Network error while searching loans
                </div>
            `;
        }
    }

    renderLoanResults(loans) {
        const container = document.getElementById('loanResults');
        
        if (loans.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    No loans found matching your search criteria.
                </div>
            `;
            return;
        }

        container.innerHTML = loans.map(loan => `
            <div class="loan-card" onclick="newPaymentForm.selectLoan('${loan.id}', '${loan.loan_number}', '${loan.customer_name}', '${loan.customer_mobile}', ${loan.principal_amount})">
                <div class="loan-info">
                    <h6>${loan.loan_number}</h6>
                    <div class="loan-details">
                        <div><i class="fas fa-user"></i> ${loan.customer_name}</div>
                        <div><i class="fas fa-phone"></i> ${loan.customer_mobile}</div>
                        <div><i class="fas fa-money-bill"></i> Principal: ₹${loan.principal_amount.toLocaleString()}</div>
                        <div><i class="fas fa-info-circle"></i> Status: ${loan.status}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    selectLoan(id, loanNumber, customerName, customerMobile, principalAmount) {
        this.selectedLoan = {
            id: id,
            loan_number: loanNumber,
            customer_name: customerName,
            customer_mobile: customerMobile,
            principal_amount: principalAmount
        };

        // Update UI
        document.getElementById('selectedLoanDetails').innerHTML = `
            ${loanNumber} - ${customerName} (${customerMobile}) - Principal: ₹${principalAmount.toLocaleString()}
        `;
        document.getElementById('selectedLoanInfo').classList.remove('d-none');
        
        // Clear search
        document.getElementById('loanSearch').value = '';
        document.getElementById('loanResults').innerHTML = '';

        // Remove selected class from all cards and add to current
        document.querySelectorAll('.loan-card').forEach(card => {
            card.classList.remove('selected');
        });

        this.validateForm();
    }

    selectPaymentMethod(card) {
        // Remove selected class from all method cards
        document.querySelectorAll('.method-card').forEach(c => {
            c.classList.remove('selected');
        });

        // Add selected class to clicked card
        card.classList.add('selected');
        
        this.selectedMethod = card.dataset.method;
        
        // Show/hide transaction ID field based on method
        const transactionField = document.getElementById('transactionId').parentElement;
        if (this.selectedMethod === 'cash') {
            transactionField.style.display = 'none';
        } else {
            transactionField.style.display = 'block';
        }

        this.validateForm();
    }

    validateForm() {
        const submitBtn = document.getElementById('submitPayment');
        const amount = document.getElementById('paymentAmount').value;
        const date = document.getElementById('paymentDate').value;
        
        const isValid = this.selectedLoan && 
                       this.selectedMethod && 
                       amount && parseFloat(amount) > 0 && 
                       date;
        
        submitBtn.disabled = !isValid;
    }

    async submitPayment() {
        if (this.isSubmitting) return;

        this.isSubmitting = true;
        const submitBtn = document.getElementById('submitPayment');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Recording Payment...';
        submitBtn.disabled = true;

        try {
            const formData = {
                loan_id: this.selectedLoan.id,
                amount: parseFloat(document.getElementById('paymentAmount').value),
                payment_date: document.getElementById('paymentDate').value + 'T00:00:00Z',
                payment_method: this.selectedMethod,
                transaction_id: document.getElementById('transactionId').value || null,
                notes: document.getElementById('paymentNotes').value || null
            };

            const response = await fetch('/api/payments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess(result);
            } else {
                this.showError(result.error || 'Error recording payment');
            }
        } catch (error) {
            console.error('Error submitting payment:', error);
            this.showError('Network error while recording payment');
        } finally {
            this.isSubmitting = false;
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    showSuccess(result) {
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        const messageContainer = document.getElementById('successMessage');
        
        messageContainer.innerHTML = `
            <div class="mb-3">
                <i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>
            </div>
            <h5>Payment Recorded Successfully!</h5>
            <p class="mb-2"><strong>Payment Number:</strong> ${result.payment.payment_number}</p>
            <p class="mb-2"><strong>Amount:</strong> ₹${result.payment.amount.toLocaleString()}</p>
            <p class="mb-2"><strong>Customer:</strong> ${this.selectedLoan.customer_name}</p>
            <p class="text-muted">The payment has been recorded and saved to the system.</p>
        `;
        
        modal.show();
    }

    showError(message) {
        alert(`Error: ${message}`);
    }

    resetForm() {
        // Reset all form fields
        document.getElementById('paymentForm').reset();
        
        // Reset selections
        this.selectedLoan = null;
        this.selectedMethod = null;
        
        // Reset UI
        document.getElementById('selectedLoanInfo').classList.add('d-none');
        document.querySelectorAll('.method-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelectorAll('.loan-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset date to today
        this.setDefaultDate();
        
        // Validate form
        this.validateForm();
    }
}

// Initialize new payment form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.newPaymentForm = new NewPaymentForm();
});
