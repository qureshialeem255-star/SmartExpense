from datetime import datetime, date
from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Unknown',
            'category_color': self.category.color if self.category else '#6b7280',
            'category_icon': self.category.icon if self.category else 'bi-tag',
            'type': self.type,
            'amount': round(self.amount, 2),
            'description': self.description,
            'date': self.date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Transaction {self.type} {self.amount} - {self.description}>'

