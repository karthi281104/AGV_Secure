from models import db, Customer, Loan, Payment
from sqlalchemy import func


class DashboardService:
    @staticmethod
    def get_dashboard_metrics():
        try:
            # Total active customers
            total_customers = Customer.query.filter_by(status='active').count()

            # Total disbursed amount
            total_disbursed = db.session.query(
                func.coalesce(func.sum(Loan.principal_amount), 0)
            ).filter_by(status='active').scalar()

            # Total interest collected
            total_interest = db.session.query(
                func.coalesce(func.sum(Payment.interest_amount), 0)
            ).scalar()

            # Active loans count
            active_loans = Loan.query.filter_by(status='active').count()

            # Overdue loans (past maturity date)
            overdue_loans = Loan.query.filter(
                Loan.maturity_date < func.now(),
                Loan.status == 'active'
            ).count()

            return {
                'total_customers': total_customers,
                'total_disbursed': float(total_disbursed),
                'total_interest': float(total_interest),
                'active_loans': active_loans,
                'overdue_loans': overdue_loans
            }
        except Exception as e:
            print(f"Dashboard metrics error: {e}")
            return {
                'total_customers': 0,
                'total_disbursed': 0.0,
                'total_interest': 0.0,
                'active_loans': 0,
                'overdue_loans': 0
            }