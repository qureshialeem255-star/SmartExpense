import pytest
from app import create_app
from config import Config
from models import db, User

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
            yield client
            db.session.remove()
            db.drop_all()

def test_register_and_login(client):
    # Register new user
    res = client.post('/register', data={
        'name': 'Test Student',
        'email': 'student@college.edu',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome to Smart Expense Management' in res.data

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200

    # Login with valid password
    res_login = client.post('/login', data={
        'email': 'student@college.edu',
        'password': 'password123'
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b'Financial Dashboard' in res.data

def test_invalid_login(client):
    # Register user first
    client.post('/register', data={
        'name': 'Test Student',
        'email': 'student@college.edu',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    client.get('/logout')

    # Attempt login with wrong password
    res = client.post('/login', data={
        'email': 'student@college.edu',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Invalid email or password' in res.data

