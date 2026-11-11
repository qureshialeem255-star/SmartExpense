from datetime import date, datetime
from collections import defaultdict
import numpy as np

class ExpenseAnalyzer:
    """
    Analyzes historical spending patterns, category breakdowns,
    month-over-month variances, and detects anomalous spikes.
    """

    @staticmethod
    def analyze_spending(transactions, target_date=None):
        """
        Analyzes transactions up to target_date (defaults to current date).
        Returns a rich summary of metrics, breakdowns, comparisons, and generated insights.
        """
        if target_date is None:
            target_date = date.today()

        current_month = target_date.month
        current_year = target_date.year

        prev_month = 12 if current_month == 1 else current_month - 1
        prev_year = current_year - 1 if current_month == 1 else current_year

        # Aggregate current month and previous month data
        current_expenses_by_cat = defaultdict(float)
        prev_expenses_by_cat = defaultdict(float)
        current_income = 0.0
        current_expenses = 0.0
        prev_expenses = 0.0
        prev_income = 0.0

        current_month_txs = []

        for tx in transactions:
            tx_amount = float(tx.amount)
            cat_name = tx.category.name if tx.category else 'Other'

            if tx.date.year == current_year and tx.date.month == current_month:
                if tx.type == 'expense':
                    current_expenses += tx_amount
                    current_expenses_by_cat[cat_name] += tx_amount
                    current_month_txs.append(tx)
                else:
                    current_income += tx_amount
            elif tx.date.year == prev_year and tx.date.month == prev_month:
                if tx.type == 'expense':
                    prev_expenses += tx_amount
                    prev_expenses_by_cat[cat_name] += tx_amount
                else:
                    prev_income += tx_amount

        # Calculate metrics
        net_savings = current_income - current_expenses
        savings_rate = round((net_savings / current_income * 100), 1) if current_income > 0 else 0.0

        # Find top spending category
        top_category = None
        top_category_amount = 0.0
        top_category_pct = 0.0

        if current_expenses_by_cat:
            top_category = max(current_expenses_by_cat, key=current_expenses_by_cat.get)
            top_category_amount = round(current_expenses_by_cat[top_category], 2)
            top_category_pct = round((top_category_amount / current_expenses * 100), 1) if current_expenses > 0 else 0.0

        # Month-over-month total expense change
        mom_change_amount = round(current_expenses - prev_expenses, 2)
        mom_change_pct = round(((current_expenses - prev_expenses) / prev_expenses * 100), 1) if prev_expenses > 0 else 0.0

        # Category variances
        category_changes = []
        for cat, curr_amt in current_expenses_by_cat.items():
            prev_amt = prev_expenses_by_cat.get(cat, 0.0)
            if prev_amt > 0:
                pct = round(((curr_amt - prev_amt) / prev_amt * 100), 1)
            else:
                pct = 100.0 if curr_amt > 0 else 0.0
            category_changes.append({
                'category': cat,
                'current': round(curr_amt, 2),
                'previous': round(prev_amt, 2),
                'change_pct': pct
            })

        # Sort category changes by current spending descending
        category_changes.sort(key=lambda x: x['current'], reverse=True)

        # Detect unusual single transaction spikes in current month
        unusual_transactions = []
        if len(current_month_txs) >= 3:
            amounts = [tx.amount for tx in current_month_txs]
            mean_amt = float(np.mean(amounts))
            std_amt = float(np.std(amounts))
            threshold = mean_amt + (1.5 * std_amt) if std_amt > 0 else mean_amt * 2.0

            for tx in current_month_txs:
                if tx.amount > threshold and tx.amount >= 1000:
                    unusual_transactions.append({
                        'id': tx.id,
                        'description': tx.description,
                        'amount': round(tx.amount, 2),
                        'category': tx.category.name if tx.category else 'Other',
                        'date': tx.date.strftime('%d %b %Y'),
                        'reason': f"High expense: ₹{tx.amount:,.2f} is significantly above your monthly transaction average (₹{mean_amt:,.2f})"
                    })

        # Generate rule-based natural language insights
        insights = []

        if top_category and current_expenses > 0:
            insights.append({
                'type': 'spending_analysis',
                'title': 'Highest Spending Category',
                'message': f"Your highest spending category this month is **{top_category}** (₹{top_category_amount:,.2f}), accounting for **{top_category_pct}%** of your total expenses.",
                'badge': 'Analysis',
                'level': 'info'
            })

            # Check if top category increased
            prev_top = prev_expenses_by_cat.get(top_category, 0.0)
            if prev_top > 0:
                top_diff = round(((top_category_amount - prev_top) / prev_top * 100), 1)
                if top_diff > 15:
                    insights.append({
                        'type': 'category_spike',
                        'title': f'{top_category} Spending Spike',
                        'message': f"{top_category} spending is up by **{top_diff}%** compared with last month (₹{top_category_amount:,.2f} vs ₹{prev_top:,.2f}). Review your recent {top_category.lower()} purchases.",
                        'badge': 'Warning',
                        'level': 'warning'
                    })
                elif top_diff < -10:
                    insights.append({
                        'type': 'savings_tip',
                        'title': f'Great {top_category} Discipline',
                        'message': f"You reduced {top_category} spending by **{abs(top_diff)}%** compared to last month! Keep up the good work.",
                        'badge': 'Positive',
                        'level': 'success'
                    })

        # Savings rate insights
        if current_income > 0:
            if savings_rate >= 30:
                insights.append({
                    'type': 'savings_tip',
                    'title': 'Healthy Savings Rate',
                    'message': f"Excellent financial health! You are saving **{savings_rate}%** of your income this month (₹{net_savings:,.2f} saved).",
                    'badge': 'Savings',
                    'level': 'success'
                })
            elif savings_rate < 10 and savings_rate >= 0:
                insights.append({
                    'type': 'savings_tip',
                    'title': 'Low Savings Warning',
                    'message': f"Your current savings rate is only **{savings_rate}%** (₹{net_savings:,.2f}). Try cutting non-essential shopping or entertainment to reach the recommended 20% savings threshold.",
                    'badge': 'Alert',
                    'level': 'warning'
                })
            elif savings_rate < 0:
                insights.append({
                    'type': 'budget_warning',
                    'title': 'Expenses Exceed Income',
                    'message': f"Deficit alert: Your monthly expenses (₹{current_expenses:,.2f}) exceed your income (₹{current_income:,.2f}) by ₹{abs(net_savings):,.2f}.",
                    'badge': 'Danger',
                    'level': 'danger'
                })

        # Month-over-month trend
        if prev_expenses > 0:
            if mom_change_pct > 20:
                insights.append({
                    'type': 'spending_analysis',
                    'title': 'Total Spending Surged',
                    'message': f"Your overall monthly expenditure increased by **{mom_change_pct}%** (₹{mom_change_amount:+,.2f}) compared with last month.",
                    'badge': 'Trend',
                    'level': 'warning'
                })
            elif mom_change_pct < -15:
                insights.append({
                    'type': 'savings_tip',
                    'title': 'Spending Controlled',
                    'message': f"Overall expenses dropped by **{abs(mom_change_pct)}%** compared to last month. Good job controlling outflows!",
                    'badge': 'Trend',
                    'level': 'success'
                })

        # Add unusual spikes to insights
        for spike in unusual_transactions[:2]:
            insights.append({
                'type': 'category_spike',
                'title': f'Unusual Purchase: {spike["description"]}',
                'message': spike['reason'],
                'badge': 'Unusual',
                'level': 'warning'
            })

        return {
            'current_month': current_month,
            'current_year': current_year,
            'current_income': round(current_income, 2),
            'current_expenses': round(current_expenses, 2),
            'net_savings': round(net_savings, 2),
            'savings_rate': savings_rate,
            'prev_expenses': round(prev_expenses, 2),
            'mom_change_amount': mom_change_amount,
            'mom_change_pct': mom_change_pct,
            'top_category': top_category,
            'top_category_amount': top_category_amount,
            'top_category_pct': top_category_pct,
            'current_expenses_by_cat': dict(current_expenses_by_cat),
            'category_changes': category_changes,
            'unusual_transactions': unusual_transactions,
            'insights': insights
        }

