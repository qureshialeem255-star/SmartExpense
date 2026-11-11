from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from models import db, Transaction, Budget, SavingsGoal, AIInsight
from services.expense_analyzer import ExpenseAnalyzer
from services.budget_analyzer import BudgetAnalyzer
from services.expense_predictor import ExpensePredictor

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights')
@login_required
def index():
    today = date.today()
    all_txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    user_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    user_savings = SavingsGoal.query.filter_by(user_id=current_user.id).all()

    spending_analysis = ExpenseAnalyzer.analyze_spending(all_txs, today)
    budget_analysis = BudgetAnalyzer.analyze_budgets(user_budgets, all_txs, user_savings, today)
    prediction = ExpensePredictor.predict_next_month(all_txs, today)

    # Calculate Financial Health Score (0 - 100)
    score = 70  # Baseline
    if spending_analysis['current_income'] > 0:
        savings_r = spending_analysis['savings_rate']
        if savings_r >= 30:
            score += 20
        elif savings_r >= 15:
            score += 10
        elif savings_r < 0:
            score -= 25

    if budget_analysis['overall_budget']:
        if budget_analysis['overall_budget']['percentage_used'] <= 80:
            score += 10
        elif budget_analysis['overall_budget']['percentage_used'] > 100:
            score -= 20

    score = max(10, min(100, score))

    if score >= 80:
        health_status = 'Excellent'
        health_color = 'success'
    elif score >= 60:
        health_status = 'Good'
        health_color = 'primary'
    elif score >= 40:
        health_status = 'Fair / Caution'
        health_color = 'warning'
    else:
        health_status = 'Critical Attention Needed'
        health_color = 'danger'

    # Retrieve stored AI insight history
    saved_insights = AIInsight.query.filter_by(user_id=current_user.id).order_by(AIInsight.created_at.desc()).limit(15).all()

    return render_template(
        'insights.html',
        spending_analysis=spending_analysis,
        budget_analysis=budget_analysis,
        prediction=prediction,
        health_score=score,
        health_status=health_status,
        health_color=health_color,
        saved_insights=saved_insights
    )

@insights_bp.route('/insights/refresh', methods=['POST'])
@login_required
def refresh():
    today = date.today()
    all_txs = Transaction.query.filter_by(user_id=current_user.id).all()
    user_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    user_savings = SavingsGoal.query.filter_by(user_id=current_user.id).all()

    spending_analysis = ExpenseAnalyzer.analyze_spending(all_txs, today)
    budget_analysis = BudgetAnalyzer.analyze_budgets(user_budgets, all_txs, user_savings, today)
    prediction = ExpensePredictor.predict_next_month(all_txs, today)

    # Persist newly discovered insights into AIInsight table
    new_count = 0
    for ins in spending_analysis.get('insights', []):
        existing = AIInsight.query.filter_by(user_id=current_user.id, message=ins['message']).first()
        if not existing:
            db.session.add(AIInsight(user_id=current_user.id, insight_type=ins['type'], message=ins['message']))
            new_count += 1

    for sug in budget_analysis.get('suggestions', []):
        existing = AIInsight.query.filter_by(user_id=current_user.id, message=sug['message']).first()
        if not existing:
            db.session.add(AIInsight(user_id=current_user.id, insight_type=sug['type'], message=sug['message']))
            new_count += 1

    if prediction.get('has_sufficient_data'):
        pred_msg = f"Upcoming Month Forecast: Estimated ₹{prediction['predicted_total']:,.2f} for {prediction['next_month_label']} ({prediction['trend_direction']} trend)."
        existing = AIInsight.query.filter_by(user_id=current_user.id, message=pred_msg).first()
        if not existing:
            db.session.add(AIInsight(user_id=current_user.id, insight_type='prediction', message=pred_msg))
            new_count += 1

    db.session.commit()
    flash(f'AI Analytics refreshed successfully! Generated {new_count} new insight records.', 'success')
    return redirect(url_for('insights.index'))

