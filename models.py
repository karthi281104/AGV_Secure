from sqlalchemy import String, Integer, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid
from typing import Optional
from extensions import db


class Customer(db.Model):
    __tablename__ = 'customers'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Personal Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)  # Changed from 'phone'
    additional_mobile: Mapped[Optional[str]] = mapped_column(String(15))  # NEW
    father_name: Mapped[Optional[str]] = mapped_column(String(100))  # NEW
    mother_name: Mapped[Optional[str]] = mapped_column(String(100))  # NEW

    # Contact Information
    email: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(Text)

    # Document Information
    aadhar_number: Mapped[Optional[str]] = mapped_column(String(16))  # Increase from 12 to 16
    pan_number: Mapped[Optional[str]] = mapped_column(String(10))

    # Cloud Storage URLs for documents
    pan_photo_url: Mapped[Optional[str]] = mapped_column(String(500))  # NEW
    aadhar_photo_url: Mapped[Optional[str]] = mapped_column(String(500))  # NEW
    document_metadata: Mapped[Optional[str]] = mapped_column(Text)  # NEW - JSON string

    # Biometric Information
    fingerprint_data: Mapped[Optional[str]] = mapped_column(Text)  # Renamed from biometric_data

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loans: Mapped[list["Loan"]] = relationship(back_populates="customer")

    def __repr__(self):
        return f'<Customer {self.name}>'


# Keep your Loan and Payment models as they are
class Loan(db.Model):
    __tablename__ = 'loans'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    loan_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    principal_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    disbursed_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    maturity_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    loan_type: Mapped[str] = mapped_column(String(50), default='gold')
    collateral_details: Mapped[Optional[dict]] = mapped_column(JSON)
    document_urls: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="loans")
    payments: Mapped[list["Payment"]] = relationship(back_populates="loan")

    def __repr__(self):
        return f'<Loan {self.loan_number}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('loans.id'), nullable=False)
    payment_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    
    # Payment Details
    payment_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    payment_method: Mapped[str] = mapped_column(String(50), default='cash')  # cash, cheque, online, card
    payment_status: Mapped[str] = mapped_column(String(20), default='completed')  # pending, completed, failed
    
    # EMI Details
    emi_month: Mapped[Optional[int]] = mapped_column(Integer)  # Which EMI month this payment is for
    principal_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    interest_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    
    # Payment Reference
    reference_number: Mapped[Optional[str]] = mapped_column(String(50))  # Bank reference, cheque number, etc.
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Receipt Information
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan: Mapped["Loan"] = relationship(back_populates="payments")

    def __repr__(self):
        return f'<Payment {self.payment_number}>'