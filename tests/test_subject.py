import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from flask import session
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

# Test creating a subject (logged in and session valid)
@patch('app.check_time', return_value=True)
@patch('app.mongoDB.insert_subject')
def test_createsubject_page_with_session_and_valid_time(mock_insert_subject, mock_check_time, client):
    # Mock the insert_subject to return a valid document ID
    mock_insert_subject.return_value = '123456'

    # Mock data to be posted
    data = {
        'year': '2024',
        'semester': '1',
        'campus': 'Melbourne',
        'coordinator': 'Dr. Smith',
        'subjectName': 'Physics',
        'subjectCode': 'PHYS101',
        'sections': ['Lecture', 'Tutorial']
    }

    # Test with the user logged in and session valid
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.post('/createsubject', json=data)

    assert response.status_code == 200
    assert b"success" in response.data

    # Ensure insert_subject was called with the correct arguments
    mock_insert_subject.assert_called_with(data, '2024', '1')

    # Ensure check_time was called
    mock_check_time.assert_called_once()
    
# Test creating a subject without being logged in
def test_createsubject_page_without_session(client):
    # Test with the user logged out (session cleared)
    with client.session_transaction() as sess:
        sess.clear()

    response = client.post('/createsubject', json={})

    assert response.status_code == 200
    assert b"<title>Victorian Institute of Technology Login Page</title>" in response.data  # Check for a common element in the login template    

# Test rendering edit subject page (session expired)
@patch('app.check_time', return_value=False)
def test_createsubject_page_with_expired_session(mock_check_time, client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get('/createsubject')
    
    assert b"<title>Victorian Institute of Technology Login Page</title>" in response.data  # Check for a common element in the login template

    # Ensure check_time was called and returned False
    mock_check_time.assert_called_once()

# Test rendering edit subject page (session expired)
@patch('app.check_time', return_value=False)
def test_editsubject_page_with_expired_session(mock_check_time, client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get('/editsubject')
    
    assert response.status_code == 200
    assert b"<title>Victorian Institute of Technology Login Page</title>" in response.data  # Check for a common element in the login template

    # Ensure check_time was called and returned False
    mock_check_time.assert_called_once()

# Test creating a subject without being logged in
def test_editsubject_page_without_session(client):
    # Test with the user logged out (session cleared)
    with client.session_transaction() as sess:
        sess.clear()

    response = client.post('/createsubject', json={})

    assert b"<title>Victorian Institute of Technology Login Page</title>" in response.data  # Check for a common element in the login template    

@patch('app.mongoDB.login')  # Mock mongoDB.login to return a mock client
def test_update_subject(mock_mongo_login,  client):
    # Mock the MongoDB client and its methods
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    # Mock the database and collection access
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    mock_collection.update_one.return_value.matched_count = 1  # Simulate successful update

    # Set the mock client to be returned when mongoDB.login() is called
    mock_mongo_login.return_value = mock_client

    # Mock data to be posted
    data = {
        'year': '2024',
        'semester': '1',
        'subjectCode': 'PHYS101',
        'campus': 'Melbourne',
    }

    # Make a POST request to the /editsubject route
    response = client.post('/editsubject', json=data)

    # Assert that the response status is 200 (success)
    assert response.status_code == 200
    assert b"success" in response.data

    # Ensure update_one was called with the correct query and data
    mock_collection.update_one.assert_called_with(
        {'subjectCode': 'PHYS101', 'campus': 'Melbourne'},
        {'$set': data}
    )

# Test inheriting subjects (successful case)
@patch('app.mongoDB.login')  # Mock the MongoDB login function
def test_inherit_subjects_success(mock_mongo_login, client):
    # Mock MongoDB client and its methods
    mock_client = MagicMock()
    mock_from_db = MagicMock()
    mock_to_db = MagicMock()
    mock_from_collection = MagicMock()
    mock_to_collection = MagicMock()
    
    # Set up the mock MongoDB structure
    mock_client.__getitem__.side_effect = [mock_from_db, mock_to_db]  # Accessing the from_db and to_db
    mock_from_db.__getitem__.return_value = mock_from_collection  # Accessing the from_collection
    mock_to_db.__getitem__.return_value = mock_to_collection  # Accessing the to_collection
    
    # Mock the find() and insert_many() operations
    mock_from_collection.find.return_value = [
        {'subjectCode': 'PHYS101', 'year': '2023', 'semester': '1'},
        {'subjectCode': 'MATH101', 'year': '2023', 'semester': '1'}
    ]
    mock_to_collection.insert_many.return_value = None  # Simulate successful insertion

    # Mock the MongoDB login
    mock_mongo_login.return_value = mock_client

    # Data to be sent in the request
    data = {
        'fromYear': '2023',
        'fromSemester': '1',
        'toYear': '2024',
        'toSemester': '1'
    }

    # Make the POST request to the /inherit_subjects route
    response = client.post('/inherit_subjects', json=data)

    # Assert that the response status is 200 (success)
    assert response.status_code == 200
    assert b"Inherited 2 subjects" in response.data

    # Ensure find() was called to get subjects from the source collection
    mock_from_collection.find.assert_called_with({}, {'_id': 0})

    # Ensure insert_many() was called to insert modified subjects into the destination collection
    mock_to_collection.insert_many.assert_called_once_with([
        {'subjectCode': 'PHYS101', 'year': '2024', 'semester': '1'},
        {'subjectCode': 'MATH101', 'year': '2024', 'semester': '1'}
    ])

# Test inheriting subjects with no subjects found (empty collection)
@patch('app.mongoDB.login')  # Mock the MongoDB login function
def test_inherit_subjects_no_subjects_found(mock_mongo_login, client):
    # Mock MongoDB client and its methods
    mock_client = MagicMock()
    mock_from_db = MagicMock()
    mock_to_db = MagicMock()
    mock_from_collection = MagicMock()
    mock_to_collection = MagicMock()
    
    # Set up the mock MongoDB structure
    mock_client.__getitem__.side_effect = [mock_from_db, mock_to_db]  # Accessing the from_db and to_db
    mock_from_db.__getitem__.return_value = mock_from_collection  # Accessing the from_collection
    mock_to_db.__getitem__.return_value = mock_to_collection  # Accessing the to_collection
    
    # Mock the find() operation to return an empty list (no subjects found)
    mock_from_collection.find.return_value = []

    # Mock the MongoDB login
    mock_mongo_login.return_value = mock_client

    # Data to be sent in the request
    data = {
        'fromYear': '2023',
        'fromSemester': '1',
        'toYear': '2024',
        'toSemester': '1'
    }

    # Make the POST request to the /inherit_subjects route
    response = client.post('/inherit_subjects', json=data)

    # Assert that the response status is 200 (no subjects found)
    assert response.status_code == 200
    assert b"Inherited 0 subjects" in response.data

    # Ensure find() was called
    mock_from_collection.find.assert_called_with({}, {'_id': 0})

    # Ensure insert_many() was NOT called since no subjects were found
    mock_to_collection.insert_many.assert_not_called()

# Test inheriting subjects with an error
@patch('app.mongoDB.login')  # Mock the MongoDB login function
def test_inherit_subjects_error(mock_mongo_login, client):
    # Mock MongoDB client and its methods
    mock_client = MagicMock()
    mock_from_db = MagicMock()
    mock_from_collection = MagicMock()
    
    # Set up the mock MongoDB structure
    mock_client.__getitem__.side_effect = [mock_from_db, Exception('Test error')]  # Raise an error on the second db access
    
    # Mock the MongoDB login
    mock_mongo_login.return_value = mock_client

    # Data to be sent in the request
    data = {
        'fromYear': '2023',
        'fromSemester': '1',
        'toYear': '2024',
        'toSemester': '1'
    }

    # Make the POST request to the /inherit_subjects route
    response = client.post('/inherit_subjects', json=data)

    # Assert that the response status is 500 (error)
    assert response.status_code == 500
    assert b"Test error" in response.data

    # Ensure find() was NOT called since there was an error before accessing collections
    mock_from_collection.find.assert_not_called()