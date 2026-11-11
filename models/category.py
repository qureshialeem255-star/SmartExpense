from . import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    icon = db.Column(db.String(50), default='bi-tag')
    color = db.Column(db.String(20), default='#6366f1')

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

    DEFAULT_EXPENSE_CATEGORIES = [
        {'name': 'Food', 'icon': 'bi-cup-hot', 'color': '#ef4444'},
        {'name': 'Shopping', 'icon': 'bi-bag-check', 'color': '#ec4899'},
        {'name': 'Transport', 'icon': 'bi-car-front', 'color': '#f97316'},
        {'name': 'Education', 'icon': 'bi-mortarboard', 'color': '#3b82f6'},
        {'name': 'Bills', 'icon': 'bi-receipt', 'color': '#eab308'},
        {'name': 'Healthcare', 'icon': 'bi-heart-pulse', 'color': '#10b981'},
        {'name': 'Entertainment', 'icon': 'bi-film', 'color': '#8b5cf6'},
        {'name': 'Other', 'icon': 'bi-three-dots', 'color': '#6b7280'}
    ]

    DEFAULT_INCOME_CATEGORIES = [
        {'name': 'Salary', 'icon': 'bi-cash-stack', 'color': '#10b981'},
        {'name': 'Freelancing', 'icon': 'bi-laptop', 'color': '#06b6d4'},
        {'name': 'Business', 'icon': 'bi-briefcase', 'color': '#3b82f6'},
        {'name': 'Allowance', 'icon': 'bi-gift', 'color': '#8b5cf6'},
        {'name': 'Other income', 'icon': 'bi-piggy-bank', 'color': '#6366f1'}
    ]

    @classmethod
    def seed_default_categories(cls, db_session):
        """Seed default categories if they do not exist."""
        for item in cls.DEFAULT_EXPENSE_CATEGORIES:
            exists = cls.query.filter_by(name=item['name'], type='expense', user_id=None).first()
            if not exists:
                db_session.add(cls(name=item['name'], type='expense', icon=item['icon'], color=item['color'], user_id=None))
        for item in cls.DEFAULT_INCOME_CATEGORIES:
            exists = cls.query.filter_by(name=item['name'], type='income', user_id=None).first()
            if not exists:
                db_session.add(cls(name=item['name'], type='income', icon=item['icon'], color=item['color'], user_id=None))
        db_session.commit()

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'
