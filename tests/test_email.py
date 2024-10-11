import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from unittest import mock
from datetime import datetime

# Mock MongoDB and the send_email function
@mock.patch('app.mongoDB')
@mock.patch('app.send_email')
def test_send_vericode_success(mock_send_email, mock_mongoDB):
    # Arrange: Setup the mock behavior
    mock_send_email.return_value = 1  # Mock the send_email function to return success
    mock_mongoDB.check_user_value.return_value = True  # Mock email existence check
    
    # Test client simulates a Flask server for testing routes
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {
            "email": "dinosauryeo@gmail.com"
        }

        # Act: Send a POST request to the /send_vericode endpoint
        response = client.post('/send_vericode', json=payload)

        # Assert: Check if send_email was called with correct arguments
        mock_send_email.assert_called_once_with({
            "dinosauryeo@gmail.com": ["Verification code to reset password", mock.ANY]
        })

        # Assert: Check if input_user_data was called to store the verification code and timestamp
        mock_mongoDB.input_user_data.assert_any_call("dinosauryeo@gmail.com", "verification_code", mock.ANY)
        mock_mongoDB.input_user_data.assert_any_call("dinosauryeo@gmail.com", "vericode_date_sent", mock.ANY)

        # Assert: Verify the response
        assert response.status_code == 200  # Success response
        assert response.get_json() == {
            'status': 'success',
            'message': 'Verification code sent successfully, please use it within one minute'
        }

# Test for email not existing
@mock.patch('app.mongoDB')
@mock.patch('app.send_email')
def test_send_vericode_email_not_exists(mock_send_email, mock_mongoDB):
    # Arrange: Mock the email check to return False, meaning the email doesn't exist
    mock_mongoDB.check_user_value.return_value = False
    
    with app.test_client() as client:
        # Send the request with a non-existent email
        payload = {"email": "nonexistent@example.com"}
        response = client.post('/send_vericode', json=payload)

        # Assert that send_email wasn't called
        mock_send_email.assert_not_called()

        # Assert the response is correct
        assert response.status_code == 200
        assert response.get_json() == {
            "status": "fail",
            "message": "email doesnt exists"
        }

# Test for failed email sending
@mock.patch('app.mongoDB')
@mock.patch('app.send_email')
def test_send_vericode_email_send_failure(mock_send_email, mock_mongoDB):
    # Arrange: Mock the email existence and failed email sending
    mock_mongoDB.check_user_value.return_value = True
    mock_send_email.return_value = 0  # Simulate email sending failure
    
    with app.test_client() as client:
        # Define the test data (JSON payload)
        payload = {"email": "dinosauryeo@gmail.com"}

        # Act: Send a POST request to the /send_vericode endpoint
        response = client.post('/send_vericode', json=payload)

        # Assert: Check if send_email was called with correct arguments
        mock_send_email.assert_called_once_with({
            "dinosauryeo@gmail.com": [
                "Verification code to reset password", 
                mock.ANY  # Verification code will be random
            ]
        })

        # Assert: Failed email response
        assert response.status_code == 200
        assert response.get_json() == {
            "status": "fail",
            "message": "Failed to send email"
        }
