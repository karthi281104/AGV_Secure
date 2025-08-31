/**
 * Customer Selection Modal and New Loan Form Management
 */

class CustomerSelectionModal {
    constructor() {
        this.currentPage = 1;
        this.perPage = 12;
        this.searchQuery = '';
        this.selectedCustomer = null;
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        // Create modal HTML
        const modalHTML = `
        <div class="modal fade" id="customerSelectionModal" tabindex="-1" aria-labelledby="customerSelectionModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="customerSelectionModalLabel">
                            <i class="fas fa-users me-2"></i>Select Customer for New Loan
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Search Bar -->
                        <div class="row mb-4">
                            <div class="col-md-8">
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-search"></i></span>
                                    <input type="text" class="form-control" id="customerModalSearch" 
                                           placeholder="Search by name, mobile, father's name, or Aadhar...">
                                    <button class="btn btn-outline-secondary" type="button" id="clearSearch">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                                <small class="text-muted">Type at least 3 characters to search</small>
                            </div>
                            <div class="col-md-4 text-end">
                                <button class="btn btn-success" onclick="window.location.href='/customers/add'">
                                    <i class="fas fa-plus me-1"></i>Add New Customer
                                </button>
                            </div>
                        </div>

                        <!-- Loading State -->
                        <div id="modalLoading" class="text-center py-5 d-none">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-3">Loading customers...</p>
                        </div>

                        <!-- Customer Grid -->
                        <div id="customersGrid" class="row">
                            <!-- Customer cards will be populated here -->
                        </div>

                        <!-- No Results -->
                        <div id="noCustomers" class="text-center py-5 d-none">
                            <i class="fas fa-users-slash fa-3x text-muted mb-3"></i>
                            <h5>No customers found</h5>
                            <p class="text-muted">Try adjusting your search criteria or add a new customer.</p>
                        </div>

                        <!-- Pagination -->
                        <div id="modalPagination" class="d-flex justify-content-center mt-4">
                            <!-- Pagination will be populated here -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="proceedWithCustomer" disabled>
                            <i class="fas fa-arrow-right me-1"></i>Proceed with Selected Customer
                        </button>
                    </div>
                </div>
            </div>
        </div>`;

        // Append modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Initialize Bootstrap modal
        if (typeof bootstrap !== 'undefined') {
            this.modal = new bootstrap.Modal(document.getElementById('customerSelectionModal'));
            
            // Add additional cleanup for Bootstrap modal
            this.modalElement = document.getElementById('customerSelectionModal');
            
            // Debug logging
            console.log('CustomerSelectionModal: Bootstrap modal initialized');
        } else {
            // Fallback for when Bootstrap is not available
            const modalElement = document.getElementById('customerSelectionModal');
            this.modalElement = modalElement;
            
            this.modal = {
                show: () => {
                    console.log('CustomerSelectionModal: Showing modal (fallback)');
                    modalElement.style.display = 'block';
                    modalElement.classList.add('show');
                    document.body.classList.add('modal-open');
                    
                    // Create backdrop if it doesn't exist
                    if (!document.querySelector('.modal-backdrop')) {
                        const backdrop = document.createElement('div');
                        backdrop.className = 'modal-backdrop fade show';
                        backdrop.setAttribute('data-modal-backdrop', 'customerSelectionModal');
                        document.body.appendChild(backdrop);
                    }
                },
                hide: () => {
                    console.log('CustomerSelectionModal: Hiding modal (fallback)');
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    
                    // Remove backdrop
                    this.removeBackdrop();
                }
            };
        }
    }

    bindEvents() {
        const searchInput = document.getElementById('customerModalSearch');
        const clearButton = document.getElementById('clearSearch');
        const proceedButton = document.getElementById('proceedWithCustomer');

        // Search functionality with debouncing
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            searchTimeout = setTimeout(() => {
                this.searchQuery = query;
                this.currentPage = 1;
                this.loadCustomers();
            }, 300);
        });

        // Clear search
        clearButton.addEventListener('click', () => {
            searchInput.value = '';
            this.searchQuery = '';
            this.currentPage = 1;
            this.loadCustomers();
        });

        // Proceed with selected customer
        proceedButton.addEventListener('click', () => {
            if (this.selectedCustomer) {
                this.proceedToLoanForm();
            }
        });

        // Handle modal events
        document.getElementById('customerSelectionModal').addEventListener('shown.bs.modal', () => {
            console.log('CustomerSelectionModal: Modal shown event');
            this.loadCustomers();
            searchInput.focus();
        });

        document.getElementById('customerSelectionModal').addEventListener('hidden.bs.modal', () => {
            console.log('CustomerSelectionModal: Modal hidden event');
            this.resetModal();
            this.cleanupModal();
        });

        // Handle fallback modal events for non-Bootstrap environments
        if (typeof bootstrap === 'undefined') {
            // Add click listener to backdrop for closing modal
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-backdrop') && 
                    e.target.getAttribute('data-modal-backdrop') === 'customerSelectionModal') {
                    console.log('CustomerSelectionModal: Backdrop clicked, closing modal');
                    this.modal.hide();
                }
            });
        }
    }

    async loadCustomers() {
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

            const response = await fetch(`/test-api/customers?${params}`);
            const data = await response.json();

            if (response.ok) {
                this.renderCustomers(data.customers);
                this.renderPagination(data.pagination);
            } else {
                this.showError(data.error || 'Error loading customers');
            }
        } catch (error) {
            console.error('Error loading customers:', error);
            this.showError('Network error loading customers');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    renderCustomers(customers) {
        const grid = document.getElementById('customersGrid');
        const noCustomers = document.getElementById('noCustomers');

        if (customers.length === 0) {
            grid.innerHTML = '';
            noCustomers.classList.remove('d-none');
            return;
        }

        noCustomers.classList.add('d-none');
        
        grid.innerHTML = customers.map(customer => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="customer-card" data-customer-id="${customer.id}">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0 text-truncate">${this.escapeHtml(customer.name)}</h6>
                                <div class="form-check">
                                    <input class="form-check-input customer-radio" type="radio" 
                                           name="selectedCustomer" value="${customer.id}">
                                </div>
                            </div>
                            <div class="customer-details">
                                <p class="mb-1 small">
                                    <i class="fas fa-user text-muted me-1"></i>
                                    <span class="text-muted">Father:</span> ${this.escapeHtml(customer.father_name)}
                                </p>
                                <p class="mb-1 small">
                                    <i class="fas fa-phone text-muted me-1"></i>
                                    ${this.escapeHtml(customer.mobile)}
                                </p>
                                <p class="mb-1 small">
                                    <i class="fas fa-id-card text-muted me-1"></i>
                                    <span class="text-muted">Aadhar:</span> ${this.escapeHtml(customer.aadhar_number)}
                                </p>
                                <p class="mb-0 small text-muted">
                                    <i class="fas fa-map-marker-alt me-1"></i>
                                    ${this.escapeHtml(customer.address).substring(0, 50)}${customer.address.length > 50 ? '...' : ''}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // Bind click events for customer cards
        this.bindCustomerCardEvents();
    }

    bindCustomerCardEvents() {
        const customerCards = document.querySelectorAll('.customer-card');
        const proceedButton = document.getElementById('proceedWithCustomer');

        customerCards.forEach(card => {
            const radio = card.querySelector('.customer-radio');
            
            // Click on card selects the customer
            card.addEventListener('click', (e) => {
                if (e.target !== radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change'));
                }
            });

            // Handle radio button changes
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    // Remove previous selection styling
                    document.querySelectorAll('.customer-card .card').forEach(c => {
                        c.classList.remove('border-primary', 'bg-light');
                    });

                    // Add selection styling
                    card.querySelector('.card').classList.add('border-primary', 'bg-light');

                    // Store selected customer
                    this.selectedCustomer = {
                        id: radio.value,
                        ...this.getCustomerDataFromCard(card)
                    };

                    // Enable proceed button
                    proceedButton.disabled = false;
                }
            });
        });
    }

    getCustomerDataFromCard(card) {
        const title = card.querySelector('.card-title').textContent;
        const details = card.querySelectorAll('.customer-details p');
        
        return {
            name: title,
            father_name: details[0]?.textContent.split('Father: ')[1] || '',
            mobile: details[1]?.textContent.trim() || '',
            aadhar_number: details[2]?.textContent.split('Aadhar: ')[1] || '',
            address: details[3]?.textContent.trim().replace('🗺️ ', '') || ''
        };
    }

    renderPagination(pagination) {
        const container = document.getElementById('modalPagination');
        
        if (pagination.pages <= 1) {
            container.innerHTML = '';
            return;
        }

        const nav = document.createElement('nav');
        nav.innerHTML = `
            <ul class="pagination pagination-sm">
                <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${pagination.page - 1}">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
                ${this.generatePageNumbers(pagination)}
                <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${pagination.page + 1}">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
            </ul>
        `;

        container.innerHTML = nav.outerHTML;

        // Bind pagination events
        container.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.closest('[data-page]')?.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadCustomers();
                }
            });
        });
    }

    generatePageNumbers(pagination) {
        const current = pagination.page;
        const total = pagination.pages;
        const pages = [];

        // Always show first page
        if (current > 3) {
            pages.push(`<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`);
            if (current > 4) {
                pages.push(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
            }
        }

        // Show pages around current
        const start = Math.max(1, current - 2);
        const end = Math.min(total, current + 2);

        for (let i = start; i <= end; i++) {
            const isActive = i === current;
            pages.push(`
                <li class="page-item ${isActive ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
        }

        // Always show last page
        if (current < total - 2) {
            if (current < total - 3) {
                pages.push(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
            }
            pages.push(`<li class="page-item"><a class="page-link" href="#" data-page="${total}">${total}</a></li>`);
        }

        return pages.join('');
    }

    showLoading(show) {
        const loading = document.getElementById('modalLoading');
        const grid = document.getElementById('customersGrid');
        const pagination = document.getElementById('modalPagination');

        if (show) {
            loading.classList.remove('d-none');
            grid.classList.add('d-none');
            pagination.classList.add('d-none');
        } else {
            loading.classList.add('d-none');
            grid.classList.remove('d-none');
            pagination.classList.remove('d-none');
        }
    }

    showError(message) {
        // You can implement a toast notification here
        console.error(message);
        alert(message); // Simple fallback
    }

    proceedToLoanForm() {
        if (!this.selectedCustomer) return;

        console.log('CustomerSelectionModal: Proceeding to loan form with customer:', this.selectedCustomer);

        // Store selected customer in sessionStorage
        sessionStorage.setItem('selectedCustomer', JSON.stringify(this.selectedCustomer));

        // Close modal and redirect to loan form
        this.modal.hide();
        
        // Ensure cleanup happens
        this.cleanupModal();
        
        // Small delay to ensure modal is hidden before navigation
        setTimeout(() => {
            window.location.href = '/loans/new';
        }, 300);
    }

    resetModal() {
        this.selectedCustomer = null;
        this.currentPage = 1;
        this.searchQuery = '';
        
        const searchInput = document.getElementById('customerModalSearch');
        const proceedButton = document.getElementById('proceedWithCustomer');
        const customersGrid = document.getElementById('customersGrid');
        const modalPagination = document.getElementById('modalPagination');
        
        if (searchInput) searchInput.value = '';
        if (proceedButton) proceedButton.disabled = true;
        if (customersGrid) customersGrid.innerHTML = '';
        if (modalPagination) modalPagination.innerHTML = '';
        
        console.log('CustomerSelectionModal: Modal reset completed');
    }

    // New method to handle backdrop cleanup
    removeBackdrop() {
        console.log('CustomerSelectionModal: Removing backdrop');
        const backdrops = document.querySelectorAll('.modal-backdrop[data-modal-backdrop="customerSelectionModal"]');
        backdrops.forEach(backdrop => {
            backdrop.remove();
        });
        
        // Also remove any orphaned Bootstrap backdrops
        const allBackdrops = document.querySelectorAll('.modal-backdrop');
        if (allBackdrops.length > 0 && !document.querySelector('.modal.show')) {
            console.log('CustomerSelectionModal: Removing orphaned backdrops');
            allBackdrops.forEach(backdrop => backdrop.remove());
        }
    }

    // New method to handle comprehensive modal cleanup
    cleanupModal() {
        console.log('CustomerSelectionModal: Performing comprehensive cleanup');
        
        // Remove any lingering backdrops
        this.removeBackdrop();
        
        // Ensure body classes are cleaned up
        document.body.classList.remove('modal-open');
        
        // Reset body overflow
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Force cleanup of any remaining modal-related styles
        setTimeout(() => {
            const remainingBackdrops = document.querySelectorAll('.modal-backdrop');
            if (remainingBackdrops.length > 0) {
                console.warn('CustomerSelectionModal: Found remaining backdrops after cleanup, removing...');
                remainingBackdrops.forEach(backdrop => backdrop.remove());
            }
        }, 100);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public method to show modal
    show() {
        console.log('CustomerSelectionModal: Showing modal');
        this.modal.show();
    }
}

// New Loan Form Management
class NewLoanForm {
    constructor() {
        this.selectedCustomer = null;
        this.init();
    }

    init() {
        // Check if we have a pre-selected customer
        const storedCustomer = sessionStorage.getItem('selectedCustomer');
        if (storedCustomer) {
            this.selectedCustomer = JSON.parse(storedCustomer);
            this.populateCustomerDetails();
            // Clear from sessionStorage
            sessionStorage.removeItem('selectedCustomer');
        }

        this.bindFormEvents();
    }

    populateCustomerDetails() {
        if (!this.selectedCustomer) return;

        // Hide customer search section and show selected customer
        const searchSection = document.querySelector('.form-section');
        const customerSearch = document.getElementById('customerSearch');
        const selectedCustomerDiv = document.getElementById('selectedCustomer');
        const customerSearchResults = document.getElementById('customerSearchResults');

        if (customerSearch) customerSearch.style.display = 'none';
        if (customerSearchResults) customerSearchResults.classList.add('d-none');

        if (selectedCustomerDiv) {
            selectedCustomerDiv.classList.remove('d-none');
            
            // Populate customer data
            document.getElementById('customerIdInput').value = this.selectedCustomer.id;
            document.getElementById('customerName').textContent = this.selectedCustomer.name;
            document.getElementById('fatherName').textContent = this.selectedCustomer.father_name;
            document.getElementById('customerMobile').textContent = this.selectedCustomer.mobile;
            document.getElementById('customerAddress').textContent = this.selectedCustomer.address;
            document.getElementById('customerId').textContent = this.selectedCustomer.id;
        }

        // Show loan details section
        const loanDetailsSection = document.getElementById('loanDetailsSection');
        if (loanDetailsSection) {
            loanDetailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    bindFormEvents() {
        // Change customer button
        const changeCustomerBtn = document.getElementById('changeCustomer');
        if (changeCustomerBtn) {
            changeCustomerBtn.addEventListener('click', () => {
                // Show customer search again
                const customerSearch = document.getElementById('customerSearch');
                const selectedCustomerDiv = document.getElementById('selectedCustomer');
                
                if (customerSearch) customerSearch.style.display = 'block';
                if (selectedCustomerDiv) selectedCustomerDiv.classList.add('d-none');
                
                this.selectedCustomer = null;
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('CustomerSelectionModal: DOM ready, initializing...');
    
    // Initialize customer selection modal
    window.customerModal = new CustomerSelectionModal();
    
    // Initialize new loan form if we're on the new loan page
    if (window.location.pathname === '/loans/new') {
        window.newLoanForm = new NewLoanForm();
    }
    
    // Global cleanup function for emergency modal cleanup
    window.emergencyModalCleanup = function() {
        console.log('Emergency modal cleanup triggered');
        
        // Remove all modal backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        
        // Reset body styles
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Hide all modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
            modal.classList.remove('show');
        });
        
        console.log('Emergency cleanup completed');
    };
    
    // Auto-cleanup on window unload
    window.addEventListener('beforeunload', () => {
        if (window.emergencyModalCleanup) {
            window.emergencyModalCleanup();
        }
    });
    
    // Periodic cleanup check (every 5 seconds)
    setInterval(() => {
        const hasOpenModal = document.querySelector('.modal.show');
        const hasBackdrop = document.querySelector('.modal-backdrop');
        const bodyHasModalOpen = document.body.classList.contains('modal-open');
        
        // If we have backdrop but no open modal, clean up
        if (hasBackdrop && !hasOpenModal) {
            console.warn('Found orphaned backdrop, cleaning up');
            window.emergencyModalCleanup();
        }
        
        // If body has modal-open but no modal is actually open, clean up
        if (bodyHasModalOpen && !hasOpenModal) {
            console.warn('Body has modal-open class but no modal is open, cleaning up');
            window.emergencyModalCleanup();
        }
    }, 5000);
});

// Function to open customer selection modal from dashboard
function openCustomerSelectionModal() {
    if (window.customerModal) {
        window.customerModal.show();
    }
}

// Export for use in other scripts
window.CustomerSelectionModal = CustomerSelectionModal;
window.NewLoanForm = NewLoanForm;
window.openCustomerSelectionModal = openCustomerSelectionModal;