import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock, mock_open, ANY
from flask import Flask
from app import app  # Replace 'app' with your Flask app module name

# Test client setup
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mocking MongoClient to prevent actual database interaction
@pytest.fixture
def mock_mongo_client():
    with patch('app.MongoClient') as mock_client:
        yield mock_client

# Mocking os functions to prevent actual file system interaction
@pytest.fixture
def mock_os():
    with patch('app.os.makedirs') as mock_makedirs, \
         patch('app.os.path.exists') as mock_exists, \
         patch('app.os.remove') as mock_remove, \
         patch('app.os.path.join') as mock_path_join, \
         patch('app.os.getcwd') as mock_getcwd:
        mock_exists.return_value = True  # Assume paths exist
        mock_getcwd.return_value = '/fake/dir'
        mock_path_join.side_effect = lambda *args: '/'.join(args)  # Simple join
        yield {
            'makedirs': mock_makedirs,
            'exists': mock_exists,
            'remove': mock_remove,
            'path_join': mock_path_join,
            'getcwd': mock_getcwd,
        }

# Mocking email sending functions
@pytest.fixture
def mock_smtp():
    with patch('app.smtplib.SMTP') as mock_smtp:
        yield mock_smtp

# Mocking open function
@pytest.fixture
def mock_open_file():
    with patch('builtins.open', mock_open()) as mock_file:
        yield mock_file

# Mocking pandas ExcelWriter
@pytest.fixture
def mock_excel_writer():
    with patch('app.pd.ExcelWriter') as mock_writer:
        yield mock_writer

# Mocking pandas read_csv
@pytest.fixture
def mock_read_csv():
    with patch('app.pd.read_csv') as mock_read_csv:
        mock_read_csv.return_value = MagicMock()
        yield mock_read_csv

# Mocking csv module functions
@pytest.fixture
def mock_csv():
    with patch('app.csv.DictWriter') as mock_csv_writer:
        yield mock_csv_writer

# Test functions

@patch('app.download_all')
@patch('app.send_email')
def test_export_all_student_timetable_success(mock_send_email, mock_download_all, client, mock_os, mock_mongo_client):
    # Mock download_all to return True (success)
    mock_download_all.return_value = True
    # Mock send_email to return True (email sent successfully)
    mock_send_email.return_value = True

    response = client.get('/export-all-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science'
    })

    # Asserts to validate the behavior
    assert response.status_code == 200
    assert b"Timetable exported successfully" in response.data

    # Ensure download_all was called with the correct parameters
    mock_download_all.assert_called_with('2024', '1', 'Melbourne', 'Prefix', 'Computer Science')

@patch('app.download_all')
def test_export_all_student_timetable_fail(mock_download_all, client, mock_os, mock_mongo_client):
    # Mock download_all to return False (failure)
    mock_download_all.return_value = False

    response = client.get('/export-all-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science'
    })

    assert response.status_code == 500
    assert b"Failed to export timetable" in response.data

    # Ensure download_all was called with the correct parameters
    mock_download_all.assert_called_with('2024', '1', 'Melbourne', 'Prefix', 'Computer Science')

# Testing send_vericode function
@patch('app.mongoDB.check_user_value')
@patch('app.mongoDB.input_user_data')
@patch('app.send_email')
def test_send_vericode_success(mock_send_email, mock_input_user_data, mock_check_user_value, client):
    # Mock the MongoDB email check to return True (email exists)
    mock_check_user_value.return_value = True
    # Mock send_email to return True (email sent successfully)
    mock_send_email.return_value = 1

    data = {
        'email': 'student@example.com'
    }

    response = client.post('/send_vericode', json=data)

    assert b'"success"' in response.data
    assert b"Verification code sent successfully" in response.data

    # Ensure send_email was called with the correct arguments
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    email_list = args[0]
    assert email_list[0] == 'student@example.com'
    assert 'Verification code to reset password' in email_list[1]

    # Ensure the verification code was stored in the database
    mock_input_user_data.assert_any_call('student@example.com', 'verification_code', ANY)
    mock_input_user_data.assert_any_call('student@example.com', 'vericode_date_sent', ANY)

@patch('app.mongoDB.check_user_value')
def test_send_vericode_email_not_exist(mock_check_user_value, client):
    # Mock the MongoDB email check to return False (email doesn't exist)
    mock_check_user_value.return_value = False

    data = {
        'email': 'nonexistent@example.com'
    }

    response = client.post('/send_vericode', json=data)

    assert b'"fail"' in response.data
    assert b"email doesnt exists" in response.data

    # Ensure check_user_value was called with the correct email
    mock_check_user_value.assert_called_once_with("email", "nonexistent@example.com")

@patch('app.mongoDB.check_user_value')
@patch('app.send_email')
def test_send_vericode_fail_sending_email(mock_send_email, mock_check_user_value, client):
    # Mock the MongoDB email check to return True (email exists)
    mock_check_user_value.return_value = True
    # Mock send_email to return False (email sending failed)
    mock_send_email.return_value = False

    data = {
        'email': 'student@example.com'
    }

    response = client.post('/send_vericode', json=data)

    assert b'"fail"' in response.data
    assert b"Failed to send email" in response.data

    # Ensure send_email was called correctly
    mock_send_email.assert_called_once()

@patch('app.download_one')
@patch('app.send_email')
def test_export_one_student_timetable_success(mock_send_email, mock_download_one, client, mock_os, mock_open_file):
    # Mock download_one to return the email address
    mock_download_one.return_value = "student@example.com"
    # Mock send_email to return True (email sent successfully)
    mock_send_email.return_value = True

    response = client.get('/export-one-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science',
        'student_id': '12345'
    })

    assert response.status_code == 200
    assert b"successful sent timetable" in response.data

    # Verify that os.remove was called to "delete" the files
    student_id = '12345'
    expected_file_path = f'student_timetable/{student_id}_timetable.xlsx'
    expected_csv_path = f'student_timetable/{student_id}_timetable.csv'

    mock_os['remove'].assert_any_call(expected_file_path)
    mock_os['remove'].assert_any_call(expected_csv_path)

    # Ensure download_one was called with the correct parameters
    mock_download_one.assert_called_with('2024', '1', 'Melbourne', 'Prefix', 'Computer Science', 12345)

@patch('app.download_one')
def test_export_one_student_timetable_invalid_id(mock_download_one, client):
    # No need to mock download_one since it won't be called due to invalid ID
    response = client.get('/export-one-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science',
        'student_id': 'invalid_id'
    })

    assert response.status_code == 400
    assert b"Invalid student ID format" in response.data

@patch('app.download_one')
def test_export_one_student_timetable_fail_download(mock_download_one, client):
    # Mock download_one to return False (failure)
    mock_download_one.return_value = False

    response = client.get('/export-one-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science',
        'student_id': '12345'
    })

    assert response.status_code == 500
    assert b"Failed to export timetable" in response.data

    # Ensure download_one was called with the correct parameters
    mock_download_one.assert_called_with('2024', '1', 'Melbourne', 'Prefix', 'Computer Science', 12345)

@patch('app.download_one')
@patch('app.send_email')
def test_export_one_student_timetable_fail_send_email(mock_send_email, mock_download_one, client, mock_os, mock_open_file):
    # Mock download_one to return the email address
    mock_download_one.return_value = "student@example.com"
    # Mock send_email to return False (email sending failed)
    mock_send_email.return_value = False

    response = client.get('/export-one-student-timetable', query_string={
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'folder_prefix': 'Prefix',
        'degree_name': 'Computer Science',
        'student_id': '12345'
    })

    assert response.status_code == 500
    assert b"failed to send" in response.data

    # Ensure download_one was called with the correct parameters
    mock_download_one.assert_called_with('2024', '1', 'Melbourne', 'Prefix', 'Computer Science', 12345)

    # Ensure the email failed to send
    mock_send_email.assert_called_once()
