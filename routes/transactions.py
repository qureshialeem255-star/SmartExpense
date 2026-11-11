from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from models import db, Transaction, Category
from forms import TransactionForm
from services.category_predictor import CategoryPredictor

transactions_bp = Blueprint('transactions', __name__)

def get_user_categories(tx_type='expense'):
    """Get default categories plus user's custom categories for given type."""
    return Category.query.filter(
        (Category.user_id == None) | (Category.user_id == current_user.id),
        Category.type == tx_type
    ).order_by(Category.name.asc()).all()

@transactions_bp.route('/transactions')
@login_required
def index():
    # Filter params
    search_query = request.args.get('q', '').strip()
    filter_type = request.args.get('type', 'all')
    filter_cat = request.args.get('category', 'all')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = Transaction.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(Transaction.description.ilike(f'%{search_query}%'))
    if filter_type in ['income', 'expense']:
        query = query.filter(Transaction.type == filter_type)
    if filter_cat and filter_cat != 'all':
        query = query.filter(Transaction.category_id == int(filter_cat))
    if start_date:
        try:
            d_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= d_start)
        except ValueError:
            pass
    if end_date:
        try:
            d_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= d_end)
        except ValueError:
            pass

    transactions = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

    # Calculate filtered statistics
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_flow = total_income - total_expense

    # All available categories for filter dropdown
    all_categories = Category.query.filter(
        (Category.user_id == None) | (Category.user_id == current_user.id)
    ).order_by(Category.name.asc()).all()

    return render_template(
        'transactions.html',
        transactions=transactions,
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_flow=round(net_flow, 2),
        all_categories=all_categories,
        search_query=search_query,
        filter_type=filter_type,
        filter_cat=filter_cat,
        start_date=start_date,
        end_date=end_date
    )

@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add():
    form = TransactionForm()

    # Preload categories into choices
    tx_type = form.type.data if form.type.data else 'expense'
    categories = get_user_categories(tx_type)
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            category_id=form.category_id.data,
            type=form.type.data,
            amount=form.amount.data,
            description=form.description.data.strip(),
            date=form.date.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Transaction of ₹{transaction.amount:,.2f} recorded successfully!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('add_transaction.html', form=form, title='Add Transaction')

@transactions_bp.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)

    # Populate categories
    tx_type = form.type.data if request.method == 'POST' else transaction.type
    categories = get_user_categories(tx_type)
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        transaction.type = form.type.data
        transaction.category_id = form.category_id.data
        transaction.amount = form.amount.data
        transaction.description = form.description.data.strip()
        transaction.date = form.date.data

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('edit_transaction.html', form=form, transaction=transaction, title='Edit Transaction')

@transactions_bp.route('/transactions/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amt = transaction.amount
    db.session.delete(transaction)
    db.session.commit()
    flash(f'Transaction of ₹{amt:,.2f} deleted successfully.', 'info')
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/api/predict-category', methods=['POST'])
@login_required
def api_predict_category():
    """
    AJAX endpoint for instant AI category prediction as user types.
    """
    data = request.get_json(silent=True) or request.form
    description = data.get('description', '').strip()
    tx_type = data.get('type', 'expense')

    past_txs = Transaction.query.filter_by(user_id=current_user.id).all()
    prediction = CategoryPredictor.predict(
        description=description,
        transaction_type=tx_type,
        user_id=current_user.id,
        past_transactions=past_txs
    )

    # Match category name to category ID
    suggested_cat = Category.query.filter(
        ((Category.user_id == None) | (Category.user_id == current_user.id)),
        Category.name.ilike(prediction['category']),
        Category.type == tx_type
    ).first()

    return jsonify({
        'category_name': prediction['category'],
        'category_id': suggested_cat.id if suggested_cat else None,
        'confidence': prediction['confidence'],
        'reason': prediction['reason']
    })

@transactions_bp.route('/api/categories-by-type')
@login_required
def api_categories_by_type():
    tx_type = request.args.get('type', 'expense')
    categories = get_user_categories(tx_type)
    return jsonify([{'id': c.id, 'name': c.name, 'icon': c.icon, 'color': c.color} for c in categories])

