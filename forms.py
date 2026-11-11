from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange, Optional
from datetime import date
from models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower().strip()).first()
        if user:
            raise ValidationError('An account with this email already exists. Please log in.')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password (only if changing password)')
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[
        Optional(),
        Length(min=6, message='New password must be at least 6 characters.')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='New passwords must match.')
    ])
    submit = SubmitField('Update Profile')

class TransactionForm(FlaskForm):
    type = SelectField('Transaction Type', choices=[('expense', 'Expense'), ('income', 'Income')], default='expense', validators=[DataRequired()])
    amount = FloatField('Amount (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Amount must be greater than zero.')
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=255)])
    date = DateField('Transaction Date', default=date.today, validators=[DataRequired()])
    submit = SubmitField('Save Transaction')

class BudgetForm(FlaskForm):
    category_id = SelectField('Category (Choose "Overall" for whole month)', coerce=int, validators=[Optional()])
    amount = FloatField('Monthly Limit (₹)', validators=[
        DataRequired(),
        NumberRange(min=1.0, message='Budget amount must be at least ₹1.00.')
    ])
    month = SelectField('Month', coerce=int, choices=[
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ], default=date.today().month, validators=[DataRequired()])
    year = SelectField('Year', coerce=int, choices=[
        (y, str(y)) for y in range(date.today().year - 2, date.today().year + 3)
    ], default=date.today().year, validators=[DataRequired()])
    submit = SubmitField('Save Budget')

class SavingsGoalForm(FlaskForm):
    title = StringField('Goal Name', validators=[DataRequired(), Length(min=2, max=100)])
    target_amount = FloatField('Target Amount (₹)', validators=[
        DataRequired(),
        NumberRange(min=1.0, message='Target amount must be at least ₹1.00.')
    ])
    current_amount = FloatField('Current Savings (₹)', default=0.0, validators=[
        NumberRange(min=0.0, message='Current amount cannot be negative.')
    ])
    deadline = DateField('Target Date / Deadline', validators=[Optional()])
    submit = SubmitField('Save Goal')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    type = SelectField('Category Type', choices=[('expense', 'Expense'), ('income', 'Income')], default='expense', validators=[DataRequired()])
    icon = SelectField('Icon', choices=[
        ('bi-tag', 'Tag (Default)'),
        ('bi-cup-hot', 'Food / Cup'),
        ('bi-bag-check', 'Shopping Bag'),
        ('bi-car-front', 'Transport / Car'),
        ('bi-mortarboard', 'Education / Cap'),
        ('bi-receipt', 'Bills / Receipt'),
        ('bi-heart-pulse', 'Healthcare / Heart'),
        ('bi-film', 'Entertainment / Film'),
        ('bi-cash-stack', 'Cash / Salary'),
        ('bi-laptop', 'Laptop / Freelance'),
        ('bi-briefcase', 'Briefcase / Business'),
        ('bi-gift', 'Gift / Allowance'),
        ('bi-piggy-bank', 'Piggy Bank / Savings'),
        ('bi-house', 'House / Rent'),
        ('bi-airplane', 'Flight / Travel'),
        ('bi-three-dots', 'Other')
    ], default='bi-tag')
    color = StringField('Color Accent', default='#6366f1')
    submit = SubmitField('Save Category')

