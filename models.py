from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid
from typing import Optional
from app import db



class Customer(db.Model):
    __tablename__ = 'customers'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(Text)
    aadhar_number: Mapped[Optional[str]] = mapped_column(String(12))
    pan_number: Mapped[Optional[str]] = mapped_column(String(10))
    biometric_data: Mapped[Optional[str]] = mapped_column(Text)
    #status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loans: Mapped[list["Loan"]] = relationship(back_populates="customer")

    def __repr__(self):
        return f'<Customer {self.name}>'


class Loan(db.Model):
    __tablename__ = 'loans'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey('customers.id'), nullable=False)
    loan_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    principal_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    disbursed_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    maturity_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    loan_type: Mapped[str] = mapped_column(String(50), default='gold')
    collateral_details: Mapped[Optional[dict]] = mapped_column(JSON)
    document_urls: Mapped[Optional[dict]] = mapped_column(JSON)
    #status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="loans")
    payments: Mapped[list["Payment"]] = relationship(back_populates="loan")

    def __repr__(self):
        return f'<Loan {self.loan_number}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_id: Mapped[str] = mapped_column(String(36), ForeignKey('loans.id'), nullable=False)
    payment_number: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    principal_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    interest_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    payment_method: Mapped[str] = mapped_column(String(50), default='cash')
    receipt_number: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    loan: Mapped["Loan"] = relationship(back_populates="payments")

    def __repr__(self):
        return f'<Payment {self.payment_number}>'


class Employee(db.Model):
    __tablename__ = 'employees'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auth0_user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default='employee')
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def __repr__(self):
        return f'<Employee {self.name}>'