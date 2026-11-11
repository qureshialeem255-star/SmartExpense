from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from models import db, SavingsGoal
from forms import SavingsGoalForm

savings_bp = Blueprint('savings', __name__)

@savings_bp.route('/savings', methods=['GET', 'POST'])
@login_required
def index():
    form = SavingsGoalForm()

    if form.validate_on_submit():
        goal = SavingsGoal(
            user_id=current_user.id,
            title=form.title.data.strip(),
            target_amount=form.target_amount.data,
            current_amount=form.current_amount.data or 0.0,
            deadline=form.deadline.data
        )
        db.session.add(goal)
        db.session.commit()
        flash(f'Savings goal "{goal.title}" created successfully!', 'success')
        return redirect(url_for('savings.index'))

    goals = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(SavingsGoal.deadline.asc(), SavingsGoal.id.desc()).all()

    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0

    return render_template(
        'savings.html',
        form=form,
        goals=goals,
        total_target=round(total_target, 2),
        total_saved=round(total_saved, 2),
        overall_progress=overall_progress,
        today=date.today()
    )

@savings_bp.route('/savings/add-funds/<int:id>', methods=['POST'])
@login_required
def add_funds(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount = float(request.form.get('deposit_amount', 0.0))
    if amount > 0:
        goal.current_amount = round(goal.current_amount + amount, 2)
        db.session.commit()
        if goal.is_completed:
            flash(f'🎉 Congratulations! You reached your savings goal "{goal.title}"!', 'success')
        else:
            flash(f'Added ₹{amount:,.2f} to "{goal.title}". Remaining: ₹{goal.remaining_amount:,.2f}', 'success')
    else:
        flash('Please enter a valid positive amount.', 'warning')

    return redirect(url_for('savings.index'))

@savings_bp.route('/savings/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash(f'Savings goal "{goal.title}" removed.', 'info')
    return redirect(url_for('savings.index'))

