import pytest
from datetime import date
from app import create_app
from config import Config
from models import db, User, Category, Transaction

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

def login_user(client, email='user1@college.edu', name='User One'):
    client.post('/register', data={
        'name': name,
        'email': email,
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

def test_transaction_crud(client):
    login_user(client)

    # 1. Add Expense
    res_add = client.post('/transactions/add', data={
        'type': 'expense',
        'amount': 450.0,
        'category_id': 1,
        'description': 'Swiggy food order',
        'date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert res_add.status_code == 200
    assert b'recorded successfully' in res_add.data
    assert b'Swiggy food order' in res_add.data

    # 2. Edit Transaction
    tx = Transaction.query.first()
    assert tx is not None
    res_edit = client.post(f'/transactions/edit/{tx.id}', data={
        'type': 'expense',
        'amount': 550.0,
        'category_id': 1,
        'description': 'Swiggy dinner feast',
        'date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert res_edit.status_code == 200
    assert b'Swiggy dinner feast' in res_edit.data
    assert Transaction.query.get(tx.id).amount == 550.0

    # 3. Delete Transaction
    res_del = client.post(f'/transactions/delete/{tx.id}', follow_redirects=True)
    assert res_del.status_code == 200
    assert Transaction.query.get(tx.id) is None

def test_ai_category_prediction_api(client):
    login_user(client)

    # Test Swiggy -> Food
    res1 = client.post('/api/predict-category', json={'description': 'Swiggy order lunch', 'type': 'expense'})
    data1 = res1.get_json()
    assert data1['category_name'] == 'Food'
    assert data1['confidence'] >= 0.5

    # Test Uber -> Transport
    res2 = client.post('/api/predict-category', json={'description': 'Uber ride to campus', 'type': 'expense'})
    data2 = res2.get_json()
    assert data2['category_name'] == 'Transport'

def test_user_data_isolation(client):
    # Register User 1 and create a transaction
    login_user(client, email='alice@college.edu', name='Alice')
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': 1000.0,
        'category_id': 1,
        'description': 'Alice Secret Purchase',
        'date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    alice_tx = Transaction.query.first()

    # Logout and Register User 2 (Bob)
    client.get('/logout')
    login_user(client, email='bob@college.edu', name='Bob')

    # Bob views transactions list -> Alice's transaction must NOT be visible
    res = client.get('/transactions')
    assert b'Alice Secret Purchase' not in res.data

    # Bob attempts to edit or delete Alice's transaction -> Must be 404
    res_edit = client.get(f'/transactions/edit/{alice_tx.id}')
    assert res_edit.status_code == 404

    res_del = client.post(f'/transactions/delete/{alice_tx.id}')
    assert res_del.status_code == 404

