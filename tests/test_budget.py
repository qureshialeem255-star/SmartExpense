import pytest
from datetime import date
from app import create_app
from config import Config
from models import db, User, Category, Transaction, Budget, SavingsGoal

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            Category.seed_default_categories(db.session)
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client):
    client.post('/register', data={
        'name': 'Budget Master',
        'email': 'budget@college.edu',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

def test_budget_creation_and_alert(client):
    login_user(client)
    today = date.today()

    # 1. Set overall monthly budget to ₹5,000
    res_b = client.post('/budgets', data={
        'category_id': 0,  # 0 indicates Overall
        'amount': 5000.0,
        'month': today.month,
        'year': today.year
    }, follow_redirects=True)
    assert res_b.status_code == 200
    assert b'5,000.00' in res_b.data

    # 2. Add expense of ₹6,000 (exceeding budget)
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': 6000.0,
        'category_id': 1,
        'description': 'Laptop Repair Exceeded',
        'date': today.strftime('%Y-%m-%d')
    }, follow_redirects=True)

    # 3. View Budgets page -> should display Over Budget alert
    res_alert = client.get(f'/budgets?month={today.month}&year={today.year}')
    assert res_alert.status_code == 200
    assert b'Overall Budget Exceeded' in res_alert.data or b'OVER BUDGET' in res_alert.data

def test_savings_goals(client):
    login_user(client)

    # Create savings goal
    res_g = client.post('/savings', data={
        'title': 'College Trip',
        'target_amount': 10000.0,
        'current_amount': 2000.0,
        'deadline': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert res_g.status_code == 200
    assert b'College Trip' in res_g.data

    goal = SavingsGoal.query.first()
    assert goal is not None
    assert goal.progress_percentage == 20.0

    # Deposit funds to goal
    res_fund = client.post(f'/savings/add-funds/{goal.id}', data={
        'deposit_amount': 3000.0
    }, follow_redirects=True)
    assert res_fund.status_code == 200
    assert SavingsGoal.query.get(goal.id).current_amount == 5000.0
    assert SavingsGoal.query.get(goal.id).progress_percentage == 50.0

def test_ai_insights_refresh(client):
    login_user(client)
    today = date.today()

    # Add income and expense
    client.post('/transactions/add', data={
        'type': 'income',
        'amount': 50000.0,
        'category_id': 9,
        'description': 'Tech Company Salary',
        'date': today.strftime('%Y-%m-%d')
    })
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': 8000.0,
        'category_id': 1,
        'description': 'Swiggy and Dineout Food',
        'date': today.strftime('%Y-%m-%d')
    })

    # Trigger AI insights refresh
    res_refresh = client.post('/insights/refresh', follow_redirects=True)
    assert res_refresh.status_code == 200
    assert b'AI Analytics refreshed successfully' in res_refresh.data

    # View Insights page
    res_page = client.get('/insights')
    assert res_page.status_code == 200
    assert 'Financial Health Index' in res_page.get_data(as_text=True)

