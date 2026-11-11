from datetime import datetime, date
from . import db

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progress_percentage(self):
        if self.target_amount <= 0:
            return 100.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return min(round(pct, 1), 100.0)

    @property
    def remaining_amount(self):
        return max(0.0, round(self.target_amount - self.current_amount, 2))

    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount

    def __repr__(self):
        return f'<SavingsGoal {self.title}: {self.current_amount}/{self.target_amount}>'

