from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from models import db, Budget, Category, Transaction
from forms import BudgetForm
from services.budget_analyzer import BudgetAnalyzer

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets', methods=['GET', 'POST'])
@login_required
def index():
    today = date.today()
    selected_month = int(request.args.get('month', today.month))
    selected_year = int(request.args.get('year', today.year))

    form = BudgetForm()
    # Populate category choices: 0 represents Overall budget, then all expense categories
    expense_categories = Category.query.filter(
        (Category.user_id == None) | (Category.user_id == current_user.id),
        Category.type == 'expense'
    ).order_by(Category.name.asc()).all()

    form.category_id.choices = [(0, 'Overall Monthly Budget')] + [(c.id, c.name) for c in expense_categories]

    if form.validate_on_submit():
        cat_id = None if form.category_id.data == 0 else form.category_id.data
        b_month = form.month.data
        b_year = form.year.data
        b_amount = form.amount.data

        # Check if budget already exists for this month/year/category
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=cat_id,
            month=b_month,
            year=b_year
        ).first()

        if existing:
            existing.amount = b_amount
            flash(f'Budget updated to ₹{b_amount:,.2f}!', 'success')
        else:
            new_budget = Budget(
                user_id=current_user.id,
                category_id=cat_id,
                amount=b_amount,
                month=b_month,
                year=b_year
            )
            db.session.add(new_budget)
            flash(f'Budget of ₹{b_amount:,.2f} saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('budgets.index', month=b_month, year=b_year))

    # Retrieve all budgets and transactions for analysis
    all_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    all_txs = Transaction.query.filter_by(user_id=current_user.id).all()

    target_date = date(selected_year, selected_month, min(today.day, 28) if (selected_month == today.month and selected_year == today.year) else 1)
    analysis = BudgetAnalyzer.analyze_budgets(all_budgets, all_txs, target_date=target_date)

    return render_template(
        'budgets.html',
        form=form,
        analysis=analysis,
        selected_month=selected_month,
        selected_year=selected_year
    )

@budgets_bp.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Budget limit removed successfully.', 'info')
    return redirect(url_for('budgets.index', month=budget.month, year=budget.year))

