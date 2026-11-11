from .auth import auth_bp
from .dashboard import dashboard_bp
from .transactions import transactions_bp
from .budgets import budgets_bp
from .reports import reports_bp
from .insights import insights_bp
from .savings import savings_bp
from .categories import categories_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'transactions_bp',
    'budgets_bp',
    'reports_bp',
    'insights_bp',
    'savings_bp',
    'categories_bp'
]

