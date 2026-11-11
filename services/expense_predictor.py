from datetime import date
from collections import defaultdict
import numpy as np

class ExpensePredictor:
    """
    Predicts upcoming monthly expenses using historical transaction data
    via Linear Regression and Weighted Rolling Moving Averages.
    """

    MONTH_NAMES = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    @classmethod
    def predict_next_month(cls, transactions, target_date=None):
        """
        Analyzes historical monthly expense totals and forecasts next month's spending.
        """
        if target_date is None:
            target_date = date.today()

        current_month = target_date.month
        current_year = target_date.year

        # Next month calculation
        next_month = 1 if current_month == 12 else current_month + 1
        next_year = current_year + 1 if current_month == 12 else current_year
        next_month_label = f"{cls.MONTH_NAMES[next_month]} {next_year}"

        # Group expenses by (year, month) and by category
        monthly_totals = defaultdict(float)
        monthly_cat_totals = defaultdict(lambda: defaultdict(float))

        for tx in transactions:
            if tx.type == 'expense':
                key = (tx.date.year, tx.date.month)
                monthly_totals[key] += float(tx.amount)
                cat_name = tx.category.name if tx.category else 'Other'
                monthly_cat_totals[key][cat_name] += float(tx.amount)

        # Sort months chronologically
        sorted_keys = sorted(monthly_totals.keys())

        # If no history or very little history
        if not sorted_keys:
            return {
                'has_sufficient_data': False,
                'predicted_total': 0.0,
                'trend_direction': 'Insufficient Data',
                'trend_percent': 0.0,
                'method': 'Default Baseline',
                'next_month_label': next_month_label,
                'history': [],
                'category_predictions': [],
                'explanation': 'Not enough transaction history to build an AI forecast. Please record at least 1 month of expenses.'
            }

        history = []
        for (y, m) in sorted_keys:
            history.append({
                'year': y,
                'month': m,
                'label': f"{cls.MONTH_NAMES[m][:3]} {y}",
                'amount': round(monthly_totals[(y, m)], 2)
            })

        amounts = [monthly_totals[k] for k in sorted_keys]

        # Use Linear Regression if we have 3 or more months, else weighted average
        if len(amounts) >= 3:
            x = np.arange(len(amounts)).reshape(-1, 1)
            y = np.array(amounts)
            
            # Simple linear regression: y = mx + c
            # Using numpy polyfit for robustness
            m_slope, c_intercept = np.polyfit(x.flatten(), y, 1)
            next_x = len(amounts)
            predicted_val = float(m_slope * next_x + c_intercept)

            # Prevent negative or unreasonable predictions
            recent_avg = float(np.mean(amounts[-3:]))
            if predicted_val < 0.3 * recent_avg:
                predicted_val = recent_avg

            method = 'Linear Trend Regression'
            trend_slope = float(m_slope)
            if trend_slope > 200:
                trend_direction = 'Increasing'
            elif trend_slope < -200:
                trend_direction = 'Decreasing'
            else:
                trend_direction = 'Stable'

            last_amount = amounts[-1]
            trend_percent = round(((predicted_val - last_amount) / last_amount * 100), 1) if last_amount > 0 else 0.0

        elif len(amounts) == 2:
            # Weighted average: 60% latest month, 40% previous month
            predicted_val = float(0.6 * amounts[1] + 0.4 * amounts[0])
            method = 'Weighted Rolling Average (2-month)'
            diff = amounts[1] - amounts[0]
            trend_direction = 'Increasing' if diff > 100 else ('Decreasing' if diff < -100 else 'Stable')
            trend_percent = round((diff / amounts[0] * 100), 1) if amounts[0] > 0 else 0.0
        else:
            # Single month
            predicted_val = float(amounts[0])
            method = 'Baseline Estimate (1-month)'
            trend_direction = 'Baseline'
            trend_percent = 0.0

        predicted_total = max(round(predicted_val, 2), 0.0)

        # Estimate category breakdown based on recent 3 months category proportions
        recent_keys = sorted_keys[-3:]
        cat_sums = defaultdict(float)
        total_recent = 0.0
        for k in recent_keys:
            for cat, amt in monthly_cat_totals[k].items():
                cat_sums[cat] += amt
                total_recent += amt

        category_predictions = []
        if total_recent > 0:
            for cat, amt in sorted(cat_sums.items(), key=lambda item: item[1], reverse=True):
                share = amt / total_recent
                pred_cat_amount = round(predicted_total * share, 2)
                category_predictions.append({
                    'category': cat,
                    'predicted_amount': pred_cat_amount,
                    'percentage': round(share * 100, 1)
                })

        explanation = (
            f"Based on your past {len(amounts)} month(s) of expense patterns, our AI model estimates you will spend "
            f"approximately ₹{predicted_total:,.2f} in {next_month_label}. "
            f"Spending trend is **{trend_direction}** ({trend_percent:+.1f}% vs current month)."
        )

        return {
            'has_sufficient_data': True,
            'predicted_total': predicted_total,
            'trend_direction': trend_direction,
            'trend_percent': trend_percent,
            'method': method,
            'next_month_label': next_month_label,
            'history': history,
            'category_predictions': category_predictions,
            'explanation': explanation
        }

