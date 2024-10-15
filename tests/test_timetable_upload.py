import io
import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
from app import app

# Fixture for the Flask test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.check_time', return_value = True)  # Mock check_time function
@patch('app.insert_student_data')  # Mock the insert_student_data function
@patch('app.os.makedirs')  # Mock os.makedirs to avoid creating directories
@patch('app.os.path.exists')  # Mock os.path.exists to simulate the upload folder existence
@patch('builtins.open', new_callable=mock_open)  # Mock the open() call to avoid actual file operations
def test_upload_file_success(mock_open_file, mock_path_exists, mock_makedirs, mock_insert_student_data, mock_check_time, client):
    # Simulate the folder already exists
    mock_path_exists.return_value = True
    
    # Mock session to simulate a logged-in user
    with client.session_transaction() as session:
        session['logged_in'] = True

    # Create a mock CSV file for testing
    data = {
        'file': (io.BytesIO(b'StudentID,Name\n1,John Doe\n2,Jane Smith'), 'students.csv'),
        'year': '2024',
        'semester': '1'
    }

    # Make a POST request to upload the file
    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Assert the response is successful
    assert response.status_code == 200
    assert b'data stored successfully' in response.data

    # Dynamically construct the expected file path
    expected_path = os.path.join('uploads', '2024_1', 'students.csv')

# Test for missing file in the request
@patch('app.check_time', return_value = True)
@patch('app.os.makedirs')
@patch('app.os.path.exists')
def test_upload_file_no_file(mock_path_exists, mock_makedirs, mock_check_time, client):
    # Simulate the folder exists
    mock_path_exists.return_value = True

    # Mock session to simulate a logged-in user
    with client.session_transaction() as session:
        session['logged_in'] = True

    # Make a POST request without a file
    response = client.post('/upload', data={'year': '2024', 'semester': '1'}, content_type='multipart/form-data')

    # Assert that the response indicates no file part
    assert response.status_code == 400
    assert b'No file part' in response.data

    # Ensure check_time was called once
    mock_check_time.assert_called_once()

# Test for invalid file format
@patch('app.check_time',return_value = True)
@patch('app.os.makedirs')
@patch('app.os.path.exists')
@patch('builtins.open', new_callable=mock_open)
def test_upload_file_invalid_format(mock_open_file, mock_path_exists, mock_makedirs, mock_check_time, client):
    # Simulate the folder exists
    mock_path_exists.return_value = True

    # Mock session to simulate a logged-in user
    with client.session_transaction() as session:
        session['logged_in'] = True

    # Create a mock invalid file format (e.g., .txt)
    data = {
        'file': (io.BytesIO(b'This is not valid CSV content'), 'invalid.txt'),
        'year': '2024',
        'semester': '1'
    }

    # Make a POST request with invalid file format
    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Assert the response indicates an invalid file format
    assert response.status_code == 400
    assert b'Invalid file format' in response.data

    # Ensure check_time was called once
    mock_check_time.assert_called_once()

@patch('app.generate_timetable_for_students')  # Mock the generate_timetable_for_students function
@patch('app.mongoDB.login')  # Mock the MongoDB login
def test_generate_timetable_success(mock_mongo_login, mock_generate_timetable, client):
    # Mock the timetable generation process to return success
    mock_generate_timetable.return_value = (['timetable1', 'timetable2'], None)  # No error messages
    mock_client = MagicMock()
    mock_mongo_login.return_value = mock_client

    # Mocking the request data
    data = {'year': '2024', 'semester': '1'}

    # Make a POST request to the generate timetable endpoint
    response = client.post('/generate_timetable', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'Timetable generated and saved successfully' in response.data

    # Ensure generate_timetable_for_students was called with the correct database name
    mock_generate_timetable.assert_called_once_with('2024_1')

# Test for missing year and semester
def test_generate_timetable_missing_params(client):
    # Make a POST request without year and semester
    response = client.post('/generate_timetable', json={})

    # Assert that the response indicates missing parameters
    assert response.status_code == 200
    assert b'Year and semester are required' in response.data

# Test for failure in timetable generation
@patch('app.generate_timetable_for_students')
@patch('app.mongoDB.login')
def test_generate_timetable_failure(mock_mongo_login, mock_generate_timetable, client):
    # Mock the timetable generation process to return failure
    mock_generate_timetable.return_value = (None, 'Generation error')
    mock_client = MagicMock()
    mock_mongo_login.return_value = mock_client

    # Mocking the request data
    data = {'year': '2024', 'semester': '1'}

    # Make a POST request to the generate timetable endpoint
    response = client.post('/generate_timetable', json=data)

    # Assert that the response indicates failure
    assert response.status_code == 200
    assert b'Failed to generate timetable' in response.data

    # Ensure generate_timetable_for_students was called with the correct database name
    mock_generate_timetable.assert_called_once_with('2024_1')