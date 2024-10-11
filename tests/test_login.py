import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from unittest import mock
from datetime import datetime
from flask import session

# Mock MongoDB
@mock.patch('app.mongoDB')
def test_login_success(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.verify.return_value = True  # Simulate a successful login
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "username": "dinosauryeo@gmail.com",
            "password": "123456"
        }

        # Act: Send a POST request to the /login endpoint
        response = client.post('/login', json=payload)

        # Assert: Check if `verify` method is called with correct arguments
        mock_mongoDB.verify.assert_called_once_with('123456', 'dinosauryeo@gmail.com')

        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'success',
            'message': 'Login successful'
        }

        # Assert: Check if the session was updated correctly
        with client.session_transaction() as sess:
            assert sess['logged_in'] == True
            assert sess['username'] == 'dinosauryeo@gmail.com'

# Mock MongoDB
@mock.patch('app.mongoDB')
def test_login_failed(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.verify.return_value = False
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "username":"dinosauryeo@gmail.com",
            "password":"123456"
        }

        # Act: Send a POST request to the /login endpoint
        response = client.post('/login', json=payload)

        # Assert: Check if verify is called with the correct statement
        mock_mongoDB.verify.assert_called_once_with("123456",'dinosauryeo@gmail.com')


        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "Invalid username or password"
        }

# Mock MongoDB
@mock.patch('app.mongoDB')
def test_login_empty(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.verify.return_value = False
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "username": "",
            "password":""
        }

        # Act: Send a POST request to the /login endpoint
        response = client.post('/login', json=payload)

        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "Username and password are required"
        }
        

# Mock MongoDB
@mock.patch('app.mongoDB')
def test_relogin_expired(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.veri_vericode.return_value = 3
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email":"dinosauryeo@gmail.com",
            "vericode":"anything",
            "resetpassword":"reset",
            "confirmpassword":"reset"
        }

        # Act: Send a POST request to the /reset_password endpoint
        response = client.post('/reset_password', json=payload)
        
        mock_mongoDB.veri_vericode.assert_called_once_with("dinosauryeo@gmail.com","anything","reset")
        
        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "vericode expired"
        }
        
# Mock MongoDB
@mock.patch('app.mongoDB')
def test_relogin_wrongvericode(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.veri_vericode.return_value = 2
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email":"dinosauryeo@gmail.com",
            "vericode":"anything",
            "resetpassword":"reset",
            "confirmpassword":"reset"
        }

        # Act: Send a POST request to the /reset_password endpoint
        response = client.post('/reset_password', json=payload)
        
        mock_mongoDB.veri_vericode.assert_called_once_with("dinosauryeo@gmail.com","anything","reset")
        
        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "vericode doesn't match"
        }
        
# Mock MongoDB
@mock.patch('app.mongoDB')
def test_relogin_mismatch(mock_mongoDB):
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email":"dinosauryeo@gmail.com",
            "vericode":"anything",
            "resetpassword":"reset",
            "confirmpassword":"reset1"
        }

        # Act: Send a POST request to the /reset_password endpoint
        response = client.post('/reset_password', json=payload)
        
        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "password doesn't match"
        }
        
        
# Mock MongoDB
@mock.patch('app.mongoDB')
def test_relogin_success(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.veri_vericode.return_value = 1
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email":"dinosauryeo@gmail.com",
            "vericode":"anything",
            "resetpassword":"reset",
            "confirmpassword":"reset"
        }

        # Act: Send a POST request to the /reset_password endpoint
        response = client.post('/reset_password', json=payload)
        
        mock_mongoDB.veri_vericode.assert_called_once_with("dinosauryeo@gmail.com","anything","reset")
        
        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'success',
            'message': "success"
        }
        
        
        
# Mock MongoDB
@mock.patch('app.mongoDB')
def test_relogin_missing(mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_mongoDB.veri_vericode.return_value = 1
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email":"dinosauryeo@gmail.com",
            "vericode":"",
            "resetpassword":"reset",
            "confirmpassword":"reset"
        }
        
        response = client.post('/reset_password',json=payload)
        
        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'fail',
            'message': "please enter all field"
        }