import csv
import io
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from models import Transaction, Category

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    today = date.today()
    period = request.args.get('period', 'this_month')

    if period == 'this_month':
        start_date = date(today.year, today.month, 1)
        end_date = today
        period_title = f"{today.strftime('%B %Y')} (This Month)"
    elif period == 'last_month':
        last_m = today - relativedelta(months=1)
        start_date = date(last_m.year, last_m.month, 1)
        # last day of last month
        next_first = date(today.year, today.month, 1)
        end_date = next_first - timedelta(days=1)
        period_title = f"{last_m.strftime('%B %Y')} (Last Month)"
    elif period == 'last_3_months':
        start_date = today - relativedelta(months=3)
        end_date = today
        period_title = "Last 3 Months"
    elif period == 'last_6_months':
        start_date = today - relativedelta(months=6)
        end_date = today
        period_title = "Last 6 Months"
    elif period == 'this_year':
        start_date = date(today.year, 1, 1)
        end_date = today
        period_title = f"{today.year} (Year-to-Date)"
    else:  # all_time
        start_date = date(2000, 1, 1)
        end_date = today
        period_title = "All Time"

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date.asc()).all()

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_savings = round(total_income - total_expense, 2)
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Category breakdown for expenses
    cat_totals = defaultdict(float)
    cat_counts = defaultdict(int)
    for t in transactions:
        if t.type == 'expense':
            c_name = t.category.name if t.category else 'Other'
            cat_totals[c_name] += t.amount
            cat_counts[c_name] += 1

    category_summary = []
    for c_name, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        pct = round((amt / total_expense * 100), 1) if total_expense > 0 else 0.0
        category_summary.append({
            'name': c_name,
            'amount': round(amt, 2),
            'count': cat_counts[c_name],
            'percentage': pct
        })

    # Timeline data for daily/monthly trend chart
    date_expenses = defaultdict(float)
    date_income = defaultdict(float)
    for t in transactions:
        d_str = t.date.strftime('%Y-%m-%d')
        if t.type == 'expense':
            date_expenses[d_str] += t.amount
        else:
            date_income[d_str] += t.amount

    sorted_dates = sorted(list(set(list(date_expenses.keys()) + list(date_income.keys()))))
    timeline_labels = sorted_dates
    timeline_expense = [round(date_expenses[d], 2) for d in sorted_dates]
    timeline_income = [round(date_income[d], 2) for d in sorted_dates]

    return render_template(
        'reports.html',
        period=period,
        period_title=period_title,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_savings=net_savings,
        savings_rate=savings_rate,
        transaction_count=len(transactions),
        category_summary=category_summary,
        timeline_labels=timeline_labels,
        timeline_expense=timeline_expense,
        timeline_income=timeline_income,
        pie_labels=[c['name'] for c in category_summary],
        pie_data=[c['amount'] for c in category_summary]
    )

@reports_bp.route('/reports/export-csv')
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Date', 'Type', 'Category', 'Description', 'Amount (INR)', 'Created At'])

    for t in transactions:
        cw.writerow([
            t.id,
            t.date.strftime('%Y-%m-%d'),
            t.type.capitalize(),
            t.category.name if t.category else 'N/A',
            t.description,
            f"{t.amount:.2f}",
            t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = f"attachment; filename=smart_expense_transactions_{date.today().strftime('%Y%m%d')}.csv"
    return output

