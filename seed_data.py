from datetime import date, timedelta
import random
from app import create_app
from models import db, User, Category, Transaction, Budget, SavingsGoal, AIInsight
from services.expense_analyzer import ExpenseAnalyzer
from services.budget_analyzer import BudgetAnalyzer
from services.expense_predictor import ExpensePredictor

def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Seeding database with realistic demonstration data...")

        # Ensure default categories exist
        Category.seed_default_categories(db.session)

        # Retrieve categories map
        cat_map = {c.name: c for c in Category.query.all()}

        # 1. Create or update Demo User
        demo_email = 'demo@example.com'
        demo_user = User.query.filter_by(email=demo_email).first()
        if not demo_user:
            demo_user = User(
                name='Alex Morgan',
                email=demo_email
            )
            demo_user.set_password('password123')
            db.session.add(demo_user)
            db.session.commit()
            print(f"[OK] Created demo user: {demo_email} (password: password123)")
        else:
            print(f"[INFO] Demo user {demo_email} already exists.")

        # Clean old demo transactions, budgets, goals to allow clean re-seed
        Transaction.query.filter_by(user_id=demo_user.id).delete()
        Budget.query.filter_by(user_id=demo_user.id).delete()
        SavingsGoal.query.filter_by(user_id=demo_user.id).delete()
        AIInsight.query.filter_by(user_id=demo_user.id).delete()
        db.session.commit()

        today = date.today()

        # 2. Add realistic transactions across the past 4 months (Aug, Sep, Oct, Nov)
        transactions_data = [
            # 3 Months Ago
            {'date': today - timedelta(days=105), 'type': 'income', 'cat': 'Salary', 'desc': 'Monthly Corporate Salary', 'amt': 48000.0},
            {'date': today - timedelta(days=102), 'type': 'expense', 'cat': 'Bills', 'desc': 'House Rent & Maintenance', 'amt': 12000.0},
            {'date': today - timedelta(days=98), 'type': 'expense', 'cat': 'Food', 'desc': 'Supermarket monthly groceries', 'amt': 4200.0},
            {'date': today - timedelta(days=95), 'type': 'expense', 'cat': 'Bills', 'desc': 'Electricity Bill payment', 'amt': 1850.0},
            {'date': today - timedelta(days=94), 'type': 'expense', 'cat': 'Bills', 'desc': 'Airtel Broadband Internet', 'amt': 999.0},
            {'date': today - timedelta(days=92), 'type': 'expense', 'cat': 'Transport', 'desc': 'Fuel petrol fillup', 'amt': 2200.0},
            {'date': today - timedelta(days=88), 'type': 'expense', 'cat': 'Food', 'desc': 'Swiggy dinner order', 'amt': 540.0},
            {'date': today - timedelta(days=85), 'type': 'expense', 'cat': 'Entertainment', 'desc': 'Netflix & Spotify subscriptions', 'amt': 799.0},
            {'date': today - timedelta(days=80), 'type': 'expense', 'cat': 'Shopping', 'desc': 'Amazon apparel and sneakers', 'amt': 3450.0},

            # 2 Months Ago
            {'date': today - timedelta(days=75), 'type': 'income', 'cat': 'Salary', 'desc': 'Monthly Corporate Salary', 'amt': 48000.0},
            {'date': today - timedelta(days=72), 'type': 'income', 'cat': 'Freelancing', 'desc': 'Web design client project payment', 'amt': 15000.0},
            {'date': today - timedelta(days=71), 'type': 'expense', 'cat': 'Bills', 'desc': 'House Rent & Maintenance', 'amt': 12000.0},
            {'date': today - timedelta(days=68), 'type': 'expense', 'cat': 'Food', 'desc': 'BigBasket Grocery replenishment', 'amt': 4800.0},
            {'date': today - timedelta(days=65), 'type': 'expense', 'cat': 'Transport', 'desc': 'Uber rides to college & campus', 'amt': 1450.0},
            {'date': today - timedelta(days=62), 'type': 'expense', 'cat': 'Education', 'desc': 'Data Science textbook & Coursera certificate', 'amt': 2400.0},
            {'date': today - timedelta(days=58), 'type': 'expense', 'cat': 'Food', 'desc': 'Zomato weekend family dinner', 'amt': 1850.0},
            {'date': today - timedelta(days=55), 'type': 'expense', 'cat': 'Entertainment', 'desc': 'PVR IMAX movie night & popcorn', 'amt': 1200.0},
            {'date': today - timedelta(days=50), 'type': 'expense', 'cat': 'Healthcare', 'desc': 'Pharmacy medications & vitamins', 'amt': 950.0},

            # 1 Month Ago (Last Month)
            {'date': today - timedelta(days=42), 'type': 'income', 'cat': 'Salary', 'desc': 'Monthly Corporate Salary', 'amt': 48000.0},
            {'date': today - timedelta(days=40), 'type': 'expense', 'cat': 'Bills', 'desc': 'House Rent & Maintenance', 'amt': 12000.0},
            {'date': today - timedelta(days=38), 'type': 'expense', 'cat': 'Food', 'desc': 'Grocery store restocking', 'amt': 5100.0},
            {'date': today - timedelta(days=35), 'type': 'expense', 'cat': 'Bills', 'desc': 'Electricity Bill payment', 'amt': 2100.0},
            {'date': today - timedelta(days=33), 'type': 'expense', 'cat': 'Shopping', 'desc': 'Festive shopping clothes on Myntra', 'amt': 6200.0},
            {'date': today - timedelta(days=30), 'type': 'expense', 'cat': 'Transport', 'desc': 'Car servicing and fuel', 'amt': 3800.0},
            {'date': today - timedelta(days=28), 'type': 'expense', 'cat': 'Food', 'desc': 'Swiggy team lunch order', 'amt': 1450.0},
            {'date': today - timedelta(days=25), 'type': 'expense', 'cat': 'Entertainment', 'desc': 'Gaming accessories Steam sale', 'amt': 1899.0},
            {'date': today - timedelta(days=22), 'type': 'expense', 'cat': 'Healthcare', 'desc': 'Dental consultation checkup', 'amt': 1500.0},

            # Current Month (This Month)
            {'date': today - timedelta(days=9), 'type': 'income', 'cat': 'Salary', 'desc': 'Monthly Corporate Salary', 'amt': 48000.0},
            {'date': today - timedelta(days=8), 'type': 'expense', 'cat': 'Bills', 'desc': 'House Rent & Maintenance', 'amt': 12000.0},
            {'date': today - timedelta(days=7), 'type': 'expense', 'cat': 'Food', 'desc': 'Monthly grocery store supplies', 'amt': 4600.0},
            {'date': today - timedelta(days=6), 'type': 'expense', 'cat': 'Bills', 'desc': 'Wifi Broadband recharge', 'amt': 999.0},
            {'date': today - timedelta(days=5), 'type': 'expense', 'cat': 'Transport', 'desc': 'Fuel petrol pump', 'amt': 2400.0},
            {'date': today - timedelta(days=4), 'type': 'expense', 'cat': 'Food', 'desc': 'Swiggy dinner order', 'amt': 620.0},
            {'date': today - timedelta(days=3), 'type': 'expense', 'cat': 'Food', 'desc': 'Cafe coffee & snacks with friends', 'amt': 480.0},
            {'date': today - timedelta(days=2), 'type': 'expense', 'cat': 'Shopping', 'desc': 'Amazon electronics USB-C hub', 'amt': 1850.0},
            {'date': today - timedelta(days=1), 'type': 'expense', 'cat': 'Food', 'desc': 'Zomato food delivery pizza', 'amt': 750.0},
            {'date': today, 'type': 'expense', 'cat': 'Transport', 'desc': 'Uber ride to college presentation', 'amt': 340.0}
        ]

        for item in transactions_data:
            cat = cat_map.get(item['cat'])
            if cat:
                tx = Transaction(
                    user_id=demo_user.id,
                    category_id=cat.id,
                    type=item['type'],
                    amount=item['amt'],
                    description=item['desc'],
                    date=item['date']
                )
                db.session.add(tx)

        # 3. Create Monthly Budgets for Demo User
        b_month = today.month
        b_year = today.year

        # Overall budget: ₹32,000
        db.session.add(Budget(user_id=demo_user.id, category_id=None, amount=32000.0, month=b_month, year=b_year))

        # Category budgets
        if 'Food' in cat_map:
            db.session.add(Budget(user_id=demo_user.id, category_id=cat_map['Food'].id, amount=8500.0, month=b_month, year=b_year))
        if 'Shopping' in cat_map:
            db.session.add(Budget(user_id=demo_user.id, category_id=cat_map['Shopping'].id, amount=4000.0, month=b_month, year=b_year))
        if 'Transport' in cat_map:
            db.session.add(Budget(user_id=demo_user.id, category_id=cat_map['Transport'].id, amount=3500.0, month=b_month, year=b_year))
        if 'Bills' in cat_map:
            db.session.add(Budget(user_id=demo_user.id, category_id=cat_map['Bills'].id, amount=15000.0, month=b_month, year=b_year))

        # 4. Create Savings Goals
        db.session.add(SavingsGoal(
            user_id=demo_user.id,
            title='Emergency Fund',
            target_amount=60000.0,
            current_amount=42000.0,
            deadline=today + timedelta(days=90)
        ))
        db.session.add(SavingsGoal(
            user_id=demo_user.id,
            title='MacBook Pro / New Laptop',
            target_amount=95000.0,
            current_amount=68000.0,
            deadline=today + timedelta(days=150)
        ))
        db.session.add(SavingsGoal(
            user_id=demo_user.id,
            title='Vacation Trip',
            target_amount=25000.0,
            current_amount=18500.0,
            deadline=today + timedelta(days=60)
        ))

        db.session.commit()

        # 5. Generate and store initial AI Insights
        all_txs = Transaction.query.filter_by(user_id=demo_user.id).all()
        user_budgets = Budget.query.filter_by(user_id=demo_user.id).all()
        user_savings = SavingsGoal.query.filter_by(user_id=demo_user.id).all()

        spending_summary = ExpenseAnalyzer.analyze_spending(all_txs, today)
        budget_summary = BudgetAnalyzer.analyze_budgets(user_budgets, all_txs, user_savings, today)
        prediction = ExpensePredictor.predict_next_month(all_txs, today)

        for ins in spending_summary.get('insights', []):
            db.session.add(AIInsight(user_id=demo_user.id, insight_type=ins['type'], message=ins['message']))

        for sug in budget_summary.get('suggestions', []):
            db.session.add(AIInsight(user_id=demo_user.id, insight_type=sug['type'], message=sug['message']))

        if prediction.get('has_sufficient_data'):
            pred_msg = f"Upcoming Month Forecast: Estimated ₹{prediction['predicted_total']:,.2f} for {prediction['next_month_label']} ({prediction['trend_direction']} trend via {prediction['method']})."
            db.session.add(AIInsight(user_id=demo_user.id, insight_type='prediction', message=pred_msg))

        db.session.commit()
        print("[SUCCESS] Database seeded successfully with transactions, budgets, savings goals, and AI insights!")

if __name__ == '__main__':
    seed_database()
