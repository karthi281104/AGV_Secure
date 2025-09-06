"""
Validation utilities for AGV Finance application
Provides comprehensive validation for forms and data inputs
"""

import re
import decimal
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any


class ValidationError(Exception):
    """Custom validation error"""
    pass


class Validator:
    """Comprehensive validation utility class"""
    
    # Regex patterns
    MOBILE_PATTERN = re.compile(r'^[6-9]\d{9}$')  # Indian mobile number
    PAN_PATTERN = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')  # PAN format
    AADHAR_PATTERN = re.compile(r'^\d{12}$')  # Aadhar format
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Tuple[bool, str]:
        """Validate that all required fields are present and not empty"""
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return False, f"Field '{field}' is required"
        return True, "All required fields present"
    
    @staticmethod
    def validate_mobile(mobile: str) -> Tuple[bool, str]:
        """Validate Indian mobile number"""
        if not mobile:
            return False, "Mobile number is required"
        
        mobile = re.sub(r'[^\d]', '', mobile)  # Remove non-digits
        
        if len(mobile) == 11 and mobile.startswith('0'):
            mobile = mobile[1:]  # Remove leading 0
        
        if not Validator.MOBILE_PATTERN.match(mobile):
            return False, "Invalid mobile number format (should be 10 digits starting with 6-9)"
        
        return True, mobile
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email:
            return True, ""  # Email is optional
        
        if not Validator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, email.lower()
    
    @staticmethod
    def validate_pan(pan: str) -> Tuple[bool, str]:
        """Validate PAN number format"""
        if not pan:
            return True, ""  # PAN is optional in some cases
        
        pan = pan.upper().strip()
        
        if not Validator.PAN_PATTERN.match(pan):
            return False, "Invalid PAN format (should be like ABCDE1234F)"
        
        return True, pan
    
    @staticmethod
    def validate_aadhar(aadhar: str) -> Tuple[bool, str]:
        """Validate Aadhar number format"""
        if not aadhar:
            return True, ""  # Aadhar is optional in some cases
        
        aadhar = re.sub(r'[^\d]', '', aadhar)  # Remove non-digits
        
        if not Validator.AADHAR_PATTERN.match(aadhar):
            return False, "Invalid Aadhar format (should be 12 digits)"
        
        return True, aadhar
    
    @staticmethod
    def validate_amount(amount: str, min_amount: float = 0.01, max_amount: float = 10000000) -> Tuple[bool, decimal.Decimal, str]:
        """Validate monetary amount"""
        try:
            amount_decimal = decimal.Decimal(str(amount))
            
            if amount_decimal < decimal.Decimal(str(min_amount)):
                return False, amount_decimal, f"Amount must be at least ₹{min_amount}"
            
            if amount_decimal > decimal.Decimal(str(max_amount)):
                return False, amount_decimal, f"Amount cannot exceed ₹{max_amount:,.2f}"
            
            return True, amount_decimal, "Valid amount"
            
        except (ValueError, decimal.InvalidOperation):
            return False, decimal.Decimal('0'), "Invalid amount format"
    
    @staticmethod
    def validate_interest_rate(rate: str) -> Tuple[bool, decimal.Decimal, str]:
        """Validate interest rate"""
        try:
            rate_decimal = decimal.Decimal(str(rate))
            
            if rate_decimal <= 0:
                return False, rate_decimal, "Interest rate must be greater than 0"
            
            if rate_decimal > 100:
                return False, rate_decimal, "Interest rate cannot exceed 100%"
            
            return True, rate_decimal, "Valid interest rate"
            
        except (ValueError, decimal.InvalidOperation):
            return False, decimal.Decimal('0'), "Invalid interest rate format"
    
    @staticmethod
    def validate_tenure(tenure: str) -> Tuple[bool, int, str]:
        """Validate loan tenure in months"""
        try:
            tenure_int = int(tenure)
            
            if tenure_int <= 0:
                return False, tenure_int, "Tenure must be greater than 0"
            
            if tenure_int > 360:  # Max 30 years
                return False, tenure_int, "Tenure cannot exceed 360 months (30 years)"
            
            return True, tenure_int, "Valid tenure"
            
        except ValueError:
            return False, 0, "Invalid tenure format"
    
    @staticmethod
    def validate_date(date_str: str, allow_future: bool = True) -> Tuple[bool, Optional[datetime], str]:
        """Validate date format and constraints"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if not allow_future and date_obj > datetime.now():
                return False, date_obj, "Date cannot be in the future"
            
            # Check if date is too far in the past (more than 50 years)
            fifty_years_ago = datetime.now() - timedelta(days=365*50)
            if date_obj < fifty_years_ago:
                return False, date_obj, "Date is too far in the past"
            
            return True, date_obj, "Valid date"
            
        except ValueError:
            return False, None, "Invalid date format"
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> Tuple[bool, str]:
        """Validate person name"""
        if not name:
            return False, "Name is required"
        
        name = name.strip()
        
        if len(name) < min_length:
            return False, f"Name must be at least {min_length} characters"
        
        if len(name) > max_length:
            return False, f"Name cannot exceed {max_length} characters"
        
        # Check for valid characters (letters, spaces, some special chars)
        if not re.match(r'^[a-zA-Z\s\.\-\']+$', name):
            return False, "Name contains invalid characters"
        
        return True, name.title()  # Capitalize properly
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 5) -> Tuple[bool, str]:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False, f"File size exceeds {max_size_mb}MB limit"
        
        return True, "File size is acceptable"


class CustomerValidator:
    """Specialized validator for customer data"""
    
    @staticmethod
    def validate_customer_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Validate complete customer data"""
        errors = {}
        
        # Required fields
        required_fields = ['name', 'mobile']
        is_valid, msg = Validator.validate_required_fields(data, required_fields)
        if not is_valid:
            errors['general'] = msg
        
        # Name validation
        if 'name' in data:
            is_valid, result = Validator.validate_name(data['name'])
            if not is_valid:
                errors['name'] = result
        
        # Mobile validation
        if 'mobile' in data:
            is_valid, result = Validator.validate_mobile(data['mobile'])
            if not is_valid:
                errors['mobile'] = result
        
        # Additional mobile validation (optional)
        if data.get('additional_mobile'):
            is_valid, result = Validator.validate_mobile(data['additional_mobile'])
            if not is_valid:
                errors['additional_mobile'] = result
        
        # Email validation (optional)
        if data.get('email'):
            is_valid, result = Validator.validate_email(data['email'])
            if not is_valid:
                errors['email'] = result
        
        # PAN validation (optional)
        if data.get('pan_number'):
            is_valid, result = Validator.validate_pan(data['pan_number'])
            if not is_valid:
                errors['pan_number'] = result
        
        # Aadhar validation (optional)
        if data.get('aadhar_number'):
            is_valid, result = Validator.validate_aadhar(data['aadhar_number'])
            if not is_valid:
                errors['aadhar_number'] = result
        
        return len(errors) == 0, errors


class LoanValidator:
    """Specialized validator for loan data"""
    
    @staticmethod
    def validate_loan_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Validate complete loan data"""
        errors = {}
        
        # Required fields
        required_fields = ['customer_id', 'principal_amount', 'interest_rate', 'tenure_months', 'loan_type']
        is_valid, msg = Validator.validate_required_fields(data, required_fields)
        if not is_valid:
            errors['general'] = msg
        
        # Principal amount validation
        if 'principal_amount' in data:
            is_valid, amount, msg = Validator.validate_amount(data['principal_amount'], min_amount=1000, max_amount=10000000)
            if not is_valid:
                errors['principal_amount'] = msg
        
        # Interest rate validation
        if 'interest_rate' in data:
            is_valid, rate, msg = Validator.validate_interest_rate(data['interest_rate'])
            if not is_valid:
                errors['interest_rate'] = msg
        
        # Tenure validation
        if 'tenure_months' in data:
            is_valid, tenure, msg = Validator.validate_tenure(data['tenure_months'])
            if not is_valid:
                errors['tenure_months'] = msg
        
        # Loan type validation
        valid_loan_types = ['gold', 'personal', 'business', 'vehicle']
        if 'loan_type' in data and data['loan_type'] not in valid_loan_types:
            errors['loan_type'] = f"Invalid loan type. Valid types: {', '.join(valid_loan_types)}"
        
        return len(errors) == 0, errors
