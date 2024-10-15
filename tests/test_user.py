import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from app import app  # Replace with your Flask app module name
from datetime import datetime

# Fixture for the Flask test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

### Test for Register Function ###

# Test for successful registration
@patch('app.mongoDB.login')
def test_register_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate no existing user found
    mock_collection.find_one.return_value = None
    mock_mongo_login.return_value = mock_client

    # Mocking the session to include the access level (0 means admin)
    with client.session_transaction() as session:
        session['accessLevel'] = 0

    # Mocking the request data
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword'
    }

    # Make a POST request to the register endpoint
    response = client.post('/register', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure insert_one was called once with the new user data
    mock_collection.insert_one.assert_called_once_with({
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword',
        'accessLevel': "1",  # User is assigned accessLevel 1 (regular user)
        'verification_code': None,
        'vericode_date_sent': datetime(1900,1,1,0,0,0)
    })

# Test for failed registration when the user already exists
@patch('app.mongoDB.login')
def test_register_user_exists(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate existing user found
    mock_collection.find_one.return_value = {'username': 'existinguser'}
    mock_mongo_login.return_value = mock_client

    # Mocking the session to include the access level (0 means admin)
    with client.session_transaction() as session:
        session['accessLevel'] = 0

    # Mocking the request data
    data = {
        'username': 'existinguser',
        'email': 'existinguser@example.com',
        'password': 'securepassword'
    }

    # Make a POST request to the register endpoint
    response = client.post('/register', json=data)

    # Assert that the response indicates the user already exists
    assert response.status_code == 200
    assert b'Username or email already exists' in response.data

    # Ensure insert_one was not called since the user already exists
    mock_collection.insert_one.assert_not_called()

# Test for registration when access level is insufficient
def test_register_access_denied(client):
    # Mocking the session to include the access level (non-admin, access level != 0)
    with client.session_transaction() as session:
        session['accessLevel'] = 1  # Regular user

    # Mocking the request data
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword'
    }

    # Make a POST request to the register endpoint
    response = client.post('/register', json=data)

    # Assert that the response indicates that registration is not allowed
    assert response.status_code == 200
    assert b'unallowed for current access level' in response.data

### Test for Login Function ###

# Test for successful login
@patch('app.mongoDB.verify')
def test_login_success(mock_verify, client):
    # Mock verify function to return an access level (success)
    mock_verify.return_value = 1

    # Mocking the request data
    data = {
        'username': 'validuser',
        'password': 'validpassword'
    }

    # Make a POST request to the login endpoint
    response = client.post('/login', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure session variables were set correctly
    with client.session_transaction() as session:
        assert session['logged_in'] is True
        assert session['username'] == 'validuser'
        assert session['accessLevel'] == 1

# Test for failed login due to invalid credentials
@patch('app.mongoDB.verify')
def test_login_invalid_credentials(mock_verify, client):
    # Mock verify function to return False (invalid credentials)
    mock_verify.return_value = False

    # Mocking the request data
    data = {
        'username': 'invaliduser',
        'password': 'wrongpassword'
    }

    # Make a POST request to the login endpoint
    response = client.post('/login', json=data)

    # Assert that the response indicates login failure
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

    # Ensure no session variables were set
    with client.session_transaction() as session:
        assert 'logged_in' not in session

### Test for relogin Function (Password Reset) ###

# Test for successful password reset
@patch('app.mongoDB.veri_vericode')
def test_relogin_success(mock_vericode, client):
    # Mock veri_vericode to return 1 (success)
    mock_vericode.return_value = 1

    # Mocking the request data
    data = {
        'email': 'user@example.com',
        'vericode': '123456',
        'resetpassword': 'newpassword',
        'confirmpassword': 'newpassword'
    }

    # Make a POST request to the relogin (reset password) endpoint
    response = client.post('/reset_password', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure veri_vericode was called with the correct parameters
    mock_vericode.assert_called_once_with('user@example.com', '123456', 'newpassword')

# Test for password mismatch during reset
def test_relogin_password_mismatch(client):
    # Mocking the request data with mismatching passwords
    data = {
        'email': 'user@example.com',
        'vericode': '123456',
        'resetpassword': 'newpassword',
        'confirmpassword': 'differentpassword'
    }

    # Make a POST request to the relogin (reset password) endpoint
    response = client.post('/reset_password', json=data)

    # Assert that the response indicates a password mismatch
    assert response.status_code == 200
    assert b'password doesn\'t match' in response.data
