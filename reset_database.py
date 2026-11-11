import os
from app import create_app
from models import db, User, Category, Transaction, Budget, SavingsGoal, AIInsight

def reset_to_zero():
    app = create_app()
    with app.app_context():
        print("[*] Resetting Smart Expense Management System to 0 DATA...")
        
        # Drop all tables and recreate clean schema
        db.drop_all()
        db.create_all()
        
        # Seed only system default categories (clean starting state for any new user)
        Category.seed_default_categories(db.session)
        
        user_count = User.query.count()
        tx_count = Transaction.query.count()
        budget_count = Budget.query.count()
        goal_count = SavingsGoal.query.count()
        insight_count = AIInsight.query.count()
        
        print("--------------------------------------------------")
        print(f"Users:            {user_count} (Clean)")
        print(f"Transactions:     {tx_count} (Clean)")
        print(f"Budgets:          {budget_count} (Clean)")
        print(f"Savings Goals:    {goal_count} (Clean)")
        print(f"AI Insights:      {insight_count} (Clean)")
        print(f"Default Cats:     {Category.query.count()} (Available for new users)")
        print("--------------------------------------------------")
        print("[SUCCESS] Project database is now completely fresh with 0 user data!")

if __name__ == '__main__':
    reset_to_zero()

