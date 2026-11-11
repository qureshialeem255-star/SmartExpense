from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

from .user import User
from .category import Category
from .transaction import Transaction
from .budget import Budget
from .savings import SavingsGoal
from .ai_insight import AIInsight

__all__ = ['db', 'login_manager', 'User', 'Category', 'Transaction', 'Budget', 'SavingsGoal', 'AIInsight']

