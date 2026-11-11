from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from models import Transaction, Budget, SavingsGoal
from services.expense_analyzer import ExpenseAnalyzer
from services.budget_analyzer import BudgetAnalyzer
from services.expense_predictor import ExpensePredictor

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    current_month = today.month
    current_year = today.year

    # All transactions for current user
    all_txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc(), Transaction.id.desc()).all()

    # Calculate overall lifetime totals
    lifetime_income = sum(tx.amount for tx in all_txs if tx.type == 'income')
    lifetime_expense = sum(tx.amount for tx in all_txs if tx.type == 'expense')
    available_balance = round(lifetime_income - lifetime_expense, 2)

    # Current month calculations
    current_month_txs = [tx for tx in all_txs if tx.date.year == current_year and tx.date.month == current_month]
    month_income = sum(tx.amount for tx in current_month_txs if tx.type == 'income')
    month_expense = sum(tx.amount for tx in current_month_txs if tx.type == 'expense')
    month_savings = round(month_income - month_expense, 2)

    # Recent transactions (top 7)
    recent_transactions = all_txs[:7]

    # Run AI Analyzers
    spending_summary = ExpenseAnalyzer.analyze_spending(all_txs, today)
    user_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    user_savings = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    budget_summary = BudgetAnalyzer.analyze_budgets(user_budgets, all_txs, user_savings, today)
    prediction_summary = ExpensePredictor.predict_next_month(all_txs, today)

    # Combine top AI insights
    combined_insights = []
    if spending_summary.get('insights'):
        combined_insights.extend(spending_summary['insights'][:2])
    if budget_summary.get('suggestions'):
        combined_insights.extend(budget_summary['suggestions'][:2])

    # Category expense breakdown for current month (Chart 1: Doughnut)
    cat_breakdown = defaultdict(float)
    for tx in current_month_txs:
        if tx.type == 'expense':
            cat_name = tx.category.name if tx.category else 'Other'
            cat_breakdown[cat_name] += tx.amount

    category_labels = list(cat_breakdown.keys())
    category_data = [round(v, 2) for v in cat_breakdown.values()]

    # Last 6 Months Income vs Expense (Chart 2: Bar / Line)
    six_months_labels = []
    monthly_income_data = []
    monthly_expense_data = []

    for i in range(5, -1, -1):
        target_m = today - relativedelta(months=i)
        y, m = target_m.year, target_m.month
        month_label = target_m.strftime('%b %Y')
        six_months_labels.append(month_label)

        m_inc = sum(tx.amount for tx in all_txs if tx.date.year == y and tx.date.month == m and tx.type == 'income')
        m_exp = sum(tx.amount for tx in all_txs if tx.date.year == y and tx.date.month == m and tx.type == 'expense')
        monthly_income_data.append(round(m_inc, 2))
        monthly_expense_data.append(round(m_exp, 2))

    return render_template(
        'dashboard.html',
        available_balance=available_balance,
        lifetime_income=round(lifetime_income, 2),
        lifetime_expense=round(lifetime_expense, 2),
        month_income=round(month_income, 2),
        month_expense=round(month_expense, 2),
        month_savings=month_savings,
        recent_transactions=recent_transactions,
        spending_summary=spending_summary,
        budget_summary=budget_summary,
        prediction_summary=prediction_summary,
        combined_insights=combined_insights,
        category_labels=category_labels,
        category_data=category_data,
        six_months_labels=six_months_labels,
        monthly_income_data=monthly_income_data,
        monthly_expense_data=monthly_expense_data
    )

