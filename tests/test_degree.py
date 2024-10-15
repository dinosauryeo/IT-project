import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app module

# Fixture for the Flask test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test for adding a new degree (successful case)
@patch('app.mongoDB.login')
def test_add_degree_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate the degree not already existing in the collection
    mock_collection.find_one.return_value = None

    mock_mongo_login.return_value = mock_client

    # Data for the new degree
    data = {'name': 'Computer Science'}

    # Make a POST request to add the new degree
    response = client.post('/api/add-degree', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure insert_one was called once with the new degree data
    mock_collection.insert_one.assert_called_once_with({'name': 'Computer Science'})

# Test for adding a degree that already exists
@patch('app.mongoDB.login')
def test_add_degree_already_exists(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate the degree already existing in the collection
    mock_collection.find_one.return_value = {'name': 'Computer Science'}

    mock_mongo_login.return_value = mock_client

    # Data for the new degree
    data = {'name': 'Computer Science'}

    # Make a POST request to add the degree
    response = client.post('/api/add-degree', json=data)

    # Assert that the response indicates the degree already exists
    assert response.status_code == 200
    assert b'Degree already exists' in response.data

    # Ensure insert_one was not called since the degree already exists
    mock_collection.insert_one.assert_not_called()

# Test for adding a degree with an invalid name
@patch('app.mongoDB.login')
def test_add_degree_invalid_name(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    mock_mongo_login.return_value = mock_client

    # Data with no degree name
    data = {'name': ''}

    # Make a POST request with an invalid degree name
    response = client.post('/api/add-degree', json=data)

    # Assert that the response indicates invalid input
    assert response.status_code == 200
    assert b'Invalid degree name' in response.data

    # Ensure insert_one was not called
    mock_collection.insert_one.assert_not_called()

# Test for removing a degree (successful case)
@patch('app.mongoDB.login')
def test_remove_degree_success(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate successful deletion of the degree
    mock_collection.delete_one.return_value.deleted_count = 1

    mock_mongo_login.return_value = mock_client

    # Data for the degree to remove
    data = {'name': 'Computer Science'}

    # Make a POST request to remove the degree
    response = client.post('/api/remove-degree', json=data)

    # Assert that the response is successful
    assert response.status_code == 200
    assert b'success' in response.data

    # Ensure delete_one was called with the correct degree name
    mock_collection.delete_one.assert_called_once_with({'name': 'Computer Science'})

# Test for removing a degree that doesn't exist
@patch('app.mongoDB.login')
def test_remove_degree_not_found(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Simulate the degree not being found (deleted_count = 0)
    mock_collection.delete_one.return_value.deleted_count = 0

    mock_mongo_login.return_value = mock_client

    # Data for the degree to remove
    data = {'name': 'Nonexistent Degree'}

    # Make a POST request to remove the degree
    response = client.post('/api/remove-degree', json=data)

    # Assert that the response indicates the degree was not found
    assert response.status_code == 200
    assert b'Degree not found' in response.data

    # Ensure delete_one was called with the correct degree name
    mock_collection.delete_one.assert_called_once_with({'name': 'Nonexistent Degree'})

# Test for removing a degree with an invalid name
@patch('app.mongoDB.login')
def test_remove_degree_invalid_name(mock_mongo_login, client):
    # Mock the MongoDB client and collection
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    mock_mongo_login.return_value = mock_client

    # Data with an invalid degree name
    data = {'name': ''}

    # Make a POST request to remove the degree
    response = client.post('/api/remove-degree', json=data)

    # Assert that the response indicates invalid input
    assert response.status_code == 200
    assert b'Invalid degree name' in response.data

    # Ensure delete_one was not called
    mock_collection.delete_one.assert_not_called()
