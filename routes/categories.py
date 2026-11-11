from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Category, Transaction
from forms import CategoryForm

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def index():
    form = CategoryForm()

    if form.validate_on_submit():
        cat_name = form.name.data.strip()
        cat_type = form.type.data

        # Check for duplicate
        existing = Category.query.filter(
            ((Category.user_id == None) | (Category.user_id == current_user.id)),
            Category.name.ilike(cat_name),
            Category.type == cat_type
        ).first()

        if existing:
            flash(f'A {cat_type} category named "{cat_name}" already exists.', 'warning')
        else:
            new_cat = Category(
                user_id=current_user.id,
                name=cat_name,
                type=cat_type,
                icon=form.icon.data,
                color=form.color.data
            )
            db.session.add(new_cat)
            db.session.commit()
            flash(f'Category "{cat_name}" added successfully!', 'success')
            return redirect(url_for('categories.index'))

    # Load categories
    default_expense = Category.query.filter_by(user_id=None, type='expense').all()
    default_income = Category.query.filter_by(user_id=None, type='income').all()
    custom_categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'categories.html',
        form=form,
        default_expense=default_expense,
        default_income=default_income,
        custom_categories=custom_categories
    )

@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    cat = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    # Check if category is used in transactions
    used = Transaction.query.filter_by(category_id=cat.id).first()
    if used:
        flash(f'Cannot delete category "{cat.name}" because transactions are currently assigned to it.', 'danger')
        return redirect(url_for('categories.index'))

    db.session.delete(cat)
    db.session.commit()
    flash(f'Custom category "{cat.name}" deleted successfully.', 'info')
    return redirect(url_for('categories.index'))

