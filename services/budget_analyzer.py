import calendar
from datetime import date
from collections import defaultdict

class BudgetAnalyzer:
    """
    Intelligent budget auditing, burn-rate velocity tracking,
    category overrun alerts, and smart budget reallocation suggestions.
    """

    @staticmethod
    def analyze_budgets(budgets, transactions, savings_goals=None, target_date=None):
        if target_date is None:
            target_date = date.today()

        current_month = target_date.month
        current_year = target_date.year
        current_day = target_date.day

        # Days in current month
        _, days_in_month = calendar.monthrange(current_year, current_month)
        days_passed = max(current_day, 1)
        days_remaining = max(days_in_month - days_passed, 0)
        month_progress_pct = round((days_passed / days_in_month) * 100, 1)

        # Calculate actual expenses for the month
        cat_expenses = defaultdict(float)
        total_expense = 0.0
        total_income = 0.0

        for tx in transactions:
            if tx.date.year == current_year and tx.date.month == current_month:
                amt = float(tx.amount)
                if tx.type == 'expense':
                    total_expense += amt
                    cat_name = tx.category.name if tx.category else 'Other'
                    cat_expenses[cat_name] += amt
                elif tx.type == 'income':
                    total_income += amt

        # Find overall budget and category budgets for this month
        overall_budget_obj = None
        category_budget_objs = []

        for b in budgets:
            if b.month == current_month and b.year == current_year:
                if b.category_id is None:
                    overall_budget_obj = b
                else:
                    category_budget_objs.append(b)

        # Evaluate Overall Budget
        overall_analysis = None
        if overall_budget_obj:
            b_amt = float(overall_budget_obj.amount)
            pct_used = round((total_expense / b_amt * 100), 1) if b_amt > 0 else 0.0
            remaining = round(b_amt - total_expense, 2)
            daily_burn = round(total_expense / days_passed, 2)
            projected_month_end = round(daily_burn * days_in_month, 2)

            if pct_used >= 100:
                status = 'danger'
                status_text = 'Over Budget'
            elif pct_used >= 80:
                status = 'warning'
                status_text = 'Near Limit'
            else:
                status = 'success'
                status_text = 'On Track'

            overall_analysis = {
                'id': overall_budget_obj.id,
                'budget_amount': b_amt,
                'spent_amount': round(total_expense, 2),
                'remaining_amount': remaining,
                'percentage_used': pct_used,
                'daily_burn_rate': daily_burn,
                'projected_total': projected_month_end,
                'days_remaining': days_remaining,
                'days_passed': days_passed,
                'month_progress_pct': month_progress_pct,
                'status': status,
                'status_text': status_text
            }

        # Evaluate Category Budgets
        category_analyses = []
        for b in category_budget_objs:
            b_amt = float(b.amount)
            cat_name = b.category.name if b.category else 'Unknown'
            cat_spent = cat_expenses.get(cat_name, 0.0)
            pct_used = round((cat_spent / b_amt * 100), 1) if b_amt > 0 else 0.0
            remaining = round(b_amt - cat_spent, 2)

            if pct_used >= 100:
                status = 'danger'
                status_text = 'Exceeded'
            elif pct_used >= 80:
                status = 'warning'
                status_text = 'Warning (>80%)'
            else:
                status = 'success'
                status_text = 'Good'

            category_analyses.append({
                'id': b.id,
                'category_id': b.category_id,
                'category_name': cat_name,
                'category_color': b.category.color if b.category else '#6366f1',
                'category_icon': b.category.icon if b.category else 'bi-tag',
                'budget_amount': b_amt,
                'spent_amount': round(cat_spent, 2),
                'remaining_amount': remaining,
                'percentage_used': pct_used,
                'status': status,
                'status_text': status_text
            })

        # Generate rule-based recommendations & alerts
        suggestions = []

        if overall_analysis:
            if overall_analysis['percentage_used'] >= 100:
                over_amt = abs(overall_analysis['remaining_amount'])
                suggestions.append({
                    'type': 'budget_warning',
                    'title': 'Overall Budget Exceeded!',
                    'message': f"You have exceeded your total monthly budget by ₹{over_amt:,.2f}. Freeze non-critical spending for the remaining {days_remaining} days.",
                    'level': 'danger',
                    'badge': 'Urgent'
                })
            elif overall_analysis['percentage_used'] >= 80:
                suggestions.append({
                    'type': 'budget_warning',
                    'title': 'Budget Alert (Over 80%)',
                    'message': f"You have used {overall_analysis['percentage_used']}% of your monthly budget with {days_remaining} days remaining. Keep daily spend below ₹{max(0.0, round(overall_analysis['remaining_amount'] / max(days_remaining, 1), 2)):,.2f}/day to stay within limit.",
                    'level': 'warning',
                    'badge': 'Budget'
                })
            elif overall_analysis['projected_total'] > overall_analysis['budget_amount']:
                suggestions.append({
                    'type': 'smart_suggestion',
                    'title': 'High Spending Velocity',
                    'message': f"Current spending pace (₹{overall_analysis['daily_burn_rate']:,.2f}/day) projects a month-end total of ₹{overall_analysis['projected_total']:,.2f}, exceeding your budget of ₹{overall_analysis['budget_amount']:,.2f}.",
                    'level': 'warning',
                    'badge': 'Projection'
                })

        for cat in category_analyses:
            if cat['percentage_used'] >= 100:
                suggestions.append({
                    'type': 'budget_warning',
                    'title': f"{cat['category_name']} Budget Overrun",
                    'message': f"You have exhausted 100% of your {cat['category_name']} budget (₹{cat['spent_amount']:,.2f} / ₹{cat['budget_amount']:,.2f}).",
                    'level': 'danger',
                    'badge': 'Category Alert'
                })
            elif cat['percentage_used'] >= 80:
                suggestions.append({
                    'type': 'smart_suggestion',
                    'title': f"{cat['category_name']} Budget Nearly Full",
                    'message': f"{cat['category_name']} is at {cat['percentage_used']}% of allocated budget with ₹{cat['remaining_amount']:,.2f} remaining.",
                    'level': 'warning',
                    'badge': 'Category Warning'
                })

        # Suggest reallocation if one category is exceeded and another has plenty of room
        exceeded_cats = [c for c in category_analyses if c['percentage_used'] > 95]
        safe_cats = [c for c in category_analyses if c['percentage_used'] < 40 and c['remaining_amount'] >= 1000]
        if exceeded_cats and safe_cats:
            e = exceeded_cats[0]
            s = safe_cats[0]
            suggest_shift = min(round(s['remaining_amount'] * 0.4, 0), round(abs(e['remaining_amount']) + 500, 0))
            if suggest_shift > 0:
                suggestions.append({
                    'type': 'smart_suggestion',
                    'title': 'Smart Budget Rebalance',
                    'message': f"Consider reallocating ₹{suggest_shift:,.0f} from your under-utilized **{s['category_name']}** budget to **{e['category_name']}** to balance your spending.",
                    'level': 'info',
                    'badge': 'AI Reallocation'
                })

        # Savings goals analysis
        if savings_goals:
            for goal in savings_goals:
                if not goal.is_completed:
                    current_savings = total_income - total_expense
                    if current_savings > 0 and goal.remaining_amount > 0:
                        months_needed = round(goal.remaining_amount / current_savings, 1)
                        if months_needed <= 1:
                            suggestions.append({
                                'type': 'savings_tip',
                                'title': f"Goal in Reach: {goal.title}",
                                'message': f"You are very close! Your current monthly surplus of ₹{current_savings:,.2f} can complete your '{goal.title}' goal this month.",
                                'level': 'success',
                                'badge': 'Savings Goal'
                            })

        return {
            'current_month': current_month,
            'current_year': current_year,
            'days_passed': days_passed,
            'days_remaining': days_remaining,
            'days_in_month': days_in_month,
            'month_progress_pct': month_progress_pct,
            'overall_budget': overall_analysis,
            'category_budgets': category_analyses,
            'suggestions': suggestions
        }

