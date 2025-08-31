// Settings Page JavaScript Functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeSettings();
    setupEventListeners();
    loadUserSettings();
});

// Initialize settings page functionality
function initializeSettings() {
    // Setup tab navigation
    setupTabNavigation();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup confirmation dialogs
    setupConfirmationDialogs();
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Profile picture upload
    const profilePictureUpload = document.getElementById('profilePictureUpload');
    if (profilePictureUpload) {
        profilePictureUpload.addEventListener('change', handleProfilePictureUpload);
    }
    
    // Form submissions
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileSubmit);
    }
    
    const preferencesForm = document.getElementById('preferencesForm');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', handlePreferencesSubmit);
    }
    
    // Password confirmation in change password modal
    const confirmPassword = document.getElementById('confirmPassword');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', validatePasswordMatch);
    }
    
    // System reset confirmation
    const resetConfirmation = document.getElementById('resetConfirmation');
    if (resetConfirmation) {
        resetConfirmation.addEventListener('input', validateResetConfirmation);
    }
    
    // Restore confirmation
    const restoreConfirm = document.getElementById('restoreConfirm');
    if (restoreConfirm) {
        restoreConfirm.addEventListener('change', validateRestoreConfirmation);
    }
}

// Setup tab navigation
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.settings-tabs .nav-link');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
        });
    });
}

// Setup form validations
function setupFormValidations() {
    // Password strength validation
    const newPassword = document.getElementById('newPassword');
    if (newPassword) {
        newPassword.addEventListener('input', validatePasswordStrength);
    }
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', validateEmail);
    });
    
    // Phone validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', formatPhoneNumber);
    });
}

// Setup confirmation dialogs
function setupConfirmationDialogs() {
    // Add confirmation for critical actions
    const criticalButtons = document.querySelectorAll('[data-confirm]');
    criticalButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// Handle profile picture upload
function handleProfilePictureUpload(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showAlert('Please select a valid image file.', 'danger');
            return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showAlert('Image size must be less than 5MB.', 'danger');
            return;
        }
        
        // Preview image
        const reader = new FileReader();
        reader.onload = function(e) {
            const profilePicture = document.getElementById('profilePicture');
            if (profilePicture) {
                profilePicture.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
        
        // Upload image (simulate)
        uploadProfilePicture(file);
    }
}

// Handle profile form submission
function handleProfileSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const profileData = Object.fromEntries(formData);
    
    // Validate required fields
    if (!profileData.firstName || !profileData.email) {
        showAlert('Please fill in all required fields.', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    showLoading(submitButton);
    
    // Simulate API call
    setTimeout(() => {
        hideLoading(submitButton);
        saveProfileData(profileData);
    }, 1500);
}

// Handle preferences form submission
function handlePreferencesSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const preferencesData = Object.fromEntries(formData);
    
    // Include radio button values
    const theme = document.querySelector('input[name="theme"]:checked')?.value;
    if (theme) {
        preferencesData.theme = theme;
    }
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    showLoading(submitButton);
    
    // Simulate API call
    setTimeout(() => {
        hideLoading(submitButton);
        savePreferencesData(preferencesData);
    }, 1500);
}

// Validate password strength
function validatePasswordStrength(event) {
    const password = event.target.value;
    const strengthIndicator = document.getElementById('passwordStrength');
    
    let strength = 0;
    let message = '';
    let className = '';
    
    // Check password criteria
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    switch (strength) {
        case 0:
        case 1:
            message = 'Very Weak';
            className = 'text-danger';
            break;
        case 2:
            message = 'Weak';
            className = 'text-warning';
            break;
        case 3:
            message = 'Fair';
            className = 'text-info';
            break;
        case 4:
            message = 'Good';
            className = 'text-success';
            break;
        case 5:
            message = 'Excellent';
            className = 'text-success fw-bold';
            break;
    }
    
    if (strengthIndicator) {
        strengthIndicator.textContent = password ? `Password Strength: ${message}` : '';
        strengthIndicator.className = className;
    }
}

// Validate password match
function validatePasswordMatch(event) {
    const confirmPassword = event.target.value;
    const newPassword = document.getElementById('newPassword').value;
    const matchIndicator = document.getElementById('passwordMatch');
    
    if (confirmPassword && newPassword) {
        const matches = confirmPassword === newPassword;
        if (matchIndicator) {
            matchIndicator.textContent = matches ? 'Passwords match' : 'Passwords do not match';
            matchIndicator.className = matches ? 'text-success' : 'text-danger';
        }
        
        // Enable/disable submit button
        const submitButton = document.querySelector('#changePasswordModal .btn-primary');
        if (submitButton) {
            submitButton.disabled = !matches;
        }
    }
}

// Validate email format
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        event.target.classList.add('is-invalid');
        showFieldError(event.target, 'Please enter a valid email address.');
    } else {
        event.target.classList.remove('is-invalid');
        hideFieldError(event.target);
    }
}

// Format phone number
function formatPhoneNumber(event) {
    let value = event.target.value.replace(/\D/g, '');
    
    // Format for Indian numbers (+91 XXXXX XXXXX)
    if (value.length <= 10) {
        if (value.length > 5) {
            value = value.replace(/(\d{5})(\d{1,5})/, '$1 $2');
        }
        event.target.value = value;
    }
}

// Validate reset confirmation
function validateResetConfirmation(event) {
    const value = event.target.value.toUpperCase();
    const submitButton = document.getElementById('confirmResetBtn');
    
    if (submitButton) {
        submitButton.disabled = value !== 'RESET';
    }
}

// Validate restore confirmation
function validateRestoreConfirmation(event) {
    const checked = event.target.checked;
    const submitButton = document.getElementById('confirmRestoreBtn');
    
    if (submitButton) {
        submitButton.disabled = !checked;
    }
}

// Upload profile picture
async function uploadProfilePicture(file) {
    try {
        // Simulate upload process
        showAlert('Uploading profile picture...', 'info');
        
        // In a real application, you would upload to your server
        // const formData = new FormData();
        // formData.append('profile_picture', file);
        // const response = await fetch('/api/upload-profile-picture', {
        //     method: 'POST',
        //     body: formData
        // });
        
        setTimeout(() => {
            showAlert('Profile picture updated successfully!', 'success');
        }, 2000);
        
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('Failed to upload profile picture. Please try again.', 'danger');
    }
}

// Save profile data
function saveProfileData(data) {
    try {
        // Store in localStorage (in real app, send to server)
        localStorage.setItem('userProfile', JSON.stringify(data));
        showAlert('Profile updated successfully!', 'success');
    } catch (error) {
        console.error('Save error:', error);
        showAlert('Failed to save profile. Please try again.', 'danger');
    }
}

// Save preferences data
function savePreferencesData(data) {
    try {
        // Store in localStorage (in real app, send to server)
        localStorage.setItem('userPreferences', JSON.stringify(data));
        
        // Apply theme immediately if changed
        if (data.theme) {
            applyTheme(data.theme);
        }
        
        showAlert('Preferences saved successfully!', 'success');
    } catch (error) {
        console.error('Save error:', error);
        showAlert('Failed to save preferences. Please try again.', 'danger');
    }
}

// Load user settings from storage
function loadUserSettings() {
    try {
        // Load profile data
        const profileData = localStorage.getItem('userProfile');
        if (profileData) {
            const data = JSON.parse(profileData);
            populateProfileForm(data);
        }
        
        // Load preferences data
        const preferencesData = localStorage.getItem('userPreferences');
        if (preferencesData) {
            const data = JSON.parse(preferencesData);
            populatePreferencesForm(data);
        }
    } catch (error) {
        console.error('Load settings error:', error);
    }
}

// Populate profile form with data
function populateProfileForm(data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.value = data[key];
        }
    });
}

// Populate preferences form with data
function populatePreferencesForm(data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'radio') {
                if (element.value === data[key]) {
                    element.checked = true;
                }
            } else if (element.type === 'checkbox') {
                element.checked = data[key] === 'true' || data[key] === true;
            } else {
                element.value = data[key];
            }
        }
    });
}

// Apply theme
function applyTheme(theme) {
    const body = document.body;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');
    
    switch (theme) {
        case 'dark':
            body.classList.add('theme-dark');
            break;
        case 'auto':
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
            break;
        default:
            body.classList.add('theme-light');
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.content-wrapper .container-fluid');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top
    alertContainer.insertBefore(alertElement, alertContainer.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 5000);
}

function showLoading(button) {
    button.classList.add('loading');
    button.disabled = true;
}

function hideLoading(button) {
    button.classList.remove('loading');
    button.disabled = false;
}

function showFieldError(field, message) {
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
}

function hideFieldError(field) {
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

// Settings action functions
function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (!currentPassword || !newPassword || !confirmPassword) {
        showAlert('Please fill in all password fields.', 'danger');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showAlert('New passwords do not match.', 'danger');
        return;
    }
    
    // Simulate password change
    showAlert('Password changed successfully!', 'success');
    const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
    modal.hide();
    
    // Clear form
    document.getElementById('changePasswordForm').reset();
}

function saveSecurityQuestions() {
    const questions = [];
    for (let i = 1; i <= 3; i++) {
        const question = document.getElementById(`question${i}`).value;
        const answer = document.getElementById(`answer${i}`).value;
        
        if (question && answer) {
            questions.push({ question, answer });
        }
    }
    
    if (questions.length < 3) {
        showAlert('Please complete all three security questions.', 'danger');
        return;
    }
    
    // Save security questions
    localStorage.setItem('securityQuestions', JSON.stringify(questions));
    showAlert('Security questions saved successfully!', 'success');
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('securityQuestionsModal'));
    modal.hide();
}

function saveSecuritySettings() {
    const settings = {
        sms2FA: document.getElementById('sms2FA').checked,
        app2FA: document.getElementById('app2FA').checked,
        maxFailedAttempts: document.getElementById('maxFailedAttempts').value,
        lockoutDuration: document.getElementById('lockoutDuration').value,
        logLogins: document.getElementById('logLogins').checked,
        logActions: document.getElementById('logActions').checked
    };
    
    localStorage.setItem('securitySettings', JSON.stringify(settings));
    showAlert('Security settings saved successfully!', 'success');
}

function saveNotificationSettings() {
    const settings = {
        emailLoans: document.getElementById('emailLoans').checked,
        emailPayments: document.getElementById('emailPayments').checked,
        emailReports: document.getElementById('emailReports').checked,
        smsCritical: document.getElementById('smsCritical').checked,
        smsPayments: document.getElementById('smsPayments').checked,
        pushRealtime: document.getElementById('pushRealtime').checked,
        pushSummary: document.getElementById('pushSummary').checked,
        emailFrequency: document.getElementById('emailFrequency').value,
        quietStart: document.getElementById('quietStart').value,
        quietEnd: document.getElementById('quietEnd').value
    };
    
    localStorage.setItem('notificationSettings', JSON.stringify(settings));
    showAlert('Notification settings saved successfully!', 'success');
}

function saveSystemSettings() {
    showAlert('System settings saved successfully!', 'success');
}

function saveDataSettings() {
    showAlert('Data settings saved successfully!', 'success');
}

function resetPreferences() {
    if (confirm('Are you sure you want to reset all preferences to default values?')) {
        localStorage.removeItem('userPreferences');
        location.reload();
    }
}

function terminateAllSessions() {
    if (confirm('This will log you out of all other devices. Continue?')) {
        showAlert('All other sessions have been terminated.', 'success');
    }
}

function testNotifications() {
    showAlert('Test notification sent! Check your email and phone.', 'info');
}

function exportData(type) {
    showAlert(`Exporting ${type} data... Download will start shortly.`, 'info');
    
    // Simulate export
    setTimeout(() => {
        showAlert(`${type} data exported successfully!`, 'success');
    }, 2000);
}

function importData(type) {
    const fileInput = document.getElementById(`${type}Import`);
    if (!fileInput.files.length) {
        showAlert('Please select a file to import.', 'danger');
        return;
    }
    
    showAlert(`Importing ${type} data...`, 'info');
    
    // Simulate import
    setTimeout(() => {
        showAlert(`${type} data imported successfully!`, 'success');
    }, 3000);
}

function createBackup() {
    showAlert('Creating system backup...', 'info');
    
    setTimeout(() => {
        showAlert('System backup created successfully!', 'success');
    }, 5000);
}

function restoreBackup() {
    const fileInput = document.getElementById('backupRestore');
    if (!fileInput.files.length) {
        showAlert('Please select a backup file.', 'danger');
        return;
    }
    
    // Modal will handle the confirmation
}

function executeRestore() {
    showAlert('Restoring from backup...', 'info');
    
    setTimeout(() => {
        showAlert('System restored successfully! Please log in again.', 'success');
        // In real app, redirect to login
    }, 10000);
}

function executeSystemReset() {
    showAlert('Resetting system settings...', 'info');
    
    setTimeout(() => {
        showAlert('System settings reset to defaults.', 'success');
        location.reload();
    }, 3000);
}

// Additional utility functions for system administration
function initiateBackup() {
    showAlert('Manual backup initiated...', 'info');
    setTimeout(() => showAlert('Backup completed successfully!', 'success'), 3000);
}

function viewBackupHistory() {
    showAlert('Opening backup history...', 'info');
}

function optimizeDatabase() {
    showAlert('Optimizing database...', 'info');
    setTimeout(() => showAlert('Database optimization completed!', 'success'), 5000);
}

function clearCache() {
    showAlert('Clearing system cache...', 'info');
    setTimeout(() => showAlert('Cache cleared successfully!', 'success'), 2000);
}

function viewSystemLogs() {
    showAlert('Opening system logs...', 'info');
}

function scheduleDataMaintenance() {
    showAlert('Data maintenance scheduled successfully!', 'success');
}

function downloadTemplate() {
    showAlert('Downloading import templates...', 'info');
}